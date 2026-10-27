from __future__ import annotations

from pathlib import Path
import json

from .schemas import TaskRecord
from .dataset import save_records


_PREDICATES = [
    "amber", "bright", "calm", "dense", "eager", "frosty", "gentle", "hollow",
    "ivory", "jagged", "kind", "lunar", "mild", "narrow", "open", "plain",
]
_ENTITIES = [
    "Ari", "Bela", "Ciro", "Dara", "Eli", "Faye", "Gio", "Hana",
    "Ira", "Juno", "Kian", "Lena", "Milo", "Nora", "Oren", "Pia",
]


def make_fixture_records(count: int = 48) -> list[TaskRecord]:
    if count < 24:
        raise ValueError("Fixture requires at least 24 tasks")
    records: list[TaskRecord] = []
    for index in range(count):
        depth = 3 + (index % 4)
        entity = _ENTITIES[index % len(_ENTITIES)]
        offset = (index * 3 + index // 4) % len(_PREDICATES)
        chain = [_PREDICATES[(offset + 5 * step) % len(_PREDICATES)] for step in range(depth + 1)]
        answer = "True" if index % 2 == 0 else "False"
        facts = [f"{entity} is {chain[0]}."]
        rules = [f"Every {chain[step]} thing is {chain[step + 1]}." for step in range(depth)]
        distractor_entity = _ENTITIES[(index + 5) % len(_ENTITIES)]
        distractor = f"{distractor_entity} is {_PREDICATES[(offset + 7) % len(_PREDICATES)]}."
        target = chain[-1] if answer == "True" else _PREDICATES[(offset + 11) % len(_PREDICATES)]
        question = " ".join(facts + rules + [distractor, f"True or false: {entity} is {target}."])
        steps = tuple(
            f"From {entity} being {chain[step]} and the rule from {chain[step]} to {chain[step + 1]}, infer {entity} is {chain[step + 1]}."
            for step in range(depth)
        )
        signature = tuple(f"edge:{chain[step]}->{chain[step + 1]}" for step in range(depth))
        records.append(
            TaskRecord(
                task_id=f"fixture-{index:03d}",
                question=question,
                answer=answer,
                steps=steps,
                proof_depth=depth,
                proof_signature=signature,
                orbit_id=f"fixture-orbit-{index:03d}",
                group_id=f"fixture-template-{index % 12:02d}",
                metadata={"fixture": True, "chain": chain},
            )
        )
    return records


def write_fixture(path: str | Path, count: int = 48) -> None:
    save_records(path, make_fixture_records(count))
