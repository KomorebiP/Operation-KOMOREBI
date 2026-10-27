from __future__ import annotations

from dataclasses import dataclass, field
from math import log
from typing import Mapping, Sequence

import numpy as np

from .bayes import BayesianRegression, FittedBayesianRegression, normalized_probabilities
from .lasm_memory import LASMMemory
from .lasm_programs import LASMProgram, default_lasm_programs
from .lasm_types import LASMFramePackets, LASMPrediction, LASMTransition
from .types import FloatArray
from ._validation import integer


@dataclass(frozen=True)
class FittedLASMProgram:
    program: LASMProgram
    regression: FittedBayesianRegression
    predictive_score: float
    log_prior: float
    log_weight: float
    posterior_probability: float
    feature_count: int
    output_count: int


@dataclass
class ProjectorResolvedLargeSignalModel:
    """Bayesian posterior over typed signal/operator programs."""

    programs: Sequence[LASMProgram] = field(default_factory=default_lasm_programs)
    regression: BayesianRegression = field(
        default_factory=lambda: BayesianRegression(prior_precision=1.5, shape=2.5, scale=0.05)
    )
    complexity_penalty: float = 0.0016
    mechanism_penalty: float = 0.8
    resolution_penalty: Mapping[str, float] = field(
        default_factory=lambda: {"macro": 0.0, "meso": 0.12, "micro": 0.28}
    )
    validation_fraction: float = 0.25
    minimum_records: int = 10
    maximum_fit_records: int = 512
    fitted: tuple[FittedLASMProgram, ...] = ()
    fit_count: int = 0
    refit_on_all_records: bool = True
    fit_report: dict[str, object] = field(default_factory=dict, init=False)
    _common_state_rank: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.programs = tuple(self.programs)
        names = [program.name for program in self.programs]
        if not names or len(names) != len(set(names)):
            raise ValueError("program names must be nonempty and unique")
        integer(self.minimum_records, "minimum_records", minimum=6)
        integer(self.maximum_fit_records, "maximum_fit_records", minimum=self.minimum_records)
        if not np.isfinite(self.validation_fraction) or not 0 < self.validation_fraction < 1:
            raise ValueError("validation_fraction must lie strictly between zero and one")
        penalties = [self.complexity_penalty, self.mechanism_penalty, *self.resolution_penalty.values()]
        if not all(np.isfinite(value) and value >= 0 for value in penalties):
            raise ValueError("model penalties must be finite and nonnegative")

    def _fit_program(
        self,
        program: LASMProgram,
        records: Sequence[LASMTransition],
    ) -> tuple[FittedBayesianRegression, float, float, int, int]:
        design = np.vstack([program.design_transition(record) for record in records])
        targets = np.vstack([program.targets(record) for record in records])
        n = design.shape[0]
        split = max(6, int(round((1.0 - self.validation_fraction) * n)))
        split = min(split, n - 2)
        if split < 4:
            split = n
        fitted = self.regression.fit(design[:split], targets[:split])
        # Comparing densities on differently sized target spaces is invalid.
        # Every candidate is scored on the same nested state prefix and five
        # shared outcome channels; extra state outputs remain useful for prediction.
        columns = list(range(self._common_state_rank)) + list(range(targets.shape[1] - 5, targets.shape[1]))
        predictive = fitted.predictive_log_likelihood(
            design[split:], targets[split:], output_indices=columns
        )
        if self.refit_on_all_records:
            fitted = self.regression.fit(design, targets)
        complexity = program.complexity(design.shape[1], targets.shape[1])
        log_prior = (
            -self.complexity_penalty * complexity
            -self.mechanism_penalty * program.mechanism_count
            -float(self.resolution_penalty.get(program.resolution, 0.0))
        )
        return fitted, float(predictive), float(log_prior), design.shape[1], targets.shape[1]

    def fit(self, memory: LASMMemory | Sequence[LASMTransition]) -> tuple[FittedLASMProgram, ...]:
        records = list(memory.records if isinstance(memory, LASMMemory) else memory)
        records = records[-self.maximum_fit_records :]
        self.fitted = ()
        self.fit_report = {"status": "insufficient_records", "records": len(records),
                           "candidate_count": len(self.programs), "failed_candidates": {}}
        if len(records) < self.minimum_records:
            self.fitted = ()
            return self.fitted
        self._common_state_rank = min(program.state_rank for program in self.programs)
        reference = np.vstack([self.programs[0].targets(record)[:self._common_state_rank] for record in records])
        for program in self.programs[1:]:
            candidate = np.vstack([program.targets(record)[:self._common_state_rank] for record in records])
            if not np.allclose(candidate, reference, rtol=1e-11, atol=1e-12):
                self.fit_report["status"] = "incomparable_state_targets"
                raise ValueError("candidate resolutions do not share a comparable nested state target")
        self.fit_report.update({"common_state_rank": self._common_state_rank,
                                "scored_output_count": self._common_state_rank + 5,
                                "refit_on_all_records": self.refit_on_all_records})
        failures: dict[str, str] = {}
        provisional: list[
            tuple[LASMProgram, FittedBayesianRegression, float, float, float, int, int]
        ] = []
        for program in self.programs:
            try:
                with np.errstate(over="raise", invalid="raise", divide="raise"):
                    fitted, predictive, log_prior, features, outputs = self._fit_program(program, records)
                if not np.isfinite(predictive + log_prior):
                    raise FloatingPointError("candidate score is not finite")
            except (ValueError, FloatingPointError, np.linalg.LinAlgError) as exc:
                failures[program.name] = f"{type(exc).__name__}: {exc}"
                continue
            provisional.append(
                (
                    program,
                    fitted,
                    predictive,
                    log_prior,
                    predictive + log_prior,
                    features,
                    outputs,
                )
            )
        self.fit_report["failed_candidates"] = failures
        self.fit_report["fitted_candidates"] = len(provisional)
        if not provisional:
            self.fit_report["status"] = "all_candidates_failed"
            self.fitted = ()
            return self.fitted
        probability = normalized_probabilities(np.asarray([row[4] for row in provisional], dtype=float))
        completed = [
            FittedLASMProgram(
                program=row[0],
                regression=row[1],
                predictive_score=row[2],
                log_prior=row[3],
                log_weight=row[4],
                posterior_probability=float(weight),
                feature_count=row[5],
                output_count=row[6],
            )
            for row, weight in zip(provisional, probability, strict=True)
        ]
        self.fitted = tuple(sorted(completed, key=lambda item: item.posterior_probability, reverse=True))
        self.fit_report["status"] = "fit_with_failures" if failures else "fit"
        self.fit_count += 1
        return self.fitted

    @staticmethod
    def _aggregate(items: Sequence[FittedLASMProgram], attribute: str) -> dict[str, float]:
        output: dict[str, float] = {}
        for item in items:
            key = str(getattr(item.program, attribute))
            output[key] = output.get(key, 0.0) + item.posterior_probability
        return output

    def posterior_summary(self) -> dict[str, object]:
        family = self._aggregate(self.fitted, "family")
        atlas = self._aggregate(self.fitted, "atlas")
        resolution = self._aggregate(self.fitted, "resolution")
        program = {item.program.name: item.posterior_probability for item in self.fitted}
        entropy = -sum(value * log(max(value, 1e-15)) for value in program.values())
        return {
            "best_program": None if not self.fitted else self.fitted[0].program.name,
            "best_probability": 0.0 if not self.fitted else self.fitted[0].posterior_probability,
            "family_probabilities": family,
            "atlas_probabilities": atlas,
            "resolution_probabilities": resolution,
            "program_probabilities": program,
            "posterior_entropy": float(entropy),
            "fit_count": self.fit_count,
            "fit_report": dict(self.fit_report),
        }

    def _design_action(
        self,
        item: FittedLASMProgram,
        packets: LASMFramePackets,
        action_features: FloatArray,
        memory: LASMMemory,
        step_index: int,
    ) -> FloatArray:
        previous, power, exponential = memory.context(item.program.resolution)
        return item.program.design_row(
            packets,
            action_features,
            step_index=step_index,
            previous=previous,
            power_memory=power,
            exponential_memory=exponential,
        )

    def predict_action(
        self,
        packets: LASMFramePackets,
        action_features: FloatArray,
        memory: LASMMemory,
        *,
        step_index: int,
    ) -> LASMPrediction:
        if not self.fitted:
            return LASMPrediction(
                expected_reward=0.0,
                expected_progress=0.0,
                win_probability=0.0,
                loss_probability=0.0,
                change_probability=0.5,
                expected_change_norm=0.25,
                predictive_variance=1.0,
                model_disagreement=1.0,
                information_score=1.0,
                family_probabilities={},
                atlas_probabilities={},
                resolution_probabilities={},
                program_probabilities={},
            )
        weights: list[float] = []
        scalars: list[FloatArray] = []
        variances: list[FloatArray] = []
        change_norms: list[float] = []
        used: list[FittedLASMProgram] = []
        for item in self.fitted:
            row = self._design_action(item, packets, action_features, memory, step_index)
            if row.size != item.feature_count:
                continue
            mean, variance = item.regression.predict(row)
            state_dimension = item.program.state_rank
            scalar = mean[0, state_dimension : state_dimension + 5]
            scalar_variance = variance[0, state_dimension : state_dimension + 5]
            if scalar.size != 5:
                continue
            weights.append(item.posterior_probability)
            scalars.append(scalar)
            variances.append(scalar_variance)
            change_norms.append(float(np.linalg.norm(mean[0, :state_dimension])))
            used.append(item)
        if not weights:
            return LASMPrediction(0, 0, 0, 0, 0.5, 0.25, 1, 1, 1, {}, {}, {}, {})
        probability = np.asarray(weights, dtype=float)
        probability /= probability.sum()
        matrix = np.vstack(scalars)
        variance_matrix = np.vstack(variances)
        mean = probability @ matrix
        aleatoric = probability @ variance_matrix
        epistemic = probability @ ((matrix - mean[None, :]) ** 2)
        total_variance = float(np.sum(aleatoric + epistemic))
        disagreement = float(np.sum(epistemic))
        normalized_used = [
            FittedLASMProgram(
                program=item.program,
                regression=item.regression,
                predictive_score=item.predictive_score,
                log_prior=item.log_prior,
                log_weight=item.log_weight,
                posterior_probability=float(weight),
                feature_count=item.feature_count,
                output_count=item.output_count,
            )
            for item, weight in zip(used, probability, strict=True)
        ]
        return LASMPrediction(
            expected_reward=float(mean[0] * 100.0),
            expected_progress=float(mean[1]),
            win_probability=float(np.clip(mean[2], 0.0, 1.0)),
            loss_probability=float(np.clip(mean[3], 0.0, 1.0)),
            change_probability=float(np.clip(mean[4], 0.0, 1.0)),
            expected_change_norm=float(probability @ np.asarray(change_norms)),
            predictive_variance=total_variance,
            model_disagreement=disagreement,
            information_score=float(np.log1p(disagreement + 0.2 * total_variance)),
            family_probabilities=self._aggregate(normalized_used, "family"),
            atlas_probabilities=self._aggregate(normalized_used, "atlas"),
            resolution_probabilities=self._aggregate(normalized_used, "resolution"),
            program_probabilities={item.program.name: item.posterior_probability for item in normalized_used},
        )

    def predict_with_program(
        self,
        program_name: str,
        packets: LASMFramePackets,
        action_features: FloatArray,
        memory: LASMMemory,
        *,
        step_index: int,
    ) -> tuple[FloatArray, FloatArray]:
        item = next((candidate for candidate in self.fitted if candidate.program.name == program_name), None)
        if item is None:
            raise KeyError(program_name)
        row = self._design_action(item, packets, action_features, memory, step_index)
        return item.regression.predict(row)


__all__ = ["FittedLASMProgram", "ProjectorResolvedLargeSignalModel"]
