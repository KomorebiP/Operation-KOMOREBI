"""Optional, bounded adapters for locally available instrumentable models."""

from .hf_local import (
    LocalCausalLMBundle,
    load_local_causal_lm,
    make_norm_matched_patch_hook,
    make_projector_ablation_hook,
    norm_matched_residual_patch,
    probe_target_token_vjps,
    projector_ablate,
    resolve_bounded_index,
    resolve_decoder_layers,
    validate_local_model_path,
    validate_projector,
)

__all__ = [
    "LocalCausalLMBundle",
    "load_local_causal_lm",
    "make_norm_matched_patch_hook",
    "make_projector_ablation_hook",
    "norm_matched_residual_patch",
    "probe_target_token_vjps",
    "projector_ablate",
    "resolve_bounded_index",
    "resolve_decoder_layers",
    "validate_local_model_path",
    "validate_projector",
]

