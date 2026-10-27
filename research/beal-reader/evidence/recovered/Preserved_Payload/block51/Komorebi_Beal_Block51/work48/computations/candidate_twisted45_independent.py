#!/usr/bin/env python3
"""Independent norm-four test for the sole retained level-norm-45 form.

This does not construct the proposed twist or prove its lowered level.
"""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "source_records/candidate_lmfdb_45_a.html"
SEARCH = ROOT / "source_records/candidate_lmfdb_45_search.html"
LOOKUP = ROOT / "verification/candidate_level45_form_lookup.json"
REPORT = ROOT / "notes/candidate_twisted45_audit.md"
OUTPUT = ROOT / "verification/candidate_twisted45_independent.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", fragment)).split())


def square(poly):
    result = [0] * (2*len(poly)-1)
    for i, a in enumerate(poly):
        for j, b in enumerate(poly):
            result[i+j] += a*b
    return result


def main():
    source = PAGE.read_text()
    text = clean(source)
    label = "2.2.5.1-45.1-a"
    assert "Hilbert cusp form "+label in text
    assert "Weight $[2, 2]$ Level norm $45$ Level $[45, 15, -6 w + 3]$" in text
    assert r"The Hecke eigenvalue field is $\Q$" in text
    search = SEARCH.read_text()
    assert "The results below are complete" in search
    assert set(re.findall(r'>(45\.1-[a-z]+)</a>', search)) == {"45.1-a"}
    assert "Results (unique match)" in clean(search)
    rows = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", source, re.S):
        cells = [clean(cell) for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) == 3 and cells[0].isdigit():
            rows.append({"norm": int(cells[0]), "prime_ideal": cells[1],
                         "eigenvalue": cells[2].replace("$", "").replace(r"\phantom{-}", "").replace(" ", "")})
    assert len(rows) == 20
    norm4 = [row for row in rows if row["norm"] == 4]
    assert len(norm4) == 1 and norm4[0]["prime_ideal"] == "$[4, 2, 2]$"
    trace = int(norm4[0]["eigenvalue"])
    assert trace == -3
    lookup = json.loads(LOOKUP.read_text())
    assert lookup["sha256"] == sha(PAGE)
    assert lookup["url"].endswith("/"+label)

    # All polynomials below are stored in ascending coefficient order.
    candidate_quadratic = [4, -trace, 1]
    candidate_full = square(candidate_quadratic)
    odd_checks = []
    for parity, old_trace in (([0, 1], -1), ([1, 0], 0)):
        new_trace = -old_trace  # Assumed twist value at this K-prime is -1.
        twisted_quadratic = [4, -new_trace, 1]
        twisted_full = square(twisted_quadratic)
        matches = [c % 7 for c in candidate_full] == [c % 7 for c in twisted_full]
        resultant = 4*(trace-new_trace)**2
        assert not matches and resultant % 7 != 0
        odd_checks.append({"A_B_parity": parity, "original_trace": old_trace,
                           "twisted_trace": new_trace,
                           "twisted_full_polynomial_ascending": twisted_full,
                           "full_polynomial_matches_mod7": matches,
                           "quadratic_resultant": resultant,
                           "quadratic_resultant_mod7": resultant % 7})
    even_checks = [{"twisted_eigenvalue": root,
                    "candidate_polynomial_value_mod7": (root*root-trace*root+4) % 7}
                   for root in (1, 4)]
    assert all(row["candidate_polynomial_value_mod7"] for row in even_checks)
    assert trace % 7 not in (1, 0, 5)

    inputs = [PAGE, SEARCH, LOOKUP,
              ROOT.parent / "work46/mod7_oddC_written_proof.md",
              ROOT.parent / "work47/notes/evenC_torus_frobenius.md"]
    result = {
        "status": "independent_finite_twisted_norm45_test_passed",
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 work48/computations/candidate_twisted45_independent.py",
        "script_sha256": sha(Path(__file__)),
        "audit_report_sha256": sha(REPORT),
        "input_sha256": {str(path.relative_to(ROOT.parent)): sha(path) for path in inputs},
        "label": label,
        "level_norm": 45,
        "displayed_level_ideal": "[45, 15, -6 w + 3]",
        "search_unique_match": True,
        "norm4_trace": trace,
        "norm4_trace_mod7": trace % 7,
        "candidate_quadratic_polynomial_ascending": candidate_quadratic,
        "candidate_full_polynomial_ascending": candidate_full,
        "hecke_rows": rows,
        "odd_C_checks": odd_checks,
        "even_C_checks": even_checks,
        "allowed_traces_mod7_under_twist_hypothesis": {"odd_C": [1, 0], "even_C": [5]},
        "conditional_conclusion": "No parity branch can match this level-norm-45 form under the stated twist and modular-comparison hypotheses.",
        "assumed_inputs_not_established_by_this_check": [
            "The twisting character is quadratic and unramified at the K-prime (2) of norm four, with value -1 on its Frobenius.",
            "There is a direct, normalized mod-seven comparison of the twisted rank-two Frey representation to a weight-two trivial-nebentypus newform of the exact displayed level of norm45.",
            "The established odd-C full Frobenius polynomials and even-C eigenvalues at norm four apply to the untwisted representation.",
            "The rank-two representation and its underlying four-dimensional J[7] realization have the previously stated lattice-semisimplification compatibility.",
            "The imported complete database search and exact eigenvalues are accepted as primary data."
        ],
        "not_claimed": [
            "Existence or arithmetic construction of the proposed twist.",
            "Proof of the twist's Frobenius value, conductor, level lowering, or modular attachment.",
            "Applicability of the exact norm45 level to a hypothetical solution.",
            "Independent computation of a Hilbert modular form space.",
            "An unconditional elimination or a Diophantine nonexistence theorem."
        ]
    }
    OUTPUT.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "label": label, "a4": trace,
                      "odd_resultants_mod7": [r["quadratic_resultant_mod7"] for r in odd_checks],
                      "even_polynomial_values_mod7": [r["candidate_polynomial_value_mod7"] for r in even_checks],
                      "output_sha256": sha(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
