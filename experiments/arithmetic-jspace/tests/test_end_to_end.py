from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from arithmetic_space_lab.audit import audit_dataset
from arithmetic_space_lab.config import DEFAULT_CONFIG, load_config, validate_config
from arithmetic_space_lab.generate import generate


class EndToEndTests(unittest.TestCase):
    def test_generation_is_auditable_and_deterministic(self) -> None:
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["counts"] = {"train": 80, "validation": 12, "test_iid": 12}
        config["difficulty_weights"] = {"1": 0.25, "2": 0.5, "3": 0.25}
        config["operations"] |= {
            "div_remainder": 0.4,
            "fraction_add": 0.3,
            "mixed": 0.3,
        }
        config["output"]["shard_size"] = 50
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            roundtrip = Path(temporary) / "roundtrip"
            first_manifest = generate(config, first)
            second_manifest = generate(config, second)
            roundtrip_config = load_config(first / "resolved_config.json")
            roundtrip_config["output"]["shard_size"] = 17
            generate(roundtrip_config, roundtrip)
            first_report = audit_dataset(first)
            second_report = audit_dataset(second)
            self.assertEqual(first_report["status"], "PASS")
            self.assertEqual(second_report["status"], "PASS")
            self.assertEqual(first_manifest["actual_counts"], second_manifest["actual_counts"])
            first_lines = sorted((first / "canonical").glob("*.jsonl"))
            second_lines = sorted((second / "canonical").glob("*.jsonl"))
            roundtrip_lines = sorted((roundtrip / "canonical").glob("*.jsonl"))
            self.assertEqual(
                [path.read_text(encoding="utf-8") for path in first_lines],
                [path.read_text(encoding="utf-8") for path in second_lines],
            )
            def records(paths: list[Path]) -> list[str]:
                return [line for path in paths for line in path.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(records(first_lines), records(roundtrip_lines))

    def test_regimes_share_prompts_and_pairs(self) -> None:
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["counts"] = {"train": 30, "validation": 5, "test_iid": 5}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "data"
            generate(config, root)

            def load(directory: Path) -> dict[str, dict]:
                records = {}
                for path in directory.glob("*.jsonl"):
                    for line in path.read_text(encoding="utf-8").splitlines():
                        record = json.loads(line)
                        records[record["pair_id"]] = record
                return records

            answer = load(root / "sft_answer_only")
            worked = load(root / "sft_worked")
            self.assertEqual(set(answer), set(worked))
            for pair_id in answer:
                self.assertEqual(answer[pair_id]["prompt"], worked[pair_id]["prompt"])
                self.assertEqual(answer[pair_id]["answer"], worked[pair_id]["answer"])

    def test_unsafe_split_names_are_rejected(self) -> None:
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["counts"] = {"train": 0, "validation": 0, "test_iid": 0, "../../escaped": 1}
        with self.assertRaises(ValueError):
            validate_config(config)
        config = copy.deepcopy(DEFAULT_CONFIG)
        config["holdouts"] = [{"name": "test_../../escaped", "count": 1}]
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_symbolic_profile_has_no_system_or_english_prompt(self) -> None:
        profile = Path(__file__).resolve().parents[1] / "configs" / "symbolic_only.json"
        config = load_config(profile)
        config["counts"] = {"train": 20, "validation": 4, "test_iid": 4}
        config["holdouts"] = []
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "symbolic"
            generate(config, root)
            record_path = next((root / "sft_symbolic_answer").glob("train-*.jsonl"))
            record = json.loads(record_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual([message["role"] for message in record["messages"]], ["user", "assistant"])
            self.assertNotRegex(record["prompt"], r"[A-Za-z]")


if __name__ == "__main__":
    unittest.main()
