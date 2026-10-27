# Euler simplicity continuation — regular addresses and critical phases

Checkpoint: `Euler-regular-address-critical-phases-20261005`.
Parent: `Euler-address-one-20261005-recenter917`, whose original ZIP has SHA256
`da527bc4950f2b8a77cc625f068d1b4bdd2b828719df6ab1f84bb02a4a48dec4`.

**Universal Euler simplicity remains open.** The new work proves complete
simplicity for additional infinite integer families, classifies the entire
terminal-129 and terminal-161 multiplier frontiers by necessary congruences,
and extends the structural argument beyond regular lower addresses. No new
Lean build or exact singular Euler index is claimed.

## Target and conventions

For every ordinary integer `r>=1` and every `x in Z_2`, prove
`G_r(x)=0` implies `G_r'(x)!=0`. The exact signed-Euler/Bernoulli packet
definition, with `sech(t)` and `B_1=-1/2`, is retained in
`sources/euler_v4.md`. Valuations have `v_2(2)=1` and `v_2(0)=infinity`.
A multiple zero of a freely perturbed analytic family is not a counterexample
to this target. A necessary finite congruence is not an exact singular index.

## New unconditional integer families

All dyadic roots are simple for every integer in either family:

| Euler index | Multiplier range | Every outer scale |
| --- | --- | --- |
| `r=B*2^L-129` | odd `0<B<2^89` | `L>=392` |
| `r=B*2^L-161` | odd `0<B<2^932` | `L>=487` |

The true-terminal property is proved throughout these ranges, including their
boundary scales. These are coefficientwise family theorems, not lists of
tested multiplier values.

For arbitrary larger multipliers with the stated actual terminal, a multiple
root has the following necessary conditions:

| True terminal | Only possible outer scale | Surviving multiplier classes |
| --- | --- | --- |
| 129 | `L=515` | two classes modulo `2^90` |
| 161 | `L=640` | one class modulo `2^935` |

The exact residues and argument classes are recorded in
`next/terminal129/phase_129.json` and
`next/critical_phases/combined_frontier.json`. They are canonical necessary
residues. No existence assertion is made inside them. Terminal 161 at `L=639`
has exactly one simple root; at `L=641` it has exactly three, uniformly for
every admissible odd multiplier.

Proofs: `next/terminal129/PROOF.md` and `next/critical_phases/PROOF.md`.
The 935-bit modulus composes a new whole-phase reduction with the inherited
917-bit local parameter certificate; it is not a new 935-bit reconstruction
or an all-precision affine interpolation.

## Structural extension

For a certified wall let `a` be its last lower minimizing address, let
`k=j-a` be the regular complement, set `t=v_2(k)`, and write
`Theta(n)=3n+1+s_2(n-1)`. If `a` is regular, every emerged-complement root is
simple. All roots are simple at every wall distance when

`Theta(a) <= t < Theta(a)+v_2(a!)`.

Equality walls are simple even outside this band. This includes the higher
address `a=2`, complement `k=256`: every certified terminal-258 wall at
`L>=777` is simple. For `a=3`, `k=4096`, the only possible critical scale is
`L=16385`; the earlier example at `L=12302` is therefore closed.

The proof retains the actual Euler prefix and the genuine terminal shift.
It does not reinstate the false claim that rewriting the same integer at a
smaller wall label reduces its true terminal. See
`next/higher_address/regular_address_transversality.md` and the inherited
`carry_audit/CARRY_ADDRESS_AUDIT.md`.

For the first irregular lower address `a=17`, with `v_2(k)=53`, the actual
prefix has one simple root `sigma=43 mod 64`. Preparing that root into a
linear factor again excludes every emerged-complement tangency. For the first
complement `k=2^53`, only `L=4*2^53+16` can remain critical, and any multiple
root must satisfy `v_2(x-sigma)=16`. This is an analytic reduction for an
irregular prefix, not merely a decreasing combinatorial label. Its proof and
six-bit actual-coefficient certificate are in `next/irregular_address/`.

## Exact remaining arithmetic obstruction

On each certified terminal-161 deep quadratic chart, the independent
undepletion parameter `epsilon=2^24*eta` has a critical-value map that is a
bijective isometry of `Z_2`. There is exactly one singular member `eta_*`,
with a double root. The actual Euler chart is singular exactly when

`eta_* = 2^(2r-25)`.

Source elimination has unit denominators on the relevant chart, so this is
an exact reduction without extraneous common zeros. It is not an avoidance
proof. The attempted rational-height argument fails to supply the needed
arithmetic bound: the critical point and evaluated analytic units are not
known to be algebraic. See `next/unit_identity/epsilon_critical_manifold.md`
and `next/height_nonintersection/HEIGHT_ROUTE_AUDIT.md`.

## Verification and reproduction

Independent reviews are in `next/review/`. Exact coefficients, independent
verifiers, bounded-run contracts and manifests accompany the corresponding
proofs. Their scopes are distinguished from the universal mathematical
arguments. Python 3.10 or newer and the standard library suffice.

From this extracted package root, the stored-output audit is:

```text
python3 next/review/check_stored_outputs.py fresh_stored_checks.json
python3 next/review/check_followup_outputs.py fresh_followup_checks.json
```

For independent Bernoulli/source reconstruction of the new phase records:

```text
python3 next/critical_phases/verify_phase_certificates.py
python3 next/terminal129/verify_phase129.py
```

These verifiers refresh their verification outputs; preserve the delivered
package as the immutable checkpoint before rerunning. The constructors are
in the same directories. The earlier recenter constructor and verifier remain
under `local_parameter/`; its original complete package is preserved as
`history/Euler_Address_One_Continuation_2026-10-05.zip`.

`ROUTE_INDEX.md` links the executed routes and their exact remaining
implications. `RESEARCH_STATE.json` records the current contract and dependency
status. `SHA256_MANIFEST.json` records this package's integrity, not mathematical
truth. `MANIFEST_ROOTS.json` gives the execution root for each new run manifest;
the bundled validator is `audit_tools/validate_manifest.py`. Both portable
stored-output checks passed from this assembled package, and all 71 pinned
inputs/outputs of its seven new run manifests were present with matching hashes.
