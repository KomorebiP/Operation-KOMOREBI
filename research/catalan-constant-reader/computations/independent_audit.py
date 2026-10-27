#!/usr/bin/env python3
"""Independent finite arithmetic checks and certified diagnostic data.

Only Python integer/Fraction operations decide assertions. Float logarithms
and decimal strings are explicitly display fields. No irrationality claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path


def recurrence(max_n: int) -> tuple[list[F], list[F]]:
    """Separate construction, with output index k rather than source index n."""
    a, b = [F(1), F(7, 4)], [F(0), F(13, 8)]
    for k in range(2, max_n + 1):
        j = k - 1
        p_prev = 20*j*j - 8*j + 1
        p_next = 20*k*k - 8*k + 1
        middle = ((((((3520*j + 5632)*j + 2064)*j - 384)*j - 156)*j + 16)*j + 7)
        leading = (2*k-1)**2 * (2*k)**2 * p_prev
        trailing = (2*k-3)**2 * (2*k-2)**2 * p_next
        a.append((middle*a[-1] + trailing*a[-2])/leading)
        b.append((middle*b[-1] + trailing*b[-2])/leading)
    return a[:max_n+1], b[:max_n+1]


def v2(value: int) -> int:
    if not value:
        raise ValueError("zero has no finite 2-adic valuation")
    return (abs(value) & -abs(value)).bit_length()-1


def decimal(value: F, digits: int = 35) -> str:
    with localcontext() as ctx:
        ctx.prec = digits
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def log10_display(value: F | int) -> float:
    value = F(value)
    return (math.log(abs(value.numerator))-math.log(value.denominator))/math.log(10)


def catalan_interval(last_euler_index: int) -> tuple[F, F, dict]:
    """Certified using integral positivity of forward differences.

    a_k = integral_0^1 x^(2k)(-log x) dx = 1/(2k+1)^2.
    Delta^j a_0 = integral_0^1 (1-x^2)^j(-log x) dx is in [0,1].
    G = sum_j>=0 Delta^j a_0 / 2^(j+1).
    Hence retaining j=0..N leaves a tail in [0,2^(-N-1)].
    The finite identities are checked here. The displayed integral argument is
    a separate elementary analytic justification of the certified tail.
    """
    row = [F(1, (2*k+1)**2) for k in range(last_euler_index+1)]
    total = F(0)
    positive = True
    for j in range(last_euler_index+1):
        positive = positive and 0 <= row[0] <= 1
        total += row[0]/(1 << (j+1))
        row = [x-y for x,y in zip(row, row[1:])]
    assert positive
    width = F(1, 1 << (last_euler_index+1))
    return total, total+width, {
        "last_euler_index": last_euler_index,
        "lower": str(total), "upper": str(total+width),
        "certified_width": str(width), "finite_differences_in_0_1": positive,
        "display_decimal_lower": decimal(total, 80),
        "display_decimal_upper": decimal(total+width, 80),
        "tail_justification": "Delta^j a0 = integral (1-x^2)^j(-log x) dx lies in [0,1]; tail geometric sum <= 2^(-N-1)",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    historical_code = Path("computations/catalan_packet_audit.py")
    spec = importlib.util.spec_from_file_location("historical", historical_code)
    historical = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(historical)

    max_k = 500
    u, v = recurrence(max_k)
    old_u, old_v = historical.zudilin_sequences(max_k)
    assert u == old_u and v == old_v
    T = [u[k]*16**k for k in range(max_k+1)]
    assert all(x.denominator == 1 for x in T)
    T = [x.numerator for x in T]
    assert T == historical.t_sequence(max_k)
    assert all(x > 0 for x in T)
    ell = 1
    denominator_failures = []
    for k in range(max_k+1):
        if k:
            ell = math.lcm(ell, 2*k-1, 2*k)
        if (8*ell*ell*16**k*v[k]).denominator != 1:
            denominator_failures.append(k)
    assert not denominator_failures

    # Compare every pair, not merely two summary maxima. The exact direct
    # binomial sum is orthogonal to Pascal's additive row evolution.
    max_n = 100
    mod = 1 << 128
    row = [x % mod for x in T]
    pascal = {}
    for m in range(4*max_n+1):
        for n in range(max(1, (m+3)//4), max_n+1):
            assert row[n] != 0
            pascal[n, m] = (row[n], v2(row[n]))
        if m < 4*max_n:
            row = [(x+y) % mod for x,y in zip(row, row[1:])]
    grid, prefix = [], []
    running = -1
    direct_argmax = None
    for n in range(1, max_n+1):
        entries = []
        for m in range(4*n+1):
            direct = sum(math.comb(m, i)*T[n+i] for i in range(m+1))
            vv = v2(direct)
            assert pascal[n,m] == (direct % mod, vv)
            entries.append(vv)
            if vv > running:
                running = vv
                direct_argmax = [n,m]
        grid.append({"n": n, "m_min": 0, "m_max": 4*n, "v2": entries})
        prefix.append({"n_max": n, "maximum_v2": running, "first_argmax_n_m": direct_argmax})

    # Exact interval certifies small diagnostic error signs. 1001 Euler terms
    # suffice to control cancellation in n<=20,m<=4n raw packet forms.
    Glo, Ghi, Ginterval = catalan_interval(1000)
    approximants = []
    for n in [0,1,2,5,10,20,40]:
        r = v[n]/u[n]
        low, high = Glo-r, Ghi-r
        assert low*high > 0
        sign = 1 if low > 0 else -1
        lo_abs, hi_abs = sorted([abs(low),abs(high)])
        approximants.append({
            "n": n, "u": str(u[n]), "v": str(v[n]), "v_over_u": str(r),
            "error_G_minus_v_over_u_lower": str(low),
            "error_G_minus_v_over_u_upper": str(high),
            "error_sign": sign, "display_approximation": decimal(r),
            "display_abs_error_lower": decimal(lo_abs),
            "display_abs_error_upper": decimal(hi_abs),
            "display_log10_abs_error_lower": log10_display(lo_abs),
            "display_log10_abs_error_upper": log10_display(hi_abs),
        })

    filter_grid, sign_mismatches = [], []
    for n in range(1,21):
        for m in range(4*n+1):
            su = sum(math.comb(m,i)*T[n+i] for i in range(m+1))
            sv = sum((math.comb(m,i)*16**(n+i)*v[n+i] for i in range(m+1)),F(0))
            # Raw filter F_(n,m)=8(-1)^n sum binom(m,i)16^(n+i)(u_(n+i)G-v_(n+i)).
            a, b = 8*(-1)**n*su, 8*(-1)**n*sv
            lower, upper = sorted([a*Glo-b, a*Ghi-b])
            assert lower*upper > 0
            observed_sign = 1 if lower > 0 else -1
            predicted = (-1)**m
            if observed_sign != predicted:
                sign_mismatches.append([n,m])
            lo_abs,hi_abs = sorted([abs(lower),abs(upper)])
            filter_grid.append({
                "n":n,"m":m,"certified_sign":observed_sign,
                "display_log10_abs_lower":log10_display(lo_abs),
                "display_log10_abs_upper":log10_display(hi_abs),
            })

    gcd_data = []
    for n,m in [(20,66),(30,100),(50,166),(70,232),(100,332)]:
        su = sum(math.comb(m,i)*T[n+i] for i in range(m+1))
        sv = sum((math.comb(m,i)*16**(n+i)*v[n+i] for i in range(m+1)),F(0))
        L = math.lcm(*range(1,2*(n+m)+1))
        Q = 8*L*L
        assert Q % sv.denominator == 0
        minimal_gcd = math.gcd(su,sv.numerator)
        redundant_scale = Q//sv.denominator
        content = redundant_scale*minimal_gcd
        A,B = historical.filtered_cleared_pair(n,m,u,v)
        assert math.gcd(abs(A),abs(B)) == content
        assert A == (-1)**n*Q*su and B == (-1)**n*Q*sv
        gcd_data.append({
            "n":n,"m":m,"sum_T":str(su),"sum_scaled_v_numerator":str(sv.numerator),
            "minimal_common_denominator":str(sv.denominator),
            "clearance_Q":str(Q),"redundant_scale_Q_over_D":str(redundant_scale),
            "minimal_pair_gcd":str(minimal_gcd),"cleared_gcd":str(content),
            "cleared_v2":v2(content),"display_log_gcd_over_n_plus_m":math.log(content)/(n+m),
            "display_log_Q_over_n_plus_m":math.log(Q)/(n+m),
            "display_log_D_over_n_plus_m":math.log(sv.denominator)/(n+m),
        })

    result = {
        "scope":"finite exact checks; certified intervals use separate elementary integral tail argument; no irrationality proof",
        "recurrence_independent":{"max_n":max_k,"u_v_match_historical":True,"T_matches_integer_recurrence":True,"T_integral_and_positive":True,"eight_L_2n_squared_scaled_v_integral":True,"denominator_failures":denominator_failures},
        "every_pair_direct_pascal":{"max_n":100,"m_bound":"0 <= m <= 4n","pairs":len(pascal),"modulus_bits":128,"all_residues_and_valuations_equal":True,"zero_residues":0,"maximum_v2":running,"first_argmax_n_m":direct_argmax},
        "certified_Catalan_interval":Ginterval,
        "raw_filter_sign_check":{"n_range":[1,20],"m_bound":"0 <= m <= 4n","pairs":len(filter_grid),"all_nonzero":True,"tested_pattern":"sign F_(n,m)=(-1)^m","pattern_mismatches":sign_mismatches,"interpretation":"finite verified pattern only; universal sign needs separate integral argument"},
        "gcd_decomposition":{"pairs":len(gcd_data),"formula":"gcd(Q su,Q sv)=(Q/D)*gcd(su,num sv), where D=den sv and su integer","all_match":True},
    }
    diagnostic = {"display_fields":"decimal strings and logarithms are rounded visual aids; integer/rational decision fields are exact","binomial_v2_grid":grid,"binomial_v2_prefix_maxima":prefix,"approximants":approximants,"raw_filter_grid":filter_grid,"cleared_gcd_decomposition":gcd_data}
    (out/"results.json").write_text(json.dumps(result,indent=2))
    (out/"diagnostic_data.json").write_text(json.dumps(diagnostic,indent=2))
    print(json.dumps({"recurrence":result["recurrence_independent"],"direct_pascal":result["every_pair_direct_pascal"],"filter":result["raw_filter_sign_check"],"gcd":result["gcd_decomposition"]},indent=2))


if __name__ == "__main__":
    main()
