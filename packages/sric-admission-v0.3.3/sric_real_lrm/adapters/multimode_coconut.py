from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping
import numpy as np

from .base import LatentReasonerAdapter, UnsupportedAdapterOperation
from ..hashing import sha256_file, sha256_file_set
from ..schemas import TaskRecord, TraceObservation
from ..source_lock import load_source_lock, verify_external_repository


class ExternalDependencyError(RuntimeError):
    pass


def _legacy_cache(cache: Any) -> Any:
    if cache is None:
        return None
    if hasattr(cache, "to_legacy_cache"):
        return cache.to_legacy_cache()
    return cache


def _slice_legacy_cache(cache: Any, end: int) -> list[tuple[Any, Any]] | None:
    legacy = _legacy_cache(cache)
    if legacy is None:
        return None
    try:
        return [(key[:, :, :end, :], value[:, :, :end, :]) for key, value in legacy]
    except Exception as exc:  # pragma: no cover - depends on external Transformers version
        raise ExternalDependencyError(
            "Unsupported past_key_values representation. Use the Transformers version pinned by the external repository."
        ) from exc


class CoconutTraceEngine:
    """Replay-compatible trace engine for the pinned multimode Coconut implementation.

    The engine mirrors the external repository's recurrence but optionally replaces
    each reinjected latent vector with a supplied trace. It supports batch size one,
    which is the external implementation's own generation contract.
    """

    def __init__(self, coconut_model: Any):
        self.coconut = coconut_model
        self.base = coconut_model.base_causallm
        self.embedding = coconut_model.get_embedding()
        self.latent_token_id = int(coconut_model.latent_token_id)

    def run(
        self,
        *,
        input_ids: Any,
        attention_mask: Any,
        position_ids: Any,
        labels: Any,
        override_trace: Any | None = None,
    ) -> tuple[Any, Any, Any]:
        import torch
        from torch.nn import CrossEntropyLoss

        if input_ids.shape[0] != 1:
            raise ValueError("Real pilot currently requires batch size one")
        latent_positions = (input_ids[0] == self.latent_token_id).nonzero(as_tuple=True)[0].tolist()
        inputs_embeds = self.embedding(input_ids).clone()
        if override_trace is not None:
            override = torch.as_tensor(override_trace, device=inputs_embeds.device, dtype=inputs_embeds.dtype)
            expected = (len(latent_positions), inputs_embeds.shape[-1])
            if tuple(override.shape) != expected:
                raise ValueError(f"Expected override trace {expected}, got {tuple(override.shape)}")
        else:
            override = None

        logits_parts: list[Any] = []
        inserted: list[Any] = []
        next_compute_range = (0, latent_positions[0] if latent_positions else input_ids.shape[1])
        kv_cache = None

        for pass_index, latent_position in enumerate(latent_positions):
            start, end = next_compute_range
            if kv_cache is None:
                outputs = self.base(
                    inputs_embeds=inputs_embeds[:, start:end, :],
                    attention_mask=attention_mask[:, start:end],
                    position_ids=position_ids[:, start:end],
                    output_hidden_states=True,
                    use_cache=True,
                )
                hidden_offset = 0
            else:
                outputs = self.base(
                    inputs_embeds=inputs_embeds[:, start:end, :],
                    attention_mask=attention_mask[:, :end],
                    position_ids=position_ids[:, start:end],
                    past_key_values=_slice_legacy_cache(kv_cache, start),
                    output_hidden_states=True,
                    use_cache=True,
                )
                hidden_offset = start
            logits_parts.append(outputs.logits)
            hidden_states = outputs.hidden_states[-1]
            natural = hidden_states[0, latent_position - 1 - hidden_offset, :]
            value = override[pass_index] if override is not None else natural
            inserted.append(value.detach().clone())

            # Avoid in-place modification of a tensor participating in autograd or a view.
            before = inputs_embeds[:, :latent_position, :]
            replacement = value.reshape(1, 1, -1)
            after = inputs_embeds[:, latent_position + 1 :, :]
            inputs_embeds = torch.cat((before, replacement, after), dim=1)
            kv_cache = outputs.past_key_values
            next_end = input_ids.shape[1] if pass_index + 1 >= len(latent_positions) else latent_position + 1
            next_compute_range = (latent_position, next_end)

        start, end = next_compute_range
        outputs = self.base(
            inputs_embeds=inputs_embeds[:, start:end, :],
            attention_mask=attention_mask[:, :end],
            position_ids=position_ids[:, start:end],
            past_key_values=_slice_legacy_cache(kv_cache, start),
            output_hidden_states=True,
            use_cache=True,
        )
        logits_parts.append(outputs.logits)
        logits = torch.cat(logits_parts, dim=-2)
        if logits.shape[1] != input_ids.shape[1]:
            raise RuntimeError(f"Logit length {logits.shape[1]} does not match input length {input_ids.shape[1]}")
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        loss = CrossEntropyLoss(ignore_index=-100)(
            shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1)
        )
        trace = torch.stack(inserted, dim=0) if inserted else inputs_embeds.new_zeros((0, inputs_embeds.shape[-1]))
        return loss, logits, trace


