#!/usr/bin/env python3
"""Build the sequence surface with the production builders and HTML wrapper.

This focused integration fixture does not build unrelated manuscript readers,
Lean runtimes or PDF bundles. Use a fresh output directory and the verified
MathJax source produced by fetch_reader_runtime.py.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from build_reader_site import Site
from reader_runtime import publish_mathjax
from sequence_atlas import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mathjax-root', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Use a new empty preview output directory')

    # These are the attributes required by Site.page/write. The full Site
    # initializer also resolves unrelated paper receipts and library runtimes.
    site = Site.__new__(Site)
    site.root, site.output = root, output
    site.revision = subprocess.check_output(
        ['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    site.search = []
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root/'website/assets', output/'assets', dirs_exist_ok=True)
    publish_mathjax(args.mathjax_root, output/'assets/mathjax')
    report = build(site)
    site.write('sequence-build-info.json', json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(output=str(output), sequence_atlas=report), indent=2))


if __name__ == '__main__':
    main()
