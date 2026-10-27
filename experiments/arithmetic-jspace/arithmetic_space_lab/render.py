from __future__ import annotations

import random
import re
from dataclasses import dataclass
from fractions import Fraction
from math import lcm
from typing import Any

from .core import Problem, SYMBOLS, ast_expression, format_number, parse_number, weighted_choice


SYSTEM_PROMPT = "Solve the arithmetic problem exactly."


@dataclass(frozen=True)
class Task:
    task_type: str
    prompt_style: str
    template_id: str
    prompt: str
    target: str
    proposed_answer: str | None = None
    hidden_operand: str | None = None


def task_from_dict(value: dict[str, Any], task_type: str) -> Task:
    return Task(
        task_type=task_type,
        prompt_style=value["prompt_style"],
        template_id=value["template_id"],
        prompt=value["prompt"],
        target=value["target"],
        proposed_answer=value.get("proposed_answer"),
        hidden_operand=value.get("hidden_operand"),
    )


def _simple_operands(problem: Problem) -> tuple[str, str] | None:
    args = problem.ast.get("args", [])
    if len(args) != 2 or any(arg.get("type") != "number" for arg in args):
        return None
    return args[0]["value"], args[1]["value"]


def _compute_target(problem: Problem) -> str:
    if problem.operation_family == "div_remainder":
        return f"{problem.answer} remainder {problem.remainder}"
    return problem.answer


def _operation_word(problem: Problem) -> str:
    return {
        "add": "plus",
        "sub": "minus",
        "mul": "times",
        "div_exact": "divided by",
        "div_remainder": "divided by",
        "fraction_add": "plus",
        "fraction_sub": "minus",
        "fraction_mul": "times",
        "fraction_div": "divided by",
    }.get(problem.operation_family, "evaluated with")


def _compute_prompt(
    problem: Problem,
    style: str,
    rng: random.Random | None = None,
    variant: int | None = None,
) -> tuple[str, str]:
    variants = rng.randrange(3) if variant is None and rng is not None else variant
    if variants not in {0, 1, 2}:
        raise ValueError("prompt variant must be 0, 1, or 2")
    if style == "symbolic":
        templates = (
            "Compute: {expression}.",
            "Evaluate {expression}.",
            "Find the exact value of {expression}.",
        )
        if problem.operation_family == "div_remainder":
            templates = (
                "Divide {expression} and give the quotient and remainder.",
                "Find the quotient and remainder for {expression}.",
                "Compute {expression}; report quotient and remainder.",
            )
        return templates[variants].format(expression=problem.expression), f"compute_symbolic_v{variants + 1}"
    if style == "equation":
        suffix = " = ?"
        if problem.operation_family == "div_remainder":
            suffix = " = ? (quotient and remainder)"
        return problem.expression + suffix, f"compute_equation_v{variants + 1}"
    if style == "structured":
        requirement = "exact_value"
        if problem.operation_family == "div_remainder":
            requirement = "quotient_and_remainder"
        prompts = (
            f"[TASK] compute [EXPRESSION] {problem.expression} [OUTPUT] {requirement}",
            f"operation: {problem.operation_family}\nexpression: {problem.expression}\nreturn: {requirement}",
            f"<compute> {problem.expression} </compute> <return>{requirement}</return>",
        )
        return prompts[variants], f"compute_structured_v{variants + 1}"
    operands = _simple_operands(problem)
    if operands is None or problem.operation_family == "mixed":
        templates = (
            "What is the exact value of {expression}?",
            "Calculate the following expression exactly: {expression}.",
            "Work out {expression}.",
        )
        return templates[variants].format(expression=problem.expression), f"compute_verbal_v{variants + 1}"
    left, right = operands
    word = _operation_word(problem)
    if problem.operation_family == "div_remainder":
        prompts = (
            f"What quotient and remainder result when {left} is divided by {right}?",
            f"Divide {left} by {right}. Give both the quotient and remainder.",
            f"How many groups of {right} fit into {left}, and what remains?",
        )
    else:
        prompts = (
            f"What is {left} {word} {right}?",
            f"Calculate {left} {word} {right}.",
            f"Find {left} {word} {right}.",
        )
    return prompts[variants], f"compute_verbal_v{variants + 1}"


def _display_literal(value: str) -> str:
    return f"({value})" if value.startswith("-") or "/" in value else value


