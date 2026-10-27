from __future__ import annotations

import math
from typing import Any


def _confusion(predicted: Any, target: Any, classes: int) -> Any:
    import torch

    if (
        predicted.ndim != 1
        or target.ndim != 1
        or predicted.shape[0] != target.shape[0]
        or predicted.shape[0] == 0
    ):
        raise ValueError("predictions and targets must be aligned nonempty vectors")
    if any(
        int(value.min()) < 0 or int(value.max()) >= int(classes)
        for value in (predicted, target)
    ):
        raise ValueError("predictions or targets are outside the class range")
    result = torch.zeros((classes, classes), dtype=torch.long)
    for truth, guess in zip(target.tolist(), predicted.tolist()):
        result[int(truth), int(guess)] += 1
    return result


def _metrics(predicted: Any, target: Any, classes: int) -> dict[str, Any]:
    matrix = _confusion(predicted, target, classes)
    total = int(matrix.sum().item())
    accuracy = float(matrix.diag().sum().item() / total)
    recalls = []
    f1_values = []
    for value in range(classes):
        true_positive = int(matrix[value, value])
        false_negative = int(matrix[value, :].sum()) - true_positive
        false_positive = int(matrix[:, value].sum()) - true_positive
        recall_denominator = true_positive + false_negative
        precision_denominator = true_positive + false_positive
        recall = true_positive / recall_denominator if recall_denominator else 0.0
        precision = true_positive / precision_denominator if precision_denominator else 0.0
        recalls.append(recall)
        f1_values.append(
            2.0 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
    z = 2.5758293035489004
    denominator = 1.0 + z * z / total
    center = (accuracy + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * math.sqrt(
            accuracy * (1.0 - accuracy) / total + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return {
        "count": total,
        "accuracy": accuracy,
        "balanced_accuracy": sum(recalls) / classes,
        "macro_f1": sum(f1_values) / classes,
        "accuracy_wilson_99pct": [max(0.0, center - radius), min(1.0, center + radius)],
        "confusion_matrix_rows_truth_columns_prediction": matrix.tolist(),
    }


def _standardize(train: Any, *others: Any) -> tuple[Any, ...]:
    mean = train.mean(dim=0, keepdim=True)
    scale = train.std(dim=0, unbiased=False, keepdim=True).clamp_min(1e-5)
    return tuple((value - mean) / scale for value in (train, *others))


def _augment(features: Any) -> Any:
    import torch

    return torch.cat(
        (features, torch.ones((features.shape[0], 1), dtype=features.dtype)), dim=1
    )


def _ridge_operator(train: Any, evaluation: Any, regularization: float) -> Any:
    import torch

    x = _augment(train)
    z = _augment(evaluation)
    rows, columns = x.shape
    if columns <= rows:
        identity = torch.eye(columns, dtype=x.dtype)
        solution = torch.linalg.solve(
            x.T @ x + float(regularization) * identity, x.T
        )
        return z @ solution
    identity = torch.eye(rows, dtype=x.dtype)
    return (z @ x.T) @ torch.linalg.solve(
        x @ x.T + float(regularization) * identity,
        torch.eye(rows, dtype=x.dtype),
    )


def _one_hot(labels: Any, classes: int) -> Any:
    import torch

    return torch.nn.functional.one_hot(labels.long(), num_classes=classes).double()


def _nearest_centroid(train: Any, train_labels: Any, evaluation: Any, classes: int) -> Any:
    import torch

    centroids = torch.stack([train[train_labels == value].mean(dim=0) for value in range(classes)])
    return torch.cdist(evaluation, centroids).argmin(dim=1)


def _knn(train: Any, train_labels: Any, evaluation: Any, classes: int, k: int = 5) -> Any:
    import torch

    neighbors = torch.cdist(evaluation, train).topk(k, largest=False).indices
    labels = train_labels[neighbors]
    counts = torch.nn.functional.one_hot(labels, num_classes=classes).sum(dim=1)
    return counts.argmax(dim=1)


def diagnostic_probe(
    train_features: Any,
    validation_features: Any,
    iid_features: Any,
    ood_features: Any,
    train_labels: Any,
    validation_labels: Any,
    iid_labels: Any,
    ood_labels: Any,
    *,
    classes: int,
    permutation_count: int = 127,
    seed: int = 94017,
) -> dict[str, Any]:
    import torch

    if isinstance(classes, bool) or int(classes) < 2:
        raise ValueError("probe requires at least two classes")
    if isinstance(permutation_count, bool) or int(permutation_count) < 1:
        raise ValueError("probe permutation_count must be positive")
    raw_features = (
        train_features,
        validation_features,
        iid_features,
        ood_features,
    )
    raw_labels = (train_labels, validation_labels, iid_labels, ood_labels)
    if any(
        not torch.is_tensor(value)
        or value.ndim != 2
        or value.shape[0] == 0
        or not bool(torch.isfinite(value).all().item())
        for value in raw_features
    ):
        raise ValueError("probe features must be finite nonempty matrices")
    if any(value.shape[1] != raw_features[0].shape[1] for value in raw_features):
        raise ValueError("probe feature widths are not aligned")
    if any(
        not torch.is_tensor(value)
        or value.ndim != 1
        or value.shape[0] != features.shape[0]
        or value.shape[0] == 0
        for features, value in zip(raw_features, raw_labels)
    ):
        raise ValueError("probe labels must be aligned nonempty vectors")
    if any(
        torch.is_floating_point(value) or value.dtype == torch.bool
        for value in raw_labels
    ):
        raise ValueError("probe labels must use an integer tensor dtype")
    if raw_features[0].shape[0] < 5:
        raise ValueError("probe training split is too small for five-neighbor analysis")
    expected_classes = set(range(int(classes)))
    if any(
        set(int(item) for item in value.detach().cpu().tolist()) != expected_classes
        for value in raw_labels
    ):
        raise ValueError("every probe split must cover every registered class")
    feature_values = [
        value.detach().cpu().double()
        for value in (
            train_features,
            validation_features,
            iid_features,
            ood_features,
        )
    ]
    labels = [
        value.detach().cpu().long()
        for value in (train_labels, validation_labels, iid_labels, ood_labels)
    ]
    train, validation, iid, ood = _standardize(*feature_values)
    train_y, validation_y, iid_y, ood_y = labels
    if any(int(value.min()) < 0 or int(value.max()) >= classes for value in labels):
        raise ValueError("probe labels are outside the registered class range")

    regularizations = (1e-4, 1e-2, 1.0, 100.0)
    encoded_train = _one_hot(train_y, classes)
    validation_candidates = []
    validation_operators = {}
    iid_operators = {}
    for regularization in regularizations:
        validation_operator = _ridge_operator(train, validation, regularization)
        iid_operator = _ridge_operator(train, iid, regularization)
        validation_operators[regularization] = validation_operator
        iid_operators[regularization] = iid_operator
        predicted = (validation_operator @ encoded_train).argmax(dim=1)
        metrics = _metrics(predicted, validation_y, classes)
        validation_candidates.append(
            {"regularization": regularization, "metrics": metrics}
        )
    selected = max(
        validation_candidates,
        key=lambda item: (
            item["metrics"]["balanced_accuracy"],
            item["metrics"]["macro_f1"],
            -item["regularization"],
        ),
    )
    regularization = float(selected["regularization"])
    ridge_results: dict[str, Any] = {}
    operators: dict[str, Any] = {}
    for name, features, target in (
        ("train", train, train_y),
        ("validation", validation, validation_y),
        ("iid", iid, iid_y),
        ("ood", ood, ood_y),
    ):
        operator = _ridge_operator(train, features, regularization)
        operators[name] = operator
        predicted = (operator @ encoded_train).argmax(dim=1)
        ridge_results[name] = _metrics(predicted, target, classes)

    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    null_balanced_accuracy = []
    null_selected_regularizations = []
    for _ in range(int(permutation_count)):
        permutation = torch.randperm(train_y.shape[0], generator=generator)
        permuted = _one_hot(train_y[permutation], classes)
        null_candidates = []
        for candidate_regularization in regularizations:
            validation_prediction = (
                validation_operators[candidate_regularization] @ permuted
            ).argmax(dim=1)
            validation_metrics = _metrics(
                validation_prediction, validation_y, classes
            )
            null_candidates.append(
                {
                    "regularization": candidate_regularization,
                    "metrics": validation_metrics,
                }
            )
        null_selected = max(
            null_candidates,
            key=lambda item: (
                item["metrics"]["balanced_accuracy"],
                item["metrics"]["macro_f1"],
                -item["regularization"],
            ),
        )
        null_regularization = float(null_selected["regularization"])
        null_selected_regularizations.append(null_regularization)
        predicted = (iid_operators[null_regularization] @ permuted).argmax(dim=1)
        null_balanced_accuracy.append(
            _metrics(predicted, iid_y, classes)["balanced_accuracy"]
        )
    observed = ridge_results["iid"]["balanced_accuracy"]
    permutation_p = (1 + sum(value >= observed for value in null_balanced_accuracy)) / (
        1 + len(null_balanced_accuracy)
    )
    macro_f1 = ridge_results["iid"]["macro_f1"]
    if permutation_p <= 0.01 and observed >= 0.50 and macro_f1 >= 0.45:
        tier = "STRONG_LINEAR"
    elif permutation_p <= 0.05:
        tier = "WEAK_LINEAR"
    else:
        tier = "NO_LINEAR_SIGNAL"

    nonparametric: dict[str, Any] = {}
    for name, features, target in (("iid", iid, iid_y), ("ood", ood, ood_y)):
        centroid_prediction = _nearest_centroid(train, train_y, features, classes)
        knn_prediction = _knn(train, train_y, features, classes, k=5)
        nonparametric[name] = {
            "nearest_centroid": _metrics(centroid_prediction, target, classes),
            "five_nearest_neighbors": _metrics(knn_prediction, target, classes),
        }

    return {
        "classes": int(classes),
        "chance_balanced_accuracy": 1.0 / classes,
        "selected_regularization": regularization,
        "validation_selection": validation_candidates,
        "ridge": ridge_results,
        "nonparametric": nonparametric,
        "permutation_null": {
            "count": len(null_balanced_accuracy),
            "seed": int(seed),
            "p_value": permutation_p,
            "balanced_accuracy_mean": sum(null_balanced_accuracy)
            / len(null_balanced_accuracy),
            "balanced_accuracy_maximum": max(null_balanced_accuracy),
            "balanced_accuracy_values": null_balanced_accuracy,
            "selected_regularization_counts": dict(
                sorted(
                    {
                        str(value): null_selected_regularizations.count(value)
                        for value in regularizations
                    }.items()
                )
            ),
        },
        "tier": tier,
        "scope": "DIAGNOSTIC_ONLY",
    }
