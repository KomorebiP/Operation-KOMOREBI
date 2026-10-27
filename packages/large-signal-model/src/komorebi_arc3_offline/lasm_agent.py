from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from .actions import ActionCandidateGenerator, CandidateConfig
from .lasm_graph import ActionIdentity, StateTransitionGraph
from .lasm_memory import LASMMemory
from .lasm_model import ProjectorResolvedLargeSignalModel
from .lasm_packetizer import LASMPacketizerConfig, UltimateLASMPacketizer
from .lasm_types import LASMFramePackets
from .replay import replay_history
from .types import ActionCandidate, ArcObservation, EnvironmentFactory, RunResult


@dataclass(frozen=True)
class UltimateAgentConfig:
    maximum_actions: int = 1200
    maximum_seconds: float = 0.0
    maximum_resets: int = 160
    initial_probe_budget: int = 14
    recurring_probe_budget: int = 6
    probe_interval: int = 3
    refit_interval: int = 3
    stagnation_limit: int = 24
    maximum_candidates: int = 64
    minimum_model_records: int = 10
    graph_frontier_bonus: float = 28.0
    graph_known_progress_bonus: float = 800.0
    graph_known_win_bonus: float = 4000.0
    novelty_weight: float = 12.0
    information_weight: float = 6.0
    uncertainty_weight: float = 0.08
    role_weight: float = 0.08
    loop_weight: float = 5.0
    loss_weight: float = 900.0


@dataclass(frozen=True)
class LASMProbeOutcome:
    observation: ArcObservation
    packets: LASMFramePackets
    reward: float


