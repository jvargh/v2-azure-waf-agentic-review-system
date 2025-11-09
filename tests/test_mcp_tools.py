"""Tests for MCP documentation client (fallback and hosted mock modes).

These tests avoid real network / Azure access by:
1. Exercising the static fallback path (enable_network=False)
2. Monkeypatching Azure credential + client classes to simulate Hosted MCP

Run with:  pytest -q  (if pytest installed) or python -m asyncio tests.test_mcp_tools
"""

import asyncio
import pytest
import types
from typing import List, Any, Dict
import sys, pathlib

# Ensure src on path for static analysis & direct execution (mirrors conftest)
_SRC_PATH = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

import importlib


def _import_mcp():
    """Dynamically import mcp_tools to avoid static path resolution issues in some analyzers."""
    mod = importlib.import_module("app.tools.mcp_tools")
    return (
        getattr(mod, "MCPDocumentationClient"),
        getattr(mod, "MCPToolManager"),
        getattr(mod, "_STATIC_FALLBACK_REFS"),
        getattr(mod, "LEARN_BASE"),
        mod,
    )


# ---------------------------
# Logging helpers
# ---------------------------
def _print_banner(title: str):
    print(f"\n=== {title} ===")


def _print_dict(d: Dict[str, Any]):
    for k, v in d.items():
        print(f"  - {k}: {v}")


def _log_case_start(name: str, description: str, inputs: Dict[str, Any], expectations: Dict[str, Any]):
    _print_banner(f"TEST START: {name}")
    print(description)
    print("Inputs:")
    _print_dict(inputs)
    print("Expectations:")
    _print_dict(expectations)


def _log_case_end(name: str, outputs: Dict[str, Any]):
    _print_banner(f"TEST END: {name}")
    print("Observed Outputs:")
    _print_dict(outputs)


def _log_assert(detail: str, **ctx: Any):
    print(f"  -> ASSERT: {detail}")
    if ctx:
        for k, v in ctx.items():
            print(f"     {k} = {v}")


async def _collect(async_iterable):  # Helper if ever needed
    return [item async for item in async_iterable]


@pytest.mark.asyncio
async def test_fallback_path():
    name = "fallback_path"
    query = "any query"
    max_items = 3
    mcp_doc_client_cls, _, static_fallback_refs, _, _ = _import_mcp()
    # Normalize possible dict-of-lists structure into flat list for slicing
    if isinstance(static_fallback_refs, dict):
        flat = []
        for v in static_fallback_refs.values():
            if isinstance(v, list):
                flat.extend(v)
        static_list = flat
    else:
        static_list = static_fallback_refs
    expected = static_list[:max_items]
    _log_case_start(
        name,
        "Validate static fallback list is returned when network disabled.",
        {"query": query, "max_items": max_items, "network": False},
        {"expected_count": len(expected), "expected_first_title": expected[0]["title"]},
    )

    client = mcp_doc_client_cls(enable_network=False)
    refs = await client.fetch_pillar_references('reliability', query, max_items=max_items)
    _log_assert("fallback list matches expected slice", expected_count=len(expected))
    assert refs == expected
    _log_assert("each ref has title & url")
    assert all({"title", "url"}.issubset(r.keys()) for r in refs)

    _log_case_end(
        name,
        {"actual_count": len(refs), "titles": [r["title"] for r in refs]},
    )


@pytest.mark.asyncio
async def test_tool_manager_fallback():
    name = "tool_manager_fallback"
    service = "reliability"
    product = "azure-well-architected"
    # Need LEARN_BASE for expectation logging
    _, _, _, learn_base2, _ = _import_mcp()
    _log_case_start(
        name,
        "Ensure MCPToolManager delegates to client fallback path.",
        {"service": service, "product": product, "network": False},
        {"expected_min_count": 1, "expected_url_prefix": learn_base2},
    )
    _, mcp_tool_manager_cls, _, learn_base, _ = _import_mcp()
    mgr = mcp_tool_manager_cls()
    mgr._client.enable_network = False  # type: ignore
    refs = await mgr.get_service_documentation(service, product)
    _log_assert(
        "at least one reference returned via manager fallback",
        actual_count=len(refs),
    )
    assert len(refs) > 0
    _log_assert(
        "first ref URL starts with learn base",
        first_url=refs[0]["url"],
        learn_base=learn_base,
    )
    assert refs[0]["url"].startswith(learn_base)
    _log_case_end(
        name,
        {"actual_count": len(refs), "first_url": refs[0]["url"]},
    )


@pytest.mark.asyncio
async def test_mock_hosted_path(monkeypatch=None):  # monkeypatch is a pytest fixture if available
    # Import module locally to patch symbols
    _, _, _, learn_base3, mcp_mod = _import_mcp()

    # Dummy credential (async context manager)
    class DummyCredential:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *exc):
            return False

    class DummyAgent:
        def __init__(self):
            # Provide two lines with learn URLs for parser
            self._text = (
                f"- High Availability Guide {learn_base3}/en-us/azure/architecture/framework/reliability/backup-and-recovery\n"
                f"Resiliency Patterns {learn_base3}/en-us/azure/architecture/framework/reliability/reliability-patterns"
            )
        async def run(self, prompt: str):  # async to match awaited usage in code
            class R:  # lightweight result object
                pass
            r = R()
            r.text = self._text
            # minimal await to satisfy async usage in linters
            await asyncio.sleep(0)
            return r

    class DummyChatClient:
        def __init__(self, async_credential):  # no state needed for tests
            self._agent = DummyAgent()
        async def __aenter__(self):
            return self
        async def __aexit__(self, *exc):
            return False
        async def setup_azure_ai_observability(self):  # no-op
            return
        def create_agent(self, **kwargs):
            return self._agent

    # Apply monkeypatching manually if pytest fixture not provided
    if monkeypatch is not None:
        monkeypatch.setattr(mcp_mod, "AzureCliCredential", DummyCredential, raising=True)
        monkeypatch.setattr(mcp_mod, "AzureAIAgentClient", DummyChatClient, raising=True)
        # Force network mode on
        monkeypatch.setattr(mcp_mod, "_AF_AVAILABLE", True, raising=True)
    else:
        mcp_mod.AzureCliCredential = DummyCredential  # type: ignore
        mcp_mod.AzureAIAgentClient = DummyChatClient  # type: ignore
        mcp_mod._AF_AVAILABLE = True  # type: ignore

    name = "mock_hosted_path"
    query = "ha+dr"
    _log_case_start(
        name,
        "Simulate hosted MCP path via monkeypatched Azure client & credential.",
        {"query": query, "network": True, "monkeypatched": True},
        {"expected_count": 2, "expected_url_prefix": learn_base3},
    )
    client = mcp_mod.MCPDocumentationClient(enable_network=True)
    refs = await client.fetch_pillar_references('reliability', query, max_items=5)
    _log_assert("exactly two references parsed from mocked hosted output", actual_count=len(refs))
    assert len(refs) == 2
    _log_assert("all refs start with learn base", urls=[r["url"] for r in refs])
    assert all(r["url"].startswith(learn_base3) for r in refs)
    titles = {r["title"] for r in refs}
    _log_assert("at least one title contains 'High Availability'", titles=list(titles))
    assert any("High Availability" in t or "Availability" in t for t in titles)
    _log_case_end(
        name,
        {"actual_count": len(refs), "titles": list(titles)},
    )


# Allow running without pytest
if __name__ == "__main__":
    async def _main():
        await test_fallback_path()
        await test_tool_manager_fallback()
        await test_mock_hosted_path()
        print("All MCP tests (manual) passed.")
    asyncio.run(_main())
