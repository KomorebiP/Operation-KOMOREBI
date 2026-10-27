from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from arithmetic_space_lab.byte_tokenizer import ByteTokenizer
from arithmetic_space_lab.train_data import (
    TrainingExample,
    apply_control_plan,
    deranged_control_plan,
)


class TrainingDataTests(unittest.TestCase):
    def test_byte_tokenizer_round_trip_and_mask(self) -> None:
        tokenizer = ByteTokenizer()
        text = "(-12) × 7 ÷ 3 = ?"
        self.assertEqual(tokenizer.decode(tokenizer.encode(text)), text)
        inputs, labels, prompt_position = tokenizer.sequence(text, "-28")
        self.assertEqual(inputs[prompt_position], tokenizer.sep_id)
        self.assertTrue(all(value == -100 for value in labels[:prompt_position]))
        self.assertEqual(labels[prompt_position], tokenizer.encode("-28")[0])
        self.assertEqual(labels[-1], tokenizer.eos_id)

    def test_matched_derangement_has_no_fixed_targets(self) -> None:
        completions = ["10", "11", "12", "13", "14", "15"]
        examples = [
            TrainingExample(
                pair_id=f"pair-{index}",
                prompt=f"{index} + {index} = ?",
                completion=value,
                answer=value,
                operation="add",
                difficulty=1,
                task_type="compute",
            )
            for index, value in enumerate(completions)
        ]
        tokenizer = ByteTokenizer()
        plan = deranged_control_plan(examples, tokenizer)
        correct = apply_control_plan(examples, plan, shuffled=False)
        shuffled = apply_control_plan(examples, plan, shuffled=True)
        self.assertEqual([item.pair_id for item in correct], [item.pair_id for item in shuffled])
        self.assertTrue(
            all(left.completion != right.completion for left, right in zip(correct, shuffled))
        )
        self.assertTrue(
            all(
                len(tokenizer.encode(left.completion)) == len(tokenizer.encode(right.completion))
                for left, right in zip(correct, shuffled)
            )
        )
        self.assertEqual(
            Counter(item.completion for item in correct),
            Counter(item.completion for item in shuffled),
        )

    def test_control_buckets_do_not_cross_task_formats(self) -> None:
        examples = []
        for task_type, completions in (("compute", ("10", "11")), ("verify", ("20", "21"))):
            for index, completion in enumerate(completions):
                examples.append(
                    TrainingExample(
                        pair_id=f"{task_type}-{index}",
                        prompt=f"{task_type} prompt {index}",
                        completion=completion,
                        answer=completion,
                        operation="add",
                        difficulty=1,
                        task_type=task_type,
                    )
                )
        plan = deranged_control_plan(examples, ByteTokenizer())
        by_pair = {item.pair_id: item for item in examples}
        for pair_id, target in plan["assignment"].items():
            source_task = by_pair[pair_id].task_type
            target_task = next(
                item.task_type for item in examples if item.completion == target
            )
            self.assertEqual(source_task, target_task)

    def test_training_profiles_have_required_checkpoints(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root / "training_configs").glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            maximum = value["training"]["max_steps"]
            steps = value["training"]["checkpoint_steps"]
            self.assertIn(0, steps, path.name)
            self.assertIn(maximum, steps, path.name)
            self.assertTrue(set(value["probe"]["checkpoint_steps"]).issubset(steps), path.name)
            self.assertEqual(value["model"]["vocab_size"], ByteTokenizer().vocab_size)

    def test_deep_symbolic_profile_has_100_step_progress_and_curriculum(self) -> None:
        root = Path(__file__).resolve().parents[1]
        profile = json.loads(
            (root / "training_configs" / "deep_symbolic.json").read_text(encoding="utf-8")
        )
        training = profile["training"]
        self.assertEqual(training["progress_every_steps"], 100)
        self.assertEqual(training["max_steps"], 20000)
        self.assertEqual(training["curriculum_stages"][-1]["end_step"], 20000)
        self.assertEqual(
            [stage["end_step"] for stage in training["curriculum_stages"]],
            sorted(stage["end_step"] for stage in training["curriculum_stages"]),
        )
        data = json.loads(
            (root / "configs" / "deep_symbolic.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(data["operations"]), {"add", "sub", "mul", "div_exact"})
        self.assertEqual(
            {holdout["name"] for holdout in data["holdouts"]},
            {"test_ood_digits_6", "test_ood_digits_8"},
        )


if __name__ == "__main__":
    unittest.main()
