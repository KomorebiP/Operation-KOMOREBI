"""Bounded recursive compiler for Block 9 relational compositions.

Compilation and prediction are deliberately separate.  ``compile_programs``
can inspect labelled demonstrations, but it never executes a test input.  Only
after the exact demonstration programs have been frozen does
``execute_candidates`` evaluate those programs on the sanitized test inputs.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .bank import RuntimeAbstractionBank
from .abstraction import (
    extract_template_bindings,
    normalize_leaf_sequence,
    semantic_subtree_schema,
)
from .dynamic_layout import compile_dynamic_layout_with_trace
from .ir_bridge import (
    execute_with_prefix_checks,
    registry_contract_hash,
    to_ir_program,
)
from .model import (
    CompositionCandidate,
    CompositionLimits,
    CompositionTrace,
    CompositeProgram,
    Grid,
    LeafInvocation,
    ProgressCertificate,
    ResidualBatch,
    canonical_value,
    sha256_record,
    validate_grid,
)
from .residual import certify_transition, derive_residual_batch, infer_background
from .stages import (
    atomic_leaf,
    execute_leaf,
    propose_atomic_stages,
    propose_endpoint_closers,
    verified_inherited_macro_ids,
)
from .task import TrainingTask, sanitize_training_task


DEFAULT_LIMITS = CompositionLimits(
    max_depth=2,
    max_frontier=32,
    max_proposals_per_state=4_096,
    max_expansions=8_192,
    max_total_cost=18,
    progress_mode="residual_subset",
)

EXPECTED_BLOCK6_BANK_ID = "79dfa3ae8817eb47eed2eaf7e9cbfdf733fcaafea0f36d308efa10059ebf3f24"
EXPECTED_BLOCK8_BANK_ID = "0f286f8fa001cff25da8dc4891214a38dfcb52224f324e9d57e23a23c71c61d9"
EXPECTED_BLOCK9_BANK_ID = "2c49c17097e76d718365b4b19cf57903ccc67d6256a74eb3fa6863ca7a881899"
EMPTY_BLOCK9_BANK_ID = "5afadbd3aa99e51c2ba3bab263067678b5607353e5f2ee10207b24b09b44c6e6"

# These are refinement contracts, not task identifiers.  Corpus-wide
# ablations established that the inherited exact endpoints currently have one
# productive partial normalizer (foreground cropping), while the open-U stage
# is the one certified enabling prefix for deeper atomic recursion.  Keeping
# the default lane narrow makes the hard search budget meaningful; callers can
# still exercise every atomic family independently through the public proposer.
_ENDPOINT_ENABLING_FAMILIES = frozenset({"crop_bbox"})
_RECURSIVE_ENABLING_FAMILIES = frozenset({"outer_clockwise_u"})


@dataclass(frozen=True, slots=True)
class _SearchState:
    currents: tuple[Grid, ...]
    residual: ResidualBatch
    leaves: tuple[LeafInvocation, ...]
    certificates: tuple[ProgressCertificate, ...]
    visited_state_hashes: tuple[str, ...]
    total_cost: int

    @property
    def behavior_hash(self) -> str:
        return sha256_record(self.currents)


def _runtime_bank(
    value: RuntimeAbstractionBank | Mapping[str, Any] | None,
) -> RuntimeAbstractionBank:
    if value is None:
        path = Path(__file__).with_name("data") / "runtime_abstraction_bank.json"
        value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, RuntimeAbstractionBank):
        # Round-trip through the public verifier so even constructed values use
        # the exact serialized runtime contract.
        bank = RuntimeAbstractionBank.verify_runtime_record(value.to_runtime_record())
    else:
        bank = RuntimeAbstractionBank.verify_runtime_record(value)
    if bank.bank_id not in {EXPECTED_BLOCK9_BANK_ID, EMPTY_BLOCK9_BANK_ID}:
        raise PermissionError("compiler requires the pinned Block 9 bank or the empty discovery bank")
    return bank


def _bank_bundle_id(
    block6_bank_record: Mapping[str, Any] | None,
    block8_bank_record: Mapping[str, Any] | None,
    abstraction_bank: RuntimeAbstractionBank,
) -> str:
    return sha256_record({
        "block6": canonical_value(block6_bank_record) if block6_bank_record is not None else None,
        "block8": canonical_value(block8_bank_record) if block8_bank_record is not None else None,
        "block9": abstraction_bank.bank_id,
    })


def _execute_batch(leaf: LeafInvocation, grids: Sequence[Grid]) -> tuple[Grid, ...] | None:
    try:
        return tuple(validate_grid(execute_leaf(leaf, grid)) for grid in grids)
    except (AssertionError, KeyError, TypeError, ValueError, OverflowError):
        return None


def _progress_certificate(
    before: Sequence[Grid],
    after: Sequence[Grid],
    targets: Sequence[Grid],
    *,
    root_backgrounds: Sequence[int],
    preferred_mode: str,
    visited_state_hashes: Sequence[str],
) -> ProgressCertificate | None:
    modes = [preferred_mode]
    if preferred_mode != "shape_correction" and any(
        (len(current), len(current[0])) != (len(target), len(target[0]))
        for current, target in zip(before, targets)
    ):
        modes.append("shape_correction")
    # Never silently widen a strict production contract to the permissive
    # distance lane.  ``strict_descent`` is used only when explicitly selected.
    for mode in dict.fromkeys(modes):
        certificate = certify_transition(
            before,
            after,
            targets,
            mode,  # type: ignore[arg-type]
            root_backgrounds=root_backgrounds,
            visited_state_hashes=visited_state_hashes,
        )
        if certificate is not None:
            return certificate
    return None


def _make_program(
    state: _SearchState,
    *,
    training_hashes: tuple[str, ...],
    bank_id: str,
    block6_macro_ids: frozenset[str],
    block8_macro_ids: frozenset[str],
) -> CompositeProgram:
    if not state.residual.exact:
        raise ValueError("only demonstration-exact states can become programs")
    program = CompositeProgram(
        leaves=state.leaves,
        certificates=state.certificates,
        training_hashes=training_hashes,
        bank_id=bank_id,
        registry_hash=registry_contract_hash(),
    )
    verify_program_authorization(
        program,
        block6_macro_ids=block6_macro_ids,
        block8_macro_ids=block8_macro_ids,
    )
    return program


def verify_program_authorization(
    program: CompositeProgram,
    *,
    block6_macro_ids: frozenset[str],
    block8_macro_ids: frozenset[str],
) -> None:
    """Bind every inherited leaf to a verified stable runtime-bank member."""
    if not isinstance(program, CompositeProgram):
        raise TypeError("program must be a CompositeProgram")
    for leaf in program.leaves:
        if leaf.namespace == "block6" and leaf.source_macro_id not in block6_macro_ids:
            raise PermissionError("Block 6 leaf is not authorized by the bound stable bank")
        if leaf.namespace == "block8" and leaf.source_macro_id not in block8_macro_ids:
            raise PermissionError("Block 8 leaf is not authorized by the bound stable bank")


def expand_matching_promoted_macro(
    program: CompositeProgram,
    bank: RuntimeAbstractionBank,
    *,
    training_inputs: Sequence[Grid],
    block6_macro_ids: frozenset[str],
    block8_macro_ids: frozenset[str],
) -> tuple[CompositeProgram, str | None]:
    """Bind and execute a matching stable rank-1 abstraction, if available.

    The bank never supplies observed values.  Bindings are recovered from the
    current demonstration-derived program, type checked, expanded, and then
    required to preserve every prefix behavior before replacing the syntax.
    """
    if len(program.leaves) < 2 or not bank.macros:
        return program, None
    schema = semantic_subtree_schema(program.leaves)
    original_prefixes: list[tuple[Grid, ...]] = []
    states = tuple(training_inputs)
    for leaf in program.leaves:
        result = _execute_batch(leaf, states)
        if result is None:
            raise ValueError("compiled program no longer executes on its demonstrations")
        states = result
        original_prefixes.append(states)
    for template in bank.matching_schema(schema, stable_only=True):
        try:
            bindings = extract_template_bindings(template, program.leaves)
            records = bank.expand(template.macro_id, bindings, stable_only=True)
            expanded = tuple(LeafInvocation.from_parameters(
                namespace=str(record["namespace"]),  # type: ignore[arg-type]
                family=str(record["family"]),
                macro_schema=str(record["macro_schema"]),
                parameters=dict(record["parameters"]),
                source_macro_id=str(record.get("source_macro_id") or ""),
                cost=int(record.get("cost", 1)),
                status=str(record.get("status", "primitive")),
            ) for record in records)
            def semantic_projection(leaves: Sequence[LeafInvocation]) -> tuple[dict[str, Any], ...]:
                projected = []
                for record in normalize_leaf_sequence(leaves):
                    projected.append({
                        key: value for key, value in record.items()
                        if key not in {"cost", "source_macro_id", "status"}
                    })
                return tuple(projected)
            if semantic_projection(expanded) != semantic_projection(program.leaves):
                continue
            states = tuple(training_inputs)
            for index, leaf in enumerate(expanded):
                result = _execute_batch(leaf, states)
                if result is None or result != original_prefixes[index]:
                    raise ValueError("promoted expansion changes a prefix behavior")
                states = result
            replacement = CompositeProgram(
                leaves=expanded,
                certificates=program.certificates,
                training_hashes=program.training_hashes,
                bank_id=program.bank_id,
                registry_hash=program.registry_hash,
            )
            verify_program_authorization(
                replacement,
                block6_macro_ids=block6_macro_ids,
                block8_macro_ids=block8_macro_ids,
            )
            # Expansion is an authorization proof, not a second costing pass.
            # The original program has already been budgeted and canonically
            # ordered.  Replacing it with a template whose leaf costs summarize
            # multiple source occurrences can change the representative of an
            # otherwise identical behavior class and make closure depend on the
            # input bank.  Preserve the compiled syntax after the bound
            # expansion has passed semantic, prefix, and provenance checks.
            return program, template.macro_id
        except (KeyError, PermissionError, TypeError, ValueError):
            continue
    return program, None


def _program_order(program: CompositeProgram) -> tuple[Any, ...]:
    return (
        program.total_cost,
        program.leaf_count,
        program.semantic_hash,
        program.syntax_hash,
    )


def _is_irreducible(program: CompositeProgram, inputs: Sequence[Grid], targets: Sequence[Grid]) -> bool:
    """Reject a composite having any exact proper order-preserving subsequence."""
    if len(program.leaves) < 2:
        return True
    count = len(program.leaves)
    if count > 8:
        # Public limits reject this earlier; retain a local guard for callers
        # constructing records directly.
        raise ValueError("irreducibility proof is bounded to eight leaves")
    for mask in range(1, (1 << count) - 1):
        state = tuple(inputs)
        valid = True
        for index, leaf in enumerate(program.leaves):
            if not mask & (1 << index):
                continue
            result = _execute_batch(leaf, state)
            if result is None:
                valid = False
                break
            state = result
        if valid and state == tuple(targets):
            return False
    return True


def _dynamic_layout_programs(
    task: TrainingTask,
    *,
    limits: CompositionLimits,
    root_backgrounds: tuple[int, ...],
    bank_id: str,
    block6_macro_ids: frozenset[str],
    block8_macro_ids: frozenset[str],
) -> tuple[list[CompositeProgram], dict[str, Any]]:
    mapping = {
        "train": [example.to_mapping() for example in task.train],
        # Intentionally omit the test member: candidate synthesis must be
        # invariant even to the held-out input shape.
    }
    programs, trace = compile_dynamic_layout_with_trace(
        mapping,
        proposal_budget=min(
            limits.max_proposals_per_state,
            limits.max_expansions,
            4_096,
        ),
    )
    result: list[CompositeProgram] = []
    cost_rejections = 0
    for program in programs:
        leaf = atomic_leaf(program.family, program.parameters.to_record())
        if leaf.cost > limits.max_total_cost:
            cost_rejections += 1
            continue
        after = _execute_batch(leaf, task.training_inputs)
        if after is None or after != task.training_outputs:
            continue
        certificate = _progress_certificate(
            task.training_inputs,
            after,
            task.training_outputs,
            root_backgrounds=root_backgrounds,
            preferred_mode="shape_correction",
            visited_state_hashes=(sha256_record(task.training_inputs),),
        )
        if certificate is None:
            continue
        exact = derive_residual_batch(
            after,
            task.training_outputs,
            root_backgrounds=root_backgrounds,
        )
        state = _SearchState(
            currents=after,
            residual=exact,
            leaves=(leaf,),
            certificates=(certificate,),
            visited_state_hashes=(sha256_record(task.training_inputs), sha256_record(after)),
            total_cost=leaf.cost,
        )
        result.append(_make_program(
            state,
            training_hashes=task.training_hashes,
            bank_id=bank_id,
            block6_macro_ids=block6_macro_ids,
            block8_macro_ids=block8_macro_ids,
        ))
    trace = {**trace, "cost_budget_rejections": cost_rejections}
    return result, trace


def compile_programs(
    task: Mapping[str, Any] | TrainingTask,
    *,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    abstraction_bank: RuntimeAbstractionBank | Mapping[str, Any] | None = None,
    limits: CompositionLimits = DEFAULT_LIMITS,
) -> tuple[tuple[CompositeProgram, ...], CompositionTrace]:
    """Compile bounded exact programs without executing any test input."""
    if not isinstance(limits, CompositionLimits):
        raise TypeError("limits must be a CompositionLimits record")
    if limits.max_depth > 8:
        raise ValueError("Block 9 composition depth is hard-capped at eight leaves")
    if block6_bank_record is None or block6_bank_record.get("bank_id") != EXPECTED_BLOCK6_BANK_ID:
        raise PermissionError("compiler requires the pinned Block 6/7 stable runtime bank")
    if block8_bank_record is None or block8_bank_record.get("bank_id") != EXPECTED_BLOCK8_BANK_ID:
        raise PermissionError("compiler requires the pinned Block 8 stable runtime bank")
    sanitized = sanitize_training_task(task)
    promoted = _runtime_bank(abstraction_bank)
    block6_macro_ids, block8_macro_ids = verified_inherited_macro_ids(
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
    )
    bank_id = _bank_bundle_id(block6_bank_record, block8_bank_record, promoted)
    targets = sanitized.training_outputs
    root_backgrounds = tuple(infer_background(grid) for grid in sanitized.training_inputs)
    root_residual = derive_residual_batch(
        sanitized.training_inputs,
        targets,
        root_backgrounds=root_backgrounds,
    )
    root_hash = sha256_record(sanitized.training_inputs)
    trace_counts: Counter[str] = Counter()
    proposals_considered = 0
    transitions_accepted = 0
    states_expanded = 0
    max_depth_reached = 0
    limit_reached = ""
    exact_by_semantics: dict[str, CompositeProgram] = {}
    promoted_macro_ids_used: set[str] = set()

    dynamic_programs, dynamic_trace = _dynamic_layout_programs(
        sanitized,
        limits=limits,
        root_backgrounds=root_backgrounds,
        bank_id=bank_id,
        block6_macro_ids=block6_macro_ids,
        block8_macro_ids=block8_macro_ids,
    )
    proposals_considered += int(dynamic_trace["proposals_considered"])
    trace_counts["cost_budget"] += int(dynamic_trace.get("cost_budget_rejections", 0))
    for program in dynamic_programs:
        exact_by_semantics.setdefault(program.semantic_hash, program)

    # Minimum-description closure: a demonstration-exact constructor is
    # already a complete behavior class.  Do not manufacture deeper programs
    # around it or execute held-out inputs during this decision.
    if exact_by_semantics:
        programs = tuple(sorted(exact_by_semantics.values(), key=_program_order))
        return programs, CompositionTrace(
            root_packet_id=root_residual.aggregate_packet_id,
            lanes_attempted=("dynamic_layout",),
            states_expanded=0,
            proposals_considered=proposals_considered,
            transitions_accepted=len(programs),
            exact_programs=len(programs),
            behavior_classes=0,
            max_depth_reached=1,
            rejection_counts=tuple(sorted(
                (name, int(count)) for name, count in trace_counts.items() if count
            )),
            limit_reached="",
        )

    frontier = (_SearchState(
        currents=sanitized.training_inputs,
        residual=root_residual,
        leaves=(),
        certificates=(),
        visited_state_hashes=(root_hash,),
        total_cost=0,
    ),)

    for depth in range(1, limits.max_depth + 1):
        next_by_behavior: dict[str, _SearchState] = {}
        for state in frontier:
            if states_expanded >= limits.max_expansions:
                limit_reached = "max_expansions"
                break
            states_expanded += 1
            leaves = propose_atomic_stages(
                state.currents,
                targets,
                state.residual,
                budget=limits.max_proposals_per_state,
            )
            for leaf in leaves:
                if proposals_considered >= limits.max_expansions:
                    limit_reached = "max_expansions"
                    break
                proposals_considered += 1
                if state.total_cost + leaf.cost > limits.max_total_cost:
                    trace_counts["cost_budget"] += 1
                    continue
                after = _execute_batch(leaf, state.currents)
                if after is None:
                    trace_counts["runtime_rejection"] += 1
                    continue
                certificate = _progress_certificate(
                    state.currents,
                    after,
                    targets,
                    root_backgrounds=root_backgrounds,
                    preferred_mode=limits.progress_mode,
                    visited_state_hashes=state.visited_state_hashes,
                )
                if certificate is None:
                    trace_counts["progress_rejection"] += 1
                    continue
                transitions_accepted += 1
                residual = derive_residual_batch(
                    after,
                    targets,
                    root_backgrounds=root_backgrounds,
                )
                child = _SearchState(
                    currents=after,
                    residual=residual,
                    leaves=state.leaves + (leaf,),
                    certificates=state.certificates + (certificate,),
                    visited_state_hashes=state.visited_state_hashes + (sha256_record(after),),
                    total_cost=state.total_cost + leaf.cost,
                )
                max_depth_reached = max(max_depth_reached, len(child.leaves))

                # Atomic programs enter the score-changing lane only when they
                # are genuinely composite.  Single-stage constructor programs
                # are handled by the separately bounded dynamic-layout family.
                if residual.exact and len(child.leaves) >= 2:
                    program = _make_program(
                        child,
                        training_hashes=sanitized.training_hashes,
                        bank_id=bank_id,
                        block6_macro_ids=block6_macro_ids,
                        block8_macro_ids=block8_macro_ids,
                    )
                    program, macro_id = expand_matching_promoted_macro(
                        program,
                        promoted,
                        training_inputs=sanitized.training_inputs,
                        block6_macro_ids=block6_macro_ids,
                        block8_macro_ids=block8_macro_ids,
                    )
                    if macro_id is not None:
                        promoted_macro_ids_used.add(macro_id)
                    if _is_irreducible(program, sanitized.training_inputs, targets):
                        prior = exact_by_semantics.get(program.semantic_hash)
                        if prior is None or _program_order(program) < _program_order(prior):
                            exact_by_semantics[program.semantic_hash] = program
                    else:
                        trace_counts["reducible_program"] += 1
                    continue

                # Stable inherited schemas may close an intermediate residual.
                remaining = max(0, limits.max_proposals_per_state - len(leaves))
                endpoints = ()
                if (
                    len(child.leaves) < limits.max_depth
                    and leaf.family in _ENDPOINT_ENABLING_FAMILIES
                ):
                    endpoints = propose_endpoint_closers(
                        after,
                        targets,
                        block6_bank_record=block6_bank_record,
                        block8_bank_record=block8_bank_record,
                        budget=remaining,
                    )
                for endpoint in endpoints:
                    if proposals_considered >= limits.max_expansions:
                        limit_reached = "max_expansions"
                        break
                    proposals_considered += 1
                    if child.total_cost + endpoint.cost > limits.max_total_cost:
                        trace_counts["cost_budget"] += 1
                        continue
                    final = _execute_batch(endpoint, after)
                    if final is None or final != targets:
                        trace_counts["endpoint_rejection"] += 1
                        continue
                    final_certificate = _progress_certificate(
                        after,
                        final,
                        targets,
                        root_backgrounds=root_backgrounds,
                        preferred_mode=limits.progress_mode,
                        visited_state_hashes=child.visited_state_hashes,
                    )
                    if final_certificate is None:
                        trace_counts["endpoint_progress_rejection"] += 1
                        continue
                    exact_state = _SearchState(
                        currents=final,
                        residual=derive_residual_batch(
                            final,
                            targets,
                            root_backgrounds=root_backgrounds,
                        ),
                        leaves=child.leaves + (endpoint,),
                        certificates=child.certificates + (final_certificate,),
                        visited_state_hashes=child.visited_state_hashes + (sha256_record(final),),
                        total_cost=child.total_cost + endpoint.cost,
                    )
                    max_depth_reached = max(max_depth_reached, len(exact_state.leaves))
                    program = _make_program(
                        exact_state,
                        training_hashes=sanitized.training_hashes,
                        bank_id=bank_id,
                        block6_macro_ids=block6_macro_ids,
                        block8_macro_ids=block8_macro_ids,
                    )
                    program, macro_id = expand_matching_promoted_macro(
                        program,
                        promoted,
                        training_inputs=sanitized.training_inputs,
                        block6_macro_ids=block6_macro_ids,
                        block8_macro_ids=block8_macro_ids,
                    )
                    if macro_id is not None:
                        promoted_macro_ids_used.add(macro_id)
                    if not _is_irreducible(program, sanitized.training_inputs, targets):
                        trace_counts["reducible_program"] += 1
                        continue
                    prior = exact_by_semantics.get(program.semantic_hash)
                    if prior is None or _program_order(program) < _program_order(prior):
                        exact_by_semantics[program.semantic_hash] = program

                if (
                    depth < limits.max_depth
                    and leaf.family in _RECURSIVE_ENABLING_FAMILIES
                ):
                    prior = next_by_behavior.get(child.behavior_hash)
                    if prior is None or (
                        child.total_cost,
                        tuple(item.semantic_hash for item in child.leaves),
                    ) < (
                        prior.total_cost,
                        tuple(item.semantic_hash for item in prior.leaves),
                    ):
                        next_by_behavior[child.behavior_hash] = child
            if limit_reached:
                break
        if limit_reached:
            break
        frontier = tuple(sorted(
            next_by_behavior.values(),
            key=lambda state: (
                tuple(example.measure for example in state.residual.examples),
                state.total_cost,
                state.behavior_hash,
            ),
        )[: limits.max_frontier])
        if not frontier:
            break

    programs = tuple(sorted(exact_by_semantics.values(), key=_program_order))
    trace = CompositionTrace(
        root_packet_id=root_residual.aggregate_packet_id,
        lanes_attempted=tuple(dict.fromkeys(
            ("dynamic_layout",)
            + root_residual.route_lanes
            + ("recursive_composition",)
            + (("abstraction_closure",) if promoted_macro_ids_used else ())
        )),
        states_expanded=states_expanded,
        proposals_considered=proposals_considered,
        transitions_accepted=transitions_accepted,
        exact_programs=len(programs),
        behavior_classes=0,
        max_depth_reached=max_depth_reached,
        rejection_counts=tuple(sorted((name, int(count)) for name, count in trace_counts.items())),
        limit_reached=limit_reached,
    )
    return programs, trace


def _execute_native(program: CompositeProgram, grid: Grid) -> tuple[Grid, tuple[Grid, ...]]:
    state = validate_grid(grid)
    prefixes: list[Grid] = []
    for leaf in program.leaves:
        state = validate_grid(execute_leaf(leaf, state))
        prefixes.append(state)
    return state, tuple(prefixes)


def execute_program(
    program: CompositeProgram,
    grid: Grid,
    *,
    block6_bank_record: Mapping[str, Any],
    block8_bank_record: Mapping[str, Any],
    abstraction_bank: RuntimeAbstractionBank | Mapping[str, Any] | None = None,
    verify_ir: bool = True,
) -> Grid:
    """Execute a frozen composite under its exact stable-bank bindings."""
    if block6_bank_record.get("bank_id") != EXPECTED_BLOCK6_BANK_ID:
        raise PermissionError("execution requires the pinned Block 6/7 bank")
    if block8_bank_record.get("bank_id") != EXPECTED_BLOCK8_BANK_ID:
        raise PermissionError("execution requires the pinned Block 8 bank")
    promoted = _runtime_bank(abstraction_bank)
    block6_ids, block8_ids = verified_inherited_macro_ids(
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
    )
    if program.bank_id != _bank_bundle_id(block6_bank_record, block8_bank_record, promoted):
        raise PermissionError("program is not bound to the supplied runtime-bank bundle")
    verify_program_authorization(
        program,
        block6_macro_ids=block6_ids,
        block8_macro_ids=block8_ids,
    )
    direct, _ = _execute_native(program, validate_grid(grid))
    if verify_ir:
        via_ir, _ = execute_with_prefix_checks(program, grid)
        if direct != via_ir:
            raise AssertionError("native and Program IR executions disagree")
    return direct


def execute_candidates(
    task: Mapping[str, Any] | TrainingTask,
    *,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    abstraction_bank: RuntimeAbstractionBank | Mapping[str, Any] | None = None,
    limits: CompositionLimits = DEFAULT_LIMITS,
) -> tuple[tuple[CompositionCandidate, ...], CompositionTrace]:
    """Freeze exact programs, then quotient their held-out-input behaviors."""
    sanitized = sanitize_training_task(task)
    programs, compilation_trace = compile_programs(
        sanitized,
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
        abstraction_bank=abstraction_bank,
        limits=limits,
    )
    all_inputs = sanitized.training_inputs + sanitized.test_inputs
    by_behavior: dict[str, CompositionCandidate] = {}
    runtime_rejections = 0
    for program in programs:
        finals: list[Grid] = []
        per_prefix: list[list[Grid]] = [[] for _ in program.leaves]
        valid = True
        try:
            for grid in all_inputs:
                direct, direct_prefixes = _execute_native(program, grid)
                via_ir, evidence = execute_with_prefix_checks(program, grid)
                if direct != via_ir:
                    raise AssertionError("native and Program IR final executions disagree")
                if tuple(item.direct_output for item in evidence) != direct_prefixes:
                    raise AssertionError("native and Program IR prefix executions disagree")
                finals.append(direct)
                for index, value in enumerate(direct_prefixes):
                    per_prefix[index].append(value)
        except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            valid = False
        if not valid:
            runtime_rejections += 1
            continue
        training_outputs = tuple(finals[: len(sanitized.training_inputs)])
        if training_outputs != sanitized.training_outputs:
            runtime_rejections += 1
            continue
        test_outputs = tuple(finals[len(sanitized.training_inputs) :])
        candidate = CompositionCandidate(
            program=program,
            training_outputs=training_outputs,
            test_outputs=test_outputs,
            native_execution_hash=sha256_record(finals),
            ir_program_hash=to_ir_program(program).content_hash(),
            prefix_behavior_hashes=tuple(sha256_record(values) for values in per_prefix),
        )
        prior = by_behavior.get(candidate.behavior_hash)
        if prior is None or _program_order(candidate.program) < _program_order(prior.program):
            by_behavior[candidate.behavior_hash] = candidate
    candidates = tuple(sorted(
        by_behavior.values(),
        key=lambda item: (_program_order(item.program), item.behavior_hash),
    ))
    rejections = Counter(dict(compilation_trace.rejection_counts))
    if runtime_rejections:
        rejections["runtime_or_ir_rejection"] += runtime_rejections
    trace = CompositionTrace(
        root_packet_id=compilation_trace.root_packet_id,
        lanes_attempted=compilation_trace.lanes_attempted,
        states_expanded=compilation_trace.states_expanded,
        proposals_considered=compilation_trace.proposals_considered,
        transitions_accepted=compilation_trace.transitions_accepted,
        exact_programs=compilation_trace.exact_programs,
        behavior_classes=len(candidates),
        max_depth_reached=compilation_trace.max_depth_reached,
        rejection_counts=tuple(sorted(rejections.items())),
        limit_reached=compilation_trace.limit_reached,
    )
    return candidates, trace


def compile_record(
    task: Mapping[str, Any] | TrainingTask,
    **kwargs: Any,
) -> dict[str, Any]:
    candidates, trace = execute_candidates(task, **kwargs)
    return {
        "schema": "komorebi.lasm_recursive_composition_record",
        "schema_version": 1,
        "trace": trace.to_record(),
        "candidates": [candidate.to_record() for candidate in candidates],
        "unique_test_behavior": len(candidates) == 1,
    }


__all__ = [
    "DEFAULT_LIMITS",
    "EXPECTED_BLOCK6_BANK_ID",
    "EXPECTED_BLOCK8_BANK_ID",
    "EXPECTED_BLOCK9_BANK_ID",
    "compile_programs",
    "compile_record",
    "execute_candidates",
    "execute_program",
    "expand_matching_promoted_macro",
    "verify_program_authorization",
]
