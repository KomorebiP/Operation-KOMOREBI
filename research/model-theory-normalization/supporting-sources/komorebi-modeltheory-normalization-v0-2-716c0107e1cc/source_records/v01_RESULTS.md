# Retained results — M1 / v0.1

## Lean

PASS: six library modules rebuilt in an empty local build directory, eleven
expected-outcome tasks, 119 named library declarations axiom-audited. The four
new modules contain 44 theorem declarations. The two inherited semantic modules
are unchanged. Observed foundations: Classical.choice, Quot.sound, propext.
No additional project axiom, sorryAx, or Lean.ofReduceBool. The positive control
passes; the false, placeholder, and invalid quantified-transfer controls fail.

Recorded cold-run seconds: 6.448424. This is one measured execution, not a performance
guarantee. The exact argv, return codes, input/output hashes, and logs are in
results/LEAN_AUDIT.json and LEAN_MANIFEST.json.

## Finite Python reference

PASS: 78011 exact check calls across 100 finite systems. Exhaustive scope: all
64 two-state systems with two labelled actions and one binary observation.
Other scope: 36 seeded/boundary systems of sizes 1..6, including empty action or
observation signatures. Source formulas are sampled at recursive depth <=5;
quantified formulas are sampled at depth <=4 with 0,1,2 free variables.

| Check | Count |
|---|---:|
| delayed observation next step | 65 |
| delayed observation prefix | 65 |
| finite code formula exact | 802 |
| finite code local certificate | 100 |
| finite code quantifier rank | 100 |
| full inequality sentence boundary | 1 |
| invalid syntax rejection | 1 |
| nonseparating predicate boundary | 1 |
| nonsurjective quantifier boundary | 1 |
| normalization retraction | 6,400 |
| normalization truth | 16,256 |
| path transport | 16,256 |
| premature code rejected | 1 |
| quantified surjective transport | 36,992 |
| quotient vs independent pair search | 802 |
| resource cap inconclusive | 1 |
| separate rank and horizon | 65 |
| state equality boundary | 1 |
| surjectivity | 100 |
| word order negative control | 1 |

The pair-search reference independently checks behavioral equivalence, not just a
finite word horizon. The Python local-code contract checks all state pairs in its
finite source. Quantifier evaluations exhaust the state witnesses of their finite
systems; formula selection is sampled, not exhaustive over all formulas.

The universal normalization and logical-fragment claims come from Lean. No
learned proposer, held-out discovery benchmark, general quantifier elimination,
full-type equivalence, or Python-to-Lean program extraction is asserted.

## Provenance

LEAN_MANIFEST.json and COMPUTATION_MANIFEST.json are validated version-2 evidence
records with accepted input hashes before and after execution. The official
manifest validator is retained as tools/validate_manifest.py, copied from the
predecessor. It validates evidence structure and hashes, not mathematical truth.
The original predecessor archive is retained. Only two selected inherited modules
were replayed, not the full historical representation or p-adic suites.
