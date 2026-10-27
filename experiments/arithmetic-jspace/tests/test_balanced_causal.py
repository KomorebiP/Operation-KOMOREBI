from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    import torch
except ImportError:
    torch = None  # type: ignore[assignment]

if torch is not None:
    from arithmetic_space_lab.balanced_space import (
        BalancedSpace,
        BalancedSpaceConfig,
        discover_balanced_space,
    )
    from arithmetic_space_lab.byte_tokenizer import ByteTokenizer
    from arithmetic_space_lab.causal_workspace import (
        _generation_record,
        _score_outputs,
        ablate_hidden,
        patch_hidden,
        rescue_hidden,
        run_causal_assay,
    )
    from arithmetic_space_lab.tiny_model import ModelConfig, TinyDecoderLM


@unittest.skipUnless(torch is not None, "PyTorch is not installed")
class BalancedCausalTests(unittest.TestCase):
    @staticmethod
    def _model() -> "TinyDecoderLM":
        torch.manual_seed(71)
        config = ModelConfig.from_dict(
            {
                "vocab_size": 260,
                "d_model": 16,
                "n_layers": 3,
                "n_heads": 2,
                "ff_multiplier": 2,
                "max_seq_len": 48,
                "dropout": 0.0,
                "rope_base": 10000.0,
                "tie_embeddings": True,
            }
        )
        return TinyDecoderLM(config).eval()

    def test_projection_primitives_ablate_patch_and_rescue_exact_coordinates(self) -> None:
        torch.manual_seed(73)
        hidden = torch.randn(2, 4, 8)
        donor = torch.randn(2, 5, 8)
        basis, _ = torch.linalg.qr(torch.randn(8, 3))
        mean = torch.randn(8)
        rows = torch.arange(2)
        positions = torch.tensor([1, 2])
        donor_positions = torch.tensor([3, 4])

        ablated, ablation_norm = ablate_hidden(
            hidden, positions, basis=basis, mean=mean
        )
        expected_mean_coordinates = mean @ basis
        torch.testing.assert_close(
            ablated[rows, positions] @ basis,
            expected_mean_coordinates.expand(2, -1),
            rtol=1e-5,
            atol=1e-5,
        )
        self.assertTrue(bool((ablation_norm >= 0).all()))

        patched, patch_norm = patch_hidden(
            hidden,
            donor,
            positions,
            donor_positions,
            basis=basis,
        )
        torch.testing.assert_close(
            patched[rows, positions] @ basis,
            donor[rows, donor_positions] @ basis,
            rtol=1e-5,
            atol=1e-5,
        )
        self.assertTrue(bool((patch_norm >= 0).all()))

        control_basis, _ = torch.linalg.qr(torch.randn(8, 3))
        _, matched_norm = ablate_hidden(
            hidden,
            positions,
            basis=control_basis,
            mean=mean,
            energy_reference_basis=basis,
        )
        reference_norm = (
            ((hidden[rows, positions] - mean) @ basis) @ basis.T
        ).norm(dim=-1)
        torch.testing.assert_close(matched_norm, reference_norm, rtol=1e-5, atol=1e-5)

        rescued, _ = rescue_hidden(
            ablated,
            hidden,
            positions,
            basis=basis,
            clean_positions=positions,
        )
        torch.testing.assert_close(
            rescued[rows, positions] @ basis,
            hidden[rows, positions] @ basis,
            rtol=1e-5,
            atol=1e-5,
        )

    def test_causal_exact_requires_valid_signed_decimal_eos_generation(self) -> None:
        tokenizer = ByteTokenizer()
        valid = _generation_record(
            [*tokenizer.encode("-15"), tokenizer.eos_id], tokenizer
        )
        missing_eos = _generation_record(tokenizer.encode("-15"), tokenizer)
        injected_sep = _generation_record(
            [*tokenizer.encode("-15"), tokenizer.sep_id, tokenizer.eos_id],
            tokenizer,
        )
        eos_only = _generation_record([tokenizer.eos_id], tokenizer)
        report = _score_outputs(
            [valid, missing_eos, injected_sep, eos_only],
            ["-15", "-15", "-15", ""],
        )
        self.assertEqual(report["exact_count"], 1)
        self.assertEqual(report["well_formed_count"], 1)
        self.assertEqual(report["eos_terminated_count"], 3)
        self.assertEqual(report["illegal_special_count"], 1)
        self.assertEqual(
            report["generation_records"][2]["token_ids"],
            injected_sep["token_ids"],
        )
        self.assertFalse(missing_eos["termination_valid"])
        self.assertFalse(injected_sep["well_formed"])
        self.assertFalse(eos_only["nonempty_signed_decimal"])

    def test_target_free_discovery_returns_serializable_rank_matched_space(self) -> None:
        model = self._model()
        tokenizer = ByteTokenizer()
        discovery = [
            tokenizer.prefix(text)
            for text in ("2+3=", "7+8=", "9-4=", "6-1=")
        ]
        selection = [tokenizer.prefix(text) for text in ("4+5=", "8-3=")]
        config = BalancedSpaceConfig(
            upstream_layer=0,
            source_layer=1,
            perturbations_per_prompt=2,
            perturbation_scale=0.03,
            ridge=1e-3,
            candidate_ranks=(1, 2),
            prediction_fraction_threshold=0.5,
            random_output_consumers=1,
            seed=79,
        )
        space = discover_balanced_space(
            model,
            discovery,
            selection,
            config=config,
            device=torch.device("cpu"),
        )
        self.assertIn(space.rank, {1, 2})
        self.assertEqual(space.basis.shape, (16, space.rank))
        self.assertEqual(space.projector.shape, (16, 16))
        self.assertEqual(set(space.control_bases), {"pca", "random", "complement"})
        self.assertTrue(all(value.shape == space.basis.shape for value in space.control_bases.values()))
        self.assertFalse(space.metadata["target_information_used"])
        self.assertTrue(space.metadata["prefix_only_api"])
        self.assertEqual(len(space.metadata["rank_selection"]), 2)
        self.assertIn("heldout_causal_prediction_fraction", space.metadata["rank_selection"][0])
        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "space.pt"
            space.save(artifact)
            loaded = BalancedSpace.load(artifact)
        torch.testing.assert_close(space.basis, loaded.basis)
        torch.testing.assert_close(space.projector, loaded.projector)
        self.assertEqual(space.summary()["rank"], loaded.summary()["rank"])

        leaked = [tokenizer.prefix("2+3=") + tokenizer.encode("5")]
        with self.assertRaisesRegex(ValueError, "SEP boundary"):
            discover_balanced_space(
                model,
                leaked,
                selection,
                config=config,
                device=torch.device("cpu"),
            )

    def test_free_generation_assay_is_sealed_and_includes_directional_controls(self) -> None:
        model = self._model()
        tokenizer = ByteTokenizer()
        prefixes = [tokenizer.prefix("2+3="), tokenizer.prefix("7+8=")]
        selection = [tokenizer.prefix("4+5="), tokenizer.prefix("8-3=")]
        space = discover_balanced_space(
            model,
            prefixes,
            selection,
            config=BalancedSpaceConfig(
                upstream_layer=0,
                source_layer=1,
                perturbations_per_prompt=1,
                perturbation_scale=0.03,
                ridge=1e-3,
                candidate_ranks=(1,),
                prediction_fraction_threshold=0.0,
                random_output_consumers=0,
                seed=83,
            ),
            device=torch.device("cpu"),
        )
        corrupt = [tokenizer.prefix("2+4="), tokenizer.prefix("7+9=")]
        report = run_causal_assay(
            model,
            prefixes,
            corrupt,
            ["5", "15"],
            ["6", "16"],
            space=space,
            tokenizer=tokenizer,
            device=torch.device("cpu"),
            max_new_tokens=2,
            require_directional_donor_effect=True,
            minimum_baseline_qualified_pairs=2,
            minimum_directional_rescue_pairs=2,
        )
        self.assertEqual(report["schema_version"], "causal-workspace-assay-v2")
        self.assertFalse(report["evaluation_information_used_for_discovery"])
        self.assertEqual(report["n_pairs"], 2)
        self.assertFalse(report["claim_gate_flags"]["mediation_claim_eligible"])
        self.assertTrue(
            report["claim_gate_flags"]["baseline_qualified_primary_estimands"]
        )
        self.assertTrue(report["independent_rescue_available"])
        self.assertEqual(
            report["registered_qualified_minima"],
            {
                "baseline_qualified_pairs": 2,
                "directional_rescue_pairs": 2,
                "require_directional_donor_effect": True,
            },
        )
        self.assertIn("upstream_residual_transplant", report)
        self.assertEqual(
            set(report["spaces"]), {"candidate", "pca", "random", "complement"}
        )
        for value in report["spaces"].values():
            self.assertIn("ablation", value)
            self.assertIn("clean_to_corrupt_patch", value)
            self.assertIn("coordinate_rescue", value)
            self.assertEqual(len(value["clean_to_corrupt_patch"]["outputs"]), 2)
            self.assertIn("corrupt_answer_retention", value["clean_to_corrupt_patch"])
            patch_estimand = value["clean_to_corrupt_patch"]["primary_estimand"]
            self.assertIn("qualified_denominator_count", patch_estimand)
            self.assertIn("qualified_clean_conversion_count", patch_estimand)
            self.assertIn("qualified_clean_conversion_rate", patch_estimand)
            self.assertEqual(
                patch_estimand["claim_eligible"],
                patch_estimand["qualified_denominator_count"] >= 2,
            )
            self.assertTrue(value["coordinate_rescue"]["independent_rescue"])
            self.assertEqual(len(value["coordinate_rescue"]["items"]), 2)
            rescue_estimand = value["coordinate_rescue"]["primary_estimand"]
            self.assertIn("qualified_denominator_count", rescue_estimand)
            self.assertIn("qualified_rescue_count", rescue_estimand)
            self.assertIn("qualified_rescue_rate", rescue_estimand)
            self.assertEqual(
                rescue_estimand["claim_eligible"],
                rescue_estimand["qualified_denominator_count"] >= 2,
            )
            for item in value["coordinate_rescue"]["items"]:
                if item["baseline_qualified"]:
                    self.assertTrue(item["corruption_matches_corrupt_expected"])
            for generation in value["ablation"]["generation_records"]:
                self.assertIn("token_ids", generation)
                self.assertIn("termination_valid", generation)


if __name__ == "__main__":
    unittest.main()
