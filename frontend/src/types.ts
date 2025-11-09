export interface DocumentItem {
  id: string;
  filename: string;
  contentType: string;
  size: number;
  uploadedAt: string;
  category: 'architecture' | 'case' | 'diagram';
  aiInsights?: string;
  analysisMetadata?: any;
  // Raw document content
  raw_text?: string;
  // Diagram enrichment fields (optional)
  raw_extracted_text?: string;
  diagram_summary?: string;
  // Structured multi-section report from backend analyzer
  structured_report?: {
    combined_markdown?: string;
    executive_summary?: string;
    architecture_overview?: string;
    support_case_concerns?: string;
    cross_cutting_concerns?: Record<string, string>;
    deployment_summary?: string;
    pillar_evidence?: Record<string, { count: number; excerpts: string[] }>;
  };
}

export interface Recommendation {
  id?: string;
  pillar: string;
  title: string;
  reasoning?: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical' | 'low' | 'medium' | 'high';
  insight?: string;
  recommendation?: string; // Explicit recommended action (how to fix)
  details: string;
  impact: string;
  business_impact?: string; // Enriched metric-driven impact (backend field)
  effort: 'Low' | 'Medium' | 'High';
  service?: string;
  azureService?: string;
  scoreRefs?: Record<string, number>;
  crossPillarConsiderations?: string[];
  source?: string;
  points_recoverable?: number; // Points that can be gained by implementing this
}

export interface PillarScore {
  pillar: string;
  score?: number;
  overallScore?: number;
  categories?: { name: string; score: number }[];
  subcategories?: Record<string, number>;
  recommendations?: Recommendation[];
  confidence?: 'Low' | 'Medium' | 'High';
  // Added diagnostics & provenance fields from backend PillarResult
  scoreSource?: 'floor' | 'evidence' | 'elevated';
  coveragePct?: number;
  negativeMentions?: number;
  // Gap-based recommendations generated from penalty analysis
  gapBasedRecommendations?: Recommendation[];
  // Flag indicating if normalization was applied
  normalizationApplied?: boolean;
  rawSubcategorySum?: number;
  domainScoresRaw?: Record<string, number>;
  subcategoryDetails?: Record<string, {
    name: string;
    base_score: number;
    coverage_penalty: number;
    gap_penalty: number;
    final_score: number;
    confidence: string;
    evidence_found: string[];
    missing_concepts: string[];
    gaps_detected: string[];
    normalization_factor?: number; // Scale factor applied if pillar normalization occurred
    // New concept provenance fields
    prompt_concepts?: string[]; // Concepts sent to LLM / expected for this subcategory
    found_concepts?: string[];  // Concepts detected (subset of prompt_concepts)
    justification_text?: string; // Unique per-subcategory natural language justification
    // Human-friendly transparency additions
    human_summary?: string; // One-line summary of coverage status
    expected_concepts?: string[]; // Full expected concept list
    substantiated?: boolean; // Any evidence was found
  }>;
  // Detailed scoring explanation aggregate values (pre/post elevation, scaling, sums)
  scoringExplanation?: {
    evidence_score?: number;
    pre_elevation_score?: number;
    elevation_uplift?: number;
    final_score?: number;
    scale_factor_initial?: number;
    scale_factor_final?: number;
    subcategories_sum_before?: number;
    subcategories_sum_final?: number;
    score_source?: string;
  } | null;
  // Full breakdown including concepts & step-wise adjustments
  scoringBreakdown?: {
    concepts?: Record<string, { found: string[]; missing: string[] }>;
    steps?: Array<Record<string, any>>;
    final?: Record<string, any>;
  } | null;
  // Simplified explanation with key drivers from backend (factor/impact pairs)
  simpleExplanation?: {
    drivers?: Array<{ factor: string; impact: string }>;
    metrics?: Record<string, any>;
  } | null;
}

export interface CrossPillarConflict {
  type: string;
  pillarA: string;
  pillarB: string;
  description: string;
  mitigation: string;
}

export interface PhaseTask {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'active' | 'completed' | 'failed';
  progress: number; // 0-100
  estimated_time_remaining?: string; // Format: "mm:ss" for active tasks only
  completed_at?: string;
  weight: number; // Relative weight for progress calculation
}

export interface EnhancedProgress {
  assessment_id: string;
  overall_progress: number; // 0-100, calculated from completed vs total weighted tasks
  current_phase?: string;
  status: string;
  phases: PhaseTask[];
  subtasks: PhaseTask[];
  estimated_total_time?: string; // Total remaining time across all active tasks
}

export interface Assessment {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  status: 'pending' | 'preprocessing' | 'analyzing' | 'aligning' | 'completed' | 'failed';
  progress: number; // 0-100
  currentPhase?: string;
  pillarStatuses?: Record<string, string>; // Per-pillar status (pending/analyzing/completed/failed)
  pillarProgress?: Record<string, number>; // Per-pillar progress (0-100)
  documents: DocumentItem[];
  unifiedCorpus?: string;
  pillarScores?: PillarScore[];
  pillarResults?: PillarScore[];
  crossPillarConflicts?: CrossPillarConflict[];
  cohesiveRecommendations?: Recommendation[]; // synthesized cross-pillar enriched recommendations
  overallArchitectureScore?: number;
  recommendations?: Recommendation[];
  // Enhanced progress data
  enhancedProgress?: EnhancedProgress;
}
