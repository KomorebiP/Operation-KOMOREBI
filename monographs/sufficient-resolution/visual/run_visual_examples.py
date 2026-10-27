#!/usr/bin/env python3
"""Run the authorized visual-example generator and copy its actual result."""
from pathlib import Path
import argparse,runpy,shutil
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--result',required=True)
args=parser.parse_args()
runpy.run_path(str(root/'generate_examples_and_figures.py'),run_name='__main__')
target=root/args.result
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(root/'validation/visual_example_checks.json',target)
