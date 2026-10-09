from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from am_spd.cli import main
from am_spd.io import load_image, save_image


def test_image_io_roundtrip(tmp_path: Path) -> None:
    image = np.linspace(0.0, 1.0, 16 * 16 * 3).reshape(16, 16, 3)
    path = tmp_path / "image.png"
    save_image(path, image)
    recovered = load_image(path)
    assert recovered.shape == image.shape
    np.testing.assert_allclose(recovered, image, atol=1.0 / 255.0, rtol=0.0)


def test_cli_info(capsys) -> None:
    assert main(["info"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["package"] == "komorebi-am-spd"
    assert payload["version"] == "1.0.0"


def test_cli_verify(capsys) -> None:
    assert main(["verify"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
