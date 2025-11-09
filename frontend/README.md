# Well-Architected Frontend

Prototype React + TypeScript UI implementing the user flow (Steps 0–8) for the Azure Well-Architected Review System. Uses in-memory mock APIs (no backend wiring yet) to simulate assessment creation, document upload, analysis progress, and scorecard results.

## Features

- Dashboard with metrics & recent assessments (Step 0 / 2)
- Create Assessment modal (Step 1)
- Assessment detail with tabs (Upload, Artifact Findings, Progress, Results)
- Multi-file upload & categorization (Steps 3–5)
- Auto-populated artifact findings (Step 6)
- Simulated pillar analysis progress with polling (Step 7)
- Scorecard & recommendation rendering (Step 8)
	- Concept Coverage panel now shows human-friendly summaries and expected concept lists.

## Getting Started

```pwsh
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Next Integration Steps

1. Replace `src/mock/api.ts` with real REST calls (FastAPI/Flask) that map to assessment + document endpoints.
2. Persist documents (object storage) and analysis outputs (JSON) referencing existing Python agent results.
3. Implement WebSocket or Server-Sent Events for real-time progress rather than polling.
4. Add authentication (Azure Entra ID) if needed for multi-user scenarios.
5. Export / download scorecard & recommendations (PDF/Markdown).

## Notes

This UI intentionally mirrors the specification narrative, emphasizing clarity of lifecycle transitions and state badges. Styling uses lightweight custom CSS (no external framework) for simplicity.

## Concept Coverage & Transparency Fields

Each pillar exposes `subcategoryDetails` including penalty math plus new fields:

- `human_summary` – concise qualitative status (e.g. "Partial coverage: 3/7 concept(s); missing logging, backup, DR")
- `expected_concepts` – full concept list evaluated for that subcategory (rendered in a collapsible section)
- `substantiated` – boolean indicating whether any evidence concepts were detected (drives ✔ vs ⚠ indicator)

If an assessment predates these backend fields they simply won't appear (safe fallback). The legacy `justification_text` remains for audit/debug beneath the summary.
