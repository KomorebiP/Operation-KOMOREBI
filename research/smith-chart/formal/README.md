# First-order RL realization: formal companion

This is a separate, source-bound Lean check of one step in the archived
exact-versus-approximate construction. It supplies and verifies explicit
component values for the degree-one limiting impedance. The
[worked reading](../../../docs/demonstrations/SMITH_FIRST_ORDER_RL.md)
shows the circuit and derivation.

## Claim and scope

For real \(a,b\) with \(0<b<1-|a|\), let
\(G_*(t)=a+bt\), \(t(s)=(s-1)/(s+1)\), and
\(z_*=(1+G_*)/(1-G_*)\). The series resistor \(R_s\), parallel resistor
\(R_p\), and inductor \(L\) given below are all positive:

\[
R_s=\frac{1+a-b}{1-a+b},\quad
R_p=\frac{4b}{(1-a-b)(1-a+b)},\quad
L=\frac{4b}{(1-a+b)^2}.
\]

The [Lean source](SmithFirstOrderRL.lean) proves the rational identity

\[
z_*(s)=R_s+\frac{R_p\,sL}{R_p+sL}
\]

over an arbitrary field whenever the indicated denominators are nonzero.
It separately proves component positivity over the reals, the identity for
complex \(s\) with \(\operatorname{Re}s\ge0\), and that the archive's parameters
\(b=(1-a^2)\rho\), \(|a|<1\), \(0<\rho<1/2\) satisfy the hypotheses.
It also checks \((R_s,R_p,L)=(5/4,9/4,9/8)\) for
\((a,\rho)=(1/3,1/4)\).

The formal circuit expression uses the standard ideal one-port formula for a
resistor in parallel with an inductor; it is not a hardware or SPICE model.
The formalization does not prove the archive's arbitrary-order theorem,
H-infinity error formula, reactive-element lower bound, or the unresolved
transformer-free six-reactive-element case. It makes no novelty claim.

## Evidence and self-review

The archived theorem note is bound by the replay to repository revision
`b1546c80c88640f7dad5fe4300c1739523fa1b4b`, archive SHA-256
`39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e`,
and theorem-note SHA-256
`71e49cabfe13fdb63b61e2b6f2afe450232ec6a5b3c127cff5b47a026f8951a2`.
The [run03 receipt](verification/run03/receipt.json) records the proof and
direct imported-object hashes, pinned dependency revisions, and four steps:
successful compilation, a nine-declaration axiom audit, rejection of the
deliberately false normalized inductance \(9/2\), and rejection of a false
positivity claim outside the parameter range. The accepted axioms are
`propext`, `Classical.choice`, and `Quot.sound`. The replay uses precompiled
Mathlib dependencies and does not rebuild or hash all transitive objects.

The source-to-formal mapping and proof review are self-review, not an
independent referee report. The [exact checker](check_exact.py) and its
[receipt](verification/rational-check.json) also record a symbolic
cross-check and 3,924 exact rational operating points; those finite checks are
diagnostics, not a replacement for the quantified Lean statements.

The original companion's historical run15 records earlier documentation
hashes. Its Lean proof files remain unchanged; updating those documents to
point to the recovered archive does not make run15 a replay of this module.

## Replay

Use the same pinned Windows Lean and Mathlib environment as the original
Smith chart companion. The output directory must not already exist:

```powershell
python research/smith-chart/formal/replay.py --lean <absolute-lean.exe> `
  --mathlib <absolute-mathlib> --git <absolute-git.exe> `
  --repo <absolute-Operation-KOMOREBI-checkout> --output <new-output-directory>
```

The script verifies the compiler, pinned Git revisions, archive and theorem
hashes, hashes direct imported caches before and after the run, compiles with
warnings as errors, audits the declared axioms, and checks the negative
controls. The repository must contain the bound source revision.

With SymPy installed, the finite diagnostic can be rerun separately with
`python research/smith-chart/formal/check_exact.py`; pass `--output` with a
new path to save its receipt.
