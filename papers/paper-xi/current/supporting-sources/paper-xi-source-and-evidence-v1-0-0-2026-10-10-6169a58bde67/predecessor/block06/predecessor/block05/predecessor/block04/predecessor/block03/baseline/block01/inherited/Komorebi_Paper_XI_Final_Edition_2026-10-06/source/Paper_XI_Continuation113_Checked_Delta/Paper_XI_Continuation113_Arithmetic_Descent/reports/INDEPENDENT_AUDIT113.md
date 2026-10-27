# Independent audit of the continuation 113 finite algebra

**Normalized claim.** An irreducible complex representation with the specified actual central-character/trace profile admits a unique determinant-one action of a specified finite cyclic group when its order is coprime to the dimension. Two complex scalar extensions of the same abelian quotient, with equal commutators and supplied honest coprime cyclic lifts, admit an equivariant scalar bridge. Actual character-preserving group automorphisms supply these pushout lifts. Combining these constructions with the continuation 112 scalar transport produces an irreducible action of the supplied actual group, containing the original character and covariant with the unchanged packet implementer.

**Primary verdict: proved as written.** This verdict concerns the abstract algebraic statements in the four Lean files listed below, under their explicit hypotheses. The finite examples are separately computationally verified in their stated range. No arithmetic simple-character occurrence, original beta-extension identification, H5 instance, or proof of original Claim 16.2 follows without further input.

This is a fresh subagent review of the raw statements and proofs. The canonical-extension and character-correction arguments were independently reconstructed before reading author reports. The finite models were checked directly from their formulas, with an additional implementation using different coordinates. Neither agreement with the author nor kernel acceptance establishes arithmetic instantiation.

## Exact inputs

Baseline archive: `Paper_XI_Continuation112_Checked_Delta.zip`, SHA-256 `4df3bff07c05985e302d5e9f4104de8f6374c17ca695b1e2e451432572272ae5`, independently recomputed.

| Current source | SHA-256 |
| --- | --- |
| `formalization/PaperXI/CyclicNormalization113.lean` | `607587d94a544d2c4e014d81b21e4c9241d852feddfaa826df57f9715d396ce7` |
| `formalization/PaperXI/CyclicDefect113.lean` | `b6fe373c44ebd8725be1683e7f851da03bcc708c896db2103e02a5a31fbb3a19` |
| `formalization/PaperXI/ActualScalarLift113.lean` | `9dca2abac60d683f19c4b2bd2bd257b8f18e5b5f459cf39df9948de4ccf41ce0` |
| `formalization/PaperXI/EquivariantRepresentation113.lean` | `f1cf8ff3343f2647c0994270f6de5bc3478925a25406ea3a221861807b08b6c9` |
| `scripts/finite_models113.py` | `483d8ed849bd5333681298e951c75cab326b626d614bf1393f420a4c29adc0c8` |
| `evidence/finite/run01/RESULT.json` | `4c7708c7b3376b988a38d73b0be7e7be477dff9a6bfa00dc834dd5674f1d9415` |

The report does not audit the separate arithmetic or literature reports. The new Lean proofs use internal algebraic arguments and inherited formal results, rather than importing the 1999 paper as a new axiom. Raw proofs of the relevant continuation 112 common-profile, determinant-phase, scalar-cochain and transport results were inspected. The full inherited development was not rebuilt or reaudited here.

## Claim cards and dependency graph

