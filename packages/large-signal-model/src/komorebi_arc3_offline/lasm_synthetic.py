from __future__ import annotations

"""Deterministic synthetic systems for PR-LASM verification and ablation."""

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .actions import ActionCandidateGenerator
from .lasm_memory import LASMMemory
from .lasm_packetizer import UltimateLASMPacketizer
from .lasm_types import LASMTransition
from .types import ActionCandidate, FloatArray


@dataclass(frozen=True)
class SyntheticScenario:
    name: str
    expected_family: str
    expected_atlas: str
    transitions: tuple[LASMTransition, ...]


def _basis_images(size: int = 64, latent_dimension: int = 8) -> FloatArray:
    y, x = np.mgrid[0:size, 0:size]
    basis = [
        np.sin(2 * np.pi * x / size),
        np.cos(4 * np.pi * y / size),
        np.sin(2 * np.pi * (x + y) / size),
        np.where(x < size // 2, 1.0, -1.0),
        np.where(y < size // 2, 1.0, -1.0),
        np.where((x // 8 + y // 8) % 2 == 0, 1.0, -1.0),
        np.where((x % 4 == 0) & (y % 4 == 0), 1.0, -0.15),
        np.exp(-((x - 44.0) ** 2 + (y - 20.0) ** 2) / 110.0) * 2.0 - 0.25,
    ]
    return np.asarray(basis[:latent_dimension], dtype=np.float64)


def _render_latent(latent: FloatArray, basis: FloatArray) -> np.ndarray:
    field = np.tensordot(latent, basis, axes=(0, 0))
    field = 7.0 + 1.6 * field / max(1.0, float(np.std(field)))
    return np.clip(np.rint(field), 0, 15).astype(np.int16)


def _action_vector(action_id: int, latent_dimension: int) -> FloatArray:
    rng = np.random.default_rng(9000 + action_id)
    vector = rng.normal(scale=0.18, size=latent_dimension)
    vector[action_id % latent_dimension] += 0.45
    return vector


def generate_scenario(
    name: str,
    *,
    steps: int = 84,
    seed: int = 0,
    packetizer: UltimateLASMPacketizer | None = None,
) -> SyntheticScenario:
    packetizer = packetizer or UltimateLASMPacketizer()
    generator = ActionCandidateGenerator()
    rng = np.random.default_rng(seed + sum(ord(char) for char in name))
    latent_dimension = 8
    basis = _basis_images(latent_dimension=latent_dimension)
    latent = rng.normal(scale=0.45, size=latent_dimension)
    previous_latent = latent.copy()
    power_state = latent.copy()
    exponential_state = latent.copy()
    memory = LASMMemory(maximum_records=steps + 4)
    first_frame = _render_latent(latent, basis)
    first_packets = packetizer.resolve(first_frame)
    memory.initialize(first_packets)
    previous_frame = first_frame
    before_packets = first_packets
    transitions: list[LASMTransition] = []

    expected = {
        "linear-fourier": ("linear", "fourier"),
        "quadratic-spatial": ("quadratic", "spatial"),
        "delay-portfolio": ("delay", "portfolio"),
        "fractional-fourier": ("fractional", "fourier"),
        "volterra-portfolio": ("volterra", "portfolio"),
        "phase2-polyphase": ("phase", "polyphase2"),
        "gated-color": ("gated", "color"),
    }
    if name not in expected:
        raise KeyError(name)

    for step in range(steps):
        action_id = 1 + int(rng.integers(0, 4))
        action = ActionCandidate(action_id, role=("synthetic", action_id))
        forcing = _action_vector(action_id, latent_dimension)
        noise = rng.normal(scale=0.008, size=latent_dimension)
        if name == "linear-fourier":
            next_latent = 0.78 * latent + forcing + noise
        elif name == "quadratic-spatial":
            next_latent = 0.46 * latent + 0.24 * (latent * latent - 0.25) + forcing + noise
        elif name == "delay-portfolio":
            next_latent = 0.46 * latent + 0.36 * previous_latent + forcing + noise
        elif name == "fractional-fourier":
            next_latent = 0.43 * latent + 0.39 * power_state + forcing + noise
        elif name == "volterra-portfolio":
            next_latent = 0.44 * latent + 0.38 * exponential_state + forcing + noise
        elif name == "phase2-polyphase":
            phase = 1.0 if step % 2 == 0 else -1.0
            next_latent = 0.58 * latent + phase * forcing + noise
        else:  # gated-color
            matrix_scale = 0.78 if latent[0] >= 0 else 0.28
            next_latent = matrix_scale * latent + (1.25 - matrix_scale) * forcing + noise

        next_latent = np.clip(next_latent, -2.2, 2.2)
        next_frame = _render_latent(next_latent, basis)
        after_packets = packetizer.resolve(next_frame, previous_frame)
        transition = memory.make_transition(
            before=before_packets,
            after=after_packets,
            action=action,
            action_features=generator.features(action),
            reward=float(np.linalg.norm(next_latent - latent)),
            level_delta=0,
            terminal_win=False,
            terminal_loss=False,
            step_index=step,
        )
        transitions.append(transition)
        memory.add(transition, after_packets=after_packets)

        previous_latent, latent = latent, next_latent
        power_state = 0.72 * power_state + 0.28 * previous_latent
        exponential_state = 0.82 * exponential_state + 0.18 * previous_latent
        previous_frame = next_frame
        before_packets = after_packets

    family, atlas = expected[name]
    return SyntheticScenario(name, family, atlas, tuple(transitions))


def generate_all_scenarios(
    *, steps: int = 84, seed: int = 0, packetizer: UltimateLASMPacketizer | None = None
) -> tuple[SyntheticScenario, ...]:
    shared = packetizer or UltimateLASMPacketizer()
    names = (
        "linear-fourier",
        "quadratic-spatial",
        "delay-portfolio",
        "fractional-fourier",
        "volterra-portfolio",
        "phase2-polyphase",
        "gated-color",
    )
    return tuple(
        generate_scenario(name, steps=steps, seed=seed + index * 17, packetizer=shared)
        for index, name in enumerate(names)
    )


__all__ = ["SyntheticScenario", "generate_all_scenarios", "generate_scenario"]


def _algebraic_packets(
    state: FloatArray,
    feature_groups: dict[str, FloatArray],
    signature: str,
    analysis,
) -> "LASMFramePackets":
    from .lasm_types import LASMFramePackets

    macro = np.zeros(48, dtype=float)
    macro[: min(48, state.size)] = state[:48]
    meso = np.zeros(96, dtype=float)
    meso[:48] = macro
    micro = np.zeros(192, dtype=float)
    micro[:96] = meso
    raw = np.concatenate([macro] + [feature_groups[name] for name in sorted(feature_groups)])
    return LASMFramePackets(
        macro=macro,
        meso=meso,
        micro=micro,
        raw=raw,
        feature_groups=feature_groups,
        analysis=analysis,
        signature=signature,
        background=0,
        components=(),
        salient_points=((32, 32, "center"),),
        change_fraction=1.0,
        non_background_fraction=0.5,
        reconstruction_residuals={
            "spatial": 0.0,
            "fourier": 0.0,
            "haar": 0.0,
            "polyphase2": 0.0,
            "polyphase4": 0.0,
            "color": 0.0,
        },
    )


def generate_program_identification_scenario(
    name: str,
    *,
    steps: int = 120,
    seed: int = 0,
) -> SyntheticScenario:
    """Generate independent finite records isolating one typed mechanism.

    Each record uses a fresh state, atlas driver, lag, and memory vector.  The
    target depends on features that are absent from all simpler candidate
    programs.  This makes the test a genuine mechanism-identification problem
    rather than a time-series memorization problem.
    """
    from hashlib import blake2b

    from .exact_atlas import MultiAtlasAnalyzer
    from .lasm_programs import LASMProgram
    from .lasm_types import LASMTransition

    expected = {
        "linear-fourier": ("linear", "fourier"),
        "quadratic-spatial": ("quadratic", "spatial"),
        "delay-portfolio": ("delay", "portfolio"),
        "fractional-fourier": ("fractional", "fourier"),
        "volterra-portfolio": ("volterra", "portfolio"),
        "phase2-polyphase": ("phase", "polyphase2"),
        "gated-color": ("gated", "color"),
    }
    if name not in expected:
        raise KeyError(name)
    family, atlas = expected[name]
    phase_modulus = 2 if family == "phase" else 1
    expected_program = LASMProgram(
        name=name,
        family=family,
        resolution="macro",
        atlas=atlas,
        state_rank=12,
        atlas_rank=24,
        interaction_rank=6,
        phase_modulus=phase_modulus,
    )
    linear_same_atlas = LASMProgram(
        name=f"linear-{atlas}",
        family="linear",
        resolution="macro",
        atlas=atlas,
        state_rank=12,
        atlas_rank=24,
        interaction_rank=6,
    )
    rng = np.random.default_rng(seed + sum(ord(char) for char in name))
    dummy_analysis = MultiAtlasAnalyzer().analyze(np.zeros((64, 64), dtype=np.int16))
    action_generator = ActionCandidateGenerator()
    groups_order = ("spatial", "color", "fourier", "haar", "polyphase2", "polyphase4")

    def signature(index: int, values: FloatArray, suffix: bytes) -> str:
        digest = blake2b(digest_size=12, person=b"LASM-algebra")
        digest.update(str(index).encode())
        digest.update(suffix)
        digest.update(np.asarray(values, dtype="<f8").tobytes())
        return digest.hexdigest()

    coefficient: np.ndarray | None = None
    extra_start = 0
    transitions: list[LASMTransition] = []
    for step in range(steps):
        state = rng.normal(scale=0.55, size=12)
        previous = rng.normal(scale=0.65, size=48)
        power = rng.normal(scale=0.65, size=48)
        exponential = rng.normal(scale=0.65, size=48)
        groups = {group: rng.normal(scale=0.75, size=32) for group in groups_order}
        # The intended atlas has a structured driver whose coordinates are not
        # copied into the other atlas groups.
        driver = rng.normal(scale=0.9, size=32)
        intended_group = atlas if atlas != "portfolio" else "color"
        groups[intended_group] = driver
        before = _algebraic_packets(
            state,
            groups,
            signature(step, state, b"before"),
            dummy_analysis,
        )
        action_id = 1 + int(rng.integers(0, 4))
        action = ActionCandidate(action_id, role=("algebraic", action_id))
        action_features = action_generator.features(action)
        expected_row = expected_program.design_row(
            before,
            action_features,
            step_index=step,
            previous=previous,
            power_memory=power,
            exponential_memory=exponential,
        )
        linear_row = linear_same_atlas.design_row(
            before,
            action_features,
            step_index=step,
            previous=previous,
            power_memory=power,
            exponential_memory=exponential,
        )
        if coefficient is None:
            extra_start = linear_row.size if family != "linear" else 1 + 12
            coefficient = np.zeros((12, expected_row.size), dtype=float)
            # Mild shared damping keeps output scale controlled.
            coefficient[:, 1 : 1 + 12] = -0.08 * np.eye(12)
            available = np.arange(extra_start, expected_row.size)
            if available.size == 0:
                available = np.arange(1 + 12, 1 + 12 + 24)
            for output in range(12):
                chosen = rng.choice(available, size=min(8, available.size), replace=False)
                coefficient[output, chosen] = rng.normal(scale=0.12, size=chosen.size)
        assert coefficient is not None
        delta = coefficient @ expected_row + rng.normal(scale=0.002, size=12)
        next_state = np.clip(state + delta, -4.0, 4.0)
        after_groups = {group: rng.normal(scale=0.75, size=32) for group in groups_order}
        after = _algebraic_packets(
            next_state,
            after_groups,
            signature(step, next_state, b"after"),
            dummy_analysis,
        )
        transitions.append(
            LASMTransition(
                before=before,
                after=after,
                action=action,
                action_features=action_features,
                reward=float(np.linalg.norm(delta)),
                level_delta=0,
                terminal_win=False,
                terminal_loss=False,
                step_index=step,
                previous_states={"macro": previous},
                power_memory={"macro": power},
                exponential_memory={"macro": exponential},
            )
        )
    return SyntheticScenario(name, family, atlas, tuple(transitions))


def generate_program_identification_scenarios(
    *, steps: int = 120, seed: int = 0
) -> tuple[SyntheticScenario, ...]:
    names = (
        "linear-fourier",
        "quadratic-spatial",
        "delay-portfolio",
        "fractional-fourier",
        "volterra-portfolio",
        "phase2-polyphase",
        "gated-color",
    )
    return tuple(
        generate_program_identification_scenario(name, steps=steps, seed=seed + index * 23)
        for index, name in enumerate(names)
    )
