#!/usr/bin/env python3
"""Independent exact local audit of all fourteen norm-2025 Hilbert candidates.

Uses only the Python standard library.  The imported Block47 certificate is
compared only after all point counts have been independently recomputed.
No code from the original point-count or candidate-check scripts is imported.
"""

from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "work47/verification/modular_correlations.json"
OUTPUT = ROOT / "verification/candidate_independent_q11.json"
REPORT = ROOT / "notes/candidate_independent_audit.md"
Q = 11
P = 7


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# F_121 = F_11[u]/(u^2-2), encoding a+b*u as a+11*b.
def add(x, y, q=Q):
    return (x % q + y % q) % q + q * ((x // q + y // q) % q)


def multiply(x, y, q=Q):
    a, b = x % q, x // q
    c, d = y % q, y // q
    return (a*c + 2*b*d) % q + q * ((a*d + b*c) % q)


def power(x, n, q=Q):
    result = 1
    while n:
        if n & 1:
            result = multiply(result, x, q)
        x = multiply(x, x, q)
        n //= 2
    return result


def strip_tags(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", fragment)).split())


def read_form(suffix):
    path = ROOT / f"source_records/candidate_lmfdb_2025_{suffix}.html"
    source = path.read_text()
    label = f"2.2.5.1-2025.1-{suffix}"
    assert f"Hilbert cusp form {label}" in source
    # Authenticate the exact defining polynomial, independently of page labels.
    fragment = source.split("root of the defining polynomial:", 1)[1]
    match = re.search(r"x\^2\s*([+-])\s*(\d+)\s*x\s*\+\s*(\d+)", fragment)
    assert match is not None
    b = int(match.group(2)) * (1 if match.group(1) == "+" else -1)
    c = int(match.group(3))
    rows = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", source, re.S):
        cells = [strip_tags(v) for v in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) == 3 and cells[0] == "11":
            value = cells[2].replace("$", "").replace(r"\phantom{-}", "").replace(" ", "")
            rows.append({"prime_ideal": cells[1], "eigenvalue": value})
    other_root = f"-e{-b:+d}"
    assert len(rows) == 2
    assert {r["eigenvalue"] for r in rows} == {"e", other_root}
    assert (b, c) == ({"h": (9, 19), "l": (-9, 19)}[suffix])
    return path, {"label": label, "coefficient_polynomial_ascending": [c, b, 1],
                  "norm11_hecke_rows": rows}, b, c


def count_all_smooth_pairs(q=Q):
    squares = {x*x % q for x in range(1, q)}
    assert 2 not in squares
    extension_squares = {multiply(x, x, q) for x in range(1, q*q)}
    assert len(extension_squares) == (q*q-1)//2
    assert all(power(x, q*q-1, q) == 1 for x in range(1, q*q))
    powers = [(x, power(x, 3, q), power(x, 6, q)) for x in range(q*q)]
    pairs = [(a, b) for a in range(q) for b in range(q) if (a**3+b**5) % q]
    assert len(pairs) == q*(q-1)
    records = []
    for a, b in pairs:
        # The leading coefficient is one: there are two rational infinity points.
        n1 = 2
        for x in range(q):
            f = (x**6 + 10*b*x**3 + 12*a*x + 5*b*b) % q
            n1 += 1 + (0 if f == 0 else (1 if f in squares else -1))
        n2 = 2
        for x, x3, x6 in powers:
            f = add(add(add(x6, multiply(10*b % q, x3, q), q),
                        multiply(12*a % q, x, q), q), 5*b*b % q, q)
            n2 += 1 + (0 if f == 0 else (1 if f in extension_squares else -1))
        s1 = q + 1 - n1
        numerator = s1*s1 - (q*q + 1) + n2
        assert numerator % 2 == 0
        s2 = numerator // 2
        polynomial = [q*q, -q*s1, s2, -s1, 1]
        records.append({"A": a, "B": b, "N1": n1, "N2": n2,
                        "jacobian_frobenius_polynomial_ascending": polynomial})
    return records


def square_polynomial(q, trace):
    return [q*q, -2*q*trace, trace*trace+2*q, -2*trace, 1]


def audit_complete_level():
    """Parse every retained page and independently implement the local sieve."""
    search = ROOT / "source_records/candidate_lmfdb_2025_search.html"
    search_source = search.read_text()
    search_labels = set(re.findall(r'>(2025\.1-[a-n])</a>', search_source))
    assert search_labels == {"2025.1-"+suffix for suffix in "abcdefghijklmn"}
    assert "The results below are complete" in search_source
    expected4 = [0, 3, 4, -4, 1, 0, -2, 0, 3, -2, -3, 0, -2, 2]
    inputs = [search]
    all_forms = []
    for suffix, expected in zip("abcdefghijklmn", expected4):
        path = ROOT / f"source_records/candidate_lmfdb_2025_{suffix}.html"
        source = path.read_text()
        label = "2.2.5.1-2025.1-"+suffix
        assert "Hilbert cusp form "+label in source
        assert "Weight $[2, 2]$ Level norm $2025$ Level $[2025, 45, 45]$" in strip_tags(source)
        rows = []
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", source, re.S):
            cells = [strip_tags(v) for v in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(cells) == 3 and cells[0].isdigit():
                rows.append({"norm": int(cells[0]), "prime_ideal": cells[1],
                             "eigenvalue": cells[2].replace("$", "").replace(r"\phantom{-}", "").replace(" ", "")})
        assert len(rows) == 20
        values4 = [r["eigenvalue"] for r in rows if r["norm"] == 4]
        assert values4 == [str(expected)]
        trace4 = int(values4[0])
        odd_parities = []
        target = [v % P for v in square_polynomial(4, trace4)]
        for parity, trace in (([0, 1], -1), ([1, 0], 0)):
            if target == [v % P for v in square_polynomial(4, trace)]:
                odd_parities.append(parity)
        # Even C gives full eigenvalues -1 and -4 at norm four.  A rank-two
        # modular polynomial with determinant four must have these two roots:
        # repeated choices have determinant one or two modulo seven, not four.
        even_match = all((root*root-trace4*root+4) % P == 0 for root in (-1, -4))
        all_forms.append({"label": label, "norm4_trace": trace4,
                          "odd_C_compatible_A_B_parities": odd_parities,
                          "even_C_compatible": even_match, "hecke_rows": rows})
        inputs.append(path)
    odd = [f["label"][-1] for f in all_forms if f["odd_C_compatible_A_B_parities"]]
    even = [f["label"][-1] for f in all_forms if f["even_C_compatible"]]
    assert odd == list("afhl") and even == ["n"]

    extra = []
    for suffix, q, trace in (("a", 19, -5), ("f", 29, 10)):
        form = next(f for f in all_forms if f["label"].endswith("-"+suffix))
        assert [int(r["eigenvalue"]) for r in form["hecke_rows"] if r["norm"] == q] == [trace, trace]
        records = count_all_smooth_pairs(q)
        target = square_polynomial(q, trace)
        matches = [[r["A"], r["B"]] for r in records
                   if all((x-y) % P == 0 for x, y in zip(r["jacobian_frobenius_polynomial_ascending"], target))]
        bad_match = trace % P in ((q+1) % P, (-q-1) % P)
        assert not matches and not bad_match
        extra.append({"label": form["label"], "q": q, "trace": trace,
                      "smooth_pair_count": len(records), "point_count_records": records,
                      "target_full_polynomial_ascending": target,
                      "smooth_matching_pairs": matches, "multiplicative_branch_match": bad_match})

    n = next(f for f in all_forms if f["label"].endswith("-n"))
    n_source = (ROOT / "source_records/candidate_lmfdb_2025_n.html").read_text()
    assert r"\(x^2 - 18\)" in n_source
    assert [r["eigenvalue"] for r in n["hecke_rows"] if r["norm"] == 11] == ["-e", "e"]
    roots = [x for x in range(P) if (x*x-18) % P == 0]
    assert roots == [2, 5]
    correlations = []
    for root in roots:
        left = [v % P for v in square_polynomial(11, -root)]
        right = [v % P for v in square_polynomial(11, root)]
        assert left != right
        correlations.append({"fixed_coefficient_residue_e": root,
                             "first_base_prime_full_polynomial_mod7": left,
                             "second_base_prime_full_polynomial_mod7": right,
                             "equal": False})
    return inputs, {"forms": all_forms, "odd_C_survivors_after_norm4": odd,
                    "even_C_survivors_after_norm4": even,
                    "additional_full_point_count_exclusions": extra,
                    "n_fixed_prime_correlation_checks": correlations,
                    "conditional_only_remaining_orbit": "2.2.5.1-2025.1-l"}


def main():
    records = count_all_smooth_pairs()
    # Imported certificate plays no role in the enumeration or point counts.
    previous = json.loads(PREVIOUS.read_text())["q11_complete_smooth_Beal_point_counts"]
    previous_by_pair = {(r["A"], r["B"]): r for r in previous}
    assert len(previous) == len(previous_by_pair) == len(records)
    assert set(previous_by_pair) == {(r["A"], r["B"]) for r in records}
    for record in records:
        old = previous_by_pair[(record["A"], record["B"])]
        assert (record["N1"], record["N2"]) == (old["N1"], old["N2"])
        assert record["jacobian_frobenius_polynomial_ascending"] == old["jacobian_frobenius_polynomial"]

    inputs = [PREVIOUS,
              ROOT.parent / "work46/mod7_oddC_written_proof.md",
              ROOT.parent / "work47/notes/evenC_torus_frobenius.md"]
    forms = []
    for suffix in ("h", "l"):
        path, form, b, c = read_form(suffix)
        inputs.append(path)
        # e+e'=-b and ee'=c: norm(T^2-e*T+q).
        polynomial = [Q*Q, Q*b, 2*Q+c, b, 1]
        residue = [v % P for v in polynomial]
        matches = [[r["A"], r["B"]] for r in records
                   if [v % P for v in r["jacobian_frobenius_polynomial_ascending"]] == residue]
        bad_evaluations = [{"trace": t, "minimal_polynomial_value_mod7": (t*t+b*t+c) % P}
                           for t in (Q+1, -Q-1)]
        roots_in_f7 = [x for x in range(P) if (x*x+b*x+c) % P == 0]
        assert not roots_in_f7
        assert all(r["minimal_polynomial_value_mod7"] for r in bad_evaluations)
        assert matches == ({"h": [], "l": [[5, 0], [6, 0]]}[suffix])
        form.update({"coefficient_discriminant": b*b-4*c,
                     "coefficient_polynomial_roots_in_F7": roots_in_f7,
                     "restriction_of_scalars_polynomial_ascending": polynomial,
                     "restriction_of_scalars_polynomial_mod7_ascending": residue,
                     "smooth_matching_pairs_mod11": matches,
                     "multiplicative_branch_checks": bad_evaluations,
                     "multiplicative_branch_match": False})
        forms.append(form)

    level_inputs, level_checks = audit_complete_level()
    inputs = list(dict.fromkeys(inputs + level_inputs))
    result = {
        "status": "independent_exact_norm2025_candidate_check_passed",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 work48/computations/candidate_independent_q11.py",
        "script_sha256": digest(Path(__file__)),
        "audit_report_sha256": digest(REPORT),
        "input_sha256": {str(path.relative_to(ROOT.parent)): digest(path) for path in inputs},
        "arithmetic": "Python integers; F(q^2)=Fq[u]/(u^2-2) for q=11,19,29; no imported arithmetic libraries",
        "enumeration": "Every (A,B) in F11^2 with A^3+B^5 nonzero",
        "smooth_pair_count": len(records),
        "previous_certificate_mismatches": 0,
        "independence": "All point counts recomputed without importing previous implementations; author-supplied targets checked afterward",
        "forms": forms,
        "point_count_records": records,
        "complete_level_checks": level_checks,
        "conditional_conclusions": [
            "A direct residual congruence to h modulo seven is impossible, for either parity of C.",
            "A direct residual congruence to l modulo seven forces 11|B and A congruent to 5 or 6 modulo 11.",
            "Among all fourteen listed weight-two trivial-nebentypus forms of level (45), only l can be directly congruent to the Frey representation modulo seven.",
            "Combined with separately established two-adic and l-specific nineteen restrictions, l forces C odd, A odd, and 418|B."
        ],
        "proof_inputs_not_formalized_by_this_script": [
            "Same-normalization direct rank-two modular comparison with weight-two trivial-nebentypus forms.",
            "Restriction of scalars of the residual rank-two Frey representation has the semisimplified J[7] representation.",
            "The full Frobenius polynomial follows from the two point counts for the smooth genus-two model.",
            "For q|C with q=11,19,29, the standard multiplicative-prime comparison forces modular trace +(q+1) or -(q+1) modulo seven.",
            "The established norm-four Frobenius polynomials for odd C and eigenvalues -1,-4 for even C.",
            "The rational Jacobian's full residual characteristic polynomials agree on conjugate Frobenius lifts at the two K-primes above eleven; n is unramified there.",
            "LMFDB's complete level-(45) list covers the fourteen imported weight-two, trivial-nebentypus Galois orbits.",
            "Database eigenvalues are accepted as primary imported data; no independent Hilbert-space computation is performed."
        ],
        "out_of_scope": [
            "No numerical PV-to-LMFDB index dictionary or elimination at the other three possible levels.",
            "No fresh verification here of the two-adic input or l-specific nineteen implication.",
            "No proof of existence of a modular comparison, or of Diophantine nonexistence.",
            "No inference that a displayed CM=yes flag is a proved CM classification."
        ]
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "smooth_pairs": len(records),
                      "previous_certificate_mismatches": 0,
                      "matches": {f["label"]: f["smooth_matching_pairs_mod11"] for f in forms},
                      "output": str(OUTPUT), "output_sha256": digest(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
