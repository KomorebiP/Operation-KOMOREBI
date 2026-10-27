from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from .actions import ActionCandidateGenerator
from .memory import TransitionMemory
from .model import ActionModelPrediction, BayesianOperatorWorldModel
from .types import ActionCandidate, ActionScore, ArcObservation, FramePackets


@dataclass(frozen=True)
class PlannerConfig:
    reward_weight: float = 1.0
    progress_weight: float = 180.0
    win_weight: float = 900.0
    loss_weight: float = 650.0
    novelty_weight: float = 8.0
    information_weight: float = 4.0
    uncertainty_weight: float = 0.12
    loop_weight: float = 3.0
    role_weight: float = 0.08


@dataclass(frozen=True)
class ProbeOutcome:
    observation: ArcObservation
    packets: FramePackets
    reward: float


class ActionPlanner:
    def __init__(self, config: PlannerConfig | None = None) -> None:
        self.config = config or PlannerConfig()

    @staticmethod
    def transition_reward(
        before: ArcObservation,
        after: ArcObservation,
        before_packets: FramePackets,
        after_packets: FramePackets,
        *,
        novelty: float,
    ) -> float:
        level_delta = after.levels_completed - before.levels_completed
        reward = 220.0 * level_delta
        reward += 1000.0 * float(after.state.value == "WIN")
        reward -= 600.0 * float(after.state.value == "GAME_OVER")
        reward += 4.0 * float(before_packets.signature != after_packets.signature)
        reward += 4.0 * float(novelty)
        reward += 2.0 * float(after_packets.change_fraction)
        reward -= 0.05
        return float(reward)

    def score_candidates(
        self,
        candidates: Sequence[ActionCandidate],
        *,
        observation: ArcObservation,
        packets: FramePackets,
        memory: TransitionMemory,
        model: BayesianOperatorWorldModel,
        action_generator: ActionCandidateGenerator,
        step_index: int,
        probes: Mapping[tuple[object, ...], ProbeOutcome] | None = None,
        state_action_counts: Mapping[tuple[str, tuple[object, ...]], int] | None = None,
    ) -> list[ActionScore]:
        probes = probes or {}
        state_action_counts = state_action_counts or {}
        rows: list[ActionScore] = []
        for candidate in candidates:
            prediction = model.predict_action(
                packets,
                action_generator.features(candidate),
                memory,
                step_index=step_index,
            )
            exact = probes.get(candidate.identity())
            if exact is not None:
                predicted_reward = exact.reward
                progress = float(exact.observation.levels_completed - observation.levels_completed)
                novelty = memory.novelty(exact.packets.signature)
                information = prediction.information_score
                loss_risk = float(exact.observation.state.value == "GAME_OVER")
                uncertainty = 0.0
            else:
                predicted_reward = prediction.expected_reward
                progress = prediction.expected_progress
                novelty = prediction.change_probability * min(1.0, prediction.expected_change_norm + 0.25)
                information = prediction.information_score
                loss_risk = prediction.loss_probability
                uncertainty = prediction.predictive_variance

            repeats = int(state_action_counts.get((packets.signature, candidate.role), 0))
            loop_penalty = self.config.loop_weight * repeats * repeats
            role_prior = memory.role_score(candidate.role)
            total = (
                self.config.reward_weight * predicted_reward
                + self.config.progress_weight * progress
                + self.config.win_weight * prediction.win_probability
                - self.config.loss_weight * loss_risk
                + self.config.novelty_weight * novelty
                + self.config.information_weight * information
                - self.config.uncertainty_weight * uncertainty
                - loop_penalty
                + self.config.role_weight * role_prior
            )
            rows.append(
                ActionScore(
                    candidate=candidate,
                    predicted_reward=float(predicted_reward),
                    progress_score=float(progress),
                    novelty_score=float(novelty),
                    information_score=float(information),
                    uncertainty_penalty=float(uncertainty),
                    loop_penalty=float(loop_penalty),
                    loss_risk=float(loss_risk),
                    total=float(total),
                    exact_probe=exact is not None,
                    probe_observation=None if exact is None else exact.observation,
                    probe_packets=None if exact is None else exact.packets,
                )
            )
        return sorted(rows, key=lambda row: row.total, reverse=True)
