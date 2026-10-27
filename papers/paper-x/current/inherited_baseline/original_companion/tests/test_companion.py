from projector_seed_residuals.companion import (
    build_root_forest,
    enumerate_branches,
    roots_mod_prime_power,
    transition_is_surjective,
)


def test_x2_plus_1_companion_forests() -> None:
    expected = {
        2: [1, 0, 0, 0],
        3: [0, 0, 0, 0],
        5: [2, 2, 2, 2],
        7: [0, 0, 0, 0],
        13: [2, 2, 2, 2],
    }
    for p, counts in expected.items():
        forest = build_root_forest([1, 0, 1], p, 4)
        assert [len(level) for level in forest.levels] == counts


def test_simple_roots_lift_uniquely() -> None:
    for p in (5, 13):
        forest = build_root_forest([1, 0, 1], p, 5)
        assert len(enumerate_branches(forest)) == 2
        assert all(transition_is_surjective(forest, level) for level in range(4))


def test_singular_square_branches() -> None:
    forest = build_root_forest([1, 0, 0], 3, 6)  # x^2 = 0
    assert [len(level) for level in forest.levels] == [1, 3, 3, 9, 9, 27]
    assert len(enumerate_branches(forest)) == 27


def test_root_enumerator_exact() -> None:
    assert roots_mod_prime_power([1, -1], 5, 3) == [1]
