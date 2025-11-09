"""Enhanced Progress API for Assessment Analysis

Provides real-time progress tracking with:
- Individual phase/subtask status and completion
- Estimated time remaining (mm:ss format) for active tasks
- Dynamic progress calculation based on completed vs total tasks
- Green completion marking for finished phases/subtasks
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import datetime as dt
import os

progress_api = APIRouter()

# Global reference to MongoDB and in-memory store (will be set by server.py)
mongo_db: Any = None
ASSESSMENTS: Dict[str, Dict] = {}

class PhaseTask(BaseModel):
    """Individual phase or subtask within assessment progress"""
    id: str
    name: str
    description: str
    status: str  # pending|active|completed|failed
    progress: int  # 0-100
    estimated_time_remaining: Optional[str] = None  # Format: "mm:ss" for active tasks only
    completed_at: Optional[str] = None
    weight: float = 1.0  # Relative weight for progress calculation

class ProgressResponse(BaseModel):
    """Enhanced progress response with all phases and subtasks"""
    assessment_id: str
    overall_progress: int  # 0-100, calculated from completed vs total weighted tasks
    current_phase: Optional[str] = None
    status: str
    phases: List[PhaseTask]
    subtasks: List[PhaseTask] = []
    estimated_total_time: Optional[str] = None  # Total remaining time across all active tasks

def set_mongo_db(db):
    """Set MongoDB reference from server.py"""
    global mongo_db
    mongo_db = db

def set_assessments_store(store):
    """Set in-memory assessments store from server.py"""
    global ASSESSMENTS
    ASSESSMENTS = store

def _calculate_estimated_time(phase_name: str, pillar_statuses: Dict[str, str]) -> str:
    """Calculate estimated time remaining for active phases/tasks"""
    # Base time estimates per phase (in seconds)
    phase_estimates = {
        "Initialization": 30,
        "Document Processing": 45,
        "Corpus Assembly": 60,
        "Pillar Evaluation": 180,  # 3 minutes for all 5 pillars
        "Cross-Pillar Alignment": 90,
        "Synthesis": 120,
        "Finalization": 45
    }
    
    # Per-pillar estimates (when analyzing individual pillars)
    pillar_estimates = {
        "Reliability": 35,
        "Security": 35,
        "Cost Optimization": 30,
        "Operational Excellence": 30,
        "Performance Efficiency": 35
    }
    
    if phase_name == "Pillar Evaluation":
        # Calculate time for remaining pillars
        analyzing_pillars = [p for p, status in pillar_statuses.items() if status == "analyzing"]
        pending_pillars = [p for p, status in pillar_statuses.items() if status == "pending"]
        
        total_seconds = 0
        for pillar in analyzing_pillars:
            total_seconds += pillar_estimates.get(pillar, 35) // 2  # Half time for currently analyzing
        for pillar in pending_pillars:
            total_seconds += pillar_estimates.get(pillar, 35)
    else:
        total_seconds = phase_estimates.get(phase_name, 60)
    
    # Format as mm:ss
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def _get_phase_tasks(assessment: Dict[str, Any]) -> tuple[List[PhaseTask], List[PhaseTask]]:
    """Generate phase and subtask lists based on assessment state"""
    status = assessment.get("status", "pending")
    progress = assessment.get("progress", 0)
    current_phase = assessment.get("current_phase", "")
    pillar_statuses = assessment.get("pillar_statuses", {})
    pillar_progress = assessment.get("pillar_progress", {})
    
    now = dt.datetime.utcnow().isoformat()
    
    # Define all assessment phases with their progress ranges
    phase_definitions = [
        ("initialization", "Initialization", "Setting up assessment environment", 0, 5),
        ("document_processing", "Document Processing", "Analyzing uploaded documents", 5, 15), 
        ("corpus_assembly", "Corpus Assembly", "Building unified analysis corpus", 15, 20),
        ("pillar_evaluation", "Pillar Evaluation", "Running AI agent evaluations", 20, 80),  # Weight handled entirely by individual pillar subtasks (0.12 each)
        ("cross_pillar_alignment", "Cross-Pillar Alignment", "Identifying conflicts and synergies", 80, 90),
        ("synthesis", "Synthesis", "Generating final recommendations", 90, 95),
        ("finalization", "Finalization", "Completing assessment report", 95, 100)
    ]
    
    phases = []
    subtasks = []
    
    for phase_id, phase_name, phase_desc, start_pct, end_pct in phase_definitions:
        # Determine phase status
        if progress >= end_pct:
            phase_status = "completed"
            phase_progress = 100
            estimated_time = None
            completed_at = now
        elif progress >= start_pct:
            if current_phase and phase_name.lower() in current_phase.lower():
                phase_status = "active"
                # Calculate progress within phase range
                phase_progress = int(((progress - start_pct) / (end_pct - start_pct)) * 100)
                estimated_time = _calculate_estimated_time(phase_name, pillar_statuses)
            else:
                phase_status = "active" if progress > start_pct else "pending"
                phase_progress = min(100, max(0, int(((progress - start_pct) / (end_pct - start_pct)) * 100)))
                estimated_time = _calculate_estimated_time(phase_name, pillar_statuses) if phase_status == "active" else None
            completed_at = None
        else:
            phase_status = "pending"
            phase_progress = 0
            estimated_time = None
            completed_at = None
        
        weight_value = 0.0 if phase_id == "pillar_evaluation" else (end_pct - start_pct) / 100
        phases.append(PhaseTask(
            id=phase_id,
            name=phase_name,
            description=phase_desc,
            status=phase_status,
            progress=phase_progress,
            estimated_time_remaining=estimated_time,
            completed_at=completed_at,
            weight=weight_value
        ))
    
    # Add pillar subtasks during pillar evaluation phase
    if 20 <= progress <= 80:
        pillar_names = ["Reliability", "Security", "Cost Optimization", "Operational Excellence", "Performance Efficiency"]
        for pillar_name in pillar_names:
            pillar_status = pillar_statuses.get(pillar_name, "pending")
            pillar_prog = pillar_progress.get(pillar_name, 0)
            
            if pillar_status == "completed":
                subtask_status = "completed"
                subtask_progress = 100
                estimated_time = None
                completed_at = now
            elif pillar_status == "analyzing":
                subtask_status = "active"
                subtask_progress = pillar_prog
                estimated_time = _calculate_estimated_time(pillar_name, {pillar_name: pillar_status})
                completed_at = None
            elif pillar_status == "failed":
                subtask_status = "failed"
                subtask_progress = 0
                estimated_time = None
                completed_at = None
            else:
                subtask_status = "pending"
                subtask_progress = 0
                estimated_time = None
                completed_at = None
            
            subtasks.append(PhaseTask(
                id=f"pillar_{pillar_name.lower().replace(' ', '_')}",
                name=f"{pillar_name} Analysis",
                description=f"AI agent evaluation of {pillar_name} pillar",
                status=subtask_status,
                progress=subtask_progress,
                estimated_time_remaining=estimated_time,
                completed_at=completed_at,
                weight=0.12  # 60% total range / 5 pillars = 12% each expressed as fraction
            ))
    
    return phases, subtasks

def _calculate_dynamic_progress(phases: List[PhaseTask], subtasks: List[PhaseTask]) -> int:
    """Calculate overall progress based on completed vs total weighted tasks"""
    total_weight = 0
    completed_weight = 0
    
    # Weight from phases
    for phase in phases:
        total_weight += phase.weight
        if phase.status == "completed":
            completed_weight += phase.weight
        elif phase.status == "active":
            completed_weight += phase.weight * (phase.progress / 100)
    
    # Weight from subtasks (if any)
    for subtask in subtasks:
        total_weight += subtask.weight
        if subtask.status == "completed":
            completed_weight += subtask.weight
        elif subtask.status == "active":
            completed_weight += subtask.weight * (subtask.progress / 100)
    
    if total_weight == 0:
        return 0
    
    return min(100, int((completed_weight / total_weight) * 100))

@progress_api.get("/api/assessments/{assessment_id}/progress", response_model=ProgressResponse)
async def get_enhanced_progress(assessment_id: str):
    """Get enhanced progress information for an assessment"""
    
    # Retrieve assessment from MongoDB or in-memory store
    if mongo_db is not None:
        try:
            assessment = await mongo_db["assessments"].find_one({"id": assessment_id})
            if not assessment:
                raise HTTPException(404, "assessment not found")
        except Exception as e:
            print(f"[get_enhanced_progress] MongoDB error: {e}")
            raise HTTPException(500, "database error")
    else:
        # Fallback to in-memory store
        assessment = ASSESSMENTS.get(assessment_id)
        if not assessment:
            raise HTTPException(404, "assessment not found")
    
    # Generate phases and subtasks
    phases, subtasks = _get_phase_tasks(assessment)
    
    # Calculate dynamic progress
    dynamic_progress = _calculate_dynamic_progress(phases, subtasks)
    
    # Calculate total estimated time for all active tasks
    active_tasks = [task for task in phases + subtasks if task.status == "active" and task.estimated_time_remaining]
    total_estimated_seconds = 0
    for task in active_tasks:
        time_parts = task.estimated_time_remaining.split(":")
        if len(time_parts) == 2:
            try:
                minutes = int(time_parts[0])
                seconds = int(time_parts[1])
                total_estimated_seconds += (minutes * 60) + seconds
            except ValueError:
                pass
    
    estimated_total_time = None
    if total_estimated_seconds > 0:
        total_minutes = total_estimated_seconds // 60
        total_seconds = total_estimated_seconds % 60
        estimated_total_time = f"{total_minutes:02d}:{total_seconds:02d}"
    
    return ProgressResponse(
        assessment_id=assessment_id,
        overall_progress=dynamic_progress,
        current_phase=assessment.get("current_phase"),
        status=assessment.get("status", "pending"),
        phases=phases,
        subtasks=subtasks,
        estimated_total_time=estimated_total_time
    )
