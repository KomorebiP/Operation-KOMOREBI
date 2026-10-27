#!/usr/bin/env python3
"""Bounded tests of this independent archive checker; no release is accepted."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import warnings
import zipfile

HERE = Path(__file__).resolve().parent
CHECKER = HERE / 'amended_archive_check.py'
spec = importlib.util.spec_from_file_location('independent_archive_checker', CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
results = []


def check(name, fn):
    fn()
    results.append({'name': name, 'status': 'PASS'})


def must_reject(fn):
    try:
        fn()
    except (ValueError, zipfile.BadZipFile, RuntimeError):
        return
    raise AssertionError('Adverse fixture unexpectedly accepted')


def archive(directory, name, payload, extra=None, manifest=None):
    path = directory / (name + '.zip')
    if manifest is None:
        manifest = ''.join(hashlib.sha256(data).hexdigest() + '  ' + relative + '\n'
                           for relative, data in payload).encode()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_STORED) as z:
            for relative, data in payload:
                z.writestr('Fixture/' + relative, data)
            z.writestr('Fixture/SHA256SUMS.txt', manifest)
            if extra:
                extra(z)
    return path


def inspect(path):
    result = checker.Archive(path, 'Fixture')
    result.zip.close()


ast.parse(CHECKER.read_text())
check('checker_python_syntax', lambda: None)
with tempfile.TemporaryDirectory(prefix='checker-tests-', dir=HERE) as temporary:
    tmp = Path(temporary)
    check('valid_archive_all_payloads', lambda: inspect(archive(tmp, 'valid', [('a.txt', b'alpha'), ('x/b.txt', b'beta')])))
    check('manifest_missing_payload', lambda: must_reject(lambda: inspect(archive(tmp, 'missing', [('a.txt', b'alpha')], manifest=b''))))
    check('manifest_wrong_digest', lambda: must_reject(lambda: inspect(archive(tmp, 'wrong', [('a.txt', b'alpha')], manifest=('0'*64 + '  a.txt\n').encode()))))
    check('duplicate_payload', lambda: must_reject(lambda: inspect(archive(tmp, 'duplicate', [('a.txt', b'alpha'), ('a.txt', b'alpha')]))))
    check('unmanifested_payload', lambda: must_reject(lambda: inspect(archive(tmp, 'extra', [('a.txt', b'alpha')], extra=lambda z: z.writestr('Fixture/extra.txt', b'extra')))))
    for number, bad in enumerate(['../a', '/absolute', 'a//b', 'a/./b', 'C:drive', 'a\\b', 'a/../b', 'a\x7fb']):
        check('unsafe_path_' + str(number), lambda bad=bad, number=number: must_reject(
            lambda: inspect(archive(tmp, 'unsafe' + str(number), [(bad, b'x')]))))

    def symlink(z):
        entry = zipfile.ZipInfo('Fixture/link')
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        z.writestr(entry, b'a.txt')

    check('symlink_payload', lambda: must_reject(lambda: inspect(archive(tmp, 'symlink', [('a.txt', b'alpha')], extra=symlink))))
    check('file_directory_collision', lambda: must_reject(lambda: inspect(archive(tmp, 'collision', [('a', b'alpha')], extra=lambda z: z.writestr('Fixture/a/', b'')))))
    check('file_ancestor_collision', lambda: must_reject(lambda: inspect(archive(tmp, 'ancestor', [('a', b'alpha'), ('a/b', b'beta')]))))
    check('duplicate_manifest_entry', lambda: must_reject(lambda: inspect(archive(tmp, 'duplicate-manifest', [('a', b'alpha')], manifest=(hashlib.sha256(b'alpha').hexdigest()+'  a\n').encode()*2))))
    check('self_referential_manifest', lambda: must_reject(lambda: inspect(archive(tmp, 'self', [('a', b'alpha')], manifest=('0'*64+'  SHA256SUMS.txt\n').encode()))))

    def corrupt_crc():
        path = archive(tmp, 'crc', [('a.txt', b'unique-crc-fixture-payload')])
        data = path.read_bytes()
        assert data.count(b'unique-crc-fixture-payload') == 1
        path.write_bytes(data.replace(b'unique-crc-fixture-payload', b'corruptcrc-fixture-payload'))
        must_reject(lambda: inspect(path))

    check('corrupt_crc', corrupt_crc)
    target = tmp / 'target.txt'
    target.write_text('target')
    link = tmp / 'link.txt'
    link.symlink_to(target)
    check('local_symlink_file', lambda: must_reject(lambda: checker.file_digest(link)))

def public_parser():
    import re
    text = checker.strip_lean_comments('namespace X\n/- def decoy -/\nnoncomputable def changed := 0\ntheorem actual : True := by trivial\n')
    rows = re.findall(r'^\s*(?:noncomputable\s+)?(theorem|lemma|def)\s+(\S+)', text, re.M)
    assert rows == [('def', 'changed'), ('theorem', 'actual')]

check('noncomputable_public_definition_scan', public_parser)
def exclusion_predicate(source):
    from types import SimpleNamespace
    module = ast.parse(source)
    verify = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == 'verify')
    calls = [node for node in ast.walk(verify) if isinstance(node, ast.Call) and
             isinstance(node.func, ast.Name) and node.func.id == 'insist' and
             len(node.args) > 1 and isinstance(node.args[1], ast.Constant) and
             isinstance(node.args[1].value, str) and node.args[1].value.startswith('Compiled')]
    assert len(calls) == 1
    expression = compile(ast.Expression(calls[0].args[0]), '<actual checker exclusion predicate>', 'eval')
    return lambda names: eval(expression, {**vars(checker), 'a': SimpleNamespace(files=names)})

original_predicate = exclusion_predicate((HERE / 'original_frozen_checker.py').read_text())
amended_predicate = exclusion_predicate(CHECKER.read_text())

def require_result(names, expected):
    assert amended_predicate(names) is expected

historical = ['inherited_v1.11.0/inherited_v1.10.0/continuation/runtime/' + name for name in
              ['RECOVERY.md', 'RecoverySmoke.lean', 'assembly.log', 'offline_archive_manifest.json',
               'recovery.json', 'smoke.log']]
check('reproduces_original_historical_false_rejection', lambda: (_ for _ in ()).throw(AssertionError()) if original_predicate(historical) else None)
check('preserves_six_pinned_historical_provenance_files', lambda: require_result(historical, True))
check('still_rejects_inherited_compiler_object', lambda: require_result(['inherited_v1.11.0/history/runtime/x.olean'], False))
check('still_rejects_current_runtime_directory', lambda: require_result(['wr15_v1.12.0/runtime/RECOVERY.md'], False))
check('still_rejects_current_build_directory', lambda: require_result(['wr15_v1.12.0/build/evidence.txt'], False))
check('still_rejects_current_compiler_object', lambda: require_result(['formal/X.olean'], False))
check('allows_current_source_payload', lambda: require_result(['formal/X.lean'], True))

print(json.dumps({'status': 'PASS', 'scope': 'Bounded synthetic checker preparation only; no actual release inspected or accepted.',
                  'checker_sha256': hashlib.sha256(CHECKER.read_bytes()).hexdigest(),
                  'tests': results, 'count': len(results)}, indent=2))
