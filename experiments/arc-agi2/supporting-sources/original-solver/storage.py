"""Lossless storage for large frozen JSON evidence. Author: Komorebi P."""
from pathlib import Path
import gzip
import hashlib
import json


def read(path):
    path = Path(path)
    if not path.exists() and path.suffix != '.gz':
        path = Path(str(path)+'.gz')
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def write_gzip(path, value):
    path = Path(path)
    temporary = Path(str(path)+'.partial')
    digest = hashlib.sha256()
    encoder = json.JSONEncoder(indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
    size = 0
    try:
        with temporary.open('wb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=6) as stream:
                buffer = bytearray()
                for chunk in encoder.iterencode(value):
                    buffer.extend(chunk.encode('utf-8'))
                    if len(buffer) >= 1024*1024:
                        digest.update(buffer); size += len(buffer); stream.write(buffer); buffer.clear()
                buffer.extend(b'\n')
                digest.update(buffer); size += len(buffer); stream.write(buffer)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return {'format':'gzip of canonical JSON', 'uncompressed_sha256':digest.hexdigest(),
            'uncompressed_bytes':size, 'compressed_bytes':path.stat().st_size}
