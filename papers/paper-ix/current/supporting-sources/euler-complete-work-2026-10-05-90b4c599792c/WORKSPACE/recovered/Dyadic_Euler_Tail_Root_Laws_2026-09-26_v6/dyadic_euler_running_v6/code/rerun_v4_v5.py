#!/usr/bin/env python3
"""Re-execute the inherited v4 scientific checks into a new result file."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from check_completion_v4 import run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output path; existing evidence is preserved.')
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'counts': result['counts']}, indent=2))

if __name__ == '__main__':
    main()
