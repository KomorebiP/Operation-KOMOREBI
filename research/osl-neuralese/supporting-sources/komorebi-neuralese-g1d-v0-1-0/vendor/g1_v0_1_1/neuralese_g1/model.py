from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Literal

try:
    import torch
    import torch.nn as nn
except ImportError as error:  # pragma: no cover - exercised by preflight
    raise ImportError("PyTorch is required for the recurrent model runtime") from error


RecurrenceMode = Literal["recurrent", "no_feedback"]
AnswerMode = Literal["recurrent", "zero", "shuffle", "no_feedback"]


@dataclass
class RecurrentTrace:
    states: list["torch.Tensor"]
    injections: list["torch.Tensor"]
    feedback_states: list["torch.Tensor"]
    halt_probabilities: list["torch.Tensor"]

    def detached_statistics(self) -> dict[str, Any]:
        def norms(values: list["torch.Tensor"]) -> list[float]:
            return [float(value.detach().float().norm(dim=-1).mean().item()) for value in values]

        return {
            "logical_steps": len(self.injections),
            "state_mean_norm_by_step": norms(self.states),
            "injection_mean_norm_by_step": norms(self.injections),
            "feedback_mean_norm_by_step": norms(self.feedback_states),
            "halt_probability_mean_by_step": [
                float(value.detach().float().mean().item()) for value in self.halt_probabilities
            ],
        }


def find_decoder_layers(model: nn.Module) -> Any:
    candidates = [
        getattr(model, "model", None),
        getattr(getattr(model, "model", None), "model", None),
        getattr(model, "transformer", None),
    ]
    for candidate in candidates:
        if candidate is not None and hasattr(candidate, "layers"):
            return candidate.layers
        if candidate is not None and hasattr(candidate, "h"):
            return candidate.h
    raise RuntimeError("Could not locate the causal decoder block list")


def last_valid_positions(attention_mask: "torch.Tensor") -> "torch.Tensor":
    if attention_mask.ndim != 2:
        raise ValueError("attention_mask must have shape [batch, sequence]")
    if not torch.all((attention_mask == 0) | (attention_mask == 1)):
        raise ValueError("attention_mask must be binary")
    lengths = attention_mask.long().sum(dim=-1)
    if torch.any(lengths <= 0):
        raise ValueError("every row must contain at least one valid token")
    token_indices = torch.arange(
        attention_mask.shape[1], device=attention_mask.device
    ).unsqueeze(0)
    expected_mask = token_indices < lengths.unsqueeze(1)
    if not torch.equal(attention_mask.bool(), expected_mask):
        raise ValueError("G1 requires a contiguous right-padded attention mask")
    positions = lengths - 1
    rows = torch.arange(attention_mask.shape[0], device=attention_mask.device)
    if not torch.all(attention_mask[rows, positions] == 1):
        raise ValueError("attention mask is not right padded")
    return positions


class RecurrentWorkspace(nn.Module):
    """Small shared recurrent state with an intentionally unrestricted residual."""

    def __init__(
        self,
        hidden_size: int,
        width: int,
        *,
        dropout: float,
        state_clip: float,
    ) -> None:
        super().__init__()
        if hidden_size <= 0 or width <= 0:
            raise ValueError("hidden_size and width must be positive")
        self.hidden_size = int(hidden_size)
        self.width = int(width)
        self.state_clip = float(state_clip)
        self.input_norm = nn.LayerNorm(hidden_size)
        self.input_projection = nn.Linear(hidden_size, width)
        self.context_projection = nn.Linear(hidden_size, width, bias=False)
        self.state_norm = nn.LayerNorm(width)
        self.gate = nn.Linear(2 * width, width)
        self.proposal = nn.Sequential(
            nn.Linear(2 * width, 2 * width),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(2 * width, width),
            nn.Tanh(),
        )
        self.output_norm = nn.LayerNorm(width)
        self.output_projection = nn.Linear(width, hidden_size, bias=False)
        self.halt = nn.Linear(width, 1)
        nn.init.normal_(self.output_projection.weight, mean=0.0, std=1e-3)
        nn.init.constant_(self.halt.bias, -1.0)

    def initialize(self, hidden: "torch.Tensor") -> "torch.Tensor":
        source = self.input_norm(hidden.float())
        return torch.tanh(self.input_projection(source))

    def advance(
        self,
        state: "torch.Tensor",
        feedback_hidden: "torch.Tensor",
    ) -> tuple["torch.Tensor", "torch.Tensor"]:
        feedback = torch.tanh(self.context_projection(feedback_hidden.float()))
        joined = torch.cat((self.state_norm(state), feedback), dim=-1)
        gate = torch.sigmoid(self.gate(joined))
        proposal = self.proposal(joined)
        updated = state + gate * (proposal - state)
        if self.state_clip > 0:
            norm = updated.norm(dim=-1, keepdim=True).clamp_min(1e-12)
            scale = torch.clamp(self.state_clip / norm, max=1.0)
            updated = updated * scale
        halt_probability = torch.sigmoid(self.halt(self.state_norm(updated))).squeeze(-1)
        return updated, halt_probability

    def decode(self, state: "torch.Tensor") -> "torch.Tensor":
        return self.output_projection(self.output_norm(state))


