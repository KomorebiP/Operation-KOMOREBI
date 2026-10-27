#!/usr/bin/env python3
"""Bounded synthetic controls; no real archives, solver, or saved scorer imports."""
import copy
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('standalone_release_verifier', HERE/'verify_release.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
B = 'arc-evidence/fullbank-public-evaluation/'
C = 'arc-offline-data/arc-agi_evaluation_challenges.json'
S = 'arc-offline-data/arc-agi_evaluation_solutions.json'
P = ('typed_recent', 'typed_supported')
FIELDS = ['task_id', 'test_index', 'attempt_1_exact', 'attempt_2_exact',
          'attempt_2_incremental_exact', 'pass_at_2_exact', 'attempts_identical',
          'expected_height', 'expected_width', 'attempt_1_height', 'attempt_1_width',
          'attempt_2_height', 'attempt_2_width']


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sealed(value):
    result = copy.deepcopy(value)
    result['content_hash'] = sha(raw({k: v for k, v in result.items() if k != 'content_hash'}))
    return result


def csv_bytes(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


class Fixture:
    """Expected counts are analytical; never calls the verifier's calculate()."""
    def __init__(self):
        self.challenges, self.solutions, submission, per_task, rows = {}, {}, {}, {}, []
        for index in range(120):
            task = f'{index:08x}'
            n = 1 if index < 68 else 2
            self.challenges[task] = {'train': [{'input': [[1]], 'output': [[1]]}],
                                     'test': [{'input': [[1]]} for _ in range(n)]}
            targets, pairs = [], []
            for output in range(n):
                target = [[4, 5]] if index == 0 else [[7], [8]] if index == 1 else [[9, 8]] if output == 0 else [[2], [3]]
                a = copy.deepcopy(target) if index == 0 else [[0]] if index in (1, 2) else [[9], [8]] if output == 0 else [[2, 3]]
                b = copy.deepcopy(target) if index == 1 else [[0]]
                one, two, equal = index == 0, index == 1, index == 2
                targets.append(target)
                pairs.append({'attempt_1': a, 'attempt_2': b})
                rows.append(dict(zip(FIELDS, map(str, [task, output, one, two, two,
                    one or two, equal, len(target), len(target[0]), len(a), len(a[0]), len(b), len(b[0])]))))
            self.solutions[task], submission[task] = targets, pairs
            per_task[task] = {'test_outputs': n, 'pass_at_1_exact_outputs': int(index == 0),
                'pass_at_2_exact_outputs': int(index in (0, 1)), 'pass_at_1_fraction': float(index == 0),
                'pass_at_2_fraction': float(index in (0, 1)), 'whole_task_pass_at_1_exact': index == 0,
                'whole_task_pass_at_2_exact': index in (0, 1)}
        stats = {'tasks': 120, 'test_outputs': 172,
            'output_weighted_pass_at_1': {'exact': 1, 'total': 172, 'fraction': 1/172},
            'output_weighted_pass_at_2': {'exact': 2, 'total': 172, 'fraction': 2/172},
            'whole_task_pass_at_1': {'exact': 1, 'total': 120},
            'whole_task_pass_at_2': {'exact': 2, 'total': 120},
            'task_mean_pass_at_1_fraction': 1/120, 'task_mean_pass_at_2_fraction': 1/60,
            'attempt_2_exact_outputs': 1, 'attempt_2_incremental_exact_outputs': 1,
            'identical_attempt_outputs': 1, 'per_task': per_task}
        self.submissions = {p: copy.deepcopy(submission) for p in P}
        self.stats = {p: copy.deepcopy(stats) for p in P}
        self.rows = {p: copy.deepcopy(rows) for p in P}
        self.dispatch_changes, self.freeze_changes, self.audit_changes = {}, {}, {}
        self.dispatch_submissions, self.broken_seals, self.raw_overrides = {}, set(), {}

    def archive(self):
        payload = {}

        def emit(name, value):
            payload[name] = self.raw_overrides.get(name, value if isinstance(value, bytes) else raw(value))

        def identity(name):
            return {'path': '/unavailable/historical/root/'+name, 'sha256': sha(payload[name]), 'bytes': len(payload[name])}

        def seal_emit(name, value, kind):
            obj = sealed(value)
            if kind in self.broken_seals:
                obj['content_hash'] = '0'*64
            emit(name, obj)
            return obj

        emit(C, self.challenges); emit(S, self.solutions)
        emit(B+'census.json', b'opaque synthetic census; forbidden to open\n')
        bank, prediction, census_seal = sha(b'bank'), sha(b'prediction'), sha(b'census semantic identity')
        dispatches, scores = {}, {}
        for p in P:
            sub, ledger = B+p+'_submission.json', B+p+'_ledger.csv'
            emit(sub, self.submissions[p]); emit(ledger, csv_bytes(self.rows[p]))
            dispatch = {'schema': 'komorebi.block17.autonomous_dispatch.v1', 'policy': p,
                'champion_fallback': False, 'label_access': 'demonstrations_only',
                'bank_hash': bank, 'prediction_hash': prediction, 'census_hash': census_seal,
                'submission': self.dispatch_submissions.get(p, self.submissions[p]),
                'decisions': {t: [] for t in self.challenges}}
            dispatch.update(self.dispatch_changes.get(p, {}))
            dispatches[p] = seal_emit(B+p+'_dispatch.json', dispatch, p+' dispatch')
            score = {'schema': 'komorebi.arc.independent-offline-score.v1', 'submission_valid': True,
                'submission_hashed_before_labels_opened': True, 'solver_calls_in_scorer': 0,
                'dataset_split': 'evaluation', 'inputs': {'challenges': identity(C),
                    'solutions': identity(S), 'submission': identity(sub)}, 'per_test_ledger': identity(ledger),
                **self.stats[p]}
            emit(B+p+'_score.json', score); scores[p] = score
        freeze = {'schema': 'komorebi.block17.public-evaluation-pre-score-freeze.v1',
            'targets_opened': False, 'both_predictions_authenticated': True, 'policy_sequence': list(P),
            'primary_policy': P[0], 'secondary_control_policy': P[1], 'tasks': 120, 'test_outputs': 172,
            'frozen_at_utc': '2026-10-09T00:00:00+00:00',
            'inputs': {'census': identity(B+'census.json'), 'challenges': identity(C)}, 'policies': {}}
        for p in P:
            freeze['policies'][p] = {'dispatch_sha256': sha(payload[B+p+'_dispatch.json']),
                'submission_sha256': sha(payload[B+p+'_submission.json']),
                'dispatch_content_hash': dispatches[p]['content_hash'],
                'submission_hash': sha(raw(self.submissions[p])), 'bank_hash': bank,
                'prediction_hash': prediction, 'census_hash': census_seal}
        freeze.update(self.freeze_changes)
        fn = B+'predictions_before_scoring.json'
        freeze = seal_emit(fn, freeze, 'freeze')
        audit = {'schema': 'komorebi.block17.fresh-public-evaluation-independent-audit.v1',
            'both_predictions_saved_and_authenticated_before_labels': True, 'integrity_pass': True,
            'membership_complete': True, 'frozen_source_files_unchanged': True, 'no_champion_fallback': True,
            'primary_policy': P[0], 'secondary_control_policy': P[1], 'tasks': 120, 'test_outputs': 172,
            'targets_first_scoring_started_utc': '2026-10-09T00:00:01+00:00',
            'pre_score_freeze': {**identity(fn), 'content_hash': freeze['content_hash']},
            'census': {**identity(B+'census.json'), 'content_hash': census_seal},
            'challenges': identity(C), 'solutions_after_prediction_freeze': identity(S),
            'source_bindings': {'bank_hash': bank, 'prediction_hash': prediction}, 'policy_results': {}}
        for p in P:
            stat = self.stats[p]
            audit['policy_results'][p] = {k: identity(B+p+'_'+suffix) for k, suffix in
                [('dispatch', 'dispatch.json'), ('submission', 'submission.json'), ('score', 'score.json'), ('ledger', 'ledger.csv')]}
            audit['policy_results'][p].update({'dispatch_content_hash': dispatches[p]['content_hash'],
                'submission_hash': sha(raw(self.submissions[p])), 'pass_at_1': stat['output_weighted_pass_at_1'],
                'pass_at_2': stat['output_weighted_pass_at_2'], 'whole_task_pass_at_1': stat['whole_task_pass_at_1'],
                'whole_task_pass_at_2': stat['whole_task_pass_at_2'],
                'task_mean_pass_at_2_fraction': stat['task_mean_pass_at_2_fraction'],
                'second_attempt_incremental_exact': stat['attempt_2_incremental_exact_outputs']})
        audit.update(self.audit_changes)
        seal_emit(B+'independent_scoring_audit.json', audit, 'audit')
        sums = ''.join(sha(data)+'  '+name+'\n' for name, data in sorted(payload.items())).encode()
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in payload.items():
                z.writestr(name, data)
            z.writestr('SHA256SUMS.txt', sums)
        return stream.getvalue()


class GuardedZip(zipfile.ZipFile):
    def __init__(self, data):
        self.solution_reads = 0
        self.census_reads = 0
        self.opened = []
        super().__init__(io.BytesIO(data))

    def open(self, name, *args, **kwargs):
        name_text = name.filename if isinstance(name, zipfile.ZipInfo) else name
        self.opened.append(name_text)
        if name_text == S:
            self.solution_reads += 1
        if name_text == B+'census.json':
            self.census_reads += 1
            raise AssertionError('synthetic census must never be opened')
        return super().open(name, *args, **kwargs)


def run():
    cases = []

    def case(name, mutate=None, error=None, before_labels=False):
        f = Fixture()
        if mutate:
            mutate(f)
        with GuardedZip(f.archive()) as archive:
            try:
                result = V.verify_result(archive)
            except V.InvalidRelease as exc:
                if error is None or error not in str(exc):
                    raise AssertionError(name+': unexpected rejection '+str(exc)) from exc
                result = {'rejection': str(exc)}
            else:
                if error is not None:
                    raise AssertionError(name+': corruption accepted')
                assert result['policies'][P[0]]['pass_at_1'] == [1, 172]
                assert result['policies'][P[1]]['pass_at_2'] == [2, 172]
                assert result['policies'][P[0]]['whole_task_pass_at_2'] == [2, 120]
                assert result['policies'][P[1]]['task_mean_pass_at_2'] == '1/60'
                assert archive.opened.index(S) > max(archive.opened.index(B+p+'_submission.json') for p in P)
            assert archive.census_reads == 0
            if before_labels:
                assert archive.solution_reads == 0, name+': opened solutions before rejection'
            cases.append({'name': name, 'pass': True, 'solutions_member_opens': archive.solution_reads,
                          'census_member_opens': archive.census_reads, **({'rejection': result['rejection']} if error else {})})

    case('analytic_120_tasks_172_outputs_exact_shapes_and_identical_wrong_pair')
    for seal_name in ('freeze', 'audit', P[1]+' dispatch'):
        case('broken_'+seal_name.replace(' ', '_'), lambda f, s=seal_name: f.broken_seals.add(s), 'invalid semantic seal', True)
    case('second_policy_task_swap_with_120_members', lambda f: f.submissions[P[1]].__setitem__('ffffffff', f.submissions[P[1]].pop('00000000')), 'submission task membership', True)
    case('second_policy_test_arity', lambda f: f.submissions[P[1]]['00000044'].pop(), 'submission output arity', True)
    case('second_policy_missing_attempt', lambda f: f.submissions[P[1]]['00000000'][0].pop('attempt_2'), 'two-attempt membership', True)
    for name, value, error in [('boolean_cell', [[True]], 'integer colors'), ('color_10', [[10]], 'integer colors'),
                               ('ragged_grid', [[1], [1, 2]], 'ragged grid'), ('width_31', [[1]*31], 'dimensions'),
                               ('height_31', [[1]]*31, 'dimensions')]:
        case('second_policy_'+name, lambda f, v=value: f.submissions[P[1]]['00000000'][0].__setitem__('attempt_1', v), error, True)
    case('dispatch_plain_mismatch_after_rebinding', lambda f: f.dispatch_submissions.__setitem__(P[1], {}), 'dispatch/plain submission binding', True)
    case('dispatch_wrong_policy_after_resealing', lambda f: f.dispatch_changes.__setitem__(P[1], {'policy': P[0]}), 'dispatch policy/label scope', True)
    case('challenge_query_contains_output', lambda f: f.challenges['00000000']['test'][0].__setitem__('output', [[1]]), 'query labels', True)
    case('recorded_label_order_reversed', lambda f: f.audit_changes.__setitem__('targets_first_scoring_started_utc', '2026-10-08T00:00:00+00:00'), 'scoring precedes', True)
    case('duplicate_json_key_before_labels', lambda f: f.raw_overrides.__setitem__(C, b'{"x":1,"x":2}'), 'duplicate JSON key', True)
    case('nonfinite_json_before_labels', lambda f: f.raw_overrides.__setitem__(C, b'{"x":NaN}'), 'non-finite JSON', True)
    for field in FIELDS:
        case('CSV_'+field, lambda f, k=field: f.rows[P[1]][0].__setitem__(k, 'CORRUPTED'), 'CSV all fields')
    case('CSV_duplicate_output_row', lambda f: f.rows[P[1]].__setitem__(1, copy.deepcopy(f.rows[P[1]][0])), 'CSV output membership', True)
    case('score_equal_task_mean_uses_output_denominator', lambda f: f.stats[P[1]].__setitem__('task_mean_pass_at_2_fraction', 2/172), 'score.task_mean_pass_at_2_fraction')
    case('score_per_task_wrong_boolean', lambda f: f.stats[P[1]]['per_task']['00000000'].__setitem__('whole_task_pass_at_2_exact', False), 'whole_task_pass_at_2_exact')
    case('solution_task_swap_preserving_120_members', lambda f: f.solutions.__setitem__('ffffffff', f.solutions.pop('00000000')), 'solution task membership')
    try:
        V.manifest(('0'*64+'  nested/file.txt\n').encode(), leaf_only=True)
    except V.InvalidRelease as exc:
        assert 'leaf names' in str(exc)
        cases.append({'name': 'root_manifest_nested_path', 'pass': True, 'solutions_member_opens': 0, 'census_member_opens': 0, 'rejection': str(exc)})
    else:
        raise AssertionError('root nested path accepted')
    core = (HERE/'verify_release.py').read_bytes()
    own = Path(__file__).read_bytes()
    report = sealed({'schema': 'komorebi.block17.release-verifier-synthetic-controls.v1',
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'integrity_pass': True,
        'verifier': {'sha256': sha(core), 'bytes': len(core)}, 'test': {'sha256': sha(own), 'bytes': len(own)},
        'cases': cases, 'cases_passed': len(cases), 'cases_failed': 0,
        'fixture_tasks': 120, 'fixture_test_outputs': 172, 'policies': list(P),
        'analytic_expected': {'pass_at_1': [1, 172], 'pass_at_2': [2, 172], 'whole_task_pass_at_2': [2, 120],
                              'task_mean_pass_at_2': '1/60', 'identical_wrong_attempt_pairs': 1},
        'all_13_csv_fields_individually_corrupted': True,
        'corruption_rebinding': 'Every negative rebuilds inner manifest and dependent raw identities and semantic seals, except the intended broken seal.',
        'real_archives_read': 0, 'runtime_or_scorer_imports': 0, 'census_member_reads': 0,
        'scope': 'Small synthetic ZIPs only. Imports the standalone verifier under test, never its calculate function as fixture oracle.',
        'limitations': ['Does not rerun the real release verifier, source restoration, optional all-member CRC mode, solver, or historical scorer.',
                        'Static review covers target-member guard; selected raw-byte limits are not a bound on decoded/canonical Python memory.']})
    output = HERE/'verify_release_synthetic_controls.json'
    output.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'integrity_pass': True, 'cases_passed': len(cases), 'report': str(output),
                      'report_sha256': sha(output.read_bytes()), 'verifier_sha256': sha(core)}, sort_keys=True))


if __name__ == '__main__':
    run()
