from __future__ import annotations

import importlib
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Callable
from unittest.mock import patch

import numpy as np

from rrct_lab.adapters import hf_local
from rrct_lab.adapters.hf_local import (
    load_local_causal_lm,
    norm_matched_residual_patch,
    projector_ablate,
    resolve_bounded_index,
    resolve_decoder_layers,
    validate_local_model_path,
    validate_projector,
)
from rrct_lab.exceptions import DependencyError


def _raises(error_type: type[BaseException], action: Callable[[], object]) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_local_path_and_index_safety() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        model_file = directory / "model.safetensors"
        model_file.write_bytes(b"local-test-placeholder")
        assert validate_local_model_path(directory) == directory.resolve()
        assert validate_local_model_path(model_file) == model_file.resolve()
        _raises(
            ValueError,
            lambda: validate_local_model_path(directory / "missing-model"),
        )
    for remote in (
        "https://example.invalid/model",
        "hf://organization/model",
        "s3://bucket/model",
    ):
        _raises(ValueError, lambda value=remote: validate_local_model_path(value))
    assert resolve_bounded_index(-1, 4, name="layer") == 3
    assert resolve_bounded_index(0, 4, name="layer") == 0
    _raises(ValueError, lambda: resolve_bounded_index(4, 4, name="layer"))
    _raises(ValueError, lambda: resolve_bounded_index(True, 4, name="layer"))


def test_decoder_layout_resolution() -> None:
    layers = [object(), object()]
    found, label = resolve_decoder_layers(
        SimpleNamespace(model=SimpleNamespace(layers=layers))
    )
    assert found == tuple(layers)
    assert label == "model.layers"
    found, label = resolve_decoder_layers(
        SimpleNamespace(transformer=SimpleNamespace(h=layers))
    )
    assert found == tuple(layers)
    assert label == "transformer.h"
    found, label = resolve_decoder_layers(
        SimpleNamespace(gpt_neox=SimpleNamespace(layers=layers))
    )
    assert found == tuple(layers)
    assert label == "gpt_neox.layers"
    _raises(ValueError, lambda: resolve_decoder_layers(SimpleNamespace()))


def test_loading_is_lazy_local_only_and_remote_code_disabled() -> None:
    tokenizer_calls: list[tuple[str, dict]] = []
    model_calls: list[tuple[str, dict]] = []

    class FakeTokenizerFactory:
        @classmethod
        def from_pretrained(cls, source: str, **options: object) -> object:
            tokenizer_calls.append((source, dict(options)))
            return object()

    class FakeModel:
        def __init__(self) -> None:
            self.model = SimpleNamespace(layers=[object()])
            self.eval_called = False
            self.device = None

        def eval(self) -> None:
            self.eval_called = True

        def to(self, device: str) -> None:
            self.device = device

    loaded_model = FakeModel()

    class FakeModelFactory:
        @classmethod
        def from_pretrained(cls, source: str, **options: object) -> FakeModel:
            model_calls.append((source, dict(options)))
            return loaded_model

    fake_torch = SimpleNamespace(
        float32=object(), float16=object(), bfloat16=object()
    )
    fake_transformers = SimpleNamespace(
        AutoTokenizer=FakeTokenizerFactory,
        AutoModelForCausalLM=FakeModelFactory,
    )

    def fake_import(name: str) -> object:
        if name == "torch":
            return fake_torch
        if name == "transformers":
            return fake_transformers
        raise ModuleNotFoundError(name)

    with tempfile.TemporaryDirectory() as temporary:
        model_path = Path(temporary).resolve()
        with patch.object(importlib, "import_module", side_effect=fake_import):
            bundle = load_local_causal_lm(model_path, dtype="float32")
    assert bundle.model is loaded_model
    assert loaded_model.eval_called is True
    assert loaded_model.device == "cpu"
    assert len(tokenizer_calls) == len(model_calls) == 1
    for source, options in (*tokenizer_calls, *model_calls):
        assert source == str(model_path)
        assert options["local_files_only"] is True
        assert options["trust_remote_code"] is False
    assert model_calls[0][1]["torch_dtype"] is fake_torch.float32
    assert bundle.metadata()["network_access"] is False
    assert bundle.metadata()["training"] is False
    # Importing hf_local itself must not bind either optional runtime module.
    assert "torch" not in vars(hf_local)
    assert "transformers" not in vars(hf_local)


def test_missing_optional_dependency_is_explicit() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        with patch.object(
            importlib,
            "import_module",
            side_effect=ModuleNotFoundError("torch"),
        ):
            _raises(
                DependencyError,
                lambda: load_local_causal_lm(Path(temporary)),
            )


def test_numpy_patch_and_projector_ablation_helpers() -> None:
    source = np.array([3.0, 4.0, 0.0])
    target = np.array([0.0, 0.0, 10.0])
    patch_vector = norm_matched_residual_patch(source, target)
    assert np.isclose(np.linalg.norm(patch_vector), np.linalg.norm(target))
    np.testing.assert_allclose(patch_vector, [6.0, 8.0, 0.0])
    _raises(
        ValueError,
        lambda: norm_matched_residual_patch(np.zeros(3), np.ones(3)),
    )

    projector = np.diag([1.0, 0.0, 1.0])
    np.testing.assert_array_equal(validate_projector(projector), projector)
    residual = np.array([2.0, 3.0, 4.0])
    np.testing.assert_allclose(projector_ablate(residual, projector), [0.0, 3.0, 0.0])
    batch = np.stack([residual, residual * 2.0])
    np.testing.assert_allclose(
        projector_ablate(batch, projector),
        [[0.0, 3.0, 0.0], [0.0, 6.0, 0.0]],
    )
    _raises(ValueError, lambda: validate_projector([[1.0, np.nan], [0.0, 0.0]]))
    _raises(ValueError, lambda: validate_projector([[1.0, 1.0], [0.0, 0.0]]))
    _raises(ValueError, lambda: validate_projector(np.diag([0.5, 0.5])))
    _raises(ValueError, lambda: projector_ablate(np.ones(2), projector))


def test_json_metadata_contract() -> None:
    metadata = hf_local.LocalCausalLMBundle(
        model_path="/local/model",
        model=object(),
        tokenizer=object(),
        layers=(object(),),
        layer_layout="model.layers",
        device="cpu",
        dtype=None,
    ).metadata()
    assert json.loads(json.dumps(metadata)) == metadata
    assert metadata["local_files_only"] is True
    assert metadata["trust_remote_code"] is False
    assert metadata["network_access"] is False
    assert metadata["training"] is False


if __name__ == "__main__":
    test_local_path_and_index_safety()
    test_decoder_layout_resolution()
    test_loading_is_lazy_local_only_and_remote_code_disabled()
    test_missing_optional_dependency_is_explicit()
    test_numpy_patch_and_projector_ablation_helpers()
    test_json_metadata_contract()
    print("test_hf_local_adapter: 6 direct tests passed")
