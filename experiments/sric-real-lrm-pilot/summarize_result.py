from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt(effect):
    interval = effect["interval_95"]
    return f"{effect['mean']:.6f} [{interval[0]:.6f}, {interval[1]:.6f}]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = json.loads(Path(args.result).read_text(encoding="utf-8"))
    summary = result["summary"]
    lines = [
        "# SRIC Real-LRM Pilot Result",
        "",
        f"- Status: **`{summary['status']}`**",
        f"- Tasks: {summary['task_count']}",
        f"- Replay maximum absolute logit error: {summary['replay_max_abs']:.9g}",
        f"- Necessity: {fmt(summary['necessity'])}",
        f"- Order: {fmt(summary['order'])}",
        f"- Norm-matched structure: {fmt(summary['structure'])}",
        f"- Same-answer procedure transplant: {fmt(summary['procedure_transplant'])}",
        f"- Semantic-twin transplant: {fmt(summary['twin_transplant'])}",
        f"- Result receipt: `{result['result_sha256']}`",
        "",
        "## Gates",
        "",
    ]
    lines.extend(f"- {name}: {'PASS' if value else 'FAIL'}" for name, value in summary["gates"].items())
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"SUMMARY_PATH={Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
