# Independent review: actual primes above cyclotomic Frobenius samples

**Normalized claim.** For each permitted rational prime p in a fixed finite cyclotomic extension K/Q, there exists an actual maximal ideal P of O_K above (p), with ramification index one, stabilized by the sampled automorphism, and with its actual integral residue action equal to the p-power map. For every automorphism sigma, every finite forbidden set, and every lower bound B, there exist such p and P with p>B, p outside the forbidden set, and sampled automorphism equal to sigma.

**Primary verdict: proved as written.** The new wrapper removes the former need to supply P for the existence conclusion. It uses the exact imported lying-over theorem and combines it with the separately reviewed actual prime and residue-action proofs. No prime ideal, residue compatibility, unramification, or coverage premise is assumed.

Review date: 2026-09-08. This review is independent of the author and inspects all three frozen theorem statements and proofs. No production source or earlier review was changed. The wrapper was not compiled a second time in this review because a separate release auditor is compiling the complete frozen new block. The immediate dependency `CyclotomicPrimeCoverage.lean` was independently compiled in the preceding arithmetic review, including all sixteen transitive axiom checks. A private example of the exact lying-over application also passed before this wrapper existed.

## Frozen target

File: `lean/PaperX/CyclotomicFrobeniusPrimes.lean`.

SHA256: `315bdb71a834a6024fa47e7dc41ebb64954b0279d1df0fea451b662d7c8231fe`.

Preserved prior review: `CYCLOTOMIC_ARITHMETIC_REVIEW.md`, SHA256 `2a26702d77feaa45e6fbda1867fb3c4477e814004222866d48caf6b5b490c521`.

The prior review's statement that the original module did not package P-existence remains historically and literally correct. This separate module now supplies that previously absent production conclusion.

## Theorem-by-theorem audit

1. `exists_prime_above_with_frobenius` takes n != 0, an actual cyclotomic number field K, a rational prime p, and p.Coprime n. It derives maximality of (p) in Z, invokes `Ideal.exists_maximal_ideal_liesOver_of_isIntegral (S := O_K)`, and installs the returned maximality and lying-over proofs as local instances. It then applies the previous module's universal-in-P unramified Frobenius theorem. The output is an existential P together with all five required properties: maximality, lying over (p), ramification index one, decomposition-group membership, and the residue identity for every integral x. There is no residue-degree-one or complete-splitting requirement.

2. `permitted_prime_has_frobenius_witness` takes an actual element of the permitted-prime subtype, extracts its already proved rational primality and conductor coprimality, and applies the first theorem. `primeSample` unfolds to `primePowerAutomorphism`, so the result concerns the same automorphism used by the prime-coverage theorem. The finite forbidden-set condition stays inside the subtype; no different prime is substituted during this step.

3. `exists_arithmetic_frobenius_prime` first obtains p from `exists_prime_with_automorphism`, retaining p>B and sample(p)=sigma. It obtains P above exactly that p from the second theorem. Finally it rewrites decomposition-group membership and the residue formula with the proved equality sample(p)=sigma. The resulting witnesses p and P therefore satisfy all conditions simultaneously. This is not a conjunction of unrelated existence results.

The quantifier order is

    forall finite forbidden, forall sigma, forall B,
      exists permitted p, exists maximal P above p,
        p>B and sample(p)=sigma and e(P/p)=1
        and sigma stabilizes P
        and forall integral x, reduction_P(sigma x)=reduction_P(x)^p.

No global choice of one P for every p is asserted, and none is necessary for this conclusion. The original dependency separately retains the stronger pointwise fact that the same p-power automorphism has the residue property at every maximal P above p.

## Primary source leaf

`Ideal.exists_maximal_ideal_liesOver_of_isIntegral` requires an integral algebra extension, faithful scalar action, and a maximal ideal downstairs. Here O_K is integral over Z by the `NumberField.RingOfIntegers` integral-closure instance; the characteristic-zero inclusion gives the faithful scalar action; and rational primality gives maximality of (p) through `Int.ideal_span_isMaximal_of_prime`.

These are established properties of the actual ring of integers. They are not new hypotheses added to the wrapper. The earlier private probe compiled the same application with only `[Field K] [NumberField K] [Fact p.Prime]`, so cyclotomicity and p.Coprime n are used for the Frobenius and unramification part, not for prime-above existence itself.

## Scope and convention

The residue convention is arithmetic Frobenius, with p-power action. The numerical unramification conclusion is explicitly `Ideal.ramificationIdx P Z = 1`, the standard unramified criterion here. The theorem does not construct a new named generic Frobenius definition or separately prove a general Frobenius uniqueness lemma.

All automorphisms and primes belong to one fixed finite cyclotomic extension over Q. These theorems do not prove coverage in arbitrary finite quotients of the absolute Galois group, general Chebotarev, Hodge–Tate/Weil–Deligne attachment, or the full unrestricted arithmetic Claim 9.1.

## Evidence hashes

| Source | SHA256 |
|---|---|
| Block 25 `lean/PaperX/CyclotomicFrobeniusPrimes.lean` | `315bdb71a834a6024fa47e7dc41ebb64954b0279d1df0fea451b662d7c8231fe` |
| Block 25 `lean/PaperX/CyclotomicPrimeCoverage.lean` | `497cb15ebc4b9c48206bcf1782758ef3f66c0c46c30a2168d6c169a9dcab6273` |
| Block 25 `CYCLOTOMIC_ARITHMETIC_REVIEW.md` | `2a26702d77feaa45e6fbda1867fb3c4477e814004222866d48caf6b5b490c521` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/ArithmeticProbe.lean` | `31bd0ff02da85c81df5aff251378b429a0d8818df1abb793572366376ff2eeee` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/arithmetic_probe.log` | `8e2670df30971d2f9a679d8d71c32394339bdaa724d182fcbcfa2585c0e91b1c` |
| Block 25 `privatechecks/cyclotomic_arithmetic_review/arithmetic_probe.json` | `a1a497c91882c07f95ac7b514839d6d9765ec0cf06d645a45b3292f41192b99b` |
| Mathlib `RingTheory/Ideal/GoingUp.lean` | `6363ce60994dd160c97aa0919d401ab9e1ccac4711d7cb9c4036c84bf622e065` |
| Mathlib `RingTheory/Ideal/Int.lean` | `6a34f6d45487752d5e8ff75755eca667c0720c906b72916b8adbfaf5f5762e85` |
| Mathlib `NumberTheory/NumberField/Basic.lean` | `4e9e600e2aeee2c69f498c2d5d8af2622b03d35a13e4f61dbb5730a88a7eb58b` |
