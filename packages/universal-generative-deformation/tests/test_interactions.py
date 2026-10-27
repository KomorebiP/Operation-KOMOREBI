from generative_deformation import InteractionRule, ScalarInteractionSystem, generate_interactions


def test_binary_addition_interactions() -> None:
    output = generate_interactions([1, 2, 3], [InteractionRule("add", 2)], ScalarInteractionSystem())
    values = {item[2] for item in output}
    assert {2, 3, 4, 5, 6}.issubset(values)


def test_binary_multiplication_interactions() -> None:
    output = generate_interactions([2, 3], [InteractionRule("multiply", 2)], ScalarInteractionSystem())
    values = {item[2] for item in output}
    assert values == {4, 6, 9}


def test_interaction_limit() -> None:
    output = generate_interactions(
        list(range(20)), [InteractionRule("add", 2)], ScalarInteractionSystem(), limit=7
    )
    assert len(output) == 7
