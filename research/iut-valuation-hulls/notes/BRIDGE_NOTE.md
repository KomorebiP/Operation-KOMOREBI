# An algebraic reduct model for an IUT-inspired Komorebi realization bridge

**Checkpoint:** Hodge Reduct B04, 25 October 2026

**Claim type:** Fully proved elementary model and formal obstruction; a proposed interface to IUT. **Not** a formal Hodge theater, theta link, new proof of abc, or proof/disproof of IUT III Corollary 3.12.

## 1. What the source actually says

* IUT I (May 2020), Abstract, Introduction I1 and Definition 6.13, constructs `Theta^(±ell NF)` Hodge theaters from initial theta data, including an elliptic curve over a number field, a prime ell >= 5, and prescribed arithmetic auxiliary data. Its theta links identify *selected prime-strip/Frobenioid information* and are not conventional ring/scheme isomorphisms. The full theta link is **not** an arbitrary bijection of the entire ring carrier.
* IUT II (December 2020), Abstract and Introduction, develops multiradial and coricity properties. The source distinguishes an expression that makes sense within a single spoke from one that can make sense across spoke structures. These distinctions require IUT's genuine arithmetic and anabelian data.
* IUT III, Theorem 3.11, Remark 3.11.1 and Corollary 3.12, culminates in a comparison of a fixed q-pilot measurement and the theta-output holomorphic hull. The pre-existing checked Komorebi Transport Geometry Block 03 makes that boundary explicit as `SourceWitnessTheorem`. No source-specific inhabitant of that theorem has been established in the predecessor or here.
* The later ABC/IUT checkpoint `ABC_Global_IUT_RR5_2026-10-25.zip` supplies an independent numerical-realization and normalization audit. It does not settle the witness step or unrestricted ABC.

## 2. The deliberately smaller mathematical model

Let `S` be a labelled carrier. An arithmetic layer is

    A = (S, 0, 1, plus_A, times_A).

The *multiplicative reduct* is `U(A)=(S,0,1,times_A)`.
A reduct link `L:A->B` here is a bijection of labelled carriers preserving zero, one and multiplication. The formal structure `KTG.HodgeBridge.MultiplicativeLink` asks for an actual inverse and preservation proofs. It **does not assume preservation of addition**.

This is a toy shadow, deliberately stronger in one direction and weaker in another than a true IUT theta link: our link is a function on all field elements, but we remember only the multiplication table. Actual IUT links relate much richer, specific arithmetic data and should not be replaced by this record.

The exact additive obstruction is

    exists x,y: L(x +_A y) != L(x) +_B L(y).

Its absence is equivalent to an additive lift **for this specified bijection**. In the Lean file this is `compatible_iff_no_additive_obstruction`.

### Positive preservation

Define a multiplication-only power word recursively by `pow_A(x,0)=1` and `pow_A(x,n+1)=pow_A(x,n)*x`. Every reduct link preserves it:

    L(pow_A(x,n)) = pow_B(L(x),n).

Since the link is injective and sends one to one,

    pow_A(x,n) = 1  <->  pow_B(L(x),n) = 1.

These statements are proved in `HodgeReduct.lean` without assuming any ring axioms. Thus a nontrivial class of multiplicative invariants *does* survive.

### Exact observational descent criterion

Let `U:X->Y` forget structure and let `F:X->Z` be an observable. With an inhabited output type for values outside `range(U)`, there exists `G:Y->Z` with `F=G o U` **if and only if** `F(x)=F(x')` whenever `U(x)=U(x')`. This familiar fiber-constancy lemma is proved in `factor_iff_constant_on_fibers`. Without fiber constancy, no uniform reconstruction from `Y` is possible. One direction uses the pre-existing Komorebi `FactorsThrough` interface.

It is a *necessary test for strong, exact descent through our reduct*. Multiradiality in IUT is substantially more elaborate and is NOT identified with this simple factorization without further proof.

## 3. Concrete finite arithmetic obstruction

Take the field `F_5`, preserving its usual multiplication, and let `T(0)=0`, `T(x)=x^3` for nonzero `x`. This is inversion on `F_5^*`, and is an involutive multiplicative automorphism of the whole multiplicative monoid, including zero. However

    T(1+1) = T(2) = 3 != 2 = T(1)+T(1).

Pull back ordinary addition by `T`:

    x boxplus y = T^-1(T(x)+T(y)).

This gives a second field addition compatible with the *same multiplication*, because `T` is multiplicative and sends zero and one to themselves. In particular

    1+1=2,       1 boxplus 1=3.

The two **marked** arithmetic layers differ, although they are **isomorphic as abstract fields**. This is not a contradiction: the specified multiplicative identity comparison is not an additive comparison, whereas `T` becomes a field isomorphism after transporting the addition.

In `HodgeFinite.lean`, Lean kernel-checks the involution and multiplicativity, the difference of the two sums, associativity and commutativity of the transported addition, zero and additive inverses, both distributive laws, and existence of inverses for nonzero elements. It also embeds the two layers into an actual `KTG.KTransport` context whose public carrier is the multiplication table. They are `Related` but disagree in the additive observation.

