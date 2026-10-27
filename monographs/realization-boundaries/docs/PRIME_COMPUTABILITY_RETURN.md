# Native prime computation: checked return

Owner: `/root/reachability`. Parent: checked Lean v0.6.0 archive SHA-256 `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.

Owned production artifact: `RealizationBoundaries/PrimeComputability.lean`.
Source SHA-256: `55bc437c950eafb805b8ad812d00250f268d3f95ad3d42336b30f430ff379511`.

## Exact checked declarations

- `primrec_nat_dvd : PrimrecRel ((· ∣ ·) : ℕ → ℕ → Prop)`.
- `primrec_prime_predicate : PrimrecPred Nat.Prime`.
- `primrec_prime_decide : Primrec (fun n : ℕ => decide n.Prime)`.
- `primrec_prime_count : Primrec (Nat.count Nat.Prime)`.
- `primeIndexRelation_primrec`: the relation `p.Prime ∧ Nat.count Nat.Prime p = n` is primitive recursive.
- `primeIndexRelation_total`: each index has a prime witness.
- `computable_nth_prime : Computable (Nat.nth Nat.Prime)`.
- `computable_primeAt_value : Computable (fun n : ℕ => (primeAt n).val)`.

The last result applies to the actual existing production `primeAt`; it is not a replacement enumeration. The proof derives trial division from primitive recursive remainder, primality from the bounded divisor criterion, prime counting from filtering finite ranges, and native total unbounded search using `Computable.find`. The resulting search is identified with mathematical `Nat.nth` using `Nat.nth_count`. Termination is supplied by infinitude of primes. No claim that an arbitrary Lean definition is computable is used.

## Verification

- `verification/development/PrimeComputability_002.json`: exit 0, warnings as errors, autoImplicit false, exact source hash above.
- `verification/development/PrimeComputability_replay.log`: native kernel replay exit 0.
- `verification/development/PrimeComputability_contract.log`: exact type and axiom checks exit 0.
- Axiom dependencies of `computable_primeAt_value`: only `propext`, `Classical.choice`, `Quot.sound`.
- Preliminary compile 001 failed because a proof function had two binders where the primitive-recursive predicate API expected one pair argument; corrected in 002.

The computability owner was notified directly and may import the module. Add `PrimeComputability` after `PairedPrimes` to the root import/build integration list. This is a reusable native computability dependency for entries 8.1–8.4, not by itself completion of those presentation/oracle contracts.
