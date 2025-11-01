"""
Tests for the Reliability Framework Agent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from agents.reliability.agent import ReliabilityFrameworkAgent
from shared.models import (
    AssessmentInput, ArchitectureDocument, AzureService, 
    NonFunctionalRequirement, SeverityLevel, PillarType
)


class TestReliabilityFrameworkAgent:
    
    @pytest.fixture
    def agent(self):
        return ReliabilityFrameworkAgent()
    
    @pytest.fixture
    def sample_input(self):
        services = [
            AzureService(
                name="web-app",
                service_type="App Service",
                region="East US",
                zones=["1"],
                dependencies=["sql-db"]
            ),
            AzureService(
                name="sql-db",
                service_type="SQL Database", 
                region="East US",
                zones=["1"],
                dependencies=[]
            )
        ]
        
        arch_doc = ArchitectureDocument(
            title="Test Architecture",
            content="Test content",
            document_type="ADR",
            services=services
        )
        
        nonfunc_req = NonFunctionalRequirement(
            rto_hours=1.0,
            rpo_minutes=15.0,
            availability_target=99.9
        )
        
        return AssessmentInput(
            arch_docs=[arch_doc],
            nonfunc_requirements=nonfunc_req
        )
    
    @pytest.mark.asyncio
    async def test_assess_basic_functionality(self, agent, sample_input):
        """Test basic assessment functionality."""
        result = await agent.assess(sample_input)
        
        assert result.pillar == PillarType.RELIABILITY
        assert 0 <= result.overall_score <= 100
        assert len(result.subscores) == 5
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)
    
    def test_extract_service_names(self, agent, sample_input):
        """Test service name extraction."""
        service_names = agent._extract_service_names(sample_input)
        assert "App Service" in service_names
        assert "SQL Database" in service_names
    
    def test_audit_high_availability_single_zone(self, agent, sample_input):
        """Test HA audit detects single-zone deployments."""
        findings, _ = agent._audit_high_availability(
            sample_input, []
        )
        
        # Should detect single-zone deployment
        single_zone_findings = [
            f for f in findings 
            if "single-zone" in f.title.lower()
        ]
        assert len(single_zone_findings) > 0
        assert single_zone_findings[0].severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    
    def test_disaster_recovery_analysis(self, agent, sample_input):
        """Test DR analysis detects single-region deployment."""
        findings, _ = agent._analyze_disaster_recovery(
            sample_input, []
        )
        
        # Should detect single-region deployment
        single_region_findings = [
            f for f in findings 
            if "single-region" in f.title.lower()
        ]
        assert len(single_region_findings) > 0
    
    def test_calculate_subscores(self, agent):
        """Test subscore calculation."""
        from shared.models import Finding
        
        # Create test finding
        finding = Finding(
            id="test-finding",
            title="Single-zone deployment detected",
            description="Test description", 
            severity=SeverityLevel.HIGH,
            pillar=PillarType.RELIABILITY
        )
        
        subscores = agent._calculate_subscores([finding])
        
        # Should have all required categories
        assert "high_availability" in subscores
        assert "disaster_recovery" in subscores
        assert "fault_tolerance" in subscores
        assert "backup_restore" in subscores
        assert "monitoring" in subscores
        
        # HA score should be reduced due to single-zone finding
        assert subscores["high_availability"] < 100
    
    def test_calculate_overall_score(self, agent):
        """Test overall score calculation."""
        subscores = {
            "high_availability": 80.0,
            "disaster_recovery": 90.0,
            "fault_tolerance": 85.0,
            "backup_restore": 75.0,
            "monitoring": 70.0
        }
        
        overall_score = agent._calculate_overall_score(subscores)
        
        # Should be weighted average
        expected = (
            80.0 * 0.25 +    # HA
            90.0 * 0.25 +    # DR
            85.0 * 0.20 +    # FT
            75.0 * 0.15 +    # Backup
            70.0 * 0.15      # Monitoring
        )
        
        assert abs(overall_score - expected) < 0.1
    
    def test_prioritize_recommendations(self, agent):
        """Test recommendation prioritization."""
        from shared.models import Recommendation
        
        recommendations = [
            Recommendation(
                id="rec1",
                title="Low priority rec",
                description="Test",
                priority=5,
                effort_estimate="low",
                impact_score=3.0,
                likelihood_score=2.0,
                pillar=PillarType.RELIABILITY
            ),
            Recommendation(
                id="rec2", 
                title="High priority rec",
                description="Test",
                priority=1,
                effort_estimate="low",
                impact_score=9.0,
                likelihood_score=8.0,
                pillar=PillarType.RELIABILITY
            )
        ]
        
        prioritized = agent._prioritize_recommendations(recommendations, [])
        
        # High impact/likelihood should be first
        assert prioritized[0].id == "rec2"
        assert prioritized[1].id == "rec1"


if __name__ == "__main__":
    pytest.main([__file__])