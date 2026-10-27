"""Bounded negative controls for supplemental duplicate-record authentication."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tested_supplement_gate', HERE / 'authenticate_block17_supplement.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

metadata = {'initial_missing': 1, 'reserved_active_task_ids': [], 'events': [
    {'task_id': 'synthetic', 'event': 'started'},
    {'task_id': 'synthetic', 'event': 'duplicate_identical_not_overwritten', 'record_hash': 'a' * 64}]}
records = {'synthetic': 'a' * 64}
checkpoints = dict(records)
events, skipped = gate.completion_agreement(metadata, records, checkpoints)
assert len(events) == 1 and events[0]['event'] == 'duplicate_identical_not_overwritten' and skipped == []
cases = []

def rejected(name, body, census=records, checkpoint=checkpoints):
    try:
        gate.completion_agreement(body, census, checkpoint)
    except ValueError as error:
        cases.append({'case': name, 'rejected': True, 'reason': str(error)})
    else:
        raise AssertionError('Accepted invalid evidence: ' + name)

rejected('duplicate_checkpoint_hash_differs', metadata, checkpoint={'synthetic': 'b' * 64})
rejected('duplicate_final_census_hash_differs', metadata, census={'synthetic': 'b' * 64})
bad = copy.deepcopy(metadata); bad['events'][1]['record_hash'] = 'b' * 64
rejected('completion_event_hash_differs', bad)
bad = copy.deepcopy(metadata); bad['events'].pop()
rejected('unresolved_started_task', bad)
bad = copy.deepcopy(metadata); bad['events'].pop(0)
rejected('completion_has_no_start', bad)
bad = copy.deepcopy(metadata); bad['reserved_active_task_ids'] = ['synthetic']
rejected('supplemental_event_uses_reserved_task', bad)
bad = copy.deepcopy(metadata); bad['events'][1]['event'] = 'unrecognized_completion'
rejected('unknown_event_type', bad)
two_records = {'synthetic': 'a' * 64, 'other': 'c' * 64}
bad = copy.deepcopy(metadata); bad['initial_missing'] = 2
rejected('truncated_terminal_membership', bad, census=two_records, checkpoint=two_records)
bad = copy.deepcopy(metadata); bad['initial_missing'] = 2; bad['reserved_active_task_ids'] = ['other', 'other']
rejected('duplicate_reserved_membership', bad, census=two_records, checkpoint=two_records)
bad = copy.deepcopy(metadata); bad['events'].insert(0, {'task_id': 'synthetic', 'event': 'skip_existing'})
rejected('started_after_skip_existing', bad)
report = {'schema': 'komorebi.block17.supplement-agreement-negative-controls.v1',
          'gate_sha256': hashlib.sha256((HERE / 'authenticate_block17_supplement.py').read_bytes()).hexdigest(),
          'valid_duplicate_completion_passed': True, 'negative_controls': cases,
          'compiler_dispatcher_program_calls': 0, 'evaluation_target_access': False,
          'scope': 'Synthetic event and hash dictionaries only; no live records, grids, scanner changes or process-history equivalence test.',
          'overall_pass': True}
out = HERE.parent / 'later-source-audit/supplement_agreement_negative_controls.json'
out.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
print(json.dumps({'report': str(out), 'negative_controls': len(cases), 'overall_pass': True}))
