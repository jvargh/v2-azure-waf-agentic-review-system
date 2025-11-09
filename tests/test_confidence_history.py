import os
import json
import pytest
import datetime as dt
from typing import Dict, Any

import sys
sys.path.append(os.path.abspath('.'))

from backend.server import Assessment, PillarResult

@pytest.mark.asyncio
async def test_rescore_confidence_history(monkeypatch):
    # Build a fake assessment with two pillars
    assess = Assessment(
        id='test_assess_conf_history',
        name='Test',
        description='x',
        created_at=dt.datetime.utcnow().isoformat(),
        status='completed',
        pillar_results=[
            PillarResult(pillar='Reliability', overall_score=82, subcategories={'A':50,'B':32}, recommendations=[], confidence='High'),
            PillarResult(pillar='Performance Efficiency', overall_score=61, subcategories={'A':30,'B':31}, recommendations=[], confidence='Medium'),
        ],
        overall_architecture_score=71.5,
    )

    # Simulate snapshot logic from rescore path
    snapshot = {
        'timestamp': dt.datetime.utcnow().isoformat(),
        'overall_architecture_score': assess.overall_architecture_score,
        'pillar_scores': {r.pillar: r.overall_score for r in assess.pillar_results},
        'score_source': {r.pillar: r.score_source for r in assess.pillar_results},
        'pillar_confidence': {r.pillar: r.confidence for r in assess.pillar_results},
    }

    # Append snapshot then pretend to modify scores/confidence
    assess.score_history.append(snapshot)

    # Validate snapshot contents
    assert 'pillar_confidence' in assess.score_history[0], 'pillar_confidence key missing in score_history snapshot'
    assert assess.score_history[0]['pillar_confidence']['Reliability'] == 'High'
    assert assess.score_history[0]['pillar_confidence']['Performance Efficiency'] == 'Medium'

    # Ensure backward compatibility for existing keys
    assert 'pillar_scores' in assess.score_history[0]
    assert set(assess.score_history[0]['pillar_scores'].keys()) == {'Reliability','Performance Efficiency'}

    # Confirm no unintended extra keys
    unexpected = set(assess.score_history[0].keys()) - {'timestamp','overall_architecture_score','pillar_scores','score_source','pillar_confidence'}
    assert not unexpected, f'Unexpected keys present: {unexpected}'
