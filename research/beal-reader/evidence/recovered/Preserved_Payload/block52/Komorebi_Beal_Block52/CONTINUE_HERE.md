# Continue with Block 53

Open `Komorebi_Beal_Block52_Frobenius_Kummer_v5.2.0.zip` as the authoritative
checkpoint. It contains the original complete Block51 ZIP byte for byte.
Block51 in turn retains the full recovered Blocks49--50 and their originals.
Do not discard nested predecessors or overwrite their historical status.

Read completely before editing:

- README.md
- work52/TARGET_CONTRACT.md
- work52/REPORT.md
- work52/PROOF_BOUNDARY.md
- work52/THEOREM_INDEX.md
- work52/notes/FROBENIUS_DEPTH.md
- work52/notes/COMPATIBLE_KUMMER_COORDINATES.md
- work52/DEVELOPMENT_FAILURES.md
- work52/source_records/SOURCE_CHECK.md
- work52/VERIFICATION.md

Run `python verify.py --replay-predecessors` first. This runs in temporary
copies and writes its report outside the package. Timeouts are inconclusive.
The exact predecessor SHA is pinned by this package and by its target contract.
Extract the original predecessor to a separate clean directory before
reading its full Kummer/cup/monodromy arguments. Do not modify it in place.

## Preserve the new distinctions

1. On the inherited reducible branch71|C. Actual n>=2 forces29*43|C.
   Divisibility by those primes is not sufficient for any depth or solution.
2. Good13 gives actual rho(F13)=-13I, hence a_phi=0, and the local value
   eta_n(F13)=-1/13 mod7^n. Neither conclusion supplies the global eta_n.
3. Use the SAME global(a_phi,a_3,a_5), with a_3*a_5!=0. Local functionals:
   at29, (4,1,5) and(3,1,5); at43,(0,1,2); at71,(2,1,0) and(5,1,0).
   They are anchored to the image of the global generator3, not freely
   normalized relative coefficients at different places.
4. With good13 and n1, beta is unramified at71, and beta-ramification at29
   forces r=a_3/a_5=2 while at43 it forces r=5. It cannot use both.
   It must use an eligible divisor other than71, but such divisors exist
   abstractly. Do not discard them as unlikely.
5. Good13 excludes inert-minus ramified upper endpoints and the old
   nonliftable q1504231 ray family. Bad13 is still open. The old family is
   not a realized Frey example even there; its earlier multiplicity cost
   remains necessary.
6. The ordinary n in{1,3} conclusion still requires all eligible t=h=1.
   Do not assume it for arbitrary C. No CM or higher-level branch is closed.

## Primary next bounded target

Use the computed common-coordinate functionals to constrain the actual
remaining ratio and endpoint character, rather than repeat a free abstract
Selmer dimension calculation.

A promising first audit is arithmetic conjugation/descent of the PARTICULAR
Frey Jacobian: determine whether its semilinear action under Gal(K/Q), after
the exact nu twist and in compatible lattices, constrains a_3/a_5 to F7 or
constrains the unit coordinate. J being defined over Q alone is not a proof
of the required twisted semilinear identity. Establish the comparison map
and its effect on[phi],[3],[sqrt5] before using any field-of-coefficients
restriction. Do not assume r is in F7 rather than F49.

In parallel, compute an actual global ray-class restriction for beta using
the depth-one exclusions at71 and the incompatible29/43 zero loci. Keep
all eligible divisors of C and their possible conductors visible. Restricting
the support to a convenient finite set requires a proved hypothesis.

For the ordinary depth-three branch, combine the actual local diagonal
value at13 and the common Kummer functionals with the nonzero endpoint
obstruction. Do not replace it by the false assertion that all characters
lift. A newly surviving ray family is only a character family until it is
shown to belong to the actual representation.

For bad13, use the local integral toric geometry to determine what a_phi
can be. If beta actually ramifies at13, the old endpoint criterion and the
nontrivial phi symbol distinguish the zero and nonzero a_phi cases. Mere
bad reduction does not determine beta-ramification or the global ratio.

## Verification discipline

Do not revive the invalid orbit-representative equation filter. Curve
isomorphism scales A^3+B^5 by u^15, not automatically by a seventh power.
Test equation admissibility per member, and use an independent direct count
or other exact certificate for every new finite exclusion.

A new Lean proof may be useful, but no existing Block52 Lean compilation is
claimed. Written proof, finite computation, independent implementation,
self-review, and independent mathematical review are distinct statuses.
