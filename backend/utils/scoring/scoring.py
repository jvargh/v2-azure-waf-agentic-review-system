# Migrated scoring module from src.utils.scoring.scoring
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import json, re
BASE_DIR = Path(__file__).parent
class PillarNotFoundError(FileNotFoundError):
    pass
@dataclass
class PracticeScore:
    code: str; title: str; weight: float; score: int; matched_signals: List[str]; total_signals: int; coverage: float; mode: str
    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "title": self.title, "weight": self.weight, "score": self.score, "matched_signals": self.matched_signals, "total_signals": self.total_signals, "coverage": round(self.coverage,3), "mode": self.mode}
@dataclass
class PillarScores:
    pillar: str; version: str; overall_maturity_percent: float; scale: Dict[str,str]; practice_scores: List[PracticeScore]; recommendations: List[Dict[str,Any]]; gap_results: List[Dict[str,Any]]; framework: Optional[str]=None
    def to_dict(self) -> Dict[str, Any]:
        return {"pillar": self.pillar,"version": self.version,"overall_maturity_percent": self.overall_maturity_percent,"scale": self.scale,"practice_scores": [p.to_dict() for p in self.practice_scores],"recommendations": self.recommendations,"gaps": self.gap_results}

def _pillar_file_name(pillar: str) -> str: return f"{pillar.lower()}_pillar.json"

def list_pillars() -> List[str]: return [p.name.split("_pillar.json")[0] for p in BASE_DIR.glob("*_pillar.json")]

def load_pillar(pillar: str) -> Dict[str, Any]:
    file_path = BASE_DIR / _pillar_file_name(pillar)
    if not file_path.exists(): raise PillarNotFoundError(f"Pillar definition not found: {file_path}")
    with file_path.open('r', encoding='utf-8') as f: return json.load(f)

def _phrase_present(text: str, phrase: str) -> bool:
    phrase=phrase.strip()
    if not phrase: return False
    return re.search(r"\b" + re.escape(phrase) + r"\b", text) is not None

def _match_scoring_signals(text: str, scoring_conf: Dict[str, Any]) -> Dict[str, Any]:
    signals: List[str] = scoring_conf.get("signals", [])
    weights: Dict[str,float] = scoring_conf.get("signal_weights", {}) or dict.fromkeys(signals,1.0)
    aliases: Dict[str,List[str]] = scoring_conf.get("signal_aliases", {}) or {}
    matched=[]; matched_weight=0.0; total_weight=sum(weights.get(s,1) for s in signals) or 0.0
    for sig in signals:
        base_terms=[sig.lower()]+[str(a).lower() for a in aliases.get(sig,[])]
        if any(_phrase_present(text,t) for t in base_terms): matched.append(sig); matched_weight+=weights.get(sig,1)
    coverage = matched_weight/total_weight if total_weight else 0.0
    return {"matched": matched, "matched_weight": matched_weight, "total_weight": total_weight, "coverage": coverage}

def _score_from_coverage(mode: str, coverage: float, any_matched: bool, full_match: bool) -> int:
    if not any_matched: return 0
    if mode == 'proportional': return int(round(coverage*5))
    if mode == 'tiered':
        thresholds=[(1.0,5),(0.75,4),(0.5,3),(0.25,2),(0.0,1)]
        for t,sc in thresholds:
            if coverage>=t-1e-9 and (t<1.0 or full_match): return sc
        return 1
    if mode == 'binary': return 5 if full_match else (4 if coverage>=0.5 else 2)
    return int(round(coverage*5))

def _score_practice(practice: Dict[str,Any], text: str, override_weight: Optional[float]=None) -> PracticeScore:
    scoring_conf = practice.get('scoring')
    if scoring_conf:
        mode = scoring_conf.get('mode','proportional').lower(); match_info=_match_scoring_signals(text, scoring_conf)
        coverage=match_info['coverage']; any_matched=bool(match_info['matched']); full_match=coverage>=0.999
        score=_score_from_coverage(mode,coverage,any_matched,full_match); matched=match_info['matched']; total_signals=len(scoring_conf.get('signals',[]))
    else:
        signals: List[str] = practice.get('signals',[]); matched=[s for s in signals if _phrase_present(text,s.lower())]
        coverage=len(matched)/len(signals) if signals else 0.0; score=int(round(coverage*5)) if signals else 0; total_signals=len(signals); mode='legacy-proportional'
    return PracticeScore(code=practice.get('code'), title=practice.get('title',''), weight=float(override_weight if override_weight is not None else practice.get('weight',0)), score=score, matched_signals=matched, total_signals=total_signals, coverage=coverage, mode=mode)

