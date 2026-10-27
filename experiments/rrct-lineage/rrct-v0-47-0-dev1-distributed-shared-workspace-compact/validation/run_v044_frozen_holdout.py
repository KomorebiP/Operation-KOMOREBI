#!/usr/bin/env python3
"""Execute the one source-sealed RRCT v0.44 holdout cohort.

This runner must remain byte-identical to the file listed in
V0_44_PREOUTCOME_FREEZE.json. The imported experiment verifies the complete
freeze before constructing any holdout candidate world or random stream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the source-sealed RRCT v0.44 holdout cohort"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "validation/v0.44.0_transformational_self_continuity/results"
        ),
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="permit a deterministic replay over an existing output directory",
    )
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[1]
    source_root = project_root / "src"
    sys.path.insert(0, str(source_root))

    from rrct.transformational_self_continuity_experiment import (  # noqa: PLC0415
        V044_HOLDOUT_SEEDS,
        run_transformational_self_continuity_cohort,
        write_transformational_self_continuity_results,
    )

    output = args.output
    if not output.is_absolute():
        output = project_root / output
    analysis_path = output / "transformational_self_continuity_analysis.json"
    if analysis_path.exists() and not args.allow_overwrite:
        raise RuntimeError(
            "frozen holdout output already exists; use a different --output "
            "for replay or pass --allow-overwrite explicitly"
        )
    output.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result = run_transformational_self_continuity_cohort(
        V044_HOLDOUT_SEEDS,
        cohort="frozen_holdout",
    )
    completed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result = dict(result)
    result["execution_receipt"] = {
        "schema": "rrct.v044.holdout_execution.v1",
        "started_at_utc": started,
        "completed_at_utc": completed,
        "python_version": sys.version,
        "platform": sys.platform,
        "process_id": os.getpid(),
        "runner_sha256": _sha256(Path(__file__).resolve()),
        "source_root": "src",
        "outcome_opened_only_after_freeze_verification": True,
    }
    paths = write_transformational_self_continuity_results(result, output)
    result_sha = _sha256(Path(paths["analysis"]))
    receipt_path = output / "HOLDOUT_EXECUTION_RECEIPT.json"
    receipt = {
        **result["execution_receipt"],
        "preoutcome_freeze_sha256": result["preoutcome_freeze_sha256"],
        "holdout_seeds": list(V044_HOLDOUT_SEEDS),
        "analysis_sha256": result_sha,
        "all_frozen_endpoints_met": bool(result["all_frozen_endpoints_met"]),
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    receipt_path.with_suffix(receipt_path.suffix + ".sha256").write_text(
        f"{_sha256(receipt_path)}  {receipt_path.name}\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": (
                    "V044_FROZEN_ENDPOINTS_MET"
                    if result["all_frozen_endpoints_met"]
                    else "V044_FROZEN_ENDPOINT_FAILURE"
                ),
                "seeds": list(V044_HOLDOUT_SEEDS),
                "preoutcome_freeze_sha256": result[
                    "preoutcome_freeze_sha256"
                ],
                "analysis_sha256": result_sha,
                **paths,
                "execution_receipt": str(receipt_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["all_frozen_endpoints_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
