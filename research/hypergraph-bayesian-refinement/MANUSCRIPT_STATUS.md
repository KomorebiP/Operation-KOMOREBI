# Manuscript status

## Identity

| Field | Value |
|---|---|
| Title | **Hypergraph Lumpability and Bayesian Refinement for Dynamical Systems with Projector Resolutions** |
| Subtitle | **Exact Interaction Quotients, Filtering Cocycles, and Certified Coarse Models** |
| Author | **Komorebi P.** |
| Release | **0.1.4** |
| Manuscript length | **52 pages** |

## Freeze state

```text
internal_complete: true
submission_ready: false
external_proof_review: pending
literature_priority_review: pending
major_new_section_required: false
ready_to_begin_paper_2: true
```

The manuscript is complete at the internal project level. It contains the declared definitions, theorem chain, proofs, examples, algorithms, numerical certificates, limitations, open problems, appendices, dependency ledger, references, and reproducibility materials. Work on the next paper can begin without adding another major section here.

Before journal submission, the manuscript still needs an independent proof review and a systematic comparison with work on nonlinear lumping, polynomial differential equivalence, probabilistic bisimulation, Bayesian sufficiency, and related quotient theories.

## Final editorial pass

Version 0.1.4 preserves the completed theorem and proofreading state and adds the final publication figure system.

The certificate generator now produces nine publication visual assets as vector PDF and 600 dpi PNG files. The manuscript places them in seven figure environments. Two paired layouts present the quotient criterion and the hyperedge compression results without expanding the page count unnecessarily.

1. The prose was read from beginning to end and revised for clarity, rhythm, and precision.
2. Ordinary prose now contains no semicolon punctuation.
3. Ordinary prose avoids dash punctuation and word hyphens.
4. Necessary mathematical signs, internal identifiers, commands, proper names, and bibliographic ranges remain intact.
5. The analytic descent proof now handles the constant coefficient explicitly.
6. The proof of existence of a best coarse interaction no longer suggests uniqueness under an arbitrary norm.
7. The polynomial descent proof now identifies the coefficient comparison as a polynomial with values in the coarse space.
8. The rooted tree notation now defines its leaf count.
9. Every theorem, proposition, lemma, and corollary has an explicit proof.
10. The normalization bound, positive likelihood regime, implementation, tests, and generated certificate ledgers agree with one another.
11. The exact evidence theorem now states the required initial aggregation and defines sequence evidence before it is used.
12. The hidden Markov specialization now writes every composition symbol explicitly.
13. The numerical algorithm now distinguishes exact algebraic acceptance from tolerance based approximation.
14. The combined quotient and pruning defect is defined before its bounds are applied.
15. The likelihood oscillation criterion is stated only in the nontrivial coarse setting where necessity holds.
16. The evidence error proof now states the probability vector assumption that supplies the unit norm bound.
17. The quotient diagram and its coefficient labels now match the theorem exactly.

## Mathematical state

The central finite chain is

\[
CA_m^f=A_m^cC^{\times m}
\Rightarrow
CF_f=F_cC
\Rightarrow
C\Phi_t^f=\Phi_t^cC.
\]

It combines with

\[
CL_y^f=s_yL_y^cC
\Rightarrow
C\mathsf B_y^f=\mathsf B_y^cC
\Rightarrow
C\Psi_{1:N}^f=\Psi_{1:N}^cC.
\]

The paper also proves finite bounds for interaction defects, errors in quotient flows, likelihood variation within fibers, posterior error, evidence error, and hyperedge pruning.

## Implemented verification

The deterministic certificate generator records **35 passing checks and 0 failures**. The checks cover the following areas.

1. Exact tensor quotients of orders one, two, and three
2. Annihilation of hidden inputs
3. Recovery in packet coordinates
4. A deliberate negative control that is not lumpable
5. Symmetry inheritance
6. Hidden output annihilation
7. Exact quotient transitivity
8. The interaction defect identity across two levels
9. Intertwining of fine and coarse vector fields
10. Exact nonlinear prediction and Bayesian filtering
11. Evidence preservation
12. Mass and positivity preservation in the finite example
13. Invariance under a global likelihood scale
14. The symmetric normalization perturbation inequality
15. Controlled dynamical and observational perturbation bounds
16. First order perturbation scaling
17. Recursive posterior and evidence certificates
18. Hyperedge energy and residual identities for optimal retention

The independent pytest module contains **8 passing test functions**.

## Build verification

| Check | Result |
|---|---:|
| LaTeX errors | 0 |
| Undefined references | 0 |
| Undefined citations | 0 |
| Overfull boxes | 0 |
| Theorem statements without an explicit proof | 0 |
| Referenced figures missing | 0 |
| Semicolons in ordinary prose | 0 |
| Banned stylistic dash compounds in ordinary prose | 0 |
| Deterministic manuscript audit | 22 passed, 0 failed |

The PDF was rendered page by page and reviewed through a complete contact sheet. The title page, theorem pages, normalization section, numerical ledger, figures, appendices, and bibliography were also checked at full page resolution.

## Claim boundary

This release does not establish any of the following claims.

1. Historical priority for every equivalent quotient formulation
2. Universal optimality or efficient discovery of a packet partition
3. Global existence of nonlinear flows
4. Automatic sparsity or guaranteed compression gains
5. Infinite dimensional Bayesian consistency
6. A general theory of stochastic or memory bearing quotients
7. Empirical superiority of coarse filtering in arbitrary applications

The main externally auditable contribution is the assembled theorem chain connecting interaction descent at every arity, naturality of rooted trees and flows, Bayesian refinement, and certified approximate filtering.