def _missing_equation(problem: Problem, hidden_operand: str) -> tuple[str, str]:
    operands = _simple_operands(problem)
    if operands is None or hidden_operand not in {"left", "right"}:
        raise ValueError("invalid missing-operand specification")
    left, right = operands
    hide_left = hidden_operand == "left"
    hidden = left if hide_left else right
    shown_left = "?" if hide_left else _display_literal(left)
    shown_right = "?" if not hide_left else _display_literal(right)
    symbol = SYMBOLS[problem.ast["op"]]
    return f"{shown_left} {symbol} {shown_right} = {_display_literal(problem.answer)}", hidden


def _missing_prompt_text(equation: str, style: str, variant: int) -> str:
    if style == "structured":
        prompts = (
            f"[TASK] solve_missing_operand [EQUATION] {equation}",
            f"task: missing_operand\nequation: {equation}\nreturn: missing_value",
            f"<missing-operand> {equation} </missing-operand>",
        )
    elif style == "verbal":
        prompts = (
            f"Which number makes this equation true: {equation}?",
            f"Find the missing number in {equation}.",
            f"What value should replace the question mark in {equation}?",
        )
    else:
        prompts = (
            f"Solve for ?: {equation}.",
            f"Complete the equation: {equation}.",
            equation,
        )
    return prompts[variant]


def _missing_task(problem: Problem, style: str, rng: random.Random) -> Task | None:
    operands = _simple_operands(problem)
    if operands is None or problem.operation_family == "div_remainder":
        return None
    left_value = parse_number(operands[0])
    right_value = parse_number(operands[1])
    if problem.ast["op"] == "mul" and (left_value == 0 or right_value == 0):
        return None
    if problem.ast["op"] == "div" and left_value == 0:
        return None
    hidden_operand = "left" if rng.random() < 0.5 else "right"
    equation, hidden = _missing_equation(problem, hidden_operand)
    variant = rng.randrange(3)
    return Task(
        task_type="missing_operand",
        prompt_style=style,
        template_id=f"missing_{style}_v{variant + 1}",
        prompt=_missing_prompt_text(equation, style, variant),
        target=hidden,
        hidden_operand=hidden_operand,
    )


def _perturb(answer: str, rng: random.Random) -> str:
    value = parse_number(answer)
    offset = Fraction(rng.choice((-3, -2, -1, 1, 2, 3)), max(1, value.denominator))
    return format_number(value + offset)


def _verification_prompt_text(statement: str, style: str, variant: int) -> str:
    if style == "structured":
        prompts = (
            f"[TASK] verify [STATEMENT] {statement} [OUTPUT] true_or_false",
            f"task: verify\nstatement: {statement}\nreturn: true_or_false",
            f"<verify> {statement} </verify>",
        )
    else:
        prompts = (
            f"Is this statement true or false? {statement}",
            f"Verify the equation {statement}. Answer true or false.",
            f"Determine whether {statement} is true or false.",
        )
    return prompts[variant]


def _verify_task(problem: Problem, style: str, rng: random.Random) -> Task | None:
    if problem.operation_family == "div_remainder":
        return None
    correct = rng.random() < 0.5
    proposed = problem.answer if correct else _perturb(problem.answer, rng)
    statement = f"{problem.expression} = {proposed}"
    variant = rng.randrange(3)
    return Task(
        task_type="verify",
        prompt_style=style,
        template_id=f"verify_{style}_v{variant + 1}",
        prompt=_verification_prompt_text(statement, style, variant),
        target="true" if correct else "false",
        proposed_answer=proposed,
    )


def make_task(
    problem: Problem,
    rng: random.Random,
    task_weights: dict[str, float],
    style_weights: dict[str, float],
) -> Task:
    task_type = weighted_choice(rng, task_weights)
    style = weighted_choice(rng, style_weights)
    if task_type == "missing_operand":
        task = _missing_task(problem, style, rng)
        if task is not None:
            return task
    if task_type == "verify":
        task = _verify_task(problem, style, rng)
        if task is not None:
            return task
    prompt, template_id = _compute_prompt(problem, style, rng)
    return Task(
        task_type="compute",
        prompt_style=style,
        template_id=template_id,
        prompt=prompt,
        target=_compute_target(problem),
    )


