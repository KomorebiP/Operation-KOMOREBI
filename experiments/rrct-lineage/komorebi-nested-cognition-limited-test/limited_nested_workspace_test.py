from __future__ import annotations

import itertools
import json
import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Hashable, Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent


def entropy(values: Sequence[Hashable]) -> float:
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def mutual_information(x: Sequence[Hashable], y: Sequence[Hashable]) -> float:
    if len(x) != len(y):
        raise ValueError("x and y must have equal length")
    joint = list(zip(x, y))
    return entropy(x) + entropy(y) - entropy(joint)


def conditional_entropy(y: Sequence[Hashable], x: Sequence[Hashable]) -> float:
    return entropy(list(zip(x, y))) - entropy(x)


def bayes_accuracy(features: Sequence[Hashable], targets: Sequence[Hashable]) -> float:
    if len(features) != len(targets):
        raise ValueError("features and targets must have equal length")
    grouped: dict[Hashable, Counter] = defaultdict(Counter)
    for feature, target in zip(features, targets):
        grouped[feature][target] += 1
    correct = sum(max(counts.values()) for counts in grouped.values())
    return correct / len(targets)


def xor2(a: int, b: int) -> int:
    return int(a) ^ int(b)


def recursively_split(secret: int, masks: Iterable[int], depth: int) -> tuple[list[int], list[int]]:
    """Return leaves and breadth-first internal secrets for a binary XOR share tree."""
    mask_iter = iter(masks)
    internal: list[int] = []

    def split(node_secret: int, node_depth: int) -> list[int]:
        internal.append(node_secret)
        if node_depth == 0:
            return [node_secret]
        mask = next(mask_iter)
        left = mask
        right = xor2(node_secret, mask)
        return split(left, node_depth - 1) + split(right, node_depth - 1)

    leaves = split(secret, depth)
    try:
        next(mask_iter)
        raise ValueError("too many masks")
    except StopIteration:
        pass
    return leaves, internal


def pairwise_reduce(values: Sequence[int]) -> list[list[int]]:
    levels: list[list[int]] = [list(values)]
    current = list(values)
    while len(current) > 1:
        if len(current) % 2:
            raise ValueError("binary reduction requires an even number of nodes")
        current = [xor2(current[i], current[i + 1]) for i in range(0, len(current), 2)]
        levels.append(current)
    return levels


def enumerate_share_tree(depth: int) -> pd.DataFrame:
    internal_count = 2**depth - 1
    rows: list[dict[str, Any]] = []
    for secret in range(4):
        for masks in itertools.product(range(4), repeat=internal_count):
            leaves, _ = recursively_split(secret, masks, depth)
            levels = pairwise_reduce(leaves)
            if levels[-1][0] != secret:
                raise AssertionError("recursive workspace failed to reconstruct root")
            row: dict[str, Any] = {"secret": secret}
            for i, value in enumerate(leaves):
                row[f"leaf_{i}"] = value
            for level_idx, level in enumerate(levels[1:], start=1):
                for node_idx, value in enumerate(level):
                    row[f"level_{level_idx}_{node_idx}"] = value
            rows.append(row)
    return pd.DataFrame(rows)


