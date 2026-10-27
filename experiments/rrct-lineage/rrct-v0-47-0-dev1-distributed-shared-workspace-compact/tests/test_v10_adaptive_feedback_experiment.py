import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from rrct._release_provenance import V0_10_DEV2_SOURCE_HASHES
from rrct._version import __version__
from rrct.environment import BindingEpisode
import rrct.adaptive_feedback_experiment as experiment


def _relabel(item: experiment.LoadEpisode) -> experiment.LoadEpisode:
    episode = BindingEpisode(
        observations=item.episode.observations.copy(),
        context=-item.episode.context,
        object_cue=-item.episode.object_cue,
        actuator_map=-item.episode.actuator_map,
        episode_id=item.episode.episode_id,
    )
    return experiment.LoadEpisode(
        episode=episode,
        regime=item.regime,
        load_profile=item.load_profile,
        split=item.split,
        split_index=item.split_index,
        digest=experiment._episode_digest(
            episode,
            regime=item.regime,
            load_profile=item.load_profile,
            split=item.split,
        ),
    )


def _snapshots(
    seed: int,
    episodes: list[experiment.LoadEpisode],
) -> tuple[dict, dict]:
    predictor, forecaster, _ = experiment._train_shared_predictors(seed, episodes)
    return predictor, forecaster


