from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .actions import ActionCandidateGenerator, CandidateConfig
from .memory import TransitionMemory
from .model import BayesianOperatorWorldModel
from .packetizer import FramePacketizer, PacketizerConfig
from .planner import ActionPlanner, PlannerConfig, ProbeOutcome
from .replay import replay_history
from .types import ActionCandidate, ArcObservation, EnvironmentFactory, FramePackets, RunResult


@dataclass(frozen=True)
class AgentConfig:
    maximum_actions: int = 500
    maximum_resets: int = 24
    initial_probe_budget: int = 8
    recurring_probe_budget: int = 2
    probe_interval: int = 4
    refit_interval: int = 3
    stagnation_limit: int = 18
    maximum_candidates: int = 48
    maximum_records: int = 512
    random_seed: int = 0
    strict_replay_check: bool = True
    maximum_seconds: float = 0.0


class OfflineBayesianOperatorAgent:
    """Offline ARC-AGI-3 agent using Bayesian multiresolution operator programs.

    Only observations, public actions, local resets, and local replay are used.
    The agent does not inspect the game source code and cannot make network calls.
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()
        self.packetizer = FramePacketizer(PacketizerConfig())
        self.actions = ActionCandidateGenerator(
            CandidateConfig(maximum_candidates=self.config.maximum_candidates)
        )
        self.memory = TransitionMemory(maximum_records=self.config.maximum_records)
        self.model = BayesianOperatorWorldModel()
        self.planner = ActionPlanner(PlannerConfig())
        self.rng = np.random.default_rng(self.config.random_seed)
        self.state_action_counts: Counter[tuple[str, tuple[object, ...]]] = Counter()
        self.replay_enabled = True
        self.trace: list[dict[str, Any]] = []
        self.posterior_trace: list[dict[str, Any]] = []

    def _probe_candidates(
        self,
        factory: EnvironmentFactory,
        history: Sequence[ActionCandidate],
        observation: ArcObservation,
        packets: FramePackets,
        candidates: Sequence[ActionCandidate],
        budget: int,
        step_index: int,
    ) -> dict[tuple[object, ...], ProbeOutcome]:
        if budget <= 0 or not self.replay_enabled:
            return {}
        subset = self.actions.diverse_subset(
            candidates,
            budget,
            seen_roles=self.memory.recent_roles(),
        )
        outcomes: dict[tuple[object, ...], ProbeOutcome] = {}
        for candidate in subset:
            try:
                replayed = replay_history(
                    factory,
                    history,
                    self.packetizer,
                    expected_signature=packets.signature,
                )
            except Exception as exc:
                self.replay_enabled = False
                self.trace.append({"event": "replay-disabled", "error": repr(exc), "step": step_index})
                break
            if not replayed.matched_signature:
                if self.config.strict_replay_check:
                    self.replay_enabled = False
                    self.trace.append(
                        {
                            "event": "replay-disabled",
                            "reason": "signature-mismatch",
                            "expected": packets.signature,
                            "actual": replayed.packets.signature,
                            "step": step_index,
                        }
                    )
                    break
            after = replayed.environment.step(candidate)
            after_packets = self.packetizer.resolve(after.frame, observation.frame)
            novelty = self.memory.novelty(after_packets.signature)
            reward = self.planner.transition_reward(
                observation,
                after,
                packets,
                after_packets,
                novelty=novelty,
            )
            record = self.memory.make_record(
                before=packets,
                after=after_packets,
                action_features=self.actions.features(candidate),
                candidate=candidate,
                reward=reward,
                level_delta=after.levels_completed - observation.levels_completed,
                terminal_win=after.state.value == "WIN",
                terminal_loss=after.state.value == "GAME_OVER",
                step_index=step_index,
                source="probe",
            )
            self.memory.add(record)
            outcomes[candidate.identity()] = ProbeOutcome(after, after_packets, reward)
        return outcomes

    def _write_progress(self, output_dir: Path, result: RunResult | None = None) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "trace.json").write_text(json.dumps(self.trace, indent=2), encoding="utf-8")
        (output_dir / "posterior_trace.json").write_text(
            json.dumps(self.posterior_trace, indent=2), encoding="utf-8"
        )
        if result is not None:
            (output_dir / "result.json").write_text(
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
            if self.config.maximum_seconds > 0 and (time.perf_counter() - started) >= self.config.maximum_seconds:
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
            if not candidates:
                notes.append("no public actions were available")
                break

            if len(self.memory.records) >= self.model.minimum_records and (
                self.model.fit_count == 0 or committed_actions % self.config.refit_interval == 0
            ):
                self.model.fit(self.memory)
                summary = self.model.posterior_summary()
                summary["step"] = committed_actions
                self.posterior_trace.append(summary)

            if committed_actions == 0 or just_progressed:
                probe_budget = self.config.initial_probe_budget
            elif committed_actions % self.config.probe_interval == 0:
                probe_budget = self.config.recurring_probe_budget
            else:
                probe_budget = 0
            probes = self._probe_candidates(
                factory,
                history,
                observation,
                packets,
                candidates,
                probe_budget,
                committed_actions,
            )
            probe_actions += len(probes)
            if len(self.memory.records) >= self.model.minimum_records and probes:
                self.model.fit(self.memory)
                summary = self.model.posterior_summary()
                summary["step"] = committed_actions
                summary["after_probes"] = True
                self.posterior_trace.append(summary)

            scored = self.planner.score_candidates(
                candidates,
                observation=observation,
                packets=packets,
                memory=self.memory,
                model=self.model,
                action_generator=self.actions,
                step_index=committed_actions,
                probes=probes,
                state_action_counts=self.state_action_counts,
            )
            if not scored:
                notes.append("candidate scoring returned no actions")
                break

            # Exact probes that win or advance a level take precedence.  Otherwise
            # the Bayesian utility score determines the committed action.
            progressing = [
                row
                for row in scored
                if row.exact_probe
                and row.probe_observation is not None
                and (
                    row.probe_observation.state.value == "WIN"
                    or row.probe_observation.levels_completed > observation.levels_completed
                )
            ]
            selected = progressing[0] if progressing else scored[0]
            candidate = selected.candidate
            before_observation, before_packets = observation, packets
            after = environment.step(candidate)
            after_packets = self.packetizer.resolve(after.frame, before_observation.frame)
            novelty = self.memory.novelty(after_packets.signature)
            reward = self.planner.transition_reward(
                before_observation,
                after,
                before_packets,
                after_packets,
                novelty=novelty,
            )
            record = self.memory.make_record(
                before=before_packets,
                after=after_packets,
                action_features=self.actions.features(candidate),
                candidate=candidate,
                reward=reward,
                level_delta=after.levels_completed - before_observation.levels_completed,
                terminal_win=after.state.value == "WIN",
                terminal_loss=after.state.value == "GAME_OVER",
                step_index=committed_actions,
                source="committed",
            )
            self.memory.add(record, after_packets=after_packets)
            committed_actions += 1
            self.state_action_counts[(before_packets.signature, candidate.role)] += 1
            changed = after_packets.signature != before_packets.signature
            progressed = after.levels_completed > before_observation.levels_completed
            stagnation = 0 if changed or progressed else stagnation + 1
            just_progressed = progressed

            trace_row = {
                "step": committed_actions,
                "action_id": candidate.action_id,
                "data": dict(candidate.data),
                "role": [str(value) for value in candidate.role],
                "source": candidate.source,
                "score": selected.total,
                "exact_probe": selected.exact_probe,
                "reward": reward,
                "before_signature": before_packets.signature,
                "after_signature": after_packets.signature,
                "state": after.state.value,
                "levels_completed": after.levels_completed,
                "win_levels": after.win_levels,
                "stagnation": stagnation,
                "model": self.model.posterior_summary(),
            }
            self.trace.append(trace_row)

            if after.state.value == "GAME_OVER":
                # Keep the failed transition as evidence, then reconstruct the
                # previous state without adding the losing action to history.
                resets += 1
                replayed = replay_history(factory, history, self.packetizer)
                environment = replayed.environment
                observation = replayed.observation
                packets = replayed.packets
                stagnation += 2
            else:
                history.append(candidate)
                observation, packets = after, after_packets

            if stagnation >= self.config.stagnation_limit:
                # A fresh deterministic replay removes any hidden animation or
                # wrapper state while preserving the action history.
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
