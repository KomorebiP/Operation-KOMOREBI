# Block 48 formal verification

Checked 2026-09-19. **Eight public theorems and one private helper pass
Lean**, with warnings treated as errors. The complete printed axiom closure
of each public theorem contains only `propext`, `Classical.choice`, and
`Quot.sound` (or a subset). There is no `sorryAx`, added axiom, or native
decision shortcut in this certificate.

The source is `../lean/BealBlock48LocalAlgebra.lean`. This is a certificate
for the exact local algebra used in the written arguments. It does not
formalize their arithmetic or source-dependent inputs.

## What is proved

Write \(Q_a(t)=t^2-at+4\). The first seven statements quantify over
**every field of characteristic seven**, so their common-root exclusions
apply over an algebraic closure, not just at elements of \(\mathbf F_7\).

| Public declaration | Checked statement |
|---|---|
| `common_root_forces_trace_eq` | A common root of \(Q_a\) and \(Q_b\) forces \(a=b\). |
| `oddC_three_traces_excluded` | For \(a\in\{4,-4,1\}\) and \(b\in\{0,-1\}\), a root of \(Q_a\) is not a root of \(Q_b\). |
| `oddC_zero_trace_forces_zero_branch` | A common root of \(Q_0\) and \(Q_b\) forces \(b=0\). |
| `evenC_candidate_nonzero_at_neg_one` | For \(a\in\{4,-4,1,0\}\), \(Q_a(-1)\ne0\). |
| `evenC_candidate_nonzero_at_neg_four` | For the same four traces, \(Q_a(-4)\ne0\). |
| `evenC_full_polynomial_excluded` | A root of one of those four \(Q_a\) is not a root of \((t+1)^2(t+4)^2\). |
| `oddC_full_polynomial_excluded` | The odd-C exclusion also holds for the full polynomial \(Q_b(t)^2\). |
| `determinant_weight_uniqueness` | For natural numbers \(d_0,d_1\le2\), \((d_0+7d_1)\bmod48=8\) forces \(d_0=d_1=1\). |

The private helper applies `CharP.cast_eq_zero_iff` to prove that a natural
number not divisible by seven has nonzero image in the field. It is included
in the public theorems' audited dependency closures and is not counted as a
separate research result.

The first statement uses the difference of the two equations and the fact
that a root cannot be zero because the constant term is four. The actual
trace substitutions and the finite determinant calculation then follow by
exact arithmetic. These are universal Lean propositions with their written
hypotheses; no numerical search bound is promoted to a theorem.

## Interpretation boundary

The written note `bad7_candidate_q2_audit.md` imports the curve's
four-dimensional Frobenius polynomials, the rational Hecke values attached to
the five exact LMFDB labels, and eigenvalue containment under the assumed
direct modular identification. Its labels c,d,e have traces 4,-4,1, while
h,l have trace zero. Given those inputs, the algebra excludes c,d,e for
both parities of C and h,l for even C; in the odd-C case h,l require the
trace-zero branch. None of those source identities is encoded as an axiom
in the Lean source.

Likewise, `level_lowering.md` derives the determinant exponent congruence
from the finite-flat representation and its coefficient action. Lean checks
only the resulting uniqueness of the filtration dimensions. It does not
prove Fontaine–Laffaille theory, construct a crystalline lift, or verify
that the determinant/inertia dictionary applies to this Jacobian.

This certificate does not establish residual irreducibility, modular
attachment, completeness of a candidate space, nonexistence for the full
(3,5,7) signature, or Beal's conjecture.

## Replay and provenance

The runtime is Lean **4.34.0-rc2**, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, with mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. It is the retained portable
Linux x86_64 runtime. No installation or network access is needed.

From the project root, run:

```bash
python3 work48/lean/check_formal.py
```

The driver resolves the proof and runtime relative to its own location, so
it also works when invoked through an absolute path from another working
directory. If the runtime was stored elsewhere, pass
`--runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2`. The underlying command
uses the existing `run.sh lake -d ... env lean` interface, `-j 1`, and
`-DwarningAsError=true`. The driver verifies that all eight declarations
have an axiom report and that every reported axiom belongs to the standard
three-item allowlist above.

The authoritative completed run is
`../verification/formal_final/manifest.json`; its compiler output and
scientific result are `stdout.txt` and `result.json` in the same directory.
Compilation and the axiom audit completed in approximately 1.82 seconds,
with exit status zero. The runner enforced a 120-second wall-clock cap,
90-second per-process CPU cap, 8 GiB address-space cap, one CPU core,
and a 1 MiB output cap. Lean itself received its explicit single-thread
flag. The manifest pins the proof source, replay driver, runtime launcher,
and Lake dependency manifest. It records the other software versions but
does not hash the entire installed runtime dependency closure.

The computation-audit manifest validator returned
`valid evidence record; mathematical interpretation requires review`
with `--root /workspace/scratch/3e94b90aa142`. Paths in that historical
manifest record the actual execution location; the replay driver does not
hard-code that location.

| Artifact | SHA-256 |
|---|---|
| `lean/BealBlock48LocalAlgebra.lean` | `63126f8c2ff68613315fb3f61e63684e00793290531667b01a86a4ef4461fc85` |
| `lean/check_formal.py` | `3f258fb4934a6c71f19ae384ed889b486efd48998fb12e416ac0e795f1306db3` |
| `lean/formal_contract.json` | `1a453d9d0f08042f0718dbae82a6b5d1c8b0b3a24767d1f643080430131f68ba` |
| `verification/formal_final/manifest.json` | `44d6f15632820d29498dd848c93cd92a01af70a24db1bb984f9cf597917bdaae` |
| `verification/formal_final/result.json` | `5185b3d213b41514c1e3dccb440d9c1dc0e1b27ef1adebc7b388d35fe24f690e` |

Two earlier bounded-run diagnostics are retained, not counted as successful
evidence. `formal_run` attempted a draft importing all of Mathlib and failed
to read an imported `.olean.private` file under the address-space cap; the
same draft had passed the ordinary uncapped check. Its preserved input
snapshot has SHA-256
`78aee00f992a5fbddec698dff2911cb4cec77f15d1d6382866a94237fcad8cdd`.
`formal_verified` used the final narrower imports but encountered an explicit
thread-creation error. The final run retained those imports and supplied
Lean's single-thread flag. These failures concern the bounded execution
environment, not rejected mathematical statements. The first historical
manifest's source path is intentionally superseded by the final source;
its snapshot preserves the old bytes, and it should not be used as a current
input-freshness record.

Conservative mathematical self-proofreading covered this note and the new
Lean comments and declarations. No unresolved notation issue or further
mathematical-token correction remained. No unrelated project files changed.
