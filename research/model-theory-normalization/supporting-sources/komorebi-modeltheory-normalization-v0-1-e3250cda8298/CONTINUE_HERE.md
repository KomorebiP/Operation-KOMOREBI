# Continue from M1 / Model-Theory Normalization v0.1

Read NORMALIZED_CORE.md, FORMALIZATION_COVERAGE.md, PROOF_AUDIT.md, and RESULTS.md.
Run distribution integrity before overwriting any execution records. Preserve the
v0.4 frozen predecessor and every current proof boundary.

This is a new scoped model-theory branch, not Representation Calculus v0.5 or
p-adic Block 16. Current checked core: path normalizer, observation-fragment types,
quantified preservation for surjective transports with no state equality, explicit
finite-code defining formula, and stronger-language counterexamples.

Next central obligation: map ObsFO into a conventional FirstOrder language,
using a many-sorted presentation or tagged single-sorted interpretation with
appropriate sort guards and nonemptiness hypotheses, and prove satisfaction
commutes. Do not claim elementary preservation with unrestricted state equality.

Then add actual matrix-certificate-derived finite test lists and compile their
codeRelationFormula automatically. The certificate must check immediate outputs
and step stability, or derive them from previously proved matrix obligations.

Do not claim quantifier elimination merely because behavior equals a fragment
type. Do not confuse quantifier rank with term horizon. Do not infer that an
infinite-test relation lacks any first-order definition: the stream example is
defined by state equality in the larger language. Do not claim elimination of
imaginaries from one particular certified code.

Audit command:
  python tools/audit_all.py --lean /absolute/path/to/lean

No build is still running. Runtime/cache bytes are excluded from the release.
