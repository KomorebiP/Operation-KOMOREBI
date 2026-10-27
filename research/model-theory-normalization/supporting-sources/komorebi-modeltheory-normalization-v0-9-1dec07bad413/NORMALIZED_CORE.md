# A costed evaluator for exact observation discovery

Author: Komorebi P.

## Lineage and exact claim

The sole immediate predecessor is Komorebi_ModelTheory_Normalization_v0.8.zip,
SHA-256 cd68b63a1e1ac76a93d2d791cd3e2ecf175b1da421f9519f1d9909a20d61b1b5.
That archive is preserved verbatim under history/. Inherited Lean proof files are
unchanged. This advances Model-Theory Normalization only; it does not advance the
parallel Logical Resolution, Representation Calculus, or p-adic release numbers.

The target is a costed evaluator whose value equals the existing solver, together
with exact primitive-count identities and a polynomial bound on its declared
high-level arithmetic units. This is NOT a theorem about CPU instructions, elapsed
time, allocated memory, native big-integer implementation, or proof-kernel work.
Completed build and test evidence belongs in RESULTS.md and the manifests, not in
this mathematical exposition. Interpretation is self-review, not external refereeing.

## 1. Mathematical interface

The input is a complete linear system on all states of (Z/(p^r))^d, with k operation
matrices and o observation rows. The required semantics includes every finite word
and every initial state. The empty word is included. Right multiplication of an
observation row by an operation matrix PREPENDS the corresponding operation to
its recorded input word.

The existing FIFO algorithm discovers the full module spanned by all future
observation rows. It stores a normalized positive-pivot integer basis of the full
preimage of the accepted modular row module. It neither saturates over Q nor treats
nonunits as invertible. Its verified reference result, size/horizon bounds, and
standard guarded first-order defining formula are inherited.

## 2. Value paired with a declared arithmetic count

Eval(alpha) = alpha x Nat. Each new evaluator computes its value through the
metered recursive subroutines; it does not obtain a value by calling the whole
unmetered algorithm and attach an arbitrary bound afterward. Each returned Nat
counts the units specified in COST_MODEL.md. Erasing that Nat is proved to recover
the inherited value.

The model charges each scalar arithmetic operation once under an eager dense-array
interpretation. In the Lean value definitions, vectors remain functions on Fin d.
The count does not prove that Lean's evaluator or compiler materializes those
functions once or follows this particular sharing strategy. That refinement is an
explicit remaining obligation. Counter bookkeeping itself is not charged.

## 3. Exact arithmetic counts

Let E(a,b) be the number of nonterminal calls in the inherited Euclidean descent.
The actual metered coefficient routine has cost 5E(a,b)+1: a terminal zero test costs
one, and a nonterminal comparison, remainder, division, multiplication, and subtraction
cost five. The signed wrapper costs four more units.

The predecessor separately computes gcd and Bezout coefficients. The costed evaluator
therefore includes a second real Euclidean gcd evaluation, not an uncharged native
gcd call. Its cost is 2E(a,b)+1. The separate recursive gcd is proved equal to Nat.gcd.

A dot product of n entries costs 2n units. A row-times-d-by-d-matrix action costs
2d^2 units. Reconstructing the row of a word of length h costs exactly 2d^2 h. Every
popped candidate is reconstructed from its word; no source-row cache is assumed.

For a positive-pivot triangular basis of dimension d:

* Membership costs at most d^2+2d units, and may stop early on a failed pivot.
* Full residue reduction costs exactly d(d+1) units.
* Bottom-up normalization costs C(d), where C(0)=0 and
  C(d+1)=C(d)+d(d+1). Universally, 3C(d)+d=d^3.
* Insertion costs exactly 3d^2+8d+7 sum_i E_i, with the actual Euclidean call count
  E_i at each insertion level.
* Normalized insertion adds C(d) to that insertion cost.

The insertion formula counts gcd and extended-gcd work separately, two signed
absolute-value conversions for gcd, two pivot quotients, a negation, and all four
products and two sums for each pair of tail entries. Zero-dimensional cases have
zero cost. Normalization of the initial diagonal basis is still executed and
charged; its zero-valued arithmetic is not silently optimized away.

Theorems: euclidEval_units, gcdEval_units, signedEuclidEval_units, dotEval_units,
rowEval_units, testEval_units, coordinatesEval_units_le, residueEval_units,
normalizationUnits_cubic, insertEval_units, updateEval_units.

