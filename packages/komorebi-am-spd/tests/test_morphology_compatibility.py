"""Threshold-boundary checks for the supported scikit-image APIs."""
import numpy as np
import pytest
from scipy import ndimage

from am_spd import atlas


@pytest.mark.parametrize("modern", [False, True])
def test_object_size_boundary(modern, monkeypatch):
    # Independent legacy-signature implementation lets both branches run on CI.
    def legacy_objects(mask, min_size):
        labels, _ = ndimage.label(mask)
        sizes = np.bincount(labels.ravel())
        return mask & (sizes[labels] >= min_size)

    if not modern:
        monkeypatch.setattr(atlas, "_OBJECTS_MAX_SIZE", False)
        monkeypatch.setattr(atlas.morphology, "remove_small_objects", legacy_objects)
    else:
        if not atlas._OBJECTS_MAX_SIZE:
            def inclusive_objects(mask, max_size):
                return legacy_objects(mask, min_size=max_size + 1)
            monkeypatch.setattr(atlas, "_OBJECTS_MAX_SIZE", True)
            monkeypatch.setattr(atlas.morphology, "remove_small_objects", inclusive_objects)
    mask = np.zeros((5, 10), dtype=bool)
    mask[1, 1:3] = True  # N-1
    mask[3, 1:4] = True  # N
    mask[1, 5:9] = True  # N+1
    expected = mask.copy()
    expected[1, 1:3] = False
    np.testing.assert_array_equal(atlas._remove_small_objects(mask, min_size=3), expected)


@pytest.mark.parametrize("modern", [False, True])
def test_hole_size_boundary(modern, monkeypatch):
    def legacy_holes(mask, area_threshold):
        labels, _ = ndimage.label(~mask)
        sizes = np.bincount(labels.ravel())
        return mask | ((labels > 0) & (sizes[labels] < area_threshold))

    if not modern:
        monkeypatch.setattr(atlas, "_HOLES_MAX_SIZE", False)
        monkeypatch.setattr(atlas.morphology, "remove_small_holes", legacy_holes)
    else:
        if not atlas._HOLES_MAX_SIZE:
            def inclusive_holes(mask, max_size):
                return legacy_holes(mask, area_threshold=max_size + 1)
            monkeypatch.setattr(atlas, "_HOLES_MAX_SIZE", True)
            monkeypatch.setattr(atlas.morphology, "remove_small_holes", inclusive_holes)
    mask = np.ones((6, 10), dtype=bool)
    mask[1, 1:3] = False  # N-1
    mask[3, 1:4] = False  # N
    mask[1, 5:9] = False  # N+1
    expected = mask.copy()
    expected[1, 1:3] = True
    np.testing.assert_array_equal(atlas._remove_small_holes(mask, min_size=3), expected)
