"""Compile an explicit sequential author-build wave with unique logs and exit records."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
from lean_env import lean_env

root = Path(__file__).resolve().parents[1]
kit, tag, *modules = sys.argv[1:]
assert tag.isidentifier() and modules and all(m.isidentifier() for m in modules)
lean, env = lean_env(kit)
for name in modules:
    src = root / 'lean/PaperX' / (name + '.lean')
    obj = root / 'build/PaperX' / (name + '.olean')
    log = root / 'privatechecks' / (tag + '_' + name + '.log')
    assert not log.exists(), 'unique log tag required'
    start = time.monotonic()
    with log.open('w') as handle:
        proc = subprocess.run([lean, '-DwarningAsError=true', '-o', str(obj), str(src)],
            cwd=root / 'lean', env=env, stdout=handle, stderr=subprocess.STDOUT)
    row = {'module': name, 'exit_code': proc.returncode, 'elapsed_seconds': time.monotonic()-start,
           'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest()}
    if proc.returncode == 0:
        row['olean_sha256'] = hashlib.sha256(obj.read_bytes()).hexdigest()
    log.with_suffix('.json').write_text(json.dumps(row, indent=2)+'\n')
    print(json.dumps(row), flush=True)
    if proc.returncode:
        raise SystemExit(proc.returncode)
