# Strong Artin v0.28 — Continuous Local Gluing

**Author:** Komorebi P.  
**Base:** `Strong_Artin_Lean_v0.27.0_Continuous_Obstruction_FiniteQuotient_Checked.zip`  
**Base SHA-256:** `4c295925c15e3047d8fd5ebad97744911e2ae79f07e72ae0b080cb8e5af05d56`

This is an additive, audited continuation of the continuous representation-obstruction branch.
It does not merge or renumber any sibling archive. It does not prove Strong Artin.

## Exact main result

Let q:A -> B be a surjective homomorphism of discrete coefficient rings with square-zero kernel K.
Let rho:G -> B^units be a continuous representation of a topological group.
For any indexed family of continuous group homomorphisms loc_i:G_i -> G, give continuous
representations t_i:G_i -> A^units whose reductions equal rho composed with loc_i.

The release constructs a continuous constrained obstruction and proves:

    a continuous global lift matching every t_i literally exists
      iff the constructed constrained class is zero.

The local maps need not be embeddings, open, clopen, or have open images. No global provisional
section extending all t_i is assumed. Instead, the existing normalized global provisional section
is compared separately with each actual local lift.

## The cochain object

Let r be the continuous provisional section, c its normalized multiplication defect, and

    a_i(h) = -((t_i(h) - r(loc_i h)) r(loc_i h)^(-1)).

The local mismatch obeys d a_i = res_i c. Define the module of pairs

    Z2_constr = { (c,a): c is a continuous two-cocycle,
                            a_i continuous one-cochains, res_i c = d a_i }.

A global continuous one-cochain b has boundary

    b |-> (d b, (res_i b)_i).

The distinguished class is the class of (c,a) in Z2_constr / range(boundary).
Vanishing means the SAME global primitive both cancels multiplication failure and matches ALL
local prescriptions. This is an explicit strict low-degree cochain quotient. It is not silently
identified with a homogeneous continuous-cohomology API or a derived arithmetic Selmer complex.
Local zero-cochain gauge terms are not quotiented out in this strict construction.

## Secondary gluing obstruction

Once d b0 = c, the remaining local mismatch is

    m_i = a_i - res_i b0,

which is a continuous one-cocycle on G_i. Its class belongs to

    coker( Z1_cont(G,K) -> product_i Z1_cont(G_i,K) ).

Lean proves this class is independent of the chosen absolute primitive b0 and that it vanishes
exactly when the original representation has a simultaneous literal local lift. Surjectivity of
this restriction map is a sufficient extra condition AFTER absolute vanishing; it is not assumed
to hold in general. Z1 rather than H1 is intentional because the prescriptions are literal.

## Positive finite-image sector up to local conjugacy

If rho factors through a finite group Q with |Q| invertible in A, an absolute lift through Q exists
by the preserved v0.27 theorem. Suppose each local prescription is a representation of a displayed
finite group H_i mapping to Q, and |H_i| is also invertible in A. The release constructs independent
u_i in A^units with q(u_i)=1 such that

    t_i(h) = u_i L(loc_i h) u_i^(-1).

The lift pulls back continuously along any continuous finite quotient map. A matrix specialization
is included. This does not assert a single common conjugator, simultaneous literal equality, wild
image vanishing, or arbitrary prescriptions not factoring through the stated finite groups.

## Negative controls

1. Over Z/4 -> F2, let G=C2 x C2 and prescribe trivial characters on the two coordinate order-two
   subgroups, but the nontrivial character on the diagonal subgroup. All prescriptions agree on
   overlaps, every pair has an actual global lift, and the absolute obstruction is zero.
   Nevertheless no simultaneous lift exists. Both the constructed constrained class and the
   secondary gluing obstruction are proved nonzero. Local conjugacy cannot help in this rank-one
   commutative example.

2. Over Z/9 -> F3, use A=diag(-1,1), B=[[-1,6],[0,1]], and U=[[1,3],[0,1]].
   A and B are involutions with the same residue, and B=U A U^(-1), with U reducing to identity.
   They do not commute, so they cannot be literal images of the two generators of C2 x C2.
   An explicit global representation matches the two prescriptions up to independent local
   conjugacies. The group order 4 is invertible modulo 9.

## Replay

Use an existing portable kit pinned to Lean 4.34.0-rc2 and mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume
```

An explicit module-limit run reports PARTIAL, not PASS. The final result must report PASS, all
source and object hashes must agree, and all named constants must have allowed axiom reports.
The verifier recompiles 12 unchanged direct dependencies, 9 new source modules, and one audit
module. It reuses the pinned compiled Mathlib cache, not historical custom module objects.
This is self-review plus Lean checking, not an independent referee report or full-history replay.

Incremental scope: 41 theorem declarations, 36 definitions, 11 abbreviations, 899 new source lines.
There are 8 anonymous local topology instances in the finite character example. All 88 explicitly
named constants are axiom-audited. Helper results and examples are included in these counts;
no cumulative historical theorem count is asserted.

## Independent finite corroboration

`python3 checks/exact_examples.py` exhausts all 16 maps from `C2 x C2` to
`(Z/4Z)^units` and verifies the pairwise-but-not-global character prescription.
It also checks the tame matrix example by exact modular integer arithmetic.
`checks/FINITE_CHECKS.json` records the result. These finite checks corroborate
the examples and are not proofs of the universal results.