| Endpoint | Quantified objects and retained hypotheses | Conclusion and dependency |
| --- | --- | --- |
| `canonical_action_of_actual_profile` | Finite group P; subgroup H; character theta; irreducible complex rho scalar on H and trace-zero outside H; an actual homomorphism Omega from cyclic C to Aut(P); a generator c of positive finite order; its restriction preserves H and theta; gcd(order(c),dim(rho))=1 | A unique determinant-one homomorphism C to GL(V) implementing exactly Omega. Common-profile uniqueness supplies an implementer; Schur, complex roots and Bezout normalize it. |
| `canonical_equivariant_bridge_of_actual_profile` | Two irreducible representations on the same actual finite group with the same scalar/trace profile and actual cyclic action | Constructs both normalized actions and a representation equivalence intertwining them. No target equivalence or normalized action is an input. |
| `exists_equivariant_scalarBridge` | Abelian A; normalized complex-unit cocycles c,d with equal labelled commutators; actual scalar-fixing lifts L,M of the same quotient automorphism beta; beta^n=L^n=M^n=1; a^m=1 for every a; gcd(n,m)=1 | An isomorphism of complex scalar extensions fixing scalars and quotient labels and commuting with the supplied lifts. Equal commutators give an ordinary cochain by continuation 112; an explicit character correction supplies covariance. |
| `actualLift_power_eq_one` | Actual group G, normal D, invariant original theta; exact quotient q with kernel D and normalized section; an actual automorphism alpha covering beta and preserving theta; alpha^n=1 | Derives the honest scalar-pushout lift and its n-th power relation. No phase-period assertion is assumed. |
| `exists_equivariant_actual_action` | Actual G and packet P with exact maps to one abelian A, original invariant characters and normalized sections; irreducible packet rho; full theta/chi-preserving automorphisms alpha,gamma covering beta, both with n-th power one; A exponent dividing m with gcd(n,m)=1; equal labelled scalar commutators; an original implementer U of gamma | Constructs an irreducible representation Xi of the supplied G on the original packet carrier. Xi contains precisely theta on D and U implements alpha for Xi. Uses actual lifts, the corrected cochain, and continuation 112 scalar transport. |

These dependencies are forward implications. The existence of Xi, the cochain, its covariance, the pushout lifts, and the normalized cyclic action are conclusions at their respective endpoints. The arithmetic groups, common quotient identifications, full group automorphisms, original characters and labelled commutator comparison remain genuine inputs.

## Independent reconstruction of the proofs

### Canonical cyclic extension

Let A be any invertible implementer of the full automorphism alpha on an irreducible rho. If alpha^n=1, then A^n commutes with rho, so Schur gives A^n=zI with z nonzero. Over the complex numbers choose c with c^n=z^{-1}. Thus B=cA has B^n=I and implements the same alpha.

Writing d=dim(rho), det(B)^n=1. If gcd(n,d)=1, exponentiation by d is an automorphism of the n-th roots of unity. There is a scalar e with e^n=1 and e^d=det(B)^{-1}. The operator eB is honest of period dividing n and has determinant one. It remains on the original vector space and implements the same full automorphism.

For uniqueness, two implementers differ by a scalar t by Schur. Their order relations give t^n=1 and their determinant-one conditions give t^d=1. Bezout forces t=1. The resulting generator defines a unique action of the specified cyclic group, even if the action on P has a nontrivial kernel. No faithfulness is required.

The finite profile endpoint supplies the initial implementer without assuming it: rho and rho composed with alpha have the same prescribed profile and are irreducible, so the inherited common-profile theorem gives their equivalence. The hypothesis on the automorphism of H ensures that alpha preserves the support in both directions. Finite-dimensionality follows from irreducibility for finite P. The nondegenerate-form endpoint derives the trace-zero condition from the original form.

The positive-order requirement appears where complex n-th roots and a finite cyclic action require it. The auxiliary Bezout statements also allow zero natural arguments; their degenerate coprime cases remain valid. Irreducibility excludes the zero carrier at the Schur uniqueness endpoints.

### Correcting the cochain defect

With the extension convention `(z,a)(w,b)=(zw c(a,b),ab)`, a scalar-fixing lift has the form `(z,a) -> (z lambda(a), beta(a))`. Its multiplication law is

`lambda(ab) = lambda(a) lambda(b) c(beta(a),beta(b))/c(a,b)`.

If `c = delta(s) d`, the discrepancy between the two full lifts is

`r(a) = lambda_L(a) s(beta(a)) / (s(a) lambda_M(a))`.

Substituting the multiplication laws and the cocycle comparison proves that r is a character. The supplied full order relations give norm one for each lift phase. Together with telescoping for `s(beta(a))/s(a)`, this yields `prod_{i=0}^{n-1} r(beta^i(a))=1`.

Define `W(a)=prod_{i=0}^{n-1} r(beta^i(a))^i`. Directly shifting indices gives `W(beta(a))/W(a)=r(a)^n`. Choose an integer u with `n*u=1 mod m` and put `k=W^u`. Every character value r(a) has m-th power one, so `k(beta(a))/k(a)=r(a)`. The corrected cochain `s'=s/k` has unchanged coboundary and satisfies exactly

