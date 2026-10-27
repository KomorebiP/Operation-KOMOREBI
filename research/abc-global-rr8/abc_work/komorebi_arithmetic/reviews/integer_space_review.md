# Independent audit: bounded integer realization

## Normalized claim and verdict

**Primary verdict: proved as written** for the requested local arithmetic claims: finite view functoriality, the canonical bounded reconstruction bijection, the stated stabilization bound, the unrestricted additive correction quotient, the factorial escape construction and strict inclusion, its exact minimal level budget, and eventual recovery of the radical from prime support.

For every integer budget \(B\ge2\), let \(F_N(B)\), \(N\ge3\), be exactly the residue subsets defined at proof-note lines 14–20, with restrictions given by reduction modulo \(N!\). Let \(X_B\) consist of positive integer triples \((a,b,c)\) with \(a+b=c\), \(\gcd(a,b)=1\), and \(\max(a,b,c)\le B\). The principal claim is the canonical bijection

\[
X_B\xrightarrow{\sim}K_B:=\varprojlim_{N\ge3}F_N(B),
\]

natural in increasing \(B\), with \(F_N(B)\cong X_B\) once \(N\ge B+1\). Separately, the additive module \(\mathbb Z^3\) with \(D(a,b,c)=a+b-c\) and permitted corrections \(M\mathbb Z^3\) has obstruction \([D(v)]\in\mathbb Z/M\mathbb Z\). For \(b_N=\sum_{k=1}^{N-1}k!\), the family \(x_N=(1,b_N,b_N+1)\bmod N!\) lies in \(\varprojlim_N\bigcup_BF_N(B)\) but outside \(\bigcup_BK_B\), and its minimum level-\(N\) coordinate budget is exactly \(b_N+1\).

The domains are sets for the bounded construction and \(\mathbb Z\)-modules only for the unrestricted correction calculation. No topology, completion of the bounded source, linear prime-support observable, IUT hypothesis, or radical-dependent height bound is assumed. The optional identification with the separately named Realization Calculus interface and the optional refinement by the other route's diagrams were not source-audited; neither is a dependency of the local claims assessed here.

## Dependency graph

1. **Definitions and elementary arithmetic:** \(N!\mid(N+1)!\); bounded intervals contain at most one representative of a residue when the modulus exceeds the budget; factorials are unbounded; every prime \(p\le N\) divides \(N!\).
2. **Finite view system:** bounded representatives and divisibility imply the restriction maps preserve membership; ordinary modular reduction gives identity and composition. Budget enlargement gives natural subset inclusions.
3. **Bounded reconstruction:** uniqueness at one modulus larger than \(B\), together with coherence, fixes every later bounded lift. Divisibility by all later factorials forces exact additivity; detecting every common prime forces ordinary primitivity.
4. **Stabilization:** \(N\ge B+1\) supplies both a modulus larger than \(2B\) and every possible prime divisor of the positive bounded coordinates.
5. **Correction obstruction:** the homomorphism image \(D(M\mathbb Z^3)=M\mathbb Z\) gives the quotient criterion. This branch does not imply bounded positive solvability.
6. **Escape and strictness:** the factorial recurrence gives coherence; the factorial sum bounds identify the least positive coordinate representatives; their divergence rules out a uniform budget. The nested embeddings put the two sides of (1) in one ambient inverse limit, so the escape point proves strictness.
7. **Radical channel:** positivity and the fixed coordinate bound put every coordinate prime at most \(B\); the finite divisibility observations eventually recover their union exactly.