class MultimodeCoconutProntoQAAdapter(LatentReasonerAdapter):
    REPOSITORY = "connordilgren/are-lrms-easily-interpretable"
    PINNED_COMMIT = "32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
    CHECKPOINT_REPO = "connordilgren/gpt2-prontoqa-multimode-coconut"
    CHECKPOINT_REVISION = "4ec759a9f9b8a8e7e1a8d1e3e2d43eef969ac83f"
    CHECKPOINT_FILENAME = "checkpoint_37"
    BASE_MODEL_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"

    def __init__(
        self,
        *,
        external_repo: str | Path,
        checkpoint: str | Path,
        base_model: str = "openai-community/gpt2",
        device: str = "cuda",
        num_latents: int = 6,
        require_pinned_commit: bool = True,
        checkpoint_revision: str = CHECKPOINT_REVISION,
        base_model_revision: str = BASE_MODEL_REVISION,
        source_lock_path: str | Path | None = None,
    ):
        self.external_repo = Path(external_repo).resolve()
        self.checkpoint = Path(checkpoint).resolve()
        self.base_model = str(base_model)
        self.device = device
        self.num_latents = int(num_latents)
        self.require_pinned_commit = require_pinned_commit
        self.checkpoint_revision = str(checkpoint_revision)
        self.base_model_revision = str(base_model_revision)
        self.wrapper: Any | None = None
        self.engine: CoconutTraceEngine | None = None
        self._repo_commit = self._git_commit()
        if require_pinned_commit and self._repo_commit != self.PINNED_COMMIT:
            raise ExternalDependencyError(
                f"External repository commit is {self._repo_commit}; expected {self.PINNED_COMMIT}"
            )
        if not self.checkpoint.is_file():
            raise FileNotFoundError(self.checkpoint)
        lock_file = (
            Path(source_lock_path).resolve()
            if source_lock_path is not None
            else Path(__file__).resolve().parents[2] / "external_source_lock.json"
        )
        source_lock = load_source_lock(lock_file)
        self._source_verification = verify_external_repository(
            self.external_repo,
            source_lock,
            dataset_key="prontoqa_test",
        )
        base_required_files = list(source_lock["base_model"].get("required_files", ()))
        base_path = Path(self.base_model)
        self._fingerprint = {
            "adapter": "MultimodeCoconutProntoQAAdapter",
            "evidence_kind": "real_checkpoint",
            "engineered_positive_control": False,
            "external_repository": self.REPOSITORY,
            "external_commit": self._repo_commit,
            "source_verification_sha256": self._source_verification["verification_sha256"],
            "checkpoint_repo": self.CHECKPOINT_REPO,
            "checkpoint_revision": self.checkpoint_revision,
            "checkpoint_filename": self.checkpoint.name,
            "checkpoint_sha256": sha256_file(self.checkpoint),
            "base_model": self.base_model,
            "base_model_revision": self.base_model_revision,
            "base_model_tree_sha256": (
                sha256_file_set(base_path, base_required_files)
                if base_path.is_dir() and base_required_files
                else None
            ),
            "num_latents": self.num_latents,
            "device": self.device,
        }

    def _git_commit(self) -> str:
        try:
            return subprocess.check_output(
                ["git", "-C", str(self.external_repo), "rev-parse", "HEAD"],
                text=True,
                stderr=subprocess.STDOUT,
            ).strip()
        except Exception as exc:
            raise ExternalDependencyError(f"Cannot read git commit in {self.external_repo}") from exc

    def load(self) -> None:
        if self.wrapper is not None:
            return
        if str(self.external_repo) not in sys.path:
            sys.path.insert(0, str(self.external_repo))
        module = importlib.import_module("models.multimode_coconut.multimode_coconut_model")
        wrapper_class = getattr(module, "MultimodeCoconutModel")
        wrapper = wrapper_class(
            model_path=str(self.checkpoint),
            device=self.device,
            model_id=self.base_model,
            num_latent=self.num_latents,
        )
        wrapper.load()
        self.wrapper = wrapper
        self.engine = CoconutTraceEngine(wrapper.model)

    def _prepare(self, task: TaskRecord, mode: str = "latent") -> tuple[Any, Any, Any, Any, int]:
        import torch
        self.load()
        assert self.wrapper is not None
        if mode not in {"latent", "direct", "verbalized"}:
            raise UnsupportedAdapterOperation(f"Unsupported Coconut mode: {mode}")
        prepared = self.wrapper.prepare_input(
            task.question,
            mode=mode,
            num_latents=self.num_latents,
        )
        prefix_ids = prepared["input_ids"].to(self.device)
        extra_ids: list[int] = []
        if mode == "verbalized":
            reasoning_text = " ".join(task.steps)
            extra_ids.extend(self.wrapper.tokenizer.encode(reasoning_text, add_special_tokens=False))
            extra_ids.append(int(self.wrapper.special_tokens["eocot"]))
        answer_ids = self.wrapper.tokenizer.encode(
            "### " + task.answer,
            add_special_tokens=False,
        ) + [self.wrapper.tokenizer.eos_token_id]
        answer_start = int(prefix_ids.shape[1] + len(extra_ids))
        suffix_tensor = torch.tensor(
            extra_ids + answer_ids,
            dtype=prefix_ids.dtype,
            device=self.device,
        ).reshape(1, -1)
        input_ids = torch.cat((prefix_ids, suffix_tensor), dim=1)
        attention_mask = torch.ones_like(input_ids)
        position_ids = torch.arange(input_ids.shape[1], device=self.device, dtype=torch.long).reshape(1, -1)
        labels = input_ids.clone()
        labels[:, :answer_start] = -100
        return input_ids, attention_mask, position_ids, labels, answer_start

    def _observe(self, task: TaskRecord, override_trace: Any | None, mode: str = "latent") -> TraceObservation:
        import torch
        self.load()
        assert self.engine is not None
        input_ids, attention_mask, position_ids, labels, prefix_length = self._prepare(task, mode=mode)
        with torch.no_grad():
            loss, logits, trace = self.engine.run(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                labels=labels,
                override_trace=override_trace,
            )
        answer_logits = logits[0, prefix_length - 1 : -1, :].detach().float().cpu().numpy()
        return TraceObservation(
            trace=trace.detach().float().cpu().numpy(),
            answer_loss=float(loss.detach().cpu().item()),
            answer_logits=answer_logits,
            predicted_answer=None,
            mode=mode,
            metadata={
                "prefix_length": int(prefix_length),
                "input_length": int(input_ids.shape[1]),
                "device": self.device,
            },
        )

    def capture(self, task: TaskRecord) -> TraceObservation:
        return self._observe(task, None, mode="latent")

    def score_with_trace(self, task: TaskRecord, trace: Any) -> TraceObservation:
        return self._observe(task, trace, mode="latent")

    def supports_mode(self, mode: str) -> bool:
        return mode in {"latent", "direct", "verbalized"}

    def capture_mode(self, task: TaskRecord, mode: str) -> TraceObservation:
        if mode == "latent":
            return self.capture(task)
        return self._observe(task, None, mode=mode)

    @staticmethod
    def _parse_boolean(text: str) -> str | None:
        import re
        matches = re.findall(r"\b(true|false)\b", text, flags=re.IGNORECASE)
        return matches[-1].title() if matches else None

    def generate_mode(self, task: TaskRecord, mode: str) -> TraceObservation:
        import torch
        self.load()
        assert self.wrapper is not None
        if not self.supports_mode(mode):
            raise UnsupportedAdapterOperation(f"Unsupported Coconut mode: {mode}")
        prepared = self.wrapper.prepare_input(
            task.question,
            mode=mode,
            num_latents=self.num_latents,
        )
        with torch.no_grad():
            output = self.wrapper.generate(
                prepared["input_ids"].to(self.device),
                prepared["attention_mask"].to(self.device),
                mode=mode,
                num_iterations=self.num_latents,
                max_new_tokens=48,
            )
        text = self.wrapper.decode(output.output_ids, skip_special_tokens=False)
        predicted = self._parse_boolean(text)
        base = self.capture_mode(task, mode)
        return TraceObservation(
            trace=base.trace,
            answer_loss=base.answer_loss,
            answer_logits=base.answer_logits,
            predicted_answer=predicted,
            generated_text=text,
            generated_correct=(predicted is not None and predicted.lower() == task.answer.strip().lower()),
            mode=mode,
            metadata={**dict(base.metadata), "free_generation": True},
        )

    def model_fingerprint(self) -> Mapping[str, Any]:
        return dict(self._fingerprint)

    def close(self) -> None:
        self.wrapper = None
        self.engine = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass


