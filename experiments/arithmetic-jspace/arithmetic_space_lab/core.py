from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable


COMMUTATIVE = {"add", "mul"}
SYMBOLS = {"add": "+", "sub": "-", "mul": "×", "div": "÷", "divmod": "÷"}


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def seeded_rng(*parts: Any) -> random.Random:
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    total = sum(float(value) for value in weights.values())
    point = rng.random() * total
    running = 0.0
    for key, value in sorted(weights.items()):
        running += float(value)
        if point < running:
            return key
    return next(reversed(weights))


def format_number(value: Fraction | int) -> str:
    fraction = value if isinstance(value, Fraction) else Fraction(value)
    if fraction.denominator == 1:
        return str(fraction.numerator)
    return f"{fraction.numerator}/{fraction.denominator}"


def parse_number(value: str) -> Fraction:
    return Fraction(value)


def number_digits(value: Fraction | int) -> int:
    fraction = value if isinstance(value, Fraction) else Fraction(value)
    return max(len(str(abs(fraction.numerator))), len(str(fraction.denominator)))


def carry_features(a: int, b: int) -> tuple[int, int]:
    if a < 0 or b < 0:
        return 0, 0
    carry = 0
    count = 0
    longest = 0
    chain = 0
    while a or b or carry:
        digit_sum = a % 10 + b % 10 + carry
        carry = int(digit_sum >= 10)
        if carry:
            count += 1
            chain += 1
            longest = max(longest, chain)
        else:
            chain = 0
        a //= 10
        b //= 10
    return count, longest


def borrow_features(a: int, b: int) -> tuple[int, int]:
    if a < 0 or b < 0 or a < b:
        return 0, 0
    borrow = 0
    count = 0
    longest = 0
    chain = 0
    while a or b:
        top = a % 10 - borrow
        bottom = b % 10
        if top < bottom:
            borrow = 1
            count += 1
            chain += 1
            longest = max(longest, chain)
        else:
            borrow = 0
            chain = 0
        a //= 10
        b //= 10
    return count, longest


def normalize_ast(node: dict[str, Any]) -> dict[str, Any]:
    if node["type"] == "number":
        return {"type": "number", "value": format_number(parse_number(node["value"]))}
    children = [normalize_ast(child) for child in node["args"]]
    if node["op"] in COMMUTATIVE:
        children.sort(key=lambda child: json.dumps(child, sort_keys=True, separators=(",", ":")))
    return {"type": node["type"], "op": node["op"], "args": children}


def evaluate_ast(node: dict[str, Any]) -> Fraction:
    if node["type"] == "number":
        return parse_number(node["value"])
    if node["type"] == "divmod":
        left = evaluate_ast(node["args"][0])
        right = evaluate_ast(node["args"][1])
        if left.denominator != 1 or right.denominator != 1 or right <= 0 or left < 0:
            raise ValueError("divmod AST requires a nonnegative integer dividend and positive integer divisor")
        quotient, _ = divmod(int(left), int(right))
        return Fraction(quotient)
    left = evaluate_ast(node["args"][0])
    right = evaluate_ast(node["args"][1])
    op = node["op"]
    if op == "add":
        return left + right
    if op == "sub":
        return left - right
    if op == "mul":
        return left * right
    if op == "div":
        if right == 0:
            raise ZeroDivisionError("zero divisor in AST")
        return left / right
    raise ValueError(f"unknown AST operation: {op}")


def ast_expression(node: dict[str, Any], outer: bool = True) -> str:
    if node["type"] == "number":
        return node["value"]
    left_node, right_node = node["args"]
    left = ast_expression(left_node, False)
    right = ast_expression(right_node, False)
    if left_node["type"] == "number" and (left.startswith("-") or "/" in left):
        left = f"({left})"
    if right_node["type"] == "number" and (right.startswith("-") or "/" in right):
        right = f"({right})"
    expression = f"{left} {SYMBOLS[node['op']]} {right}"
    return expression if outer else f"({expression})"


