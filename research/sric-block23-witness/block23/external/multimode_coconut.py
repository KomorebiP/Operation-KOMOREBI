from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .protocol import LatentReasonerAdapter, PilotTask, TraceRun
from .source_lock import verify_source_lock


class MultimodeCoconutAdapter(LatentReasonerAdapter):
    """Adapter for the locked third-party GPT-2 multimode Coconut runtime.

    The adapter imports the upstream wrapper from a local, source-locked checkout.
    It captures the exact embeddings written into the latent-token positions and
    evaluates externally supplied traces by a deterministic one-shot recomputation.
    """

    def __init__(
        self,
        repo_dir: str | Path,
        checkpoint: str | Path,
        source_lock: str | Path,
        *,
        device: str = "cuda",
        num_latents: int = 6,
        base_model: str = "openai-community/gpt2",
    ):
        self.repo_dir = Path(repo_dir).resolve()
        self.checkpoint = Path(checkpoint).resolve()
        self.source_lock = Path(source_lock).resolve()
        self.device = device
        self.num_latents = int(num_latents)
        self.base_model = base_model
        self.runtime: Any | None = None

    def load(self) -> None:
        lock = verify_source_lock(self.repo_dir, self.source_lock)
        if not lock.get("passed"):
            raise RuntimeError(f"external repository does not match SOURCE_LOCK: {lock}")
        if not self.checkpoint.is_file():
            raise FileNotFoundError(self.checkpoint)
        if importlib.util.find_spec("transformers") is None:
            raise RuntimeError("transformers is required for real checkpoint execution")
        sys.path.insert(0, str(self.repo_dir))
        try:
            module_path = self.repo_dir / "models" / "multimode_coconut" / "multimode_coconut_model.py"
            spec = importlib.util.spec_from_file_location("sric_locked_multimode_coconut", module_path)
            if spec is None or spec.loader is None:
                raise ImportError(module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls = module.MultimodeCoconutModel
            runtime = cls(
                model_path=str(self.checkpoint),
                device=self.device,
                model_id=self.base_model,
                num_latent=self.num_latents,
            )
            runtime.load()
            self.runtime = runtime
        finally:
            if sys.path and sys.path[0] == str(self.repo_dir):
                sys.path.pop(0)

    def _require(self) -> Any:
        if self.runtime is None:
            self.load()
        return self.runtime

    @staticmethod
    def _answer_token_ids(runtime: Any, answer: str) -> list[int]:
        text = answer.strip()
        ids = runtime.tokenizer.encode(text, add_special_tokens=False)
        if not ids:
            raise ValueError(f"answer tokenized to an empty sequence: {answer!r}")
        return ids

    def _scoring_inputs(self, task: PilotTask) -> tuple[Any, Any, np.ndarray, list[int]]:
        import torch
        runtime = self._require()
        prepared = runtime.prepare_input(task.question, mode="latent", num_latents=self.num_latents)
        prefix = prepared["input_ids"].to(runtime.device)
        ans = self._answer_token_ids(runtime, task.answer)
        eos = [runtime.tokenizer.eos_token_id] if runtime.tokenizer.eos_token_id is not None else []
        suffix = torch.tensor([ans + eos], dtype=prefix.dtype, device=runtime.device)
        input_ids = torch.cat([prefix, suffix], dim=1)
        attention = torch.ones_like(input_ids)
        latent_id = runtime.special_tokens["latent"]
        positions = (input_ids[0] == latent_id).nonzero(as_tuple=True)[0].detach().cpu().numpy()
        return input_ids, attention, positions, ans

    @staticmethod
    def _masked_answer_loss(logits: Any, input_ids: Any, answer_start: int, eos_included: bool = True) -> float:
        import torch
        shift_logits = logits[:, :-1, :]
        shift_labels = input_ids[:, 1:]
        token_positions = torch.arange(1, input_ids.shape[1], device=input_ids.device)
        mask = token_positions >= answer_start
        if not eos_included:
            mask = mask & (token_positions < input_ids.shape[1] - 1)
        selected_logits = shift_logits[:, mask, :]
        selected_labels = shift_labels[:, mask]
        return float(torch.nn.functional.cross_entropy(
            selected_logits.reshape(-1, selected_logits.shape[-1]), selected_labels.reshape(-1)
        ).detach().cpu())

    def _result(self, task: PilotTask, trace: np.ndarray, logits: Any, input_ids: Any, answer_start: int) -> TraceRun:
        import torch
        runtime = self._require()
        loss = self._masked_answer_loss(logits, input_ids, answer_start)
        first_logits = logits[0, answer_start - 1]
        true_id = int(input_ids[0, answer_start])
        prob = float(torch.softmax(first_logits.float(), dim=-1)[true_id].detach().cpu())
        pred_id = int(torch.argmax(first_logits).item())
        pred = runtime.tokenizer.decode([pred_id]).strip()
        return TraceRun(task.task_id, trace.astype(float), loss, prob, pred, {
            "runtime": "multimode_coconut",
            "num_latents": self.num_latents,
            "answer_start": answer_start,
        })

    def capture(self, task: PilotTask) -> TraceRun:
        import torch
        runtime = self._require()
        input_ids, attention, positions, _ = self._scoring_inputs(task)
        position_ids = torch.arange(input_ids.shape[1], device=runtime.device).reshape(1, -1)
        with torch.no_grad():
            outputs = runtime.model.forward(
                input_ids=input_ids,
                attention_mask=attention,
                labels=input_ids.clone(),
                position_ids=position_ids,
            )
            trace_t = outputs.inputs_embeds[0, torch.as_tensor(positions, device=runtime.device), :]
        trace = trace_t.detach().float().cpu().numpy()
        answer_start = int(positions[-1] + 2)  # final latent, then eocot, then answer
        return self._result(task, trace, outputs.logits, input_ids, answer_start)

    def evaluate_trace(self, task: PilotTask, trace: np.ndarray) -> TraceRun:
        import torch
        runtime = self._require()
        input_ids, attention, positions, _ = self._scoring_inputs(task)
        x = np.asarray(trace, float)
        expected = (len(positions), int(runtime.model.get_embedding().embedding_dim))
        if x.shape != expected:
            raise ValueError(f"expected trace shape {expected}, got {x.shape}")
        with torch.no_grad():
            embeds = runtime.model.get_embedding()(input_ids).clone()
            embeds[0, torch.as_tensor(positions, device=runtime.device), :] = torch.as_tensor(
                x, dtype=embeds.dtype, device=runtime.device
            )
            outputs = runtime.model.base_causallm(
                inputs_embeds=embeds,
                attention_mask=attention,
                use_cache=False,
            )
        answer_start = int(positions[-1] + 2)
        return self._result(task, x, outputs.logits, input_ids, answer_start)
