#!/usr/bin/env python3
"""Train and save one RRCT v0.51 dyad in a fresh Python process."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--holdout-seed", type=int, required=True)
    parser.add_argument(
        "--objective",
        choices=("round_curriculum", "terminal_only"),
        required=True,
    )
    parser.add_argument("--model-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    from rrct.emergent_synergistic_workspace import (
        EmergentWorkspaceConfig,
        save_emergent_model,
        train_emergent_dyad,
    )

    config = EmergentWorkspaceConfig()
    model, receipt = train_emergent_dyad(
        args.training_seed,
        args.objective,
        config,
    )
    save_emergent_model(
        args.model_output,
        model,
        receipt,
        args.holdout_seed,
    )
    args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
    args.receipt_output.write_text(
        json.dumps(
            {
                "schema": "rrct.v051.training_process_receipt.v1",
                "holdout_seed": args.holdout_seed,
                "objective": args.objective,
                "training_receipt": receipt.__dict__,
                "model_path": str(args.model_output),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(args.receipt_output.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
