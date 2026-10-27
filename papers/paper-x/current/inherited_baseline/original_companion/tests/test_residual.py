from projector_seed_residuals.residual import (
    compatible_residue_tower,
    first_separation_depth,
    full_digit_levels,
    partition_by_residual,
    positive_depth_perturbation_preserves_root,
    reconstruct_digits,
)


def test_residual_partition_is_disjoint_and_exhaustive() -> None:
    objects = list(range(15))
    partition = partition_by_residual(objects, 3)
    assert set(partition) == {0, 1, 2}
    flattened = [value for values in partition.values() for value in values]
    assert sorted(flattened) == objects
    assert all(value % 3 == root for root, values in partition.items() for value in values)


def test_no_crossing_positive_depth() -> None:
    for p in (2, 3, 5, 7):
        for a in range(15):
            for correction in range(-5, 6):
                assert positive_depth_perturbation_preserves_root(a, correction, p)


def test_compatible_inverse_limit_digits() -> None:
    p = 5
    digits = [2, 4, 1, 3, 0, 2]
    residues = []
    value = 0
    for index, digit in enumerate(digits):
        value += digit * p**index
        residues.append(value % p ** (index + 1))
    assert compatible_residue_tower(residues, p)
    assert reconstruct_digits(residues, p) == digits


def test_incompatible_tower_rejected() -> None:
    residues = [1, 7, 8]
    assert not compatible_residue_tower(residues, 3)


def test_dyadic_delayed_sign_separation() -> None:
    assert first_separation_depth(1, -1, 2, 8) == 2
    assert 1 % 2 == (-1) % 2
    assert 1 % 4 != (-1) % 4


def test_full_digit_level_counts() -> None:
    levels = full_digit_levels(3, 4)
    assert [len(level) for level in levels] == [3, 9, 27, 81]