`lambda_L(a) s'(beta(a)) = s'(a) lambda_M(a)`.

This is the correct orientation for the bridge `(z,a) -> (z s'(a),a)`. The argument needs no finite-generation assumption on A, only the stated exponent bound. It does not assert uniqueness of the corrected cochain: invariant character factors may remain.

Coprimeness cannot be discarded. For A=Z/2, trivial beta, n=2 and the nontrivial character r, the norm is one while every character coboundary is trivial. This boundary was checked explicitly in the independent test.

### Actual lift and the composed representation

For an actual normalized section t, put `lambda_G(g)=theta(g t(q(g))^{-1})`. The supplied invariant theta makes `g -> (lambda_G(g),q(g))` a homomorphism into its scalar extension. An actual character-preserving alpha covering beta gives the section phase

`ell(a)=lambda_G(alpha(t(a)))`.

Decomposing g into its subgroup remainder and section proves `lambda_G(alpha(g))=lambda_G(g) ell(q(g))`. This derives the pushout action. Its n-th power fixes the actual section by alpha^n=1 and fixes every scalar by construction. Those two sets generate the scalar extension, proving honesty on the entire pushout. The proof correctly does not assume that the map from G is surjective onto all complex scalars.

For the final composition, the packet operator identity is `U rho(u(a)) = ell_P(a) rho(u(beta(a))) U`. The new actual representation is `Xi(g)=lambda_G(g) s'(q(g)) rho(u(q(g)))`. Its required covariance is equivalent precisely to `ell_G(a) s'(beta(a))=s'(a) ell_P(a)`, which was derived above. Restriction to D uses t(1)=u(1)=1 and s'(1)=1, giving the literal original theta. Irreducibility follows because every packet operator is a nonzero scalar multiple of an Xi-section operator, so Xi-stable subspaces are rho-stable.

The final endpoint preserves the supplied U. It does not assume or conclude `U^n=1` or `det(U)=1`. If those properties are supplied by the packet contract or the separate canonical-action theorem, preservation is literal because the operator is unchanged. Calling this endpoint a construction of an honest normalized cyclic operator without that separate input would exceed its statement.

## Finite-model audit

### F9/F3 Heisenberg model

The field polynomial u^2+1 is irreducible over F3. The trace pairing in coordinates is `Tr((a+bu)(c+du))=2(ac-bd)`. It is nondegenerate. The group cocycle is one half of `Tr(y x')-Tr(x y')`; bilinearity proves associativity. The operator formula in the script has cross term one half of `Tr(xy)`. Composing the operators produces exactly the group cocycle with the displayed sign, not its inverse.

The delivered script checks all 59,049 group pairs at all nine basis vectors. Its trace support is precisely the three central elements, with values `9 omega^z`. The character norm is `3*9^2/243=1`, so this is irreducible over C. The exact monomial operators are faithful: a trivial shift forces x=0, and nondegeneracy then forces y=0 and z=0.

Frobenius is `(a,b)->(a,-b)`. It fixes three basis vectors and swaps the other six in three transpositions. Its permutation operator S therefore has order two, determinant -1 and trace 3. Since the dimension is nine, -S has order two, determinant one and trace -3. The independent coordinate implementation recovered all of these counts.

The fixed group has order 27. On it, the trace of `(-S)rho(g)` is `-3 omega^z` on the center and zero off the center. The fixed-group irreducible character has values `3 omega^z` on the center and zero elsewhere, giving sign -1 in this model. The arithmetic diagonal central-character warning in the script is consistent with `Tr_F9/F3(z)=2z`; the finite calculation itself does not prove an arithmetic group embedding or identify an arithmetic beta-extension.

### D8 and Q8

For coordinates r^a s^b, the script implements `s r = r^{-1}s`; it uses s^2=1 for D8 and s^2=r^2 for Q8. The prescribed quotient automorphism cycles the three nonzero vectors of F2^2. Both groups have the same nondegenerate alternating commutator form.

An automorphism must preserve squares into the retained center. D8 has square exponents `(1,0,0)` on the three nonzero quotient vectors, so their three-cycle cannot lift. Q8 has `(1,1,1)`, and the choices `i -> +/-j`, `j -> +/-k` give exactly four lifts, all of order three. A separate quaternion multiplication-table implementation checked these four maps and their orders.

