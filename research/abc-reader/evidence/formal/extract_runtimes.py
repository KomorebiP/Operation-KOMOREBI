#!/usr/bin/env python3
from pathlib import Path
import concurrent.futures
import json
import subprocess
import time

EVIDENCE = Path(__file__).resolve().parent
PRIVATE = EVIDENCE.parents[2] / 'abc_private_runtime'

def extract(version):
    argv = ['tar', '--no-same-owner', '--zstd', '-xf', f'lean-{version}-linux.tar.zst']
    started = time.monotonic()
    proc = subprocess.run(argv, cwd=PRIVATE, capture_output=True, text=True)
    log = EVIDENCE / f'{version}_runtime_extract.log'
    log.write_text(proc.stdout + proc.stderr)
    result = {'argv': argv, 'cwd': str(PRIVATE), 'exit_code': proc.returncode,
              'elapsed_seconds': round(time.monotonic() - started, 6), 'log': log.name}
    (EVIDENCE / f'{version}_runtime_extract.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return proc.returncode

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(extract, ['4.34.0-rc2', '4.19.0']))
    raise SystemExit(1 if any(results) else 0)
