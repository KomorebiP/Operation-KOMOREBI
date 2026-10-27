"""Build distributions using the already installed setuptools PEP 517 backend.

Requires setuptools >=77. Does not resolve or download build dependencies.
Normal online builds may instead use `python -m build`.
"""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import os
from pathlib import Path


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('dist'))
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]
    version=importlib.metadata.version('setuptools')
    if int(version.split('.')[0]) < 77:
        raise RuntimeError('setuptools >=77 is required')
    os.chdir(root)
    os.environ.setdefault('SOURCE_DATE_EPOCH','1791547200')
    from setuptools.build_meta import build_wheel, build_sdist
    wheel=build_wheel(str(output))
    source=build_sdist(str(output))
    print(json.dumps({'wheel':wheel,'sdist':source,'backend':'setuptools','backend_version':version},indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