def _format_trace_step(step: dict[str, Any]) -> str:
    if step["op"] == "div_remainder":
        return (
            f"{step['left_value']} = {step['right_value']} × {step['result']} "
            f"+ {step['remainder']}"
        )
    symbol = SYMBOLS[step["op"]]
    return f"{step['left_value']} {symbol} {step['right_value']} = {step['result']}"


def _integer_addition_lines(left: int, right: int) -> list[str]:
    lines: list[str] = []
    carry = 0
    place = 1
    a = left
    b = right
    while a or b or carry:
        left_digit = a % 10
        right_digit = b % 10
        incoming = carry
        total = left_digit + right_digit + incoming
        digit = total % 10
        carry = total // 10
        lines.append(
            f"place {place}: {left_digit} + {right_digit} + carry {incoming} = {total}; "
            f"write {digit}, carry {carry}"
        )
        a //= 10
        b //= 10
        place *= 10
    return lines or ["place 1: 0 + 0 + carry 0 = 0; write 0, carry 0"]


def _integer_subtraction_lines(left: int, right: int) -> list[str]:
    lines: list[str] = []
    borrow = 0
    place = 1
    a = left
    b = right
    digits = max(len(str(left)), len(str(right)))
    for _ in range(digits):
        left_digit = a % 10
        right_digit = b % 10
        incoming = borrow
        adjusted = left_digit - incoming
        if adjusted < right_digit:
            adjusted += 10
            borrow = 1
        else:
            borrow = 0
        digit = adjusted - right_digit
        lines.append(
            f"place {place}: {left_digit} - {right_digit} - borrow {incoming}; "
            f"write {digit}, borrow {borrow}"
        )
        a //= 10
        b //= 10
        place *= 10
    return lines


def _integer_multiplication_lines(left: int, right: int) -> list[str]:
    partials: list[int] = []
    lines: list[str] = []
    for index, digit_text in enumerate(reversed(str(right))):
        digit = int(digit_text)
        place = 10**index
        partial = left * digit * place
        partials.append(partial)
        lines.append(f"partial {index + 1}: {left} × {digit} × {place} = {partial}")
    if len(partials) > 1:
        lines.append("sum partials: " + " + ".join(map(str, partials)) + f" = {sum(partials)}")
    return lines


