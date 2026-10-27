#!/usr/bin/env python3
"""Fetch the two exact official compiler releases. No release bytes are edited."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import requests
import time

ROOT = Path(__file__).resolve().parents[3]
PRIVATE = ROOT / 'abc_private_runtime'
EVIDENCE = Path(__file__).resolve().parent

def recover(record):
    asset = record['assets'][0]
    path = PRIVATE / asset['name']
    started = time.monotonic()
    result = {'tag': record['tag'], 'url': asset['browser_download_url'],
              'expected_size': asset['size'], 'official_api_digest': asset['digest'],
              'connect_timeout_seconds': 30, 'read_timeout_seconds': 60}
    try:
        with requests.get(asset['browser_download_url'], stream=True,
                          timeout=(30, 60)) as response:
            result['http_status'] = response.status_code
            response.raise_for_status()
            h = hashlib.sha256()
            size = 0
            with path.open('wb') as output:
                for chunk in response.iter_content(1024 * 1024):
                    output.write(chunk)
                    h.update(chunk)
                    size += len(chunk)
            result.update(bytes=size, sha256=h.hexdigest())
            result['size_matches'] = size == asset['size']
            result['official_digest_matches'] = (
                'sha256:' + h.hexdigest() == asset['digest']
                if asset['digest'] else None)
            result['status'] = 'PASS' if result['size_matches'] and result['official_digest_matches'] is not False else 'FAIL_AUTHENTICATION'
    except Exception as error:
        result.update(status='FAIL_DOWNLOAD', error=repr(error))
    result['elapsed_seconds'] = round(time.monotonic() - started, 6)
    (EVIDENCE / (record['tag'] + '_runtime_recovery.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return result

if __name__ == '__main__':
    PRIVATE.mkdir(exist_ok=True)
    records = json.loads((EVIDENCE / 'runtime_release_lookup.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(recover, records))
    raise SystemExit(0 if all(r['status'] == 'PASS' for r in results) else 1)