class FrozenRecurrentCausalLM(nn.Module):
    """Frozen HF causal LM plus a recurrent activation-space sidecar.

    Logical recurrent steps are full top-level forward passes. A single bounded
    pre-hook injects one delta at the last valid token before `source_layer`.
    KV caching is always disabled so recurrence cannot be mistaken for token
    progression.
    """

    def __init__(
        self,
        backbone: nn.Module,
        *,
        source_layer: int,
        workspace_width: int,
        recurrent_steps: int,
        injection_scale: float,
        state_clip: float,
        dropout: float,
    ) -> None:
        super().__init__()
        if recurrent_steps <= 0:
            raise ValueError("recurrent_steps must be positive")
        self.backbone = backbone
        decoder_layers = find_decoder_layers(backbone)
        object.__setattr__(self, "_decoder_layers", decoder_layers)
        if not 0 <= source_layer < len(decoder_layers):
            raise ValueError(
                f"source_layer={source_layer} outside decoder depth {len(decoder_layers)}"
            )
        hidden_size = int(backbone.config.hidden_size)
        self.source_layer = int(source_layer)
        self.recurrent_steps = int(recurrent_steps)
        self.injection_scale = float(injection_scale)
        self.workspace = RecurrentWorkspace(
            hidden_size,
            workspace_width,
            dropout=dropout,
            state_clip=state_clip,
        )
        for parameter in self.backbone.parameters():
            parameter.requires_grad_(False)
        self.backbone.eval()

    @property
    def backbone_is_frozen(self) -> bool:
        return all(not parameter.requires_grad for parameter in self.backbone.parameters())

    @property
    def layers(self) -> Any:
        return self._decoder_layers

    def workspace_parameters(self) -> list[nn.Parameter]:
        return [parameter for parameter in self.workspace.parameters() if parameter.requires_grad]

    def train(self, mode: bool = True) -> "FrozenRecurrentCausalLM":
        super().train(mode)
        self.backbone.eval()
        self.workspace.train(mode)
        return self

    def _injection_hook(
        self,
        delta: "torch.Tensor",
        positions: "torch.Tensor",
    ) -> Any:
        def hook(
            module: nn.Module,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> tuple[tuple[Any, ...], dict[str, Any]]:
            del module
            if args:
                hidden = args[0]
                remaining = args[1:]
                location = "args"
            elif "hidden_states" in kwargs:
                hidden = kwargs["hidden_states"]
                remaining = ()
                location = "kwargs"
            else:
                raise RuntimeError("decoder hook did not receive hidden states")
            if hidden.ndim != 3 or hidden.shape[0] != delta.shape[0]:
                raise RuntimeError("decoder hidden state is incompatible with injection")
            rows = torch.arange(hidden.shape[0], device=hidden.device)
            patched = hidden.clone()
            patched[rows, positions] = (
                patched[rows, positions]
                + self.injection_scale * delta.to(device=hidden.device, dtype=hidden.dtype)
            )
            if location == "args":
                return (patched, *remaining), kwargs
            updated_kwargs = dict(kwargs)
            updated_kwargs["hidden_states"] = patched
            return args, updated_kwargs

        return hook

    def _backbone_pass(
        self,
        input_ids: "torch.Tensor",
        attention_mask: "torch.Tensor",
        *,
        delta: "torch.Tensor | None" = None,
    ) -> tuple["torch.Tensor", torch.Tensor]:
        positions = last_valid_positions(attention_mask)
        handle = None
        if delta is not None:
            handle = self.layers[self.source_layer].register_forward_pre_hook(
                self._injection_hook(delta, positions), with_kwargs=True
            )
        try:
            outputs = self.backbone(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                use_cache=False,
                return_dict=True,
            )
        finally:
            if handle is not None:
                handle.remove()
        hidden_states = outputs.hidden_states
        if hidden_states is None or len(hidden_states) <= self.source_layer + 1:
            raise RuntimeError("backbone did not return the registered source activation")
        rows = torch.arange(input_ids.shape[0], device=input_ids.device)
        source = hidden_states[self.source_layer + 1][rows, positions]
        logits = outputs.logits[rows, positions]
        return logits, source

    def encode(
        self,
        input_ids: "torch.Tensor",
        attention_mask: "torch.Tensor",
        *,
        mode: RecurrenceMode = "recurrent",
    ) -> tuple["torch.Tensor", RecurrentTrace]:
        if mode not in ("recurrent", "no_feedback"):
            raise ValueError(f"unsupported recurrence mode: {mode}")
        _, initial_hidden = self._backbone_pass(input_ids, attention_mask)
        state = self.workspace.initialize(initial_hidden)
        states = [state]
        injections: list[torch.Tensor] = []
        feedback_states = [initial_hidden]
        halt_probabilities: list[torch.Tensor] = []
        for _logical_step in range(self.recurrent_steps):
            delta = self.workspace.decode(state)
            _, observed_feedback = self._backbone_pass(
                input_ids, attention_mask, delta=delta
            )
            feedback = observed_feedback if mode == "recurrent" else initial_hidden
            state, halt_probability = self.workspace.advance(state, feedback)
            states.append(state)
            injections.append(delta)
            feedback_states.append(feedback)
            halt_probabilities.append(halt_probability)
        return state, RecurrentTrace(
            states=states,
            injections=injections,
            feedback_states=feedback_states,
            halt_probabilities=halt_probabilities,
        )

    def answer(
        self,
        query_input_ids: "torch.Tensor",
        query_attention_mask: "torch.Tensor",
        state: "torch.Tensor | None",
    ) -> "torch.Tensor":
        delta = None if state is None else self.workspace.decode(state)
        logits, _ = self._backbone_pass(
            query_input_ids, query_attention_mask, delta=delta
        )
        return logits

    def forward(
        self,
        compute_input_ids: "torch.Tensor",
        compute_attention_mask: "torch.Tensor",
        query_input_ids: "torch.Tensor",
        query_attention_mask: "torch.Tensor",
        *,
        recurrence_mode: RecurrenceMode = "recurrent",
        answer_mode: AnswerMode = "recurrent",
        donor_indices: "torch.Tensor | None" = None,
    ) -> tuple["torch.Tensor", RecurrentTrace]:
        state, trace = self.encode(
            compute_input_ids, compute_attention_mask, mode=recurrence_mode
        )
        answer_state: torch.Tensor | None = state
        if answer_mode == "zero":
            answer_state = None
        elif answer_mode == "shuffle":
            if donor_indices is None or donor_indices.shape != (state.shape[0],):
                raise ValueError("shuffle answer mode requires one donor index per row")
            answer_state = state.index_select(0, donor_indices.to(device=state.device))
        elif answer_mode not in ("recurrent", "no_feedback"):
            raise ValueError(f"unsupported answer mode: {answer_mode}")
        return self.answer(query_input_ids, query_attention_mask, answer_state), trace


def finite_nonzero_norm(tensors: list["torch.Tensor"]) -> bool:
    if not tensors:
        return False
    total = torch.zeros((), dtype=torch.float64)
    for tensor in tensors:
        value = tensor.detach().double().norm().cpu()
        if not torch.isfinite(value):
            return False
        total += value
    return bool(torch.isfinite(total) and total.item() > 0.0)


def gradient_norm(parameters: list[nn.Parameter]) -> float:
    total = 0.0
    for parameter in parameters:
        if parameter.grad is None:
            continue
        # Float64 accumulation prevents a norm reduction from overflowing when
        # every individual FP32 gradient element is still finite. A nonfinite
        # result can therefore be treated as a genuine GradScaler overflow.
        value = parameter.grad.detach().double().norm().item()
        if not math.isfinite(value):
            return float("nan")
        total += value * value
    return math.sqrt(total)
