from __future__ import annotations

from deterministic_bootstrap import ensure as _ensure_deterministic
_ensure_deterministic()

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import json
from collections import Counter
from pathlib import Path

from block23.core import EpisodeSpec, audit_hidden, build_episode, compile_ontology, expected_certificate, summarize_records
from block23.receipts import compiled_record, digest, write_json

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "configs" / "block23.json").read_text())


def main() -> dict:
    seal_path = ROOT / "frozen" / "preaudit_seal.json"
    if not seal_path.is_file():
        raise RuntimeError("run stage_preaudit.py before final audit")
    seal = json.loads(seal_path.read_text())
    expected_plan = digest({
        "seeds": CFG["final_seeds"],
        "family_cycle": CFG["family_cycle"],
        "compiler_seed_offset": CFG["compiler_seed_offset"],
    })
    if seal["final_seed_plan_commitment"] != expected_plan:
        raise RuntimeError("final seed plan differs from pre-audit commitment")

    records = []
    cycle = CFG["family_cycle"]
    for i, seed in enumerate(CFG["final_seeds"]):
        family = cycle[i % len(cycle)]
        episode = build_episode(EpisodeSpec(family, int(seed), "final"))
        compiled = compile_ontology(episode.visible, int(seed) + int(CFG["compiler_seed_offset"]))
        audit = audit_hidden(episode, compiled)
        audit["expected_certificate"] = expected_certificate(family)
        audit["correct"] = audit["certificate"] == audit["expected_certificate"]
        audit["episode_id"] = episode.visible.episode_id
        audit["compiled"] = compiled_record(compiled)
        records.append(audit)

    summary = summarize_records(records)
    summary["all_correct"] = all(r["correct"] for r in records)
    summary["selected_methods"] = dict(Counter(str(r["selected_method"]) for r in records))
    summary["preaudit_seal"] = seal["preaudit_seal"]

    # Controls and causal-patch summaries.
    answer_rows = [r for r in records if r["family"] == "answer_shortcut"]
    identified_rows = [r for r in records if r["family"] == "identified"]
    patch_rows = identified_rows + answer_rows
    selected_patch = []
    answer_patch = []
    pca_patch = []
    random_patch = []
    for r in patch_rows:
        for m in r.get("counterfactual_patch", {}).values():
            selected_patch.append(m["selected_future_r2"])
            answer_patch.append(m["answer_only_future_r2"])
            pca_patch.append(m["pca_future_r2"])
            random_patch.append(m["random_future_r2"])
    summary["counterfactual_patch"] = {
        "minimum_selected_future_r2": min(selected_patch),
        "maximum_answer_only_future_r2": max(answer_patch),
        "maximum_pca_future_r2": max(pca_patch),
        "maximum_random_future_r2": max(random_patch),
    }

    # Answer-only candidate is allowed to predict the label but should fail semantic dynamics.
    answer_control = []
    for r in answer_rows:
        rows = [x for x in r["compiled"]["candidate_table"] if x["method"] == "answer_only"]
        answer_control.extend(rows)
    summary["answer_shortcut_control"] = {
        "minimum_answer_accuracy": min(x["worst_answer_accuracy"] for x in answer_control),
        "maximum_future_r2": max(x["worst_future_r2"] for x in answer_control),
        "maximum_intervention_r2": max(x["worst_intervention_r2"] for x in answer_control),
        "any_passed": any(x["passed"] for x in answer_control),
    }

    result = {
        "schema": "sric.block23.final-result.v1",
        "summary": summary,
        "records": records,
    }
    result["result_receipt"] = digest(result)
    write_json(ROOT / "results" / "block23_final.json", result)
    print("SRIC_BLOCK23_SYNTHETIC=PASS" if summary["all_correct"] else "SRIC_BLOCK23_SYNTHETIC=FAIL")
    print(f"episodes={summary['episodes']}")
    print(f"certificate_accuracy={summary['certificate_accuracy']:.6f}")
    print(f"result_receipt={result['result_receipt']}")
    return result


if __name__ == "__main__":
    main()
