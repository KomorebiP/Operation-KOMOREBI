"""Reproduce bounded acceptance defects in the retained Block 24 edition.

This is a counterexample harness, not a repaired runtime or model experiment.
Run from the collection root; requires NumPy and the preserved source package.
"""
from dataclasses import replace
from pathlib import Path
import json
import math
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / 'research/sric-external-admission'
sys.path.insert(0, str(PACKAGE))
from sric_real_lrm.adapters.fake import FakeProcedureLatentAdapter
from sric_real_lrm.dataset import deterministic_calibration_audit_split
from sric_real_lrm.fixture import make_fixture_records
from sric_real_lrm.pipeline import run_block24_pipeline
from sric_real_lrm.schemas import AuditConfig


class EmptyLogits(FakeProcedureLatentAdapter):
    def _score(self, task, trace, **kwargs):
        return replace(super()._score(task, trace, **kwargs), answer_logits=np.array([]))


class MissingFingerprint(FakeProcedureLatentAdapter):
    def model_fingerprint(self):
        return {}


class CorruptCapture(FakeProcedureLatentAdapter):
    bad_task = None
    corrupt_value = float('nan')

    def capture(self, task):
        observation = super().capture(task)
        if task.task_id == self.bad_task:
            logits = observation.answer_logits.copy()
            logits[0] = self.corrupt_value
            return replace(observation, answer_logits=logits)
        return observation


def compact(result):
    causal = result['causal_admission']
    replay = causal['summary']['replay_max_abs']
    return {
        'overall_status': result['overall_status'],
        'causal_status': causal['summary']['status'],
        'replay_max_abs': replay if math.isfinite(replay) else 'non-finite',
        'nonfinite_replay_rows': sum(not math.isfinite(row['replay_max_abs']) for row in causal['rows']),
        'audit_task_count': causal['summary']['task_count'],
        'real_checkpoint_evidence': result['claim_boundary']['real_checkpoint_evidence'],
    }


def main():
    frozen = AuditConfig.load(PACKAGE / 'configs/fake_fixture.json')
    records = make_fixture_records(48)
    full = run_block24_pipeline(FakeProcedureLatentAdapter(num_latents=frozen.num_latents, seed=frozen.seed), records, frozen)
    assert full['overall_status'] == 'CAUSALLY_VALIDATED'
    assert full['claim_boundary']['real_checkpoint_evidence'] is False
    # These changes bound diagnostic cost and isolate causal admission. They do
    # not change the frozen thresholds or the calibration/audit support split.
    focused = replace(frozen, bootstrap_replicates=20, semantic_escalation=False,
                      truncation=False, run_mode_controls=False)
    support = deterministic_calibration_audit_split(records, seed=focused.seed,
                calibration_fraction=focused.causal_calibration_fraction)['audit']
    assert len(support) == 40
    cases = [('unaltered_fixture', FakeProcedureLatentAdapter(), None, None),
             ('empty_logits', EmptyLogits(), None, None),
             ('missing_fingerprint', MissingFingerprint(), None, None),
             ('nan_first_row', CorruptCapture(), support[0].task_id, float('nan')),
             ('nan_later_row', CorruptCapture(), support[1].task_id, float('nan')),
             ('finite_replay_mismatch', CorruptCapture(), support[1].task_id, 1000.0)]
    observations = {'unmodified_full_fixture': compact(full)}
    for name, adapter, task_id, value in cases:
        if task_id is not None:
            adapter.bad_task, adapter.corrupt_value = task_id, value
        observations[name] = compact(run_block24_pipeline(adapter, records, focused))
    for name in ['unaltered_fixture', 'empty_logits', 'missing_fingerprint', 'nan_later_row']:
        assert observations[name]['overall_status'] == 'CONTENT_SPECIFIC', name
    for name in ['nan_first_row', 'finite_replay_mismatch']:
        assert observations[name]['overall_status'] == 'ADAPTER_INVALID', name
    assert observations['nan_later_row']['nonfinite_replay_rows'] == 1
    assert observations['nan_later_row']['replay_max_abs'] == 0.0
    assert observations['missing_fingerprint']['real_checkpoint_evidence'] is True
    assert observations['unaltered_fixture']['real_checkpoint_evidence'] is False
    print(json.dumps({'status': 'EXPECTED_DEFECTS_REPRODUCED',
                      'source_revision': '91ed38283ad924cd56f0b0179f41ec8d19acb00c',
                      'cases': observations, 'real_model_executed': False}, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
