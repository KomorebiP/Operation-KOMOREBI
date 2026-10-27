"""Bounded synthetic equivalence test; no ARC targets or compiler calls."""
from __future__ import annotations
import ast
import copy
import importlib.util
import json
from pathlib import Path
import resource
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent / 'arc-fullbank/block17'
sys.path.insert(0, str(ROOT))
import engine
import solver
spec = importlib.util.spec_from_file_location('fresh_stream_adapter', HERE / 'stream_fresh_block17_dispatch.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def candidate(task, entrant, block, outputs, complexity=10, program=None, evidence=None):
    body = {'entrant': entrant, 'source_block': block, 'family': 'synthetic_only',
        'program': {} if program is None else program, 'test_outputs': outputs,
        'complexity': complexity, 'evidence': {} if evidence is None else evidence,
        'behavior_hash': engine.contract.digest(outputs),
        'task_semantic_hash': engine.contract.digest(task)}
    body['candidate_hash'] = engine.contract.digest(body)
    return body


def make_census(challenges, records, bindings):
    return engine.seal({'schema': 'komorebi.block17.live_census.v1', 'author': 'Komorebi P.',
        'run_hash': engine.contract.digest({'code': bindings['code_hash'], 'bank': bindings['bank_hash'],
            'challenges': challenges, 'include_new': True, 'limits': engine.LIMITS}),
        'code_hash': bindings['code_hash'], 'bank_hash': bindings['bank_hash'],
        'challenges_hash': engine.contract.digest(challenges), 'scope': 'all_banks',
        'limits': engine.LIMITS, 'records': records,
        'label_access': 'demonstrations_only', 'champion_fallback': False})


def main():
    bindings = adapter.source_identity(engine, solver)
    challenges = {
        'synthetic_a': {'train': [{'input': [[1]], 'output': [[2]]}],
            'test': [{'input': [[3]]}, {'input': [[4]]}]},
        'synthetic_b': {'train': [{'input': [[5]], 'output': [[6]]}],
            'test': [{'input': [[7]]}]}}
    a, b = challenges.values()
    rows_a = [
        candidate(a, 'alpha_v1', 13, [[[1]], [[2]]]),
        candidate(a, 'alpha_v2', 13, [[[3]], [[4]]]),
        candidate(a, 'beta', 14, [[[3]], [[4]]], complexity=5),
        candidate(a, 'feature_induction', 13, [[[8]], [[9]]], evidence={'unseen_test_keys': 1}),
        candidate(a, 'core_search', 2, [[[6]], [[6]]]),
        candidate(a, 'multiscale_codec', 14, [[[9]], [[9]]], program={
            'operator': 'scalar_feature_codebook', 'feature': 'synthetic', 'mapping': [[1, 0], [2, 0]]})]
    rows_b = [
        candidate(b, 'feature_induction', 13, [[[8]]], evidence={'unseen_test_keys': 0}),
        candidate(b, 'gamma', 14, [[[8]]], complexity=1),
        candidate(b, 'multiscale_codec', 14, [[[9]]], program={
            'operator': 'scalar_feature_codebook', 'feature': 'synthetic', 'mapping': [[1, 0], [2, 1]]})]
    records = {
        'synthetic_a': engine.seal({'task_semantic_hash': engine.contract.digest(a),
            'base': [{'attempt_1': [[3]], 'attempt_2': [[0]]}, {'attempt_1': [[0]], 'attempt_2': [[1]]}],
            'candidates': sorted(rows_a, key=lambda c: c['candidate_hash']),
            'receipts': {'synthetic_provider': {'status': 'error', 'error': 'retained synthetic error'}}}),
        'synthetic_b': engine.seal({'task_semantic_hash': engine.contract.digest(b),
            'base': [{'attempt_1': [[7]], 'attempt_2': [[7]]}],
            'candidates': sorted(rows_b, key=lambda c: c['candidate_hash']),
            'receipts': {'synthetic_provider': {'status': 'ok'}}})}
    census = make_census(challenges, records, bindings)
    reports = []
    negatives = []
    with tempfile.TemporaryDirectory(prefix='arc_synthetic_stream_', dir=HERE) as folder:
        path = Path(folder) / 'tiny_census.json'
        engine.write(path, census)
        for policy in adapter.POLICIES:
            expected = solver.dispatch(challenges, census, policy)
            observed, receipt = adapter.stream_dispatch(engine, solver, challenges, path, policy, bindings)
            assert observed == expected, policy
            engine.verify(observed)
            expected_path = Path(folder) / (policy + '_full.json')
            observed_path = Path(folder) / (policy + '_stream.json')
            engine.write(expected_path, expected)
            engine.write(observed_path, observed)
            assert adapter.sha256_file(expected_path) == adapter.sha256_file(observed_path), policy
            assert receipt['records'] == 2 and receipt['test_outputs'] == 3
            assert receipt['error_receipt_count'] == 1
            assert receipt['compiler_receipts_by_task'] == {k: v['receipts'] for k, v in records.items()}
            assert receipt['streamed_utf8_sha256'] == adapter.sha256_file(path)
            assert receipt['streamed_utf8_bytes'] == path.stat().st_size
            reports.append({'policy': policy, 'full_and_streamed_objects_identical': True,
                'serialized_bytes_identical': True, 'content_hash': observed['content_hash'],
                'output_sha256': adapter.sha256_file(observed_path)})
        cases = {}
        wrong_run = copy.deepcopy(census); wrong_run['run_hash'] = '0' * 64
        cases['wrong_fresh_run_hash'] = engine.seal(wrong_run)
        wrong_scope = copy.deepcopy(census); wrong_scope['scope'] = 'core_blocks2_13'
        cases['incomplete_bank_scope'] = engine.seal(wrong_scope)
        wrong_limits = copy.deepcopy(census); wrong_limits['limits']['max_candidates'] += 1
        cases['changed_fixed_limits'] = engine.seal(wrong_limits)
        bad_arity = copy.deepcopy(census); bad_arity['records']['synthetic_a']['base'].pop()
        bad_arity['records']['synthetic_a'] = engine.seal(bad_arity['records']['synthetic_a'])
        cases['base_test_arity_mismatch'] = engine.seal(bad_arity)
        bad_task = copy.deepcopy(census); bad_task['records']['synthetic_a']['task_semantic_hash'] = '1' * 64
        bad_task['records']['synthetic_a'] = engine.seal(bad_task['records']['synthetic_a'])
        cases['record_task_binding_mismatch'] = engine.seal(bad_task)
        bad_candidate = copy.deepcopy(census); bad_candidate['records']['synthetic_b']['candidates'][0]['complexity'] += 1
        bad_candidate['records']['synthetic_b'] = engine.seal(bad_candidate['records']['synthetic_b'])
        cases['candidate_content_binding_mismatch'] = engine.seal(bad_candidate)
        missing = copy.deepcopy(census); del missing['records']['synthetic_b']
        cases['missing_task'] = engine.seal(missing)
        bad_seal = copy.deepcopy(census); bad_seal['author'] = 'tampered'
        cases['original_census_seal_mismatch'] = bad_seal
        for name, bad in cases.items():
            engine.write(path, bad)
            try:
                adapter.stream_dispatch(engine, solver, challenges, path, 'typed_recent', bindings)
            except (ValueError, KeyError) as error:
                negatives.append({'case': name, 'rejected': True, 'reason': str(error)})
            else:
                raise AssertionError('accepted invalid corpus: ' + name)
    tree = ast.parse((HERE / 'stream_fresh_block17_dispatch.py').read_text())
    functions = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert 'score' not in functions
    text = (HERE / 'stream_fresh_block17_dispatch.py').read_text()
    assert '--solutions' not in text
    assert adapter.source_identity(engine, solver) == bindings
    report = {'schema': 'komorebi.block17.fresh-stream-aggregation-equivalence.v1',
        'scope': 'Two synthetic tasks, three output positions, nine synthetic candidate records. No benchmark targets, compiler calls, or candidate program executions.',
        'source_root': str(ROOT), 'source_bindings_before_and_after': bindings,
        'cases_exercised': ['multiple test outputs', 'version supersession', 'same behavior across sources',
            'typed veto', 'supported codebook', 'unsupported feature abstention', 'core-search exclusion',
            'immutable first attempt', 'retained compiler error receipt'],
        'policy_equivalence': reports, 'negative_controls': negatives,
        'no_score_function_or_solutions_option': True,
        'maximum_resident_mib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'overall_pass': True}
    engine.write(HERE / 'fresh_stream_aggregation_equivalence.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
