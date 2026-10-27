# Focused review of the revised Paper XI proofs

**Review date:** 18 October 2026. **Reviewer:** independent completion-obligations subagent, applying `mathbox:proof-audit`. **Primary verdict:** the four corrected passages below are valid in their declared scope. The type-side passage retains its explicitly cited simple-character input. No new mathematical gap was found in these passages after the final symplectic-hypothesis clarification.

## Revision and scope

Reviewed the actual staging file `paperxi_release/publication/source/traditional/Paper_XI_Traditional_Final.tex`, against the preserved baseline under `paperxi_work`. At this review, the staging file SHA-256 is `a579be9790f04c3738f74ec02a1fdc3e1ae82f664cc00fc450535208ea832a23`. The accompanying JSON receipt records exact hashes of the reviewed passages so unrelated subsequent edits need not invalidate this bounded review.

After the mathematical review, two pagination controls were added: `\usepackage{needspace}` and `\Needspace{13\baselineskip}` before the tame-package proposition. At that pagination-only stage, removing exactly those two lines recovered the audited source SHA-256 `e734a38832bf55c143908de92d14002ecd1c7e491f88ce06759a12820fe07bde`. All six reviewed passage hashes are unchanged; only their line locators shifted. That pagination-only stage preserved the mathematical passages exactly.

A later editorial check inspected the introduction’s acknowledgement of the local corrections and the updated edition date command. Reversing exactly those two edits recovers source SHA-256 `978c638c68c295a0861e9341b110c3ccc758a784f89d94652efce29cc886ce9e`. All six reviewed passage hashes remain unchanged. The current fingerprint and locators above include both the pagination and these editorial updates. No further mathematical proof review was required.

This is an independent mathematical check of the specified corrections, not a certificate for the entire manuscript or its external literature. The reviewer did not edit the manuscript, package, catalogue, or claim ledger. The earlier completion-obligations review and the separate HL11 source review retain their own scopes.

| Passage | Current locator | Verdict |
|---|---|---|
| Direct twisted Maschke averaging | `thm:twisted_matrix`, lines 957–983 | Valid for every normalized complex-valued cocycle under the stated hypotheses |
| Type-side scalar-field convention | Section 10, especially the definition immediately before `fact:type_heisenberg` | Well-defined over the prime field, conditional on the retained simple-character input |
| Moving-space phase product | `cor:break_phase`, lines 1783–1797 | Valid with the final explicit hypothesis `g in Sp(V)` and the stated moving-space condition |
| Rank-one conductor and trivial Gauss boundary | `prop:tame_package`, lines 1819–1834 | Correct boundary cases, with the additive character declared nontrivial |

## 1. Direct averaging for the twisted algebra

The stated algebra has basis elements satisfying `u_a u_b = c(a,b) u_(a+b)` for a normalized cocycle with values in the nonzero complex numbers. Thus every `u_a` is a unit. If `W` is a submodule and `P` is any linear projection onto it, each conjugate `u_a P u_a^{-1}` has image in `W` and restricts to its identity. The same is true of their average.

Conjugating the summand indexed by `a` by `u_x` gives the summand indexed by `x+a`: the scalar in `u_x u_a = c(x,a) u_(x+a)` cancels against the inverse scalar. Translation permutes the finite index set. The average therefore commutes with every algebra generator and is an equivariant projection. Its kernel supplies an invariant complement. Applying this to finite-dimensional modules, in particular the regular module, gives semisimplicity.

The preceding coefficient argument correctly reduces the center to the scalar multiples of `u_0` when the commutator pairing is nondegenerate. A finite-dimensional semisimple complex algebra with this center has one matrix factor. Its dimension is `|A|`, giving the asserted matrix size and the square-order conclusion.

No finite-image condition on the chosen cocycle or unproved finite central extension is needed. The trivial-group boundary also works: the average is the original projection and the algebra is the complex numbers.

## 2. Prime-field type-side pairing

The revised passage uses a nontrivial homomorphism from the additive group of `F_p` to `mu_p`. Both groups have order `p`, so the homomorphism is injective and surjective. Every declared commutator value therefore has exactly one preimage. This makes the displayed equation a valid definition of an `F_p`-valued pairing.

The elementary-abelian quotient and its alternating, nondegenerate commutator are retained simple-character inputs, explicitly attributed in `fact:type_heisenberg`. This review does not independently reconstruct that theory. Under those inputs, multiplicativity of the commutator in each variable translates to additivity, hence to `F_p`-bilinearity. Alternation and nondegeneracy translate through the same injective map. Using the identical identification on the Galois side makes the two forms comparable without an undeclared scalar convention.

