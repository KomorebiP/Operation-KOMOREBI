"""Synthetic recurrent systems with known ground truth."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin
from typing import Callable

import numpy as np


Array = np.ndarray


@dataclass(frozen=True)
class AffineSystem:
    name: str
    operator: Array
    offset: Array

    def step(self, state: Array) -> Array:
        return self.operator @ np.asarray(state, dtype=float) + self.offset

    def trajectory(self, initial: Array, steps: int) -> Array:
        if steps < 1:
            raise ValueError("steps must be positive")
        states = [np.asarray(initial, dtype=float).copy()]
        for _ in range(steps):
            states.append(self.step(states[-1]))
        return np.vstack(states)


def contraction_system() -> tuple[AffineSystem, Array]:
    operator = np.diag([0.35, 0.72])
    fixed_point = np.array([1.25, -0.75])
    offset = fixed_point - operator @ fixed_point
    return AffineSystem("contraction", operator, offset), fixed_point


def rotation_system(theta: float = 0.37, radius: float = 1.0) -> AffineSystem:
    operator = radius * np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    return AffineSystem("rotation", operator, np.zeros(2))


def slider_system() -> AffineSystem:
    operator = np.array([[1.0, 1.0], [0.0, 1.0]])
    return AffineSystem("slider_jordan", operator, np.zeros(2))


def mixed_system(theta: float = 0.41) -> tuple[AffineSystem, tuple[tuple[int, ...], ...]]:
    rotation = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    slider = np.array([[1.0, 1.0], [0.0, 1.0]])
    operator = np.zeros((5, 5))
    operator[0, 0] = 0.55
    operator[1:3, 1:3] = rotation
    operator[3:5, 3:5] = slider
    operator[1:3, 0:1] = np.array([[0.2], [-0.1]])
    operator[3:5, 1:3] = np.array([[0.10, -0.05], [0.02, 0.04]])
    groups = ((0,), (1, 2), (3, 4))
    return AffineSystem("mixed", operator, np.zeros(5)), groups


def generate_trajectories(
    system: AffineSystem,
    initials: list[Array],
    steps: int,
) -> list[Array]:
    return [system.trajectory(initial, steps) for initial in initials]


def nonlinear_saturating_system(scale: float = 0.82) -> Callable[[Array], Array]:
    """A bounded nonlinear recurrence for leakage and local-fit controls."""

    def step(state: Array) -> Array:
        value = np.asarray(state, dtype=float)
        return np.tanh(scale * value + np.array([0.2, -0.1]))

    return step


def nonlinear_trajectory(step: Callable[[Array], Array], initial: Array, steps: int) -> Array:
    states = [np.asarray(initial, dtype=float).copy()]
    for _ in range(steps):
        states.append(step(states[-1]))
    return np.vstack(states)
