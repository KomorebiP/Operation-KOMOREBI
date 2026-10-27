from __future__ import annotations

import random
import unittest
from fractions import Fraction

from arithmetic_space_lab.core import (
    Problem,
    _relation_key,
    carry_features,
    evaluate_ast,
    format_number,
    generate_problem,
    parse_number,
    trace_ast,
    verify_trace,
)
from arithmetic_space_lab.render import algorithm_lines


POLICY = {
    "allow_negative_operands": True,
    "negative_probability": 0.2,
    "allow_negative_subtraction": True,
    "include_identities": False,
    "max_mixed_depth": 3,
}


class CoreTests(unittest.TestCase):
    def test_exact_fraction(self) -> None:
        self.assertEqual(format_number(Fraction(6, 8)), "3/4")
        self.assertEqual(parse_number("-10/15"), Fraction(-2, 3))

    def test_ast_exact(self) -> None:
        ast = {
            "type": "operation",
            "op": "div",
            "args": [
                {"type": "number", "value": "2"},
                {"type": "number", "value": "3"},
            ],
        }
        self.assertEqual(evaluate_ast(ast), Fraction(2, 3))
        self.assertEqual(trace_ast(ast)[0]["result"], "2/3")

    def test_inverse_family_key(self) -> None:
        add_key = _relation_key("add", Fraction(3), Fraction(4), Fraction(7))
        sub_key = _relation_key("sub", Fraction(7), Fraction(3), Fraction(4))
        self.assertEqual(add_key, sub_key)
        mul_key = _relation_key("mul", Fraction(3), Fraction(4), Fraction(12))
        div_key = _relation_key("div", Fraction(12), Fraction(3), Fraction(4))
        self.assertEqual(mul_key, div_key)

    def test_carry_features(self) -> None:
        self.assertEqual(carry_features(58, 67), (2, 2))
        self.assertEqual(carry_features(12, 23), (0, 0))

    def test_all_operations_generate_valid_problems(self) -> None:
        operations = [
            "add",
            "sub",
            "mul",
            "div_exact",
            "div_remainder",
            "fraction_add",
            "fraction_sub",
            "fraction_mul",
            "fraction_div",
            "mixed",
        ]
        for index, operation in enumerate(operations):
            with self.subTest(operation=operation):
                problem = generate_problem(operation, 4, random.Random(100 + index), POLICY)
                verify_trace(problem)
                if operation == "mixed":
                    self.assertGreaterEqual(problem.difficulty["ast_depth"], 1)
                    self.assertGreaterEqual(problem.difficulty["operation_count"], 1)

    def test_algorithmic_carry_trace(self) -> None:
        problem = generate_problem("add", 2, random.Random(7), POLICY)
        verify_trace(problem)
        lines = algorithm_lines(problem)
        self.assertTrue(lines)
        self.assertTrue(any("carry" in line for line in lines))

    def test_negative_subtraction_policy_covers_fractions_and_mixed_nodes(self) -> None:
        policy = dict(POLICY)
        policy["allow_negative_subtraction"] = False
        policy["negative_probability"] = 1.0
        for index in range(100):
            fraction_problem = generate_problem("fraction_sub", 4, random.Random(index), policy)
            self.assertGreaterEqual(parse_number(fraction_problem.answer), 0)
            mixed_problem = generate_problem("mixed", 4, random.Random(1000 + index), policy)
            for step in mixed_problem.trace:
                if step["op"] == "sub":
                    self.assertGreaterEqual(parse_number(step["result"]), 0)


if __name__ == "__main__":
    unittest.main()
