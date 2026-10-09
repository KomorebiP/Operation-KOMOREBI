"""Protect historical inputs and the byte-preserved replay backend."""
import hashlib
import json
from importlib import resources

import numpy as np
import pytest

from am_spd import AMSpdConfig, reconstruct, reference


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


def test_reopening_coordinates_ignore_equivalent_degenerate_basis_rotation():
    rng = np.random.default_rng(919)
    image = rng.uniform(size=(8, 9, 1))
    core, _ = np.linalg.qr(rng.normal(size=(image.size, 1)))
    raw = rng.normal(size=(image.size, 2))
    raw -= core @ (core.T @ raw)
    archived, _ = np.linalg.qr(raw)
    angle = 0.73
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    rotated = archived @ rotation
    target = image.reshape(-1)
    full = (core @ (core.T @ target) + rotated @ (rotated.T @ target)).reshape(image.shape)
    archived_images = archived.T.reshape(2, *image.shape)
    costs = np.array([3.0, 5.0])
    directions, retained_costs, checks = reference._anchor_reopening_seed(
        image, core, full, list(rotated.T.reshape(2, *image.shape)), list(costs), archived_images, costs,
    )
    np.testing.assert_array_equal(np.asarray(directions), archived_images)
    assert retained_costs == [3.0, 5.0]
    assert checks["span_error"] < 1e-12
    assert checks["projection_error"] < 1e-12
    # Individual coefficients vary under a degenerate rotation even though
    # the full projector does not. Reopening must use the archived ones.
    assert not np.allclose(archived.T @ target, rotated.T @ target)
    np.testing.assert_allclose(np.asarray(directions).reshape(2, -1) @ target, archived.T @ target, atol=1e-15)


def test_reopening_anchor_rejects_a_different_seed_span():
    rng = np.random.default_rng(920)
    image = rng.uniform(size=(8, 9, 1))
    columns, _ = np.linalg.qr(rng.normal(size=(image.size, 4)))
    core = columns[:, :1]
    fresh = columns[:, 1:3]
    archive = columns[:, 2:4].T.reshape(2, *image.shape)
    target = image.reshape(-1)
    full = (core @ (core.T @ target) + fresh @ (fresh.T @ target)).reshape(image.shape)
    with pytest.raises(ValueError, match="disagrees with fresh"):
        reference._anchor_reopening_seed(
            image, core, full, list(fresh.T.reshape(2, *image.shape)), [1.0, 1.0], archive, np.ones(2),
        )
    # Equal total cost does not make a missing coordinate cost legitimate.
    with pytest.raises(ValueError, match="cost count differs"):
        reference._anchor_reopening_seed(
            image, core, full, list(fresh.T.reshape(2, *image.shape)), [2.0],
            fresh.T.reshape(2, *image.shape), np.ones(2),
        )


def test_normal_decomposition_does_not_consult_historical_seed_anchors(monkeypatch):
    def forbidden(_case):
        raise AssertionError("normal decomposition used historical coordinates")
    monkeypatch.setattr(reference, "_historical_seed_bases", forbidden)
    source = np.random.default_rng(921).uniform(size=(8, 9, 1))
    result = reconstruct(source, AMSpdConfig(method="core", packet_budget=1))
    assert result.exact_identity_error < 1e-12


def test_reopening_seed_rejects_nonfinite_fresh_state():
    image = np.ones((2, 2, 1))
    core = np.eye(4)[:, :1]
    direction = np.eye(4)[:, 1].reshape(image.shape)
    archive = np.array([direction])
    target = image.reshape(-1)
    full = (core @ (core.T @ target) + direction.reshape(-1) * target[1]).reshape(image.shape)
    for name in ("image", "core_basis", "reconstruction", "directions", "costs"):
        values = {
            "image": image.copy(), "core_basis": core.copy(), "reconstruction": full.copy(),
            "directions": [direction.copy()], "costs": [1.0],
        }
        if name == "directions":
            values[name][0].flat[0] = np.nan
        elif name == "costs":
            values[name][0] = np.nan
        else:
            values[name].flat[0] = np.nan
        with pytest.raises(ValueError, match="must be finite"):
            reference._anchor_reopening_seed(**values, archived_directions=archive, archived_costs=np.ones(1))


@pytest.mark.parametrize("case", reference.PAPER_CASES)
def test_archived_seed_fixtures_are_complete(case):
    image, _ = reference._load_paper_core(case)
    seeds = reference._historical_seed_bases(case)
    assert set(seeds) == {"greedy", "lagrange_tree", "exact_budget_tree"}
    for directions, costs in seeds.values():
        assert directions.shape[1:] == image.shape
        assert costs.shape == (len(directions),)
        assert np.isfinite(directions).all() and np.isfinite(costs).all()
        assert np.min(costs) >= 0
