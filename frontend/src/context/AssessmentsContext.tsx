import React, { createContext, useContext, useEffect, useState } from 'react';
import { Assessment, DocumentItem } from '../types';
import { api, AssessmentApi } from '../api/service';

interface AssessmentsContextValue {
  assessments: Assessment[];
  selected?: Assessment;
  refresh: () => Promise<void>;
  select: (id: string) => Promise<void>;
  create: (name: string, description?: string) => Promise<Assessment>;
  remove: (id: string) => Promise<void>;
  addDocuments: (id: string, files: File[]) => Promise<DocumentItem[]>;
  removeDocument: (id: string, documentId: string) => Promise<void>;
  beginAnalysis: (id: string) => Promise<void>;
  updateSelected: () => Promise<void>;
}

const AssessmentsContext = createContext<AssessmentsContextValue | undefined>(undefined);

export const useAssessments = () => {
  const ctx = useContext(AssessmentsContext);
  if (!ctx) throw new Error('useAssessments must be inside provider');
  return ctx;
};

export const AssessmentsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selected, setSelected] = useState<Assessment | undefined>();

  async function refresh() {
    const data = await api.listAssessments();
    setAssessments(data.map(mapAssessment));
    if (selected) {
      const latest = data.find(a => a.id === selected.id);
      if (latest) setSelected(mapAssessment(latest));
    }
  }

  async function select(id: string) {
    const a = await api.getAssessment(id);
    setSelected(mapAssessment(a));
  }

  async function create(name: string, description?: string) {
    const a = await api.createAssessment(name, description);
    await refresh();
    return mapAssessment(a);
  }

  async function remove(id: string) {
    await api.deleteAssessment(id);
    await refresh();
  }

  async function removeDocument(id: string, documentId: string) {
    try {
      await api.deleteDocument(id, documentId);
      // Refresh selected assessment to show updated document list
      await select(id);
    } catch (err) {
      console.error('Delete document failed', err);
      throw err;
    }
  }

  async function addDocuments(id: string, files: File[]) {
    const docs = await api.uploadDocuments(id, files);
    await refresh();
    return docs.map(d => ({
      id: d.id,
      filename: d.filename,
      contentType: d.content_type,
      size: d.size,
      uploadedAt: d.uploaded_at,
      category: d.category as any,
      aiInsights: d.llm_analysis,
      analysisMetadata: d.analysis_metadata,
      raw_extracted_text: d.raw_extracted_text,
      diagram_summary: d.diagram_summary,
      structured_report: d.structured_report
    }));
  }

  async function beginAnalysis(id: string) {
    await api.startAnalysis(id);
    await refresh();
  }

  async function fetchEnhancedProgress(id: string) {
    try {
      const response = await fetch(`/api/assessments/${id}/progress`);
      if (response.ok) {
        const enhancedProgress = await response.json();
        return enhancedProgress;
      }
    } catch (err) {
      console.error('Failed to fetch enhanced progress:', err);
    }
    return null;
  }

  async function updateSelected() {
    if (selected) {
      const a = await api.poll(selected.id);
      if (a) {
        const mapped = mapAssessment(a);
        
        // Fetch enhanced progress data
        const enhancedProgress = await fetchEnhancedProgress(a.id);
        if (enhancedProgress) {
          mapped.enhancedProgress = enhancedProgress;
        }
        
        setSelected(mapped);
        // Also update the assessment in the list to keep dashboard in sync
        setAssessments(prev => prev.map(item => item.id === a.id ? mapped : item));
      }
    }
  }

  useEffect(() => { refresh(); }, []);

  // Poll if analyzing or preprocessing
  useEffect(() => {
    const activeStatuses = ['analyzing', 'preprocessing', 'aligning'];
    if (selected && activeStatuses.includes(selected.status)) {
      const interval = setInterval(async () => {
        try {
          await updateSelected();
        } catch (err) {
          console.error('Polling failed:', err);
          // Continue polling; connection may be restored
        }
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [selected?.status]);

  function mapAssessment(a: AssessmentApi): Assessment {
    return {
      id: a.id,
      name: a.name,
      description: a.description,
      createdAt: a.created_at,
      status: a.status as any,
      progress: a.progress,
      currentPhase: a.current_phase,
      pillarStatuses: a.pillar_statuses || {},
      pillarProgress: a.pillar_progress || {},
      documents: a.documents.map(d => ({
        id: d.id,
        filename: d.filename,
        contentType: d.content_type,
        size: d.size,
        uploadedAt: d.uploaded_at,
        category: d.category as any,
        aiInsights: d.llm_analysis,
        analysisMetadata: (d as any).analysis_metadata,
        raw_text: (d as any).raw_text,
        raw_extracted_text: (d as any).raw_extracted_text,
        diagram_summary: (d as any).diagram_summary,
        structured_report: (d as any).structured_report
      })),
      pillarScores: a.pillar_results?.map(pr => ({
        pillar: pr.pillar,
        score: pr.overall_score,
        overallScore: pr.overall_score,
        confidence: pr.confidence as 'Low' | 'Medium' | 'High' | undefined,
        subcategories: pr.subcategories,
        categories: Object.entries(pr.subcategories).map(([name, score]) => ({ name, score })),
        recommendations: pr.recommendations.map(r => ({
          pillar: pr.pillar,
          title: r.title,
          reasoning: r.reasoning,
          recommendation: (r.recommendation || r.details),
          details: r.details,
          priority: r.priority as any,
          impact: r.impact,
          effort: r.effort as any,
          azureService: r.azure_service,
          source: r.source
        })),
        domainScoresRaw: (pr as any).domain_scores_raw || undefined,
        subcategoryDetails: (pr as any).subcategory_details || undefined,
      })),
      pillarResults: a.pillar_results?.map(pr => ({
        pillar: pr.pillar,
        score: pr.overall_score,
        overallScore: pr.overall_score,
        confidence: pr.confidence as 'Low' | 'Medium' | 'High' | undefined,
        subcategories: pr.subcategories,
        categories: Object.entries(pr.subcategories).map(([name, score]) => ({ name, score })),
        recommendations: pr.recommendations.map(r => ({
          pillar: pr.pillar,
          title: r.title,
          reasoning: r.reasoning,
          recommendation: (r.recommendation || r.details),
          details: r.details,
          priority: r.priority as any,
          impact: r.impact,
          effort: r.effort as any,
          azureService: r.azure_service,
          source: r.source
        })),
        scoringExplanation: (pr as any).scoring_explanation || null,
        scoringBreakdown: (pr as any).scoring_breakdown || null,
        simpleExplanation: (pr as any).simple_explanation || null,
        normalizationApplied: (pr as any).normalization_applied || false,
        rawSubcategorySum: (pr as any).raw_subcategory_sum || undefined,
        gapBasedRecommendations: ((pr as any).gap_based_recommendations || []).map((r: any) => ({
          pillar: pr.pillar,
          title: r.title,
          reasoning: r.reasoning,
          recommendation: (r.recommendation || r.details),
          details: r.details,
          priority: r.priority as any,
          impact: r.impact,
          effort: r.effort as any,
          azureService: r.azure_service,
          source: r.source,
          points_recoverable: r.points_recoverable
        })),
        domainScoresRaw: (pr as any).domain_scores_raw || undefined,
        subcategoryDetails: (pr as any).subcategory_details || undefined,
      })),
      recommendations: a.pillar_results?.flatMap(pr => pr.recommendations.map(r => ({
        id: `${a.id}-${pr.pillar}-${r.title}`,
        pillar: pr.pillar,
        title: r.title,
        priority: r.priority.toLowerCase() as 'low' | 'medium' | 'high',
        insight: r.reasoning,
        recommendation: (r.recommendation || r.details),
        details: r.details,
        impact: r.impact,
        effort: r.effort as 'Low' | 'Medium' | 'High',
        service: r.azure_service,
        source: r.source,
        scoreRefs: {}
      })))
      ,
      cohesiveRecommendations: (a as any).cohesive_recommendations?.map((r: any, idx: number) => ({
        id: `${a.id}-cohesive-${idx}`,
        pillar: r.source_pillar || 'Multi-Pillar',
        title: r.title,
        reasoning: r.reasoning,
        recommendation: (r.recommendation || r.details),
        details: r.details,
        priority: (r.priority || 'Medium') as any,
        impact: r.impact || r.business_impact || '',
        effort: (r.effort || 'Medium') as any,
        service: r.azure_service,
        source: r.source,
        crossPillarConsiderations: r.cross_pillar_considerations || [],
        scoreRefs: {},
      })) || []
    };
  }

  return (
    <AssessmentsContext.Provider value={{ assessments, selected, refresh, select, create, remove, addDocuments, removeDocument, beginAnalysis, updateSelected }}>
      {children}
    </AssessmentsContext.Provider>
  );
};
