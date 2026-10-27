from __future__ import annotations

from deterministic_bootstrap import ensure as _ensure_deterministic
_ensure_deterministic()

import argparse
import json
from pathlib import Path

from block23.external.audit import run_causal_audit, summarize_causal_audit
from block23.external.multimode_coconut import MultimodeCoconutAdapter
from block23.external.prontoqa import donor_pairs, load_prontoqa, semantic_twin
from block23.external.preflight import run_preflight
from block23.receipts import digest, write_json

ROOT = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the sealed SRIC Block 23 real Coconut causal pilot.")
    ap.add_argument("--repo-dir", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--limit", type=int, default=32)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--num-latents", type=int, default=6)
    ap.add_argument("--output", default=str(ROOT / "external_status" / "real_pilot_result.json"))
    args = ap.parse_args()

    preflight = run_preflight(args.repo_dir, args.checkpoint, ROOT / "frozen" / "SOURCE_LOCK.json")
    if preflight["status"] not in {"READY_FOR_REAL_CHECKPOINT_AUDIT", "READY_CPU_ONLY"}:
        raise SystemExit(f"preflight failed closed: {preflight['blockers']}")

    tasks = load_prontoqa(args.tasks)[: args.limit]
    donors = donor_pairs(tasks)
    twins = {t.task_id: semantic_twin(t, 7000+i) for i, t in enumerate(tasks)}
    adapter = MultimodeCoconutAdapter(
        args.repo_dir,
        args.checkpoint,
        ROOT / "frozen" / "SOURCE_LOCK.json",
        device=args.device,
        num_latents=args.num_latents,
    )
    records = run_causal_audit(adapter, tasks, donors=donors, twins=twins)
    result = {
        "schema": "sric.block23.real-pilot-result.v1",
        "preflight": preflight,
        "summary": summarize_causal_audit(records),
        "records": records,
        "claim_boundary": "External-checkpoint evidence only. This result does not by itself establish endogenous ontology discovery or unrestricted interpretability.",
    }
    result["receipt"] = digest(result)
    write_json(args.output, result)
    print(f"SRIC_BLOCK23_REAL_TASKS={len(records)}")
    print(f"SRIC_BLOCK23_REAL_RECEIPT={result['receipt']}")


if __name__ == "__main__":
    main()
