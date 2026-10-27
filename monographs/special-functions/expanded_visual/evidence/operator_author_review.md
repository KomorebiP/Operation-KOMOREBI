# Operator contracts: author review

Status: PASS for the three authored chapter blocks, the generator's exact coefficient checks, and native-resolution inspection of all three figures. Final assembled-page review remains an integration step.

Owned source files are `chapters_operators.tex` and `figures_operators.py`. They contain exactly one volume declaration and three lesson calls, O01–O03. All six PDF/PNG references exist. The generated figures use the guide's unchanged Python/Matplotlib style and contain no AI-generated imagery.

## Source-stable execution

The final generation command was:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_operators.py
```

Run from the v0.4 guide root. Exact inputs, output values, tested bounds, software versions, start time, duration, execution-input hashes before/after, and six artifact hashes are recorded in `operator_checks.json`. The successful run takes approximately two seconds. Thread caps are cooperative; no hard memory or CPU limit is imposed for these deterministic bounded checks. No random sampling is used.

The final author source hashes are:

- `figures_operators.py`: `d1528388d07c135a2701154c16bf42ef340b412f86b42377c17a248c1fd51f5b`
- `chapters_operators.tex`: `bd467fbb91c8f6ac9f14259e607db9a8f8b102fd25c77794e65567a192dcd0db`

The embedded version-1 computation manifest was validated with the computation-audit skill's validator. All six output hashes and all three execution-input hashes were checked. Its legacy provenance limitations remain stated; no git revision identifies this scratch artifact.

## O01: transport the operator with factorial normalization

Domain: formal sequences over Q, R, or C. All exact checks use Q. Restricting the domain to a field with invertible factorials is necessary: characteristic zero alone could include the integers, on which factorial normalization is not an automorphism of the same coefficient space.

Define N(a)[n]=a[n]/n! and let H be the stationary causal FIR H(b)[n]=sum_(k=0)^min(K,n) h[k]b[n-k]. Here K and n are nonnegative integers, and negative indices are zero.

The principal direction is a Taylor-coefficient FIR pulled back to counts:

N^(-1) H N(a)[n]
= n! sum_k h[k]a[n-k]/(n-k)!
= sum_k h[k](n)_k a[n-k].

Conversely, the count-space stationary FIR transported to Taylor coordinates is N H N^(-1), whose weights are h[k]/(n)_k for k≤n. The summation excludes k>n, avoiding division by a zero falling factorial.

The two visible stationary FIR rows intentionally apply equal weights in different coordinates, so they do not represent one unchanged operator. Starting with the infinite count stream a[n]=1 and h=(1,-1), stationary count filtering leaves delta_0, with EGF 1. Stationary Taylor filtering gives the ordinary Taylor series (1-z)e^z, with coefficients 1,0,-1/2,-1/3,-1/8,-1/30,… . Pullback to count coordinates gives 1-n. The samples drawn through n=5 and checked through n=11 are prefixes of infinite streams, not finite inputs with flushed tails.

Finite implementation checks: four input families, four finite tap lists, and 24 indices produce 384 tested pairs of conjugation identities, checking both directions. This bounded computation verifies the implementation. The displayed universal identities follow from the coefficient calculation above.

## O02: Bernoulli in the translation variable

The order is fixed at four. The operated variable is the polynomial argument x, not the Bernoulli order and not a Taylor-coefficient index.

B_4(x)=x^4-2x^3+x^2-1/30.

Expanding at x+1 gives x^4+2x^3+x^2-1/30. Subtraction therefore gives the exact polynomial 4x^3. The generator independently expands the complete five coefficient slots over Q and compares them with (0,0,0,4,0). Because the polynomials have degree at most four, this full coefficient equality determines the identity for every real or complex argument; it is not inferred from sampled argument values.

For every integer N≥0, telescope the identities at x=k, k=0,…,N-1:

sum_k k^3 = [B_4(N)-B_4(0)]/4.

The N=0 empty sum agrees with the zero endpoint difference. At N=5, B_4(5)=11999/30 and B_4(0)=-1/30, giving (400)/4=100. The five plotted gaps divided by four are 0,1,8,27,64.

The Bernoulli normalization is the one already used in Paper I and sequence lesson S11; B_1=-1/2. The complete polynomial proof is supplemented by exact sum checks at all 51 integer endpoints N=0,…,50. These checks make no new general Bernoulli theorem or novelty claim.

## O03: the boundary changes the inversion contract

Periodic domain: four stored values repeated with period four, over Q or R. The periodic operator is D_per(x)[n]=x[n]-x[(n-1) mod 4]. If D_per(x)=0, each neighboring value agrees, so the kernel is precisely the constant vectors. Telescoping every periodic output gives sum_n y[n]=0.

Conversely, for any four-vector y with zero sum and any chosen x[0], define x[n]=x[0]+sum_(j=1)^n y[j] for n=1,2,3. Its three forward edges have the requested differences. The final periodic edge also agrees because sum y=0. Thus the image is exactly the zero-sum subspace, and fixing x[0] produces a unique solution. The incompatible example (1,0,0,0) cannot be resolved in this domain.

Causal domain: exactly four stored values, zero at all other input indices. Addition of five affects those four stored values only. Apply the same taps (1,-1), keeping indices 0,…,4. The last index is generated by one explicit zero flush.

- x=(1,3,2,0): periodic output (1,2,-1,-2), causal flushed output (1,2,-1,-2,0).
- x+5=(6,8,7,5): periodic output (1,2,-1,-2), causal flushed output (6,2,-1,-2,-5).

Cumulative summation of a causal full difference stream returns the original zero-extended input. In the examples it also returns zero after the final flushed value. This is recovery of actual difference outputs; it is not a claim that every finitely supported output has a finitely supported causal inverse.

Finite implementation checks enumerate 625 periodic input vectors with components in [-2,2], their three constant shifts -5,0,5, and 1,875 causal inverse checks. Another 625 candidate periodic outputs test the zero-sum solvability condition with x[0]=1/3; exactly 85 are compatible and all reconstruct exactly. The universal kernel/image statements follow from the algebra above.

## Visual inspection and failures

All three final PNGs were opened at native resolution. O01's five coefficient rows and all fraction signs are legible. O02's endpoint fraction box does not overlap its bars. O03's cycle direction, four edge differences, output bars, initial boundary, and flushed tail are clear. Its bar legends say “From x” and “From x + 5,” making explicit that the plotted bars are filtered outputs.

The first render attempt failed in O02 because Matplotlib's math-text parser rejected the shorthand fraction `\frac1{30}`. It was corrected to `\frac{1}{30}` and the complete generator reran successfully. No mathematical check failed. The successful final run writes its completed evidence only after all assertions pass.

The root also inspected a three-figure contact sheet and found the values and layout consistent with the chapter. Final TeX page-level review is separate because the lesson macro resizes the figures and assembles captions.

## Final mathematical proofreading

Scope: the three new chapter blocks, their generator sections, and these notes. The conjugation direction, coefficient domains, nonnegative index conventions, translation variable, period length, finite support, and flush length agree throughout. The figures and captions match the recorded numeric values. The preliminary broad characteristic-zero phrase was narrowed to Q/R/C as requested by both reviewers. No unresolved formula, source-reference, or LaTeX-token issue remains at author review.
