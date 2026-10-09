from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from am_spd.cli import main
from am_spd.components import PixelClosure
from am_spd.io import load_image, save_image


def test_rgba_and_palette_transparency_are_preserved(tmp_path: Path) -> None:
    rgba = np.zeros((8, 8, 4), dtype=np.uint8)
    rgba[..., 0] = 123
    rgba[..., 3] = np.arange(64, dtype=np.uint8).reshape(8, 8)
    path = tmp_path / "rgba.png"
    Image.fromarray(rgba).save(path)
    np.testing.assert_array_equal(load_image(path), rgba.astype(np.float64) / 255)
    palette = Image.new("P", (8, 8), color=1)
    palette.putpalette([0, 0, 0, 255, 0, 0] + [0] * 762)
    palette.info["transparency"] = 1
    palette.save(tmp_path / "palette.png")
    assert load_image(tmp_path / "palette.png").shape == (8, 8, 4)
    assert np.all(load_image(tmp_path / "palette.png")[..., 3] == 0)


def test_16_bit_grayscale_uses_declared_depth(tmp_path: Path) -> None:
    source = np.full((8, 8), 32768, dtype=np.uint16)
    path = tmp_path / "depth16.png"
    Image.fromarray(source).save(path)
    np.testing.assert_array_equal(load_image(path), source[..., None].astype(np.float64) / 65535)


def test_normalized_numpy_source_preserves_coordinates(tmp_path: Path) -> None:
    source = np.random.default_rng(7).random((8, 8, 5))
    path = tmp_path / "source.npy"
    np.save(path, source, allow_pickle=False)
    np.testing.assert_array_equal(load_image(path), source)
    np.save(path, source * 3, allow_pickle=False)
    with pytest.raises(ValueError):
        load_image(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_display_save_rejects_nonfinite_rasters(tmp_path: Path, value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        save_image(tmp_path / "invalid.png", np.full((8, 8, 1), value))


def test_exact_cli_decode_requires_float_array_destination(tmp_path: Path, capsys) -> None:
    assert main(["decode", str(tmp_path / "unused.amspd"), str(tmp_path / "preview.png"), "--mode", "exact"]) != 0
    assert ".npy" in capsys.readouterr().err


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), -1.0])
def test_pixel_closure_rejects_invalid_threshold_before_using_result(threshold: float) -> None:
    with pytest.raises(ValueError, match="finite and nonnegative"):
        PixelClosure.from_result(None, threshold)  # type: ignore[arg-type]
