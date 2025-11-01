"""
Shared data models for Azure Well-Architected Framework agents.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class SeverityLevel(str, Enum):
    """Severity levels for findings and recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PillarType(str, Enum):
    """Well-Architected Framework pillars."""
    RELIABILITY = "reliability"
    SECURITY = "security"
    COST_OPTIMIZATION = "cost_optimization"
    OPERATIONAL_EXCELLENCE = "operational_excellence"
    PERFORMANCE_EFFICIENCY = "performance_efficiency"


class AzureService(BaseModel):
    """Represents an Azure service in the architecture."""
    name: str
    service_type: str
    tier: Optional[str] = None
    region: Optional[str] = None
    zones: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class ArchitectureDocument(BaseModel):
    """Architecture document input."""
    title: str
    content: str
    document_type: str  # ADR, design_doc, etc.
    last_updated: Optional[datetime] = None
    services: List[AzureService] = Field(default_factory=list)


class DiagramFindings(BaseModel):
    """Findings from architecture diagram analysis."""
    services: List[AzureService] = Field(default_factory=list)
    topology: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    patterns: List[str] = Field(default_factory=list)


class IncidentPattern(BaseModel):
    """Pattern from past incidents."""
    incident_id: str
    root_cause: str
    outage_duration_minutes: int
    affected_services: List[str]
    severity: SeverityLevel
    description: str


class NonFunctionalRequirement(BaseModel):
    """Non-functional requirements like RTO/RPO."""
    rto_hours: Optional[float] = None
    rpo_minutes: Optional[float] = None
    availability_target: Optional[float] = None  # e.g., 99.9
    slo_targets: Dict[str, float] = Field(default_factory=dict)
    error_budget: Optional[float] = None


class AzureDocReference(BaseModel):
    """Reference to Azure documentation."""
    title: str
    url: str
    content_excerpt: str
    full_content: Optional[str] = None
    relevance_score: Optional[float] = None


class Finding(BaseModel):
    """A finding from agent analysis."""
    id: str
    title: str
    description: str
    severity: SeverityLevel
    pillar: PillarType
    affected_services: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    azure_docs: List[AzureDocReference] = Field(default_factory=list)


class Recommendation(BaseModel):
    """A recommendation from agent analysis."""
    id: str
    title: str
    description: str
    priority: int  # 1-10, where 1 is highest priority
    effort_estimate: str  # low, medium, high
    impact_score: float  # 0-10
    likelihood_score: float  # 0-10
    pillar: PillarType
    related_findings: List[str] = Field(default_factory=list)
    azure_docs: List[AzureDocReference] = Field(default_factory=list)
    implementation_steps: List[str] = Field(default_factory=list)


class PillarScore(BaseModel):
    """Score for a specific pillar."""
    pillar: PillarType
    score: float  # 0-100
    subscores: Dict[str, float] = Field(default_factory=dict)
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


class AssessmentInput(BaseModel):
    """Input for agent assessment."""
    arch_docs: List[ArchitectureDocument] = Field(default_factory=list)
    diagram_findings: Optional[DiagramFindings] = None
    incident_patterns: List[IncidentPattern] = Field(default_factory=list)
    nonfunc_requirements: Optional[NonFunctionalRequirement] = None
    constraints_from_other_agents: Dict[str, Any] = Field(default_factory=dict)
    azure_docs: List[AzureDocReference] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    """Result from agent assessment."""
    pillar: PillarType
    overall_score: float  # 0-100
    subscores: Dict[str, float] = Field(default_factory=dict)
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    constraints_for_other_agents: Dict[str, Any] = Field(default_factory=dict)
    assessment_timestamp: datetime = Field(default_factory=datetime.now)


class AgentMessage(BaseModel):
    """Message for agent-to-agent communication."""
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)