# Coupled special functions: formal verification block

## Result

The new `lean/CoupledFormal.lean` contains **29 named theorem declarations**. They have passed Lean compilation with warnings treated as errors, an exact declaration-by-declaration axiom audit, and a separate kernel replay of the compiled module. The recovered 39-theorem projector core was compiled and audited again. The resulting 68 named declarations are not a count of independent discoveries. Several are supporting lemmas, and the earlier core is not counted a second time as new work.

The compiler and cached Mathlib were restored from the five stored compact runtime parts. Assembly matched SHA-256 `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`. Lean remains pinned to 4.34.0-rc2 and Mathlib to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. No network installation or online compiler service was used.

## Mathematical object

Let the four labeled positive real scales be `(q,r,a,b)`. The paired recurrence begins with `u_0=v_0=1`. For n >= 0, its next terms are

\[
u_{n+1}=\frac{\sum_{i=0}^{n}q^{2i+1}r^{2(n-i)+1}u_i v_{n-i}}{2n+3},\qquad
v_{n+1}=\frac{\sum_{i=0}^{n}a^{2i+1}b^{2(n-i)+1}u_i v_{n-i}}{2n+3}.
\]

These are the odd coefficients of the normalized coupled family in Appendix F. The Lean definition constructs the sequence by well-founded recursion. Its existence is not supplied as an axiom or a premise. A separate recurrence contract proves uniqueness among all sequences satisfying the same initial values and equations.

The module proves that every odd coefficient is strictly positive when all scales are positive. If each scale is also at most one, it proves

\[
0<u_n\le 2^{-n},\qquad 0<v_n\le 2^{-n}.
\]

Both complex series are therefore absolutely convergent whenever `norm(z)^2 < 2`. This is the open disk of radius sqrt(2). The same majorant yields an explicit tail estimate. For either coefficient sequence `c_n`, put `rho=norm(z)^2/2`. For every N >= 0,

\[
\left|\sum_{n\ge N}c_nz^{2n+1}\right|
\le \frac{|z|\rho^N}{1-\rho},\qquad |z|^2<2.
\]

The compiled statement uses the reindexed tail `n+N`. It bounds the omitted infinite series. It is not the stronger, whole-plane outer-radius certificate in the research laboratory, and it does not yet identify the sum as a holomorphic solution of the differential equations.

## Exact inverse from coefficients through degree seven

Set `p=qr` and `k=ab`. The formal recurrence is proved to produce the six explicit coefficients `u_1,v_1,u_2,v_2,u_3,v_3` used in Appendix G. In particular,

\[
D=k^2u_2-p^2v_2
=\frac{pkar}{15}(q^2-b^2)(qb-ar).
\]

Within the positive domain, Lean proves `D=0` exactly when `q=b` or `qb=ar`. Away from this union, equality of the six coefficients through degree seven forces equality of all four ordered scales. The conclusion is about the labeled pair, not an unlabeled pair up to permutation.

The proof does not assume the inverse as a black box. It reduces each parameter row to a positive-pair lemma. If `xy=XY` and `p*x+k*y=p*X+k*Y`, subtraction gives

\[
(x-X)(pX-ky)=0.
\]

If `x` and `X` differ, the alternative root relation and the seventh-order observation give

\[
(k^2u-p^2v)(x^2-X^2)=0.
\]

A nonzero defect and positivity then force `x=X`, a contradiction. The second row is treated by the same proved lemma. Positive squares recover the scales themselves, not just their magnitudes.

The theorem is first checked for the explicit jet map, then transported to the recursively constructed infinite sequence. There is no circular assumption that those coefficients already encode the parameters.

## Examples and necessary boundaries

For `(q,r,a,b)=(1/5,2/5,3/5,7/10)`, the checked exact defect is `189/7812500`, which is nonzero. The corresponding recovery corollary is included.

A checked collision shows why the defect hypothesis cannot simply be deleted. The distinct positive tuples `(1/4,1/2,1/4,1/2)` and `(1/2,1/4,1/2,1/4)` have zero defect and equal six-coordinate jets. The theorem does not claim that every point on the exceptional surfaces is non-identifiable in every possible observation model. This example refutes unconditional injectivity of the specified jet map.

## Verification evidence

The five verification stages passed: runtime and nine dependency pins, the inherited finite core, the new source compilation and all 29 axiom reports, kernel replay, and five deliberately failing controls. The only reported logical dependencies are `propext`, `Classical.choice`, and `Quot.sound`. There are no `sorryAx` dependencies or new custom axioms in the production module.

The kernel replay uses `leanchecker` on the newly compiled module. It rechecks the new declarations against the imported environment. It does not replay all of Mathlib from an empty environment, and it is not an external independent proof checker.

Five negative fixtures reject an incorrect worked defect, an incorrect fifth-order coefficient, equality of distinct boundary parameters, positivity without positive scales, and a placeholder proof. The placeholder exists only in the negative-control directory and is required to fail.

A separate standard-library Python regression compares dense ordinary-Taylor coefficient matching with the preserved EGF laboratory over 256 rational parameter tuples. It passes **15,658 exact assertions**. These cover coefficients, parity, positivity, geometric bounds, factorization, exceptional surfaces, tail-index conventions, and finite-grid collisions. They are implementation checks, not universal proofs or additional formal theorem counts.

## What remains

This block does not formalize the entire analytic monograph. The next obligations are to identify the convergent sums with holomorphic germs satisfying the coupled differential equations, prove the termwise differentiation and product identities, and then formalize continuation along the strict contraction radius ladder. The global Perron growth law and the full rescaling equivalence of Appendix G.1 remain outside this block. None has been relabeled as complete.

Appendix G.2 is now checked in its exact coefficient and formal-recurrence form. Its analytic-germ wording still needs the explicit Lean bridge from analytic solutions to that recurrence. Appendix F.1 has checked recurrence, positivity, coefficient bounds, and local absolute convergence, but not its full entire-solution claim.

The three books and their manuscript sources are unchanged. Their evidence pages are historical snapshots. This companion records the newer formal coverage without pretending the books already contained it. The 99 missing prior-run records described by the previous repair report remain missing.

## Reproduction

From the complete package root, with the stored Linux runtime available:

```bash
python tools/verify_coupled_block.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work /tmp/sf-coupled-check
python tools/check_coupled_exact.py --output /tmp/sf-coupled-exact.json
python tools/verify_package.py --strict
```

Use a new external work directory for a clean replay. A command can be divided into `--stage runtime`, `baseline`, `compile`, `kernel`, and `controls` calls when the execution environment limits individual runs. Compile before kernel or controls. Every stage saves its own receipt even on failure. No network access is required. The runtime is Linux x86-64 and can be used in WSL; native Windows execution was not tested.
