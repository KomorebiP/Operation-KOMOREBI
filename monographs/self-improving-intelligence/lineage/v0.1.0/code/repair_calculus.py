"""Finite, table-defined repair synthesis. No network access or dynamic code execution.

The compiler's exact model is supplied. A compiled policy never receives the
hidden state; only the interpreter queries the model and passes back a report.
Storage counts literal tree records, not DAGs, bytecode, or environment tables.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Iterable

Q = Fraction

@dataclass(frozen=True)
class Experiment:
    name: str
    cost: Q
    transitions: tuple[tuple[int, int] | None, ...]  # (next state, report)

@dataclass(frozen=True)
class Repair:
    name: str
    cost: Q
    good: frozenset[int]

@dataclass(frozen=True)
class Problem:
    n: int
    experiments: tuple[Experiment, ...]
    repairs: tuple[Repair, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.n, int) or self.n < 1:
            raise ValueError('A problem needs a positive finite state count.')
        names = [x.name for x in self.experiments] + [x.name for x in self.repairs]
        if len(set(names)) != len(names):
            raise ValueError('Operation names must be distinct.')
        for e in self.experiments:
            if e.cost < 0 or len(e.transitions) != self.n:
                raise ValueError('Invalid experiment cost or transition count.')
            for item in e.transitions:
                if item is not None and (not 0 <= item[0] < self.n or not isinstance(item[1], int)):
                    raise ValueError('Invalid state or report.')
        for r in self.repairs:
            if r.cost < 0 or not r.good <= set(range(self.n)):
                raise ValueError('Invalid repair specification.')

@dataclass(frozen=True)
class Tree:
    kind: str
    index: int
    children: tuple[tuple[int, 'Tree'], ...] = ()

@dataclass(frozen=True)
class Witness:
    work: Q
    storage: int
    tree: Tree


def pareto(candidates: Iterable[Witness]) -> tuple[Witness, ...]:
    """Keep one deterministic representative per nondominated work/storage pair."""
    unique: dict[tuple[Q, int], Witness] = {}
    for w in candidates:
        unique.setdefault((w.work, w.storage), w)
    out = []
    best_storage: int | None = None
    for key in sorted(unique):
        if best_storage is None or key[1] < best_storage:
            out.append(unique[key])
            best_storage = key[1]
    return tuple(out)


def compile_frontier(problem: Problem, support: Iterable[int], horizon: int,
                     stats: dict[str, int] | None = None) -> tuple[Witness, ...]:
    """Exact theorem recurrence. Costs and model discovery are not hidden here."""
    support = tuple(sorted(set(support)))
    if not support or not set(support) <= set(range(problem.n)):
        raise ValueError('Initial support must be nonempty and in the model.')
    if not isinstance(horizon, int) or horizon < 0:
        raise ValueError('Horizon must be a nonnegative integer.')
    tally = stats if stats is not None else {}
    for key in ('support_horizon_states', 'experiment_roots_considered', 'child_combinations', 'terminal_candidates'):
        tally[key] = 0

    @lru_cache(None)
    def solve(states: tuple[int, ...], h: int) -> tuple[Witness, ...]:
        tally['support_horizon_states'] += 1
        b = frozenset(states)
        candidates = []
        for i, r in enumerate(problem.repairs):
            if b <= r.good:
                tally['terminal_candidates'] += 1
                candidates.append(Witness(r.cost, 1, Tree('repair', i)))
        if h:
            for ei, e in enumerate(problem.experiments):
                tally['experiment_roots_considered'] += 1
                if any(e.transitions[x] is None for x in states):
                    continue
                branches: dict[int, set[int]] = {}
                for x in states:
                    item = e.transitions[x]
                    if item is None:  # guarded above
                        raise RuntimeError('Inconsistent domain check.')
                    nx, report = item
                    branches.setdefault(report, set()).add(nx)
                reports = tuple(sorted(branches))
                child_frontiers = [solve(tuple(sorted(branches[o])), h-1) for o in reports]
                if any(not child for child in child_frontiers):
                    continue
                for combination in product(*child_frontiers):
                    tally['child_combinations'] += 1
                    tree = Tree('query', ei, tuple((o, w.tree) for o, w in zip(reports, combination)))
                    candidates.append(Witness(e.cost + max(w.work for w in combination),
                                              1 + sum(w.storage for w in combination), tree))
        return pareto(candidates)
    return solve(support, horizon)


def tree_records(tree: Tree) -> int:
    return 1 + sum(tree_records(child) for _, child in tree.children)


def tree_depth(tree: Tree) -> int:
    return 0 if tree.kind == 'repair' else 1 + max(tree_depth(c) for _, c in tree.children)


def replay(problem: Problem, tree: Tree, hidden: int, max_steps: int = 1000) -> dict:
    """The policy receives reports, never the hidden-state argument."""
    if not 0 <= hidden < problem.n:
        raise ValueError('Invalid initial hidden state.')
    node, state, spent, trace = tree, hidden, Q(0), []
    for _ in range(max_steps):
        if node.kind == 'repair':
            if node.children or not 0 <= node.index < len(problem.repairs):
                raise ValueError('Malformed repair leaf.')
            repair = problem.repairs[node.index]
            if state not in repair.good:
                raise ValueError('Repair is not valid in this case.')
            spent += repair.cost
            return {'initial_state': hidden, 'final_state': state,
                    'repair': repair.name, 'work': str(spent), 'trace': trace}
        if node.kind != 'query' or not 0 <= node.index < len(problem.experiments):
            raise ValueError('Malformed query node.')
        experiment = problem.experiments[node.index]
        item = experiment.transitions[state]
        if item is None:
            raise ValueError('Query is outside its admitted domain.')
        nx, report = item
        options = dict(node.children)
        if len(options) != len(node.children) or report not in options:
            raise ValueError('Missing or duplicate report branch.')
        trace.append({'query': experiment.name, 'report': report})
        spent += experiment.cost
        state, node = nx, options[report]
    raise ValueError('Replay exceeded its explicit traversal bound.')


def check_tree(problem: Problem, support: Iterable[int], tree: Tree, horizon: int,
               allowance: tuple[Q, int] | None = None) -> tuple[Q, int]:
    """Independent support reconstruction plus exhaustive episode replay."""
    states = frozenset(support)
    if not states or not states <= set(range(problem.n)) or horizon < 0:
        raise ValueError('Invalid checking contract.')

    def cover(node: Tree, possible: frozenset[int], h: int) -> None:
        if node.kind == 'repair':
            if node.children or not 0 <= node.index < len(problem.repairs):
                raise ValueError('Malformed leaf.')
            if not possible <= problem.repairs[node.index].good:
                raise ValueError('Leaf lacks a common successful repair.')
            return
        if node.kind != 'query' or h <= 0 or not 0 <= node.index < len(problem.experiments):
            raise ValueError('Invalid query or insufficient horizon.')
        e = problem.experiments[node.index]
        observed: dict[int, set[int]] = {}
        for state in possible:
            entry = e.transitions[state]
            if entry is None:
                raise ValueError('Experiment is not uniformly admissible.')
            observed.setdefault(entry[1], set()).add(entry[0])
        claimed = dict(node.children)
        if len(claimed) != len(node.children) or set(claimed) != set(observed):
            raise ValueError('Branch coverage differs from possible reports.')
        for report, future in observed.items():
            cover(claimed[report], frozenset(future), h-1)

    cover(tree, states, horizon)
    actual_work = max(Q(replay(problem, tree, s, horizon+2)['work']) for s in states)
    storage = tree_records(tree)
    if allowance is not None and (actual_work > allowance[0] or storage > allowance[1]):
        raise ValueError('The complete witness exceeds its allowance.')
    return actual_work, storage


def tree_to_dict(tree: Tree) -> dict:
    result = {'kind': tree.kind, 'index': tree.index}
    if tree.kind == 'query':
        result['children'] = [[o, tree_to_dict(c)] for o, c in tree.children]
    return result


def tree_from_dict(obj: dict, depth_limit: int = 100) -> Tree:
    if depth_limit < 0 or not isinstance(obj, dict):
        raise ValueError('Invalid tree serialization or depth.')
    if obj.get('kind') not in ('repair', 'query') or type(obj.get('index')) is not int:
        raise ValueError('Invalid tree fields.')
    raw = obj.get('children', [])
    if not isinstance(raw, list):
        raise ValueError('Children must be a list.')
    branches = []
    for pair in raw:
        if not isinstance(pair, list) or len(pair) != 2 or type(pair[0]) is not int:
            raise ValueError('Malformed branch.')
        branches.append((pair[0], tree_from_dict(pair[1], depth_limit-1)))
    return Tree(obj['kind'], obj['index'], tuple(branches))


def cell_problem(n: int, bits: bool = True) -> Problem:
    if n < 2 or n & (n-1):
        raise ValueError('The cell family requires a power of two at least two.')
    exps = [Experiment(f'eq_{i}', Q(1), tuple((j, int(j == i)) for j in range(n))) for i in range(n)]
    if bits:
        exps += [Experiment(f'bit_{b}', Q(1), tuple((j, (j >> b) & 1) for j in range(n)))
                 for b in range(n.bit_length()-1)]
    repairs = tuple(Repair(f'repair_{i}', Q(1), frozenset((i,))) for i in range(n))
    return Problem(n, tuple(exps), repairs)


def equality_tree(n: int, index: int = 0) -> Tree:
    if index == n-1:
        return Tree('repair', index)
    return Tree('query', index, ((0, equality_tree(n, index+1)), (1, Tree('repair', index))))


def bit_tree(n: int, support: tuple[int, ...] | None = None, bit: int = 0) -> Tree:
    support = tuple(range(n)) if support is None else support
    if len(support) == 1:
        return Tree('repair', support[0])
    children = tuple((o, bit_tree(n, tuple(j for j in support if ((j >> bit) & 1) == o), bit+1))
                     for o in (0, 1))
    return Tree('query', n+bit, children)


def relabel_problem(problem: Problem, sigma: tuple[int, ...], flips: tuple[int, ...] | None = None) -> Problem:
    if tuple(sorted(sigma)) != tuple(range(problem.n)):
        raise ValueError('State transport must be a permutation.')
    flips = flips or (0,) * len(problem.experiments)
    if len(flips) != len(problem.experiments) or any(x not in (0,1) for x in flips):
        raise ValueError('Invalid report flips.')
    experiments = []
    for i, e in enumerate(problem.experiments):
        rows: list[tuple[int, int] | None] = [None] * problem.n
        for x, item in enumerate(e.transitions):
            if item is not None:
                nx, report = item
                rows[sigma[x]] = (sigma[nx], report ^ flips[i])
        experiments.append(Experiment(e.name, e.cost, tuple(rows)))
    # Repair indices stay fixed. Their effects and names, not the indices, are transported.
    repairs = tuple(Repair(f'target_{r.name}', r.cost, frozenset(sigma[x] for x in r.good)) for r in problem.repairs)
    return Problem(problem.n, tuple(experiments), repairs)


def relabel_tree(tree: Tree, flips: tuple[int, ...]) -> Tree:
    if tree.kind == 'repair':
        return tree
    return Tree('query', tree.index,
                tuple(sorted((o ^ flips[tree.index], relabel_tree(c, flips)) for o, c in tree.children)))


def stable_partition(labels: tuple[int, ...], functions: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    n = len(labels)
    if n == 0 or any(len(f) != n or any(not 0 <= y < n for y in f) for f in functions):
        raise ValueError('Invalid finite transition model.')
    def normalize(keys: Iterable[object]) -> tuple[int, ...]:
        seen: dict[object,int] = {}
        return tuple(seen.setdefault(k, len(seen)) for k in keys)
    classes = normalize(labels)
    while True:
        refined = normalize((classes[x], tuple(classes[f[x]] for f in functions)) for x in range(n))
        if refined == classes:
            return classes
        classes = refined


@dataclass(frozen=True)
class Attempt:
    name: str
    outcomes: tuple[tuple[int, int], ...]  # successor, checked progress bit


def recursive_progress(actions: tuple[tuple[Attempt, ...], ...], safe: frozenset[int],
                       horizon: int, target: int) -> tuple[frozenset[int], dict[tuple[int,int], frozenset[int]], dict]:
    n = len(actions)
    if not safe <= set(range(n)) or horizon < 0 or target < 0:
        raise ValueError('Invalid recursive-progress contract.')
    for available in actions:
        for a in available:
            if not a.outcomes or any(not 0 <= z < n or p not in (0,1) for z,p in a.outcomes):
                raise ValueError('Invalid attempt outcomes.')
            if len({z for z,_ in a.outcomes}) != len(a.outcomes):
                raise ValueError('One attempt cannot assign two progress marks to a successor.')
    kernel = safe
    while True:
        smaller = frozenset(z for z in kernel if any(all(s in kernel for s,_ in a.outcomes) for a in actions[z]))
        if smaller == kernel:
            break
        kernel = smaller
    table: dict[tuple[int,int], frozenset[int]] = {(0,k): kernel if k == 0 else frozenset() for k in range(target+1)}
    policy: dict[tuple[int,int,int], int] = {}
    for h in range(1,horizon+1):
        for k in range(target+1):
            winning = set()
            for z in kernel:
                for ai,a in enumerate(actions[z]):
                    if all(s in kernel and s in table[h-1, max(0,k-p)] for s,p in a.outcomes):
                        winning.add(z)
                        policy[z,h,k] = ai
                        break
            table[h,k] = frozenset(winning)
    return kernel, table, policy
