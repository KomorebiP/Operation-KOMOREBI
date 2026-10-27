# First-order root motion verification contract

The target is `TARGET_CONTRACT.json`. For a prime p, the new theorem uses actual
square polynomial systems F,H over Z_p, an exact root a of F, and the actual
original Jacobian J = DF(a). The hypothesis is that J is invertible over Q_p
and p^s J inverse is integral. For natural M > 2s, the perturbed polynomial
system is G = F + p^M H. The target includes exactly one root in the full ball
of depth s+1, displacement depth M-s, and the first-order formula

    b-a = -p^M J inverse H(a) + epsilon,
    epsilon in p^(2M-3s) Z_p^d.

The rational identity and the integral error bound must refer to the same
constructed root. An estimate conditional on an assumed nearby root does not
complete this contract. The final expanded Lean statement contract writes out
the actual polynomial derivatives and G evaluation, so no abstract contraction,
normalization, root-existence hypothesis, or derivative surrogate can replace
the mathematical conclusion unnoticed.

The computational assertion is Lean kernel acceptance of the frozen theorem
sources and expanded statement contracts. This checks universally quantified
formal proofs. It is not a numerical sample, and the semantic identification
of the formal statement with the written mathematics also requires the separate
raw proof audit.

Run from the project root:

```bash
python3 scripts/verify_polynomial_motion.py \
  --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --output /path/to/a-new-run-directory
```

The output directory must not exist. Its build subdirectory starts empty, and
every active project module, positive control support, and statement contract
is compiled again in dependency order. Only the pinned Lean toolchain and
precompiled Mathlib dependencies are reused. The gate does not claim an
independent Lean kernel or a Mathlib rebuild.

The runner uses one compiler thread, a 240-second compiler timeout per source,
and warnings as errors. The outer gate subprocess timeout is 380 seconds;
partial timeout output is preserved. The source audit rejects unbounded
heartbeat or recursion settings, custom axioms, omitted proofs, unsafe
implementation shortcuts, and other listed bypasses. The shipped executable
path adapter is hash checked and used directly. It changes process path
discovery only, not the compiler, kernel, or proofs.

`inventory.json` freezes every active source, import, and declaration. Creating
it with `scripts/generate_inventory.py` is a release maintenance step, not a
verification result. The gate rejects missing final theorem and contract
modules, unexpected files, duplicate or unexpected declaration names, source
hash changes, and changes to the target or inventory during the run. Every
inventoried theorem, definition, and abbreviation receives an explicit
`#print axioms` query. Only `propext`, `Classical.choice`, and `Quot.sound` are
allowed. The parser preserves apostrophes in Lean names and has regression
checks for duplicate, mismatched, and forbidden-axiom reports.

`audit/inherited_sources.json` records 30 mathematical sources copied byte for
byte from PRSC_IX_Complete_Weighted_Lifting.zip, archive SHA-256
`dd99a705b933eff4fb8305afa6ebe4bcf8bc70812f0178ab76050c57d3e7efce`.
The source hashes were checked against the actual archive contents while the
record was created. All 30 sources are compiled afresh with the new motion
modules. Six inherited mathematical negative controls remain active. New
motion controls test the sharp first-order error precision. A negative control
passes only on its expected mathematical type mismatch; it cannot pass because
of a missing module, missing constant, panic, or timeout.

Every attempted fresh gate receives raw logs, a verification report, source
and output hashes, and a computation manifest. A failure remains a failure
until classified and repaired; failed logs are retained. A compilation failure
alone does not refute the mathematical theorem. `audit/reconcile_review.py`
links a completed gate with the independently frozen raw-proof review, verifies
source and build hashes, and re-parses all axiom reports independently.

A successful run checks the exact frozen statements. It does not establish
higher-order expansions, analyticity, arbitrary rank-deficient lifting,
native presentation invariance, or completed descent.