The prime-field specification is material: a nontrivial additive character of a larger residue field need not be injective. Such a character alone would not uniquely recover a pairing valued in that larger field. The correction also works for `p=2`; the manuscript's separately required quadratic refinements and central-extension lifts are still needed there. This review makes no new claim about the adjacent canonical beta-extension input.

## 3. Product of phases on moving spaces

Normalize the claim as follows. Let `p` be odd, let `V` be the orthogonal direct sum of the finite symplectic break spaces `V_s`, and let `g` be a symplectic automorphism preserving every `V_s`. Set `M = im(g-I)` and `M_s = im(g_s-I)`. Suppose `g|M` has zero fixed space. Then the forms restricted to `M` and `M_s` are nondegenerate, the corresponding restrictions of `g` are fixed point free, and

\[
\Phi_p(g|_M,M)=\prod_s\Phi_p(g_s|_{M_s},M_s).
\]

The proof is complete. The invariant decomposition gives `M` as the orthogonal direct sum of the `M_s`. For a symplectic `g`, the identity

\[
b((g-I)x,y)=b(x,(g^{-1}-I)y)
\]

gives `M^perp = ker(g-I)`. Thus the radical of the form on `M` is `M intersect ker(g-I)`, which is zero by the moving-space hypothesis. Orthogonality then makes every `M_s` nondegenerate. The spaces are invariant under `g`; restriction of `g-I` to each has zero kernel and is invertible in finite dimension. All phase expressions now satisfy `def:odd_phase`, and the determinant and half-dimension factors multiply as in `prop:odd_multiplicativity`.

A zero moving space has determinant one and dimension zero, so contributes one. In particular the identity action now has a defined product, equal to one. No assumption that the order of `g` is prime to `p` has been introduced. The characteristic-two sentence retains the independently supplied breakwise quadratic-refinement setting and follows from the referenced multiplicativity of its normalized Gauss signs.

The final explicit hypothesis `g in Sp(V)` is essential. Merely preserving the summands is insufficient: on the standard symplectic plane over `F_3`, the map `diag(1,-1)` preserves the single packet and is fixed point free on its one-dimensional moving image, but the restricted alternating form is degenerate. This counterexample was reported during review, and the final staging text includes the required qualification.

The neighboring breakwise bridge theorem can use this corrected moving-phase comparison; the correction supplies no new arithmetic realization or additional phase agreement.

## 4. Tame rank one and the trivial residue character

The conductor proposition cited earlier assumes dimension greater than one. The added rank-one sentence now covers the omitted boundary directly. For a tame one-dimensional representation, the Swan conductor is zero, while its inertia-fixed space has dimension one for trivial inertia and zero otherwise. The defining Artin-conductor formula therefore gives zero or one exactly as stated. The local-polynomial formula already specializes correctly to `1-a u` or `1` respectively.

The Gauss phase definition explicitly requires a nontrivial multiplicative character. For the trivial character, the manuscript's declared nontrivial additive character satisfies

\[
\sum_{x\in k^\times}\psi(x)=\sum_{x\in k}\psi(x)-\psi(0)=-1.
\]

Its normalization by the square root of the field size is consequently not a unit-modulus phase. The revised proposition correctly promises a finite Gauss sum for each declared residue character and reserves the unit-modulus normalization for the nontrivial characters. These arguments include the smallest residue fields and the unramified rank-one case. The additive-character convention remains part of the declared data, rather than being inferred from packet coordinates alone.

## Adjacent bounded checks

The revised `cor:gcd_lcm_count` correctly distinguishes the number and dimension of induced Mackey packets from the inertia orbit length of an interaction character. Each summand has the indicated induced carrier dimension even when it splits further. The revised scalar-holonomy proposition explicitly assumes scalar based holonomies for both systems; with this qualification and chosen edge representatives, the loop ratios have the asserted vertex-rescaling invariance and multiply under loop concatenation. Neither correction expands the arithmetic conclusion.

## Remaining obligations and source status

The unrestricted arithmetic realization claim, full-character occurrence for the fixed candidate, the separately declared native marking, and H5 for that same candidate remain distinct obligations. These local repairs do not discharge them. The terminal `ActualMonomialLocalGlobal` module retains its actual tame conductor/polynomial/unramified-base-change scope; it does not construct an automorphic representation.

The separate HL11 review now includes direct visual verification of the selected published formulas and normalization clauses. That closes the selected source-access gap, conditional on the preserved arithmetic fixture and its separately cited inputs. It does not promote the restricted self-pair calculation to unrestricted local-factor comparison.
