# Independent reviews: primitive scaling, stable reduction, and modular traces

Reviewed 2026-09-19 by the arithmetic-stratification subagent. The reviewer
did not author or modify the four target proof files. This record gives
separate verdicts for separate statements. The reviewer did author
`stratification.md`, which is therefore not independently audited here.

## Frozen target revisions

| File | SHA256 |
|---|---|
| `notes/primitive_scaling.md` | `2394ee439a35820cd7e6f82a6d96e019a48371965c6485ea515dcf484668f11a` |
| `notes/evenC_semistability_at2.md` | `73b5859b9eccfecdb250960b6f643501ae0a3620bb17c1985ff72331b20fd7a8` |
| `notes/mod7_irreducibility_extension.md` | `633a1c392396eadd02d3872f31666acae7a2eef223aed37acb3f7c61b879e9ab` |
| `notes/modular_correlations.md` | `3df338a01668b4500ed08b156d87b063d3dd63ae043409e262326f00cd2d9e03` |
| Dependency `notes/cartier_independent_audit.md` | `502fba199936fc28625b05cfe4ba83836fad50acad26c771414448ab010e0955` |

Subsequent substantive changes require an impact check; these hashes
identify the text actually reviewed.

## 1. Primitive weighted scaling

**Claim.** For each rational `0<t<1`, the displayed universal signature
triple has a unique positive rational weighted scaling to primitive
positive integer bases if and only if the three specified valuation
divisibility conditions hold at every prime.

**Verdict: proved as written.**

Dependency chain: universal polynomial identity -> exhaustive valuation
sectors from `t+(1-t)=1` -> forced local scaling valuation -> finite support
construction of a positive rational scale -> disjoint valuation supports.
All leaves are elementary internal calculations.

Independently recomputed the four valuation sectors. The forced scaling
valuations are `-m/3`, `-4n/5`, `8r/7`, and `0`. The resulting base
valuation triples are `(m/3,0,0)`, `(0,n/5,0)`, `(0,0,r/7)`, and
`(0,0,0)`. These verify necessity and sufficiency, including arbitrary
valuation sizes. Finitely many nonzero valuations give a rational scale.
Positivity removes the sole possible sign ambiguity in uniqueness.

For reduced `t=m/n`, the final equivalence to `m` a cube, `n-m` a fifth
power, and `n` a seventh power is correct. It explicitly retains the
original Diophantine obstruction. There is no claim that the criterion
finds or excludes every rational parameter.

## 2. Stable reduction at two for odd A,B

**Claim.** The displayed integral genus-two curve has a stable model over
`Z_2` whenever A,B are odd and its generic discriminant is nonzero;
therefore its Jacobian is semistable at two, and one-dimensional residual
constituents at seven are unramified there.

**Verdict: proved as written.**

The finite flat quadratic cover charts and their transition were checked.
Their module `O + O(-3)` has the asserted fiber arithmetic genus two. The
generic discriminant is nonzero. In the special fiber, the two derivatives
force precisely `(r,r)` with `r^2+r+1=0`. The local expansion and the
separable quadratic tangent cone were independently rederived. Both
infinite points have unit derivative. The Artin–Schreier right side has
a simple pole at `x=1`, and therefore is not `h^2+h` for rational `h`.
This proves geometric irreducibility. Two nodes reduce the normalization
genus from two to zero and produce four distinct branches, so the fiber
is stable. No regular-total-space hypothesis is silently imposed on the
stable model.

The curve-to-Jacobian theorem in residue characteristic two was already
checked from Deligne–Mumford Theorem 2.4 in the separate durable audit
`cartier_independent_audit.md`. This review checked the application and
did not fetch that PDF again. Semistable inertia-unipotence makes every
inertia eigenvalue one on the seven-adic representation; reduction and
passing to a one-dimensional constituent preserve that conclusion.

This establishes the inertia input only. It does not reuse the old
good-reduction Frobenius-at-two contradiction in the even-C case.

## 3. Combined irreducibility when seven divides AB

**Claim.** Under the hypotheses and source dictionary stated in the target
file, the residual rank-two RM representation is absolutely irreducible
if `7|AB`. Combined with the predecessor, it is absolutely irreducible
when C is odd or `7|AB`.

**Verdict: proved as written.**

The conclusion is a written arithmetic theorem relative to its declared,
project-verified external inputs. It is not a Lean proof. The review did
not independently fetch the original arithmetic papers again.

Dependency chain:

1. `7|AB` and primitivity imply good reduction at seven.
2. The exact Cartier identity gives nilpotent Cartier and geometric
   seven-rank zero, also after the unramified quadratic base extension.
3. Hypothetical absolute reducibility gives two global associated
   characters. Restriction of scalars and lattice independence transfer
   their Jordan–Hölder constituents to the full Jacobian torsion.
4. The rank-two determinant's eighth power is the full determinant
   `chi^2`; no unsupported equality of the rank-two determinant with
   `chi` is used.
