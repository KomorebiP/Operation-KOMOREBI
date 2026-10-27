"""Classical leakage controls for the Micro OSL benchmark."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .metrics import classification_metrics, evaluate_by_split
from .model import text_from_record


try:  # pragma: no cover - dependency availability varies by installation
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    SKLEARN_AVAILABLE = True
except Exception:  # pragma: no cover
    TfidfVectorizer = LogisticRegression = Pipeline = None  # type: ignore[assignment]
    SKLEARN_AVAILABLE = False


def _labels(records: Sequence[Mapping[str, Any]]) -> list[str]:
    return [str(record.get("answer", "")) for record in records]


class MajorityBaseline:
    """Deterministic global or question-conditioned majority predictor."""

    def __init__(self, *, condition_on_question: bool = False) -> None:
        self.condition_on_question = bool(condition_on_question)
        self.global_label: str | None = None
        self.question_labels: dict[str, str] = {}

    @staticmethod
    def _winner(labels: Iterable[str]) -> str:
        counts = Counter(str(label) for label in labels)
        if not counts:
            raise ValueError("Cannot fit a majority baseline on an empty dataset")
        return min(counts, key=lambda label: (-counts[label], label))

    def fit(self, records: Sequence[Mapping[str, Any]]) -> "MajorityBaseline":
        self.global_label = self._winner(_labels(records))
        if self.condition_on_question:
            grouped: dict[str, list[str]] = {}
            for record in records:
                question_key = str(record.get("question_id", record.get("question", "")))
                grouped.setdefault(question_key, []).append(str(record.get("answer", "")))
            self.question_labels = {
                key: self._winner(values) for key, values in sorted(grouped.items())
            }
        return self

    def predict(self, records: Sequence[Mapping[str, Any]]) -> list[str]:
        if self.global_label is None:
            raise RuntimeError("Fit the majority baseline before prediction")
        result = []
        for record in records:
            key = str(record.get("question_id", record.get("question", "")))
            result.append(self.question_labels.get(key, self.global_label))
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition_on_question": self.condition_on_question,
            "global_label": self.global_label,
            "question_labels": dict(sorted(self.question_labels.items())),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "MajorityBaseline":
        model = cls(condition_on_question=bool(payload.get("condition_on_question", False)))
        model.global_label = payload.get("global_label")
        model.question_labels = {
            str(key): str(value) for key, value in payload.get("question_labels", {}).items()
        }
        return model


class TfidfBaseline:
    """Word/character TF-IDF with deterministic logistic regression."""

    def __init__(
        self,
        *,
        max_features: int = 100_000,
        word_ngram_range: tuple[int, int] = (1, 2),
        regularization: float = 1.0,
        seed: int = 17,
        max_iter: int = 1000,
    ) -> None:
        if not SKLEARN_AVAILABLE:
            raise RuntimeError(
                "scikit-learn is not installed. The majority baseline still works; "
                "install scikit-learn to enable the TF-IDF leakage control."
            )
        self.settings = {
            "max_features": int(max_features),
            "word_ngram_range": tuple(int(value) for value in word_ngram_range),
            "regularization": float(regularization),
            "seed": int(seed),
            "max_iter": int(max_iter),
        }
        self.pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=self.settings["word_ngram_range"],
                        max_features=self.settings["max_features"],
                        sublinear_tf=True,
                        strip_accents="unicode",
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        C=self.settings["regularization"],
                        max_iter=self.settings["max_iter"],
                        random_state=self.settings["seed"],
                        solver="saga",
                    ),
                ),
            ]
        )

    def fit(self, records: Sequence[Mapping[str, Any]]) -> "TfidfBaseline":
        if not records:
            raise ValueError("Cannot fit TF-IDF on an empty dataset")
        self.pipeline.fit([text_from_record(record) for record in records], _labels(records))
        return self

    def predict(self, records: Sequence[Mapping[str, Any]]) -> list[str]:
        return [str(value) for value in self.pipeline.predict([text_from_record(r) for r in records])]


def run_baselines(
    train_records: Sequence[Mapping[str, Any]],
    evaluation_records: Sequence[Mapping[str, Any]],
    *,
    include_tfidf: bool = True,
    tfidf_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fit leakage controls and return overall and split-aware metrics."""

    if not train_records or not evaluation_records:
        raise ValueError("Both training and evaluation records are required")
    gold = _labels(evaluation_records)
    models: list[tuple[str, Any]] = [
        ("majority", MajorityBaseline()),
        ("question_majority", MajorityBaseline(condition_on_question=True)),
    ]
    skipped: dict[str, str] = {}
    if include_tfidf:
        if SKLEARN_AVAILABLE:
            models.append(("tfidf", TfidfBaseline(**dict(tfidf_config or {}))))
        else:
            skipped["tfidf"] = "scikit-learn is not installed"
    results: dict[str, Any] = {"models": {}, "skipped": skipped}
    for name, model in models:
        model.fit(train_records)
        predictions = model.predict(evaluation_records)
        results["models"][name] = {
            "overall": classification_metrics(gold, predictions),
            "by_split": evaluate_by_split(evaluation_records, predictions),
            "predictions": predictions,
        }
    return results


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected a JSON object on {path}:{line_number}")
            records.append(value)
    return records


def run_baselines_from_jsonl(
    train_path: str | Path,
    evaluation_path: str | Path,
    *,
    output_path: str | Path | None = None,
    include_tfidf: bool = True,
    tfidf_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result = run_baselines(
        read_jsonl(train_path),
        read_jsonl(evaluation_path),
        include_tfidf=include_tfidf,
        tfidf_config=tfidf_config,
    )
    if output_path is not None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
