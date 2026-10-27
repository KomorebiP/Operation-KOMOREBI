#!/usr/bin/env python3
"""Read-only, stdlib saved-score verifier. It never imports or runs the solver."""
import argparse
import csv
from datetime import datetime
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

SOURCE = 'Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip'
RESULT = 'ARC_AGI2_Block17_public_evaluation_results_2026-10-09.zip'
HISTORY = 'HISTORICAL_TRAINING_REPLAY_EVIDENCE.zip'
PINS = {
    SOURCE: '457d66c2a45e729a3b4db9bae55a19d4f016f4a602090b82cb9e3380be3cd1b0',
    RESULT: '4cd329e06ec327ab320d803d6c6cc16a9244b93f50ab462ed25a968949dadf09',
    HISTORY: '202b3e0af9774271743ec2a8aeba05af4c466ac802c17593f12cd735a0aed6b9',
}
TRAINING_SHA = '4d44f937e2edafdb1b3327d1e6e0f5084a5592eed4431db16cc27c578da8dad4'
POLICIES = ('typed_recent', 'typed_supported')
BASE = 'arc-evidence/fullbank-public-evaluation/'
CHALLENGES = 'arc-offline-data/arc-agi_evaluation_challenges.json'
SOLUTIONS = 'arc-offline-data/arc-agi_evaluation_solutions.json'
FIELDS = ['task_id', 'test_index', 'attempt_1_exact', 'attempt_2_exact',
          'attempt_2_incremental_exact', 'pass_at_2_exact', 'attempts_identical',
          'expected_height', 'expected_width', 'attempt_1_height', 'attempt_1_width',
          'attempt_2_height', 'attempt_2_width']


