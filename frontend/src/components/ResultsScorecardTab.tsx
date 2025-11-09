import React, { useMemo, useState } from 'react';
import { useAssessments } from '../context/AssessmentsContext';
import { PillarScore, Recommendation } from '../types';
import * as XLSX from 'xlsx';

const ResultsScorecardTab: React.FC = () => {
  const { selected, refresh } = useAssessments();
  const [isRescoring, setIsRescoring] = useState(false);
  const [rescoreError, setRescoreError] = useState<string | null>(null);
  const [rescoreSuccess, setRescoreSuccess] = useState(false);
  
  // Use pillarResults (new format) or fallback to pillarScores (legacy)
  const pillarResults = selected?.pillarResults || selected?.pillarScores || [];
  const crossPillarConflicts = selected?.crossPillarConflicts || [];
  const overallScore = selected?.overallArchitectureScore;
  
  // Extract all recommendations from pillar results
  const allRecommendations = useMemo(() => {
    const recs: Recommendation[] = [];
    pillarResults.forEach((pillar: PillarScore) => {
      if (pillar.recommendations) {
        pillar.recommendations.forEach(rec => {
          recs.push({
            ...rec,
            pillar: pillar.pillar
          });
        });
      }
    });
    return recs;
  }, [pillarResults]);
  
  const overall = useMemo(() => {
    if (overallScore !== undefined) return overallScore;
    if (!pillarResults.length) return 0;
    const sum = pillarResults.reduce((acc: number, p: PillarScore) => {
      return acc + (p.overallScore || p.score || 0);
    }, 0);
    return +(sum / pillarResults.length).toFixed(1);
  }, [pillarResults, overallScore]);

  function ringPct() {
    const pct = Math.min(Math.max(overall, 0), 100);
    return pct + '%';
  }

  function scoreClass(score: number) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    return 'poor';
  }

  async function handleRescore() {
    if (!selected?.id) return;
    
    setIsRescoring(true);
    setRescoreError(null);
    setRescoreSuccess(false);
    
    try {
      const response = await fetch(`http://localhost:8000/api/assessments/${selected.id}/rescore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Rescore failed');
      }
      
      setRescoreSuccess(true);
      // Refresh assessments to get updated data
      await refresh();
      
      // Clear success message after 3 seconds
      setTimeout(() => setRescoreSuccess(false), 3000);
    } catch (err) {
      setRescoreError(err instanceof Error ? err.message : 'Failed to rescore assessment');
    } finally {
      setIsRescoring(false);
    }
  }

  // Expansion state moved to top-level to comply with React Hooks rules
  const [expandedSubcats, setExpandedSubcats] = useState<Record<string, boolean>>({});
  const [expandedPillars, setExpandedPillars] = useState<Record<string, boolean>>({});
  // Separate expansion map for Concept Coverage section (default collapsed)
  const [coverageExpanded, setCoverageExpanded] = useState<Record<string, boolean>>({});
  // Panel-level (outer) open/close states (default closed)
  const [conceptCoveragePanelOpen, setConceptCoveragePanelOpen] = useState<boolean>(false);
  const [recommendationsPanelOpen, setRecommendationsPanelOpen] = useState<boolean>(false);
  // Section-wide inner pillar expansion toggles (retain previous behavior)
  const [coverageGlobalExpanded, setCoverageGlobalExpanded] = useState<boolean>(false);
  const [recsGlobalExpanded, setRecsGlobalExpanded] = useState<boolean>(false);
  // Removed score justification UI; related expansion state eliminated.

  // Generate dynamic scoring explanation using Reliability pillar data
  const scoringExplanation = useMemo(() => {
    const reliabilityPillar = pillarResults.find((p: PillarScore) => p.pillar === 'Reliability');
    if (!reliabilityPillar) {
      // Fallback to generic explanation
      return (
        <>
          Each pillar is evaluated across multiple subcategories representing specific Azure Well-Architected best practices. 
          The LLM assesses each subcategory independently based on your documentation quality and implementation evidence. 
          The <strong>pillar score is the sum of all its subcategory scores</strong>—this ensures complete transparency and mathematical consistency. 
          If the sum exceeds 100, we normalize it to fit the 0-100 scale and show you exactly what was adjusted in the "Hidden Gap Analysis" section. 
          The <strong>Overall Architecture Score</strong> is the average of all five pillar scores.
        </>
      );
    }

    const subcats = reliabilityPillar.subcategories || {};
    const categories = reliabilityPillar.categories || Object.keys(subcats).map(name => ({
      name,
      score: subcats[name]
    }));
    const pillarScore = reliabilityPillar.overallScore ?? reliabilityPillar.score ?? 0;
    const rawSum = reliabilityPillar.rawSubcategorySum ?? 0;
    const normalized = reliabilityPillar.normalizationApplied ?? false;
    
    // Get first 3 subcategories as examples
    const exampleSubcats = categories.slice(0, 3);
    const subcatSum = categories.reduce((sum: number, c: any) => sum + (c.score || 0), 0);
    
    return (
      <>
        Each pillar is evaluated across multiple subcategories. 
        For example, <strong>Reliability</strong> includes{' '}
        {exampleSubcats.map((c: any, idx: number) => (
          <span key={idx}>
            "{c.name}" ({c.score}){idx < exampleSubcats.length - 1 ? ', ' : ''}
          </span>
        ))}
        {categories.length > 3 && `, and ${categories.length - 3} more`}. 
        The LLM assesses each subcategory independently based on documentation quality, implementation evidence, and completeness. 
        In this assessment, Reliability's {categories.length} subcategories sum to <strong>{subcatSum} points</strong>
        {normalized && rawSum > 0 ? (
          <>, which was normalized from {rawSum} → {pillarScore} to fit the 0-100 scale (see "Hidden Gap Analysis" below for details)</>
        ) : (
          <>, giving the <strong>pillar score of {pillarScore}</strong> directly—no normalization needed</>
        )}. 
        This bottom-up approach ensures the pillar score always matches the sum of its parts, providing complete transparency. 
        The <strong>Overall Architecture Score</strong> ({overall}) is the average of all five pillar scores.
      </>
    );
  }, [pillarResults, overall]);

  return (
    <div>
      {/* Page Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        paddingBottom: '1rem',
        borderBottom: '1px solid #e1e4e8'
      }}>
        <div>
          <h3 style={{ 
            margin: '0 0 0.5rem', 
            fontSize: '1.5rem', 
            fontWeight: 600,
            color: '#24292e'
          }}>Agentic Well-Architected Scorecard</h3>
          <p style={{ 
            margin: 0, 
            fontSize: '0.9rem', 
            color: '#586069' 
          }}>Comprehensive analysis across the five pillars of Azure Well-Architected Framework</p>
        </div>
        {/* Download Excel Report Button - client-side XLSX generation */}
        {pillarResults.length > 0 && (
          <button
            type="button"
            onClick={async () => {
              try {
                const assessmentName = selected?.name || 'Unnamed Assessment';
                
                // Heuristic enrich coverage/gaps if missing
                const enriched = pillarResults.map(p => {
                  let coveragePct: number | undefined = (p as any).coveragePct;
                  let negativeMentions: number | undefined = (p as any).negativeMentions;
                  const details = p.subcategoryDetails || {};
                  const entries: any[] = Object.values(details);
                  if ((coveragePct === undefined || coveragePct === null) && entries.length) {
                    const withEvidence = entries.filter(d => (d.found_concepts || d.evidence_found || []).length > 0).length;
                    coveragePct = Math.round((withEvidence / entries.length) * 100);
                  }
                  if ((negativeMentions === undefined || negativeMentions === null) && entries.length) {
                    const totalMissing = entries.reduce((acc, d) => acc + (d.missing_concepts ? d.missing_concepts.length : 0), 0);
                    negativeMentions = totalMissing; // simple gap count heuristic
                  }
                  return { ...p, coveragePct, negativeMentions } as any;
                });

                const allRecs: Recommendation[] = [];
                enriched.forEach(p => (p.recommendations || []).forEach((r: Recommendation) => allRecs.push(r)));
                const highPriorityCount = allRecs.filter(r => ['critical','high'].includes((r.priority || '').toLowerCase())).length;
                const avgCoverage = enriched.length ? Math.round(enriched.reduce((a,p)=> a + (Number(p.coveragePct)||0),0)/enriched.length) : 0;

                // Create a new workbook
                const wb = XLSX.utils.book_new();

                // Helper function to style cells
                const styleCell = (ws: any, cell: string, style: any) => {
                  if (!ws[cell]) ws[cell] = { t: 's', v: '' };
                  ws[cell].s = style;
                };

                // Base style factories
                const mkFill = (hex: string) => ({ fgColor: { rgb: hex.replace('#','').toUpperCase() } });
                const headerStyle = {
                  font: { bold: true, sz: 14, color: { rgb: 'FFFFFF' } },
                  fill: mkFill('#0B6FA4'),
                  alignment: { horizontal: 'center', vertical: 'center' }
                };
                const tableHeaderStyle = {
                  font: { bold: true, sz: 11, color: { rgb: 'FFFFFF' } },
                  fill: mkFill('#0B6FA4'),
                  border: { top:{style:'thin'},bottom:{style:'thin'},left:{style:'thin'},right:{style:'thin'} },
                  alignment: { horizontal: 'center', vertical: 'center' }
                };
                const dataStyleBase = {
                  font: { sz: 10 },
                  border: { top:{style:'thin'},bottom:{style:'thin'},left:{style:'thin'},right:{style:'thin'} },
                  alignment: { vertical: 'top', wrapText: true },
                  fill: mkFill('#FFFFFF')
                };
                const labelStyle = { font: { bold: true }, alignment: { vertical: 'top' } };
                const subHeaderStyle = { font: { bold: true, sz: 12 }, fill: mkFill('#E7E6E6'), alignment: { horizontal: 'center', vertical: 'center' } };

                // Helper for score coloring
                // Legacy formatting: keep plain white cells, no conditional score coloring.

                // 1. OVERVIEW SHEET
                const overviewData: any[][] = [
                  ['Azure Well-Architected Assessment Report'],
                  [],
                  ['Assessment Name:', assessmentName],
                  ['Assessment ID:', selected?.id || ''],
                  ['Generated:', new Date().toLocaleString()],
                  ['Overall Architecture Score:', overall],
                  ['Average Coverage %:', avgCoverage],
                  ['Total Recommendations:', allRecs.length],
                  ['High/Critical Recommendations:', highPriorityCount],
                  [],
                  ['Pillar Summary'],
                  ['Pillar', 'Score', 'Confidence', 'Coverage %', 'Gaps']
                ];

                enriched.forEach(p => {
                  const s = p.overallScore ?? p.score ?? 0;
                  overviewData.push([
                    p.pillar,
                    s,
                    p.confidence || '',
                    p.coveragePct ?? '',
                    p.negativeMentions ?? ''
                  ]);
                });

                const wsOverview = XLSX.utils.aoa_to_sheet(overviewData);
                wsOverview['!cols'] = [
                  { wch: 32 },
                  { wch: 18 },
                  { wch: 16 },
                  { wch: 14 },
                  { wch: 10 }
                ];

                // Merges (title + subheader)
                wsOverview['!merges'] = [
                  { s: { r: 0, c: 0 }, e: { r: 0, c: 4 } },
                  { s: { r: 10, c: 0 }, e: { r: 10, c: 4 } }
                ];
                styleCell(wsOverview, 'A1', headerStyle);
                // Label rows
                ['A3','A4','A5','A6','A7','A8','A9'].forEach(c => styleCell(wsOverview, c, labelStyle));
                styleCell(wsOverview, 'A11', subHeaderStyle);
                ['A12','B12','C12','D12','E12'].forEach(c => styleCell(wsOverview, c, tableHeaderStyle));
                const overviewStart = 13;
                for (let i = 0; i < enriched.length; i++) {
                  const row = overviewStart + i;
                  ['A','B','C','D','E'].forEach(col => {
                    const cellRef = `${col}${row}`;
                    styleCell(wsOverview, cellRef, { ...dataStyleBase });
                  });
                }
                // Auto filter (community version supports ref assignment)
                wsOverview['!autofilter'] = { ref: `A12:E${overviewStart + enriched.length - 1}` };
                XLSX.utils.book_append_sheet(wb, wsOverview, 'Overview');

                // 2. PILLAR SCORES SHEET
                const pillarScoresData: any[][] = [
                  ['Pillar Scores Breakdown'],
                  [],
                  ['Pillar', 'Overall Score', 'Confidence', 'Coverage %', 'Negative Mentions']
                ];
                enriched.forEach(p => {
                  const s = p.overallScore ?? p.score ?? 0;
                  pillarScoresData.push([p.pillar, s, p.confidence || '', p.coveragePct ?? '', p.negativeMentions ?? '']);
                });
                const wsPillarScores = XLSX.utils.aoa_to_sheet(pillarScoresData);
                wsPillarScores['!cols'] = [
                  { wch: 28 },
                  { wch: 16 },
                  { wch: 16 },
                  { wch: 14 },
                  { wch: 18 }
                ];
                wsPillarScores['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 4 } }];
                styleCell(wsPillarScores, 'A1', headerStyle);
                ['A3','B3','C3','D3','E3'].forEach(c => styleCell(wsPillarScores, c, tableHeaderStyle));
                for (let i = 0; i < enriched.length; i++) {
                  const row = 4 + i;
                  ['A','B','C','D','E'].forEach(col => {
                    const cellRef = `${col}${row}`;
                    styleCell(wsPillarScores, cellRef, { ...dataStyleBase });
                  });
                }
                wsPillarScores['!autofilter'] = { ref: `A3:E${4 + enriched.length - 1}` };
                XLSX.utils.book_append_sheet(wb, wsPillarScores, 'Pillar Scores');

                // 3. CONCEPT COVERAGE SHEET
                const conceptCoverageData: any[][] = [
                  ['Concept Coverage & Justification'],
                  [],
                  ['Pillar', 'Subcategory', 'Score', 'Found Concepts', 'Missing Concepts', 'Justification']
                ];
                let conceptRowCount = 0;
                enriched.forEach(p => {
                  const details = p.subcategoryDetails || {};
                  const entries = Object.values(details);
                  if (entries.length === 0) {
                    conceptCoverageData.push([p.pillar, 'No subcategory details available', '', '', '', '']);
                    conceptRowCount++;
                  } else {
                    entries.forEach((d: any) => {
                      const foundArr = (d.found_concepts || d.evidence_found || []);
                      const found = foundArr.join(', ') || 'None';
                      const missingArr = (d.missing_concepts || []);
                      const missing = missingArr.join(', ') || 'None';
                      const justification = d.justification_text || '';
                      conceptCoverageData.push([p.pillar, d.name, d.final_score, found, missing, justification]);
                      conceptRowCount++;
                    });
                  }
                });
                const wsConcept = XLSX.utils.aoa_to_sheet(conceptCoverageData);
                wsConcept['!cols'] = [
                  { wch: 24 },
                  { wch: 36 },
                  { wch: 8 },
                  { wch: 48 },
                  { wch: 48 },
                  { wch: 80 }
                ];
                wsConcept['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 5 } }];
                styleCell(wsConcept, 'A1', headerStyle);
                ['A3','B3','C3','D3','E3','F3'].forEach(c => styleCell(wsConcept, c, tableHeaderStyle));
                for (let i = 0; i < conceptRowCount; i++) {
                  const row = 4 + i;
                  ['A','B','C','D','E','F'].forEach(col => {
                    const cellRef = `${col}${row}`;
                    styleCell(wsConcept, cellRef, { ...dataStyleBase });
                  });
                }
                wsConcept['!autofilter'] = { ref: `A3:F${3 + conceptRowCount + 1}` };
                XLSX.utils.book_append_sheet(wb, wsConcept, 'Concept Coverage');

                // 4. RECOMMENDATIONS SHEET
                const recommendationsData: any[][] = [
                  ['Recommendations by Pillar'],
                  [],
                  ['Pillar', '#', 'Title', 'Priority', 'Effort', 'Impact', 'Recommendation', 'Source']
                ];
                let recRowCount = 0;
                enriched.forEach(p => {
                  const recs = p.recommendations || [];
                  if (recs.length === 0) {
                    recommendationsData.push([p.pillar, '', 'No recommendations available', '', '', '', '', '']);
                    recRowCount++;
                  } else {
                    // Sort per pillar by priority
                    const priorityOrder: Record<string, number> = { critical:1, high:2, medium:3, low:4 };
                    const sorted = [...recs].sort((a,b) => (priorityOrder[(a.priority||'').toLowerCase()]||5) - (priorityOrder[(b.priority||'').toLowerCase()]||5));
                    sorted.forEach((r, idx) => {
                      const reasoning = r.reasoning || r.insight || (r as any).recommendation || r.details || '';
                      const impact = (r as any).business_impact || r.impact || '';
                      const source = r.source || 'Unknown';
                      recommendationsData.push([p.pillar,(idx+1).toString(),r.title||'',r.priority||'',r.effort||'',impact,reasoning,source]);
                      recRowCount++;
                    });
                  }
                });
                const wsRecs = XLSX.utils.aoa_to_sheet(recommendationsData);
                wsRecs['!cols'] = [
                  { wch: 20 },
                  { wch: 4 },
                  { wch: 42 },
                  { wch: 12 },
                  { wch: 10 },
                  { wch: 46 },
                  { wch: 80 },
                  { wch: 44 }
                ];
                wsRecs['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: 7 } }];
                styleCell(wsRecs, 'A1', headerStyle);
                ['A3','B3','C3','D3','E3','F3','G3','H3'].forEach(c => styleCell(wsRecs, c, tableHeaderStyle));
                for (let i = 0; i < recRowCount; i++) {
                  const row = 4 + i;
                  ['A','B','C','D','E','F','G','H'].forEach(col => {
                    const cellRef = `${col}${row}`;
                    styleCell(wsRecs, cellRef, { ...dataStyleBase });
                    if (col === 'D') {
                      const pri = (wsRecs[cellRef].v || '').toLowerCase();
                      const priColor = pri === 'critical' ? '#DC3545' : pri === 'high' ? '#FD7E14' : pri === 'medium' ? '#FFC107' : pri === 'low' ? '#28A745' : '#6C757D';
                      wsRecs[cellRef].s = { ...wsRecs[cellRef].s, ...mkFill(priColor), font: { bold: true, color:{rgb:'FFFFFF'} } };
                    }
                    if (col === 'H') {
                      const val: string = wsRecs[cellRef].v || '';
                      const urlMatch = val.match(/https?:\/\/[^\s]+/);
                      if (urlMatch) {
                        wsRecs[cellRef].l = { Target: urlMatch[0] };
                        wsRecs[cellRef].s = { ...wsRecs[cellRef].s, font: { color: { rgb: '0563C1' }, underline: true } };
                      }
                    }
                  });
                }
                wsRecs['!autofilter'] = { ref: `A3:H${3 + recRowCount + 1}` };
                XLSX.utils.book_append_sheet(wb, wsRecs, 'Recommendations');

                // 5. Cohesive Recommendations (if present on assessment)
                const cohesive = (selected as any)?.cohesiveRecommendations || [];
                if (Array.isArray(cohesive) && cohesive.length) {
                  const cohesiveData: any[][] = [
                    ['Cross-Pillar Cohesive Recommendations'],
                    [],
                    ['#','Title','Priority','Effort','Impact','Recommendation','Source']
                  ];
                  cohesive.forEach((r: any, idx: number) => {
                    cohesiveData.push([
                      (idx+1).toString(),
                      r.title || '',
                      r.priority || '',
                      r.effort || '',
                      r.impact || r.business_impact || '',
                      r.reasoning || r.recommendation || r.details || '',
                      r.source || ''
                    ]);
                  });
                  const wsCoh = XLSX.utils.aoa_to_sheet(cohesiveData);
                  wsCoh['!cols'] = [ {wch:4},{wch:38},{wch:12},{wch:10},{wch:46},{wch:80},{wch:44} ];
                  wsCoh['!merges'] = [{ s:{r:0,c:0}, e:{r:0,c:6} }];
                  styleCell(wsCoh,'A1',headerStyle);
                  ['A3','B3','C3','D3','E3','F3','G3'].forEach(c=> styleCell(wsCoh,c,tableHeaderStyle));
                  for (let i=0;i<cohesive.length;i++) {
                    const row = 4 + i;
                    ['A','B','C','D','E','F','G'].forEach(col => {
                      const cellRef = `${col}${row}`;
                      styleCell(wsCoh, cellRef, { ...dataStyleBase });
                      if (col === 'C') {
                        const pri = (wsCoh[cellRef].v || '').toLowerCase();
                        const priColor = pri === 'critical' ? '#DC3545' : pri === 'high' ? '#FD7E14' : pri === 'medium' ? '#FFC107' : pri === 'low' ? '#28A745' : '#6C757D';
                        wsCoh[cellRef].s = { ...wsCoh[cellRef].s, ...mkFill(priColor), font: { bold: true, color:{rgb:'FFFFFF'} } };
                      }
                      if (col === 'G') {
                        const val: string = wsCoh[cellRef].v || '';
                        const urlMatch = val.match(/https?:\/\/[^\s]+/);
                        if (urlMatch) {
                          wsCoh[cellRef].l = { Target: urlMatch[0] };
                          wsCoh[cellRef].s = { ...wsCoh[cellRef].s, font: { color: { rgb: '0563C1' }, underline: true } };
                        }
                      }
                    });
                  }
                  wsCoh['!autofilter'] = { ref: `A3:G${3 + cohesive.length + 1}` };
                  XLSX.utils.book_append_sheet(wb, wsCoh, 'Cohesive Recs');
                }

                // Write the file with styling enabled
                const filename = `${assessmentName}_${selected?.id?.substring(0,8)}.xlsx`;
                XLSX.writeFile(wb, filename, { cellStyles: true });

              } catch (e) {
                console.error('Excel export failed', e);
                alert('Failed to generate Excel report. Check console for details.');
              }
            }}
            style={{
              padding:'0.6rem 1.25rem',
              background:'#0078d4',
              color:'#fff',
              border:'none',
              borderRadius:'4px',
              fontSize:'0.85rem',
              fontWeight:600,
              cursor:'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = '#106ebe'}
            onMouseOut={(e) => e.currentTarget.style.background = '#0078d4'}
            title="Download Excel report with multiple sheets (Overview, Pillar Scores, Concept Coverage, Recommendations)"
          >📥 Download Excel Report</button>
        )}
      </div>

      {pillarResults.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '3rem 2rem',
          background: '#f6f8fa',
          border: '1px solid #e1e4e8',
          borderRadius: '6px',
          margin: '2rem 0'
        }}>
          <p style={{ fontSize: '0.95rem', color: '#586069', margin: 0 }}>
            Scorecard will appear after analysis completes.
          </p>
        </div>
      )}
      {pillarResults.length > 0 && (
        <>
          {/* Cross-pillar alignment visualization removed per request; analysis artifacts moved to Analysis tab */}
          {/* Pillar Breakdown Section with Overall Score */}
          <div style={{ 
            marginBottom: '1.75rem',
            padding: '1.4rem 1.6rem',
            background: '#fff',
            border: '1px solid #e1e4e8',
            borderRadius: '8px'
          }}>
            {/* Header with Overall Score */}
            <div style={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '1.5rem',
              paddingBottom: '0.75rem',
              borderBottom: '2px solid #0078d4'
            }}>
              <h4 style={{ 
                margin: 0, 
                fontSize: '1.35rem', 
                fontWeight: 600,
                color: '#24292e'
              }}>Pillar Breakdown</h4>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ 
                  fontSize: '0.9rem', 
                  color: '#586069',
                  fontWeight: 500
                }}>Overall Architecture Score</span>
                <div style={{
                  fontSize: '2rem',
                  fontWeight: 700,
                  color: '#0078d4',
                  minWidth: '60px',
                  textAlign: 'center'
                }}>{overall}%</div>
              </div>
            </div>
            <div className="scorecard-grid">
            {pillarResults.map((pillar: PillarScore) => {
              const subcats = pillar.subcategories || {};
              const categories = pillar.categories || Object.keys(subcats).map(name => ({
                name,
                score: subcats[name]
              }));
              // Fallback: compute average if overall score is zero but we have categories
              let rawScore = pillar.overallScore ?? pillar.score ?? 0;
              if ((!rawScore || rawScore === 0) && categories.length) {
                const avg = categories.reduce((a: number, c: any) => a + (c.score || 0), 0) / categories.length;
                rawScore = Math.round(avg);
              }
              const pillarScore = rawScore;
              
              // Determine confidence level - if backend didn't provide it, infer from score
              let confidence = pillar.confidence || 'Low';
              if (!pillar.confidence) {
                // Infer confidence if not provided by backend (mirrors backend thresholds)
                if (pillarScore >= 80) confidence = 'High';
                else if (pillarScore >= 60) confidence = 'Medium';
                else confidence = 'Low';
              }
              
              const confidenceColor = confidence === 'High' ? '#28a745' : confidence === 'Medium' ? '#ffc107' : '#dc3545';
              const confidenceTooltip = (() => {
                // Unified tooltip explicitly describing rule + rationale
                const rule = 'Confidence bands: High ≥80, Medium 60–79, Low <60.';
                if (confidence === 'High') {
                  return `${rule} High confidence indicates strong coverage (≥75% concepts referenced), few gaps (≤2), and consistent pillar/subcategory alignment.`;
                } else if (confidence === 'Medium') {
                  return `${rule} Medium confidence indicates moderate coverage (≈60–74%) with limited gaps (<3). Adding architectural detail can raise confidence.`;
                } else {
                  return `${rule} Low confidence indicates sparse or fragmented evidence (<60% coverage) and/or multiple gaps (≥3). Provide more implementation detail to improve scoring defensibility.`;
                }
              })();
              
              const expanded = expandedSubcats[pillar.pillar] || false;
              const visibleCategories = expanded ? categories : categories.slice(0, 5);
              return (
                <div key={pillar.pillar} className="score-card">
                  <h3>
                    {pillar.pillar}
                    <span 
                      title={confidenceTooltip}
                      style={{ 
                        marginLeft: '.5rem',
                        padding: '.15rem .4rem',
                        backgroundColor: confidenceColor,
                        color: 'white',
                        fontSize: '.55rem',
                        fontWeight: 600,
                        borderRadius: '3px',
                        cursor: 'help'
                      }}
                    >
                      {confidence}
                    </span>
                  </h3>
                  <div className="score" style={{ color: confidenceColor }}>{pillarScore}</div>
                  <div style={{ marginTop:'.5rem' }}>
                    {visibleCategories.map((c: any) => {
                      const detail = pillar.subcategoryDetails?.[c.name];
                      const foundConcepts = detail?.found_concepts || detail?.evidence_found || [];
                      const missingConcepts = detail?.missing_concepts || [];
                      return (
                        <div key={c.name} className="subcat" style={{ marginBottom:'.35rem', display:'flex', alignItems:'center', justifyContent:'space-between', gap:'.5rem' }}>
                          <span style={{ fontSize:'.65rem', fontWeight:600, flex:1 }}>{c.name}</span>
                          <span style={{
                            fontSize:'.6rem',
                            fontWeight:700,
                            minWidth:'30px',
                            textAlign:'center',
                            padding:'.15rem .35rem',
                            lineHeight:1,
                            background:'#f1f5f9',
                            borderRadius:'4px',
                            border:'1px solid #e2e8f0'
                          }}>{c.score}</span>
                        </div>
                      );
                    })}
                    {categories.length > 5 && (
                      <button
                        type="button"
                        onClick={() => setExpandedSubcats(prev => ({ ...prev, [pillar.pillar]: !expanded }))}
                        style={{
                          marginTop:'.35rem',
                          background:'transparent',
                          border:'none',
                          padding:0,
                          cursor:'pointer',
                          color:'#0078d4',
                          fontSize:'.6rem',
                          fontWeight:600
                        }}
                      >
                        {expanded ? 'Collapse' : `+${categories.length - 5} more subcategories`}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
            </div>
            
            {/* How Scores Work - Footnote */}
            <div style={{ 
              fontSize: '0.75rem', 
              color: '#6c757d', 
              marginTop: '1.5rem',
              paddingTop: '1rem',
              borderTop: '1px solid #e1e4e8',
              lineHeight: '1.4'
            }}>
              <strong style={{ color: '#24292e' }}>How Scores Work:</strong> {scoringExplanation}
            </div>
          </div>
          
          {/* Gap-Based Recommendations - Visible penalties/normalizations */}
          {pillarResults.some((p: PillarScore) => p.normalizationApplied || (p.gapBasedRecommendations && p.gapBasedRecommendations.length > 0)) && (
            <div style={{ 
              marginBottom: '1.75rem',
              padding: '1.4rem 1.6rem',
              backgroundColor: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '8px'
            }}>
              <h4 style={{ 
                margin: '0 0 1rem', 
                color: '#856404', 
                fontSize: '1.35rem',
                fontWeight: 600,
                paddingBottom: '0.75rem',
                borderBottom: '2px solid #ffc107'
              }}>
                ⚠️ Hidden Gap Analysis
              </h4>
              <p style={{ fontSize:'.75rem', color:'#856404', margin:'0 0 1rem', lineHeight:'1.4' }}>
                Some pillar scores were normalized because subcategories summed beyond 100. This indicates areas with gaps or missing implementations that were penalized during scoring.
              </p>
              {pillarResults.map((pillar: PillarScore) => {
                const gapRecs = pillar.gapBasedRecommendations || [];
                if (!pillar.normalizationApplied && gapRecs.length === 0) return null;
                
                return (
                  <div key={pillar.pillar} style={{ 
                    marginBottom:'1rem',
                    padding:'.75rem',
                    backgroundColor:'white',
                    borderRadius:'4px',
                    border:'1px solid #ffeaa7'
                  }}>
                    <div style={{ fontSize:'.8rem', fontWeight:600, color:'#856404', marginBottom:'.5rem' }}>
                      {pillar.pillar} {pillar.normalizationApplied && (
                        <span style={{ fontSize:'.7rem', fontWeight:400 }}>
                          (Normalized from {pillar.rawSubcategorySum} → {pillar.overallScore ?? pillar.score})
                        </span>
                      )}
                    </div>
                    {gapRecs.map((rec, idx) => (
                      <div key={idx} style={{ fontSize:'.7rem', color:'#6c757d', marginTop:'.5rem', paddingLeft:'.75rem' }}>
                        <div style={{ fontWeight:600, color:'#856404' }}>{rec.title}</div>
                        <div style={{ marginTop:'.25rem' }}>{rec.reasoning}</div>
                        <div style={{ marginTop:'.25rem', fontStyle:'italic', color:'#28a745' }}>
                          💡 {rec.recommendation || rec.details}
                        </div>
                        {rec.points_recoverable && (
                          <div style={{ marginTop:'.25rem', fontSize:'.65rem', color:'#0078d4' }}>
                            Potential improvement: +{rec.points_recoverable} points
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          )}

          {/* Score Justification Section removed per request */}
          
          {/* Concept Coverage & Justification Section */}
          <div style={{ 
            marginBottom: '1.75rem',
            padding: '1.4rem 1.6rem',
            background: '#fff',
            border: '1px solid #e1e4e8',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              margin: '0 0 1.5rem',
              fontSize: '1.35rem',
              fontWeight: 600,
              color: '#24292e',
              paddingBottom: '0.75rem',
              borderBottom: '2px solid #0078d4'
            }}>Concept Coverage & Justification</h4>
            <p style={{ 
              fontSize: '0.9rem', 
              color: '#586069', 
              margin: '0 0 1.5rem', 
              lineHeight: '1.5' 
            }}>
              Review how each pillar's subcategories align with Azure Well-Architected best practices. 
              Each entry shows detected concepts (evidence found in your documentation), missing concepts (recommended practices not yet documented), 
              and a unique justification explaining the scoring rationale.
            </p>
          
          {/* Concept Coverage & Justification Panel */}
          <div style={{ marginTop:'0', border:'1px solid #e1e4e8', borderRadius:'8px', background:'#f6f8fa' }}>
            <div
              style={{
                display:'flex',
                justifyContent:'space-between',
                alignItems:'center',
                padding:'.6rem .75rem',
                background:'#f6f8fa',
                borderBottom: conceptCoveragePanelOpen ? '1px solid #e1e4e8' : 'none',
                cursor:'pointer'
              }}
              onClick={() => setConceptCoveragePanelOpen(prev => !prev)}
            >
              <div style={{ display:'flex', alignItems:'center', gap:'.5rem' }}>
                <span style={{ fontWeight:600, fontSize:'.75rem' }}>Concept Coverage & Justification</span>
                <span style={{ fontSize:'.55rem', color:'#586069' }}>({pillarResults.length} pillars)</span>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:'.5rem' }}>
                {/* Rescore Button */}
                {selected && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRescore();
                    }}
                    disabled={isRescoring}
                    style={{
                      background: isRescoring ? '#cccccc' : '#107c10',
                      border: 'none',
                      padding: '.35rem .6rem',
                      fontSize: '.55rem',
                      fontWeight: 600,
                      borderRadius: '4px',
                      cursor: isRescoring ? 'not-allowed' : 'pointer',
                      color: '#fff',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '.25rem'
                    }}
                    title="Recalculate with latest scoring logic"
                  >
                    <span>{isRescoring ? '⟳' : '🔄'}</span>
                    <span>{isRescoring ? 'Rescoring...' : 'Rescore'}</span>
                  </button>
                )}
                {conceptCoveragePanelOpen && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      const next = !coverageGlobalExpanded;
                      setCoverageGlobalExpanded(next);
                      setCoverageExpanded(() => {
                        const updated: Record<string, boolean> = {};
                        pillarResults.forEach((p: PillarScore) => { updated[p.pillar] = next; });
                        return updated;
                      });
                    }}
                    style={{
                      background:'transparent',
                      border:'1px solid #d0d7de',
                      padding:'.35rem .6rem',
                      fontSize:'.55rem',
                      fontWeight:600,
                      borderRadius:'4px',
                      cursor:'pointer',
                      color:'#0078d4'
                    }}
                    title="Expand or collapse all pillars in Concept Coverage panel"
                  >{coverageGlobalExpanded ? 'Collapse All' : 'Expand All'}</button>
                )}
                <span style={{ fontSize:'.65rem', fontWeight:600 }}>{conceptCoveragePanelOpen ? '▾' : '▸'}</span>
              </div>
            </div>
            {conceptCoveragePanelOpen && (
              <div style={{ padding:'0 .75rem 1rem' }}>
                {/* Rescore Status Messages */}
                {rescoreSuccess && (
                  <div style={{
                    padding: '0.5rem 0.75rem',
                    marginTop: '0.75rem',
                    marginBottom: '0.75rem',
                    backgroundColor: '#dff6dd',
                    border: '1px solid #107c10',
                    borderRadius: '4px',
                    color: '#0d5c0d',
                    fontSize: '.6rem',
                    fontWeight: 600
                  }}>
                    ✓ Assessment rescored successfully! All subcategories updated with latest logic.
                  </div>
                )}
                {rescoreError && (
                  <div style={{
                    padding: '0.5rem 0.75rem',
                    marginTop: '0.75rem',
                    marginBottom: '0.75rem',
                    backgroundColor: '#fde7e9',
                    border: '1px solid #d13438',
                    borderRadius: '4px',
                    color: '#a0260d',
                    fontSize: '.6rem',
                    fontWeight: 600
                  }}>
                    ✗ Error: {rescoreError}
                  </div>
                )}
                <p style={{ fontSize:'.6rem', color:'#555', margin:'0 0 1rem', paddingTop:'.75rem' }}>
                  Each subcategory lists detected concepts, missing concepts, and a unique justification sentence summarizing evidence and gaps.
                </p>
                {pillarResults.map((pillar: PillarScore) => {
              const details = pillar.subcategoryDetails || {};
              const entries = Object.values(details);
              if (entries.length === 0) return null;
                  const expanded = coverageExpanded[pillar.pillar] !== undefined ? coverageExpanded[pillar.pillar] : coverageGlobalExpanded;
                  const toggle = () => setCoverageExpanded(prev => ({ ...prev, [pillar.pillar]: !expanded }));
              return (
                <div key={pillar.pillar} style={{ marginBottom:'1rem', border:'1px solid #e1e4e8', borderRadius:'6px', background:'#fff' }}>
                  <div
                    onClick={toggle}
                    style={{ cursor:'pointer', padding:'.6rem .75rem', background:'#f6f8fa', display:'flex', justifyContent:'space-between', alignItems:'center' }}
                  >
                    <span style={{ fontSize:'.75rem', fontWeight:600, color:'#0078d4' }}>{expanded ? '▼' : '▶'} {pillar.pillar}</span>
                    <span style={{ fontSize:'.55rem', color:'#555' }}>{entries.length} subcategories</span>
                  </div>
                  {expanded && (
                    <div style={{ padding:'.6rem .75rem' }}>
                      {entries.map((d: any, idx: number) => {
                        const found = d.found_concepts || d.evidence_found || [];
                        const missing = d.missing_concepts || [];
                        return (
                          <div key={d.name} style={{ marginBottom:'.6rem', fontSize:'.6rem', lineHeight:1.25 }}>
                            <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'.15rem' }}>
                              <strong style={{ fontSize:'.6rem' }}>{d.name}</strong>
                                <span style={{ fontSize:'.55rem', color:'#444', fontWeight:600, background:'#eef2f7', padding:'.15rem .4rem', borderRadius:'4px', minWidth:'26px', textAlign:'center' }}>{d.final_score}</span>
                            </div>
                            <div style={{ display:'flex', flexWrap:'wrap', gap:'.75rem', alignItems:'flex-start' }}>
                              <div style={{ flex:'1 1 260px' }}>
                                <div style={{ display:'flex', alignItems:'center', gap:'.4rem', marginBottom:'.15rem' }}>
                                  <span style={{ fontWeight:600, color:'#28a745' }}>Found</span>
                                  <span style={{ fontSize:'.5rem', background:'#28a745', color:'#fff', padding:'.1rem .35rem', borderRadius:'10px' }}>{found.length}</span>
                                </div>
                                <div>{found.length ? found.join(', ') : <span style={{ fontStyle:'italic', color:'#666' }}>No detected concepts</span>}</div>
                              </div>
                              <div style={{ flex:'1 1 260px' }}>
                                <div style={{ display:'flex', alignItems:'center', gap:'.4rem', marginBottom:'.15rem' }}>
                                  <span style={{ fontWeight:600, color:'#dc3545' }}>Missing</span>
                                  <span style={{ fontSize:'.5rem', background:'#dc3545', color:'#fff', padding:'.1rem .35rem', borderRadius:'10px' }}>{missing.length}</span>
                                </div>
                                <div>{missing.length ? missing.join(', ') : <span style={{ fontStyle:'italic', color:'#666' }}>No explicit gaps identified</span>}</div>
                              </div>
                            </div>
                            {/* Human-friendly summary */}
                            {(d.human_summary || d.justification_text) && (
                              <div style={{ marginTop:'.3rem', background:'#f1f8ff', padding:'.4rem .5rem', borderLeft:'3px solid #0078d4', borderRadius:'3px', display:'flex', flexDirection:'column', gap:'.25rem' }}>
                                {d.human_summary && (
                                  <div style={{ fontSize:'.55rem', fontWeight:600, color: d.substantiated ? '#1b5e20' : '#8a6d3b' }}>
                                    {d.substantiated ? '✔ Evidence: ' : '⚠ No Direct Evidence: '} {d.human_summary}
                                  </div>
                                )}
                                {d.justification_text && (
                                  <div style={{ fontSize:'.5rem', color:'#044b94' }}>{d.justification_text}</div>
                                )}
                                {/* Collapsible expected concepts */}
                                {d.expected_concepts && d.expected_concepts.length > 0 && (
                                  <details style={{ fontSize:'.5rem' }}>
                                    <summary style={{ cursor:'pointer' }}>Expected Concepts ({d.expected_concepts.length})</summary>
                                    <div style={{ marginTop:'.25rem' }}>
                                      <span style={{ fontWeight:600 }}>All:</span> {d.expected_concepts.join(', ')}
                                    </div>
                                  </details>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
                  );
                })}
              </div>
            )}
          </div>
          </div>
          
          {/* Recommendations by Pillar Section */}
          <div style={{ 
            marginBottom: '1.75rem',
            padding: '1.4rem 1.6rem',
            background: '#fff',
            border: '1px solid #e1e4e8',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              margin: '0 0 1.5rem',
              fontSize: '1.35rem',
              fontWeight: 600,
              color: '#24292e',
              paddingBottom: '0.75rem',
              borderBottom: '2px solid #0078d4'
            }}>Recommendations by Pillar</h4>
            <p style={{ 
              fontSize: '0.9rem', 
              color: '#586069', 
              margin: '0 0 1.5rem', 
              lineHeight: '1.5' 
            }}>
              Actionable recommendations grouped by pillar, sorted by priority. 
              Each recommendation includes business impact, estimated effort, and links to official Azure Well-Architected documentation.
            </p>
          
          <div className="recs" style={{ marginTop:'0', border:'1px solid #e1e4e8', borderRadius:'8px', background:'#f6f8fa' }}>
            <div
              style={{
                display:'flex',
                justifyContent:'space-between',
                alignItems:'center',
                padding:'.6rem .75rem',
                background:'#f6f8fa',
                borderBottom: recommendationsPanelOpen ? '1px solid #e1e4e8' : 'none',
                cursor:'pointer'
              }}
              onClick={() => setRecommendationsPanelOpen(prev => !prev)}
            >
              <div style={{ display:'flex', alignItems:'center', gap:'.5rem' }}>
                <span style={{ fontWeight:600, fontSize:'.75rem' }}>Recommendations by Pillar</span>
                <span style={{ fontSize:'.55rem', color:'#586069' }}>({pillarResults.length} pillars)</span>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:'.5rem' }}>
                {recommendationsPanelOpen && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      const next = !recsGlobalExpanded;
                      setRecsGlobalExpanded(next);
                      setExpandedPillars(() => {
                        const updated: Record<string, boolean> = {};
                        pillarResults.forEach((p: PillarScore) => { updated[p.pillar] = next; });
                        return updated;
                      });
                    }}
                    style={{
                      background:'transparent',
                      border:'1px solid #d0d7de',
                      padding:'.35rem .6rem',
                      fontSize:'.55rem',
                      fontWeight:600,
                      borderRadius:'4px',
                      cursor:'pointer',
                      color:'#0078d4'
                    }}
                    title="Expand or collapse all pillars in Recommendations panel"
                  >{recsGlobalExpanded ? 'Collapse All' : 'Expand All'}</button>
                )}
                <span style={{ fontSize:'.65rem', fontWeight:600 }}>{recommendationsPanelOpen ? '▾' : '▸'}</span>
              </div>
            </div>
            {recommendationsPanelOpen && (
              <div style={{ padding:'0 .75rem 1rem' }}>
                <p style={{ fontSize:'.6rem', color:'#555', margin:'0 0 1rem', paddingTop:'.75rem' }}>
                  Each recommendation is prioritized and linked to relevant Azure Well-Architected Framework guidance.
                </p>
                {pillarResults.map((pillar: PillarScore) => {
              const pillarRecs = pillar.recommendations || [];
              if (pillarRecs.length === 0) return null;
              
              // Sort recommendations by priority: Critical > High > Medium > Low
              const priorityOrder: Record<string, number> = { 
                'critical': 1, 
                'high': 2, 
                'medium': 3, 
                'low': 4 
              };
              const sortedRecs = [...pillarRecs].sort((a, b) => {
                const aPriority = (a.priority || 'medium').toLowerCase();
                const bPriority = (b.priority || 'medium').toLowerCase();
                return (priorityOrder[aPriority] || 5) - (priorityOrder[bPriority] || 5);
              });
              
                  const pillarExpanded = expandedPillars[pillar.pillar] !== undefined ? expandedPillars[pillar.pillar] : recsGlobalExpanded;
              
                  return (
                <div key={pillar.pillar} style={{ marginBottom:'1.5rem', border:'1px solid #e1e4e8', borderRadius:'6px', overflow:'hidden' }}>
                  <div 
                    onClick={() => setExpandedPillars(prev => ({ ...prev, [pillar.pillar]: !pillarExpanded }))}
                    style={{ 
                      padding:'.75rem',
                      backgroundColor:'#f6f8fa',
                      cursor:'pointer',
                      display:'flex',
                      alignItems:'center',
                      justifyContent:'space-between',
                      userSelect:'none'
                    }}
                  >
                    <h5 style={{ margin:0, fontSize:'.85rem', color:'#0078d4', fontWeight:600 }}>
                      {pillarExpanded ? '▼' : '▶'} {pillar.pillar} ({pillarRecs.length} recommendation{pillarRecs.length > 1 ? 's' : ''})
                    </h5>
                  </div>
                  {pillarExpanded && (
                    <div style={{ padding:'1rem' }}>
                      {sortedRecs.map((rec: Recommendation, idx: number) => {
                    const priorityClass = (rec.priority || 'medium').toLowerCase();
                    const priorityColor = priorityClass === 'critical' ? '#dc3545' : priorityClass === 'high' ? '#fd7e14' : priorityClass === 'medium' ? '#ffc107' : '#28a745';
                    const reasoning = rec.reasoning || rec.insight || '';
                    // UI CHANGE: Remove Description section; always show Recommendation using description content.
                    // If reasoning empty, fallback to original recommendation fields.
                    const recommendation = reasoning || (rec as any).recommendation || rec.details || 'No recommendation available';
                    const source = rec.source || 'Unknown Subcategory';
                    
                    // Azure Learn URL mapping for Well-Architected subcategories
                    const azureDocsMap: Record<string, string> = {
                      // Reliability
                      'Reliability-Focused Design Foundations': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/simplify',
                      'Identify and Rate User and System Flows': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/identify-flows',
                      'Perform Failure Mode Analysis (FMA)': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis',
                      'Define Reliability and Recovery Targets': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics',
                      'Add Redundancy at Different Levels': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/redundancy',
                      'Implement a Timely and Reliable Scaling Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/scaling',
                      'Strengthen Resiliency with Self-Preservation and Self-Healing': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation',
                      'Test for Resiliency and Availability Scenarios': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/testing-strategy',
                      'Implement Structured, Tested, and Documented Disaster Plans': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
                      'Implement Structured, Tested, and Documented BCDR Plans': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
                      'Measure and Model the Solution\'s Health Indicators': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/monitoring',
                      // Reliability - Normalized backend names
                      'Simplicity & Efficiency': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/principles',
                      'Flow Identification & Criticality': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/identify-flows',
                      'Failure Mode Analysis': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/failure-mode-analysis',
                      'Reliability & Recovery Targets': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/metrics',
                      'Redundancy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/redundancy',
                      'Scaling Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/scaling',
                      'Self-Healing & Resilience Patterns': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/self-preservation',
                      'Resiliency & Chaos Testing': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/testing-strategy',
                      'BCDR Planning': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/disaster-recovery',
                      'Health Indicators & Monitoring': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/monitoring',
                      // Security
                      'Establish a Security Baseline': 'https://learn.microsoft.com/en-us/azure/well-architected/security/establish-baseline',
                      'Maintain a Secure Development Lifecycle': 'https://learn.microsoft.com/en-us/azure/well-architected/security/secure-development-lifecycle',
                      'Classify and Label Data Sensitivity': 'https://learn.microsoft.com/en-us/azure/well-architected/security/data-classification',
                      'Create Intentional Segmentation and Perimeters': 'https://learn.microsoft.com/en-us/azure/well-architected/security/segmentation',
                      'Implement Conditional Identity and Access Management': 'https://learn.microsoft.com/en-us/azure/well-architected/security/identity-access',
                      'Isolate, Filter, and Control Network Traffic': 'https://learn.microsoft.com/en-us/azure/well-architected/security/segmentation',
                      'Encrypt Data with Modern Methods': 'https://learn.microsoft.com/en-us/azure/well-architected/security/encryption',
                      'Harden Workload Components': 'https://learn.microsoft.com/en-us/azure/well-architected/security/harden-resources',
                      'Protect Application Secrets': 'https://learn.microsoft.com/en-us/azure/well-architected/security/application-secrets',
                      'Establish a Comprehensive Security Testing Regimen': 'https://learn.microsoft.com/en-us/azure/well-architected/security/test',
                      'Implement Holistic Threat Detection and Monitoring': 'https://learn.microsoft.com/en-us/azure/well-architected/security/monitor-threats',
                      'Define and Exercise Incident Response Procedures': 'https://learn.microsoft.com/en-us/azure/well-architected/security/incident-response',
                      // Operational Excellence
                      'Define standard practices to develop and operate workload': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices',
                      'Formalize operational tasks': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-operations-tasks',
                      'Formalize software ideation and planning': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-software-ideation',
                      'Enhance software development and quality assurance': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices',
                      'Use infrastructure as code': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/infrastructure-as-code-design',
                      'Build workload supply chain with pipelines': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/release-engineering-continuous-integration',
                      'Establish structured incident management': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/incident-response',
                      'Automate repetitive tasks': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/automate-tasks',
                      'Expand Observability and Operational Monitoring': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/observability',
                      // Cost Optimization
                      'Create a culture of financial responsibility': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/culture',
                      'Create and maintain a cost model': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/cost-model',
                      'Collect and review cost data': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/collect-review-cost-data',
                      'Set spending guardrails': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/set-spending-guardrails',
                      'Get the best rates from providers': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/get-best-rates',
                      'Align usage to billing increments': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/align-usage-to-billing-increments',
                      'Optimize component costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-component-costs',
                      'Optimize environment costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-environment-costs',
                      'Optimize flow costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-flow-costs',
                      'Optimize data costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-data-costs',
                      'Optimize code costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-code-costs',
                      'Optimize scaling costs': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-scaling-costs',
                      'Optimize personnel time': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/optimize-personnel-time',
                      'Consolidate resources and responsibility': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/consolidation',
                      // Performance Efficiency
                      'Performance Targets & SLIs/SLOs': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-targets',
                      'Capacity & Demand Planning': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/capacity-planning',
                      'Service & Architecture Selection': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/select-services',
                      'Data Collection & Telemetry': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/collect-performance-data',
                      'Performance Testing & Benchmarking': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/performance-test',
                      'Code & Runtime Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-code-infrastructure',
                      'Data Usage Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-data-performance',
                      'Critical Flow Optimization': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/prioritize-critical-flows',
                      'Operational Load Efficiency': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/respond-live-performance-issues',
                      'Live Issue Triage & Remediation': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/respond-live-performance-issues',
                      'Continuous Optimization & Feedback Loop': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/continuous-performance-optimize',
                      // Additional mapping for normalized agent titles
                      'Implement Proactive Scaling and Partitioning Strategy': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/optimize-scaling-costs',
                      // Pillar-level fallbacks for edge cases
                      'Reliability Best Practices': 'https://learn.microsoft.com/en-us/azure/well-architected/reliability/',
                      'Security Best Practices': 'https://learn.microsoft.com/en-us/azure/well-architected/security/',
                      'Cost Optimization Best Practices': 'https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/',
                      'Operational Excellence Best Practices': 'https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/',
                      'Performance Efficiency Best Practices': 'https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/'
                    };
                    const sourceUrl = azureDocsMap[source] || null;
                    
                    return (
                      <div key={idx} className="rec-card" style={{ marginBottom:'.75rem', position: 'relative' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem', marginBottom: '.75rem' }}>
                          <strong style={{ fontSize:'.8rem', flex: 1 }}>{rec.title}</strong>
                          <span style={{ 
                            padding: '.2rem .5rem', 
                            backgroundColor: priorityColor,
                            color: 'white',
                            fontSize: '.65rem',
                            fontWeight: 600,
                            borderRadius: '3px'
                          }}>
                            {rec.priority} Priority
                          </span>
                        </div>
                        
                        {/* Description removed per user request; content merged into Recommendation box */}
                        
                        <div className="recommendation-box" style={{ fontSize:'.7rem', marginBottom: '.55rem' }}>
                          <strong style={{ display:'block', fontWeight:600, marginBottom:'.25rem' }}>💡 Recommendation</strong>
                          <div style={{ color: '#333', lineHeight:'1.05rem' }}>{recommendation}</div>
                        </div>
                        
                        {/* Business Impact section with Impact, Effort, Source */}
                        <div className="business-impact-box" style={{ marginTop: '.5rem', fontSize: '.7rem' }}>
                          <strong style={{ display:'block', fontWeight:600, marginBottom:'.25rem' }}>📊 Business Impact</strong>
                          <div style={{ lineHeight:'1.05rem' }}>
                            {(rec as any).business_impact || rec.impact}
                            <div style={{ marginTop:'.35rem', color:'#555' }}>
                              <strong>Effort:</strong> {rec.effort} {' | '} <strong>Source:</strong>{' '}
                              {sourceUrl ? (
                                <a href={sourceUrl} target="_blank" rel="noopener noreferrer" style={{ color:'#0078d4', textDecoration:'underline' }}>{source}</a>
                              ) : (
                                source
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {/* Cross-pillar considerations intentionally omitted from Scorecard per user request (moved to Analysis tab) */}
                      </div>
                      );
                    })}
                    </div>
                  )}
                </div>
                  );
                })}
              </div>
            )}
            
            {recommendationsPanelOpen && allRecommendations.length === 0 && (
              <p style={{ fontSize:'.75rem', color:'#666', padding:'0 .75rem 1rem' }}>No recommendations generated yet.</p>
            )}
          </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ResultsScorecardTab;
