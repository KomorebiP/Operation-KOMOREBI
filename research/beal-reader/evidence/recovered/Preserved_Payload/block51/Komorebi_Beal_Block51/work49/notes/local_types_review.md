# Independent audit of the local monodromy calculation

**Normalized claim.** For every positive pairwise-coprime integer solution of
`A^3+B^5=C^7` with `15 | C`, put `K=Q(sqrt(5))`,
`D=3(5-sqrt(5))/2`, and let `J^nu` be the Jacobian of
`z^2=D(x^6+10Bx^3+12Ax+5B^2)`. With `v_3(3)=1` at the inert prime
over three and `v_5^K(sqrt(5))=1` at the ramified prime over five, its
split toric monodromy pairing in the two twin-loop bases is respectively
`(7v_3(C)-3) I_2` and `(14v_5(C)-5) I_2`. The actual representation
`J^nu[7]`, on the natural Jacobian lattice, consequently has tame inertia
rank two and Artin conductor exponent two at both places.

**Primary verdict: proved as written.** The assertion about rank-two RM
factors retains its stated hypothesis of an integral RM decomposition.
The audit finds no implication about integer nonexistence and no
lattice-independent residual ramification assertion. Neither is justified
by this local result, and neither is claimed in the audited note.

This is a fresh mathematical audit, using the proof-audit and
literature-check workflows. It is not a formal verification. The main
note and script were not edited by the reviewer.

## Reviewed revisions and source boundary

Checked on 2026-09-19 in `/workspace/scratch/3e94b90aa142`:

| Artifact | SHA-256 |
|---|---|
| `work49/notes/local_types.md` | `9d7284d9a050acf4de2db9d7e85a1b91eed6ad01590c41cd199ec2f1538d2bfc` |
| `work49/computations/local_types_exact.py` | `d250fe8c0245358c2acaeff1348916f8f99aff2b51b94cd3e6107e3100bcae0e` |
| `work49/computations/local_types_contract.json` | `e0eee5cfdf2988c84b2881b68cf21dfdf56034e97cd5729a0f1b7bd33c76b5f5` |
| `work49/verification/local_types_run/result.json` | `61dedcf6a29cffab680a7b347e8e38dcfb404da2889efad0d4cefddd96c3e14e` |

The project target contract was read. No applicable `AGENTS.md` or
`.mathbox` ledger was found within this workspace by the scoped file search.
The exact cached primary sources were read, including their title/version
pages and the relevant theorem bodies. This audit made no novelty or
literature-completeness search.