class UltimateLargeSignalAgent:
    """PR-LASM world model plus exact replay graph and active planning."""

    def __init__(
        self,
        config: UltimateAgentConfig | None = None,
        *,
        packetizer: UltimateLASMPacketizer | None = None,
        model: ProjectorResolvedLargeSignalModel | None = None,
    ) -> None:
        self.config = config or UltimateAgentConfig()
        self.packetizer = packetizer or UltimateLASMPacketizer(LASMPacketizerConfig())
        self.model = model or ProjectorResolvedLargeSignalModel(
            minimum_records=self.config.minimum_model_records
        )
        self.actions = ActionCandidateGenerator(
            CandidateConfig(maximum_candidates=self.config.maximum_candidates)
        )
        self.memory = LASMMemory()
        self.graph = StateTransitionGraph()
        self.state_action_counts: Counter[tuple[str, tuple[object, ...]]] = Counter()
        self.trace: list[dict[str, object]] = []
        self.posterior_trace: list[dict[str, object]] = []
        self.replay_valid = True

    @staticmethod
    def transition_reward(
        before: ArcObservation,
        after: ArcObservation,
        before_packets: LASMFramePackets,
        after_packets: LASMFramePackets,
        *,
        novelty: float,
    ) -> float:
        progress = after.levels_completed - before.levels_completed
        reward = 260.0 * progress
        reward += 1400.0 * float(after.state.value == "WIN")
        reward -= 850.0 * float(after.state.value == "GAME_OVER")
        reward += 5.0 * float(before_packets.signature != after_packets.signature)
        reward += 5.0 * novelty
        reward += 2.5 * after_packets.change_fraction
        reward -= 0.05
        return float(reward)

    @staticmethod
    def _identity_lookup(
        candidates: Sequence[ActionCandidate], identity: ActionIdentity
    ) -> ActionCandidate | None:
        return next((candidate for candidate in candidates if candidate.identity() == identity), None)

    def _probe_candidates(
        self,
        factory: EnvironmentFactory,
        history: Sequence[ActionCandidate],
        observation: ArcObservation,
        packets: LASMFramePackets,
        candidates: Sequence[ActionCandidate],
        budget: int,
        step_index: int,
    ) -> dict[tuple[object, ...], LASMProbeOutcome]:
        if budget <= 0 or not self.replay_valid:
            return {}
        untried = self.graph.untried_actions(packets.signature, candidates)
        ordered = self.actions.diverse_subset(
            untried or candidates,
            budget,
            seen_roles=self.memory.role_statistics.keys(),
        )
        outcomes: dict[tuple[object, ...], LASMProbeOutcome] = {}
        for candidate in ordered:
            replayed = replay_history(
                factory,
                history,
                self.packetizer,
                expected_signature=packets.signature,
            )
            if not replayed.matched_signature:
                self.replay_valid = False
                self.trace.append(
                    {
                        "event": "replay-disabled",
                        "step": step_index,
                        "expected": packets.signature,
                        "actual": replayed.packets.signature,
                    }
                )
                break
            after = replayed.environment.step(candidate)
            after_packets = self.packetizer.resolve(after.frame, observation.frame)
            novelty = self.memory.novelty(after_packets.signature)
            reward = self.transition_reward(
                observation,
                after,
                packets,
                after_packets,
                novelty=novelty,
            )
            transition = self.memory.make_transition(
                before=packets,
                after=after_packets,
                action=candidate,
                action_features=self.actions.features(candidate),
                reward=reward,
                level_delta=after.levels_completed - observation.levels_completed,
                terminal_win=after.state.value == "WIN",
                terminal_loss=after.state.value == "GAME_OVER",
                step_index=step_index,
            )
            self.memory.add(transition)
            self.graph.record(
                packets.signature,
                candidate,
                after_packets.signature,
                reward=reward,
                level_delta=transition.level_delta,
                terminal_win=transition.terminal_win,
                terminal_loss=transition.terminal_loss,
            )
            outcomes[candidate.identity()] = LASMProbeOutcome(after, after_packets, reward)
        return outcomes

    def _score(
        self,
        candidate: ActionCandidate,
        *,
        observation: ArcObservation,
        packets: LASMFramePackets,
        probes: Mapping[tuple[object, ...], LASMProbeOutcome],
        step_index: int,
    ) -> tuple[float, dict[str, float | bool]]:
        prediction = self.model.predict_action(
            packets,
            self.actions.features(candidate),
            self.memory,
            step_index=step_index,
        )
        exact = probes.get(candidate.identity())
        known = self.graph.known_outcome(packets.signature, candidate)
        if exact is not None:
            predicted_reward = exact.reward
            progress = float(exact.observation.levels_completed - observation.levels_completed)
            win = float(exact.observation.state.value == "WIN")
            loss = float(exact.observation.state.value == "GAME_OVER")
            novelty = self.memory.novelty(exact.packets.signature)
            uncertainty = 0.0
            exact_probe = True
        elif known is not None:
            predicted_reward = known.mean_reward
            progress = known.mean_progress
            win = float(known.wins > 0)
            loss = float(known.losses > 0)
            novelty = self.memory.novelty(known.target)
            uncertainty = 0.05
            exact_probe = False
        else:
            predicted_reward = prediction.expected_reward
            progress = prediction.expected_progress
            win = prediction.win_probability
            loss = prediction.loss_probability
            novelty = prediction.change_probability * min(
                1.0, prediction.expected_change_norm + 0.2
            )
            uncertainty = prediction.predictive_variance
            exact_probe = False

        repeats = self.state_action_counts[(packets.signature, candidate.role)]
        loop_penalty = self.config.loop_weight * repeats * repeats
        untried = known is None and exact is None
        total = (
            predicted_reward
            + 220.0 * progress
            + 1100.0 * win
            - self.config.loss_weight * loss
            + self.config.novelty_weight * novelty
            + self.config.information_weight * prediction.information_score
            - self.config.uncertainty_weight * uncertainty
            + self.config.role_weight * self.memory.role_score(candidate.role)
            - loop_penalty
            + self.config.graph_frontier_bonus * float(untried)
        )
        if known is not None:
            total += self.config.graph_known_progress_bonus * float(known.mean_progress > 0)
            total += self.config.graph_known_win_bonus * float(known.wins > 0)
        if exact is not None:
            total += 1200.0 * float(progress > 0)
            total += 6000.0 * float(win > 0)
        return float(total), {
            "predicted_reward": float(predicted_reward),
            "progress": float(progress),
            "win": float(win),
            "loss": float(loss),
            "novelty": float(novelty),
            "uncertainty": float(uncertainty),
            "exact_probe": exact_probe,
            "known_graph_edge": known is not None,
            "untried": untried,
            "loop_penalty": float(loop_penalty),
        }

    def _write_progress(self, output: Path, result: RunResult | None = None) -> None:
        output.mkdir(parents=True, exist_ok=True)
        (output / "trace.json").write_text(json.dumps(self.trace, indent=2), encoding="utf-8")
        (output / "posterior_trace.json").write_text(
            json.dumps(self.posterior_trace, indent=2), encoding="utf-8"
        )
        (output / "graph_summary.json").write_text(
            json.dumps(self.graph.summary(), indent=2), encoding="utf-8"
        )
        if result is not None:
            (output / "result.json").write_text(
                json.dumps(asdict(result), indent=2), encoding="utf-8"
            )

    def solve(self, factory: EnvironmentFactory, output_dir: str | Path) -> RunResult:
        output = Path(output_dir).expanduser().resolve()
        started = time.perf_counter()
        environment = factory.create()
        observation = environment.reset()
        packets = self.packetizer.resolve(observation.frame)
        self.memory.initialize(packets)
        history: list[ActionCandidate] = []
        committed_actions = 0
        probe_actions = 0
        resets = 1
        stagnation = 0
        just_progressed = False
        notes: list[str] = []

        while committed_actions < self.config.maximum_actions:
            if self.config.maximum_seconds > 0 and time.perf_counter() - started >= self.config.maximum_seconds:
                notes.append("maximum wall-clock budget reached")
                break
            if observation.state.value == "WIN":
                break
            if resets > self.config.maximum_resets:
                notes.append("maximum reset budget reached")
                break

            candidates = self.actions.generate(
                observation,
                packets,
                action_space=getattr(environment, "action_space", ()),
            )
            self.graph.register_state(packets.signature, candidates)
            if not candidates:
                notes.append("no public actions")
                break

            if len(self.memory.records) >= self.model.minimum_records and (
                self.model.fit_count == 0
                or committed_actions % self.config.refit_interval == 0
            ):
                self.model.fit(self.memory)
                posterior = self.model.posterior_summary()
                posterior["step"] = committed_actions
                self.posterior_trace.append(posterior)

            if committed_actions == 0 or just_progressed:
                budget = self.config.initial_probe_budget
            elif committed_actions % self.config.probe_interval == 0:
                budget = self.config.recurring_probe_budget
            else:
                budget = 0
            probes = self._probe_candidates(
                factory,
                history,
                observation,
                packets,
                candidates,
                budget,
                committed_actions,
            )
            probe_actions += len(probes)
            if probes and len(self.memory.records) >= self.model.minimum_records:
                self.model.fit(self.memory)
                posterior = self.model.posterior_summary()
                posterior.update({"step": committed_actions, "after_probes": True})
                self.posterior_trace.append(posterior)

            scored = [
                (candidate, *self._score(
                    candidate,
                    observation=observation,
                    packets=packets,
                    probes=probes,
                    step_index=committed_actions,
                ))
                for candidate in candidates
            ]
            scored.sort(key=lambda row: row[1], reverse=True)
            candidate, score, detail = scored[0]

            before_observation, before_packets = observation, packets
            after = environment.step(candidate)
            after_packets = self.packetizer.resolve(after.frame, before_observation.frame)
            reward = self.transition_reward(
                before_observation,
                after,
                before_packets,
                after_packets,
                novelty=self.memory.novelty(after_packets.signature),
            )
            transition = self.memory.make_transition(
                before=before_packets,
                after=after_packets,
                action=candidate,
                action_features=self.actions.features(candidate),
                reward=reward,
                level_delta=after.levels_completed - before_observation.levels_completed,
                terminal_win=after.state.value == "WIN",
                terminal_loss=after.state.value == "GAME_OVER",
                step_index=committed_actions,
            )
            self.memory.add(transition, after_packets=after_packets)
            self.graph.record(
                before_packets.signature,
                candidate,
                after_packets.signature,
                reward=reward,
                level_delta=transition.level_delta,
                terminal_win=transition.terminal_win,
                terminal_loss=transition.terminal_loss,
            )
            self.state_action_counts[(before_packets.signature, candidate.role)] += 1
            committed_actions += 1
            changed = before_packets.signature != after_packets.signature
            progressed = transition.level_delta > 0
            stagnation = 0 if changed or progressed else stagnation + 1
            just_progressed = progressed

            self.trace.append(
                {
                    "step": committed_actions,
                    "action_id": candidate.action_id,
                    "data": dict(candidate.data),
                    "role": [str(value) for value in candidate.role],
                    "score": score,
                    "score_detail": detail,
                    "reward": reward,
                    "before_signature": before_packets.signature,
                    "after_signature": after_packets.signature,
                    "state": after.state.value,
                    "levels_completed": after.levels_completed,
                    "win_levels": after.win_levels,
                    "stagnation": stagnation,
                    "posterior": self.model.posterior_summary(),
                    "graph": self.graph.summary(),
                    "reconstruction_residual_max": max(after_packets.reconstruction_residuals.values()),
                }
            )

            if after.state.value == "GAME_OVER":
                resets += 1
                replayed = replay_history(factory, history, self.packetizer)
                environment = replayed.environment
                observation = replayed.observation
                packets = replayed.packets
                stagnation += 2
            else:
                history.append(candidate)
                observation, packets = after, after_packets

            if stagnation >= self.config.stagnation_limit and self.replay_valid:
                resets += 1
                replayed = replay_history(factory, history, self.packetizer)
                environment = replayed.environment
                observation = replayed.observation
                packets = replayed.packets
                stagnation = 0
                notes.append(f"stagnation replay at action {committed_actions}")

            if committed_actions % 10 == 0:
                self._write_progress(output)

        elapsed = time.perf_counter() - started
        result = RunResult(
            game_id=factory.game_id,
            solved=observation.state.value == "WIN",
            final_state=observation.state.value,
            levels_completed=observation.levels_completed,
            win_levels=observation.win_levels,
            committed_actions=committed_actions,
            probe_actions=probe_actions,
            resets=resets,
            elapsed_seconds=float(elapsed),
            model_updates=self.model.fit_count,
            output_dir=str(output),
            notes=tuple(notes),
        )
        self._write_progress(output, result)
        return result


__all__ = ["UltimateAgentConfig", "UltimateLargeSignalAgent"]
