"""Procedural environments for testing recursive resolution closure.

The environments in this module contain no language about consciousness and no
valence-like state.  They test whether an architecture can bind information
that arrives through separate channels, preserve it across a delay, model a
changing actuator map, and reuse the resulting representation for new tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np


TaskName = Literal["product", "majority", "context_object", "object_actuator"]


@dataclass(frozen=True)
class BindingEpisode:
    """One delayed, partially observed binding episode."""

    observations: np.ndarray
    context: int
    object_cue: int
    actuator_map: int
    episode_id: int

    def label(self, task: TaskName = "product") -> int:
        """Return the binary decision for one compositional task."""

        c = self.context
        o = self.object_cue
        a = self.actuator_map
        if task == "product":
            signed = c * o * a
        elif task == "majority":
            signed = c + o + a
        elif task == "context_object":
            signed = c * o
        elif task == "object_actuator":
            signed = o * a
        else:  # pragma: no cover - guarded by the Literal type
            raise ValueError(f"unknown task: {task}")
        return int(signed > 0)


class DelayedBindingEnvironment:
    """Generate episodes that require temporal and cross-channel integration.

    Observation layout (12 dimensions):

    ``0:3`` cue values, ``3:6`` cue-presence masks, ``6`` normalized time,
    ``7`` decision flag, ``8`` an independent episode marker, and ``9:12``
    distractors.  The marker is sampled independently of the latent factors so
    it cannot leak the target through enumeration order.
    """

    observation_dim = 12

    def __init__(
        self,
        *,
        delay: int = 5,
        noise: float = 0.04,
        distractor_scale: float = 0.7,
        seed: int = 0,
    ) -> None:
        if delay < 1:
            raise ValueError("delay must be positive")
        if noise < 0 or distractor_scale < 0:
            raise ValueError("noise scales must be nonnegative")
        self.delay = int(delay)
        self.noise = float(noise)
        self.distractor_scale = float(distractor_scale)
        self.rng = np.random.default_rng(seed)
        self._episode_counter = 0

    @property
    def sequence_length(self) -> int:
        return self.delay + 3

    def sample(self) -> BindingEpisode:
        """Sample a new episode from the balanced latent-factor space."""

        c, o, a = self.rng.choice((-1, 1), size=3).astype(int)
        eid = self._episode_counter
        self._episode_counter += 1
        obs = self._build_observations(c, o, a, eid)
        return BindingEpisode(obs, int(c), int(o), int(a), eid)

    def enumerate_latents(self, repeats: int = 1) -> Iterable[BindingEpisode]:
        """Yield every latent combination, with fresh observation noise."""

        if repeats < 1:
            raise ValueError("repeats must be positive")
        for _ in range(repeats):
            for c in (-1, 1):
                for o in (-1, 1):
                    for a in (-1, 1):
                        eid = self._episode_counter
                        self._episode_counter += 1
                        yield BindingEpisode(
                            self._build_observations(c, o, a, eid), c, o, a, eid
                        )

    def _build_observations(self, c: int, o: int, a: int, eid: int) -> np.ndarray:
        steps = self.sequence_length
        x = np.zeros((steps, self.observation_dim), dtype=np.float64)

        # The three relevant variables are never directly co-present.
        x[0, 0] = c
        x[0, 3] = 1.0
        x[1, 1] = o
        x[1, 4] = 1.0
        x[-1, 2] = a
        x[-1, 5] = 1.0

        x[:, 6] = np.linspace(0.0, 1.0, steps)
        x[-1, 7] = 1.0
        x[:, 8] = self.rng.uniform(-1.0, 1.0)
        x[:, 9:12] = self.rng.normal(
            0.0, self.distractor_scale, size=(steps, 3)
        )

        if self.noise:
            # Noise is applied to values, not masks or the decision flag.
            noisy = np.r_[0:3, 6, 8:12]
            x[:, noisy] += self.rng.normal(0.0, self.noise, size=(steps, len(noisy)))
        return x


def task_names() -> tuple[TaskName, ...]:
    """Return all preregistered flexible-reuse tasks."""

    return ("product", "majority", "context_object", "object_actuator")