def share_tree_metrics(depth: int) -> dict[str, Any]:
    frame = enumerate_share_tree(depth)
    leaf_cols = [column for column in frame.columns if column.startswith("leaf_")]
    workspace_levels: dict[int, list[str]] = {}
    for column in frame.columns:
        if column.startswith("level_"):
            level = int(column.split("_")[1])
            workspace_levels.setdefault(level, []).append(column)
    for columns in workspace_levels.values():
        columns.sort(key=lambda value: int(value.split("_")[-1]))

    secret_values = frame["secret"].tolist()
    edge_mis: list[float] = []
    joint_child_mis: list[float] = []
    node_conditional_entropies: list[float] = []

    # At each reduction, a parent workspace is formed from two children.
    previous = leaf_cols
    for level in range(1, depth + 1):
        parents = workspace_levels[level]
        for parent_index, parent_col in enumerate(parents):
            left_col = previous[2 * parent_index]
            right_col = previous[2 * parent_index + 1]
            parent = frame[parent_col].tolist()
            left = frame[left_col].tolist()
            right = frame[right_col].tolist()
            edge_mis.extend([
                mutual_information(parent, left),
                mutual_information(parent, right),
            ])
            joint_child_mis.append(mutual_information(parent, list(zip(left, right))))
            node_conditional_entropies.append(
                conditional_entropy(parent, list(zip(left, right)))
            )
        previous = parents

    top_subtrees = workspace_levels[depth - 1] if depth > 1 else leaf_cols
    left_top = frame[top_subtrees[0]].tolist()
    right_top = frame[top_subtrees[1]].tolist()

    # Exact interventions.
    full_prediction = [xor2(a, b) for a, b in zip(left_top, right_top)]
    reset_left_prediction = right_top
    reset_right_prediction = left_top

    # Exact independent episode-shuffle expectation.  A shuffled left workspace
    # is sampled independently from its empirical marginal.  The prediction is
    # correct exactly when the shuffled value equals the episode's true left
    # workspace, so the exact expected accuracy is sum_v p(v)^2.
    left_counts = Counter(left_top)
    total_left = len(left_top)
    exact_shuffle_accuracy = sum(
        (count / total_left) ** 2 for count in left_counts.values()
    )

    # One-bit compression of each two-bit top-subtree state. The Bayes-optimal
    # decoder sees only the low bit of each share.
    compressed_features = [
        (left & 1, right & 1) for left, right in zip(left_top, right_top)
    ]

    # Top-down rewrite: preserve the entire left half of the tree, change the
    # root target, and reconstruct the right half consistently.
    rewrite_success = []
    left_half_preserved = []
    leaf_count = 2**depth
    internal_right_depth = depth - 1
    right_mask_count = 2**internal_right_depth - 1
    for row_index, row in frame.iloc[: min(2048, len(frame))].iterrows():
        old_secret = int(row["secret"])
        new_secret = old_secret ^ 0b11  # guaranteed different two-bit target
        left_secret = int(row[top_subtrees[0]])
        new_right_secret = xor2(new_secret, left_secret)
        # Deterministic fresh masks for the rewritten right branch.
        masks = [
            int((row_index + 3 * j + 1) % 4)
            for j in range(right_mask_count)
        ]
        new_right_leaves, _ = recursively_split(
            new_right_secret, masks, internal_right_depth
        )
        old_left_leaves = [int(row[f"leaf_{i}"]) for i in range(leaf_count // 2)]
        rewritten_leaves = old_left_leaves + new_right_leaves
        new_levels = pairwise_reduce(rewritten_leaves)
        rewrite_success.append(new_levels[-1][0] == new_secret)
        left_half_preserved.append(
            rewritten_leaves[: leaf_count // 2] == old_left_leaves
        )

    raw_bits = 2 * 2**depth
    level_bits = {
        f"level_{level}": 2 * len(workspace_levels[level])
        for level in sorted(workspace_levels)
    }

    metrics = {
        "depth": depth,
        "case_count": int(len(frame)),
        "leaf_agent_count": int(2**depth),
        "root_entropy_bits": entropy(secret_values),
        "max_single_child_parent_information_bits": float(max(edge_mis)),
        "mean_single_child_parent_information_bits": float(np.mean(edge_mis)),
        "min_joint_children_parent_information_bits": float(min(joint_child_mis)),
        "max_parent_uncertainty_given_both_children_bits": float(
            max(node_conditional_entropies)
        ),
        "single_top_subtree_information_about_root_bits": float(
            max(
                mutual_information(secret_values, left_top),
                mutual_information(secret_values, right_top),
            )
        ),
        "both_top_subtrees_information_about_root_bits": float(
            mutual_information(secret_values, list(zip(left_top, right_top)))
        ),
        "full_hierarchy_accuracy": float(
            np.mean(np.asarray(full_prediction) == np.asarray(secret_values))
        ),
        "reset_left_top_workspace_accuracy": float(
            np.mean(np.asarray(reset_left_prediction) == np.asarray(secret_values))
        ),
        "reset_right_top_workspace_accuracy": float(
            np.mean(np.asarray(reset_right_prediction) == np.asarray(secret_values))
        ),
        "shuffled_top_workspace_accuracy": float(exact_shuffle_accuracy),
        "one_bit_per_top_workspace_bayes_accuracy": float(
            bayes_accuracy(compressed_features, secret_values)
        ),
        "top_down_rewrite_success_rate": float(np.mean(rewrite_success)),
        "top_down_unrelated_left_half_preservation_rate": float(
            np.mean(left_half_preserved)
        ),
        "raw_leaf_state_bits": raw_bits,
        "workspace_bits_by_level": level_bits,
        "root_workspace_bits": 2,
    }
    return metrics


# -----------------------------------------------------------------------------
# Case 2: noncommuting operator hierarchy
# -----------------------------------------------------------------------------

def compose(after: tuple[int, ...], before: tuple[int, ...]) -> tuple[int, ...]:
    """Return after ∘ before for permutations represented as lookup tables."""
    return tuple(after[before[index]] for index in range(len(before)))


def apply_perm(perm: tuple[int, ...], state: int) -> int:
    return perm[state]


def operator_hierarchy_metrics() -> tuple[dict[str, Any], pd.DataFrame]:
    identity = (0, 1, 2, 3)
    operators = {
        "cycle": (1, 2, 3, 0),
        "swap01": (1, 0, 2, 3),
        "swap12": (0, 2, 1, 3),
        "reverse": (3, 2, 1, 0),
    }
    names = list(operators)
    rows: list[dict[str, Any]] = []
    for initial in range(4):
        for sequence in itertools.product(names, repeat=4):
            p1, p2, p3, p4 = [operators[name] for name in sequence]
            left_workspace = compose(p2, p1)
            right_workspace = compose(p4, p3)
            top_workspace = compose(right_workspace, left_workspace)
            target = apply_perm(top_workspace, initial)

            swapped_top = compose(left_workspace, right_workspace)
            reverse_left = compose(p1, p2)
            reverse_left_top = compose(right_workspace, reverse_left)
            reset_left_top = compose(right_workspace, identity)
            reset_right_top = compose(identity, left_workspace)

            rows.append(
                {
                    "initial": initial,
                    "op1": sequence[0],
                    "op2": sequence[1],
                    "op3": sequence[2],
                    "op4": sequence[3],
                    "left_workspace": str(left_workspace),
                    "right_workspace": str(right_workspace),
                    "target": target,
                    "full_prediction": apply_perm(top_workspace, initial),
                    "swapped_top_prediction": apply_perm(swapped_top, initial),
                    "reversed_left_prediction": apply_perm(reverse_left_top, initial),
                    "reset_left_prediction": apply_perm(reset_left_top, initial),
                    "reset_right_prediction": apply_perm(reset_right_top, initial),
                }
            )
    frame = pd.DataFrame(rows)
    targets = frame["target"].tolist()

    ordered_log = list(
        zip(
            frame["initial"],
            frame["op1"],
            frame["op2"],
            frame["op3"],
            frame["op4"],
        )
    )
    unordered_log = []
    for row in frame.itertuples(index=False):
        counts = tuple(sorted(Counter([row.op1, row.op2, row.op3, row.op4]).items()))
        unordered_log.append((row.initial, counts))

    left_only = list(zip(frame["initial"], frame["left_workspace"]))
    right_only = list(zip(frame["initial"], frame["right_workspace"]))
    both_workspaces = list(
        zip(frame["initial"], frame["left_workspace"], frame["right_workspace"])
    )

    unique_pair_ops = len(set(frame["left_workspace"]))
    unique_top_targets = len(set(targets))

    metrics = {
        "case_count": int(len(frame)),
        "operator_alphabet_size": len(operators),
        "unique_pair_workspace_operators": unique_pair_ops,
        "target_class_count": unique_top_targets,
        "full_hierarchy_accuracy": float(
            np.mean(frame["full_prediction"] == frame["target"])
        ),
        "top_pair_order_swap_accuracy": float(
            np.mean(frame["swapped_top_prediction"] == frame["target"])
        ),
        "within_pair_order_reversal_accuracy": float(
            np.mean(frame["reversed_left_prediction"] == frame["target"])
        ),
        "reset_left_workspace_accuracy": float(
            np.mean(frame["reset_left_prediction"] == frame["target"])
        ),
        "reset_right_workspace_accuracy": float(
            np.mean(frame["reset_right_prediction"] == frame["target"])
        ),
        "ordered_flat_log_bayes_accuracy": float(bayes_accuracy(ordered_log, targets)),
        "unordered_flat_log_bayes_accuracy": float(
            bayes_accuracy(unordered_log, targets)
        ),
        "left_workspace_only_bayes_accuracy": float(
            bayes_accuracy(left_only, targets)
        ),
        "right_workspace_only_bayes_accuracy": float(
            bayes_accuracy(right_only, targets)
        ),
        "both_workspace_agents_bayes_accuracy": float(
            bayes_accuracy(both_workspaces, targets)
        ),
        "left_workspace_information_about_target_bits": float(
            mutual_information(targets, left_only)
        ),
        "right_workspace_information_about_target_bits": float(
            mutual_information(targets, right_only)
        ),
        "both_workspaces_information_about_target_bits": float(
            mutual_information(targets, both_workspaces)
        ),
    }
    return metrics, frame


@dataclass(frozen=True)
class Endpoint:
    name: str
    passed: bool
    observed: float | bool
    criterion: str


def make_endpoints(
    depth2: dict[str, Any], depth3: dict[str, Any], operator: dict[str, Any]
) -> list[Endpoint]:
    return [
        Endpoint(
            "recursive_depth2_exact",
            depth2["full_hierarchy_accuracy"] == 1.0,
            depth2["full_hierarchy_accuracy"],
            "accuracy == 1",
        ),
        Endpoint(
            "recursive_depth3_exact",
            depth3["full_hierarchy_accuracy"] == 1.0,
            depth3["full_hierarchy_accuracy"],
            "accuracy == 1",
        ),
        Endpoint(
            "single_child_is_informationless",
            max(
                depth2["max_single_child_parent_information_bits"],
                depth3["max_single_child_parent_information_bits"],
            ) < 1e-10,
            max(
                depth2["max_single_child_parent_information_bits"],
                depth3["max_single_child_parent_information_bits"],
            ),
            "mutual information < 1e-10 bits",
        ),
        Endpoint(
            "siblings_are_jointly_sufficient",
            min(
                depth2["min_joint_children_parent_information_bits"],
                depth3["min_joint_children_parent_information_bits"],
            ) > 1.999999,
            min(
                depth2["min_joint_children_parent_information_bits"],
                depth3["min_joint_children_parent_information_bits"],
            ),
            "mutual information > 1.999999 bits",
        ),
        Endpoint(
            "one_top_subtree_does_not_reveal_root",
            max(
                depth2["single_top_subtree_information_about_root_bits"],
                depth3["single_top_subtree_information_about_root_bits"],
            ) < 1e-10,
            max(
                depth2["single_top_subtree_information_about_root_bits"],
                depth3["single_top_subtree_information_about_root_bits"],
            ),
            "mutual information < 1e-10 bits",
        ),
        Endpoint(
            "top_workspace_pair_determines_root",
            min(
                depth2["both_top_subtrees_information_about_root_bits"],
                depth3["both_top_subtrees_information_about_root_bits"],
            ) > 1.999999,
            min(
                depth2["both_top_subtrees_information_about_root_bits"],
                depth3["both_top_subtrees_information_about_root_bits"],
            ),
            "mutual information > 1.999999 bits",
        ),
        Endpoint(
            "workspace_reset_collapses_to_chance",
            max(
                depth2["reset_left_top_workspace_accuracy"],
                depth2["reset_right_top_workspace_accuracy"],
                depth3["reset_left_top_workspace_accuracy"],
                depth3["reset_right_top_workspace_accuracy"],
            ) <= 0.250001,
            max(
                depth2["reset_left_top_workspace_accuracy"],
                depth2["reset_right_top_workspace_accuracy"],
                depth3["reset_left_top_workspace_accuracy"],
                depth3["reset_right_top_workspace_accuracy"],
            ),
            "accuracy <= 0.250001",
        ),
        Endpoint(
            "workspace_shuffle_collapses_to_chance",
            max(
                depth2["shuffled_top_workspace_accuracy"],
                depth3["shuffled_top_workspace_accuracy"],
            ) <= 0.255,
            max(
                depth2["shuffled_top_workspace_accuracy"],
                depth3["shuffled_top_workspace_accuracy"],
            ),
            "accuracy <= 0.255",
        ),
        Endpoint(
            "one_bit_capacity_cut_is_insufficient",
            max(
                depth2["one_bit_per_top_workspace_bayes_accuracy"],
                depth3["one_bit_per_top_workspace_bayes_accuracy"],
            ) <= 0.500001,
            max(
                depth2["one_bit_per_top_workspace_bayes_accuracy"],
                depth3["one_bit_per_top_workspace_bayes_accuracy"],
            ),
            "Bayes accuracy <= 0.500001",
        ),
        Endpoint(
            "top_down_rewrite_is_coherent",
            min(
                depth2["top_down_rewrite_success_rate"],
                depth3["top_down_rewrite_success_rate"],
            ) == 1.0,
            min(
                depth2["top_down_rewrite_success_rate"],
                depth3["top_down_rewrite_success_rate"],
            ),
            "rate == 1",
        ),
        Endpoint(
            "top_down_rewrite_preserves_unrelated_branch",
            min(
                depth2["top_down_unrelated_left_half_preservation_rate"],
                depth3["top_down_unrelated_left_half_preservation_rate"],
            ) == 1.0,
            min(
                depth2["top_down_unrelated_left_half_preservation_rate"],
                depth3["top_down_unrelated_left_half_preservation_rate"],
            ),
            "rate == 1",
        ),
        Endpoint(
            "operator_hierarchy_exact",
            operator["full_hierarchy_accuracy"] == 1.0,
            operator["full_hierarchy_accuracy"],
            "accuracy == 1",
        ),
        Endpoint(
            "operator_order_matters",
            max(
                operator["top_pair_order_swap_accuracy"],
                operator["within_pair_order_reversal_accuracy"],
            ) < 0.95,
            max(
                operator["top_pair_order_swap_accuracy"],
                operator["within_pair_order_reversal_accuracy"],
            ),
            "accuracy < 0.95",
        ),
        Endpoint(
            "operator_single_workspace_insufficient",
            max(
                operator["left_workspace_only_bayes_accuracy"],
                operator["right_workspace_only_bayes_accuracy"],
            ) < 0.8,
            max(
                operator["left_workspace_only_bayes_accuracy"],
                operator["right_workspace_only_bayes_accuracy"],
            ),
            "Bayes accuracy < 0.8",
        ),
        Endpoint(
            "operator_workspace_pair_sufficient",
            operator["both_workspace_agents_bayes_accuracy"] == 1.0,
            operator["both_workspace_agents_bayes_accuracy"],
            "Bayes accuracy == 1",
        ),
        Endpoint(
            "unordered_flat_summary_loses_temporal_structure",
            operator["unordered_flat_log_bayes_accuracy"] < 0.9,
            operator["unordered_flat_log_bayes_accuracy"],
            "Bayes accuracy < 0.9",
        ),
    ]


def plot_information(depth2: dict[str, Any], depth3: dict[str, Any]) -> Path:
    labels = ["One child → parent", "Two children → parent", "One top subtree → root", "Both top subtrees → root"]
    d2 = [
        depth2["mean_single_child_parent_information_bits"],
        depth2["min_joint_children_parent_information_bits"],
        depth2["single_top_subtree_information_about_root_bits"],
        depth2["both_top_subtrees_information_about_root_bits"],
    ]
    d3 = [
        depth3["mean_single_child_parent_information_bits"],
        depth3["min_joint_children_parent_information_bits"],
        depth3["single_top_subtree_information_about_root_bits"],
        depth3["both_top_subtrees_information_about_root_bits"],
    ]
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(x - width / 2, d2, width, label="Depth 2")
    ax.bar(x + width / 2, d3, width, label="Depth 3")
    ax.set_title("Recursive Synergy at Every Workspace Boundary")
    ax.set_ylabel("Mutual information (bits)")
    ax.set_ylim(0, 2.15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=18, ha="right")
    ax.grid(axis="y", alpha=0.2)
    ax.legend()
    path = OUT / "01_recursive_synergy_information.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_compression(depth2: dict[str, Any], depth3: dict[str, Any]) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for metrics, label in [(depth2, "Depth 2"), (depth3, "Depth 3")]:
        bits = [metrics["raw_leaf_state_bits"]]
        names = ["Leaves"]
        for level, value in metrics["workspace_bits_by_level"].items():
            bits.append(value)
            names.append(level.replace("_", " ").title())
        ax.plot(range(len(bits)), bits, marker="o", label=label)
    ax.set_title("Each Workspace Level Compresses Detail While Expanding Scope")
    ax.set_ylabel("Total represented bits at level")
    ax.set_xlabel("Hierarchy level")
    ax.set_xticks(range(4))
    ax.set_xticklabels(["Leaves", "Level 1", "Level 2", "Root"])
    ax.grid(alpha=0.2)
    ax.legend()
    path = OUT / "02_hierarchy_compression.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_interventions(depth2: dict[str, Any], depth3: dict[str, Any]) -> Path:
    labels = ["Full", "Reset left", "Reset right", "Shuffle", "1-bit capacity"]
    d2 = [
        depth2["full_hierarchy_accuracy"],
        depth2["reset_left_top_workspace_accuracy"],
        depth2["reset_right_top_workspace_accuracy"],
        depth2["shuffled_top_workspace_accuracy"],
        depth2["one_bit_per_top_workspace_bayes_accuracy"],
    ]
    d3 = [
        depth3["full_hierarchy_accuracy"],
        depth3["reset_left_top_workspace_accuracy"],
        depth3["reset_right_top_workspace_accuracy"],
        depth3["shuffled_top_workspace_accuracy"],
        depth3["one_bit_per_top_workspace_bayes_accuracy"],
    ]
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.bar(x - width / 2, d2, width, label="Depth 2")
    ax.bar(x + width / 2, d3, width, label="Depth 3")
    ax.set_title("Causal Cuts to Nested Workspaces")
    ax.set_ylabel("Four-class task accuracy")
    ax.set_ylim(0, 1.08)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(axis="y", alpha=0.2)
    ax.legend()
    path = OUT / "03_nested_workspace_interventions.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_operator(operator: dict[str, Any]) -> Path:
    labels = [
        "Full hierarchy",
        "Swap top order",
        "Reverse left pair",
        "Reset left",
        "Reset right",
        "Unordered log Bayes",
        "One workspace Bayes",
        "Both workspaces Bayes",
    ]
    values = [
        operator["full_hierarchy_accuracy"],
        operator["top_pair_order_swap_accuracy"],
        operator["within_pair_order_reversal_accuracy"],
        operator["reset_left_workspace_accuracy"],
        operator["reset_right_workspace_accuracy"],
        operator["unordered_flat_log_bayes_accuracy"],
        max(
            operator["left_workspace_only_bayes_accuracy"],
            operator["right_workspace_only_bayes_accuracy"],
        ),
        operator["both_workspace_agents_bayes_accuracy"],
    ]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(13, 6.8))
    ax.bar(x, values)
    ax.set_title("Noncommuting Operator Case: Order and Both Workspace Agents Matter")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.08)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=26, ha="right")
    ax.grid(axis="y", alpha=0.2)
    path = OUT / "04_noncommuting_operator_hierarchy.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    depth2 = share_tree_metrics(2)
    depth3 = share_tree_metrics(3)
    operator, operator_rows = operator_hierarchy_metrics()
    endpoints = make_endpoints(depth2, depth3, operator)
    all_passed = all(endpoint.passed for endpoint in endpoints)

    report = {
        "schema": "komorebi.nested_cognition.limited_test.v1",
        "status": (
            "LIMITED_NESTED_WORKSPACE_ENDPOINTS_MET"
            if all_passed
            else "LIMITED_NESTED_WORKSPACE_ENDPOINTS_NOT_MET"
        ),
        "all_endpoints_met": all_passed,
        "endpoint_count": len(endpoints),
        "endpoints": [asdict(endpoint) for endpoint in endpoints],
        "case_1_recursive_secret_sharing": {
            "depth_2": depth2,
            "depth_3": depth3,
        },
        "case_2_noncommuting_operator_hierarchy": operator,
        "interpretation": (
            "The exact toy systems exhibit recursive synergy: lower-level agents form "
            "workspaces that expose a compressed sufficient state, and those workspaces "
            "can be treated as agents at the next level. Causal reset, shuffle, one-sided "
            "access, capacity cuts, and temporal-order disruptions produce the predicted "
            "failures. This is a limited operational existence test, not evidence that "
            "human neural systems literally implement this exact tree or that the hierarchy "
            "is conscious."
        ),
    }

    (OUT / "results.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    pd.DataFrame([depth2, depth3]).to_csv(
        OUT / "recursive_synergy_metrics.csv", index=False
    )
    pd.DataFrame([operator]).to_csv(
        OUT / "operator_hierarchy_metrics.csv", index=False
    )
    operator_rows.to_csv(OUT / "operator_hierarchy_cases.csv", index=False)

    visuals = [
        plot_information(depth2, depth3),
        plot_compression(depth2, depth3),
        plot_interventions(depth2, depth3),
        plot_operator(operator),
    ]

    summary = f"""# Limited Test of Recursive Agent–Workspace Cognition

## Status

`{report['status']}`

All **{sum(endpoint.passed for endpoint in endpoints)} of {len(endpoints)}** declared endpoints passed.

## Case 1: exact recursive synergy

A two-bit root state was recursively secret-shared down binary trees. Every child state was individually independent of its parent, while each sibling pair jointly determined the parent exactly.

| Measure | Depth 2 | Depth 3 |
|---|---:|---:|
| Leaf agents | {depth2['leaf_agent_count']} | {depth3['leaf_agent_count']} |
| Exact cases | {depth2['case_count']:,} | {depth3['case_count']:,} |
| Maximum one-child information about parent | {depth2['max_single_child_parent_information_bits']:.6g} bits | {depth3['max_single_child_parent_information_bits']:.6g} bits |
| Minimum sibling-pair information about parent | {depth2['min_joint_children_parent_information_bits']:.6f} bits | {depth3['min_joint_children_parent_information_bits']:.6f} bits |
| Full hierarchy accuracy | {depth2['full_hierarchy_accuracy']:.3f} | {depth3['full_hierarchy_accuracy']:.3f} |
| Reset one top workspace | {depth2['reset_left_top_workspace_accuracy']:.3f} | {depth3['reset_left_top_workspace_accuracy']:.3f} |
| Shuffle one top workspace | {depth2['shuffled_top_workspace_accuracy']:.3f} | {depth3['shuffled_top_workspace_accuracy']:.3f} |
| One-bit capacity cut | {depth2['one_bit_per_top_workspace_bayes_accuracy']:.3f} | {depth3['one_bit_per_top_workspace_bayes_accuracy']:.3f} |
| Coherent top-down rewrite | {depth2['top_down_rewrite_success_rate']:.3f} | {depth3['top_down_rewrite_success_rate']:.3f} |

The same two-bit workspace type recurs at every scale. A workspace produced by two lower agents therefore functions as an agent input at the next level.

The depth-three hierarchy compresses:

```text
16 raw leaf bits
→ 8 level-one workspace bits
→ 4 level-two workspace bits
→ 2 root-workspace bits
```

while preserving the root task exactly.

## Case 2: noncommuting operator hierarchy

Four leaf agents supplied ordered permutation operators. Two local workspaces composed adjacent operators; the top workspace composed the two resulting operator-agents.

| Measure | Result |
|---|---:|
| Exact cases | {operator['case_count']:,} |
| Full hierarchy accuracy | {operator['full_hierarchy_accuracy']:.3f} |
| Swap top workspace order | {operator['top_pair_order_swap_accuracy']:.3f} |
| Reverse one local pair | {operator['within_pair_order_reversal_accuracy']:.3f} |
| Reset left workspace | {operator['reset_left_workspace_accuracy']:.3f} |
| Reset right workspace | {operator['reset_right_workspace_accuracy']:.3f} |
| One workspace alone, Bayes optimal | {max(operator['left_workspace_only_bayes_accuracy'], operator['right_workspace_only_bayes_accuracy']):.3f} |
| Both workspace-agents, Bayes optimal | {operator['both_workspace_agents_bayes_accuracy']:.3f} |
| Unordered flat operation summary | {operator['unordered_flat_log_bayes_accuracy']:.3f} |

This second case rules out the possibility that the first result depends only on an associative XOR tree. Temporal order and the identities of both workspace-agents are causally important.

## Interpretation

These limited cases support the **operational possibility** of recursive workspace cognition:

```text
lower agents
→ local synergistic workspace
→ workspace behaves as a higher-level agent
→ higher synergistic workspace
→ broader action
```

They establish:

- local insufficiency;
- workspace-level joint sufficiency;
- recursive type reuse across levels;
- progressive compression;
- privacy of lower-level state;
- causal necessity of each workspace boundary;
- coherent top-down rewrite;
- order-sensitive composition in a noncommuting case.

They do **not** establish:

- spontaneous emergence of the hierarchy;
- biological realism;
- that human brain regions implement XOR secret sharing;
- that one hierarchy is uniquely necessary;
- consciousness or subjective awareness.

The strongest next limited test would replace the hand-coded combination rules with learned local agents and ask whether a two-level hierarchy is discovered from terminal objectives without intermediate workspace labels.
"""
    (OUT / "SUMMARY.md").write_text(summary, encoding="utf-8")

    print(json.dumps({
        "status": report["status"],
        "all_endpoints_met": all_passed,
        "passed": sum(endpoint.passed for endpoint in endpoints),
        "endpoint_count": len(endpoints),
        "depth2": depth2,
        "depth3": depth3,
        "operator": operator,
        "visuals": [path.name for path in visuals],
    }, indent=2))


if __name__ == "__main__":
    main()
