# Independent arithmetic review: CyclotomicPrimeCoverage

**Normalized claim.** Fix a nonzero natural number n and an actual number field K that is an n-th cyclotomic extension of Q. After removing any prescribed finite set of rational primes, every automorphism of K/Q is represented by arbitrarily large rational primes p coprime to n. The sampled automorphism sends every n-th root of unity x to x^p. At every supplied maximal ideal P of O_K above (p), it stabilizes P, induces x -> x^p on the residue field, and has ramification index e(P/p)=1.

**Primary verdict: proved as written.** The frozen module establishes actual prime existence through the pinned Mathlib proof of Dirichlet's theorem and proves the residue-field property on all integral elements. Its coverage assumption is derived, not supplied. Scope is one fixed finite cyclotomic extension over Q. This is not coverage of every finite quotient of the absolute Galois group.

Review date: 2026-09-08. Independent raw-source and primary-Mathlib-source review, followed by an isolated compiler replay. No production source was changed. The new existential-prime-above wrapper was not part of this initial review; it must receive a separate source-pinned review when frozen.

## Frozen source and replay

Production source:

`lean/PaperX/CyclotomicPrimeCoverage.lean`

SHA256:

`497cb15ebc4b9c48206bcf1782758ef3f66c0c46c30a2168d6c169a9dcab6273`

The exact source was compiled independently with `-DwarningAsError=true`, using a private output directory and copied Block 24 predecessor proof objects. No Block 25 production proof object was used as an import fallback. Compilation exited 0 with an empty log. The rebuilt proof object has SHA256

`3d75a0f6000bd8128c473cada6cae633d6fc91ffe2b92aaf50d9f69fdaf221f8`.

A separate probe printed transitive axioms for all 16 public declarations: four definitions and twelve theorems. Every output contained only `propext`, `Classical.choice`, and `Quot.sound`. The probe also compiled the standard existential lying-over implication for a rational prime in an arbitrary number field; that private example is validation evidence, not a new production theorem.

Evidence resides in `privatechecks/cyclotomic_arithmetic_review/`. The copied predecessor build is reproducible temporary material; the logs, probe source, JSON records, and hashes are the durable review evidence.

## Arithmetic object and quantifier audit

### Rational primes and finite avoidance

