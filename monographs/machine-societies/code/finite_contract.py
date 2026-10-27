"""Exact finite reference implementation for the v0.7 continuation theorems.

States and actions are zero-indexed. Sets of complete states are nonnegative
integer bit masks. Successors include ALL outcomes covered by the sure contract.
A catalogue action is a previously justified protocol profile, not a grant of
new information or authority. The code does not verify its physical implementation.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping


def bits(mask: int):
    if not isinstance(mask, int) or mask < 0:
        raise ValueError("A finite state mask must be a nonnegative integer.")
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


@dataclass(frozen=True)
class Contract:
    observations: tuple[int, ...]
    admissible: tuple[frozenset[int], ...]
    transitions: tuple[tuple[int, ...], ...]
    safe: int

    def __post_init__(self) -> None:
        n = len(self.observations)
        if not n or len(self.admissible) != n or len(self.transitions) != n:
            raise ValueError('The nonempty state arrays must have matching lengths.')
        m = len(self.transitions[0])
        if not m or any(len(row) != m for row in self.transitions):
            raise ValueError('The finite nonempty action catalogue must be rectangular.')
        full = (1 << n) - 1
        if not isinstance(self.safe, int) or self.safe < 0 or self.safe & ~full:
            raise ValueError('Safe-state mask is out of range.')
        if any(not isinstance(mask, int) or mask <= 0 or mask & ~full
               for row in self.transitions for mask in row):
            raise ValueError('Every successor set must be nonempty and in range.')
        if any(not isinstance(a, int) or not 0 <= a < m
               for row in self.admissible for a in row):
            raise ValueError('An admissible profile is outside the catalogue.')

    @property
    def state_count(self) -> int:
        return len(self.observations)

    @property
    def action_count(self) -> int:
        return len(self.transitions[0])


@dataclass
class KnowledgeGame:
    model: Contract
    beliefs: tuple[int, ...]
    actions: dict[int, frozenset[int]]
    successors: dict[tuple[int, int], frozenset[int]]


def expand(model: Contract) -> KnowledgeGame:
    fibres: dict[int, int] = {}
    for i, obs in enumerate(model.observations):
        fibres[obs] = fibres.get(obs, 0) | (1 << i)
    # Enumerate nonempty subsets within each observation fibre, rather than
    # every global subset. Fully observed n-state models now enumerate n sets,
    # not 2**n candidates. Order is retained for deterministic certificates.
    subsets: list[int] = []
    for fibre in fibres.values():
        b = fibre
        while b:
            subsets.append(b)
            b = (b - 1) & fibre
    beliefs = tuple(sorted(subsets))
    actions, successors = {}, {}
    for b in beliefs:
        members = tuple(bits(b))
        allowed = frozenset.intersection(*(model.admissible[i] for i in members))
        actions[b] = allowed
        for a in allowed:
            post = 0
            for i in members:
                post |= model.transitions[i][a]
            successors[b, a] = frozenset(post & fibre for fibre in fibres.values()
                                        if post & fibre)
    return KnowledgeGame(model, beliefs, actions, successors)


def safety_kernel(game: KnowledgeGame) -> tuple[frozenset[int], dict[int, int], list[frozenset[int]]]:
    current = frozenset(b for b in game.beliefs if not b & ~game.model.safe)
    layers = [current]
    while True:
        nxt = frozenset(b for b in current if any(
            game.successors[b, a] <= current for a in game.actions[b]))
        if nxt == current:
            break
        current = nxt
        layers.append(current)
    policy = {b: min(a for a in game.actions[b] if game.successors[b, a] <= current)
              for b in current}
    return current, policy, layers


def service_attractor(game: KnowledgeGame, viable: frozenset[int], goal: int
                     ) -> tuple[dict[int, int], dict[int, int]]:
    if not isinstance(goal, int) or goal < 0 or goal >= (1 << game.model.state_count):
        raise ValueError('Goal mask out of range.')
    ranks = {b: 0 for b in viable if not b & ~goal}
    choices: dict[int, int] = {}
    k = 0
    while True:
        prior = frozenset(ranks)
        additions = {}
        for b in sorted(viable - prior):
            options = [a for a in game.actions[b]
                       if game.successors[b, a] <= prior]
            if options:
                additions[b] = min(options)
        if not additions:
            break
        k += 1
        for b, a in additions.items():
            ranks[b] = k
            choices[b] = a
    return ranks, choices


def check_certificate(game: KnowledgeGame, initial: int, policy: Mapping[int, int],
                      ranks: Mapping[int, int] | None = None, goal: int | None = None
                      ) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    family = frozenset(policy)
    if initial not in family:
        errors.append('Initial possibility set is absent.')
    for b in family:
        if b not in game.actions:
            errors.append(f'{b}: invalid public possibility set.')
            continue
        if b & ~game.model.safe:
            errors.append(f'{b}: includes an unsafe state.')
        a = policy[b]
        if a not in game.actions[b]:
            errors.append(f'{b}: profile {a} is not admissible in every state.')
            continue
        if not game.successors[b, a] <= family:
            errors.append(f'{b}: certificate omits a possible successor.')
    if ranks is not None:
        if (not isinstance(goal, int) or goal < 0 or
                goal >= (1 << game.model.state_count)):
            errors.append('Progress goal mask is absent or outside the state space.')
        if set(ranks) != set(family):
            errors.append('Progress ranks must have exactly the policy domain.')
        invalid_ranks = [b for b, r in ranks.items() if not isinstance(r, int) or r < 0]
        if invalid_ranks:
            errors.append('Every progress rank must be a nonnegative integer.')
        if errors:
            return False, tuple(errors)
        for b, r in ranks.items():
            if r == 0 and b & ~goal:
                errors.append(f'{b}: zero rank does not certify completion.')
            a = policy[b]
            if r > 0:
                for nxt in game.successors[b, a]:
                    if ranks[nxt] >= r:
                        errors.append(f'{b}: rank fails to decrease at successor {nxt}.')
    return not errors, tuple(errors)


def image(mask: int, projection: tuple[int, ...]) -> int:
    out = 0
    for i in bits(mask):
        out |= 1 << projection[i]
    return out


def check_quotient(full: Contract, reduced: Contract, projection: tuple[int, ...],
                   full_goal: int, reduced_goal: int) -> tuple[bool, tuple[str, ...]]:
    errors = []
    if (len(projection) != full.state_count or
            set(projection) != set(range(reduced.state_count)) or
            full.action_count != reduced.action_count):
        return False, ('Projection is not a surjection with a shared catalogue.',)
    for i, z in enumerate(projection):
        if full.observations[i] != reduced.observations[z]:
            errors.append(f'{i}: observation mismatch.')
        if full.admissible[i] != reduced.admissible[z]:
            errors.append(f'{i}: action-admissibility mismatch.')
        if bool(full.safe & (1 << i)) != bool(reduced.safe & (1 << z)):
            errors.append(f'{i}: safety mismatch.')
        if bool(full_goal & (1 << i)) != bool(reduced_goal & (1 << z)):
            errors.append(f'{i}: completion mismatch.')
        for a in full.admissible[i]:
            if image(full.transitions[i][a], projection) != reduced.transitions[z][a]:
                errors.append(f'{i}, {a}: successor-image mismatch.')
    return not errors, tuple(errors)
