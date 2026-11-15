"""Fetch the two official bulk exports, outside the published site tree."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


def fetch(name, destination):
    url = 'https://oeis.org/' + name
    path = destination / name
    if path.exists():
        raise FileExistsError(f'Retain existing snapshots: choose a new directory ({path})')
    part = path.with_suffix('.part')
    sha = hashlib.sha256()
    size = 0
    with urlopen(Request(url, headers={'User-Agent': 'KomorebiSequenceAtlas/1.0 (bulk sequence research)'}), timeout=60) as response, part.open('wb') as output:
        headers = {key: response.headers.get(key) for key in ('Last-Modified', 'ETag', 'Content-Length')}
        while block := response.read(1024 * 1024):
            size += len(block)
            if size > 300 * 1024 * 1024:
                raise ValueError('Bulk export exceeds the documented 300 MiB resource cap')
            sha.update(block)
            output.write(block)
    with gzip.open(part, 'rb') as data:
        first_raw = data.readline()
        first = first_raw.decode('utf-8').strip()
        if not first.startswith('# OEIS Sequence'):
            raise ValueError('Not the expected OEIS bulk export')
        uncompressed = len(first_raw)
        for block in iter(lambda: data.read(1024 * 1024), b''):
            uncompressed += len(block)
    part.replace(path)
    return dict(file=name, url=url, bytes=size, sha256=sha.hexdigest(), uncompressed_bytes=uncompressed, headers=headers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        files = list(pool.map(lambda name: fetch(name, args.output), ('stripped.gz', 'names.gz')))
    report = dict(downloaded_at=datetime.now(timezone.utc).isoformat(), guidance='https://oeis.org/wiki/Download', attribution='The Online Encyclopedia of Integer Sequences', license='CC-BY-SA-4.0', license_url='https://oeis.org/LICENSE', files=files)
    (args.output / 'snapshot.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
