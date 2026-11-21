# Final-edition integration review

Author: Komorebi P. Edition 1.0. Source revision:
af2d91ead77d06f7903239f1da293e26bb00f240.

Primary verdict: **proved as written**, for the two integration claims below.
Provenance: project self-review. This review does not replace the retained
individual K/L/M/N reviews or claim an independent whole-manuscript audit.

## Claim cards

1. For any characteristic-zero field and any four scalars a,b,u,v, the
   published M and N rules together classify the minimal eventual scalar
   constant-coefficient order of the moments in (E1), with the reduced
   recurrence holding from index one and W0 retained separately.
2. Under the recurrence hypothesis in the certificate lemma, its reversed
   polynomial determines a finite numerator from W0 through Wr; exact cross
   multiplication identifies a proposed GF, and a coprime reduced denominator
   has degree equal to the minimal eventual recurrence order.

## Dependency graph

E1 <- L6/L7 -> K formal functional and transformed determinant -> L uniform
bound and start index -> M boundary / N nonzero classification -> main result.
The source reviews and ASSEMBLY.json pin the four unchanged proof notes.
The new certificate lemma uses formal power-series multiplication and
polynomial divisibility. It supplies exposition for the existing exact
certificate logic, without inferring a recurrence from a finite prefix.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| Domain and normalization | passed | E1 equals the published L6/M/N moment definition; the field remains characteristic zero |
| Parameter coverage | passed | abuv=0 and abuv!=0 are disjoint and exhaustive; M's ordered rows include both zero pairs and all remaining boundary intersections |
| Nonzero normalization | passed | a,u,b,v are units in N's locus, so t=b/a and q=(v/u)^2 are defined and nonzero |
| Coefficient field | passed | M's parameter-polynomial identities stay over the base field; N.7 explicitly descends the minimal annihilator and preserves gcd degrees |
| Initial index | passed | M and N assert the reduced recurrence from one; the new overview makes no stronger assertion at zero |
| Finite-to-infinite implication | passed | A monic order-r recurrence from one kills every coefficient of DG above r |
| GF identification | passed | D(0)=V(0)=1 permits division of the cross multiplication in formal series |
| Minimality lower bound | passed | Every eventual recurrence yields a polynomial multiplier; gcd(U,V)=1 forces V to divide it |
| Order-zero case | passed | A polynomial GF is eventually zero, and the zero-order recurrence gives a constant numerator under the stated start condition |
| Modular witnesses | passed | After clearing denominators, retained degrees and a Bezout identity exclude a nonconstant common rational factor |
| Computational leaves | passed | All six retained replayers passed from source-verified programs; their all-index conclusions still depend on the written proofs |
| Source integrity | passed | All 589 imported TeX expressions preserve their mathematical tokens; ASSEMBLY.json lists two layout corrections |
| External theorem leaves | out of scope | No new external theorem or novelty claim is introduced |
| Independent review / Lean | not addressed | Provenance remains project self-review |

## Proofreading record

- Routine edits: consolidated title, abstract, definitions, local notation guide,
  internal cross-references, reproduction instructions, and current scope.
- Imported mathematical-token changes: none.
- TeX layout correction: K5's equation tag is moved after the closing aligned
  environment. The norm formula and its label are unchanged. The common reader
  renderer also handles the retained source's old tag placement.
- Display layout: the unchanged expansion used to check N6 is promoted from
  inline mathematics to a display so it remains usable on a narrow screen.
- Added mathematics: the explicit recurrence-order definition, restatement E1,
  and the elementary certificate lemma E2 with its proof.
- Validation: deterministic assembly and TeX-conservation checks, six source-
  verified certificate replays, PDF math-error/anchor checks, and visual page
  review. ARTIFACTS.json records the frozen outputs and rendering inputs.
- Coverage: final integration, new exposition, and rendering. The preserved
  source reviews remain the review records for the individual proofs.

No unresolved integration or proofreading issue remains within this scope.
Independent mathematical review, historical novelty, and formalization remain
unassessed. Pointwise quadratic orders and higher families remain open.