class InvalidRelease(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise InvalidRelease(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse(data):
    return json.loads(data, object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          InvalidRelease('non-finite JSON number: ' + value)))


def seal(value, name):
    need(isinstance(value, dict), name + ': object required')
    supplied = value.get('content_hash')
    need(isinstance(supplied, str) and supplied == digest(canonical(
        {key: val for key, val in value.items() if key != 'content_hash'})),
        name + ': invalid semantic seal')


def manifest(data, *, leaf_only=False):
    result = {}
    for line in data.decode('utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'([0-9a-f]{64}) [ *](.+)', line)
        need(match is not None, 'invalid SHA256 manifest line')
        sha, name = match.groups()
        path = PurePosixPath(name)
        need(not path.is_absolute() and '..' not in path.parts and
             str(path) == name and '\\' not in name, 'unsafe manifest path')
        if leaf_only:
            need(len(path.parts) == 1 and ':' not in name, 'root manifest entries must be leaf names')
        need(name not in result, 'duplicate manifest path: ' + name)
        result[name] = sha
    need(bool(result), 'empty SHA256 manifest')
    return result


def stat_key(path):
    st = path.stat()
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns


def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class Members:
    """Selected member reads are CRC checked by zipfile and manifest authenticated."""
    def __init__(self, archive):
        self.archive = archive
        entries = archive.infolist()
        self.names = {entry.filename for entry in entries}
        need(len(self.names) == len(entries), 'duplicate ZIP member')
        for name in self.names:
            p = PurePosixPath(name)
            need(not p.is_absolute() and '..' not in p.parts and str(p) == name and
                 '\\' not in name, 'unsafe ZIP member path')
        info = archive.getinfo('SHA256SUMS.txt')
        need(info.file_size <= 1024 * 1024, 'inner manifest too large')
        self.hashes = manifest(archive.read(info))
        need(set(self.hashes) == self.names - {'SHA256SUMS.txt'},
             'inner manifest member coverage differs')
        self.opened_solutions = False
        self.predictions_authenticated = False
        self.identities = {}

    def read(self, name):
        if name == SOLUTIONS:
            need(self.predictions_authenticated, 'solutions before BOTH predictions authenticated')
            self.opened_solutions = True
        need(name in self.hashes, 'missing authenticated member: ' + name)
        need(self.archive.getinfo(name).file_size <= 64 * 1024 * 1024,
             'selected JSON/CSV member exceeds bounded read limit')
        data = self.archive.read(name)
        sha = digest(data)
        need(sha == self.hashes[name], 'inner member SHA mismatch: ' + name)
        self.identities[name] = {'bytes': len(data), 'sha256': sha}
        return data

    def json(self, name):
        return parse(self.read(name))

    def bind(self, reference, name):
        actual = self.identities[name]
        need(reference.get('sha256') == actual['sha256'], 'raw identity SHA mismatch: ' + name)
        if 'bytes' in reference:
            need(type(reference['bytes']) is int and reference['bytes'] == actual['bytes'],
                 'raw identity size mismatch: ' + name)


def grid(value, name):
    need(isinstance(value, list) and bool(value), name + ': grid must be nonempty')
    need(isinstance(value[0], list) and bool(value[0]), name + ': row must be nonempty')
    width = len(value[0])
    need(len(value) <= 30 and width <= 30, name + ': grid dimensions must be 1..30')
    need(all(isinstance(row, list) and len(row) == width for row in value), name + ': ragged grid')
    need(all(type(cell) is int and 0 <= cell <= 9 for row in value for cell in row),
         name + ': cells must be integer colors 0..9')


def same(actual, expected, name):
    """Strict counts/booleans and structure; numerical fractions allow roundoff only."""
    if isinstance(expected, dict):
        need(isinstance(actual, dict) and set(actual) == set(expected), name + ': fields differ')
        for key in expected:
            same(actual[key], expected[key], name + '.' + key)
    elif type(expected) is float:
        need(type(actual) in (int, float) and abs(actual - expected) <= 1e-15,
             name + ': fraction differs')
    else:
        need(type(actual) is type(expected) and actual == expected, name + ': value differs')


def calculate(challenges, solutions, submission):
    """Independent full-grid comparisons; no saved scorer function is called."""
    first = second = second_only = identical = attempt2 = whole1 = whole2 = 0
    mean1 = mean2 = Fraction(0)
    per_task, rows = {}, []
    for task in sorted(challenges):
        n = len(challenges[task]['test'])
        p1 = p2 = 0
        for index, target in enumerate(solutions[task]):
            pair = submission[task][index]
            a, b = pair['attempt_1'], pair['attempt_2']
            one, two = a == target, b == target
            combined, increment, equal = one or two, two and not one, a == b
            first += one; attempt2 += two; second += combined
            second_only += increment; identical += equal; p1 += one; p2 += combined
            rows.append(dict(zip(FIELDS, [task, index, one, two, increment, combined, equal,
                len(target), len(target[0]), len(a), len(a[0]), len(b), len(b[0])])))
        whole1 += p1 == n; whole2 += p2 == n
        mean1 += Fraction(p1, n); mean2 += Fraction(p2, n)
        per_task[task] = {'test_outputs': n, 'pass_at_1_exact_outputs': p1,
            'pass_at_2_exact_outputs': p2, 'pass_at_1_fraction': p1/n,
            'pass_at_2_fraction': p2/n, 'whole_task_pass_at_1_exact': p1 == n,
            'whole_task_pass_at_2_exact': p2 == n}
    tasks, outputs = len(challenges), len(rows)
    mean1 /= tasks; mean2 /= tasks
    stats = {'tasks': tasks, 'test_outputs': outputs,
        'output_weighted_pass_at_1': {'exact': first, 'total': outputs, 'fraction': first/outputs},
        'output_weighted_pass_at_2': {'exact': second, 'total': outputs, 'fraction': second/outputs},
        'whole_task_pass_at_1': {'exact': whole1, 'total': tasks},
        'whole_task_pass_at_2': {'exact': whole2, 'total': tasks},
        'task_mean_pass_at_1_fraction': float(mean1), 'task_mean_pass_at_2_fraction': float(mean2),
        'attempt_2_exact_outputs': attempt2, 'attempt_2_incremental_exact_outputs': second_only,
        'identical_attempt_outputs': identical, 'per_task': per_task}
    return stats, rows, mean1, mean2


def verify_result(archive, dimensions=(120, 172), expected=(1, 2, 2, Fraction(1, 60))):
    m = Members(archive)
    freeze_name, audit_name = BASE+'predictions_before_scoring.json', BASE+'independent_scoring_audit.json'
    freeze, audit = m.json(freeze_name), m.json(audit_name)
    seal(freeze, 'freeze'); seal(audit, 'audit')
    need(freeze.get('schema') == 'komorebi.block17.public-evaluation-pre-score-freeze.v1', 'freeze schema')
    need(audit.get('schema') == 'komorebi.block17.fresh-public-evaluation-independent-audit.v1', 'audit schema')
    need(freeze.get('targets_opened') is False and freeze.get('both_predictions_authenticated') is True,
         'freeze label-order assertions')
    need(audit.get('both_predictions_saved_and_authenticated_before_labels') is True and
         audit.get('integrity_pass') is True and audit.get('membership_complete') is True and
         audit.get('frozen_source_files_unchanged') is True and
         audit.get('no_champion_fallback') is True, 'audit integrity assertions')
    need(freeze.get('policy_sequence') == list(POLICIES) and
         freeze.get('primary_policy') == audit.get('primary_policy') == POLICIES[0] and
         freeze.get('secondary_control_policy') == audit.get('secondary_control_policy') == POLICIES[1] and
         set(freeze['policies']) == set(audit['policy_results']) == set(POLICIES), 'fixed policy membership')
    for obj in (freeze, audit):
        need((obj.get('tasks'), obj.get('test_outputs')) == dimensions, 'reported benchmark membership')
    need(datetime.fromisoformat(audit['targets_first_scoring_started_utc']) >
         datetime.fromisoformat(freeze['frozen_at_utc']), 'recorded scoring precedes prediction freeze')
    m.bind(audit['pre_score_freeze'], freeze_name)
    need(audit['pre_score_freeze']['content_hash'] == freeze['content_hash'], 'audit freeze seal binding')
    need(freeze['inputs']['census']['sha256'] == audit['census']['sha256'] and
         freeze['inputs']['census']['bytes'] == audit['census']['bytes'], 'recorded census identities differ')
    census_name = BASE+'census.json'
    need(m.hashes.get(census_name) == audit['census']['sha256'] and
         archive.getinfo(census_name).file_size == audit['census']['bytes'], 'recorded census member binding')
    challenge = m.json(CHALLENGES)
    m.bind(freeze['inputs']['challenges'], CHALLENGES); m.bind(audit['challenges'], CHALLENGES)
    need(isinstance(challenge, dict) and len(challenge) == dimensions[0], 'challenge task membership')
    counts = {}
    for task, value in challenge.items():
        need(isinstance(value, dict) and isinstance(value.get('test'), list) and value['test'],
             'challenge test arity')
        counts[task] = len(value['test'])
        for example in value['test']:
            need(isinstance(example, dict) and set(example) == {'input'}, 'query labels in challenges')
            grid(example['input'], 'query input')
    need(sum(counts.values()) == dimensions[1], 'challenge output membership')
    predictions, scores, ledgers = {}, {}, {}
    for policy in POLICIES:
        fixed, result = freeze['policies'][policy], audit['policy_results'][policy]
        dispatch_name, submission_name = BASE+policy+'_dispatch.json', BASE+policy+'_submission.json'
        dispatch, submission = m.json(dispatch_name), m.json(submission_name)
        seal(dispatch, policy+' dispatch')
        m.bind(result['dispatch'], dispatch_name); m.bind(result['submission'], submission_name)
        need(fixed['dispatch_sha256'] == m.identities[dispatch_name]['sha256'] and
             fixed['submission_sha256'] == m.identities[submission_name]['sha256'], 'freeze prediction raw binding')
        need(dispatch['content_hash'] == fixed['dispatch_content_hash'] == result['dispatch_content_hash'],
             'dispatch seal binding')
        need(dispatch.get('schema') == 'komorebi.block17.autonomous_dispatch.v1' and
             dispatch.get('policy') == policy and dispatch.get('champion_fallback') is False and
             dispatch.get('label_access') == 'demonstrations_only', 'dispatch policy/label scope')
        for key in ('bank_hash', 'prediction_hash'):
            need(dispatch[key] == fixed[key] == audit['source_bindings'][key], 'source binding: '+key)
        need(dispatch['census_hash'] == fixed['census_hash'] == audit['census']['content_hash'], 'census seal binding')
        need(digest(canonical(submission)) == fixed['submission_hash'] == result['submission_hash'] and
             dispatch['submission'] == submission, 'dispatch/plain submission binding')
        need(isinstance(submission, dict) and set(submission) == set(challenge), 'submission task membership')
        need(set(dispatch['decisions']) == set(challenge), 'dispatch decision membership')
        for task, pairs in submission.items():
            need(isinstance(pairs, list) and len(pairs) == counts[task], 'submission output arity')
            for pair in pairs:
                need(isinstance(pair, dict) and set(pair) == {'attempt_1', 'attempt_2'}, 'two-attempt membership')
                grid(pair['attempt_1'], 'attempt_1'); grid(pair['attempt_2'], 'attempt_2')
        predictions[policy] = submission
        del dispatch
        score_name, ledger_name = BASE+policy+'_score.json', BASE+policy+'_ledger.csv'
        score, ledger_data = m.json(score_name), m.read(ledger_name)
        m.bind(result['score'], score_name); m.bind(result['ledger'], ledger_name)
        need(score.get('schema') == 'komorebi.arc.independent-offline-score.v1' and
             score.get('submission_valid') is True and score.get('submission_hashed_before_labels_opened') is True and
             score.get('solver_calls_in_scorer') == 0 and score.get('dataset_split') == 'evaluation', 'score scope assertions')
        for key, name in [('challenges', CHALLENGES), ('submission', submission_name)]:
            m.bind(score['inputs'][key], name)
        m.bind(score['per_test_ledger'], ledger_name)
        reader = csv.DictReader(io.StringIO(ledger_data.decode('utf-8'), newline=''))
        need(reader.fieldnames == FIELDS, 'CSV headers differ')
        rows = list(reader)
        keys = [(row.get('task_id'), row.get('test_index')) for row in rows]
        need(len(rows) == dimensions[1] and len(set(keys)) == len(keys), 'CSV output membership/duplicates')
        scores[policy], ledgers[policy] = score, rows
    # First query-solution member access occurs only after BOTH frozen predictions validate.
    m.predictions_authenticated = True
    solutions = m.json(SOLUTIONS)
    m.bind(audit['solutions_after_prediction_freeze'], SOLUTIONS)
    need(isinstance(solutions, dict) and set(solutions) == set(challenge), 'solution task membership')
    for task, targets in solutions.items():
        need(isinstance(targets, list) and len(targets) == counts[task], 'solution output arity')
        for target in targets:
            grid(target, 'solution')
    output = {}
    for policy in POLICIES:
        score, result = scores[policy], audit['policy_results'][policy]
        m.bind(score['inputs']['solutions'], SOLUTIONS)
        stats, rows, mean1, mean2 = calculate(challenge, solutions, predictions[policy])
        for key, value in stats.items():
            same(score[key], value, policy+' score.'+key)
        same(ledgers[policy], [{key: str(value) for key, value in row.items()} for row in rows],
             policy+' CSV all fields')
        for name, key in [('pass_at_1','output_weighted_pass_at_1'), ('pass_at_2','output_weighted_pass_at_2'),
                          ('whole_task_pass_at_1','whole_task_pass_at_1'), ('whole_task_pass_at_2','whole_task_pass_at_2')]:
            same(result[name], stats[key], policy+' audit.'+name)
        same(result['task_mean_pass_at_2_fraction'], float(mean2), policy+' audit.task_mean')
        same(result['second_attempt_incremental_exact'], stats['attempt_2_incremental_exact_outputs'], policy+' audit.increment')
        observed = (stats['output_weighted_pass_at_1']['exact'], stats['output_weighted_pass_at_2']['exact'],
                    stats['whole_task_pass_at_2']['exact'], mean2)
        need(observed == expected, 'release expected exact-grid metrics differ')
        output[policy] = {'pass_at_1': [observed[0], dimensions[1]], 'pass_at_2': [observed[1], dimensions[1]],
            'whole_task_pass_at_2': [observed[2], dimensions[0]], 'task_mean_pass_at_2': str(mean2),
            'task_mean_pass_at_1': str(mean1), 'ledger_rows_verified': len(rows)}
    return {'integrity_pass': True, 'tasks': dimensions[0], 'test_outputs': dimensions[1],
        'policies': output, 'both_predictions_authenticated_before_solution_member_read': True,
        'retained_compiler_error_receipts': audit.get('retained_compiler_error_receipts'),
        'census_json_parsed': False, 'solver_imports_or_calls': 0,
        'limitations': audit.get('limitations', [])}


def verify(root, check_all_member_crcs=False, *, pins=None):
    root = Path(root).resolve()
    entries = manifest((root/'INPUTS_SHA256SUMS.txt').read_bytes(), leaf_only=True)
    need(all(name in entries for name in (SOURCE, RESULT, HISTORY)), 'required archive absent from handoff manifest')
    pins = PINS if pins is None else pins
    before = {}
    for name, sha in entries.items():
        path = root.joinpath(*PurePosixPath(name).parts)
        need(path.is_file(), 'missing handoff input: '+name)
        before[name] = stat_key(path)
        need(hash_file(path) == sha, 'handoff input SHA mismatch: '+name)
        if name in pins:
            need(sha == pins[name], 'pinned release archive SHA mismatch: '+name)
    with zipfile.ZipFile(root/RESULT) as archive:
        report = verify_result(archive)
    if check_all_member_crcs:
        for name in (SOURCE, RESULT, HISTORY):
            with zipfile.ZipFile(root/name) as archive:
                names = [member.filename for member in archive.infolist()]
                need(len(set(names)) == len(names), 'duplicate original ZIP member: '+name)
                for member in archive.infolist():
                    with archive.open(member) as stream:
                        while stream.read(1024*1024):
                            pass
    for name, identity in before.items():
        need(stat_key(root.joinpath(*PurePosixPath(name).parts)) == identity, 'handoff input changed during verification: '+name)
    report.update({'handoff_inputs_verified': len(entries), 'original_archives_all_member_crcs_checked': check_all_member_crcs,
                   'source_runtime_executed': False, 'source_archive_sha256': entries[SOURCE],
                   'results_archive_sha256': entries[RESULT], 'historical_evidence_archive_sha256': entries[HISTORY],
                   'verification_scope': 'Independent saved public-evaluation exact-grid scoring; historical replay is byte-authenticated, not rescored.'})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--check-all-member-crcs', action='store_true',
                        help='Optional streaming decompression of all three original ZIPs; no census JSON parsing.')
    args = parser.parse_args()
    try:
        report = verify(args.root, args.check_all_member_crcs)
    except Exception as error:
        print(json.dumps({'integrity_pass': False, 'error': type(error).__name__+': '+str(error)}, separators=(',', ':')))
        return 1
    print(json.dumps(report, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
