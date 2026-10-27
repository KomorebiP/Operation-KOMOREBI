# Independent audit: finite translation observers

Normalized claim: for every fixed finite `T ⊂ Z`, every finite family of digit reductions, every integer `d ∉ T`, and every prime `p`, a sufficiently high single-prime perturbation of the diagonal tuple `d` lies in `A_int = R × ∏q Z_q`, is non-diagonal, preserves every stated observation, and passes every stated translated product test. The bounded-window corollary and the declared-separation precision implication are also audited below.

**Primary verdict: proved as written.** There is no missing mathematical implication in Theorem 1, Corollary 2, Proposition 3, or the stated Set-valued fiber construction. Two terminology cautions below delimit the verdict without changing any hypothesis or conclusion.

## Exact input and provenance

- Author file: `abc_work/komorebi_global_rr8/routes/finite_observers/PROOF_NOTE.md`.
- Audited SHA-256: `7b576c241cb97c9724553871de34b5ecd7abc10eebc762fec979674cc85c9cb1`.
- Review type: independent audit by a fresh delegated reviewer, using the raw proof and exact revision, with no desired verdict or suspected gap supplied. A further delegated check independently examined the category variance and fiber interpretation.
- Author file was not edited.
- The local `ROUTE_STATUS.json` labels the written argument proved with independent review pending. That status was treated as a claim to review, not evidence.
- No applicable `AGENTS.md` and no ancestor `.mathbox` ledger were found. No ledger was updated.

## Claim cards

1. **Theorem 1.** Quantifiers are `∀ finite T, ∀ finite digit families, ∀ d ∈ Z\T, ∀ prime p, ∀ sufficiently large integer L`. The conclusion concerns the exact real coordinate, all declared digit values, and every scalar `q`-adic translation norm for `n ∈ T`. Product tests require finitely many norms different from one and no zero norm. The target is failure to distinguish membership in the diagonal image `Z → A_int`.
2. **Corollary 2.** For integer `W ≥ 0`, `T=[-W,W]∩Z`, `d=W+1`, prime `p`, and an integer `L` with `p^L>2W+1`, the one-prime perturbation has the same full norm profile on that window. Larger `L` can additionally exceed any finite digit budget.
3. **Proposition 3.** For `d ∈ Z`, integral local coordinates, prime `p`, and integer `N ≥ 1`, a product test at `n=d+p^N` with a finite nonzero local norm profile implies `x_p-d ∈ p^N Z_p`. The claim is a sufficient precision test at declared displacement `p^N`, not a universal lower bound or an ABC estimate.
4. **Set realization.** The view category is a star with arrows from each observer object to the raw object. The diagram is contravariant and Set-valued. Its protected observer fiber contains both the diagonal tuple and the constructed non-diagonal tuple.

## Dependency graph

All leaves are definitions or elementary facts, with no computational or literature-dependent leaf.

`T finite, d∉T, finite digit precisions`
→ finite maximum `h`
→ choose integer `L>h`
→ unequal-valuation identity at the altered prime
→ equality of every local norm profile
→ elementary integer product formula from unique factorization
→ every stated product test passes.

`x_infty=d` and `x_p=d+p^L ≠ d`
→ tuple lies outside the diagonal image.

`1 ≤ d-n ≤ 2W+1` and `p^L>2W+1`
→ `v_p(d-n)<L`
→ Corollary 2 by the same construction.

`product test at d+p^N` and `|d-(d+p^N)|=p^N`
→ `∏q q^{k_q}=p^N`
→ unique factorization gives `k_p=N`, all other `k_q=0`
→ `x_p-d ∈ p^N Z_p`.

