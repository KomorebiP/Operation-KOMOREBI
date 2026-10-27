# AVOC v0.28.0 — dimension-typed affine semantics and cost-aware fusion

This release extends the semantic-feedback v0.27 baseline. Its 135 non-audit modules are byte-identical. The parallel v0.26 learned-rewriting branch is not merged. The present block provides a second exact semantic domain; it does not rediscover affine algebra or establish autonomous improvement.

## 1. Exact semantic signatures over any ring

For a ring R and dimensions n,m, `Signature R n m` stores A : Matrix (Fin m) (Fin n) R and b : Fin m -> R. It denotes x -> A*x+b. Zero dimensions are permitted. Theorems do not require R to be a finite field or to be commutative.

Composition is dimension-typed:

    (C,d) after (A,b) = (C*A, C*b+d).

The executable coefficient composition is proved to agree with sequential function evaluation. Identity, associativity and pointwise sum are proved.

The complete semantic equality theorem is

    f = g iff forall x, eval f x = eval g x.

Coefficient equality is a finite decidable test whenever equality in R is decidable. It compares m*(n+1) ring coefficients rather than enumerating the input space.

## 2. A complete n+1-probe theorem

Let e_j be the coordinate basis vectors. Affine maps f,g are equal iff

    f(0)=g(0), and f(e_j)=g(e_j) for all j.

The zero evaluation identifies the offset. Each basis evaluation, after cancellation of that offset, identifies a column. Thus exactly n+1 designated input vectors suffice, including n=0. A mismatch has a witness at zero or at one of the basis vectors.

This is not a finite-sample heuristic for arbitrary functions. The positive library proves that x^2 and x agree at 0 and 1 over GF(5) but disagree at 2. It also proves that dropping the zero test allows identity and the constant-one affine map to agree on the basis while remaining different.

## 3. Typed programs and contextual replacement

`Program Atom n m` has dimension-indexed primitives, identity, sequential composition, and pointwise sum. Composition only exists when output/input dimensions match; sum only exists between identically typed maps.

`run` evaluates the syntax compositionally. `normalize` independently computes its coefficient signature. The theorem

    eval (normalize semantics program) x = run semantics program x

holds for every typed program, every finite syntax depth, and every input.

Consequently, equality of normalized signatures is equivalent to equality of complete behavior. `checkProgram` is an executable sound-and-complete check in this language when coefficient equality is decidable.

Typed one-hole contexts can place a replacement before or after another map or inside either argument of a sum. Equivalence is preserved under every such context. If the replacement has no greater declared additive cost, plugging it into any of those contexts also has no greater cost.

## 4. Dimension-indexed weighted lower certificates

Unlike the previous fixed Bool3 syntax, the new `LowerValid` contract is indexed by dimensions and permits declared primitive weights. Cost is additive under sequencing; pointwise sum adds m scalar additions; identity costs zero in this arithmetic-only tariff.

For a semantic lower function L, the required inequalities are:

    L(primitive_semantics a) <= primitive_cost a
    L(identity n) <= 0
    L(compose g f) <= L(f)+L(g)
    L(add f g) <= L(f)+L(g)+m.

Structural induction proves L(normalize p) <= cost(p) for every typed program p. If a supplied witness attains L at its signature, it is globally minimal against every equivalent finite program in the declared grammar and tariff, with no depth restriction.

This is a CONDITIONAL certificate theorem. This release does not supply a generally tight lower function, a finite closure checker across all dimensions, or a global optimal-factorization library. The supplied zero lower function is valid but generally uninformative beyond zero-cost identity.

## 5. Semantic canonicalization is not cost minimization

For dense affine primitives, the declared eager scalar-operation tariff is

    denseCost(n,m) = m*(2*n+1).

Per output coordinate it charges n multiplications, n accumulations from zero, and one bias addition. Zeros and sparsity are not discounted. Primitive identity in the syntax costs zero because copying/allocation is outside this tariff.

Dense fusion of a typed program is always semantically correct. It is not always cheap. The exact per-call guard retains the original whenever dense fusion has higher declared execution cost.

Normalization is charged separately:

    composeCost(n,m,k) = 2*k*n*m + k*(2*m+1).

This counts forming the k-by-n coefficient product and affine bias. Pointwise sum of two n-to-m coefficient signatures charges m*(n+1). The compile-once lifecycle certificate is

    normalizationCost(p) + calls*denseCost(n,m) <= calls*executionCost(p).

If it holds, the fused replacement preserves behavior and satisfies the declared lifecycle comparison. If it fails, any normalization already performed is still spent work: the read-only analyzer does not refund it or prove the whole exploration economically nondegrading.

## 6. Concrete kernel-checked examples

Over GF(5), take

    A = [[1,2],[0,1],[1,1]], b=[1,0,2]
    C = [[1,0,1],[2,1,0]], d=[0,3].

The 2->3->2 pipeline normalizes to

    [[2,3],[2,0]], offset=[3,0].

Direct evaluation has tariff 29, fused evaluation 10, and coefficient construction 38. Two calls break even at 58; three calls cost 68 after fusion versus 87 unfused. Strict improvement holds iff calls>=3 in this example's tariff.

The 4->1->4 bottleneck has direct tariff 21 but fused tariff 36, with compile tariff 44. It is never worth dense fusion at any nonnegative call count under this model. The cost guard retains it.

These are exact algebra/tariff results, not measured runtime speedups or unrestricted matrix-computation lower bounds.

## 7. Executed interface

The new Lean JSON interpreter fixes R = ZMod 5, accepts canonical residues 0..4, dimensions 0..8, syntax depth 24 and at most 256 AST nodes, and at most 128 supplied input vectors. Deployment counts are capped at one million. The file entrypoint caps input at 4 MiB and batch size at 256.

The decoded result is a typed program. `Compiled` includes the actual parse equality, computed signature, and its all-input semantic correctness proof. Source parsing is not a universal JSON round-trip or OS/file-authenticity theorem.

The CLI returns the coefficient normal form, executions of both the original and normalized forms on requested vectors, and tariff comparisons. It does not install code, update a proof store, run candidate synthesis, or silently reuse the Bool3 global-minimum result.

## 8. Verification and provenance

52 new declarations; 1,499 total; 156 local compilation targets; 75 rejected negative files, including one intentional dimension/type error. All local sources were freshly compiled with warnings as errors against the nine pinned caches. The 1,499-name axiom audit contains only propext, Classical.choice and Quot.sound.

Independent Python validation uses homogeneous augmented matrices for normalization and a separate AST evaluator for execution. It checks 1,137 executed Lean requests, 937 equivalence cases, 185 normalizations, 7,120 input vectors, and 15 rejected malformed requests. Low-dimensional random programs are checked on every input; higher-dimensional programs use finite input samples. Generic Lean proofs, not those samples, establish universal correctness.

See PROOF_BOUNDARY.md, results/v0.28.0/verification_summary.json and REPRODUCE.md.