def trace_ast(node: dict[str, Any]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []

    def visit(current: dict[str, Any]) -> tuple[str, Fraction]:
        if current["type"] == "number":
            value = parse_number(current["value"])
            return format_number(value), value
        left_label, left_value = visit(current["args"][0])
        right_label, right_value = visit(current["args"][1])
        value = evaluate_ast(current)
        label = f"t{len(steps) + 1}"
        steps.append(
            {
                "index": len(steps) + 1,
                "label": label,
                "op": current["op"],
                "left": left_label,
                "right": right_label,
                "left_value": format_number(left_value),
                "right_value": format_number(right_value),
                "result": format_number(value),
            }
        )
        return label, value

    visit(node)
    return steps


@dataclass(frozen=True)
class Problem:
    operation_family: str
    ast: dict[str, Any]
    answer: str
    answer_type: str
    expression: str
    family_key: str
    difficulty: dict[str, Any]
    trace: list[dict[str, Any]]
    remainder: str | None = None

    @property
    def family_id(self) -> str:
        return stable_hash(self.family_key)

    @property
    def relation_ids(self) -> list[str]:
        if self.operation_family == "div_remainder":
            return [stable_hash(expected_problem_family_key(self))]
        return sorted({stable_hash(key) for key in ast_relation_keys(self.ast)})


def _digit_bounds(level: int) -> tuple[int, int]:
    digits = max(1, min(level, 9))
    lower = 0 if digits == 1 else 10 ** (digits - 1)
    upper = 10**digits - 1
    return lower, upper


def _sample_unsigned(rng: random.Random, level: int, minimum: int = 0) -> int:
    low, high = _digit_bounds(level)
    return rng.randint(max(low, minimum), high)


def _maybe_signed(value: int, rng: random.Random, level: int, policy: dict[str, Any]) -> int:
    if level >= 3 and policy.get("allow_negative_operands", False):
        if rng.random() < float(policy.get("negative_probability", 0.0)):
            return -value
    return value


def _leaf(value: Fraction | int) -> dict[str, str]:
    return {"type": "number", "value": format_number(value)}


def _binary(op: str, left: Fraction | int, right: Fraction | int) -> dict[str, Any]:
    return {"type": "operation", "op": op, "args": [_leaf(left), _leaf(right)]}


def _relation_key(op: str, left: Fraction, right: Fraction, result: Fraction) -> str:
    if op == "add":
        terms = sorted((format_number(left), format_number(right)))
        return f"add_relation:{terms[0]}:{terms[1]}:{format_number(result)}"
    if op == "sub":
        terms = sorted((format_number(right), format_number(result)))
        return f"add_relation:{terms[0]}:{terms[1]}:{format_number(left)}"
    if op == "mul":
        factors = sorted((format_number(left), format_number(right)))
        return f"mul_relation:{factors[0]}:{factors[1]}:{format_number(result)}"
    if op == "div":
        factors = sorted((format_number(right), format_number(result)))
        return f"mul_relation:{factors[0]}:{factors[1]}:{format_number(left)}"
    raise ValueError(op)


def expected_problem_family_key(problem: Problem) -> str:
    if problem.operation_family == "div_remainder":
        if problem.ast.get("type") != "divmod" or problem.ast.get("op") != "divmod":
            raise ValueError("div_remainder problem requires a divmod AST")
        left = evaluate_ast(problem.ast["args"][0])
        right = evaluate_ast(problem.ast["args"][1])
        if left.denominator != 1 or right.denominator != 1 or left < 0 or right <= 0:
            raise ValueError("invalid divmod operands")
        quotient, remainder = divmod(int(left), int(right))
        if remainder == 0:
            return _relation_key("div", left, right, Fraction(quotient))
        return f"div_remainder:{int(left)}:{int(right)}:{quotient}:{remainder}"
    if problem.operation_family == "mixed":
        normalized = normalize_ast(problem.ast)
        return "mixed:" + json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    expected_ops = {
        "add": "add",
        "sub": "sub",
        "mul": "mul",
        "div_exact": "div",
        "fraction_add": "add",
        "fraction_sub": "sub",
        "fraction_mul": "mul",
        "fraction_div": "div",
    }
    expected_op = expected_ops.get(problem.operation_family)
    if expected_op is None or problem.ast.get("type") != "operation" or problem.ast.get("op") != expected_op:
        raise ValueError("operation family does not match AST operation")
    left = evaluate_ast(problem.ast["args"][0])
    right = evaluate_ast(problem.ast["args"][1])
    result = evaluate_ast(problem.ast)
    return _relation_key(expected_op, left, right, result)


def _difficulty(level: int, operation: str, left: Fraction, right: Fraction, answer: Fraction) -> dict[str, Any]:
    info: dict[str, Any] = {
        "level": level,
        "left_digits": number_digits(left),
        "right_digits": number_digits(right),
        "answer_digits": number_digits(answer),
        "signed": left < 0 or right < 0 or answer < 0,
    }
    if operation == "add" and left.denominator == right.denominator == 1:
        if left >= 0 and right >= 0:
            count, chain = carry_features(int(left), int(right))
            info.update({"carry_count": count, "longest_carry_chain": chain})
        else:
            info.update({"carry_count": None, "longest_carry_chain": None})
    if operation == "sub" and left.denominator == right.denominator == 1:
        if left >= right >= 0:
            count, chain = borrow_features(int(left), int(right))
            info.update({"borrow_count": count, "longest_borrow_chain": chain})
        else:
            info.update({"borrow_count": None, "longest_borrow_chain": None})
    return info


def expected_answer_type(problem: Problem) -> str:
    """Return the canonical answer-type label implied by a problem's arithmetic."""
    if problem.operation_family == "div_remainder":
        return "quotient_remainder"
    return "integer" if evaluate_ast(problem.ast).denominator == 1 else "fraction"


def expected_problem_difficulty(problem: Problem, level: int) -> dict[str, Any]:
    """Recompute all difficulty metadata from the semantic problem and its sampled level."""
    if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 9:
        raise ValueError("difficulty level must be an integer from 1 through 9")

    if problem.operation_family == "div_remainder":
        if problem.ast.get("type") != "divmod" or problem.ast.get("op") != "divmod":
            raise ValueError("div_remainder problem requires a divmod AST")
        dividend = evaluate_ast(problem.ast["args"][0])
        divisor = evaluate_ast(problem.ast["args"][1])
        if dividend.denominator != 1 or divisor.denominator != 1 or dividend < 0 or divisor <= 0:
            raise ValueError("invalid divmod operands")
        quotient, remainder = divmod(int(dividend), int(divisor))
        return {
            "level": level,
            "dividend_digits": len(str(int(dividend))),
            "divisor_digits": len(str(int(divisor))),
            "quotient_digits": len(str(quotient)),
            "has_remainder": remainder != 0,
        }

    if problem.operation_family == "mixed":
        result = evaluate_ast(problem.ast)
        leaves = [parse_number(value) for value in iter_numbers(problem.ast)]
        if not leaves:
            raise ValueError("mixed problem has no numeric leaves")
        return {
            "level": level,
            "ast_depth": _ast_depth(problem.ast),
            "operation_count": len(problem.trace),
            "answer_digits": number_digits(result),
            "signed": any(value < 0 for value in leaves)
            or any(parse_number(step["result"]) < 0 for step in problem.trace),
            "max_leaf_digits": max(number_digits(value) for value in leaves),
        }

    expected_ops = {
        "add": "add",
        "sub": "sub",
        "mul": "mul",
        "div_exact": "div",
        "fraction_add": "add",
        "fraction_sub": "sub",
        "fraction_mul": "mul",
        "fraction_div": "div",
    }
    operation = expected_ops.get(problem.operation_family)
    if operation is None or problem.ast.get("type") != "operation" or problem.ast.get("op") != operation:
        raise ValueError("operation family does not match AST operation")
    left = evaluate_ast(problem.ast["args"][0])
    right = evaluate_ast(problem.ast["args"][1])
    result = evaluate_ast(problem.ast)
    expected = _difficulty(level, operation, left, right, result)
    if problem.operation_family.startswith("fraction_"):
        expected["rational_operands"] = True
    return expected


def _simple_problem(operation: str, level: int, rng: random.Random, policy: dict[str, Any]) -> Problem:
    identity = bool(policy.get("include_identities", False))
    if operation in {"add", "sub"}:
        minimum = 0 if identity else 1
        left = _maybe_signed(_sample_unsigned(rng, level, minimum), rng, level, policy)
        right = _maybe_signed(_sample_unsigned(rng, level, minimum), rng, level, policy)
        if operation == "sub" and not policy.get("allow_negative_subtraction", False) and left < right:
            left, right = right, left
        ast = _binary(operation, left, right)
        result = evaluate_ast(ast)
    elif operation == "mul":
        factor_level = level
        minimum = 0 if identity else 2
        left = _maybe_signed(_sample_unsigned(rng, factor_level, minimum), rng, level, policy)
        right = _maybe_signed(_sample_unsigned(rng, factor_level, minimum), rng, level, policy)
        ast = _binary("mul", left, right)
        result = evaluate_ast(ast)
    elif operation == "div_exact":
        factor_level = level
        minimum = 1 if identity else 2
        divisor = _sample_unsigned(rng, factor_level, minimum)
        quotient = _sample_unsigned(rng, factor_level, minimum)
        quotient = _maybe_signed(quotient, rng, level, policy)
        dividend = divisor * quotient
        left, right = dividend, divisor
        ast = _binary("div", left, right)
        result = evaluate_ast(ast)
    else:
        raise ValueError(operation)
    family_key = _relation_key(ast["op"], Fraction(left), Fraction(right), result)
    return Problem(
        operation_family=operation,
        ast=ast,
        answer=format_number(result),
        answer_type="integer" if result.denominator == 1 else "fraction",
        expression=ast_expression(ast),
        family_key=family_key,
        difficulty=_difficulty(level, ast["op"], Fraction(left), Fraction(right), result),
        trace=trace_ast(ast),
    )


def _division_remainder_problem(level: int, rng: random.Random, policy: dict[str, Any]) -> Problem:
    divisor_level = level
    divisor = _sample_unsigned(rng, divisor_level, 2)
    quotient = _sample_unsigned(rng, divisor_level, 1)
    remainder = rng.randrange(divisor)
    dividend = divisor * quotient + remainder
    ast = {"type": "divmod", "op": "divmod", "args": [_leaf(dividend), _leaf(divisor)]}
    if remainder == 0:
        family_key = _relation_key("div", Fraction(dividend), Fraction(divisor), Fraction(quotient))
    else:
        family_key = f"div_remainder:{dividend}:{divisor}:{quotient}:{remainder}"
    trace = [
        {
            "index": 1,
            "label": "t1",
            "op": "div_remainder",
            "left": str(dividend),
            "right": str(divisor),
            "left_value": str(dividend),
            "right_value": str(divisor),
            "result": str(quotient),
            "remainder": str(remainder),
        }
    ]
    return Problem(
        operation_family="div_remainder",
        ast=ast,
        answer=str(quotient),
        answer_type="quotient_remainder",
        expression=f"{dividend} ÷ {divisor}",
        family_key=family_key,
        difficulty={
            "level": level,
            "dividend_digits": len(str(dividend)),
            "divisor_digits": len(str(divisor)),
            "quotient_digits": len(str(quotient)),
            "has_remainder": remainder != 0,
        },
        trace=trace,
        remainder=str(remainder),
    )


def _sample_fraction(
    rng: random.Random,
    level: int,
    policy: dict[str, Any],
    nonzero: bool = False,
) -> Fraction:
    denominator = rng.randint(2, min(50, 4 + level * 6))
    limit = min(200, 4 + level * 10)
    exclude_zero = nonzero or not policy.get("include_identities", False)
    numerator = rng.randint(1 if exclude_zero else 0, limit)
    if (
        level >= 3
        and policy.get("allow_negative_operands", False)
        and rng.random() < float(policy.get("negative_probability", 0.0))
    ):
        numerator = -numerator
    return Fraction(numerator, denominator)


def _fraction_problem(
    operation: str,
    level: int,
    rng: random.Random,
    policy: dict[str, Any],
) -> Problem:
    op = operation.removeprefix("fraction_")
    for _ in range(100):
        left = _sample_fraction(rng, level, policy, nonzero=op == "div")
        right = _sample_fraction(rng, level, policy, nonzero=op == "div")
        if policy.get("include_identities", False):
            break
        if op in {"add", "sub"} and left != 0 and right != 0:
            break
        if op == "mul" and abs(left) not in {0, 1} and abs(right) not in {0, 1}:
            break
        if op == "div" and left != 0 and abs(right) != 1:
            break
    else:
        raise RuntimeError("could not sample a non-identity fraction problem")
    if op == "sub" and not policy.get("allow_negative_subtraction", False) and left < right:
        left, right = right, left
    ast = _binary(op, left, right)
    result = evaluate_ast(ast)
    family_key = _relation_key(op, left, right, result)
    return Problem(
        operation_family=operation,
        ast=ast,
        answer=format_number(result),
        answer_type="integer" if result.denominator == 1 else "fraction",
        expression=ast_expression(ast),
        family_key=family_key,
        difficulty=_difficulty(level, op, left, right, result) | {"rational_operands": True},
        trace=trace_ast(ast),
    )


def _random_mixed_ast(level: int, rng: random.Random, policy: dict[str, Any]) -> dict[str, Any]:
    max_depth = max(2, min(int(policy.get("max_mixed_depth", 3)), 2 + level // 2))
    depth = rng.randint(2, max_depth)

    def build(remaining: int, force_operation: bool = False) -> dict[str, Any]:
        if remaining == 0 or (not force_operation and remaining > 1 and rng.random() < 0.20):
            value = _sample_unsigned(rng, max(1, min(level, 3)), 1)
            value = _maybe_signed(value, rng, level, policy)
            return _leaf(value)
        op = rng.choices(["add", "sub", "mul", "div"], weights=[3, 3, 2, 1], k=1)[0]
        left = build(remaining - 1)
        right = build(remaining - 1)
        if op == "sub" and not policy.get("allow_negative_subtraction", False):
            if evaluate_ast(left) < evaluate_ast(right):
                left, right = right, left
        if op == "div" and evaluate_ast(right) == 0:
            right = _leaf(rng.randint(1, 9))
        return {"type": "operation", "op": op, "args": [left, right]}

    for _ in range(100):
        node = build(depth, force_operation=True)
        value = evaluate_ast(node)
        if abs(value.numerator) <= 10**12 and value.denominator <= 100000:
            return node
    raise RuntimeError("could not sample bounded mixed expression")


def _mixed_problem(level: int, rng: random.Random, policy: dict[str, Any]) -> Problem:
    for _ in range(100):
        ast = _random_mixed_ast(level, rng, policy)
        candidate_trace = trace_ast(ast)
        operation_types = {step["op"] for step in candidate_trace}
        if len(candidate_trace) >= 2 and len(operation_types) >= 2:
            break
    else:
        raise RuntimeError("could not sample a genuinely mixed expression")
    result = evaluate_ast(ast)
    normalized = normalize_ast(ast)
    family_key = "mixed:" + json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    trace = candidate_trace
    return Problem(
        operation_family="mixed",
        ast=ast,
        answer=format_number(result),
        answer_type="integer" if result.denominator == 1 else "fraction",
        expression=ast_expression(ast),
        family_key=family_key,
        difficulty={
            "level": level,
            "ast_depth": _ast_depth(ast),
            "operation_count": len(trace),
            "answer_digits": number_digits(result),
            "signed": any(parse_number(value) < 0 for value in iter_numbers(ast))
            or any(parse_number(step["result"]) < 0 for step in trace),
            "max_leaf_digits": max(number_digits(parse_number(value)) for value in iter_numbers(ast)),
        },
        trace=trace,
    )


def _ast_depth(node: dict[str, Any]) -> int:
    if node["type"] == "number":
        return 0
    return 1 + max(_ast_depth(child) for child in node["args"])


def ast_relation_keys(node: dict[str, Any]) -> list[str]:
    if node["type"] == "number":
        return []
    left_node, right_node = node["args"]
    left = evaluate_ast(left_node)
    right = evaluate_ast(right_node)
    result = evaluate_ast(node)
    keys = ast_relation_keys(left_node) + ast_relation_keys(right_node)
    keys.append(_relation_key(node["op"], left, right, result))
    return keys


def generate_problem(operation: str, level: int, rng: random.Random, policy: dict[str, Any]) -> Problem:
    if operation in {"add", "sub", "mul", "div_exact"}:
        return _simple_problem(operation, level, rng, policy)
    if operation == "div_remainder":
        return _division_remainder_problem(level, rng, policy)
    if operation.startswith("fraction_"):
        return _fraction_problem(operation, level, rng, policy)
    if operation == "mixed":
        return _mixed_problem(level, rng, policy)
    raise ValueError(f"unknown operation: {operation}")


def split_for_family(family_id: str, seed: int, counts: dict[str, int]) -> str:
    active = sorted((name, count) for name, count in counts.items() if count > 0)
    total = sum(count for _, count in active)
    point = int(stable_hash(f"split|{seed}|{family_id}")[:16], 16) % total
    running = 0
    for name, count in active:
        running += count
        if point < running:
            return name
    return active[-1][0]


def verify_trace(problem: Problem) -> None:
    if problem.expression != ast_expression(problem.ast):
        raise ValueError("rendered expression does not match AST")
    if problem.operation_family == "div_remainder":
        step = problem.trace[0]
        a = int(step["left_value"])
        b = int(step["right_value"])
        q = int(step["result"])
        r = int(step["remainder"])
        ast_a = evaluate_ast(problem.ast["args"][0])
        ast_b = evaluate_ast(problem.ast["args"][1])
        if ast_a != a or ast_b != b:
            raise ValueError("divmod AST operands do not match trace operands")
        if b == 0:
            raise ValueError("zero divisor in quotient-remainder trace")
        if a != b * q + r or not 0 <= r < abs(b):
            raise ValueError("invalid quotient-remainder trace")
        ast_q, ast_r = divmod(int(ast_a), int(ast_b))
        if str(ast_q) != problem.answer:
            raise ValueError("divmod AST quotient does not match problem answer")
        if str(ast_r) != str(problem.remainder):
            raise ValueError("divmod AST remainder does not match problem remainder")
        expected_trace = [
            {
                "index": 1,
                "label": "t1",
                "op": "div_remainder",
                "left": str(a),
                "right": str(b),
                "left_value": str(a),
                "right_value": str(b),
                "result": str(q),
                "remainder": str(r),
            }
        ]
        if problem.trace != expected_trace:
            raise ValueError("quotient-remainder trace is incomplete or noncanonical")
        return
    expected = evaluate_ast(problem.ast)
    if format_number(expected) != problem.answer:
        raise ValueError("problem answer does not match AST")
    if problem.trace != trace_ast(problem.ast):
        raise ValueError("trace is incomplete, reordered, or noncanonical")
    if problem.operation_family == "mixed":
        operation_types = {step["op"] for step in problem.trace}
        if len(problem.trace) < 2 or len(operation_types) < 2:
            raise ValueError("mixed problem is not genuinely mixed")
    for step in problem.trace:
        left = parse_number(step["left_value"])
        right = parse_number(step["right_value"])
        node = _binary(step["op"], left, right)
        if format_number(evaluate_ast(node)) != step["result"]:
            raise ValueError(f"invalid trace step {step['index']}")


def iter_numbers(node: dict[str, Any]) -> Iterable[str]:
    if node["type"] == "number":
        yield node["value"]
    else:
        for child in node["args"]:
            yield from iter_numbers(child)
