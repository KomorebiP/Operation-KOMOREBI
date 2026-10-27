# A numerical realization contract for a proposed IUT repair

Checkpoint: ABC-20261025-RR5, based on RR4 archive SHA-256
`689847eefd2cf75b9804b574d6613c13d10606e6e805a979cd74facb998ea8ae`.
Owner: `/root/iut_numeric_bridge`.

## 1. Scope and exact source location

This note proves elementary order and error-budget lemmas. It does not construct
an IUT comparison, model the full IUT axioms, refute those axioms, or establish
ABC. Its purpose is to give a precise, falsifiable numerical obligation for a
comparison proposed as a repair.

The source inspected is Shinichi Mochizuki, *Inter-universal Teichmuller theory
III: Canonical splittings of the log-theta-lattice*, author PDF dated May 2020,
199 PDF pages, proof of Corollary 3.12, Step (xi-d)--(xi-f), printed pp. 183--184.
Locator:
<https://www.kurims.kyoto-u.ac.jp/~motizuki/Inter-universal%20Teichmuller%20Theory%20III.pdf>.
Checked 2026-10-25 through the primary author URL. Browser extraction reference:
`turn52view0`, lines 9632--9693. The PDF bytes were not retained or hashed in this
route. This is a location/extraction check, not an audit of the surrounding
theorems.

Step (xi-d) defines a downward real ray with endpoint
`b = -|log(Theta)|` and identifies `q0 = -|log(q)|` as a real log-volume. Step
(xi-f) infers `q0 <= b`, allowing approximation in its preceding discussion.
The source asserts that the relevant input/output relationships establish this
inference. We do not independently establish or disprove that source-dependent
assertion here.

Let `V` below mean the actual numerical values obtained from the admissible
output representatives, after all required hull, determinant, normalization,
and indeterminacy operations. The set `V` is an abstract argument of our lemmas,
not a construction of that set from IUT. In particular, we do not silently
identify `V` with the whole downward ray asserted in the source.

## 2. The exact order-theoretic obligation

Let `q0` be a real number and `V` any subset of the real numbers. Use extended
suprema, with `sup(empty)=-infinity`.

**Lemma 1 (upper cofinality).** The following are equivalent:

1. `q0 <= sup V`.
2. For every real `eta>0`, there is `v in V` with `v > q0-eta`.
3. Every real upper bound `b` of `V` satisfies `q0 <= b`.

Consequently, if `V` has a finite upper bound `b`, any of these conditions
implies `q0 <= b`. Neither exact attainment `q0 in V` nor convergence to `q0`
from below is needed.

*Proof.* If the first condition holds, `q0-eta` cannot be an upper bound for
`V`, so the second holds. Conversely, if `sup V<q0`, choose `eta>0` smaller
than `q0-sup V` when the supremum is finite. If `V` is empty, the second
condition also fails. Thus the second implies the first, including the
extended cases. The first implies the third because every upper bound is at
least `sup V`. If the first fails and the supremum is finite, taking
`b=sup V` disproves the third. If `V` is empty, take any `b<q0`.
If `sup V=+infinity`, all three hold, the third vacuously. This proves the
equivalence. In that last case there is no finite upper bound to transfer. QED.

This is the weakest sufficient condition in the following precise sense: it
is equivalent to transferring *every* finite real upper bound of `V` to `q0`.
For one preselected endpoint `b`, it is sufficient but need not be necessary.
The condition is independent of whether the representation maps before
measurement are linear or nonlinear.

**Examples.** For `V={q0-1/m : m>=1}`, the conclusion holds although the input
value is not attained. For `V={q0-1}`, it fails. These are elementary examples
about the lemma, not IUT countermodels. Merely labelling the elements as outputs
over a particular ring or linking their underlying objects by an isomorphism
does not specify which of these numerical situations occurs. A genuine
application must prove how the specified measurements interact with its actual
maps and admissible regions.

## 3. Additive distortion and its optimal scalar budget

Let `E>=0` be finite. The following distorted realization hypothesis suffices:

    for every eta>0, some v in V satisfies v > q0-E-eta.       (R_E)

If all `v in V` satisfy `v<=b`, then

    q0 <= b+E.                                               (1)

This follows by Lemma 1 applied to `q0-E`. When `V` is nonempty with finite
supremum `s`, the smallest nonnegative `E` for which `(R_E)` holds is exactly

    D = max(0,q0-s).                                         (2)

