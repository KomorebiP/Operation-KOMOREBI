# Strong Artin Lean v0.29 — Continuous Local Gauge Obstruction

Author: Komorebi P.

Exact base: `Strong_Artin_Lean_v0.28.0_Continuous_Local_Gluing_Checked.zip`

Base SHA-256: `35043bbef695875f2f1316a2313dadab77d7b23ab5a28660c3bd735ae673d5f0`

## Result
The open general local-conjugacy obstruction from v0.28 is constructed in the
continuous inhomogeneous cochain model. Its vanishing is necessary and sufficient
for a lift of the ORIGINAL representation matching all specified local lifts up
to independent conjugators reducing to one. There is no finite-image or
order-invertibility hypothesis in this criterion.

For discrete rings A and B, a surjective ring map q:A->B with square-zero kernel K,
a topological group G, a continuous rho:G->B^units, and any indexed family of
continuous group maps alpha_i:L_i->G with continuous local lifts t_i:L_i->A^units,
the theorem constructs a class and proves:

```
class = 0
iff there exist a continuous representation lift r_tilde and units u_i,
    q(r_tilde)=rho, q(u_i)=1,
    t_i(h)=u_i r_tilde(alpha_i(h)) u_i^(-1) for every i,h.
```

No local map is required to be injective, open, or clopen. The family need not be
finite. The u_i are CONSTANT for each local group, not arbitrary functions of h.
The theorem preserves the given source topology.

Main theorem:

```
Komorebi.StrongArtin.SquareZeroH2.
  continuous_local_conjugacy_lifts_iff_constructed_class_zero
```

## Cochain convention and construction
For the actual square-zero kernel with its induced action:

```
d0(x)(g) = g.x - x
d1(b)(g,h) = g.b(h) - b(gh) + b(g).
```

The v0.28 compatible pairs are `(c,(a_i))`, with c a continuous two-cocycle and
`d a_i = alpha_i^* c`. The new boundary adds the previously omitted local
zero-cochains:

```
(b,(x_i)) |-> (d b, (alpha_i^* b + d x_i)).
```

The new degree-two group is the quotient of those compatible pairs by this
boundary image. Literal matching used only b. Local conjugacy requires x_i too.
The identity is checked on actual units:

```
(1+x) ((1-b)r) (1+x)^(-1) = (1-(b+d0(x)))r.
```

Every unit reducing to one is of the form 1+x with x in K. This establishes both
directions of the representation-level lifting criterion, not just a cochain
analogy.

## Secondary H1 obstruction and exactness
Define continuous H1 as continuous one-cocycles modulo continuous one-coboundaries.
The local-family H1 is the family of local one-cocycles modulo independent local
zero-cochain boundaries. The global restriction descends to these actual quotient
modules.

After a continuous absolute primitive b0 with db0=c is supplied, the local
mismatch `m_i=a_i-alpha_i^*b0` is a family of one-cocycles. Its class in

```
coker(H1_cts(G,K) -> H1_loc)
```

vanishes iff the local-conjugacy lifting problem is solvable. The class is proved
independent of b0.

Moreover the following injection and exactness are checked:

```
0 -> coker(H1_cts(G,K) -> H1_loc)
  -> H2_local_gauge -> H2_cts(G,K).
```

There is deliberately NO zero at the right end: surjectivity onto absolute H2 is
not asserted. The image of the first map equals the kernel of the second.

The map from the strict v0.28 degree-two quotient to the gauge quotient is
surjective. Strict vanishing implies gauge vanishing, but the converse is false.
Replacing any prescribed local lift by a kernel-conjugate lift preserves the
actual class in the fixed gauge obstruction group.

## Examples
1. The v0.28 Z/4 character prescriptions on the three C2 subgroups of C2 x C2
   have zero absolute obstruction but NONZERO new gauge obstruction. Their
   secondary H1 localization-cokernel class is also proved nonzero. Pairwise
   extendability does not suffice.
2. The v0.28 GL2(Z/9) matrix prescriptions have NONZERO strict obstruction but
   ZERO gauge obstruction. The general criterion proves class vanishing from
   the explicitly constructed global representation and local conjugators.
3. `checks/exact_gauge_examples.py` independently checks the small F2 localization
   matrix and modular matrix calculations. These finite checks do not replace
   the universal Lean proofs.

## Limits
This is a continuous representation-deformation result, not a Strong Artin proof.
It does not assert universal obstruction vanishing, supply an arithmetic Selmer
complex, prove local Tate duality, produce auxiliary-prime descent, or construct
an automorphic carrier. General p-adic nondiscrete coefficient modules and a full
compatible coefficient-tower theorem are not included. Provisional-section
changes have intrinsic zero criteria, but a full quotient-level transport between
all distinct Datum objects is not added here.

No historical novelty is asserted for the classical cochain/mapping-fibre
mechanism. The contribution here is its explicit Lean construction and integration
with the original representation, continuity, kernel conjugators, and controls.

## Replay

```
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 6
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 6
# Repeat --resume until RESULT.json records PASS.
python3 checks/exact_gauge_examples.py
```

Pinned Lean: 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Pinned Mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

The verifier checks ancestor bytes, source declaration counts and prohibited
escapes. It compiles every direct dependency and all new source with warnings as
errors, then audits every explicitly named new constant. It trusts the pinned
Mathlib compiled cache; it is not an independent Lean kernel, full Mathlib rebuild,
or replay of every historical branch. See RESULT.json for the observed scope.

## Release evidence
The clean source replay returned PASS for 28 source modules and the axiom audit
of all 70 named constants. New source totals: 43 theorems, 23 definitions,
4 abbreviations, 8 modules and 881 lines. Any additional extracted-archive
replay record is supplied separately, so packaging does not rewrite its own
verification target.