* Dokchitser--Dokchitser--Maistret--Morgan,
  *Arithmetic of hyperelliptic curves over local fields*,
  [arXiv:1808.02936v2](https://arxiv.org/pdf/1808.02936v2), 15 October 2018.
  Cached PDF SHA-256:
  `f46f20a4adf8215c566252779a3b4b9028890df36013c7b747fcec2c0313f3a5`.
  Checked Definitions 1.4--1.7, 1.9, 1.11--1.12; Theorems 1.8,
  1.14, 9.3 and 10.3; and Section 2.2, especially (2.9)--(2.12)
  and Lemma 2.21. The definitions/theorems apply in odd residue
  characteristic and use the normalized discrete valuation of the base.
* Baker--Rabinoff, *The skeleton of the Jacobian, the Jacobian of the
  skeleton, and lifting meromorphic functions from tropical to algebraic
  curves*, [arXiv:1308.3864v1](https://arxiv.org/pdf/1308.3864v1),
  18 August 2013. Cached PDF SHA-256:
  `acf7cd5977d24d8561718b33c0d855996f131cbb075189eedff6bdb9a64e6010`.
  Checked the general complete-field hypotheses preceding Theorem 2.9,
  Section 4.1, Section 5.1, the proof of Theorem 2.9 in Section 6,
  and Remarks 6.3--6.7. The relevant comparison does not require the
  original local base field to be algebraically closed: the general
  formulation uses a split semistable model and is compatible with
  base extension.

## Dependency graph

1. Primitivity and `15 | C` make `A,B` units at both primes.
2. Unique local fifth/cube roots give the two normalized perturbations
   of `F_0=(x^2+x-1)^2(x^2-2x+5)`.
3. Exact coefficient valuations and the Newton polygons give the two
   twins and their absolute depths; Hensel estimates locate the other
   roots and establish the principal clusters.
4. Galois-stable discs, separable twin reductions and the principal
   invariants establish the DDMM semistability criterion over the
   original base field.
5. The square classes `D g'(r)^2 h(r)` give trivial Galois characters
   on both twin loops. This establishes splitness, including Frobenius.
6. The DDMM integral homology pairing and the graph/period comparison
   give the two exact integral monodromy matrices.
7. Kummer theory for periods at residue characteristic different from
   seven gives the asserted actual inertia operators on `J^nu[7]`.

Steps 1--5 are local algebra/valuation arguments. Steps 4--6 also use
the checked external theorems. The companion computation supports the
symbolic identities and finite Newton-polygon checks, but does not
replace those arguments or the external theorems.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Local base fields and valuation normalization | Passed | Three is inert in `Q(sqrt(5))`; five is ramified with uniformizer `sqrt(5)`, so rational five-adic valuations double. |
| Normalized perturbations | Passed | `B/u^3=1+epsilon` at three and `A/u^5=-1+epsilon` at five give the displayed polynomials and `v(epsilon)=7c_3,14c_5`. |
| Coefficient valuations, all `c>=1` | Passed | Perturbation valuations strictly exceed the relevant nonzero limiting coefficients; the constant/linear leading terms are units times `epsilon`. |
| Twin mutual depths | Passed | After at most adjoining a square root of the uniformizer, the two leading residual roots are distinct because the residue characteristics are odd. |
| Singleton/root separation | Passed | Explicit Hensel derivative/displacement estimates below exclude extra subclusters. |
| Root splitting ramification at most two | Passed | Both stable twin factors are quadratic; over the maximal unramified field every unit is a square, leaving only the uniformizer square class. |
| Principal clusters and `nu_s` | Passed | At three there are two triples of depth one with `nu_s=4`; at five one five-cluster of depth one with `nu_s=6`. The full six-cluster is excluded from principality because it has two children. |
| Totally toric reduction | Passed | There are precisely two even non-ubereven clusters besides the full set, and all normalized principal components have genus zero. |
| Galois splitness | Passed | Each twin is fixed and its defining radicand is a square in the base field; this includes the arithmetic Frobenius action. |
| Exact integral monodromy pairing | Passed | Each twin has `t^*=t`; distinct generators are orthogonal, and diagonal entries are `2(d_t-1)`. |
| Period valuation comparison | Passed | Checked BR Theorem 2.9/Remark 6.7; DDMM Section 2.2/Lemma 2.21 also supplies the integral Galois-equivariant monodromy comparison. |
| Natural residual inertia/conductor | Passed | The two matrices reduce to `4 I_2` and `2 I_2` modulo seven; units contribute no inertia Kummer class. |
| Rank-two RM-factor conclusion | Conditional as stated | An actual integral rank-two decomposition is assumed; this note does not construct it. Once supplied, rank two of the full nilpotent operator forces rank one on each factor. |
| Orientation of a globally reducible natural RM representation | Passed under its stated hypotheses | Nonzero local rank-one monodromy forces the unique invariant line to be the cyclotomic line; Frobenius at norm nine distinguishes it from the trivial character. |
| Same residual conclusion for every stable lattice | Out of scope | The audited note explicitly rejects this inference. |

## Reconstructed local details

Write `r_+=(-1+sqrt(5))/2`, `r_-=(-1-sqrt(5))/2`. At three,
the two residues are distinct in `F_9`, and `r`, `r-1`, `2-r` are
units. At five, both residues are `2`, their mutual distance has
valuation one, and `h(r)=3(2-r)` has normalized valuation one.

For `c>=1`, the lower hulls follow uniformly, not just for the finite
range in the script:

| Place | Coefficient valuations in degrees 0 through 6 | Lower-hull vertices | Twin depth | Principal depth |
|---|---|---|---|---|
| Three | `(7c,7c+1,1,0,1,1,0)` | `(0,7c),(2,1),(3,0),(6,0)` | `(7c-1)/2` | `1` |
| Five | `(14c,14c,3,2,2,0,0)` | `(0,14c),(2,3),(5,0),(6,0)` | `(14c-3)/2` | `1` |

The minimum values `c=1` already make the inequalities strict where
required. At five the degree-three point lies on the middle side,
but this does not justify treating its residual cubic as separable.
The proof correctly avoids that inference by constructing both twins
and locating the remaining roots from `h`.

Here is an explicit Hensel justification for that last step and for the
square-class comparison. The two roots `a` of `h` are simple since its
discriminant is `-16`.

* At three, each `h` root is distance one from the corresponding `r`;
  it is distance zero from the other `r`. Thus
  `v_3(F_0'(a))=v_3(g(a)^2 h'(a))=2`. The perturbation at `a` has
  valuation at least `7c>=7`, and its derivative has higher valuation
  than two. Hensel's inequality therefore applies, and the perturbed
  singleton has displacement valuation at least `7c-2>=5`, strictly
  greater than the distance-one scale.
* At five, the near `h` root is distance one from both `r_+` and `r_-`,
  so `v_5^K(g(a))=2` and `v_5^K(F_0'(a))=4`. The perturbation has
  valuation `14c>=14`; the near singleton displacement has valuation
  `14c-4>=10`. The far `h` root has unit derivative and remains at
  distance zero from the entire five-cluster.

Consequently the ratio of the outside-root product for a twin to its
limiting outside-root product lies in `1+m` and is defined over the base
field. The limiting product is `g'(r)^2h(r)`. With
`phi=(1+sqrt(5))/2`,

`h(r_-)=h(r_+) phi^2`, `h(r_+)=D`.

Thus both `D h(r)` are squares, and the ratio in `1+m` is also a square
by Hensel's lemma. This proves the graph characters are trivial as full
local Galois characters, not merely on inertia. The character and period
lattices are then trivial Galois modules; principal polarization supplies
the integral identification needed for the compatible period bases.

The residual quadratic statement for a half-integral slope should be
read after scaling over a field containing a square root of the
uniformizer. In the usual base-field Newton-polygon convention, the
unscaled residual polynomial attached to such a side can instead be
written with degree one. This convention issue does not alter the root
separation or the ramification-degree conclusion.

## Natural lattice and conductor

For the split totally toric uniformization `T/Y`, multiplication by seven
gives the actual Galois-module sequence

`0 -> mu_7^2 -> J^nu[7] -> Y/7Y -> 0`, with `Y/7Y=(Z/7)^2`.

At either place every local unit has a seventh root over a finite
unramified extension: lift a residue-field seventh root using a derivative
which is a unit. Hence the restriction of the period Kummer classes to
inertia is exactly their valuation matrix modulo seven. The two values
are `4 I_2` and `2 I_2`, both invertible. A tame inertia element on which
the mod-seven tame character is nonzero has a square-zero operator of
rank two. Its invariant space has dimension two, wild inertia is trivial,
and the full four-dimensional conductor exponent is two.

The lattice limitation is substantive. Even in a local two-dimensional
representation of shape `[[chi,c],[0,1]]`, replacing a stable basis
`e_1,e_2` by `e_1,7e_2` multiplies the upper-right entry by seven and can
make its reduction vanish. This is only a local illustration; it neither
constructs a globally stable lattice with the desired properties nor
preserves finite-flat conditions at seven. The note correctly leaves
such global and seven-adic obligations to a separate argument.

The added orientation corollary was also checked on the revision hashed
above. If a natural rank-two residual factor has global semisimplification
`1 + chi_bar` and is reducible, its global invariant line is invariant
under local inertia. A nontrivial two-dimensional unipotent operator has
exactly one invariant line, its kernel, which here is the toric
`chi_bar` line. At the prime over three the residue field has size nine,
so arithmetic Frobenius has `chi_bar=9=2 (mod 7)`, whereas the trivial
character has value one. Thus the global line cannot carry the trivial
character; it carries `chi_bar`, and the quotient is trivial. The local
extension is nonsplit, so the global extension is nonsplit. This verifies
the claimed orientation without assuming a global lattice-change result.

## Computation checks and limits

The script was rerun with Python 3.12.14:

`python work49/computations/local_types_exact.py`

It passed its exact quadratic-algebra identities and its `c=1,...,100`
Newton-hull/discriminant-compatibility checks. The multiplication rule
implements `r^2=1-r`; the hull orientation is correct for the ordered
points. The script is transparent about not implementing p-adic geometry.
In particular, its valuation arrays are inputs, not derived valuations:
their uniform validity rests on the written local argument checked above.
Likewise its discriminant compatibility lines substitute the already
computed cluster depths; they do not independently compute a resultant.

As a separate scratch sanity check, a rational-arithmetic determinant of
multiplication by `f'` in `Q[x]/(f)` was used to compute the discriminant
for `(-1,1+3^7)`, `(-1+5^7,1)`, `(-2,3)` and `(3,2)` as `(A,B)`.
In all four cases the ratio to `(A^3+B^5)^2` was `9331200000`.
The first two tests gave ordinary valuations `v_3=20` and `v_5=19`,
respectively, agreeing with `6+14` and `5+14`. These are finite checks
of perturbation inputs, not integer solutions and not a proof of a
universal discriminant identity. The review verdict does not depend on
them. An attempted optional symbolic check using SymPy could not run
because that package was unavailable; no result was inferred from it.

## Remaining gap and strongest safe statement

There is no remaining gap in the asserted local theorem. The cheapest
next step is to use it only with its natural-lattice scope. Any global
argument invoking a different residual extension must identify its actual
stable lattice and recompute the relevant local extension and finite-flat
properties. The present result proves a precise obstruction to the
shortcut that twisting alone makes the natural seven-torsion unramified
at three and five; it does not exclude the remaining Diophantine branch.