The original enumeration covers every identity-fixing permutation of each eight-element group, 7!=5,040 candidates per group. It tests each candidate on every multiplication pair. It is exhaustive for this single prescribed quotient action on these two groups, not for arbitrary dyadic groups.

This establishes why a quotient symplectic action is insufficient. A complex scalar bridge can forget the retained finite square map. The new Lean theorems correctly require full lifts or actual full group automorphisms, and do not claim to manufacture the impossible D8 lift.

## Obligation matrix

| Obligation | Status | Reason |
| --- | --- | --- |
| Full-action implementation and scalar normalization | Passed | Direct Schur/root/Bezout derivation; same carrier and same automorphism retained |
| Character defect, norm and correction signs | Passed | Independently recomputed with the stated cocycle convention |
| Derived pushout lift and its honest order | Passed | Section decomposition plus fixed scalars; no unjustified surjectivity |
| Final original-character restriction and unchanged-U covariance | Passed | Exact operator substitution and inherited irreducibility argument |
| Coprime and degenerate cases | Passed | Conditions sufficient; noncoprime counterexample confirms the boundary |
| F9/F3 representation and fixed trace | Passed in stated finite range | Exact formulas and independent coordinate checks |
| D8/Q8 exhaustive lift count | Passed in stated finite range | Exhaustive enumeration plus independent square-map/quaternion argument |
| Arithmetic realization of the prescribed common quotient and theta | Not addressed | No such input is constructed by these four abstract files |
| Identification with the original arithmetic kappa | Not addressed | Its full action/normalization must still be attached |
| Original H5 and Claim 16.2 | Not addressed | Neither a witness nor a new characterizing family is supplied |

## Verification and failure record

Reproduction command: `python3 evidence/independent/independent_check113.py`, run from this project or using its full path. The script records source hashes, checks that they remain unchanged, replays the delivered finite code and compares the parsed result exactly, runs separate finite-coordinate checks, and builds fresh objects for the four new Lean sources in the audit's own directory. It then runs leanchecker against each new module. The inherited continuation 112 objects are copied and hash-recorded, not rebuilt.

The first audit replay failed before checking a proof: Lean selected the new empty PaperXI object directory as the package root and did not fall through to another LEAN_PATH entry for an inherited module. The failure is retained as `attempt01_namespace_resolution_failure.log` and `attempt01_failure.json`. The harness was corrected by materializing the inherited object tree alongside the new objects. This was a verifier setup failure, not a mathematical counterexample.

The definitive machine receipt is `evidence/independent/RESULT.json`; compilation and kernel-check output are stored beside it. All four source compilations and all four leanchecker runs passed. A further independent check of nine critical endpoints passed with exactly the allowed axioms `Classical.choice`, `Quot.sound` and `propext`; its receipt is `evidence/independent/AXIOMS_RESULT.json`. The 280 inherited object files were hash-recorded and reused. The report's mathematical verdict is restricted to the pinned sources and the precise hypotheses above.

Conservative mathematical proofreading covered this report in full. One phrase about the complex-valued fixed-group character was replaced by its explicit already-stated formula. No source theorem or proof was edited, and no unresolved notation or cross-reference issue was found in the report.

## Remaining gap and strongest safe statement

The new work genuinely eliminates separate finite-algebra existence assumptions: an initial cyclic implementer can be obtained from an actual finite profile, normalized canonically, and an ordinary scalar comparison can be made equivariant. The actual-group adapter and final transport endpoint connect those results without replacing the original theta or packet operator.

The smallest missing arithmetic implication is an actual compatible instance: the prescribed packet and prescribed simple-character data must admit the common exact quotient maps, labelled commutator equality and compatible full automorphisms required here. One must then attach the original arithmetic extension/action and prove the unchanged H5 comparison. The abstract existence of Xi for supplied compatible groups is not a construction of those groups or of their arithmetic occurrence.

The cheapest meaningful next check is therefore a single fully specified arithmetic instance with those literal maps and characters, followed by a comparison of its original kappa action with the constructed canonical action. Repeating the finite tests cannot settle that implication. Original Paper XI remains at 65/66 on the evidence reviewed here.