class AdaptiveFeedbackDesignTests(unittest.TestCase):
    def test_embedded_dev2_manifest_matches_complete_checkout(self) -> None:
        if __version__ != "0.10.0.dev2":
            self.skipTest("exact dev2 checkout assertion applies only to v0.10.0.dev2")
        project_root = Path(__file__).resolve().parents[1]
        observed = {
            relative: hashlib.sha256((project_root / relative).read_bytes()).hexdigest()
            for relative in V0_10_DEV2_SOURCE_HASHES
        }
        self.assertEqual(observed, V0_10_DEV2_SOURCE_HASHES)

    def test_source_hashes_use_embedded_manifest_outside_checkout(self) -> None:
        if __version__ != "0.10.0.dev2":
            self.skipTest("installed dev2 manifest assertion applies only to v0.10.0.dev2")
        source_package = Path(experiment.__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            installed_package = Path(directory) / "site-packages" / "rrct"
            installed_package.mkdir(parents=True)
            for relative in V0_10_DEV2_SOURCE_HASHES:
                if relative.startswith("src/rrct/"):
                    name = Path(relative).name
                    shutil.copyfile(source_package / name, installed_package / name)
            shutil.copyfile(
                source_package / "_release_provenance.py",
                installed_package / "_release_provenance.py",
            )
            installed_file = installed_package / "adaptive_feedback_experiment.py"
            with patch.object(experiment, "__file__", str(installed_file)):
                observed = experiment._source_hashes()
                self.assertEqual(
                    {
                        key: value
                        for key, value in observed.items()
                        if key != "src/rrct/_release_provenance.py"
                    },
                    V0_10_DEV2_SOURCE_HASHES,
                )
                self.assertEqual(
                    observed["src/rrct/_release_provenance.py"],
                    hashlib.sha256(
                        (installed_package / "_release_provenance.py").read_bytes()
                    ).hexdigest(),
                )
                self.assertEqual(
                    experiment._source_provenance_mode(),
                    "installed_distribution",
                )

    def test_source_hashes_reject_partial_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package_file = (
                Path(directory)
                / "project"
                / "src"
                / "rrct"
                / "adaptive_feedback_experiment.py"
            )
            package_file.parent.mkdir(parents=True)
            package_file.write_bytes(b"placeholder")
            with patch.object(experiment, "__file__", str(package_file)):
                with self.assertRaises(FileNotFoundError):
                    experiment._source_hashes()

    def test_balanced_design_and_profiles_are_deterministic(self) -> None:
        first = experiment._make_load_split(
            32,
            seed=4101,
            split="probe",
            sequence_length=6,
        )
        second = experiment._make_load_split(
            32,
            seed=4101,
            split="probe",
            sequence_length=6,
        )
        self.assertEqual([item.digest for item in first], [item.digest for item in second])
        for left, right in zip(first, second):
            np.testing.assert_array_equal(
                left.episode.observations,
                right.episode.observations,
            )

        self.assertEqual(Counter(item.regime for item in first), {name: 8 for name in experiment.REGIMES})
        factor_regimes = Counter(
            (
                item.episode.context,
                item.episode.object_cue,
                item.episode.actuator_map,
                item.regime,
            )
            for item in first
        )
        self.assertEqual(set(factor_regimes.values()), {1})
        self.assertEqual(len({item.digest for item in first}), len(first))
        self.assertTrue(
            all(
                np.all(np.isfinite(item.episode.observations))
                and len(item.load_profile) == 6
                and all(0.0 <= value <= 1.0 for value in item.load_profile)
                for item in first
            )
        )

        for regime in experiment.REGIMES:
            profile = experiment._load_profile(regime, 6)
            self.assertEqual(profile.shape, (6,))
            if regime == "low":
                np.testing.assert_array_equal(profile, np.full(6, 0.18))
            elif regime == "high":
                np.testing.assert_array_equal(profile, np.full(6, 0.92))
            elif regime == "load_up":
                self.assertLess(profile[0], profile[-1])
            else:
                self.assertGreater(profile[0], profile[-1])
        with self.assertRaises(ValueError):
            experiment._load_profile("unknown", 6)

    def test_derangement_is_deterministic_bijective_and_has_no_fixed_points(self) -> None:
        for count in (2, 3, 8):
            first = experiment._derangement(count, seed=4200 + count)
            second = experiment._derangement(count, seed=4200 + count)
            self.assertEqual(first, second)
            self.assertEqual(sorted(first), list(range(count)))
            self.assertTrue(all(index != source for index, source in enumerate(first)))
        with self.assertRaises(ValueError):
            experiment._derangement(1, seed=1)

        episodes = experiment._make_load_split(
            32,
            seed=4209,
            split="evaluation",
            sequence_length=6,
        )
        cross_regime = experiment._regime_derangement(episodes, seed=4210)
        self.assertEqual(sorted(cross_regime), list(range(len(episodes))))
        self.assertTrue(
            all(
                target != source
                and episodes[target].regime != episodes[source].regime
                for target, source in enumerate(cross_regime)
            )
        )

    def test_predictor_training_and_adaptive_schedule_do_not_read_metadata_labels(self) -> None:
        original = experiment._make_load_split(
            8,
            seed=4301,
            split="probe",
            sequence_length=6,
        )[:2]
        relabeled = [_relabel(item) for item in original]

        original_predictor, original_forecaster, original_receipt = (
            experiment._train_shared_predictors(4302, original)
        )
        relabeled_predictor, relabeled_forecaster, relabeled_receipt = (
            experiment._train_shared_predictors(4302, relabeled)
        )
        self.assertEqual(
            experiment._object_digest(original_predictor),
            experiment._object_digest(relabeled_predictor),
        )
        self.assertEqual(
            experiment._object_digest(original_forecaster),
            experiment._object_digest(relabeled_forecaster),
        )
        self.assertNotEqual(
            original_receipt["training_split_digest"],
            relabeled_receipt["training_split_digest"],
        )

        original_agent = experiment._make_agent(
            4302,
            arm="adaptive_aligned",
            predictor_snapshot=original_predictor,
            forecaster_snapshot=original_forecaster,
        )
        relabeled_agent = experiment._make_agent(
            4302,
            arm="adaptive_aligned",
            predictor_snapshot=original_predictor,
            forecaster_snapshot=original_forecaster,
        )
        original_run = experiment._run_split(
            original_agent,
            original,
            seed=4302,
            arm="adaptive_aligned",
            split="probe",
        )
        relabeled_run = experiment._run_split(
            relabeled_agent,
            relabeled,
            seed=4302,
            arm="adaptive_aligned",
            split="probe",
        )
        np.testing.assert_array_equal(original_run.features, relabeled_run.features)
        self.assertEqual(original_run.schedules, relabeled_run.schedules)
        self.assertFalse(np.array_equal(original_run.factors, relabeled_run.factors))

    def test_manual_shuffled_run_applies_the_declared_source_schedules(self) -> None:
        episodes = experiment._make_load_split(
            8,
            seed=4401,
            split="evaluation",
            sequence_length=6,
        )[:2]
        predictor, forecaster = _snapshots(4402, episodes)
        aligned_agent = experiment._make_agent(
            4402,
            arm="adaptive_aligned",
            predictor_snapshot=predictor,
            forecaster_snapshot=forecaster,
        )
        aligned = experiment._run_split(
            aligned_agent,
            episodes,
            seed=4402,
            arm="adaptive_aligned",
            split="evaluation",
        )
        permutation = (1, 0)
        schedules = tuple(aligned.schedules[source] for source in permutation)
        shuffled_agent = experiment._make_agent(
            4402,
            arm="adaptive_shuffled",
            predictor_snapshot=predictor,
            forecaster_snapshot=forecaster,
        )
        shuffled = experiment._run_split(
            shuffled_agent,
            episodes,
            seed=4402,
            arm="adaptive_shuffled",
            split="evaluation",
            manual_schedules=schedules,
            schedule_sources=permutation,
        )

        self.assertEqual(shuffled.schedules, schedules)
        for target, record in enumerate(shuffled.episode_records):
            source = permutation[target]
            self.assertEqual(record["schedule_source_episode_index"], source)
            self.assertEqual(
                record["schedule_source_episode_hash"],
                episodes[source].digest,
            )
        for row in shuffled.telemetry_rows:
            target = int(row["episode_index"])
            step = int(row["step"])
            expected = schedules[target][step]
            self.assertEqual(row["applied_recurrent_gain"], expected[0])
            self.assertEqual(row["applied_closure_gain"], expected[1])
        self.assertTrue(shuffled.frozen_audit["frozen"])

    def test_manual_schedule_source_validation_is_fail_closed(self) -> None:
        episodes = experiment._make_load_split(
            8,
            seed=4501,
            split="evaluation",
            sequence_length=6,
        )[:2]
        predictor, forecaster = _snapshots(4502, episodes)
        schedule = tuple((0.65, 0.65) for _ in range(6))
        schedules = (schedule, schedule)
        invalid_sources = ((0,), (2, 0), (-1, 0))
        for sources in invalid_sources:
            with self.subTest(sources=sources):
                agent = experiment._make_agent(
                    4502,
                    arm="adaptive_shuffled",
                    predictor_snapshot=predictor,
                    forecaster_snapshot=forecaster,
                )
                with self.assertRaises(ValueError):
                    experiment._run_split(
                        agent,
                        episodes,
                        seed=4502,
                        arm="adaptive_shuffled",
                        split="evaluation",
                        manual_schedules=schedules,
                        schedule_sources=sources,
                    )


class AdaptiveFeedbackOutputTests(unittest.TestCase):
    @staticmethod
    def _fake_plot(path: Path, **_: object) -> None:
        path.write_bytes(b"rrct-v010-test-plot\n")

    def test_invalid_parameters_do_not_create_an_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "invalid"
            with self.assertRaises(ValueError):
                experiment.run_adaptive_feedback_experiment(
                    output,
                    seeds=(),
                    predictor_episode_count=8,
                    probe_episode_count=8,
                    calibration_episode_count=8,
                    evaluation_episode_count=8,
                    sequence_length=6,
                    bootstrap_resamples=4,
                )
            self.assertFalse(output.exists())
            for name, replacement in (
                ("seeds", (True,)),
                ("bootstrap_seed", True),
                ("schedule_seed", 1.5),
            ):
                with self.subTest(name=name):
                    arguments = {
                        "seeds": (3011,),
                        "predictor_episode_count": 8,
                        "probe_episode_count": 8,
                        "calibration_episode_count": 8,
                        "evaluation_episode_count": 8,
                        "sequence_length": 6,
                        "bootstrap_resamples": 4,
                    }
                    arguments[name] = replacement
                    invalid_output = Path(directory) / f"invalid-{name}"
                    with self.assertRaises(ValueError):
                        experiment.run_adaptive_feedback_experiment(
                            invalid_output,
                            **arguments,
                        )
                    self.assertFalse(invalid_output.exists())

    def test_nonempty_output_is_refused_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "occupied"
            output.mkdir()
            marker = output / "owned.txt"
            marker.write_bytes(b"user-data")
            with self.assertRaises(FileExistsError):
                experiment.run_adaptive_feedback_experiment(output, seeds=(3011,))
            self.assertEqual(marker.read_bytes(), b"user-data")
            self.assertEqual(tuple(output.iterdir()), (marker,))

    def test_tiny_runner_is_deterministic_and_artifacts_are_complete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "first"
            second_path = root / "second"
            parameters = {
                "seeds": (3011,),
                "predictor_episode_count": 8,
                "probe_episode_count": 8,
                "calibration_episode_count": 8,
                "evaluation_episode_count": 8,
                "sequence_length": 6,
                "bootstrap_resamples": 8,
                "bootstrap_seed": 4601,
            }
            with patch.object(
                experiment,
                "_plot_results",
                side_effect=self._fake_plot,
            ):
                first = experiment.run_adaptive_feedback_experiment(
                    first_path,
                    **parameters,
                )
                second = experiment.run_adaptive_feedback_experiment(
                    second_path,
                    **parameters,
                )

            self.assertEqual(first, second)
            self.assertEqual(
                first["row_counts"],
                {
                    "telemetry": 864,
                    "episode_predictions": 144,
                    "seed_summaries": 7,
                    "bootstrap_contrasts": 4,
                },
            )
            self.assertEqual(len(first["split_records"]), 1)
            self.assertTrue(first["split_records"][0]["episode_hashes_disjoint"])
            self.assertEqual(len(first["shared_snapshot_load_audits"]), 6)
            self.assertTrue(
                all(
                    row["exact_shared_snapshot_match"]
                    for row in first["shared_snapshot_load_audits"]
                )
            )
            self.assertEqual(len(first["schedule_permutation_provenance"]), 3)
            self.assertTrue(
                all(
                    row["is_bijection"]
                    and row["has_no_fixed_points"]
                    and row["schedule_multiset_preserved"]
                    for row in first["schedule_permutation_provenance"]
                )
            )
            self.assertEqual(len(first["frozen_learning_audits"]), 18)
            self.assertTrue(
                all(row["frozen"] for row in first["frozen_learning_audits"])
            )
            self.assertEqual(len(first["probe_immutability_audits"]), 12)
            self.assertTrue(
                all(row["unchanged"] for row in first["probe_immutability_audits"])
            )
            self.assertFalse(first["integrity"]["official_development_design"])
            self.assertTrue(first["gate_results"]["all_integrity_checks_pass"])
            self.assertTrue(first["integrity"]["all_next_step_links_valid"])
            self.assertTrue(first["integrity"]["telemetry_rows_unique"])

            for artifact in first["artifacts"]:
                self.assertTrue((first_path / artifact).is_file())
            manifest = json.loads(
                (first_path / "artifact_sha256.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                set(manifest),
                set(first["artifacts"]) - {"artifact_sha256.json"},
            )
            for name, expected_digest in manifest.items():
                observed = hashlib.sha256((first_path / name).read_bytes()).hexdigest()
                self.assertEqual(observed, expected_digest)
                self.assertEqual(
                    (first_path / name).read_bytes(),
                    (second_path / name).read_bytes(),
                )

            csv_counts = {
                "adaptive_feedback_telemetry.csv": 864,
                "adaptive_feedback_episode_predictions.csv": 144,
                "adaptive_feedback_seed_summaries.csv": 7,
                "adaptive_feedback_bootstrap_contrasts.csv": 4,
            }
            for name, expected_count in csv_counts.items():
                with (first_path / name).open(newline="", encoding="utf-8") as handle:
                    self.assertEqual(sum(1 for _ in csv.DictReader(handle)), expected_count)

    def test_bootstrap_is_deterministic_and_strictly_validated(self) -> None:
        values = (-0.2, 0.1, 0.3, 0.4)
        first = experiment._bootstrap_mean(values, resamples=25, seed=4701)
        second = experiment._bootstrap_mean(values, resamples=25, seed=4701)
        self.assertEqual(first, second)
        self.assertEqual(first["seed_count"], 4)
        self.assertEqual(first["strictly_positive_seeds"], 3)
        for invalid in (0, True, 1.5):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    experiment._bootstrap_mean(values, resamples=invalid, seed=1)


if __name__ == "__main__":
    unittest.main()