5. At 3 and 5, trivial wild determinant and total conductor at most three
   force both constituents tame. Their inertia orders divide 8 and 4.
   Semistability elsewhere, including the new two-adic model, makes
   their eighth powers unramified outside seven.
6. The order-sixteen global unit and principal-idele reciprocity reduce
   both seven-adic inertia exponents from `{0,1,7,8}` to `{0,8}`. The
   determinant equation `8(e+f)=16 mod48` forces exactly one exponent
   zero. Reversing the reciprocity convention changes all signs and
   preserves this conclusion.
7. The local Raynaud consequence forbids that nonzero unramified
   subquotient in good reduction of seven-rank zero.

Each internal implication was checked. The external conductor and local
weight statements are inherited with their already-audited exact scope
from Block46. The new Raynaud input has a primary-source verification in
`cartier_independent_audit.md`: absolute ramification index `1<7-1`,
finite flat closures and quotient, uniqueness of the constant generic
fiber's model, and the contradiction between its étale special fiber and
a quotient of a connected seven-torsion subgroup.

The coefficient-field distinction is handled correctly. A constituent
over an algebraic closure descends to a finite coefficient extension;
restriction of scalars of that extension is a direct sum of copies of
the original torsion and is realized by a power of the abelian variety.
It remains of seven-rank zero. A Jordan–Hölder factor is a quotient of a
submodule, and the local proof explicitly treats both subgroup closures.

No class-number argument or Frobenius-at-two contradiction is required
for this extension. The remaining branch C even with `7` not dividing AB
is correctly left open, including ordinary good reduction and `7|C`.

## 4. Trace-zero restrictions at eleven and nineteen

**Claims.** Assuming the stated modular comparison to trivial
nebentypus and the stated multiplicative-prime trace comparison, rank-two
trace zero modulo seven at a K-prime above eleven forces `11|A`, and at
a K-prime above nineteen forces `19|B`.

**Verdict: conditional on the named modular and multiplicative-prime
comparison inputs.** The finite good-reduction assertions and the
restriction-of-scalars implication have passed independent checks.

Both rational primes split in `Q(sqrt5)`, so the residue norm at either
base prime is q. The residual RM coefficient field is F49. If the
rank-two trace is zero and determinant q, restriction of scalars gives
the full four-dimensional polynomial `(T^2+q)^2 mod7`. This remains
valid via residual semisimplification when the actual Jacobian lattice
does not carry a chosen integral maximal RM order. A zero scalar
four-dimensional trace alone is insufficient, and the proof correctly
checks the entire polynomial.

An independently written script,
`computations/modular_independent_pointcounts.py`, recounted **all 452
smooth pairs**: 110 at eleven and 342 at nineteen. Unlike the original
script, it computes extension-field quadratic characters using the norm
to the prime field, and it does not use orbit reduction to count at
nineteen. Every degree-four polynomial agrees with the original output.
The full-polynomial matches are exactly the ten `A=0` pairs at eleven
and the eighteen `B=0` pairs at nineteen.

The original nineteen-orbit argument is independently valid:
`(A,B)->(u^5 A,u^3 B)` comes from the coordinate scaling of the displayed
monic sextic, and the stored orbits cover every smooth pair.

For `q|C`, the note explicitly assumes the modular-method bad-prime
comparison. Its required traces are `+/-(q+1)`: `+/-12` and `+/-20`,
neither zero modulo seven. As an additional algebra check, the repeated
roots of the nodal model are rational at both q, and the branch
characters of `6-3r` agree at its two roots. Thus the elementary nodal
data do not reveal a conflicting toric-sign issue. This check alone is
not presented as a proof of level lowering or modular attachment.

The CM consequence at eleven is correct conditional on the comparison:
eleven splits in K and is inert in the quadratic CM extension defined
by `sqrt(-3)`, so the CM representation has trace zero there. The
conclusion `11|A` is a restriction, not elimination. No corresponding
nineteen CM label is invented.

The imported source-data parser, complete GitHub-code audit, and the
parameter-inversion observation were outside this review's independent
scope. No global Hilbert form has been eliminated by the checked claims.

## Independent computation provenance

The recorded run is `verification/modular_independent_run/manifest.json`;
its input contract is
`computations/modular_independent_pointcounts_contract.json`.
All arithmetic is exact, no random sampling is used, and the complete
declared ranges were checked. The run and manifest validation completed
successfully. No execution failure occurred.

Result SHA256:
`3aa9d178838077570071c70accd7d358b497bc6daa59827145ddb5dbfe2131b8`.

The earlier exploratory output
`verification/modular_independent_pointcounts.json` agrees with the
recorded result but is not the authoritative manifest-backed copy.

## Remaining scope

These reviews find no gap in the three written proofs under their stated
and project-verified arithmetic inputs. The modular restrictions retain
their explicit external comparison conditions. None is a proof of the
nonexistence of primitive positive signature-(3,5,7) solutions, or of
Beal's conjecture. In particular, source verification, coefficient
identities, local geometry, residual irreducibility, level lowering, and
form elimination remain distinct proof obligations.
