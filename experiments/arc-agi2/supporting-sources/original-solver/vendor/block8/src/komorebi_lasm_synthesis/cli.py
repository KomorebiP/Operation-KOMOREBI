from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .audit import main as audit_main
from .compiler import compile_record


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PR-LASM obstruction-guided macro synthesis")
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile", help="compile one ARC-style task JSON")
    compile_parser.add_argument("task", type=Path)
    audit_parser = sub.add_parser("audit", help="run the complete Block 8 audit")
    audit_parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command == "compile":
        task = json.loads(args.task.read_text(encoding="utf-8"))
        print(json.dumps(compile_record(task), indent=2, sort_keys=True))
        return 0
    return audit_main(args.arguments)


if __name__ == "__main__":
    raise SystemExit(main())
