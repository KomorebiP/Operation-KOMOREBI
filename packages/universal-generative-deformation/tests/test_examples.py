from generative_deformation.examples import catalan_numbers, fibonacci_numbers


def test_catalan_prefix() -> None:
    assert catalan_numbers(7) == [1, 1, 2, 5, 14, 42, 132, 429]


def test_fibonacci_prefix() -> None:
    assert fibonacci_numbers(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_negative_count_rejected() -> None:
    try:
        catalan_numbers(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative count was not rejected")