Indeed `(R_E)` is equivalent to `q0-E<=s`, or `E>=q0-s`.
This identifies the actual scalar loss that a proposed construction must bound.
It supplies no bound on that loss for IUT or ABC inputs.

If `V` is empty, no finite `E` satisfies `(R_E)`. If `V` is unbounded above,
`E=0` works, but no finite output upper bound `b` can then be invoked. These
two edge cases cannot provide a finite height bound.

### Branch and normalization compatibility

Suppose admissible choices are indexed by `alpha`, with value sets `V_alpha`.
The realization and upper-bound assertions must concern the same value set and
the same normalization. Either prove `(R_E)` and `V_alpha<=b` for one common
choice `alpha`, or use the union over choices and a bound valid for that union.
Realization in the union and an upper bound for just one chosen branch do not
suffice: `q0=0`, `V_1={0}`, `V_2={-100}` demonstrate the logical mismatch.
No inference is drawn here about which quantifier structure actual IUT uses.

## 4. Amplification with a genuinely controlled loss

Write `Q>=0` and `Theta>=0` for positive magnitudes, so `q0=-Q` and `b=-Theta`.
Equation (1) is

    Theta <= Q+E.                                            (3)

If an independent arithmetic estimate also gives

    Theta >= kappa Q-L,   kappa>1,                           (4)

with finite `L`, then

    (kappa-1) Q <= E+L.                                      (5)

This is obtained by substituting (4) in (3) and subtracting `Q`. Thus a positive
amplification factor is useful only after controlling the sum of the numerical
transport loss `E` and the independent-estimate loss `L`. Enlarging an
admissible hull can alter those losses and cannot simply be called free.

Equation (5) is generic algebra. In this note neither `Q=log c`, nor a particular
`kappa`, nor a conductor estimate for `L` has been derived from IUT. Actual
applications must supply that dictionary, including all normalizations and
auxiliary-parameter dependence.

## 5. What a uniform error budget would have to achieve for ABC

Here is a separate, fully stated stability lemma for the final ABC height
variables. It does not assert that IUT produces its hypothesis.

Let `H=log c`, `r=log rad(abc)` for every primitive positive triple `a+b=c`.
Fix a real `K>0`. Suppose real errors `F(a,b,c)` satisfy both

    K H <= K r + F(a,b,c),                                   (6)

and, for every `delta>0`, a constant `C_delta>=0`, independent of the triple,
exists such that

    F(a,b,c) <= delta H+C_delta.                             (7)

Then the all-epsilon ABC conjecture follows in its constant form. In fact, for
any `epsilon>0`, choose `delta=K epsilon/(1+epsilon)<K`. Equations (6)--(7)
give

    H <= (1+epsilon) r + C_delta/(K-delta).                   (8)

Exponentiating proves `c <= A_epsilon rad(abc)^(1+epsilon)` with
`A_epsilon=exp(C_delta/(K-delta))` independent of the triple. Applying (8) first
with a smaller exponent, such as `epsilon/2`, also gives the usual finitely many
exceptions formulation at exponent `epsilon`: a violating triple has bounded
radical, then bounded `c`, then belongs to a finite set of positive triples.

The uniformity in (7) is essential. If one merely allows a new unconstrained
constant for each triple, choose `F=K max(0,H-r)`. Then (6) always holds and
contains no new information about ABC. Thus an observed finite collection of
small losses, or point-dependent error terms, cannot close this route.

This stability lemma is not an alternative route to ABC by itself. Its purpose
is to state the accuracy required of a quantitative comparison once the
arithmetic estimate and normalizations have been independently proved.

## 6. Outcome and continuation

Proved here: the exact upper-cofinality transfer criterion, its additive-loss
version, its optimal scalar defect, and the uniform-error stability implication.
These are elementary general lemmas, with no novelty claim and no load-bearing
finite computation.

Open source-dependent obligation: construct the actual admissible output value
set from IUT's stated data, in the normalization used by its conductor/height
estimates, and prove `(R_0)` or a quantitatively sufficient `(R_E)`. This must
retain the actual hull, determinant, indeterminacy, and branch quantifiers.
We have not checked that those constructions satisfy this criterion, nor shown
that they cannot. The next discriminating check is an exact derivation of the
numerical realization property from the IPL/SHE comparison and its referenced
dependencies, rather than another change of vocabulary for that property.
