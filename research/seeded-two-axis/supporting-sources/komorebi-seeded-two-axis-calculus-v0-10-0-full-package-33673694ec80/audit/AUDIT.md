# Mathematical self-review — v0.10.0

## Claim and verdict

For fixed finite G, prime p, rank d, and n>=1, set e=v_p(|G|) and h=max(n+e,2e+1). A representation modulo p^n lifts to a Z_p representation of that same group exactly when it extends to a representation modulo p^h.

**Verdict: proved as written by the supplied argument; authoring-session self-review only.** The quantitative stability input is known in Fournier-Facio's Lemma 7.3. The direct proof in this release makes the bounds and implementation explicit. No independent review or Lean check is claimed.

## Dependency graph

1. Square-zero arithmetic and associativity -> normalized relation cocycle -> H^2 obstruction.
2. Multiplicative defect identity -> averaging with e-digit loss -> quadratic bound 2m-2e.
3. m>2e -> increasing certified depths -> completeness of Z_p -> exact action preserving m-e digits.
4. Finite witness at h -> initial m=h -> constructed lift preserving n.
5. Exact averaging on intertwiners -> conjugacy beyond e digits -> finite class catalogue.

K64's central-sign counterexample uses the retained one-step cyclic obstruction K60 and the elementary central-idempotent splitting of a group algebra. K71 uses that same obstruction only for fixed C_p; its positive Z_p-source lift has a direct convergent-binomial proof.

## Adversarial checks

| Obligation | Outcome |
|---|---|
| Square-zero kernel at n=1, including p=2 | Passed: 2n>=n+1 |
| Left versus right correction and cocycle signs | Passed: expanded explicitly and checked on fixtures |
| Cocycle class independence versus raw residual | Passed: change is delta b |
| Nonexact approximate adjoint action | Passed: proof uses exact matrix associativity, not an assumed action |
| Loss under division by group order | Passed: e digits carried throughout |
| Noncommutative quadratic terms | Passed: exact product and valuation bounds retained |
| Boundary m=2e | Not claimed; recurrence need not improve |
| Preservation of requested seed versus high-precision witness | Passed: C2 example distinguishes them |
| Zero beta sufficient for a lift | Refuted by the central-sign example |
| Exact framed uniqueness | Not claimed; controlled conjugacy is proved instead |
| Fixed finite group versus arbitrary profinite source | Separated by explicit Z_p-source lift |
| Globalization/automorphy implications | Out of scope, not inferred |
| Broad novelty | Not established, not claimed |

## Finite evidence

Five suites passed. Their commands, script hashes, outputs, and wall times are in checks/all_runs.json. The new suite combines normalized cochains, exhaustive listed cyclic matrix lifts, deterministic nonabelian approximate actions, finite-precision averaging, conjugacy, horizon images, and counterexample calculations. It does not prove convergence or classify all groups. The general proofs are separate.

## Changes and failures

The hoped-for sufficiency of one derived-invariant exchange diagnostic was mathematically refuted, not rescued by changing its statement. The strongest replacement is the actual relation obstruction plus finite-group stability. No execution or LaTeX failure occurred in this block. Broad initial source queries were irrelevant and discarded. The first rendered layout left a short contents spill page; appendix subsection entries were hidden from the contents without removing manuscript material, resulting in a 95-page final PDF.

## Open obligations

Continuous lifting with a profinite source and growing images; additional geometric/arithmetic local conditions; detecting those obstructions with an appropriate probe family; independent proof review; Lean formalization. No general finite threshold for these larger problems follows from the fixed-group result.