Therefore no total reconstruction procedure that sees **only this fixed multiplication table** can return `1+1` correctly for every admissible marked field layer. Lean proves `no_uniform_additive_reconstruction`, and both intentionally false statements fail elaboration.

This model is about insufficient public data, *not a contradiction in IUT*. Genuine Hodge-theater data may contain enough additional rigidity, marking, Kummer or Frobenioid information to remove the ambiguity.

## 4. A general family and precise cardinality

For any prime `p >= 5` and any integer `k` coprime to `p-1`, set

    sigma_k(0) = 0,
    sigma_k(x) = x^k for x != 0.

The nonzero multiplicative group is cyclic of order `p-1`, so these are exactly the multiplicative-monoid automorphisms of `F_p` (fixing zero and one). Their number is Euler's totient `phi(p-1)`. For each such automorphism define

    x boxplus_k y = sigma_k^-1(sigma_k(x)+sigma_k(y)).

Every pulled-back addition yields a field structure with original multiplication. These are distinct labelled addition laws: if two laws coincide, the composite of their transport maps is a field automorphism of `F_p`, which must be the identity, so the two multiplicative automorphisms coincide.

Conversely, any field addition on this p-element carrier having the same multiplication and designated zero and one gives a prime field. Its unique prime-field isomorphism to the standard `F_p` is multiplicative, hence one of the `sigma_k`, so its addition is one of the pulled-back laws.

**Conclusion:** exactly `phi(p-1)` field addition laws exist on the *fixed labelled multiplication structure* `(F_p, times, 0,1)`. Up to abstract field isomorphism, there is only one. This is an elementary classification, not claimed as a novel theorem.

For the specific inversion map `T(0)=0, T(x)=x^-1` for `x !=0`,

    T(2)=1/2 != 2=T(1)+T(1)   (p>=5),
    1 boxplus 1=1/2.

This proves a non-additive witness for every prime `p>=5` without a computer. The independent Python tests check all field laws arising this way for p=5,7,11,13,17,19, including all additions, associativity and distributivity. They also enumerate every permutation of the full `F_5` carrier that fixes zero and one and verify that precisely two are multiplicative.

## 5. Implication for the genuine IUT/Komorebi junction

The source-level question is **not** whether a theta link preserves ordinary ring addition: it explicitly need not. The question is what carefully reconstructed, *multiradial* information survives, and whether the particular q-pilot-to-output numerical comparison is justified after all allowed indeterminacies and normalizations.

The checked predecessor `KTG.IUT312` already separates:

1. Source-level IPL full poly-isomorphism of prime-strip data.
2. SHE: simultaneous holomorphic expressibility, holding a specified q-pilot fixed.
3. APT: the actual algorithmic construction trace, not necessarily a map of entire regions.
4. Obstruction controls including Ind1/Ind2, Ind3, unit multiples, tensor powers, vertical shifts, log iterates, and the one-sided orientation.
5. Explicit determinant/procession grade normalizations.
6. A missing **source witness preservation** implication giving `QPilotHullContainment`.

Our new algebraic shadow certifies why the first few *reduct-level* kinds of agreement cannot be silently promoted to full arithmetic or numerical agreement. The prior Block 03 Boolean countermodel already makes this abstract logical point at the target typed interface; the new model does so inside two genuinely valid, isomorphic finite field structures and explicitly within `KTG.KTransport`.

This does **not** close a single actual IUT source-instantiation obligation O1-O6. In particular it does not exhibit or exclude an actual IUT witness satisfying Theorem 3.11, nor bound the log-volume loss from actual admissible hulls.

The nearest mathematically decisive next step is to construct, from *the cited source definitions*, a map or multivalued correspondence from theta-link prime-strip data to the **specific measured/hulled output family**, then prove the needed fiber invariance or a controlled one-sided discrepancy. Do not infer that compatibility solely from equivalence of an underlying reduct. The RR5 numerical bridge describes the precise log-volume cofinality and loss budget this subsequent step must satisfy.

## 6. Verification contract

* `lake build -KwarningAsError=true`: all 24 Lean source files, including two new modules and the preserved 22-module predecessor.
* `verify_block03.py --clean`: predecessor contracts and new source files passed its checks.
* `experiments/finite_theaters.py`: exact exhaustive checks for six prime fields.
* Two negative-control files deliberately attempt false equalities; Lean **must** reject them.
* No `sorry`, `admit`, custom axioms, or trusted numerical premises are used in the two new Lean modules.
* The provided PDFs are source references, not mathematical dependencies of the Lean proofs.

**What is proved:** Reduct preservation, exact descent criterion, finite marked-field ambiguity, and failure of additive reconstruction from the stated public data.

**What remains open:** Real IUT Hodge-theater construction in Lean, theta-link-specific multiradiality and coricity, actual determinant/hull witness preservation, and any claim about abc.
