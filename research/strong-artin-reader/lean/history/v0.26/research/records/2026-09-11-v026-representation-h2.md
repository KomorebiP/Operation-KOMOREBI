# Route record: actual representation obstruction after the audit

## Target contract

Construct the obstruction of an actual representation across a surjective square-zero coefficient homomorphism, using the actual coefficient kernel and actual group cohomology. Prove that the original representation lifts exactly when the class vanishes. Do not replace the target by an augmented equation system or assume a Selmer/cotangent comparison.

Success criterion: fresh kernel-checked construction, choice independence, iff lifting criterion, and a negative control where the constructed class is nonzero.

Relative extension: preserve a specified subgroup lift exactly and distinguish the resulting obstruction from absolute H².

## Outcome

Proved as written for abstract groups and ring maps, including finite invertible-matrix representations. The relative result uses an explicit degree-two cochain quotient. No topology or arithmetic vanishing has been proved.

## Mechanism

Units lift through a surjective square-zero ring map. Conjugation by any provisional lift acts identically on the square-zero kernel. The normalized multiplication error is a two-cocycle by associativity. Different sections differ by a kernel-valued one-cochain and their errors differ by its coboundary. A primitive yields the corrected representation `(1-b(g))*r(g)`.

For strict fixed restriction, require the primitive to vanish on the subgroup. The relative defect is the class of the same cocycle modulo differentials of those restricted primitives.

## Decisive controls

- C3, coefficient map Z/27 -> Z/9, generator image 4: no lift and actual H² class nonzero.
- C4, coefficient map Z/4 -> Z/2, trivial residual representation: an absolute lift exists, but specifying the order-two subgroup generator as 3 makes relative lifting impossible.

## Evidence

The source files, all-constant axiom audit, direct replay logs, and `RESULT.json` are authoritative. The preserved development attempts include failures and must not be interpreted as passing proof evidence.

## Remaining implication

Construct the continuous locally constrained version for a concrete arithmetic setting and prove vanishing of its particular obstruction. The carrier/automorphy problem remains separate. No percentage of Strong Artin completion is assigned.
