from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "tools" / "verify_package.py")], check=True)
    smoke = load_toml(ROOT / "configs" / "qwen25_05b_multispace_smoke.toml")
    primary = load_toml(ROOT / "configs" / "qwen25_15b_multispace_primary.toml")
    spaces = json.loads((ROOT / "schemas" / "candidate_spaces.json").read_text(encoding="utf-8"))
    gates = json.loads((ROOT / "schemas" / "success_gates.json").read_text(encoding="utf-8"))
    prompts = json.loads((ROOT / "data" / "smoke_prompts.json").read_text(encoding="utf-8"))

    ids = [item["id"] for item in spaces["candidates"]]
    require(ids == ["V", "P", "T", "C", "O", "B", "F", "R"], "candidate IDs or order changed")
    by_id = {item["id"]: item for item in spaces["candidates"]}
    require(not by_id["V"]["admissible_for_independent_consensus"], "V must be excluded from consensus fitting")
    require(by_id["F"]["admissible_for_independent_consensus"], "frozen F must be an independent primary family")
    require(not by_id["R"]["admissible_for_independent_consensus"], "R is a diagnostic, not a consensus vote")
    require(all(not by_id[item]["uses_lens"] for item in ["P", "T", "C", "O", "B", "F", "R"]), "non-V candidates must not use the lens")

    gate_ids = [gate["id"] for gate in gates["gates"]]
    require(gate_ids == [f"G{i}" for i in range(11)], "gates must be exactly G0 through G10")
    require(primary["claim"]["required_gates"] == gate_ids[:10], "primary claim must require G0 through G9")
    require(len(primary["run"]["seeds"]) == 8, "primary must predeclare eight field seeds")
    require(len(set(primary["run"]["seeds"])) == 8, "primary field seeds must be unique")
    require(primary["data"]["task_families"] == 9, "nine task families are required")
    require(primary["data"]["holdout_total"] == 9 * primary["data"]["holdout_cases_per_family"] == 720, "primary holdout must contain 720 cases")
    require(primary["multispace"]["verbal_space_excluded_from_consensus"], "V must be excluded from primary consensus")
    require(primary["multispace"]["family_equal_weighting"], "primary consensus must weight estimator families equally")
    require(len(primary["multispace"]["required_independent_families"]) == 3, "primary needs three independent estimator families")
    require(not primary["multispace"]["relational_binding_is_consensus_estimator"], "binding cannot be counted as an independent vote")
    require(primary["lens"]["nonnegative_gradient_pursuit_required"], "primary must construct sparse nonnegative cones")
    require(primary["formation_field"]["information_firewall"], "formation field firewall must be enabled")
    require(not primary["formation_field"]["hardening"], "primary formation field must remain fuzzy")
    require(smoke["claim"]["scientific_interpretation_forbidden"], "smoke interpretation must be forbidden")
    require(smoke["multispace"]["primary_three_family_gate_unavailable"], "smoke must declare the missing third family")
    require(len(smoke["multispace"]["estimator_families"]) == 2, "smoke must contain exactly two nonverbal estimator families")
    require(len(prompts["prompts"]) == smoke["data"]["prompt_count"] == 24, "smoke prompt count must be 24")
    require(len(set(prompts["prompts"])) == 24, "smoke prompts must be unique")

    for name, config in (("smoke", smoke), ("primary", primary)):
        require(config["model"]["weights_frozen"], f"{name} model must be frozen")
        require(config["model"]["local_files_only"], f"{name} model must be local-only")
        require(all(value is False for value in config["safety"].values()), f"{name} safety blocks must remain false")
        require(config["resources"]["gpu_workers"] == 1, f"{name} GPU work must be serialized")

    require(primary["statistics"]["seed_selection_forbidden"], "performance-based seed selection must be forbidden")
    require((ROOT / "protocol" / "TASK_SUITES.md").read_text(encoding="utf-8").count("## T") == 9, "task document must define T1 through T9")

    print("V061_PROTOCOL_VALID")
    print("candidate_objects=8")
    print("smoke_estimator_families=2")
    print("primary_required_families=3")
    print("primary_holdout_cases=720")
    print("required_claim_gates=10")
    print("all_defined_gates=11")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"V061_PROTOCOL_INVALID: {exc}", file=sys.stderr)
        raise

