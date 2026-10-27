# SF-DISCOVERY-110: resolution atlas and coupled family

**Author: Komorebi P. · contemporaneous cutoff and assessment: 9 October 2026.**
The authorized extension target was reached. The exact base was the Special Function Discovery 1.0 source archive, Library version 1, SHA256 `ca4debff6f9653b784b849ccc7519fcf2493a7a24e814658a950a936e8513f21`. Its complete bytes are retained in `historical/release_1.0/`. No Git revision or Mathbox ledger is present; exact source revisions are pinned by the audit and computation manifests. This closeout records the 1.1 phase and does not retroactively change earlier checkpoint status.

The live entry point is [README.md](README.md). The target is [research_v11/TARGET_CONTRACT.json](research_v11/TARGET_CONTRACT.json). The previous closeout remains at [historical/release_1.0/CLOSEOUT.md](historical/release_1.0/CLOSEOUT.md).

## Completed claims and decisive evidence

| Claim | Exact scope and conclusion | Proof and review |
|---|---|---|
| CF-GROWTH | Every `(q,r,a,b)` in `(0,1)^4` defines a unique odd entire pair with positive odd coefficients. Both order and lower order are the unique positive root of `(1-q^rho)(1-b^rho)=(ar)^rho`. Both lower/upper types are positive and finite, with Perron-vector proportions. | `research_v11/coupled_growth_proof.md`, Theorems 1–3; separate `coupled_independent_derivation.md`; independent audit §§1–4 |
| CF-REDUCTION | For the normalized pair, `V(z)=A U(Bz)` with nonzero complex A,B iff `q=b` or `qb=ar`. Explicit reductions have contracting scalar scales. | `research_v11/coupled_identifiability.md`, §1 |
| CF-INVERSE | Outside the reduction locus, six ordinary coefficients through degree seven recover the four ordered positive scales exactly. Repeated candidate roots are covered. | `research_v11/coupled_identifiability.md`, §2; exact inverse API and rational checks |
| CF-OPERATOR | On arbitrary analytic inputs, a nonzero autonomous constant linear projection exists only for equal ordered rows and is a multiple of U−V. No invertible constant linear basis decouples the full defining operator. | `research_v11/coupled_structure.md`, S1; this is distinct from solution-specific reduction |
| RA-TAPS | An exact unit-disk Lipschitz certificate and an explicit sufficient large-radius separation bound for the `(1/4,3/4)` weak-tap bank. | `research_v11/resolution_atlas.md`, RA-1–RA-3 |
| RA-PRIMES | Rational disk/derivative envelopes for a removed prime and exact formulas bracketing a negative-depth threshold; separate subtraction-conditioning estimate. | Same, RA-4–RA-8 |
| RA-SIGNED | At delta=10^-12 every nonzero real polynomial through degree four has positive norm; an explicit degree-seven polynomial has rigorously negative norm after bounding the complete positive tail. | Same, RA-9–RA-10 |
| CF-LAB | Exact derivative recurrences, denominator clearing, certified disk tails, and inherited polyphase/tap identities instantiated on the pair. | `evidence/v11/coupled_lab_notes.md`, APIs, three check reports |

The independent report [evidence/v11/independent_math_audit.md](evidence/v11/independent_math_audit.md) gives the verdict **proved as written** after its recorded quantifier correction. It reconstructs proof implications and checks their leaf assumptions. It does not assert formal proof verification or historical priority.

## Route outcomes and corrections

- The proposed characteristic-matrix growth law succeeded. Fixed-width integration and a shifted power comparison prove positive lower type without losing the exponent. A separate polynomial-exponential barrier derivation confirms the result. The positive left eigenvector then fixes both liminf and limsup type proportions.
- Coefficient elimination strengthened the initial family proposal: a factored degree-five invariant identifies the exact component reduction surfaces, and degree-seven coefficients separate the remaining quadratic candidates.
- A zero-scale example in the independent growth derivation invalidates extending the positive-matrix law indiscriminately to boundary systems. The theorem retains strict positivity and contraction. General boundary analysis requires a different graph/support classification.
- The first general detector statement allowed extra killed labels beyond the complete initial segment. That condition did not justify its tail-factor inequality. The corrected statement requires exactly the complete initial segment. The worked set `{1,3,5,7}` already met it, so the displayed certificate did not change.
- One Matplotlib fraction label failed during figure authoring and was repaired. A final portability review removed an unused absolute scratch dependency fallback. The preserved earlier run and later corrected run distinguish these revisions. No failed execution was interpreted as a mathematical counterexample.
- The printed appendices preserve all 512 mathematical expressions from the five source chapters. Final editing clarified recurrence ranges, the positive epsilon domain, the scalar definition used by the standalone guide, appendix navigation, and dated 1.0 verification headings.

## Verification scope

The current finite run is identified by [evidence/v11/release_run_review.json](evidence/v11/release_run_review.json), with its fresh snapshot, full logs, results, manifest and validator outcome. It passes **5,272 exact assertions**, **26 ordinary numerical assertions**, and **13 separate operational guards**, and regenerates 14 figure pairs. The inverse grid covers 256 rational tuples, including 166 generic and 90 reduced cases. Exact tail and sign certificates include their complete analytic remainder bounds.

The preserved 1.0 run remains separate: 19,871 exact and 5,576 numerical assertions. Its scientific modules and mathematical proof sources are unchanged and were not rerun here. Presentation changes and new material have their own manuscript record. All guide pages and all new monograph material receive final visual review. [package_manifest.json](package_manifest.json) pins the final packaged revision and reports final page counts.

There is no open conflicting mathematical review of the stated claims. A finite passing check does not prove a universal theorem. Float plots and high precision values are not interval certificates. Conservative sufficient bounds do not establish optimal measurement complexity.

## Open questions and next discriminating steps

| Open issue | Cheapest useful next step |
|---|---|
| Existence of an ordinary coupled type limit | Analyze the scalar log-radius renewal remainder after extracting the Perron direction; distinguish lattice and nonlattice contraction patterns. No convergence conclusion is currently justified. |
| Stability of the exact inverse near D=0 | Derive local conditioning from the explicit seventh-coefficient separation factors, with a specified bounded parameter/error model. |
| Minimum detecting degree in the delta=10^-12 example | Certify the degree-five and degree-six moment matrices using exact or rigorous interval arithmetic. Current certificates decide only degree ≤4 and a degree-7 witness. |
| Sharper weak-tap crossover | Improve the comparison constants or derive a separate effective transition law. The current R2 is only sufficient. |
| Coupled angular growth and zeros | Start with rigorously controlled complex-disk samples and identify a precise testable asymptotic statement. Real-axis order alone does not settle it. |
| Historical priority | Broaden the primary-source search around multitype pantograph equations and coupled tree recurrences; check exact hypotheses and equations before any priority assertion. |

These are follow-on research directions, not missing dependencies of the completed extension. The current bounded comparison [research_v11/literature_v11.md](research_v11/literature_v11.md) authenticates six primary-source relationships; it leaves priority unresolved. No external paper or OEIS submission was made.
