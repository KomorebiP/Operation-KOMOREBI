from __future__ import annotations

from deterministic_bootstrap import ensure as _ensure_deterministic
_ensure_deterministic()

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_name, "1")

import json
from pathlib import Path

from block23.core import EpisodeSpec, build_episode, compile_ontology
from block23.receipts import compiled_record, digest, write_json

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / "configs" / "block23.json").read_text())


def main() -> dict:
    records = []
    cycle = CFG["family_cycle"]
    for i, seed in enumerate(CFG["preaudit_seeds"]):
        family = cycle[i % len(cycle)]
        episode = build_episode(EpisodeSpec(family, int(seed), "preaudit"))
        compiled = compile_ontology(episode.visible, int(seed) + int(CFG["compiler_seed_offset"]))
        records.append({
            "episode_id": episode.visible.episode_id,
            "construction_index": i,
            "hidden_family_commitment": digest({"family": family, "seed": seed, "salt": "block23-hidden-family"}),
            "compiled": compiled_record(compiled),
        })
    seal_payload = {
        "schema": "sric.block23.preaudit-seal.v1",
        "config_digest": digest(CFG),
        "thresholds_locked": True,
        "candidate_grammar_locked": True,
        "external_source_lock": json.loads((ROOT / "frozen" / "SOURCE_LOCK.json").read_text()),
        "final_seed_plan_commitment": digest({
            "seeds": CFG["final_seeds"],
            "family_cycle": CFG["family_cycle"],
            "compiler_seed_offset": CFG["compiler_seed_offset"],
        }),
        "construction_records": records,
    }
    seal_payload["preaudit_seal"] = digest(seal_payload)
    write_json(ROOT / "frozen" / "preaudit_seal.json", seal_payload)
    print(f"BLOCK23_PREAUDIT_EPISODES={len(records)}")
    print(f"BLOCK23_PREAUDIT_SEAL={seal_payload['preaudit_seal']}")
    return seal_payload


if __name__ == "__main__":
    main()