All load-bearing leaves are elementary internal arguments. There is no load-bearing external theorem or finite computation, and no circular dependency.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Define actual finite sets before asserting global realizability | Passed | Membership requires positive bounded integer representatives; congruence and \(\gcd(a,b,N!)\) are residue-invariant. |
| Restriction maps preserve membership | Passed | The same bounded representatives work at the smaller modulus, and \(\gcd(a,b,(N+1)!)=1\) implies \(\gcd(a,b,N!)=1\). |
| Contravariant variance, composition, and budget naturality | Passed | Reduction runs from a higher level to a lower level; all compatibility squares are literal modular reduction. |
| Canonical map \(X_B\to K_B\) | Passed | Exact additivity and ordinary primitivity imply every finite condition. |
| Surjectivity of reconstruction | Passed | At any \(N_0!>B\), uniqueness fixes all later lifts, so one fixed defect is divisible by unbounded factorials and each putative common prime is detected. |
| Injectivity and inverse identities | Passed | Two bounded triples with the same level-\(N_0\) residue have identical coordinates; coherence recovers earlier levels too. |
| Uniform stabilization at \(N\ge B+1\) | Passed | \((B+1)!>2B\) for \(B\ge2\); \(|a+b-c|\le2B-1\); every possible common prime is at most \(B\). |
| Correct additive obstruction and representative independence | Passed | \(D\) is \(\mathbb Z\)-linear and \(D(M\mathbb Z^3)=M\mathbb Z\); changing a protected lift changes its defect by an element of this image. |
| No bounded-positive/module conflation | Passed | The exhibited correction can leave the positive bounded set, and the note explicitly does not infer bounded solvability from quotient vanishing. |
| Factorial family coherence and admissibility at every finite level | Passed | \(b_{N+1}-b_N=N!\); \((1,b_N,b_N+1)\) is an actual positive primitive additive triple. |
| Factorial bounds and smallest allowed index | Passed | \(b_3=3\), \(b_3+1=4<6\); the stated induction and the \(N\ge4\) inequality establish all later cases. |
| Exact minimum level budget | Passed | The positive representatives \(b_N,b_N+1\) are below \(N!\); no smaller positive representative exists, and the displayed triple attains the lower bound. |
| Strict union/inverse-limit inclusion | Passed | Nested budget subsets give the canonical inclusion; \(b_N+1\to\infty\) excludes the coherent escape family from every fixed-budget inverse limit. |
| No ordinary integer beta realization | Passed | Positive fixed integers eventually fall below \(b_N\); zero has residue zero; negative fixed integers have normalized residues tending to one, while \(b_N/N!\to0\). |
| Radical recovery for fixed budget | Passed | For \(N\ge B\), all prime divisors of the positive coordinates occur among the observed primes; take their union before their product. |
| Compatibility with the named external framework / optional other-route refinement | Out of scope | The raw local proof suffices; those separate sources were not inspected. No requested arithmetic result uses them. |
| ABC or another uniform conductor-height inequality | Out of scope | It is explicitly identified as a remaining global theorem, not claimed as a consequence. |

## Decisive derivations and boundary checks

The inverse-limit quantifier is used correctly. A coherent section supplies a lift at every level, but the proof does not assume these independently chosen lifts agree. Instead, once \(N_0!>B\), every later lift reduces to the same level-\(N_0\) residue and hence equals the unique bounded lift there. Only after this step is it legitimate to say that one fixed integer \(a+b-c\) is divisible by every later factorial. A nonzero fixed integer cannot have this property. If \(p\) divided both fixed positive coordinates, taking \(N\ge\max(N_0,p)\) would contradict that level's finite gcd condition. Earlier residues follow by the section's actual restrictions.

For stabilization, no unproved compactness or limit interchange is needed. A point of \(F_N(B)\) has a bounded positive lift. At \(N\ge B+1\), the defect has absolute value at most \(2B-1<N!\) and is a multiple of \(N!\), so it is zero. Any common prime of the first two coordinates is at most \(B\) and divides \(N!\), so the finite gcd condition excludes it. The unique bounded residue lift makes this an actual bijection with \(X_B\), compatible with all later restrictions.

