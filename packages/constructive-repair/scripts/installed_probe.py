#!/usr/bin/env python3
"""Probe the installed wheel, not the checkout; no network or external packages."""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, locale, os, platform, sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fixtures', type=Path, required=True)
    ap.add_argument('--prefix', type=Path, required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    import komorebi_repair as K
    from repair_certificates import canonical, read_json
    result = {'status': 'RUNNING', 'scope': 'Installed Python acceptance; no Lean claim',
              'python': platform.python_version(), 'implementation': platform.python_implementation(),
              'platform': platform.platform(), 'machine': platform.machine(),
              'sys_executable': sys.executable, 'import_path': K.__file__,
              'locale_encoding': locale.getpreferredencoding(False), 'utf8_mode': sys.flags.utf8_mode,
              'checks': [], 'cases': []}
    def check(name: str, value: bool) -> None:
        result['checks'].append({'name': name, 'pass': bool(value)})
        if not value:
            raise AssertionError(name)
    try:
        check('import_is_inside_isolated_prefix', Path(K.__file__).resolve().is_relative_to(args.prefix.resolve()))
        check('release_version', K.__version__ == args.version)
        check('sympy_not_installed', importlib.util.find_spec('sympy') is None)
        for folder in ('corpus', 'menu_corpus', 'branch_corpus'):
            for path in sorted((args.fixtures/folder).glob('*_input.json')):
                p = K.load(path)
                old = read_json(path.with_name(path.name.replace('_input', '_certificate')))
                checked = K.verify(p, old)
                check('retained_certificate_' + path.stem, checked.status == 'PYTHON_CERTIFICATE_VALID')
                original = copy.deepcopy(p)
                solved = K.solve(p)
                check('newly_constructed_' + path.stem, solved.status == 'PYTHON_CERTIFICATE_VALID')
                check('input_preserved_' + path.stem, p == original)
                check('no_kernel_status_' + path.stem, not solved.kernel_checked)
                check('independent_recheck_' + path.stem,
                      K.verify(p, solved.certificate).status == 'PYTHON_CERTIFICATE_VALID')
                result['cases'].append({'file': str(path.relative_to(args.fixtures)),
                    'problem_sha256': hashlib.sha256(canonical(p)).hexdigest(),
                    'kind': solved.certificate['kind'], 'status': solved.status,
                    'cost': solved.certificate.get('cost'), 'dimension': solved.certificate.get('t')})
        check('fixture_count', len(result['cases']) == 72)
        # Typed public interface, including zero dimensions and negative controls.
        A = K.ExactMatrix
        d, e, r = A.of([[1],[0],[0]]), A.of([[0,0],[1,0],[1,1]]), A.of([[0],[1],[0]])
        p = K.menu_problem(d, e, r, [1,1])
        answer = K.solve(p)
        check('typed_api_minimum_cost', answer.certificate['cost'] == 2)
        broken = copy.deepcopy(answer.certificate); broken['cost'] = 0
        check('corrupt_certificate_unresolved', K.verify(p, broken).status == 'UNRESOLVED')
        check('budget_not_infeasibility', K.solve(p, max_nodes=0).status == 'UNRESOLVED')
        p = K.menu_problem(d,e,r,[1,1],[])
        check('empty_admissibility_scoped_no_repair', K.solve(p).certificate['kind'] == 'no_admissible_repair')
        check('zero_target', K.solve(K.free_problem(A.zero(0,3), A.zero(0,2))).certificate['t'] == 0)
        result['status'] = 'PASS'
    except Exception as exc:
        result.update(status='FAIL', error=repr(exc))
    with args.output.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=True)
        f.write('\n')
    print(json.dumps({'status':result['status'], 'python':result['python'],
                      'cases':len(result['cases']), 'checks':len(result['checks'])}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
