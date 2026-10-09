"""Protect historical inputs and the byte-preserved replay backend."""
import hashlib
import json
from importlib import resources

import numpy as np
import pytest

from am_spd import reference


@pytest.mark.parametrize("case", reference.PAPER_CASES)
def test_archived_core_fixture(case):
    image, core = reference._load_paper_core(case)
    assert image.shape[:2] == (56, 56)
    assert len(core.active_atoms) == len(core.active_specs) == 44
    assert core.coefficients.shape == (44, image.shape[2])
    assert len(core.history) == 43
    assert np.isfinite(image).all()
    assert np.min(image) >= 0 and np.max(image) <= 1
    np.testing.assert_allclose(core.reconstruction + core.residual, image, rtol=0, atol=2e-16)


def test_frozen_backend_matches_recovered_source_hashes():
    provenance = json.loads(reference._resource_text("paper_backend_provenance.json"))
    backend = resources.files("am_spd._paper_v03")
    for name, digest in provenance["files"].items():
        assert hashlib.sha256(backend.joinpath(name).read_bytes()).hexdigest() == digest


def test_replay_rejects_modified_fixture(tmp_path, monkeypatch):
    resource_root = resources.files("am_spd.resources")
    fixture = "paper_fixture_synthetic_geometry.npz"
    data = bytearray(resource_root.joinpath(fixture).read_bytes())
    data[len(data) // 2] ^= 1
    (tmp_path / fixture).write_bytes(data)
    (tmp_path / "paper_backend_provenance.json").write_text(
        resource_root.joinpath("paper_backend_provenance.json").read_text(), encoding="utf-8"
    )
    monkeypatch.setattr(reference.resources, "files", lambda _: tmp_path)
    with pytest.raises(ValueError, match="fixture checksum mismatch"):
        reference._load_paper_core("synthetic_geometry")