At the minimum budget \(B=2\), \(X_2=\{(1,1,2)\}\), and the level \(N=3\) already has exactly this residue triple. The conservative bound \(N\ge B+1\) covers this case. Early views are deliberately weaker than exact additivity: \((3,4,1)\) represents a point of \(F_3(4)\), since its defect is \(6\) and \(\gcd(3,4,6)=1\), although it is not an exact additive triple. This does not contradict reconstruction or stabilization. It also demonstrates why quotient vanishing cannot be substituted for a bounded-positive existence statement: the note's first-coordinate correction gives \((-3,4,1)\), which is exact but loses positivity.

For the escape estimate, if \(S_n=\sum_{k=1}^nk!\), then \(S_2=3\le2\cdot2!\), and

\[
S_{n+1}\le2n!+(n+1)!\le2(n+1)!\qquad(n\ge2).
\]

The summand \((N-1)!\) gives the lower bound. At \(N=3\), the last coordinate is \(4<6\). For \(N\ge4\), \(2(N-1)!+1<N!\). Thus the last coordinate's least positive representative is exactly \(b_N+1\), and the displayed primitive additive triple realizes that budget. Both the minimum and its logarithmic bounds follow without sampling. Already \(b_3=3\), \(b_4=9\), and \(b_4-b_3=6\) verify the first coherence step directly from the definition.

The notation in (1) is legitimate under the canonical subset embeddings: every \(K_B\) embeds into the inverse limit of the levelwise unions, and the inclusions are compatible as \(B\) increases. The identification of its left side with all positive primitive additive integer triples is the compatible union of the canonical bijections, not a claim that arbitrary inverse limits commute with unions. The escape point fails the uniform-budget condition directly; its noninteger beta coordinate is an additional verified description.

## Scope, source checks, and commands

The audited file is `abc_work/komorebi_arithmetic/routes/integer_space/PROOF_NOTE.md`, checkpoint `ABC-20261025-RR7`, SHA-256:

`b561875aee81f80bc43d68e3fc8ccf62d7b7c79516081c1ee8936fbb7eafff4e`.

The note records RR6 base archive SHA-256 `026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a`. That is recorded provenance, not an independently authenticated archive input to this audit. No route outcome, other review, or other route proof was read. No applicable `AGENTS.md` or `.mathbox` directory was found at the checked ancestors and local route locations.

The audit read the raw proof, its numbered lines, and the proof-audit skill with the relevant general-logic, category/variance, external-source, and computation checklists. Commands included `sha256sum` and `nl -ba` on the exact proof path. The examples above were checked by displayed elementary arithmetic; no exhaustive finite computation, formal verification, or Lean compilation was run or is claimed. No internet source or named external mathematical theorem was needed.

## Remaining gap and safe conclusion

There is no missing implication in the audited local theorem package. Its strongest safe conclusion is exact recovery of a supplied bounded positive primitive additive source, eventual stabilization, a correctly typed unrestricted correction obstruction, and an explicit failure of exchanging unbounded budget union with inverse limit.

The global quantitative obligation remains exactly the one stated in section 6: for every \(\epsilon>0\), produce a constant independent of the positive primitive triple bounding \(\log c-(1+\epsilon)\log\operatorname{rad}(abc)\). None of the local constructions supplies that estimate. Each finite factorial triple is an ordinary ABC input, but the coherent escape point itself is not an ordinary integer triple, and no fixed or bounded radical is established for the family. No inference about ABC's truth follows from this audit.

The cheapest next check for the local note is unnecessary for correctness; if the optional cross-route/framework identification is to be asserted as independently verified, inspect those exact raw source diagrams and definitions separately. Advancing toward ABC requires a new quantitative argument, not another verification of the reconstruction bijection.

## Review provenance

Independent delegated proof audit, completed 2026-10-25, of the exact hash above. The reviewer received the raw proof scope without a desired verdict and reconstructed the requested claims from their definitions. The proof was not edited. The report is independent of the author's reasoning process and of other review reports; independence is provenance, not an additional mathematical proof.
