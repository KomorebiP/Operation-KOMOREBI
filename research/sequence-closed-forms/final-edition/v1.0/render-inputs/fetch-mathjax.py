#!/usr/bin/env python3
"""Fetch the pinned MathJax browser runtime, verify it and retain its license."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request

URL='https://registry.npmjs.org/mathjax/-/mathjax-3.2.2.tgz'
INTEGRITY='Bt+SSVU8eBG27zChVewOicYs7Xsdt40qm4+UpHyX7k0/O9NliPc+x77k1/FEsPsjKPZGJvtRZM1vO+geW0OhGw=='


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError('Use a new empty runtime directory')
    with urllib.request.urlopen(URL,timeout=60) as response:
        raw=response.read(30*1024*1024)
    assert base64.b64encode(hashlib.sha512(raw).digest()).decode()==INTEGRITY,'Runtime integrity mismatch'
    args.output.mkdir(parents=True,exist_ok=True)
    count=0
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        for member in archive.getmembers():
            if not member.isfile():continue
            if member.name.startswith('package/es5/'):
                name=member.name[len('package/es5/'):]
            elif member.name in {'package/LICENSE','package/README.md'}:
                name=PurePosixPath(member.name).name
            else:continue
            relative=PurePosixPath(name)
            assert not relative.is_absolute() and '..' not in relative.parts
            destination=args.output/relative.as_posix()
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(archive.extractfile(member).read())
            count+=1
    (args.output/'SOURCE.json').write_text(json.dumps(dict(url=URL,sha512_base64=INTEGRITY,files=count),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runtime='MathJax 3.2.2',verified=True,files=count)))


if __name__=='__main__':main()
