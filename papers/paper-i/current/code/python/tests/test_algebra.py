import sympy as sp

from seed_calculus.algebra import elliptic_packet_matrix, elliptic_product, elliptic_reduce, x, y


def test_elliptic_normal_form() -> None:
    expression = (x**2 + y) * (x - y)
    assert sp.expand(elliptic_reduce(expression) - (x + (x - x**2) * y)) == 0


def test_elliptic_packet_product() -> None:
    even, odd = elliptic_product(x**2, 1, x, -1)
    assert sp.expand(even - x) == 0
    assert sp.expand(odd - (x - x**2)) == 0


def test_y_packet_matrix_relation() -> None:
    my = elliptic_packet_matrix("y")
    assert my**2 == sp.eye(2) * (x**3 - x)


def test_x_and_y_commute_in_packet_model() -> None:
    mx = elliptic_packet_matrix("x")
    my = elliptic_packet_matrix("y")
    assert mx * my == my * mx