def _collect_recommendations(practice: Dict[str,Any], ps: PracticeScore) -> List[Dict[str,Any]]:
    recs=[]
    for rec in practice.get('recommendations',[]):
        severity_raw = rec.get('severity') or rec.get('execution_priority') or rec.get('priority') or 5
        try: severity=int(severity_raw)
        except (TypeError,ValueError): severity=5
        if ps.score<=2 and severity<=2:
            norm={k:v for k,v in rec.items() if k not in ('priority','execution_priority')}; norm['severity']=severity; norm['practice']=ps.code; recs.append(norm)
    return recs

def _evaluate_gaps(text: str, gaps_def: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    import re as _re
    norm_text=_re.sub(r"\s+"," ", text.lower()); results=[]
    for gap in gaps_def:
        raw_patterns: List[str] = gap.get('patterns',[]); matched_patterns=[]; compiled=[]
        for raw in raw_patterns:
            raw_norm=_re.sub(r"\s+"," ", raw.strip().lower())
            if _re.search(r"[\(\)\|\[\]\?\+\*]", raw_norm): pattern_str=raw_norm
            else:
                tokens=raw_norm.split();
                if not tokens: continue
                escaped=[_re.escape(t) for t in tokens]; pattern_str=fr"\b{'\\s+'.join(escaped)}\b"
            try: compiled.append((raw,_re.compile(pattern_str,_re.IGNORECASE)))
            except _re.error: continue
        for original, regex in compiled:
            if regex.search(norm_text): matched_patterns.append(original)
        results.append({"id": gap.get('id'), "label": gap.get('label'), "detail": gap.get('detail'), "practice": gap.get('practice'), "matched": bool(matched_patterns), "matchedPatterns": matched_patterns, "recommendationHintKeywords": gap.get('recommendation_hint_keywords', [])})
    return results

def compute_pillar_scores(architecture_text: str, pillar: str='reliability') -> PillarScores:
    data=load_pillar(pillar); text=architecture_text.lower(); practice_scores=[]; recommendations=[]; total_weight=0.0; weighted_scores=0.0; weights_map: Dict[str,Any]=data.get('weights',{})
    for practice in data.get('practices',[]):
        code=practice.get('code'); override_weight=weights_map.get(code) if code and code in weights_map else None
        ps=_score_practice(practice,text,override_weight=override_weight); practice_scores.append(ps); total_weight+=ps.weight; weighted_scores+=ps.score*ps.weight; recommendations.extend(_collect_recommendations(practice,ps))
    overall_percent=(weighted_scores/(5*total_weight))*100 if total_weight else 0.0
    gap_results=_evaluate_gaps(text,data.get('gaps',[]))
    return PillarScores(pillar=data.get('pillar',pillar), version=data.get('version','1.0'), overall_maturity_percent=round(overall_percent,2), scale=data.get('scale',{}), practice_scores=practice_scores, recommendations=recommendations, gap_results=gap_results, framework=data.get('framework'))

def summarize_scores(scores: PillarScores) -> Dict[str,Any]:
    gaps=scores.gap_results; matched=[g for g in gaps if g.get('matched')]; unmatched=[g for g in gaps if not g.get('matched')]
    return {"pillar": scores.pillar, "overall_maturity_percent": scores.overall_maturity_percent, "practice_scores": [{"code": p.code, "score": p.score, "weight": p.weight, "matched_signals": p.matched_signals, "coverage": round(p.coverage,3), "mode": p.mode} for p in scores.practice_scores], "recommendations": scores.recommendations, "gaps": gaps, "matched_gap_count": len(matched), "unmatched_gap_count": len(unmatched), "framework": scores.framework}

def reliability_category_breakdown(scores: PillarScores) -> Dict[str,Any]:
    code_to_score={p.code: p.score for p in scores.practice_scores}
    def pct(code: str) -> float: return (code_to_score.get(code,0)/5.0)*100.0
    mappings={"Reliability-Focused Design Foundations": ["RE01","RE02","RE03"],"Reliability Objectives & Health Metrics": ["RE04","RE10"],"Resilient Architecture & Scaling Strategies": ["RE05","RE06","RE07"],"Reliability Testing & Chaos Validation": ["RE08"],"Recovery & Continuity Preparedness": ["RE09"]}
    categories={name: round(sum(pct(c) for c in codes)/len(codes),2) if codes else 0.0 for name,codes in mappings.items()}
    practice_details={p.code: p.title for p in scores.practice_scores}
    category_practices={name: [{"code": c, "title": practice_details.get(c,""), "percent": round((code_to_score.get(c,0)/5.0)*100.0,2)} for c in codes] for name,codes in mappings.items()}
    return {"pillar": scores.pillar, "overall_maturity_percent": scores.overall_maturity_percent, "categories": categories, "category_practices": category_practices}
__all__=["list_pillars","load_pillar","compute_pillar_scores","summarize_scores","reliability_category_breakdown","PillarScores","PracticeScore","PillarNotFoundError"]
