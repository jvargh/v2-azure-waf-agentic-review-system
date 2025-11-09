// Fetch-based API client replacing mock layer.
export interface UploadDocResult {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  category: string;
  uploaded_at: string;
  llm_analysis?: string;
  // Extended fields from backend Document model
  analysis_metadata?: any;
  raw_extracted_text?: string;
  diagram_summary?: string;
  structured_report?: {
    executive_summary?: string;
    architecture_overview?: string;
    support_case_concerns?: string;
    cross_cutting_concerns?: Record<string, string>;
    deployment_summary?: string;
    pillar_evidence?: Record<string, { count: number; excerpts: string[] }>;
  };
}
export interface PillarResult { pillar: string; overall_score: number; subcategories: Record<string, number>; recommendations: Recommendation[]; confidence?: string; }
export interface Recommendation { pillar: string; title: string; reasoning: string; recommendation?: string; details: string; priority: string; impact: string; effort: string; azure_service: string; source?: string; }
export interface AssessmentApi {
  id: string; name: string; description?: string; created_at: string; status: string; progress: number; current_phase?: string; pillar_statuses?: Record<string, string>; pillar_progress?: Record<string, number>; documents: UploadDocResult[]; unified_corpus?: string; pillar_results?: PillarResult[]; overall_architecture_score?: number;
}

// Vite injects import.meta.env; cast to any to avoid TS complaints if types not picked up.
const BASE = (((import.meta as any).env?.VITE_API_BASE) as string) || 'http://localhost:8000';

async function j(method: string, path: string, body?: any): Promise<any> {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    method,
    headers: body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    body: body ? (body instanceof FormData ? body : JSON.stringify(body)) : undefined
  });
  if (!res.ok) {
    let extra = '';
    try {
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('application/json')) {
        const data = await res.json();
        extra = typeof data === 'string' ? data : (data.detail || data.message || JSON.stringify(data));
      } else {
        extra = await res.text();
      }
    } catch (e) {
      // ignore parse errors
    }
    throw new Error(`${method} ${path} failed: ${res.status}${extra ? ' - ' + extra : ''}`);
  }
  return res.json();
}

export const api = {
  listAssessments: (): Promise<AssessmentApi[]> => j('GET', '/api/assessments'),
  getAssessment: (id: string): Promise<AssessmentApi> => j('GET', `/api/assessments/${id}`),
  createAssessment: (name: string, description?: string): Promise<AssessmentApi> => j('POST', '/api/assessments', { name, description }),
  deleteAssessment: (id: string): Promise<{status: string; id: string}> => j('DELETE', `/api/assessments/${id}`),
  deleteDocument: (assessmentId: string, documentId: string): Promise<{status: string; document_id: string}> => j('DELETE', `/api/assessments/${assessmentId}/documents/${documentId}`),
  uploadDocuments: (id: string, files: File[]): Promise<UploadDocResult[]> => {
    const fd = new FormData();
    files.forEach(f => fd.append('files', f));
    return j('POST', `/api/assessments/${id}/documents`, fd);
  },
  startAnalysis: (id: string): Promise<AssessmentApi> => j('POST', `/api/assessments/${id}/analyze`),
  poll: (id: string): Promise<AssessmentApi> => j('GET', `/api/assessments/${id}/poll`)
};
