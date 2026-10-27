from __future__ import annotations

from pathlib import Path

from download_external_assets import DEFAULT_BASE_FILES, build_asset_plan


def _lock() -> dict:
    return {
        "base_model": {
            "repository": "openai-community/gpt2",
            "revision": "base-revision",
            "required_files": list(DEFAULT_BASE_FILES),
        },
        "checkpoints": {
            "prontoqa_primary": {
                "repository": "example/checkpoint",
                "revision": "checkpoint-revision",
                "filename": "checkpoint_37",
            }
        },
    }


def test_asset_plan_is_revision_pinned_and_minimal(tmp_path: Path):
    plan = build_asset_plan(_lock(), tmp_path)
    assert plan["checkpoint_revision"] == "checkpoint-revision"
    assert plan["checkpoint_filename"] == "checkpoint_37"
    assert plan["base_model_revision"] == "base-revision"
    assert set(plan["base_model_required_files"]) == set(DEFAULT_BASE_FILES)
    assert plan["base_model_dir"].endswith("models/gpt2")


def test_default_base_file_set_excludes_alternate_framework_weights(tmp_path: Path):
    lock = _lock()
    del lock["base_model"]["required_files"]
    plan = build_asset_plan(lock, tmp_path)
    assert "model.safetensors" in plan["base_model_required_files"]
    assert "pytorch_model.bin" not in plan["base_model_required_files"]
    assert "tf_model.h5" not in plan["base_model_required_files"]
    assert "flax_model.msgpack" not in plan["base_model_required_files"]


def test_allowlisted_payload_hash_ignores_unrelated_files(tmp_path: Path):
    from sric_real_lrm.hashing import sha256_file_set

    for name in DEFAULT_BASE_FILES:
        (tmp_path / name).write_text(name + "\n", encoding="utf-8")
    before = sha256_file_set(tmp_path, DEFAULT_BASE_FILES)
    (tmp_path / "pytorch_model.bin").write_bytes(b"unrelated legacy payload")
    (tmp_path / ".cache").mkdir()
    (tmp_path / ".cache" / "metadata.json").write_text("{}\n", encoding="utf-8")
    after = sha256_file_set(tmp_path, DEFAULT_BASE_FILES)
    assert after == before
