"""
Test diagram vision analysis path with llm_provider
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from backend.app.analysis.document_analyzer import DocumentAnalyzer


class TestDiagramVisionPath:
    """Verify vision API is called when llm_provider is injected"""
    
    @pytest.mark.asyncio
    async def test_vision_called_via_llm_provider(self):
        """DocumentAnalyzer.analyze_diagram uses llm_provider.vision() when available"""
        # Mock llm_provider
        mock_provider = Mock()
        
        # Mock vision response
        mock_vision_result = Mock()
        mock_vision_result.choices = [Mock(message=Mock(content="• Azure Front Door\n• Azure App Service\n• Azure SQL Database"))]
        
        async def mock_vision_call(messages):
            return mock_vision_result
        
        mock_provider.vision = AsyncMock(side_effect=mock_vision_call)
        
        # Create analyzer with provider
        analyzer = DocumentAnalyzer(llm_enabled=True, llm_provider=mock_provider)
        
        # Fake JPEG diagram data
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
        
        result = await analyzer.analyze_diagram(
            image_data=image_data,
            filename="test-diagram.jpg",
            content_type="image/jpeg"
        )
        
        # Assertions
        assert mock_provider.vision.called, "llm_provider.vision() should be called"
        assert "strategy" in result
        assert "llm_provider_vision" in result["strategy"] or "vision_error" in result["strategy"]
        
        # Verify vision was invoked with correct message structure
        call_args = mock_provider.vision.call_args
        messages = call_args[0][0]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert any(item.get("type") == "image_url" for item in messages[1]["content"])
    
    @pytest.mark.asyncio
    async def test_vision_populates_structured_report(self):
        """Vision summary should populate structured report with actual content"""
        mock_provider = Mock()
        
        # Rich vision response
        vision_content = """• Azure Front Door with WAF for global routing
• Multi-region deployment (East US, West Europe)
• Azure App Service for web tier
• Azure SQL Database with geo-replication
• Azure Cache for Redis for session state
• Application Insights for monitoring"""
        
        mock_vision_result = Mock()
        mock_vision_result.choices = [Mock(message=Mock(content=vision_content))]
        
        async def mock_vision_call(messages):
            return mock_vision_result
        
        mock_provider.vision = AsyncMock(side_effect=mock_vision_call)
        
        analyzer = DocumentAnalyzer(llm_enabled=True, llm_provider=mock_provider)
        
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
        
        result = await analyzer.analyze_diagram(
            image_data=image_data,
            filename="multi-region-arch.jpg",
            content_type="image/jpeg"
        )
        
        # Verify structured report contains content
        assert "structured_report" in result
        sr = result["structured_report"]
        
        assert "executive_summary" in sr
        assert len(sr["executive_summary"]) > 100, "Executive summary should be populated"
        
        assert "pillar_evidence" in sr
        # At least some pillars should have evidence from vision content
        assert len(sr["pillar_evidence"]) > 0, "pillar_evidence should be populated from vision analysis"
        
        # Check for specific inferred evidence
        if "reliability" in sr["pillar_evidence"]:
            assert sr["pillar_evidence"]["reliability"]["count"] > 0
        if "security" in sr["pillar_evidence"]:
            assert sr["pillar_evidence"]["security"]["count"] > 0
    
    @pytest.mark.asyncio
    async def test_vision_disabled_fallback(self):
        """When vision disabled, should still generate structured report"""
        mock_provider = Mock()
        
        # Vision returns disabled signal
        async def mock_vision_disabled(messages):
            return {"disabled": True}
        
        mock_provider.vision = AsyncMock(side_effect=mock_vision_disabled)
        
        analyzer = DocumentAnalyzer(llm_enabled=True, llm_provider=mock_provider)
        
        image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
        
        result = await analyzer.analyze_diagram(
            image_data=image_data,
            filename="test.jpg",
            content_type="image/jpeg"
        )
        
        assert "vision_disabled" in result["strategy"]
        assert "structured_report" in result
        # Should still have minimal pillar evidence from heuristics
        assert "pillar_evidence" in result["structured_report"]
    
    @pytest.mark.asyncio
    async def test_no_provider_uses_legacy_client(self):
        """Without llm_provider, should fall back to self.azure_client"""
        import os
        from unittest.mock import patch
        
        # Mock environment variable for deployment
        with patch.dict(os.environ, {"AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o"}):
            # Create analyzer without provider
            analyzer = DocumentAnalyzer(llm_enabled=True, llm_provider=None)
            
            # Mock azure_client
            mock_client = MagicMock()
            
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="• Test service"))]
            
            async def mock_create(**kwargs):
                return mock_response
            
            mock_client.chat.completions.create = AsyncMock(side_effect=mock_create)
            analyzer.azure_client = mock_client
            
            image_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
            
            result = await analyzer.analyze_diagram(
                image_data=image_data,
                filename="test.jpg",
                content_type="image/jpeg"
            )
            
            # Should use legacy path
            assert "azure_vision_summary" in result["strategy"] or "vision_error" in result["strategy"]
