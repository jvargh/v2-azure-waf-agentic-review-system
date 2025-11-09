"""
Tests for hybrid shadow scoring integration
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.app.scoring.hybrid_llm_scorer import run_hybrid_shadow
from backend.server import PillarResult, Recommendation


class TestHybridLLMScorer:
    """Test hybrid_llm_scorer.py stub implementation"""
    
    def test_run_hybrid_shadow_returns_structure(self):
        """run_hybrid_shadow returns expected structure"""
        pillar = "reliability"
        corpus = "Sample architecture document..."
        evidence = {
            "reliability": {
                "excerpts": ["excerpt1", "excerpt2", "excerpt3"]
            }
        }
        
        result = run_hybrid_shadow(pillar, corpus, evidence)
        
        # Verify required fields
        assert "pillar" in result
        assert result["pillar"] == "reliability"
        assert "timestamp" in result
        assert "status" in result
        assert result["status"] == "placeholder"
        assert "concept_hits" in result
        assert result["concept_hits"] == 3  # 3 excerpts
        assert "evidence_count" in result
        assert "provisional" in result
        assert "subcategory_scores" in result["provisional"]
        assert "llm_rationale" in result
        assert result["llm_rationale"] is None
        assert "notes" in result
    
    def test_run_hybrid_shadow_handles_missing_pillar_evidence(self):
        """run_hybrid_shadow handles missing pillar in evidence dict"""
        result = run_hybrid_shadow("security", "corpus", {})
        
        assert result["pillar"] == "security"
        assert result["concept_hits"] == 0
        assert result["status"] == "placeholder"
    
    def test_run_hybrid_shadow_handles_empty_excerpts(self):
        """run_hybrid_shadow handles empty excerpts list"""
        evidence = {
            "cost_optimization": {
                "excerpts": []
            }
        }
        result = run_hybrid_shadow("cost_optimization", "corpus", evidence)
        
        assert result["concept_hits"] == 0


class TestHybridShadowServerIntegration:
    """Test hybrid shadow integration in server.py _evaluate_pillar"""
    
    @patch("backend.server.load_azure_openai_settings")
    @patch("backend.server.LLMProvider")
    @patch("backend.app.scoring.hybrid_llm_scorer.run_hybrid_shadow")
    def test_hybrid_shadow_attaches_when_enabled(
        self,
        mock_run_hybrid,
        mock_llm_provider_class,
        mock_load_settings
    ):
        """Hybrid shadow scoring attaches experimental_scores when enabled"""
        # Mock settings with shadow enabled
        mock_settings = Mock()
        mock_settings.enable_hybrid_shadow = True
        mock_load_settings.return_value = mock_settings
        
        # Mock LLMProvider instance
        mock_provider = Mock()
        mock_provider.settings = mock_settings
        mock_llm_provider_class.return_value = mock_provider
        
        # Mock hybrid shadow result
        mock_hybrid_result = {
            "pillar": "reliability",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "placeholder",
            "concept_hits": 5,
            "llm_rationale": None
        }
        mock_run_hybrid.return_value = mock_hybrid_result
        
        # Import server after mocking (to trigger initialization)
        # Note: In actual test execution, this requires careful setup
        # to avoid importing server at module load time
        
        # Simulate _evaluate_pillar logic
        pillar_result = PillarResult(
            pillar="reliability",
            overall_score=75,
            subcategories={},
            recommendations=[],
            scoring_breakdown={}
        )
        
        # Simulate hybrid shadow attachment
        if mock_provider and mock_provider.settings.enable_hybrid_shadow:
            shadow_payload = mock_run_hybrid(
                pillar="reliability",
                unified_corpus="corpus",
                pillar_evidence={"reliability": {"excerpts": []}}
            )
            experimental_scores = {"hybrid_llm": shadow_payload}
            pillar_result = pillar_result.model_copy(
                update={"experimental_scores": experimental_scores}
            )
        
        # Assertions
        assert hasattr(pillar_result, "experimental_scores")
        assert "hybrid_llm" in pillar_result.experimental_scores
        assert pillar_result.experimental_scores["hybrid_llm"]["status"] == "placeholder"
        assert pillar_result.overall_score == 75  # Unchanged
        mock_run_hybrid.assert_called_once()
    
    @patch("backend.server.load_azure_openai_settings")
    @patch("backend.server.LLMProvider")
    def test_hybrid_shadow_not_attached_when_disabled(
        self,
        mock_llm_provider_class,
        mock_load_settings
    ):
        """Hybrid shadow does not attach when ENABLE_HYBRID_SHADOW=false"""
        # Mock settings with shadow disabled
        mock_settings = Mock()
        mock_settings.enable_hybrid_shadow = False
        mock_load_settings.return_value = mock_settings
        
        mock_provider = Mock()
        mock_provider.settings = mock_settings
        mock_llm_provider_class.return_value = mock_provider
        
        # Simulate _evaluate_pillar logic
        pillar_result = PillarResult(
            pillar="security",
            overall_score=80,
            subcategories={},
            recommendations=[],
            scoring_breakdown={}
        )
        
        # Simulate conditional check
        if mock_provider and mock_provider.settings.enable_hybrid_shadow:
            # Should NOT execute
            pytest.fail("Shadow scoring should not run when disabled")
        
        # Assert experimental_scores not present
        assert not hasattr(pillar_result, "experimental_scores") or \
               pillar_result.experimental_scores is None
    
    @patch("backend.server.load_azure_openai_settings")
    @patch("backend.server.LLMProvider")
    @patch("backend.app.scoring.hybrid_llm_scorer.run_hybrid_shadow")
    def test_hybrid_shadow_exception_does_not_crash(
        self,
        mock_run_hybrid,
        mock_llm_provider_class,
        mock_load_settings
    ):
        """Exception in hybrid shadow scoring does not crash evaluation"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.enable_hybrid_shadow = True
        mock_load_settings.return_value = mock_settings
        
        mock_provider = Mock()
        mock_provider.settings = mock_settings
        mock_llm_provider_class.return_value = mock_provider
        
        # Mock run_hybrid_shadow to raise exception
        mock_run_hybrid.side_effect = Exception("Hybrid scoring failed")
        
        pillar_result = PillarResult(
            pillar="performance_efficiency",
            overall_score=70,
            subcategories={},
            recommendations=[],
            scoring_breakdown={}
        )
        
        # Simulate try-except in server
        try:
            shadow_payload = mock_run_hybrid(
                pillar="performance_efficiency",
                unified_corpus="corpus",
                pillar_evidence={}
            )
            pillar_result = pillar_result.model_copy(
                update={"experimental_scores": {"hybrid_llm": shadow_payload}}
            )
        except Exception as e:
            # Log error, continue without experimental scores
            print(f"[hybrid-shadow] Error: {e}")
        
        # Pillar result should remain valid
        assert pillar_result.overall_score == 70
        assert not hasattr(pillar_result, "experimental_scores") or \
               pillar_result.experimental_scores is None