def fingerprint_real_inputs(
    *,
    external_repo: str | Path,
    checkpoint: str | Path,
    base_model: str,
    num_latents: int,
    checkpoint_revision: str = MultimodeCoconutProntoQAAdapter.CHECKPOINT_REVISION,
    base_model_revision: str = MultimodeCoconutProntoQAAdapter.BASE_MODEL_REVISION,
    source_lock_path: str | Path | None = None,
) -> dict[str, Any]:
    repo = Path(external_repo).resolve()
    checkpoint_path = Path(checkpoint).resolve()
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    lock_file = (
        Path(source_lock_path).resolve()
        if source_lock_path is not None
        else Path(__file__).resolve().parents[2] / "external_source_lock.json"
    )
    source_lock = load_source_lock(lock_file)
    source_verification = verify_external_repository(
        repo, source_lock, dataset_key="prontoqa_test"
    )
    base_required_files = list(source_lock["base_model"].get("required_files", ()))
    base_path = Path(base_model)
    return {
        "adapter": "MultimodeCoconutProntoQAAdapter",
            "evidence_kind": "real_checkpoint",
            "engineered_positive_control": False,
        "external_repository": MultimodeCoconutProntoQAAdapter.REPOSITORY,
        "external_commit": commit,
        "source_verification_sha256": source_verification["verification_sha256"],
        "checkpoint_repo": MultimodeCoconutProntoQAAdapter.CHECKPOINT_REPO,
        "checkpoint_revision": checkpoint_revision,
        "checkpoint_filename": checkpoint_path.name,
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "base_model": base_model,
        "base_model_revision": base_model_revision,
        "base_model_tree_sha256": (
            sha256_file_set(base_path, base_required_files)
            if base_path.is_dir() and base_required_files
            else None
        ),
        "num_latents": num_latents,
    }