## 4. Costed FIFO evaluation and exact semantic refinement

The costed run evaluates a popped observation row, lifts its d entries to integers,
uses metered membership, tests whether that result is present, and on acceptance
uses metered insertion and normalization. It then performs the same FIFO update.
Success is possible only at an empty queue with positive remaining fuel; fuel zero
returns none. Arithmetic accumulated before exhaustion is retained in the counter.

For EVERY fuel budget, cache, accepted list, and pending queue:

    (runEval ...).value = boundedRun ... .

For the default prime-power wrapper:

    (discoverEval ...).value = boundedPrimeDiscover ...
                            = finitePrimeDiscover ... .

The initial normalization is part of discoverEval's arithmetic count. Supplied
modulus/matrices, input parsing, computation of p^r as an input representation,
list allocation/traversal, index manipulation, and output serialization are outside
this arithmetic model. They are not claimed to be free in an actual implementation.

The inherited prime-power theorem therefore gives successful output, complete
observable span, at most rd accepted tests, all returned words shorter than rd,
and the standard first-order defining formula for complete future behavior.
Theorems: runEval_value, discoverEval_value, discoverEval_eq_reference,
discoverEval_total_correct, discoverEval_defines_behavior, discoverEval_code.

This does not make the raw test list minimal, nor enlarge the observational language
to unrestricted first-order semantics. Prime hypotheses are needed for the reused
successful-return guarantee; the value refinement and fixed-fuel arithmetic bound
have broader positive-modulus scope.

## 5. A formally proved polynomial arithmetic-unit bound

Let m=p^r>0 and choose b with m <= 2^b. Put

    B = b + (2b+2)d + 1,
    F = o + k(rd) + 1.

The previous bound m[2m(m+1)]^d < 2^B applies to the real insertion operands. The
previous Euclidean theorem implies E_i <= 2B at each of d levels. Thus

    update cost <= 3d^2 + 8d + 14Bd + d^3.

For a pending-word horizon h and fuel f, child words grow by at most one per
acceptance. An induction bounds the run by f times a per-round bound evaluated at
h+f. This works on incomplete and complete runs. It conservatively charges a full
update on every possible round, even though many rounds are skips.

At the initial empty-word frontier, the universal final inequality is

    discoverEval.cost <= d^3 + F(2d^2 F + d^3 + 4d^2 + 11d + 14Bd + 1).

Every symbol on the right is explicit. This is a polynomial in the displayed
parameters after substituting B. It is a cost theorem for the stipulated high-level
arithmetic evaluator, NOT a bit-runtime theorem. Division and multiplication each
cost one unit in it even though their native or bit costs differ.

Theorems: updateEval_uniform_bound, runEval_units_bound,
discoverEval_units_bound, discoveryUnitsBound_expansion.

## 6. Concrete boundary checks

Starting with 4I in dimension two and inserting (3,3), raw insertion costs 56 units;
normalization adds two; the normalized update costs 58. Claiming 57 is rejected.
Normalizing 4I costs two, not zero. A membership failure at the first pivot costs
two units, not zero. Noncommuting action words are checked in both orders, so
reversing word semantics is not masked by identical counts.

The inherited synthetic eight-coordinate source modulo 65536 has 2^128 possible
initial states. It is evaluated without state or coefficient-tuple enumeration.
The new exact counter is 2465 units. The generic polynomial upper bound is 17092754.
The descending 24-test torsion example modulo 2^24 costs 696 units; its generic
bound is 57086. These deliberately coarse bounds are not intended to predict runtime.

All 203 inherited sources receive kernel-computed equalities of the pair
(some expectedTests, exactUnits), not just equality of the returned test list.
Their all-word logical certificate is obtained separately from the general theorem.
The Python port meters its individual scalar primitives and agrees with every
saved result/count pair. It is independently tested, not formally extracted code.

## 7. Boundaries and next obligation

The selected value-refinement and arithmetic-unit bound are closed at the supplied
Lean declarations, subject to the completed audit records. A complete backend-level
bit-complexity theorem still needs explicit priced integer primitives, data access,
sharing/allocation semantics, and a refinement from the implementation to that model.
The previous written schoolbook analysis is not upgraded to a verified runtime
claim merely by adding this unit counter.

Parsing/export, minimum formula/test count, general relational or multi-input
discovery, trained search policies, independently held-out performance studies, and
external review remain separate. No historical novelty is claimed for standard
cost annotation, Euclidean recurrences, or integer-lattice arguments.
