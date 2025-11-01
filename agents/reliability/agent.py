"""
Reliability Framework Agent for Azure Well-Architected Framework assessment.

This agent assesses the resiliency, availability, disaster recovery, backup/restore 
and monitoring posture of a workload, producing a weighted 0-100 reliability score 
with subscores and prioritized recommendations.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from shared.models import (
    AssessmentInput, AssessmentResult, Finding, Recommendation,
    PillarType, SeverityLevel, AzureService, AzureDocReference
)
from shared.utils.azure_docs import AzureDocsSearcher

logger = logging.getLogger(__name__)


class ReliabilityFrameworkAgent:
    """
    Reliability Framework Agent that assesses Azure workloads for reliability,
    availability, disaster recovery, and monitoring best practices.
    """
    
    def __init__(self):
        self.pillar = PillarType.RELIABILITY
        self.docs_searcher = AzureDocsSearcher()
        
        # Scoring weights as per specification
        self.scoring_weights = {
            "high_availability": 0.25,      # Redundancy & failover
            "disaster_recovery": 0.25,      # DR & data protection
            "fault_tolerance": 0.20,        # Fault-tolerant design patterns
            "backup_restore": 0.15,         # Backup & restore (tested)
            "monitoring": 0.15              # Reliability monitoring & drills
        }
    
    async def assess(self, input_data: AssessmentInput) -> AssessmentResult:
        """
        Perform comprehensive reliability assessment.
        
        Args:
            input_data: Assessment input data including architecture docs,
                       diagram findings, incidents, and requirements.
                       
        Returns:
            AssessmentResult with reliability score, findings, and recommendations.
        """
        logger.info("Starting reliability assessment")
        
        # Step 1: Search for relevant Azure documentation
        service_names = self._extract_service_names(input_data)
        azure_docs = await self.docs_searcher.search_reliability_docs(service_names)
        
        # Step 2: Perform analysis steps
        findings = []
        recommendations = []
        
        # Topology & HA audit
        ha_findings, ha_recommendations = self._audit_high_availability(
            input_data, azure_docs
        )
        findings.extend(ha_findings)
        recommendations.extend(ha_recommendations)
        
        # DR & risk analysis
        dr_findings, dr_recommendations = self._analyze_disaster_recovery(
            input_data, azure_docs
        )
        findings.extend(dr_findings)
        recommendations.extend(dr_recommendations)
        
        # Fault-tolerance patterns
        ft_findings, ft_recommendations = self._check_fault_tolerance_patterns(
            input_data, azure_docs
        )
        findings.extend(ft_findings)
        recommendations.extend(ft_recommendations)
        
        # Backup/restore & testing
        backup_findings, backup_recommendations = self._inspect_backup_restore(
            input_data, azure_docs
        )
        findings.extend(backup_findings)
        recommendations.extend(backup_recommendations)
        
        # Monitoring & observability
        monitoring_findings, monitoring_recommendations = self._assess_monitoring(
            input_data, azure_docs
        )
        findings.extend(monitoring_findings)
        recommendations.extend(monitoring_recommendations)
        
        # Step 3: Calculate scores
        subscores = self._calculate_subscores(findings)
        overall_score = self._calculate_overall_score(subscores)
        
        # Step 4: Prioritize recommendations
        prioritized_recommendations = self._prioritize_recommendations(
            recommendations, input_data.incident_patterns
        )
        
        # Step 5: Generate constraints for other agents
        constraints = self._generate_constraints(input_data, findings)
        
        return AssessmentResult(
            pillar=self.pillar,
            overall_score=overall_score,
            subscores=subscores,
            findings=findings,
            recommendations=prioritized_recommendations,
            constraints_for_other_agents=constraints
        )
    
    def _extract_service_names(self, input_data: AssessmentInput) -> List[str]:
        """Extract Azure service names from input data."""
        service_names = set()
        
        # From architecture documents
        for doc in input_data.arch_docs:
            for service in doc.services:
                service_names.add(service.service_type)
        
        # From diagram findings
        if input_data.diagram_findings:
            for service in input_data.diagram_findings.services:
                service_names.add(service.service_type)
        
        return list(service_names)
    
    def _audit_high_availability(self, 
                                     input_data: AssessmentInput,
                                     azure_docs: List[AzureDocReference]) -> tuple:
        """Audit topology & HA patterns."""
        findings = []
        recommendations = []
        
        services = self._get_all_services(input_data)
        
        # Check for single-zone deployments
        single_zone_services = [
            service for service in services 
            if len(service.zones) <= 1 and service.service_type not in ["Azure DNS", "Azure CDN"]
        ]
        
        if single_zone_services:
            finding = Finding(
                id=str(uuid.uuid4()),
                title="Single-zone deployments detected",
                description=f"Services deployed in single zones create availability risk: {[s.name for s in single_zone_services]}",
                severity=SeverityLevel.HIGH,
                pillar=self.pillar,
                affected_services=[s.name for s in single_zone_services],
                evidence=["Architecture analysis shows single-zone deployment"],
                azure_docs=self._find_relevant_docs(azure_docs, "zone redundant")
            )
            findings.append(finding)
            
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                title="Implement zone-redundant deployments",
                description="Deploy critical services across multiple availability zones to improve resilience",
                priority=1,
                effort_estimate="medium",
                impact_score=8.0,
                likelihood_score=7.0,
                pillar=self.pillar,
                related_findings=[finding.id],
                azure_docs=self._find_relevant_docs(azure_docs, "zone redundant"),
                implementation_steps=[
                    "Review current service deployment configuration",
                    "Enable zone-redundant deployment for critical services",
                    "Update load balancer configuration for multi-zone distribution",
                    "Test failover scenarios between zones"
                ]
            )
            recommendations.append(recommendation)
        
        # Check for missing load balancers
        services_needing_lb = [
            service for service in services
            if service.service_type in ["Virtual Machines", "App Service"] 
            and "load_balancer" not in [dep.lower() for dep in service.dependencies]
        ]
        
        if services_needing_lb:
            finding = Finding(
                id=str(uuid.uuid4()),
                title="Missing load balancers for high availability",
                description=f"Services without load balancers: {[s.name for s in services_needing_lb]}",
                severity=SeverityLevel.MEDIUM,
                pillar=self.pillar,
                affected_services=[s.name for s in services_needing_lb],
                evidence=["Architecture review shows compute services without load balancing"],
                azure_docs=self._find_relevant_docs(azure_docs, "load balancer")
            )
            findings.append(finding)
        
        return findings, recommendations
    
    def _analyze_disaster_recovery(self, 
                                       input_data: AssessmentInput,
                                       azure_docs: List[AzureDocReference]) -> tuple:
        """Analyze DR & risk patterns."""
        findings = []
        recommendations = []
        
        # Check RTO/RPO alignment
        if input_data.nonfunc_requirements:
            req = input_data.nonfunc_requirements
            
            if req.rto_hours and req.rto_hours < 1.0:
                # Very aggressive RTO requires active-active setup
                finding = Finding(
                    id=str(uuid.uuid4()),
                    title="Aggressive RTO requires active-active deployment",
                    description=f"RTO of {req.rto_hours} hours requires active-active cross-region setup",
                    severity=SeverityLevel.HIGH,
                    pillar=self.pillar,
                    affected_services=[],
                    evidence=[f"Declared RTO: {req.rto_hours} hours"],
                    azure_docs=self._find_relevant_docs(azure_docs, "disaster recovery active")
                )
                findings.append(finding)
        
        # Check for cross-region replication
        services = self._get_all_services(input_data)
        regions = {service.region for service in services if service.region}
        
        if len(regions) <= 1:
            finding = Finding(
                id=str(uuid.uuid4()),
                title="Single-region deployment increases DR risk",
                description="Workload deployed in single region lacks disaster recovery resilience",
                severity=SeverityLevel.HIGH,
                pillar=self.pillar,
                affected_services=[s.name for s in services],
                evidence=["All services deployed in single region"],
                azure_docs=self._find_relevant_docs(azure_docs, "cross region")
            )
            findings.append(finding)
            
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                title="Implement cross-region disaster recovery",
                description="Set up secondary region for disaster recovery with appropriate replication",
                priority=2,
                effort_estimate="high",
                impact_score=9.0,
                likelihood_score=6.0,
                pillar=self.pillar,
                related_findings=[finding.id],
                azure_docs=self._find_relevant_docs(azure_docs, "disaster recovery"),
                implementation_steps=[
                    "Select appropriate secondary region",
                    "Set up cross-region replication for data services",
                    "Implement automated failover procedures",
                    "Create and test DR runbooks"
                ]
            )
            recommendations.append(recommendation)
        
        return findings, recommendations
    
    def _check_fault_tolerance_patterns(self, 
                                            input_data: AssessmentInput,
                                            azure_docs: List[AzureDocReference]) -> tuple:
        """Check fault-tolerance design patterns."""
        findings = []
        recommendations = []
        
        # This would typically analyze code/configuration for patterns
        # For now, we'll create recommendations based on service types
        
        services = self._get_all_services(input_data)
        
        # Check for queue-based decoupling
        messaging_services = [
            s for s in services 
            if s.service_type in ["Service Bus", "Event Hubs", "Storage Queue"]
        ]
        
        if not messaging_services:
            finding = Finding(
                id=str(uuid.uuid4()),
                title="Missing asynchronous messaging patterns",
                description="No messaging services detected for decoupling and resilience",
                severity=SeverityLevel.MEDIUM,
                pillar=self.pillar,
                affected_services=[],
                evidence=["Architecture analysis shows direct service coupling"],
                azure_docs=self._find_relevant_docs(azure_docs, "messaging patterns")
            )
            findings.append(finding)
            
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                title="Implement asynchronous messaging patterns",
                description="Add messaging services to decouple components and improve fault tolerance",
                priority=3,
                effort_estimate="medium",
                impact_score=6.0,
                likelihood_score=5.0,
                pillar=self.pillar,
                related_findings=[finding.id],
                azure_docs=self._find_relevant_docs(azure_docs, "service bus"),
                implementation_steps=[
                    "Identify coupling points in current architecture",
                    "Design message schemas and routing",
                    "Implement Service Bus or Event Hubs",
                    "Update application code for async patterns"
                ]
            )
            recommendations.append(recommendation)
        
        return findings, recommendations
    
    def _inspect_backup_restore(self, 
                                    input_data: AssessmentInput,
                                    azure_docs: List[AzureDocReference]) -> tuple:
        """Inspect backup/restore & testing."""
        findings = []
        recommendations = []
        
        # Check for backup services
        services = self._get_all_services(input_data)
        backup_services = [
            s for s in services 
            if s.service_type in ["Azure Backup", "Recovery Services Vault"]
        ]
        
        data_services = [
            s for s in services 
            if s.service_type in ["SQL Database", "Cosmos DB", "Storage Account"]
        ]
        
        if data_services and not backup_services:
            finding = Finding(
                id=str(uuid.uuid4()),
                title="Missing backup strategy for data services",
                description="Data services detected without corresponding backup solutions",
                severity=SeverityLevel.HIGH,
                pillar=self.pillar,
                affected_services=[s.name for s in data_services],
                evidence=["Data services without backup configuration"],
                azure_docs=self._find_relevant_docs(azure_docs, "backup restore")
            )
            findings.append(finding)
        
        return findings, recommendations
    
    def _assess_monitoring(self, 
                               input_data: AssessmentInput,
                               azure_docs: List[AzureDocReference]) -> tuple:
        """Assess monitoring & observability."""
        findings = []
        recommendations = []
        
        services = self._get_all_services(input_data)
        monitoring_services = [
            s for s in services 
            if s.service_type in ["Application Insights", "Log Analytics", "Monitor"]
        ]
        
        if not monitoring_services:
            finding = Finding(
                id=str(uuid.uuid4()),
                title="Missing comprehensive monitoring solution",
                description="No monitoring services detected for observability",
                severity=SeverityLevel.HIGH,
                pillar=self.pillar,
                affected_services=[],
                evidence=["Architecture analysis shows no monitoring components"],
                azure_docs=self._find_relevant_docs(azure_docs, "monitoring alerting")
            )
            findings.append(finding)
            
            recommendation = Recommendation(
                id=str(uuid.uuid4()),
                title="Implement comprehensive monitoring and alerting",
                description="Deploy Azure Monitor, Application Insights, and configure alerts",
                priority=2,
                effort_estimate="medium",
                impact_score=8.0,
                likelihood_score=8.0,
                pillar=self.pillar,
                related_findings=[finding.id],
                azure_docs=self._find_relevant_docs(azure_docs, "application insights"),
                implementation_steps=[
                    "Deploy Application Insights for application monitoring",
                    "Configure Log Analytics workspace",
                    "Set up health probes and availability tests",
                    "Create alert rules for critical metrics"
                ]
            )
            recommendations.append(recommendation)
        
        return findings, recommendations
    
    def _get_all_services(self, input_data: AssessmentInput) -> List[AzureService]:
        """Get all services from input data."""
        services = []
        
        # From architecture documents
        for doc in input_data.arch_docs:
            services.extend(doc.services)
        
        # From diagram findings
        if input_data.diagram_findings:
            services.extend(input_data.diagram_findings.services)
        
        return services
    
    def _find_relevant_docs(self, azure_docs: List[AzureDocReference], 
                          keyword: str) -> List[AzureDocReference]:
        """Find documents relevant to a specific keyword."""
        relevant = []
        for doc in azure_docs:
            if (keyword.lower() in doc.title.lower() or 
                keyword.lower() in doc.content_excerpt.lower()):
                relevant.append(doc)
        return relevant[:2]  # Return top 2 most relevant
    
    def _calculate_subscores(self, findings: List[Finding]) -> Dict[str, float]:
        """Calculate subscores based on findings."""
        subscores = {
            "high_availability": 100.0,
            "disaster_recovery": 100.0,
            "fault_tolerance": 100.0,
            "backup_restore": 100.0,
            "monitoring": 100.0
        }
        
        # Deduct points based on severity and category
        severity_deductions = {
            SeverityLevel.CRITICAL: 30,
            SeverityLevel.HIGH: 20,
            SeverityLevel.MEDIUM: 10,
            SeverityLevel.LOW: 5
        }
        
        for finding in findings:
            deduction = severity_deductions.get(finding.severity, 0)
            
            # Map findings to subscore categories
            if "zone" in finding.title.lower() or "load balancer" in finding.title.lower():
                subscores["high_availability"] = max(0, subscores["high_availability"] - deduction)
            elif "disaster recovery" in finding.title.lower() or "region" in finding.title.lower():
                subscores["disaster_recovery"] = max(0, subscores["disaster_recovery"] - deduction)
            elif "messaging" in finding.title.lower() or "pattern" in finding.title.lower():
                subscores["fault_tolerance"] = max(0, subscores["fault_tolerance"] - deduction)
            elif "backup" in finding.title.lower():
                subscores["backup_restore"] = max(0, subscores["backup_restore"] - deduction)
            elif "monitoring" in finding.title.lower():
                subscores["monitoring"] = max(0, subscores["monitoring"] - deduction)
        
        return subscores
    
    def _calculate_overall_score(self, subscores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        total_score = 0.0
        for category, weight in self.scoring_weights.items():
            total_score += subscores[category] * weight
        return round(total_score, 1)
    
    def _prioritize_recommendations(self, 
                                  recommendations: List[Recommendation],
                                  incidents: List) -> List[Recommendation]:
        """Prioritize recommendations by impact, likelihood, and effort."""
        def priority_score(rec):
            # Higher score = higher priority
            base_score = (rec.impact_score * rec.likelihood_score) / max(1, rec.priority)
            
            # Boost priority if related to past incidents
            incident_boost = 0
            for incident in incidents:
                for service in rec.related_findings:
                    if any(affected in service for affected in incident.affected_services):
                        incident_boost += 2.0
            
            return base_score + incident_boost
        
        return sorted(recommendations, key=priority_score, reverse=True)
    
    def _generate_constraints(self, 
                            input_data: AssessmentInput,
                            findings: List[Finding]) -> Dict[str, Any]:
        """Generate constraints for other agents."""
        constraints = {
            "min_zones": 2,  # Minimum availability zones
            "regions_required": ["primary", "secondary"],  # DR requirement
            "health_probes_required": True,
            "monitoring_required": True
        }
        
        # Add RTO/RPO constraints if specified
        if input_data.nonfunc_requirements:
            req = input_data.nonfunc_requirements
            if req.rto_hours:
                constraints["rto_hours"] = req.rto_hours
            if req.rpo_minutes:
                constraints["rpo_minutes"] = req.rpo_minutes
        
        # Add constraints based on findings
        critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
        if critical_findings:
            constraints["immediate_action_required"] = True
            constraints["critical_issues"] = len(critical_findings)
        
        return constraints