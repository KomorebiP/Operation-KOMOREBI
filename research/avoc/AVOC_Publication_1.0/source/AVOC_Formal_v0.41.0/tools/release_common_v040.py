#!/usr/bin/env python3
"""Shared, relocatable v0.40 evidence checks. No checking at import time."""
from __future__ import annotations
import contextlib, fcntl, hashlib, json, os, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RD = ROOT / 'results/v0.40.0'
BASE_SHA256 = '298b6daed3875697a59c15caa6d8546c9cfe2d30aa8cfbc4aab0275ad63be44c'
BASE_PREFIX = 'AVOC_Formal_v0.39.0/'
AUDITS = {'AVOC/Audit.lean', 'AVOC/FullAudit.lean'}

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)

def masked_lean(text):
    """Mask nested /- -/ comments, line comments and strings; preserve positions."""
    out = list(text); i = 0; depth = 0; quoted = False
    while i < len(text):
        if depth:
            if text.startswith('/-', i): out[i:i+2] = '  '; depth += 1; i += 2
            elif text.startswith('-/', i): out[i:i+2] = '  '; depth -= 1; i += 2
            else:
                if text[i] != '\n': out[i] = ' '
                i += 1
        elif quoted:
            if text[i] == '\\' and i + 1 < len(text):
                if text[i] != '\n': out[i] = ' '
                if text[i+1] != '\n': out[i+1] = ' '
                i += 2
            else:
                if text[i] == '"': quoted = False
                if text[i] != '\n': out[i] = ' '
                i += 1
        elif text.startswith('/-', i): out[i:i+2] = '  '; depth = 1; i += 2
        elif text.startswith('--', i):
            j = text.find('\n', i)
            if j == -1: j = len(text)
            out[i:j] = ' ' * (j-i); i = j
        elif text[i] == '"': out[i] = ' '; quoted = True; i += 1
        else: i += 1
    if depth or quoted: raise ValueError('Unterminated Lean comment/string')
    return ''.join(out)

def local_import_names(path):
    names = []
    for match in re.finditer(r'^\s*(?:(?:public|private)\s+)?import\s+([^\n]+)', masked_lean(Path(path).read_text()), re.M):
        for name in match.group(1).split():
            if name == 'AVOC' or name.startswith('AVOC.'): names.append(name)
    return sorted(set(names))

def source_files():
    return sorted([p.relative_to(ROOT).as_posix() for p in (ROOT/'AVOC').rglob('*.lean')
                   if p.relative_to(ROOT).as_posix() not in AUDITS] + ['AVOC.lean'] +
                  [p.relative_to(ROOT).as_posix() for p in (ROOT/'tools').rglob('*.lean')])

def build_graph():
    files = {str(Path(f).with_suffix('')).replace('/', '.'): f for f in source_files()}
    deps = {}; order = []; done = set(); active = set()
    for name, source in files.items():
        imports = local_import_names(ROOT/source)
        missing = set(imports) - files.keys()
        if missing: raise ValueError(f'Missing local imports in {source}: {sorted(missing)}')
        deps[source] = {files[d] for d in imports}
    def visit(source):
        if source in done: return
        if source in active: raise ValueError('Import cycle: ' + source)
        active.add(source)
        for dep in sorted(deps[source]): visit(dep)
        active.remove(source); done.add(source); order.append(source)
    for source in sorted(files.values()): visit(source)
    return order, deps

def kit_path():
    raw = os.environ.get('AVOC_LEAN_KIT')
    if not raw: raise RuntimeError('Set AVOC_LEAN_KIT to the pinned portable Lean runtime directory.')
    path = Path(raw).expanduser().resolve()
    if not (path/'toolchain/bin/lean').is_file(): raise RuntimeError('AVOC_LEAN_KIT has no toolchain/bin/lean')
    return path

@contextlib.contextmanager
def release_lock(name='build'):
    path = ROOT / '.lake' / ('v040_' + name + '.lock'); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as lock:
        try: fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise RuntimeError('Another v040 ' + name + ' process is active; wait for it to finish.')
        try: yield
        finally: fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

def import_hashes(source):
    result = {}
    for name in local_import_names(ROOT/source):
        output = ROOT/'.lake/build/lib/lean'/Path(name.replace('.', '/')).with_suffix('.olean')
        result[name] = sha(output) if output.is_file() else None
    return result

def build_record_errors(source, record, *, output=True):
    errors = []
    if record.get('returncode') != 0 or record.get('timed_out'): errors.append('did not complete successfully')
    if not record.get('warning_as_error'): errors.append('warnings were not explicitly errors')
    if record.get('source_sha256') != sha(ROOT/source): errors.append('source changed')
    if not record.get('source_unchanged') or not record.get('imports_unchanged'): errors.append('source/imports changed during build')
    if record.get('import_outputs') != import_hashes(source): errors.append('import set/hash mismatch')
    log = ROOT/record.get('log', '__missing__')
    if not log.is_file() or record.get('log_sha256') != sha(log): errors.append('log missing/changed')
    if output:
        artifact = ROOT/'.lake/build/lib/lean'/Path(source).with_suffix('.olean')
        if not artifact.is_file() or record.get('output_sha256') != sha(artifact): errors.append('output missing/changed')
    return errors
