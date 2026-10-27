# Euler: exact radix transport and the remaining arithmetic gap

Checkpoint: `Euler-radix-audit-20261005`.
Parent: `Euler-shifted-obstruction-20261005`.
Parent archive SHA256: `7125e5ed1ce7b0a3fb25473284ac92fa1a4c6db42862980f1b07cbfb50233dea`.

**The universal Euler simplicity theorem remains open.** This continuation
executes the requested radix and available-machinery attack. It proves exact
new transport results and identifies specific failed implications. It neither
constructs an actual repeated Euler zero nor proves that none exists.

The two equations have been treated together throughout. The unresolved issue
is the value of the actual residual at its stationary point, not a failure to
locate or differentiate that point.

## Exact target and what closure requires

The universal claim is

\[
G_r(x)=0\quad\Longrightarrow\quad G_r'(x)\ne0
\qquad(r\ge1,\ x\in\mathbb Z_2).
\]

On the focused terminal-161 family, the earlier exact Morse reduction says
that a repeated zero occurs precisely when

\[
\Phi_r(2^{2r-25})=0,\qquad
r=(17659+2^{18}T)2^{640}-161.
\]

Here T is an ordinary nonnegative integer and the index must have true
terminal161. The map Phi_r belongs to the fixed-r independent undepletion
family; no all-precision analytic family in T is assumed. Proving the displayed
value nonzero for every admitted T is still required. Other address families
also remain before universal simplicity follows.

## New results and their precise limits

| Route | New exact result | Implication still missing |
|---|---|---|
| Dyadic block descent | The historical scales16, 2^68, and their successors lift to exact analytic block-unit transformations. All source units and derivatives are retained. | A nonaligned cutoff leaves a forcing term P. A double zero gives P+T_new=0 and BP'+T_new'=0, not a double zero of T_new. |
| Full spatial Cartier compiler | The regularized Euler measure has six recurrent states and a two-function Mellin recursion for value and slope at scales4 and4/3. | The actual cutoff must be included before this controls the residual. |
| Meromorphic cutoff compiler | The prescribed finite prefix has a finite O(r)-dimensional compiler, including an explicit polar correction B_8 and its derivative. | Positive-log modes have neutral transfer: their section denominators exactly cancel contraction of the Mellin argument. |
| Odd and mixed radices | Exact odd-radix transport and the complete nonlinear triplication cutoff are derived. The actual deflected tail has uniform value/derivative valuations157/158 on the focused chart. | Neither identity forces this deflected tail to vanish at a double zero of the original residual; shifted terms and cutoff forcing remain. |
| Finite-rank and cross-radix bridges | The full G_r value sequence has infinite rational/Q_2 section rank in every radix. The actual beta and gamma sequences do too. | The recovered finite-hull and regularity theorems cannot be instantiated directly on these sequences. |
| Rational-mask and lattice bridges | Actual Bernoulli tails have no rational canonical dyadic mask. The actual meromorphic prefix has no finite spanning stable integral lattice for r>=3. The full spatial measure has Smith invariants(2,2,2,12). | The valid full-measure lattice information does not exclude contact with the prescribed finite prefix. |

The strict-contraction failure is explicit. For k>0,

\[
H_k(s,z)=(2s)_{\underline{k}}z^k,
\qquad 2^{-k}H_k(s,2z)=H_k(s,z),
\]

and the same equality holds after differentiation in s. An actual occupied
prefix state is

\[
C_{16,9}F_3=\frac{32}{3t^2}-\frac12+\frac9{640}t^2.
\]

Thus a generic strict contraction on the enlarged state space cannot be the
missing proof. This does not rule out a more selective arithmetic invariant.

## Why valuations alone cannot supply the missing arithmetic

For the actual base index r=17659*2^640-161, changing only beta_r to

\[
\widetilde\beta_r=(1+2^{24}u_*)\beta_r
\]

for a specifically defined odd dyadic u_* creates an exact double zero while
preserving every coefficient valuation, every radix weight, the entire lower
prefix, and all other kernel coefficients. The changed normalization is a
nonzero unit and does not affect multiplicity. Existence follows from a
contraction/Hensel proof; the93-bit calculation is supporting evidence.

This is an artificial coefficient deformation, not a Bernoulli coefficient
and not an Euler counterexample. It does not preserve the prescribed full
Bernoulli generating identity. A separate two-free-packet prefix deformation
shows the limitation of the spatial compiler and its polar correction while
keeping the full Euler measure fixed. These two constructions preserve
different data and must not be combined into a claim that every available
arithmetic identity admits a double zero.

## Remaining proof obligation

At the actual stationary point one must exclude the simultaneous equations

\[
C_r(s)=b(s),\qquad C_r'(s)=b'(s),
\]

using the prescribed Bernoulli coefficients in C_r, where
b=(1+3*9^s)Ecal and C_r=(1+3*9^s)S_r. An equivalent focused task is the
nonvanishing of Phi_r at the actual undepletion parameter above.

A successful continuation must produce a Bernoulli-specific nonzero
certificate or an invariant excluding this contact with the complete cutoff
retained. The present work does not prove that such an argument is impossible.
More parameter digits, omission of the forcing term, or an unproved
finite-state hypothesis would not discharge this obligation.

## Navigation, verification, and source scope

- `radix_descent/RADIX_JET_TRANSPORT.md`: exact descent and one-coefficient boundary.
- `cartier_mask/EXACT_SPATIAL_COMPILER.md`: spatial states, source correction, joint Mellin recursion, neutral modes.
- `cross_radix/CROSS_RADIX_AND_TRIPLICATION.md`: odd-radix identities, actual strict defect, infinite kernel rank.
- `bridge_inventory/ACTUAL_COEFFICIENT_BRIDGE_AUDIT.md`: actual theorem hypotheses, mask/rank/lattice gates, Smith calculation.
- `review/`: independent mathematical reconstructions and exact computation replays.
- `CURRENT_EVIDENCE.json`: authoritative current manifests; older changed-source runs are development history.
- `ROUTE_INDEX.md`: new routes and inherited routes, with precise status.

The source audit recovered Padic Blocks05/12, Cartier Bridges01/02,
Universal Lane v1.16, Cross-Radix Rigidity v0.12, and the projector/polyphase
sources. Source files and archive hashes are recorded under `sources/` and
in the route source maps. The claims CSV was used only as a locator.
This is a targeted audit of these relevant sources, not a claim to have
exhaustively searched every project document. No Lean compilation was run.

The parent checkpoint is included unchanged. Current exact computations
support the stated identities and named examples; universal claims depend on
the accompanying proofs and their independent reviews. A zero residue at
finite precision is never classified as an exact actual zero.
