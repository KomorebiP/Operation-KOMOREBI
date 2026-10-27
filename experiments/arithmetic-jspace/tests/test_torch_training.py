from __future__ import annotations

import unittest

try:
    import torch
    import torch.nn.functional as F
except ImportError:  # The package's pure-data tests must still run without PyTorch.
    torch = None  # type: ignore[assignment]
    F = None  # type: ignore[assignment]

if torch is not None:
    from arithmetic_space_lab.byte_tokenizer import ByteTokenizer
    from arithmetic_space_lab.tiny_model import ModelConfig, TinyDecoderLM
    from arithmetic_space_lab.train_data import TrainingExample
    from arithmetic_space_lab.trainer import (
        TrainConfig,
        _collate,
        _optimizer,
        configure_runtime,
    )


@unittest.skipUnless(torch is not None, "PyTorch is not installed")
class TorchTrainingTests(unittest.TestCase):
    @staticmethod
    def _model_config(**overrides: object) -> "ModelConfig":
        values: dict[str, object] = {
            "vocab_size": 260,
            "d_model": 32,
            "n_layers": 3,
            "n_heads": 4,
            "ff_multiplier": 2,
            "max_seq_len": 64,
            "dropout": 0.0,
            "rope_base": 10000.0,
            "tie_embeddings": True,
        }
        values.update(overrides)
        return ModelConfig.from_dict(values)

    @staticmethod
    def _train_config() -> "TrainConfig":
        return TrainConfig.from_dict(
            {
                "max_steps": 1,
                "micro_batch_size": 1,
                "gradient_accumulation": 1,
                "learning_rate": 1e-3,
                "minimum_learning_rate": 1e-4,
                "warmup_steps": 0,
                "weight_decay": 0.01,
                "gradient_clip": 1.0,
                "checkpoint_steps": [0, 1],
                "eval_samples": 1,
                "eval_batch_size": 1,
                "max_new_tokens": 8,
                "amp": False,
                "deterministic": True,
            }
        )

    def test_continue_from_every_hidden_state_reproduces_forward_logits(self) -> None:
        torch.manual_seed(11)
        model = TinyDecoderLM(self._model_config()).eval()
        input_ids = torch.tensor(
            [[257, ord("1"), ord("2"), ord("+"), ord("3"), 258]],
            dtype=torch.long,
        )

        with torch.no_grad():
            expected_logits, hidden_states = model(input_ids, return_hidden_states=True)
            self.assertEqual(len(hidden_states), model.config.n_layers + 1)
            for completed_layers, hidden in enumerate(hidden_states):
                with self.subTest(completed_layers=completed_layers):
                    continued_logits = model.continue_from_hidden(hidden, completed_layers)
                    torch.testing.assert_close(
                        continued_logits,
                        expected_logits,
                        rtol=1e-5,
                        atol=1e-6,
                    )

    def test_separator_state_is_unchanged_by_appending_completion(self) -> None:
        torch.manual_seed(17)
        tokenizer = ByteTokenizer()
        model = TinyDecoderLM(self._model_config()).eval()
        prompt = "37 + 58 = ?"
        completion = "95"
        prefix_ids = tokenizer.prefix(prompt)
        full_input_ids, _, separator_position = tokenizer.sequence(prompt, completion)
        self.assertEqual(separator_position, len(prefix_ids) - 1)

        with torch.no_grad():
            prefix_logits, prefix_states = model(
                torch.tensor([prefix_ids], dtype=torch.long),
                return_hidden_states=True,
            )
            full_logits, full_states = model(
                torch.tensor([full_input_ids], dtype=torch.long),
                return_hidden_states=True,
            )

        for layer, (prefix_state, full_state) in enumerate(zip(prefix_states, full_states)):
            with self.subTest(layer=layer):
                torch.testing.assert_close(
                    prefix_state[:, -1],
                    full_state[:, separator_position],
                    rtol=1e-5,
                    atol=1e-6,
                )
        torch.testing.assert_close(
            prefix_logits[:, -1],
            full_logits[:, separator_position],
            rtol=1e-5,
            atol=1e-6,
        )

    def test_one_optimizer_step_is_reproducible_and_changes_weights(self) -> None:
        tokenizer = ByteTokenizer()
        example = TrainingExample(
            pair_id="unit-add-7-8",
            prompt="7 + 8 = ?",
            completion="15",
            answer="15",
            operation="add",
            difficulty=1,
            task_type="compute",
        )

        def run_once() -> tuple[dict[str, "torch.Tensor"], dict[str, "torch.Tensor"]]:
            configure_runtime(seed=23, deterministic=True)
            model = TinyDecoderLM(self._model_config(n_layers=2)).train()
            initial = {
                name: value.detach().clone() for name, value in model.state_dict().items()
            }
            optimizer = _optimizer(model, self._train_config())
            input_ids, labels, _, _ = _collate(
                [example], [0], tokenizer, torch.device("cpu")
            )
            optimizer.zero_grad(set_to_none=True)
            logits = model(input_ids)
            loss = F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]),
                labels.reshape(-1),
                ignore_index=-100,
            )
            loss.backward()
            optimizer.step()
            final = {
                name: value.detach().clone() for name, value in model.state_dict().items()
            }
            return initial, final

        first_initial, first_final = run_once()
        second_initial, second_final = run_once()
        self.assertEqual(first_initial.keys(), first_final.keys())
        self.assertTrue(
            any(
                not torch.equal(first_initial[name], first_final[name])
                for name in first_initial
            ),
            "an optimizer step must update at least one parameter",
        )
        for name in first_initial:
            with self.subTest(parameter=name):
                torch.testing.assert_close(
                    first_initial[name], second_initial[name], rtol=0.0, atol=0.0
                )
                torch.testing.assert_close(
                    first_final[name], second_final[name], rtol=0.0, atol=0.0
                )

    def test_model_config_validation_rejects_invalid_values(self) -> None:
        invalid_overrides = {
            "nonpositive_vocab": {"vocab_size": 0},
            "nonpositive_width": {"d_model": 0},
            "nonpositive_layers": {"n_layers": 0},
            "nonpositive_heads": {"n_heads": 0},
            "indivisible_heads": {"d_model": 30, "n_heads": 4},
            "odd_head_dimension": {"d_model": 28, "n_heads": 4},
            "nonpositive_ff_multiplier": {"ff_multiplier": 0},
            "short_context": {"max_seq_len": 7},
            "negative_dropout": {"dropout": -0.01},
            "unit_dropout": {"dropout": 1.0},
            "nonpositive_rope_base": {"rope_base": 0.0},
        }
        for name, overrides in invalid_overrides.items():
            with self.subTest(case=name), self.assertRaises(ValueError):
                self._model_config(**overrides)

    def test_batched_generation_matches_scalar_generation(self) -> None:
        torch.manual_seed(31)
        tokenizer = ByteTokenizer()
        model = TinyDecoderLM(self._model_config(n_layers=2)).eval()
        prefixes = [
            tokenizer.prefix("1 + 2 = ?"),
            tokenizer.prefix("3 + 4 = ?"),
        ]
        budgets = [4, 4]
        scalar = [
            model.generate(prefix, tokenizer.eos_id, budget, torch.device("cpu"))
            for prefix, budget in zip(prefixes, budgets)
        ]
        batched = model.generate_batch(
            prefixes, tokenizer.eos_id, budgets, torch.device("cpu")
        )
        self.assertEqual(batched, scalar)


if __name__ == "__main__":
    unittest.main()
