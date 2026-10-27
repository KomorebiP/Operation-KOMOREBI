from __future__ import annotations

from dataclasses import dataclass, field
from math import log
from typing import Mapping, Sequence

import numpy as np
from scipy.special import logsumexp

from .bayes import BayesianRegression, FittedBayesianRegression, normalized_probabilities
from .memory import TransitionMemory
from .operator_programs import OperatorProgram, default_operator_programs
from .types import ActionCandidate, FloatArray, FramePackets, Prediction, TransitionRecord


@dataclass(frozen=True)
class FittedProgram:
    program: OperatorProgram
    regression: FittedBayesianRegression
    log_prior: float
    predictive_score: float
    log_weight: float
    posterior_probability: float
    feature_count: int
    output_count: int


@dataclass(frozen=True)
class ActionModelPrediction:
    expected_reward: float
    expected_progress: float
    win_probability: float
    loss_probability: float
    change_probability: float
    expected_change_norm: float
    predictive_variance: float
    model_disagreement: float
    information_score: float
    family_probabilities: Mapping[str, float]
    resolution_probabilities: Mapping[str, float]


@dataclass
class BayesianOperatorWorldModel:
    programs: Sequence[OperatorProgram] = field(default_factory=default_operator_programs)
    regression: BayesianRegression = field(default_factory=BayesianRegression)
    complexity_penalty: float = 0.0025
    mechanism_penalty: float = 1.2
    fine_resolution_penalty: float = 0.25
    validation_fraction: float = 0.25
    minimum_records: int = 8
    maximum_fit_records: int = 384
    fitted: tuple[FittedProgram, ...] = ()
    fit_count: int = 0

    def _fit_program(self, program: OperatorProgram, records: Sequence[TransitionRecord]) -> tuple[FittedBayesianRegression, float, float, int, int]:
        design = np.vstack([program.design_record(record) for record in records])
        targets = np.vstack([program.targets(record) for record in records])
        n = design.shape[0]
        split = max(5, int(round((1.0 - self.validation_fraction) * n)))
        split = min(split, n - 2)
        if split < 3:
            split = n
        model = self.regression.fit(design[:split], targets[:split])
        if split < n:
            predictive = model.predictive_log_likelihood(design[split:], targets[split:])
        else:
            predictive = model.log_evidence
        complexity = program.complexity(design.shape[1], targets.shape[1])
        log_prior = (
            -self.complexity_penalty * complexity
            -self.mechanism_penalty * program.mechanism_count
            -self.fine_resolution_penalty * float(program.resolution == "fine")
        )
        return model, float(predictive), float(log_prior), design.shape[1], targets.shape[1]

    def fit(self, memory: TransitionMemory) -> tuple[FittedProgram, ...]:
        records = memory.records[-self.maximum_fit_records :]
        if len(records) < self.minimum_records:
            self.fitted = ()
            return self.fitted
        provisional: list[tuple[OperatorProgram, FittedBayesianRegression, float, float, float, int, int]] = []
        for program in self.programs:
            try:
                model, predictive, log_prior, feature_count, output_count = self._fit_program(program, records)
            except (np.linalg.LinAlgError, ValueError, FloatingPointError):
                continue
            log_weight = predictive + log_prior
            provisional.append((program, model, predictive, log_prior, log_weight, feature_count, output_count))
        if not provisional:
            self.fitted = ()
            return self.fitted
        probabilities = normalized_probabilities(np.asarray([row[4] for row in provisional], dtype=float))
        completed = []
        for row, probability in zip(provisional, probabilities):
            program, model, predictive, log_prior, log_weight, feature_count, output_count = row
            completed.append(
                FittedProgram(
                    program=program,
                    regression=model,
                    log_prior=log_prior,
                    predictive_score=predictive,
                    log_weight=log_weight,
                    posterior_probability=float(probability),
                    feature_count=feature_count,
                    output_count=output_count,
                )
            )
        self.fitted = tuple(sorted(completed, key=lambda item: item.posterior_probability, reverse=True))
        self.fit_count += 1
        return self.fitted

    def posterior_summary(self) -> dict[str, object]:
        families: dict[str, float] = {}
        resolutions: dict[str, float] = {}
        for item in self.fitted:
            families[item.program.family] = families.get(item.program.family, 0.0) + item.posterior_probability
            resolutions[item.program.resolution] = resolutions.get(item.program.resolution, 0.0) + item.posterior_probability
        entropy = -sum(p * log(max(p, 1e-15)) for p in families.values())
        return {
            "best_program": None if not self.fitted else self.fitted[0].program.name,
            "best_probability": 0.0 if not self.fitted else self.fitted[0].posterior_probability,
            "family_probabilities": families,
            "resolution_probabilities": resolutions,
            "family_entropy": float(entropy),
            "fit_count": self.fit_count,
        }

    def _program_row(
        self,
        item: FittedProgram,
        packets: FramePackets,
        action_features: FloatArray,
        memory: TransitionMemory,
        step_index: int,
    ) -> FloatArray:
        resolution = item.program.resolution
        previous, power, exponential = memory.context(resolution)
        return item.program.design_row(
            state=packets.state(resolution),
            action_features=action_features,
            step_index=step_index,
            previous=previous,
            power_memory=power,
            exponential_memory=exponential,
        )

    def predict_action(
        self,
        packets: FramePackets,
        action_features: FloatArray,
        memory: TransitionMemory,
        *,
        step_index: int,
    ) -> ActionModelPrediction:
        if not self.fitted:
            return ActionModelPrediction(
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
                resolution_probabilities={},
            )

        scalar_predictions: list[np.ndarray] = []
        scalar_variances: list[np.ndarray] = []
        change_norms: list[float] = []
        weights: list[float] = []
        family_probabilities: dict[str, float] = {}
        resolution_probabilities: dict[str, float] = {}

        for item in self.fitted:
            row = self._program_row(item, packets, action_features, memory, step_index)
            if row.size != item.feature_count:
                continue
            mean, variance = item.regression.predict(row)
            mean_row = mean[0]
            variance_row = variance[0]
            state_dimension = packets.state(item.program.resolution).size
            delta = mean_row[:state_dimension]
            scalars = mean_row[state_dimension : state_dimension + 5]
            scalar_var = variance_row[state_dimension : state_dimension + 5]
            if scalars.size < 5:
                continue
            scalar_predictions.append(scalars)
            scalar_variances.append(scalar_var)
            change_norms.append(float(np.linalg.norm(delta)))
            weights.append(item.posterior_probability)
            family_probabilities[item.program.family] = family_probabilities.get(item.program.family, 0.0) + item.posterior_probability
            resolution_probabilities[item.program.resolution] = resolution_probabilities.get(item.program.resolution, 0.0) + item.posterior_probability

        if not weights:
            return ActionModelPrediction(0.0, 0.0, 0.0, 0.0, 0.5, 0.25, 1.0, 1.0, 1.0, {}, {})
        probability = np.asarray(weights, dtype=float)
        probability /= probability.sum()
        scalar_matrix = np.vstack(scalar_predictions)
        variance_matrix = np.vstack(scalar_variances)
        mean_scalars = probability @ scalar_matrix
        aleatoric = probability @ variance_matrix
        epistemic = probability @ ((scalar_matrix - mean_scalars[None, :]) ** 2)
        total_variance = aleatoric + epistemic
        disagreement = float(np.sum(epistemic))
        predictive_variance = float(np.sum(total_variance))
        information_score = float(np.log1p(disagreement + 0.2 * predictive_variance))
        expected_change = float(probability @ np.asarray(change_norms, dtype=float))

        reward = float(mean_scalars[0] * 100.0)
        progress = float(mean_scalars[1])
        win = float(np.clip(mean_scalars[2], 0.0, 1.0))
        loss = float(np.clip(mean_scalars[3], 0.0, 1.0))
        change = float(np.clip(mean_scalars[4], 0.0, 1.0))
        return ActionModelPrediction(
            expected_reward=reward,
            expected_progress=progress,
            win_probability=win,
            loss_probability=loss,
            change_probability=change,
            expected_change_norm=expected_change,
            predictive_variance=predictive_variance,
            model_disagreement=disagreement,
            information_score=information_score,
            family_probabilities=family_probabilities,
            resolution_probabilities=resolution_probabilities,
        )
