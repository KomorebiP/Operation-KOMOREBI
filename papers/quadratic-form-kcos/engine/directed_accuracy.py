"""Directed interval decisions for the public multiplicative-accuracy contract.

Literal decimal endpoints are retained. Point arithmetic is used only for
display midpoints and never decides acceptance. mpmath.iv has a shared precision
context; these routines and the interval engine must be called sequentially.
"""
from dataclasses import dataclass
from decimal import (Decimal, InvalidOperation, localcontext, ROUND_FLOOR,
                     ROUND_CEILING, MAX_EMAX, MIN_EMIN)
import mpmath as mp
from mpmath import iv


def _outward_binary_endpoint(raw, *, rounding, digits):
    """Serialize an exact mpmath binary endpoint outward in decimal arithmetic."""
    sign, mantissa, exponent, bitcount = raw
    if bitcount < 0:
        if bitcount in (-2, -3):
            return "-inf" if sign else "+inf"
        raise ValueError("NaN interval endpoint cannot be certified")
    numerator = (-1 if sign else 1) * int(mantissa)
    if exponent >= 0:
        numerator <<= int(exponent)
        denominator = 1
    else:
        denominator = 1 << -int(exponent)
    with localcontext() as context:
        context.prec = int(digits)
        context.rounding = rounding
        context.Emax, context.Emin = MAX_EMAX, MIN_EMIN
        return str(Decimal(numerator) / Decimal(denominator))


def outward_interval_string(interval, *, digits=None) -> str:
    """Real enclosure of the binary endpoints; ordinary str(iv) is nearest.

    Uses mpmath 1.3.0's exact `_mpi_` endpoint tuples. Decimal division has
    independently specified lower/upper rounding directions.
    """
    lower, upper = interval._mpi_
    digits = int(iv.dps) + 10 if digits is None else int(digits)
    left = _outward_binary_endpoint(lower, rounding=ROUND_FLOOR, digits=digits)
    right = _outward_binary_endpoint(upper, rounding=ROUND_CEILING, digits=digits)
    return f"[{left}, {right}]"


def positive_decimal(value) -> str:
    text = str(value).strip()
    try:
        number = Decimal(text)
    except InvalidOperation as error:
        raise ValueError("accuracy must be a finite positive decimal") from error
    if not number.is_finite() or number <= 0:
        raise ValueError("accuracy must be a finite positive decimal")
    return text


def interval_endpoint_strings(text: str) -> tuple[str, str]:
    text = text.strip()
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError("expected a bracketed interval")
    left, right = (item.strip() for item in text[1:-1].split(",", 1))
    a, b = Decimal(left), Decimal(right)
    if a.is_nan() or b.is_nan() or a > b:
        raise ValueError("invalid ordered interval endpoints")
    return left, right


@dataclass(frozen=True)
class DirectedAccuracy:
    accepted: bool
    ratio_upper: str
    width_upper: str


def directed_relative_accuracy(log10_interval: str, requested, *, dps=120):
    eps_text = positive_decimal(requested)
    left, right = interval_endpoint_strings(log10_interval)
    if not Decimal(left).is_finite() or not Decimal(right).is_finite():
        return DirectedAccuracy(False, "inf", "inf")
    previous = iv.dps
    try:
        iv.dps = int(dps)
        width = iv.mpf(right) - iv.mpf(left)
        ratio = iv.expm1(iv.log(10) * width)
        eps = iv.mpf(eps_text)
        # Compare the proven upper ratio against the proven lower tolerance.
        accepted = bool(ratio.b <= eps.a)
        _, ratio_upper = interval_endpoint_strings(outward_interval_string(ratio))
        _, width_upper = interval_endpoint_strings(outward_interval_string(width))
        return DirectedAccuracy(accepted, ratio_upper, width_upper)
    finally:
        iv.dps = previous


def scaled_accuracy_budget(requested, fraction, *, dps=120) -> str:
    eps_text = positive_decimal(requested)
    frac_text = positive_decimal(fraction)
    if Decimal(frac_text) >= 1:
        raise ValueError("tail_accuracy_fraction must lie in (0,1)")
    previous = iv.dps
    try:
        iv.dps = int(dps)
        product = iv.mpf(eps_text) * iv.mpf(frac_text)
        lower, _ = interval_endpoint_strings(outward_interval_string(product))
        return lower
    finally:
        iv.dps = previous


def interval_midpoint(log10_interval: str, *, dps=120) -> str:
    left, right = interval_endpoint_strings(log10_interval)
    with mp.workdps(int(dps)):
        return mp.nstr((mp.mpf(left) + mp.mpf(right)) / 2, 40)