`observer→raw` in the view category
→ `F(raw)→F(observer)` under contravariance
→ correctly typed observer functions
→ common protected fiber containing both tuples.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Finiteness and existence of `h` | Passed | `d∉T` makes every valuation finite; both indexed families are finite; `{0}` handles empty families. |
| Admissible perturbation | Passed | `p^L∈Z_p`, and all coordinates remain in their stated factors. |
| Non-diagonality | Passed | The real coordinate forces any diagonal representative to be `d`; the altered local coordinate differs by nonzero `p^L`. |
| Digit compatibility, including exponent zero | Passed | `L>e` implies equality modulo `p^e`; untouched primes agree identically; modulus `q^0=1` is trivial. |
| All-prime norm equality | Passed | At `p`, unequal valuations give `v_p(d-n+p^L)=v_p(d-n)`; at other primes the coordinates are unchanged. |
| Product defined and equal to one | Passed | For each nonzero integer `d-n`, unique factorization gives finite support and `|d-n|∏q q^{-v_q(d-n)}=1`; equal profiles transfer both properties. |
| Empty translation set | Passed | All translation conclusions are vacuous; the construction remains non-diagonal and matches the finite digits. |
| Bounded-window estimate, including `W=0` | Passed | `d-n` ranges from `1` to `2W+1`; `p^{v_p(d-n)}≤d-n<p^L`. At `W=0`, any integer `L>0` works. |
| Proposition 3 valuation algebra | Passed | Finite nonzero profile makes each `k_q` a finite nonnegative integer with finite support; exact unique factorization forces the stated values. |
| Proposition 3 congruence | Passed | `x_p-d-p^N∈p^N Z_p` and `p^N∈p^N Z_p` imply the claimed congruence. |
| Diagram variance and map targets | Passed | Maps are `A_int→R`, `A_int→[0,∞)`, and `A_int→Z/q^eZ`; the star has no nonidentity composable pairs. |
| Protected fiber claim | Passed | The profile is the image of `d`; the theorem constructs a second inverse image outside the diagonal subsource. |
| Additive obstruction claim | Out of scope | No additive quotient is asserted, and none follows from these nonlinear maps. |
| Optimal observer cost or ABC height control | Out of scope | The note explicitly declines these conclusions; this proof supplies neither. |

## Fresh derivation of the critical step

Fix `n∈T`, and write `d-n=p^a u` in `Z_p` with `u` a unit. Since `L>a`,

`d-n+p^L = p^a(u+p^{L-a})`,

and the factor in parentheses is still a unit. Hence the altered norm is exactly the original norm, not merely close to it. This argument applies separately to every `n∈T` because a single finite maximum bounds all the exponents `a`. The perturbation cannot vanish against any tested `n` because it has valuation `a<∞` there.

For the precision implication, write each nonzero norm as `q^{-k_q}`. Multiplying the product equation by the finite denominator gives `∏q q^{k_q}=p^N`. Distinct prime factors cannot exchange exponents. Thus the changed prime has valuation exactly `N` relative to the translation, which implies valuation at least `N` relative to `d` after adding back `p^N`.

Small boundary witness: with `T={0}`, no nontrivial digit precision, `d=1`, `p=2`, and `L=1`, the tuple with real coordinate `1`, `2`-adic coordinate `3`, and every other coordinate `1` is non-diagonal and has all tested local norms equal to one. This is only a sanity check; the universal result is established by the valuation derivation above.

## Scope and wording cautions

1. **“Finite” counts translations, not scalar norm objects.** Whenever `T` is nonempty, the stated diagram has countably many norm objects, because it includes every prime. This is explicitly declared in the theorem and construction. The phrase “full finite protected profile” should be read in that declared sense. The proved indistinguishability is stronger than indistinguishability for any finite subset of those scalar observers, but the diagram itself is not a finite category.
2. **The membership predicate is the diagonal subsource.** Both raw extensions belong to the ambient set `A_int`. The failed predicate is membership in the explicitly named diagonal source image `Z→A_int`. The last phrase “recover source membership” is imprecise if detached from that preceding qualification.
3. **The exclusion `d∉T` matters.** If a tested translation equals `d`, then the diagonal norm profile is zero at every prime; reproducing that exact profile forces every local coordinate to equal `d`. The note does not assert its counterexample for such `d`.
4. **No restricted-height or adaptive conclusion follows.** The bounded-window witness chooses `d=W+1`, outside the tested window. It does not refute a procedure supplied with a smaller source-height bound and a common-zero test. A fixed finite family and an adaptive family selected using supplied budgets have different quantifiers.
5. **No ABC counterexample or general impossibility result follows.** The constructed tuples are not prescribed-support additive integer triples. The note's explicit disclaimer is correct. Compatibility with an all-translation rigidity theorem is a quantifier observation; that neighboring theorem is not a dependency of any result proved here and is not independently certified by this report.

## Source and computation checks

The proof uses only the unequal-valuation rule and unique factorization. The rational product formula invoked for a nonzero integer is immediately derived from `|m|=∏q q^{v_q(m)}`, so no external theorem or source authentication is required. There is no load-bearing finite computation and no finite search extrapolated to a universal claim.

Commands/checks: `sha256sum` verified the author-file hash before audit; the source and route status were read directly; ancestor instruction and ledger checks were performed. No executable test is needed to establish these elementary exact implications.

## Remaining gap and strongest safe statement

There is no remaining gap for the normalized claims. The strongest safe statement is Theorem 1 with all its stated quantifiers, together with Corollary 2, Proposition 3, and the Set-valued extension consequence. The quantitative ABC budget and adaptive supplied-budget certification remain outside the proof. The cheapest useful next check is editorial: replace the two ambiguous phrases by “finite translation profile” and “membership in the diagonal image”; this is not needed to repair a failed implication.
