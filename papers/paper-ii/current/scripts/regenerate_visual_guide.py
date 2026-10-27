#!/usr/bin/env python3
"""Recompile the authored visual atlas and optionally regenerate exact graphics.

This entry point preserves Paper_II_Visual_Guide_Final.tex and pages_final.tex.
It never assembles current prose from the historical appendix.
"""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=ROOT/'editable/visual_guide',
                    help='The existing editable visual-guide directory.')
parser.add_argument('--graphics', action='store_true',
                    help="Regenerate graphics from this edition's exact model sources before compiling.")
parser.add_argument('--graphics-only', action='store_true',
                    help='Regenerate exact graphics without compiling the guide.')
parser.add_argument('--original', type=Path,
                    help='Legacy compatibility option. Historical prose is never copied into the current guide.')
parser.add_argument('--traditional', type=Path,
                    help='Legacy compatibility option. Current locators are maintained by the release crosswalk workflow.')
args = parser.parse_args()
guide = args.output.expanduser().resolve()
required = [guide/'Paper_II_Visual_Guide_Final.tex', guide/'source/pages_final.tex', guide/'build.py']
missing = [str(p) for p in required if not p.is_file()]
if missing:
    raise SystemExit('An existing authored guide is required. Missing: ' + ', '.join(missing))
if args.graphics or args.graphics_only:
    generator = guide/'source/generate_graphics.py'
    if not generator.is_file():
        raise SystemExit('Exact model generator is missing: '+str(generator))
    subprocess.run([sys.executable, str(generator)], cwd=guide, check=True)
if not args.graphics_only:
    subprocess.run([sys.executable, str(guide/'build.py')], cwd=guide, check=True)
