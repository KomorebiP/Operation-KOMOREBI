"""Finite integer coefficient-transfer checks, adapted from the recovered bridge.

The bridge archive is separately preserved in the full handoff. No transform
of the rapidly growing Euler sequence and no general supercongruence is asserted.
"""
import json
from math import comb


def multiply(a: list[int], b: list[int]) -> list[int]:
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


def transfer_row(modulus: int, phase: int, order: int) -> list[int]:
    result = [comb(phase, j) for j in range(phase+1)]
    block = [0] + [comb(modulus, j) for j in range(1, modulus+1)]
    for _ in range(order):
        result = multiply(result, block)
    return result


def difference(values: list[int], order: int, start: int = 0, stride: int = 1) -> int:
    return sum((-1)**(order-j)*comb(order,j)*values[start+stride*j] for j in range(order+1))


def main() -> None:
    euler = [1]
    for n in range(1,48):
        euler.append(-sum(comb(2*n,2*j)*euler[j] for j in range(n)))
    coefficients = [difference(euler,r) for r in range(48)]
    cases = 0
    for modulus in range(1,6):
        for phase in range(modulus):
            for order in range(7):
                row=transfer_row(modulus,phase,order)
                actual=sum(weight*coefficients[r] for r,weight in enumerate(row))
                assert actual==difference(euler,order,phase,modulus)
                cases+=1
    print(json.dumps({"status":"PASS","finite_integer_transfer_cases":cases,
                      "initial_euler_values":euler[:5],
                      "first_difference_at_spacings_1_2_4":[difference(euler,1,stride=m) for m in (1,2,4)]},indent=2))


if __name__ == '__main__':
    main()
