#!/usr/bin/env python3
"""Package completed Block 17 public-evaluation evidence without solver calls.

Preparation does not run this script. At execution, all prediction authentication
and the explicit pre-score freeze are checked before the solution file is opened.
The complete census replaces intermediate checkpoints in the final ZIP. Source
archives are referenced through the previously verified training snapshot.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import zipfile

POLICIES = ('typed_recent', 'typed_supported')
EXPECTED_TASKS = 120
EXPECTED_OUTPUTS = 172
SOURCE_ARCHIVE_SHA = '457d66c2a45e729a3b4db9bae55a19d4f016f4a602090b82cb9e3380be3cd1b0'
TRAINING_PACKAGE_SHA = '4d44f937e2edafdb1b3327d1e6e0f5084a5592eed4431db16cc27c578da8dad4'
TRAINING_PACKAGE_NAME = 'ARC_AGI2_Block17_verified_training_replay_2026-10-09.zip'
FINAL_PACKAGE_NAME = 'ARC_AGI2_Block17_public_evaluation_results_2026-10-09.zip'


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_object(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=no_duplicates)
    if not isinstance(value, dict):
        raise ValueError(f'JSON object required: {path}')
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def identity(path):
    path = Path(path)
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size, 'sha256': sha256(path)}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def verify_seal(value, location):
    require(value.get('content_hash') == digest({k: v for k, v in value.items() if k != 'content_hash'}),
            f'semantic seal mismatch: {location}')


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.partial')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n',
                         encoding='utf-8')
    temporary.replace(path)


def source_is_unchanged(source_root, snapshot):
    current = {p.relative_to(source_root).as_posix(): p for p in source_root.rglob('*') if p.is_file()}
    require(set(current) == set(snapshot), 'source inventory differs from the frozen snapshot')
    for relative, receipt in snapshot.items():
        path = current[relative]
        require(path.stat().st_size == receipt['size'], f'source size changed: {relative}')
        require(path.stat().st_mtime_ns == receipt['mtime_ns'], f'source mtime changed: {relative}')
        require(sha256(path) == receipt['sha256'], f'source bytes changed: {relative}')
    return len(current)


def freeze_entry(freeze, policy):
    entries = freeze.get('policies', freeze.get('predictions'))
    require(isinstance(entries, dict) and set(entries) == set(POLICIES),
            'pre-score freeze must authenticate both predetermined policies')
    entry = entries[policy]
    require(isinstance(entry, dict), f'freeze policy entry is not an object: {policy}')
    required = {'dispatch_sha256', 'dispatch_content_hash', 'submission_sha256', 'submission_hash'}
    require(required <= set(entry), f'pre-score freeze lacks prediction hashes: {policy}')
    return entry


def pre_label_authentication(workspace, evaluation, challenges_path, census_path):
    """Everything in this function is checked before labels may be opened."""
    require(census_path.is_file(), 'complete final census is missing')
    freeze = read_object(evaluation / 'predictions_before_scoring.json')
    verify_seal(freeze, 'predictions_before_scoring.json')
    require(freeze.get('targets_opened') is False, 'freeze must explicitly record targets_opened=false')
    require(freeze.get('both_predictions_authenticated') is True,
            'freeze must explicitly record both_predictions_authenticated=true')
    unchanged = read_object(evaluation / 'source_unchanged_audit.json')
    require(unchanged.get('unchanged') is True and unchanged.get('changed_paths') == [],
            'source-unchanged audit did not pass')
    historical_path = workspace / 'arc-evidence/later-source-audit/block17_source_before.json'
    historical_snapshot = read_object(historical_path)
    selected_identity = freeze.get('source_snapshot')
    require(isinstance(selected_identity, dict), 'freeze lacks selected source-baseline identity')
    selected_path = Path(selected_identity['path']).resolve()
    require(identity(selected_path) == selected_identity,
            'selected source baseline differs from the authenticated freeze')
    snapshot = read_object(selected_path)
    require(set(snapshot) == set(historical_snapshot) and all(
        snapshot[name]['size'] == historical_snapshot[name]['size'] and
        snapshot[name]['sha256'] == historical_snapshot[name]['sha256']
        for name in snapshot), 'selected baseline does not preserve pinned source inventory and bytes')
    count = source_is_unchanged(workspace / 'arc-fullbank/block17', snapshot)
    require(unchanged.get('files_before') == count == unchanged.get('files_after'),
            'source-unchanged audit file counts differ')
    independent = read_object(evaluation / 'independent_scoring_audit.json')
    verify_seal(independent, 'independent_scoring_audit.json')
    require(independent.get('source_snapshot') == selected_identity,
            'independent audit selected a different source baseline')
    selected_copy = evaluation / 'authenticated_source_snapshot.json'
    require(selected_copy.resolve() != selected_path,
            'select a baseline outside the packaging evidence-copy path')
    shutil.copyfile(selected_path, selected_copy)
    require(sha256(selected_copy) == selected_identity['sha256'],
            'packaged source-baseline copy differs from authenticated snapshot')
    challenges = read_object(challenges_path)
    require(len(challenges) == EXPECTED_TASKS, 'challenge set must contain exactly 120 tasks')
    require(sum(len(t['test']) for t in challenges.values()) == EXPECTED_OUTPUTS,
            'challenge set must contain exactly 172 test outputs')
    require(all('output' not in example for task in challenges.values() for example in task['test']),
            'challenge test outputs must be absent')
    census_id = identity(census_path)
    challenge_id = identity(challenges_path)
    data = {}
    shared_census_hash = None
    shared_receipts = None
    for policy in POLICIES:
        dispatch_path = evaluation / (policy + '_dispatch.json')
        submission_path = evaluation / (policy + '_submission.json')
        audit = read_object(evaluation / (policy + '_dispatch_audit.json'))
        dispatch = read_object(dispatch_path)
        submission = read_object(submission_path)
        verify_seal(dispatch, dispatch_path.name)
        entry = freeze_entry(freeze, policy)
        require(entry['dispatch_sha256'] == sha256(dispatch_path), f'frozen dispatch bytes differ: {policy}')
        require(entry['dispatch_content_hash'] == dispatch['content_hash'], f'frozen dispatch seal differs: {policy}')
        require(entry['submission_sha256'] == sha256(submission_path), f'frozen submission bytes differ: {policy}')
        require(entry['submission_hash'] == digest(submission), f'frozen submission semantics differ: {policy}')
        require(submission == dispatch['submission'], f'plain submission differs from authenticated dispatch: {policy}')
        require(dispatch['policy'] == policy and dispatch['primary_policy'] == 'typed_recent',
                f'policy identity changed: {policy}')
        require(dispatch['champion_fallback'] is False and dispatch['label_access'] == 'demonstrations_only',
                f'prediction provenance differs: {policy}')
        require(set(submission) == set(challenges), f'submission task membership differs: {policy}')
        for task_id, rows in submission.items():
            require(len(rows) == len(challenges[task_id]['test']), f'output arity differs: {policy}:{task_id}')
            require(all(isinstance(r, dict) and set(r) == {'attempt_1', 'attempt_2'} for r in rows),
                    f'two-attempt schema differs: {policy}:{task_id}')
        flags = ('integrity_pass', 'raw_census_before_after_sha256_and_size_verified',
                 'streamed_semantic_census_seal_verified', 'all_record_content_and_task_bindings_verified',
                 'exact_task_and_test_membership_verified', 'all_banks_scope_verified', 'fresh_run_hash_verified')
        require(all(audit.get(flag) is True for flag in flags), f'dispatch authentication audit failed: {policy}')
        require(audit.get('records') == EXPECTED_TASKS and audit.get('test_outputs') == EXPECTED_OUTPUTS,
                f'dispatch census denominator differs: {policy}')
        require(audit['census_before_and_after']['sha256'] == census_id['sha256'] and
                audit['census_before_and_after']['bytes'] == census_id['bytes'], f'census bytes differ: {policy}')
        require(audit['challenges_before_and_after']['sha256'] == challenge_id['sha256'],
                f'challenge bytes differ: {policy}')
        require(audit['census_hash'] == dispatch['census_hash'], f'census semantic reference differs: {policy}')
        require(audit['prediction']['sha256'] == entry['dispatch_sha256'] and
                audit['prediction']['content_hash'] == entry['dispatch_content_hash'],
                f'output authentication audit differs: {policy}')
        require(audit['source_before_and_after']['prediction_hash'] == dispatch['prediction_hash'] and
                audit['source_before_and_after']['bank_hash'] == dispatch['bank_hash'],
                f'prediction source binding differs: {policy}')
        require(len(audit['error_receipts']) == audit['error_receipt_count'], f'error receipt count differs: {policy}')
        if shared_census_hash is None:
            shared_census_hash = audit['census_hash']
            shared_receipts = audit['compiler_receipts_by_task']
        else:
            require(shared_census_hash == audit['census_hash'], 'policies bind to different censuses')
            require(shared_receipts == audit['compiler_receipts_by_task'], 'policies retain different compiler receipts')
        data[policy] = {'dispatch': dispatch, 'submission': submission, 'audit': audit}
    supplemental_path = evaluation / 'supplemental_scan_metadata.json'
    supplemental = freeze.get('supplemental_execution')
    require(supplemental_path.is_file() == (supplemental is not None),
            'supplemental execution provenance is missing or inconsistent with the freeze')
    if supplemental is not None:
        agreement_path = evaluation / 'supplemental_final_record_agreement.json'
        require(identity(supplemental_path) == supplemental['metadata'] and
                identity(agreement_path) == supplemental['agreement'] and
                identity(evaluation / 'scan_process_completion.json') == supplemental['process_completion'],
                'supplemental receipt bytes differ from the pre-score freeze')
        metadata = read_object(supplemental_path)
        agreement = read_object(agreement_path)
        process = read_object(evaluation / 'scan_process_completion.json')
        verify_seal(metadata, supplemental_path.name)
        verify_seal(agreement, agreement_path.name)
        verify_seal(process, 'scan_process_completion.json')
        require(process.get('schema') == 'komorebi.block17.scan-process-completion.v1' and
                process.get('all_scans_and_assembly_stopped') is True and process.get('targets_opened') is False and
                process.get('source_budget_policy_changes') is False and
                process['content_hash'] == agreement['owning_session_completion_content_hash'],
                'owning-session completion receipt scope or seal differs')
        require(bool(metadata.get('completed_utc')), 'supplemental metadata is not terminal')
        require(agreement['content_hash'] == supplemental['agreement_content_hash'] and
                agreement.get('integrity_pass') is True and agreement.get('targets_opened') is False and
                agreement.get('every_supplemental_completion_including_duplicates_matches') is True,
                'supplemental final-record agreement did not pass')
        require(agreement['inputs']['metadata'] == supplemental['metadata'] and
                agreement['inputs']['process_completion'] == supplemental['process_completion'] and
                agreement['inputs']['census'] == census_id and agreement['census_content_hash'] == shared_census_hash,
                'supplemental agreement binds different metadata or census')
        require(metadata['run_hash'] == agreement['run_hash'] == data['typed_recent']['audit']['fresh_run_hash'] and
                metadata['code_hash'] == data['typed_recent']['audit']['source_before_and_after']['code_hash'] and
                metadata['bank_hash'] == data['typed_recent']['audit']['source_before_and_after']['bank_hash'] and
                metadata['limits'] == data['typed_recent']['audit']['fixed_limits'],
                'supplemental source, input run or limits differ')
        require(metadata.get('label_access') == 'demonstrations_only' and
                metadata.get('source_changes') is False and metadata.get('policy_changes') is False,
                'supplemental label or source/policy scope differs')
        gate_path = workspace / 'arc-evidence/scripts/authenticate_block17_supplement.py'
        scheduler_path = workspace / 'arc-evidence/scripts/supplement_block17_scan.py'
        require(agreement['gate_source']['sha256'] == sha256(gate_path) and
                metadata['scheduler_sha256'] == sha256(scheduler_path),
                'supplemental gate or scheduler source identity differs')
        spec = importlib.util.spec_from_file_location('package_supplement_gate', gate_path)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        gate.scanners_exited(evaluation / 'census.json')
        events, skipped = gate.completion_agreement(metadata, agreement['final_record_hashes'],
                                                  agreement['final_checkpoint_record_hashes'])
        require(events == agreement['completion_event_agreements'] and
                skipped == agreement['skip_existing_tasks'], 'supplemental event agreement did not reproduce')
        require(set(agreement['final_record_hashes']) == set(challenges) and
                set(agreement['final_checkpoint_identities']) == set(challenges),
                'supplemental agreement final membership differs')
        for checkpoint in agreement['final_checkpoint_identities'].values():
            require(identity(Path(checkpoint['path'])) == checkpoint,
                    'final checkpoint bytes changed after supplemental agreement')
        require(independent.get('supplemental_execution') == supplemental,
                'independent audit has different supplemental execution provenance')
    return freeze, unchanged, challenges, census_id, data


def verify_scores_after_freeze(evaluation, challenges, challenges_path, solutions_path, data, scorer_path):
    """Caller must already have authenticated both sealed predictions and freeze."""
    solutions = read_object(solutions_path)
    require(set(solutions) == set(challenges), 'solution task membership differs')
    require(sum(len(rows) for rows in solutions.values()) == EXPECTED_OUTPUTS,
            'solutions must contain exactly 172 outputs')
    spec = importlib.util.spec_from_file_location('package_independent_scorer', scorer_path)
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    scores = {}
    for policy in POLICIES:
        score_path = evaluation / (policy + '_score.json')
        ledger_path = evaluation / (policy + '_ledger.csv')
        stored = read_object(score_path)
        fresh, ledger = scorer.score(challenges, solutions, data[policy]['submission'])
        require(stored.get('dataset_split') == 'evaluation' and stored.get('solver_calls_in_scorer') == 0,
                f'scorer scope differs: {policy}')
        require(stored.get('submission_hashed_before_labels_opened') is True,
                f'score lacks prediction-before-labels receipt: {policy}')
        require(stored.get('tasks') == EXPECTED_TASKS and stored.get('test_outputs') == EXPECTED_OUTPUTS,
                f'score denominator differs: {policy}')
        require(stored['inputs']['submission']['sha256'] == sha256(evaluation / (policy + '_submission.json')),
                f'score binds to different prediction bytes: {policy}')
        require(stored['inputs']['challenges']['sha256'] == sha256(challenges_path),
                f'score challenge bytes differ: {policy}')
        require(stored['inputs']['solutions']['sha256'] == sha256(solutions_path), f'score label bytes differ: {policy}')
        require(stored['scorer_source_sha256'] == sha256(scorer_path), f'score source bytes differ: {policy}')
        require(all(stored.get(key) == value for key, value in fresh.items()), f'score did not reproduce: {policy}')
        with ledger_path.open('r', encoding='utf-8', newline='') as handle:
            csv_rows = list(csv.DictReader(handle))
        require(csv_rows == [{key: str(value) for key, value in row.items()} for row in ledger],
                f'per-output ledger did not reproduce: {policy}')
        require(stored['per_test_ledger']['sha256'] == sha256(ledger_path), f'ledger hash differs: {policy}')
        scores[policy] = stored
    independent = read_object(evaluation / 'independent_scoring_audit.json')
    verify_seal(independent, 'independent_scoring_audit.json')
    require(independent.get('integrity_pass') is True, 'independent scoring audit did not pass')
    require(independent.get('tasks') == EXPECTED_TASKS and independent.get('test_outputs') == EXPECTED_OUTPUTS,
            'independent scoring audit denominator differs')
    require(independent.get('both_predictions_saved_and_authenticated_before_labels') is True,
            'independent scoring audit lacks prediction-before-labels receipt')
    return scores


def make_readme(scores, data):
    lines = ['Komorebi ARC-AGI-2 Block 17 public-evaluation results', '2026-10-09 UTC', '',
             'Completed fresh full-bank compiler scan: 120 public tasks, 172 test outputs.',
             'Both policies were predetermined and authenticated before separate scoring.', '', 'RESULTS']
    for policy in POLICIES:
        score = scores[policy]
        first = score['output_weighted_pass_at_1']['exact']
        second = score['output_weighted_pass_at_2']['exact']
        whole = score['whole_task_pass_at_2']['exact']
        role = 'primary' if policy == 'typed_recent' else 'secondary control'
        lines.append(f'  {policy} ({role}): pass@1 {first}/172; pass@2 {second}/172 ({100*second/172:.4f}%); '
                     f'task-mean pass@2 {100*score["task_mean_pass_at_2_fraction"]:.4f}%; whole tasks {whole}/120.')
    errors = data['typed_recent']['audit']['error_receipt_count']
    lines += ['', 'Verified public-training cached-record dispatcher replay:',
              'typed_recent primary: 790/1076 exact pass@2 outputs (73.4201%).',
              'typed_supported secondary control: 846/1076 exact pass@2 outputs (78.6245%).',
              'These separately verified training results replay authenticated historical candidate records.',
              'They are not a fresh compiler search or hidden-test results.',
              '', f'Retained compiler error receipts: {errors}. Authentication passed independently of these errors.',
              'The dispatch audits retain every compiler receipt and the complete error array.', '',
              'SCOPE', 'This run freshly compiled all banks from demonstrations and test inputs.',
              'The external adapter then called the unchanged dispatcher per authenticated task.',
              'Both predictions were sealed and authenticated before target opening and scoring.',
              'No correctness-filtered champion was used. Frozen source bytes, size and mtime were verified.',
              'The public evaluation set was historically inspected in this project. These results',
              'are fresh frozen public-data execution, not a hidden competition score or a never-inspected holdout.', '',
              'SOURCE RESTORATION', f'The source archive is already included in {TRAINING_PACKAGE_NAME}.',
              f'Training snapshot SHA-256: {TRAINING_PACKAGE_SHA}',
              'Training snapshot reference: libfile_b4a96cf6d8008191b1b7b251e68cbd88',
              'Extract that snapshot, then restore its nested source with:',
              '  python -m zipfile -e arc-later-download/Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip arc-fullbank',
              f'Nested source archive SHA-256: {SOURCE_ARCHIVE_SHA}',
              'This result ZIP references the verified source archive rather than duplicating it.', '',
              'REPRODUCTION', 'After restoring the source, run from the extraction directory:',
              '  PYTHONDONTWRITEBYTECODE=1 python arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py '
              '--root arc-fullbank/block17 --challenges arc-offline-data/arc-agi_evaluation_challenges.json '
              '--census arc-evidence/fullbank-public-evaluation/census.json --output-dir fresh-replay --policy typed_recent',
              'Repeat sequentially with --policy typed_supported. Authenticate both outputs before any new scoring.',
              '', 'For a new full compiler scan, use a new output directory from the extraction root:',
              '  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 '
              'python arc-fullbank/block17/run_scan.py '
              '--challenges arc-offline-data/arc-agi_evaluation_challenges.json '
              '--include-new --workers 4 --output fresh-scan/census.json',
              'After that scan exits, dispatch its census with the adapter above, replacing the census path',
              'with fresh-scan/census.json. Preserve and authenticate both predictions before target opening.',
              '', 'To independently rescore the existing frozen primary submission without importing the solver:',
              '  PYTHONDONTWRITEBYTECODE=1 python arc-evidence/scripts/score_arc_submission.py '
              '--challenges arc-offline-data/arc-agi_evaluation_challenges.json '
              '--solutions arc-offline-data/arc-agi_evaluation_solutions.json '
              '--submission arc-evidence/fullbank-public-evaluation/typed_recent_submission.json '
              '--output fresh-score/typed_recent_score.json --ledger fresh-score/typed_recent_ledger.csv '
              '--label "Verified frozen Block17 public evaluation primary" --split evaluation',
              'For the separately frozen control:',
              '  PYTHONDONTWRITEBYTECODE=1 python arc-evidence/scripts/score_arc_submission.py '
              '--challenges arc-offline-data/arc-agi_evaluation_challenges.json '
              '--solutions arc-offline-data/arc-agi_evaluation_solutions.json '
              '--submission arc-evidence/fullbank-public-evaluation/typed_supported_submission.json '
              '--output fresh-score/typed_supported_score.json --ledger fresh-score/typed_supported_ledger.csv '
              '--label "Verified frozen Block17 public evaluation secondary control" --split evaluation', '',
              'PACKAGE', 'SHA256SUMS.txt covers every payload file. The detached package audit gives ZIP SHA-256,',
              'CRC verification, and per-member hash verification. The complete census replaces duplicate checkpoints.',
              'Scan logs, monitor observations, compiler audits, freeze, source snapshot and verification,',
              'provenance audits, streaming adapter, independent review, test and equivalence evidence are included.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    evaluation = workspace / 'arc-evidence/fullbank-public-evaluation'
    output = (args.output or workspace / FINAL_PACKAGE_NAME).resolve()
    require(not output.exists(), 'final ZIP already exists; choose a new output path explicitly')
    require(output.parent == workspace, 'final ZIP must be created directly in the workspace')
    required = ['census.json', 'predictions_before_scoring.json', 'source_unchanged_audit.json',
                'independent_scoring_audit.json', 'monitor_observations.jsonl']
    required += [policy + suffix for policy in POLICIES for suffix in
                 ('_dispatch.json', '_dispatch_audit.json', '_submission.json', '_score.json', '_ledger.csv')]
    for name in required:
        require((evaluation / name).is_file(), f'final evidence missing: {name}')
    challenges_path = workspace / 'arc-offline-data/arc-agi_evaluation_challenges.json'
    solutions_path = workspace / 'arc-offline-data/arc-agi_evaluation_solutions.json'
    scorer_path = workspace / 'arc-evidence/scripts/score_arc_submission.py'
    freeze, unchanged, challenges, census_id, data = pre_label_authentication(
        workspace, evaluation, challenges_path, evaluation / 'census.json')
    # This is the sole label-reading entry point, after both predictions and the explicit freeze pass.
    scores = verify_scores_after_freeze(evaluation, challenges, challenges_path, solutions_path, data, scorer_path)
    prior_verification_path = workspace / 'arc-evidence/later-source-audit/snapshot_package_verification.json'
    prior_verification = read_object(prior_verification_path)
    require(prior_verification['archive_sha256'] == TRAINING_PACKAGE_SHA and
            prior_verification['source_archive_sha256'] == SOURCE_ARCHIVE_SHA and
            prior_verification['all_entry_crc_verified'] is True and
            prior_verification['nested_source_crc_verified'] is True, 'verified source snapshot provenance differs')
    summary_path = workspace / 'arc-evidence/ARC_AGI2_offline_summary.json'
    summary = read_object(summary_path)
    require(summary['source_archive_sha256'] == SOURCE_ARCHIVE_SHA, 'summary source lineage differs')
    policy_scores = {}
    for policy, score in scores.items():
        policy_scores[policy] = {'pass1_exact_outputs': score['output_weighted_pass_at_1']['exact'],
            'pass2_exact_outputs': score['output_weighted_pass_at_2']['exact'], 'total_outputs': EXPECTED_OUTPUTS,
            'total_tasks': EXPECTED_TASKS, 'output_percent': 100*score['output_weighted_pass_at_2']['fraction'],
            'task_mean_pass2_percent': 100*score['task_mean_pass_at_2_fraction'],
            'whole_tasks': score['whole_task_pass_at_2']['exact']}
    summary['updated_utc'] = datetime.now(timezone.utc).isoformat()
    summary['fresh_public_evaluation'] = {'status': 'completed', 'tasks': EXPECTED_TASKS,
        'test_outputs': EXPECTED_OUTPUTS, 'scope': 'Fresh full-bank compiler scan and frozen deterministic dispatch on public evaluation.',
        'primary_policy': 'typed_recent', 'secondary_control_policy': 'typed_supported',
        'policies_frozen_before_scoring': list(POLICIES), 'policy_scores': policy_scores,
        'candidate_count': data['typed_recent']['audit']['candidates'],
        'retained_compiler_error_receipts': data['typed_recent']['audit']['error_receipt_count'],
        'census': census_id, 'source_unchanged': True, 'no_champion_fallback': True,
        'never_inspected_holdout': False, 'private_competition_result': False}
    summary['fresh_public_evaluation']['supplemental_execution'] = freeze.get('supplemental_execution')
    summary['fresh_public_evaluation']['global_scheduler_equivalence_proven'] = False
    summary['interpretation'] = ('Training scores are development coverage over previously compiled public-training records. '
        'The completed public-evaluation scores are fresh frozen execution on historically inspected public data. '
        'Neither establishes a hidden-test score. typed_recent remains primary; typed_supported remains the secondary control.')
    write_json(summary_path, summary)
    readme = make_readme(scores, data)
    (evaluation / 'README.txt').write_text(readme, encoding='utf-8')
    (workspace / 'arc-evidence/README.txt').write_text(readme, encoding='utf-8')
    reference_path = evaluation / 'source_archive_reference.json'
    write_json(reference_path, {'source_archive_basename': 'Komorebi_PR_LASM_Block17_Full_Bank_Integration.zip',
        'source_archive_sha256': SOURCE_ARCHIVE_SHA, 'source_archive_duplicated_in_this_result_zip': False,
        'verified_training_snapshot_basename': TRAINING_PACKAGE_NAME,
        'verified_training_snapshot_sha256': TRAINING_PACKAGE_SHA,
        'verified_training_snapshot_bytes': 115296337,
        'verified_training_snapshot_library_file_id': 'libfile_b4a96cf6d8008191b1b7b251e68cbd88',
        'verified_training_snapshot_file_id': 'file_00000000347481f7aadceff016e4bb17'})
    write_json(evaluation / 'package_inputs_audit.json', {'schema': 'komorebi.arc.block17.final-package-inputs.v1',
        'expected_tasks': EXPECTED_TASKS, 'expected_test_outputs': EXPECTED_OUTPUTS,
        'both_prediction_bytes_and_seals_verified_before_label_open': True,
        'explicit_pre_score_freeze_verified': True, 'pre_score_freeze_content_hash': freeze['content_hash'],
        'source_unchanged_verified_against_actual_files': True, 'source_files': unchanged['files_after'],
        'both_score_reports_and_csv_ledgers_independently_reproduced': True,
        'solver_calls': 0, 'duplicate_checkpoints_included': False, 'source_archive_duplicated': False,
        'census': census_id, 'integrity_pass': True})
    payload = set(evaluation / name for name in required)
    payload.update(evaluation / name for name in ('README.txt', 'source_archive_reference.json', 'package_inputs_audit.json'))
    # Include final direct evidence and logs, never the duplicate census.tasks directory.
    payload.update(p for p in evaluation.iterdir() if p.is_file() and p.suffix in ('.json', '.jsonl', '.csv', '.log', '.txt'))
    payload.update(workspace / name for name in (
        'arc-evidence/ARC_AGI2_offline_summary.json', 'arc-evidence/README.txt',
        'arc-evidence/scripts/score_arc_submission.py', 'arc-evidence/scripts/package_block17_public_evaluation.py',
        'arc-evidence/scripts/finalize_block17_public_evaluation.py',
        'arc-evidence/scripts/authenticate_block17_supplement.py',
        'arc-evidence/scripts/test_supplement_agreement_gate.py',
        'arc-evidence/scripts/authenticate_block17_checkpoints_pre_stop.py',
        'arc-evidence/scripts/test_block17_checkpoints_pre_stop.py',
        'arc-evidence/scripts/assemble_block17_census_streaming.py',
        'arc-evidence/scripts/test_block17_streaming_assembly.py',
        'arc-evidence/scripts/monitor_block17_scans.py',
        'arc-evidence/scripts/supplement_block17_scan.py',
        'arc-evidence/fullbank_worker_adjustment.json',
        'arc-offline-data/arc-agi_evaluation_challenges.json', 'arc-offline-data/arc-agi_evaluation_solutions.json',
        'arc-evidence/runner_independent_audit.json', 'arc-evidence/historical_frontier_provenance_audit.json',
        'arc-evidence/later-source-audit/block17_source_before.json',
        'arc-evidence/later-source-audit/block17_source_audit.json',
        'arc-evidence/later-source-audit/block17_integrity.json',
        'arc-evidence/later-source-audit/block17_literal_id_scan.json',
        'arc-evidence/later-source-audit/block17_source_unchanged_after_replay.json',
        'arc-evidence/later-source-audit/snapshot_package_verification.json',
        'arc-evidence/later-source-audit/verify_block17_unchanged.py',
        'arc-evidence/later-source-audit/PORTABLE_OFFLINE_RUN.txt',
        'arc-evidence/later-source-audit/PORTABLE_OFFLINE_RUN_AUDIT.json',
        'arc-evidence/later-source-audit/capture_restored_block17_baseline.py',
        'arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py',
        'arc-evidence/later-source-audit/fresh_stream_independent_review.json',
        'arc-evidence/later-source-audit/finalization_pipeline_review.json',
        'arc-evidence/later-source-audit/test_fresh_stream_aggregation.py',
        'arc-evidence/later-source-audit/post_score_candidate_pool_diagnostic.py',
        'arc-evidence/later-source-audit/POST_SCORE_DIAGNOSTIC_README.txt',
        'arc-evidence/later-source-audit/POST_SCORE_DIAGNOSTIC_REVIEW.json',
        'arc-evidence/later-source-audit/core_finite_search_review.json',
        'arc-evidence/later-source-audit/supplemental_schedule_static_review.json',
        'arc-evidence/later-source-audit/supplement_agreement_negative_controls.json',
        'arc-evidence/later-source-audit/supplemental_gate_review.json',
        'arc-evidence/later-source-audit/readonly_stack_probe_permissions.c',
        'arc-evidence/later-source-audit/readonly_stack_probe_permissions.json',
        'arc-evidence/later-source-audit/timed_compile_stage_diagnostic_stacks.log',
        'arc-evidence/later-source-audit/timed_compile_stage_diagnostic.py',
        'arc-evidence/later-source-audit/timed_compile_stage_diagnostic_report.json',
        'arc-evidence/later-source-audit/timed_compile_stage_diagnostic_process.log',
        'arc-evidence/later-source-audit/block17_source_unchanged_after_timed_diagnostic.json',
        'arc-evidence/later-source-audit/boundary_compile_stage_diagnostic.py',
        'arc-evidence/later-source-audit/boundary_compile_stage_diagnostic_report.json',
        'arc-evidence/later-source-audit/boundary_compile_stage_diagnostic_process.log',
        'arc-evidence/later-source-audit/boundary_compile_stage_diagnostic_boundaries.jsonl',
        'arc-evidence/later-source-audit/block17_source_unchanged_after_boundary_diagnostic.json',
        'arc-evidence/later-source-audit/LOADED_INTERFACE_TERMINATION_REVIEW.txt',
        'arc-evidence/later-source-audit/loaded_interface_termination_review.json',
        'arc-evidence/later-source-audit/termination_inherited.json',
        'arc-evidence/later-source-audit/termination_block13.json',
        'arc-evidence/later-source-audit/termination_new_a.json',
        'arc-evidence/later-source-audit/termination_new_b.json',
        'arc-evidence/later-source-audit/block17_source_unchanged_after_storage_cleanup.json',
        'arc-evidence/later-source-audit/fresh_stream_aggregation_equivalence.json',
        'arc-evidence/later-source-audit/public_eval_resource_assessment.json',
        'arc-evidence/later-source-audit/public_eval_resource_snapshot.json',
        'arc-evidence/later-source-audit/public_eval_process_snapshot.json',
        'arc-evidence/later-source-audit/bundled_eval_census_check.json'))
    payload.update((workspace / 'arc-evidence').glob('fullbank_evaluation_scan*.log'))
    payload.update((workspace / 'arc-evidence').glob('fullbank_evaluation_supplemental*.log'))
    payload.update((workspace / 'arc-evidence/later-source-audit').glob('block17_*.log'))
    for path in payload:
        require(path.is_file(), f'package evidence missing: {path}')
    hashes = {p.relative_to(workspace).as_posix(): sha256(p) for p in sorted(payload)}
    manifest = ''.join(f'{hashes[name]}  {name}\n' for name in sorted(hashes))
    temporary = output.with_name(output.name + '.partial')
    require(not temporary.exists(), 'partial ZIP already exists; inspect it before retrying')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for name in sorted(hashes):
                archive.write(workspace / name, name)
            archive.writestr('SHA256SUMS.txt', manifest)
        with zipfile.ZipFile(temporary) as archive:
            require(len(archive.namelist()) == len(hashes) + 1, 'ZIP inventory differs from payload')
            require(archive.testzip() is None, 'ZIP CRC verification failed')
            require(archive.read('SHA256SUMS.txt').decode('utf-8') == manifest,
                    'archived SHA256SUMS manifest differs from authenticated payload')
            for name, expected in hashes.items():
                with archive.open(name) as handle:
                    require(hashlib.file_digest(handle, 'sha256').hexdigest() == expected, f'ZIP payload hash differs: {name}')
                require(sha256(workspace / name) == expected, f'payload changed during packaging: {name}')
        temporary.replace(output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    audit_path = output.with_name(output.stem + '_package_audit.json')
    audit = {'schema': 'komorebi.arc.block17.public-evaluation-package-verification.v1',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'archive_path': str(output),
        'archive_bytes': output.stat().st_size, 'archive_sha256': sha256(output),
        'payload_files': len(hashes), 'zip_entries': len(hashes) + 1,
        'all_entry_crc_verified': True, 'sha256_manifest_verified_for_every_payload': True,
        'payload_files_unchanged_during_packaging': True, 'source_files_modified_by_packaging': False,
        'duplicate_checkpoints_included': False, 'source_archive_duplicated': False,
        'reference_source_archive_sha256': SOURCE_ARCHIVE_SHA,
        'reference_training_package_sha256': TRAINING_PACKAGE_SHA,
        'tasks': EXPECTED_TASKS, 'test_outputs': EXPECTED_OUTPUTS,
        'policy_scores': policy_scores, 'payload_sha256': hashes, 'overall_pass': True}
    write_json(audit_path, audit)
    print(json.dumps({k: audit[k] for k in ('archive_path', 'archive_bytes', 'archive_sha256',
        'payload_files', 'tasks', 'test_outputs', 'policy_scores', 'overall_pass')}, indent=2))


if __name__ == '__main__':
    main()