`PermittedPrime n forbidden` is exactly the subtype

    {p : N // p.Prime and p.Coprime n and p notin forbidden}.

The forbidden set can be any finite set of natural numbers; it need not contain only primes. The conductor condition n != 0 is explicit. The cases n=1 and n=2 are permitted; the trivial cyclotomic Galois groups cause no exceptional branch. The module makes no claim about primes dividing n. When n is not the minimal conductor, this can omit more primes than necessary, which does not weaken the claimed existence.

`exists_prime_with_residue` invokes the actual theorem `Nat.forall_exists_prime_gt_and_eq_mod` for the unit class u and the bound max(B, forbidden.sup id). The proof derives coprimality from invertibility of the residue class. If p were forbidden, p <= forbidden.sup id would contradict the strict lower bound. Thus both arbitrary finite avoidance and p>B are proved, including empty forbidden sets and B=0.

The quantifiers are

    forall finite forbidden, forall sigma in Gal(K/Q), forall B,
      exists permitted prime p, p>B and sample(p)=sigma.

They do not posit one finite list of primes serving every automorphism or every bound, and give no effective upper bound or search-complexity bound.

### Actual cyclotomic automorphisms

`primePowerAutomorphism` is the inverse image of p mod n under the proved group isomorphism

    Gal(K/Q) ≃ (Z/nZ)^units.

Here `IsCyclotomicExtension {n} Q K` says K is the cyclotomic extension in question, not merely a larger field containing roots of unity. The primary Mathlib equivalence is obtained from `autEquivPow` and irreducibility of the rational cyclotomic polynomial.

`primePowerAutomorphism_apply` proves sigma(x)=x^p for every x in K satisfying x^n=1. Thus the sample is not merely an abstract residue label called Frobenius. It is an actual field automorphism with its root-of-unity action proved.

Surjectivity follows by applying Dirichlet to the unit class corresponding to a given actual automorphism. `primeSample_quotientCoverage` then covers any open normal quotient of this fixed finite group by taking an exactly equal sample and the identity conjugating element. No chosen set of conjugacy representatives or density assumption replaces prime existence.

### Every supplied prime above p

The residue section has parameters

    p : N, [Fact p.Prime], P : Ideal(O_K), [P.IsMaximal],
    [P.LiesOver (span {p})], hp : p.Coprime n.

Consequently, its statements are universal over every P satisfying these hypotheses. They do not assume that p splits completely, do not choose a distinguished P, and do not restrict to one residue degree.

The frozen module does not package an existential witness P above the prime returned by Dirichlet. That is a missing convenience wrapper if a stronger output explicitly includes P, not a flaw in its universal-in-P statements. Such P exists by the exact primary theorem

    Ideal.exists_maximal_ideal_liesOver_of_isIntegral
      (Ideal.span {(p : Z)}),

using integrality and faithful scalar action of Z on O_K and maximality of (p). These instances are present in the pinned imports. The private compiler probe confirms the one-line application for every number field and rational prime. The related instance `Ideal.nonempty_primesOver` also supplies primes above (p). Neither method needs n, coprimality, a splitting assumption, or a new arithmetic conjecture.

### Stabilizer and full residue-field action

`primePowerAutomorphism_mem_stabilizer` uses the primary theorem that the image of the actual decomposition group under `galEquivZMod` is the cyclic subgroup generated by p mod n. Membership of that generator supplies stabilizer membership. The imported stabilizer theorem is itself proved, via residue-field automorphisms and the unramified decomposition-group cardinality.

`primePowerAutomorphism_residue` proves

    reduction_P(sigma • x) = reduction_P(x)^p

for every x in O_K. The target is the actual quotient O_K/P, made a field by maximality. Its characteristic p is obtained from the injective algebra map from Z/(p). The two maps from O_K to the quotient are compared as Z-algebra homomorphisms. They agree on the integral primitive n-th root by the cyclotomic power formula, and `Rat.adjoin_singleton_eq_top` states O_K=Z[zeta], extending the equality to every integral element.

This integral-generation step matters: equality only on one root of unity without generation would not certify the residue-field action on all residues. The module supplies the generation theorem and uses it in the correct domain O_K. Since the quotient map is surjective, equality on all integral representatives is exactly the p-power action on the full residue field. Stabilizer membership ensures this action is the automorphism induced by sigma.

The convention is **arithmetic Frobenius**, x -> x^p. Geometric Frobenius is its inverse; the module does not silently identify those two conventions.

### Unramification

`permitted_prime_ramificationIdx` proves the explicit numerical statement

    Ideal.ramificationIdx P Z = 1

by the primary cyclotomic theorem `Rat.ramificationIdx_eq_of_not_dvd`. Primality turns p.Coprime n into p not dividing n. The imported proof uses integral generation, reduction of the minimal polynomial, and separability when p does not divide n.

This is the standard arithmetic unramifiedness criterion for these number-field primes. The frozen module states the index equality, not a new instance of `Algebra.IsUnramifiedAt Z P`. The primary library also contains the appropriate equivalence between index one and `IsUnramifiedAt` in this number-field setting. If downstream code needs that specific predicate, it should apply the equivalence explicitly; the current proof already supplies its numerical premise.

### Independence of the prime above p and conjugacy

The sampled automorphism is defined from p and the fixed cyclotomic extension and has no P argument. The same actual automorphism is then proved to satisfy the Frobenius property at every P above p. This is the correct independence from the choice of P in a cyclotomic, hence abelian, extension. The group isomorphism to `(Z/nZ)^units` also identifies the Galois group as commutative, so its conjugacy classes are singleton classes.

The module does not separately define a general canonical Frobenius operator or prove equality to such an operator by name. Nor does it state a stand-alone uniqueness theorem for all automorphisms satisfying the residue condition. Those are stronger API assertions that should not be counted as declarations present here. Mathematically, unramification gives uniqueness in the decomposition group; equivalently, the reduced primitive n-th root has order n when p is coprime to n, which determines the exponent. The module's explicit actual field automorphism, stabilizer membership, and full residue condition are sufficient to substantiate its stated “arithmetic Frobenius” terminology without inventing an unproved named comparison.

## Dependency leaves checked

| Arrow | Primary source and result | Verdict |
|---|---|---|
| Unit residue class to arbitrarily large actual rational primes | `NumberTheory/LSeries/PrimesInAP.lean`, `Nat.forall_exists_prime_gt_and_eq_mod` | Passed; exact theorem and proof inspected |
| Infinite-prime input behind that theorem | Same file, `infinite_setOfPred_prime_and_eq_mod`, `not_summable_residueClass_prime_div` | Passed at imported proof level; these are proved results, not axioms |
| Cyclotomic Galois group to unit residues | `NumberTheory/NumberField/Cyclotomic/Galois.lean`, `galEquivZMod` | Passed |
| Automorphism acts by exponent on all n-th roots | Same file, `galEquivZMod_apply_of_pow_eq`, `galEquivZMod_smul_of_pow_eq` | Passed |
| Generator residue lies in actual decomposition group | Same file, `galEquivZMod_stabilizer` | Passed |
| Equality on integral zeta extends to O_K | `NumberTheory/NumberField/Cyclotomic/Basic.lean`, `Rat.adjoin_singleton_eq_top` | Passed |
| Coprime prime is unramified | `NumberTheory/NumberField/Cyclotomic/Ideal.lean`, `ramificationIdx_eq_of_not_dvd` | Passed |
| Z/(p) has characteristic p and is a field | `RingTheory/Ideal/Int.lean`, `Int.ringChar_idealQuot`, `Int.ideal_span_isMaximal_of_prime` | Passed |
| Prime-above existence, if packaged | `RingTheory/Ideal/GoingUp.lean`, `exists_maximal_ideal_liesOver_of_isIntegral` | Available and private application compiled; not a production conclusion of the frozen module |
| O_K integral over Z | `NumberTheory/NumberField/Basic.lean`, `Algebra.IsIntegral Z (O_K)` instance | Passed |
| Index-one interpretation | `NumberTheory/RamificationInertia/Unramified.lean` and the referenced index-one equivalence | Source interpretation checked; no new predicate theorem compiled in this review |

The primary mathematical source here is the local pinned Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Dirichlet's proof uses its analytic dependencies. This review checks the exact invoked theorem and its application and audits transitive axioms; it does not claim an independent reconstruction of the entire analytic proof from first principles. No web source or unverified literature assertion is used to discharge the new theorem.

## Remaining scope

This module proves the arithmetic coverage leaf for the actual finite cyclotomic group Gal(K/Q), including every finite exclusion. It does not prove:

- coverage for arbitrary finite Galois extensions or every open normal quotient of the absolute Galois group;
- Kronecker–Weber or containment of every abelian extension in such a field;
- Galois-to-Weil–Deligne or Hodge–Tate attachment;
- the full arithmetic Claim 9.1 for arbitrary absolutely irreducible compatible systems.

An application to representations already factoring through this fixed cyclotomic quotient can now use proved prime coverage instead of a coverage hypothesis. Pullback, quotient factorization, representation continuity, and the ordinary-trace convention must remain explicit in any broader application.

## Source and evidence hashes

The production source is independently reviewed at the exact hash above. Direct primary source leaves and interpretation sources inspected are pinned below; this table is not a claim that every line of their transitive imports was independently reread.

| Source | SHA256 |
|---|---|
| Mathlib `NumberTheory/LSeries/PrimesInAP.lean` | `a2491d48850056b27fe6ad31cf7b210a7f6455e8e0fa4fbb714671bbffb61ca4` |
| Mathlib `NumberTheory/NumberField/Cyclotomic/Galois.lean` | `1681a3493873d5a04d9cc5c6254de0ee48403291ecf410d768b43c445ced4216` |
| Mathlib `NumberTheory/NumberField/Cyclotomic/Basic.lean` | `3e454ef15141368c7fabb3db375f371a010f721aa131e4c73b87ddd2f4ff876d` |
| Mathlib `NumberTheory/NumberField/Cyclotomic/Ideal.lean` | `46ac69c6ea3635f12ff5b8fc8e1ff393e2b270cd0726acf8b02d53ff2ff568c6` |
| Mathlib `RingTheory/Ideal/GoingUp.lean` | `6363ce60994dd160c97aa0919d401ab9e1ccac4711d7cb9c4036c84bf622e065` |
| Mathlib `RingTheory/Ideal/Int.lean` | `6a34f6d45487752d5e8ff75755eca667c0720c906b72916b8adbfaf5f5762e85` |
| Mathlib `NumberTheory/NumberField/Basic.lean` | `4e9e600e2aeee2c69f498c2d5d8af2622b03d35a13e4f61dbb5730a88a7eb58b` |
| Mathlib `NumberTheory/RamificationInertia/Unramified.lean` | `85a59e5b62d5f0ab1c72b13cd958e93481e6ac2894c91389c3bc5696015e94cc` |
| Mathlib `NumberTheory/RamificationInertia/Galois.lean` | `8b982a93096532a4fb980947e5c803ead6ae78cadd4c9421aac359b37f00a499` |
| Block 25 `lean/PaperX/CyclotomicPrimeCoverage.lean` | `497cb15ebc4b9c48206bcf1782758ef3f66c0c46c30a2168d6c169a9dcab6273` |
| Block 25 `lean/PaperX/ProfiniteSeparation.lean` | `c23660150cd7a55a7da46770967d33dd9e3c068ced194f78e928be0f00b7ee1b` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/compile.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/verification.json` | `48b7e8ab715ef3c2fbd690fc0bdcc688dfc74f60a44bf99c6f5948c8f8cc7d6c` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/ArithmeticProbe.lean` | `31bd0ff02da85c81df5aff251378b429a0d8818df1abb793572366376ff2eeee` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/arithmetic_probe.log` | `8e2670df30971d2f9a679d8d71c32394339bdaa724d182fcbcfa2585c0e91b1c` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/arithmetic_probe.json` | `a1a497c91882c07f95ac7b514839d6d9765ec0cf06d645a45b3292f41192b99b` |