def _fraction_lines(problem: Problem, left: Fraction, right: Fraction) -> list[str]:
    op = problem.ast["op"]
    if op in {"add", "sub"}:
        denominator = lcm(left.denominator, right.denominator)
        left_scaled = left.numerator * (denominator // left.denominator)
        right_scaled = right.numerator * (denominator // right.denominator)
        symbol = SYMBOLS[op]
        return [
            f"common denominator: lcm({left.denominator}, {right.denominator}) = {denominator}",
            f"{format_number(left)} = {left_scaled}/{denominator}",
            f"{format_number(right)} = {right_scaled}/{denominator}",
            f"{left_scaled}/{denominator} {symbol} {right_scaled}/{denominator} = {problem.answer}",
        ]
    if op == "mul":
        raw_numerator = left.numerator * right.numerator
        raw_denominator = left.denominator * right.denominator
        return [
            f"multiply numerators: {left.numerator} × {right.numerator} = {raw_numerator}",
            f"multiply denominators: {left.denominator} × {right.denominator} = {raw_denominator}",
            f"reduce {raw_numerator}/{raw_denominator} to {problem.answer}",
        ]
    raw_numerator = left.numerator * right.denominator
    raw_denominator = left.denominator * right.numerator
    if raw_denominator < 0:
        raw_numerator = -raw_numerator
        raw_denominator = -raw_denominator
    reciprocal = format_number(Fraction(right.denominator, right.numerator))
    return [
        f"multiply by the reciprocal: {format_number(left)} × {reciprocal}",
        f"combine: ({left.numerator} × {right.denominator})/"
        f"({left.denominator} × {right.numerator}) = {raw_numerator}/{raw_denominator}",
        f"reduce {raw_numerator}/{raw_denominator} to {problem.answer}",
    ]


def algorithm_lines(problem: Problem) -> list[str]:
    operands = _simple_operands(problem)
    if operands is None:
        return [_format_trace_step(step) for step in problem.trace]
    left = parse_number(operands[0])
    right = parse_number(operands[1])
    if problem.operation_family == "div_remainder":
        return [_format_trace_step(problem.trace[0])]
    if left.denominator != 1 or right.denominator != 1:
        return _fraction_lines(problem, left, right)
    left_int = int(left)
    right_int = int(right)
    op = problem.ast["op"]
    if op == "add" and left_int >= 0 and right_int >= 0:
        return _integer_addition_lines(left_int, right_int)
    if op == "sub" and left_int >= right_int >= 0:
        return _integer_subtraction_lines(left_int, right_int)
    if op == "mul" and left_int >= 0 and right_int >= 0:
        return _integer_multiplication_lines(left_int, right_int)
    if op == "div" and right_int != 0 and left_int % right_int == 0:
        quotient = left_int // right_int
        return [
            f"check the inverse: {right_int} × {quotient} = {left_int}",
            f"therefore {left_int} ÷ {right_int} = {quotient}",
        ]
    return [_format_trace_step(step) for step in problem.trace]


def render_response(problem: Problem, task: Task, response_mode: str) -> str:
    if response_mode == "answer_only":
        return task.target
    if response_mode == "equation":
        if task.task_type == "compute":
            return f"{problem.expression} = {task.target}"
        if task.task_type == "missing_operand":
            return f"? = {task.target}"
        return f"{problem.expression} = {task.proposed_answer}: {task.target}"
    if response_mode != "worked_trace":
        raise ValueError(f"unknown response mode: {response_mode}")
    if task.task_type == "compute":
        equations = algorithm_lines(problem)
        return "\n".join(equations + [f"Answer: {task.target}"])
    if task.task_type == "missing_operand":
        side = task.hidden_operand or "operand"
        return f"Solving for the missing {side} operand gives {task.target}.\nAnswer: {task.target}"
    truth = "matches" if task.target == "true" else "does not match"
    return (
        f"{problem.expression} = {problem.answer}. This {truth} the proposed value "
        f"{task.proposed_answer}.\nAnswer: {task.target}"
    )


def expected_task_target(problem: Problem, task: Task) -> str:
    if task.task_type == "compute":
        return _compute_target(problem)
    if task.task_type == "missing_operand":
        operands = _simple_operands(problem)
        if operands is None or task.hidden_operand not in {"left", "right"}:
            raise ValueError("invalid missing-operand task")
        left = parse_number(operands[0])
        right = parse_number(operands[1])
        if problem.ast["op"] == "mul" and (left == 0 or right == 0):
            raise ValueError("underdetermined zero-product missing-operand task")
        if problem.ast["op"] == "div" and left == 0:
            raise ValueError("underdetermined zero-dividend missing-operand task")
        return operands[0] if task.hidden_operand == "left" else operands[1]
    if task.task_type == "verify":
        if task.proposed_answer is None:
            raise ValueError("verification task lacks a proposed answer")
        return "true" if parse_number(task.proposed_answer) == parse_number(problem.answer) else "false"
    raise ValueError(f"unknown task type: {task.task_type}")


def expected_task_prompt(problem: Problem, task: Task) -> str:
    match = re.fullmatch(
        r"(compute|missing|verify)_(symbolic|verbal|equation|structured)_v([123])",
        task.template_id,
    )
    if match is None:
        raise ValueError("invalid template identifier")
    kind, style, variant_text = match.groups()
    if style != task.prompt_style:
        raise ValueError("template style does not match task prompt style")
    variant = int(variant_text) - 1
    expected_kind = {
        "compute": "compute",
        "missing_operand": "missing",
        "verify": "verify",
    }.get(task.task_type)
    if kind != expected_kind:
        raise ValueError("template kind does not match task type")
    if task.task_type == "compute":
        return _compute_prompt(problem, style, variant=variant)[0]
    if task.task_type == "missing_operand":
        if task.hidden_operand is None:
            raise ValueError("missing-operand task lacks hidden side")
        equation, _ = _missing_equation(problem, task.hidden_operand)
        return _missing_prompt_text(equation, style, variant)
    if task.proposed_answer is None:
        raise ValueError("verification task lacks proposed answer")
    statement = f"{problem.expression} = {task.proposed_answer}"
    return _verification_prompt_text(statement, style, variant)


def choose_response_mode(regime: dict[str, Any], rng: random.Random) -> str:
    return weighted_choice(rng, regime["response_modes"])