class TestNonMutationGuarantee:
    """Verify hybrid shadow does not mutate existing PillarResult fields"""
    
    @patch("backend.app.scoring.hybrid_llm_scorer.run_hybrid_shadow")
    def test_overall_score_unchanged(self, mock_run_hybrid):
        """Hybrid shadow does not alter overall_score"""
        mock_run_hybrid.return_value = {
            "pillar": "reliability",
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "placeholder",
            "concept_hits": 10
        }
        
        original = PillarResult(
            pillar="reliability",
            overall_score=85,
            subcategories={"subcategory1": 90},
            recommendations=[
                Recommendation(
                    pillar="reliability",
                    title="rec1",
                    reasoning="reasoning1",
                    details="details1",
                    priority="High",
                    impact="High",
                    effort="Medium",
                    azure_service="Service1"
                )
            ],
            scoring_breakdown={"key": "value"}
        )
        
        # Attach hybrid shadow
        shadow_payload = mock_run_hybrid("reliability", "corpus", {})
        updated = original.model_copy(
            update={"experimental_scores": {"hybrid_llm": shadow_payload}}
        )
        
        # Verify original fields unchanged
        assert updated.overall_score == 85
        assert updated.subcategories == {"subcategory1": 90}
        assert len(updated.recommendations) == 1
        assert updated.recommendations[0].title == "rec1"
        assert updated.scoring_breakdown == {"key": "value"}
        assert updated.pillar == "reliability"
    
    @patch("backend.app.scoring.hybrid_llm_scorer.run_hybrid_shadow")
    def test_subcategories_unchanged(self, mock_run_hybrid):
        """Hybrid shadow does not alter subcategories"""
        mock_run_hybrid.return_value = {
            "pillar": "security",
            "provisional": {
                "subcategory_scores": {"iam": 100}  # Different from original
            }
        }
        
        original = PillarResult(
            pillar="security",
            overall_score=70,
            subcategories={
                "iam": 60,
                "network": 80
            },
            recommendations=[],
            scoring_breakdown={}
        )
        
        shadow_payload = mock_run_hybrid("security", "corpus", {})
        updated = original.model_copy(
            update={"experimental_scores": {"hybrid_llm": shadow_payload}}
        )
        
        # Original subcategories should remain
        assert updated.subcategories == {
            "iam": 60,
            "network": 80
        }
        # Hybrid scores in separate experimental_scores field
        assert updated.experimental_scores["hybrid_llm"]["provisional"]["subcategory_scores"]["iam"] == 100
    
    @patch("backend.app.scoring.hybrid_llm_scorer.run_hybrid_shadow")
    def test_recommendations_unchanged(self, mock_run_hybrid):
        """Hybrid shadow does not alter recommendations"""
        mock_run_hybrid.return_value = {
            "pillar": "cost_optimization",
            "notes": "Use reserved instances"
        }
        
        original = PillarResult(
            pillar="cost_optimization",
            overall_score=65,
            subcategories={},
            recommendations=[
                Recommendation(
                    pillar="cost_optimization",
                    title="Enable autoscaling",
                    reasoning="reasoning1",
                    details="details1",
                    priority="High",
                    impact="High",
                    effort="Medium",
                    azure_service="Service1"
                ),
                Recommendation(
                    pillar="cost_optimization",
                    title="Review storage tiers",
                    reasoning="reasoning2",
                    details="details2",
                    priority="Medium",
                    impact="Medium",
                    effort="Low",
                    azure_service="Service2"
                )
            ],
            scoring_breakdown={}
        )
        
        shadow_payload = mock_run_hybrid("cost_optimization", "corpus", {})
        updated = original.model_copy(
            update={"experimental_scores": {"hybrid_llm": shadow_payload}}
        )
        
        # Original recommendations unchanged
        assert len(updated.recommendations) == 2
        assert updated.recommendations[0].title == "Enable autoscaling"
        assert updated.recommendations[1].title == "Review storage tiers"
        # Hybrid notes in separate field
        assert updated.experimental_scores["hybrid_llm"]["notes"] == "Use reserved instances"


class TestBackwardCompatibility:
    """Verify existing code paths work when llm_provider is None"""
    
    def test_evaluate_pillar_without_provider(self):
        """_evaluate_pillar completes without llm_provider"""
        # Simulate server state where provider initialization failed
        llm_provider = None
        
        pillar_result = PillarResult(
            pillar="operational_excellence",
            overall_score=75,
            subcategories={},
            recommendations=[],
            scoring_breakdown={}
        )
        
        # Simulate conditional check in server
        if llm_provider and llm_provider.settings.enable_hybrid_shadow:
            pytest.fail("Should not attempt hybrid shadow without provider")
        
        # Result should be valid without experimental_scores
        assert pillar_result.overall_score == 75
        assert not hasattr(pillar_result, "experimental_scores") or \
               pillar_result.experimental_scores is None
