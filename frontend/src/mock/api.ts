import { Assessment, DocumentItem, Recommendation, PillarScore } from '../types';

let assessments: Assessment[] = [];

const randomId = () => Math.random().toString(36).slice(2, 10);

export function listAssessments(): Promise<Assessment[]> {
  return Promise.resolve(assessments.map(a => ({ ...a })));
}

export function createAssessment(name: string, description?: string): Promise<Assessment> {
  const a: Assessment = {
    id: randomId(),
    name,
    description,
    createdAt: new Date().toISOString(),
    status: 'pending',
    progress: 0,
    documents: []
  };
  assessments.unshift(a); // newest first
  return Promise.resolve({ ...a });
}

export function deleteAssessment(id: string): Promise<void> {
  assessments = assessments.filter(a => a.id !== id);
  return Promise.resolve();
}

export function getAssessment(id: string): Promise<Assessment | undefined> {
  return Promise.resolve(assessments.find(a => a.id === id));
}

export function uploadDocuments(assessmentId: string, files: File[]): Promise<DocumentItem[]> {
  const a = assessments.find(x => x.id === assessmentId);
  if (!a) return Promise.reject(new Error('Not found'));
  const uploaded: DocumentItem[] = files.map(f => ({
    id: randomId(),
    filename: f.name,
    contentType: f.type || guessContentType(f.name),
    size: f.size,
    uploadedAt: new Date().toISOString(),
    category: classifyFile(f.name, f.type),
    aiInsights: generateInsights(f.name)
  }));
  a.documents.push(...uploaded);
  return Promise.resolve(uploaded);
}

function guessContentType(name: string) {
  if (name.endsWith('.csv')) return 'text/csv';
  if (name.endsWith('.txt') || name.endsWith('.md')) return 'text/plain';
  if (/(png|jpg|jpeg|svg)$/i.test(name)) return 'image/*';
  return 'application/octet-stream';
}

function classifyFile(name: string, type: string): DocumentItem['category'] {
  if (/architecture|design|system/i.test(name)) return 'architecture';
  if (name.endsWith('.csv')) return 'case';
  if (/(png|jpg|jpeg|svg)$/i.test(name)) return 'diagram';
  return 'architecture';
}

function generateInsights(name: string) {
  if (name.endsWith('.csv')) {
    return 'Identified support case patterns: configuration errors, scaling incidents, security access issues.';
  }
  if (/architecture/i.test(name)) {
    return 'Detected patterns: microservices, API-first, event-driven messaging, serverless workloads.';
  }
  return 'Content ingested. Ready for pillar analysis.';
}

export function startAnalysis(assessmentId: string): Promise<void> {
  const a = assessments.find(x => x.id === assessmentId);
  if (!a) return Promise.reject(new Error('Not found'));
  a.status = 'analyzing';
  a.progress = 0;
  // Simulate async progress
  const steps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
  steps.forEach((p, i) => {
    setTimeout(() => {
      if (!a) return;
      a.progress = p;
      if (p === 100) {
        a.status = 'completed';
        a.pillarScores = generateScores();
        a.recommendations = generateRecommendations(a.pillarScores);
      }
    }, 800 + i * 900);
  });
  return Promise.resolve();
}

function generateScores(): PillarScore[] {
  return [
    pillar('Reliability', [
      'High Availability', 'Disaster Recovery', 'Fault Tolerance', 'Backup Strategy', 'Monitoring'
    ]),
    pillar('Security', [
      'Identity & Access', 'Data Protection', 'Network Security', 'Security Monitoring', 'Compliance'
    ]),
    pillar('Cost Optimization', [
      'Right-Sizing', 'Reserved Capacity', 'Cost Governance', 'Automation & Scaling', 'Waste Elimination'
    ]),
    pillar('Operational Excellence', [
      'DevOps & Deployment', 'Observability', 'Infra as Code', 'Incident Response', 'Continuous Improvement'
    ]),
    pillar('Performance Efficiency', [
      'Scalability', 'Resource Optimization', 'Caching & Delivery', 'Database Performance', 'Network Optimization'
    ])
  ];
}

function pillar(name: string, cats: string[]): PillarScore {
  return {
    pillar: name,
    score: randomBetween(name.includes('Cost') ? 55 : 75, name.includes('Cost') ? 65 : 88),
    categories: cats.map(c => ({ name: c, score: randomBetween(65, 90) }))
  };
}

function randomBetween(min: number, max: number) {
  return Math.round(min + Math.random() * (max - min));
}

function generateRecommendations(scores?: PillarScore[]): Recommendation[] {
  if (!scores) return [];
  return [
    {
      id: randomId(),
      pillar: 'Reliability',
      title: 'Architecture leverages microservices reducing single points of failure',
      priority: 'medium',
      insight: 'Microservices & container orchestration detected (AKS / Container Apps).',
      details: 'Consider documenting failure isolation strategies & chaos testing to further improve resiliency.',
      impact: 'Improves resilience, faster recovery from localized failures.',
      effort: 'Medium',
      service: 'Azure Kubernetes Service',
      scoreRefs: { Reliability: scores.find(s => s.pillar === 'Reliability')?.score || 0 }
    },
    {
      id: randomId(),
      pillar: 'Security',
      title: 'Strengthen data protection with deeper encryption & key rotation audits',
      priority: 'medium',
      insight: 'Use of managed databases detected; encryption at rest likely enabled.',
      details: 'Add periodic key rotation reviews & integrate Defender for Cloud alerts into incident workflows.',
      impact: 'Reduces breach impact, improves compliance posture.',
      effort: 'Medium',
      service: 'Azure Key Vault',
      scoreRefs: { Security: scores.find(s => s.pillar === 'Security')?.score || 0 }
    },
    {
      id: randomId(),
      pillar: 'Cost Optimization',
      title: 'Right-size compute & introduce budget alerts',
      priority: 'medium',
      insight: 'Compute workloads suggest potential over-allocation during non-peak hours.',
      details: 'Apply autoscaling policies & review Azure Advisor cost recommendations monthly.',
      impact: 'Lowers monthly spend 10-25%.',
      effort: 'Medium',
      service: 'Azure Advisor',
      scoreRefs: { Cost: scores.find(s => s.pillar === 'Cost Optimization')?.score || 0 }
    }
  ];
}
