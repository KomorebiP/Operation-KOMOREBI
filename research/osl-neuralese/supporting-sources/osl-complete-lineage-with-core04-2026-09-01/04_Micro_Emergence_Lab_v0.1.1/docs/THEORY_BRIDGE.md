# Contextual Quotient and Operator Closure Theory

## Purpose

The lab separates an engineered operator language from evidence that a learned representation discovered reusable operator structure. It does not infer emergence from ordinary accuracy, a linear probe, CKA, or one fitted transition map.

## Observation doctrines

An observation doctrine specifies legal initial states, one-hole contexts, observable outcomes, interventions, provenance fields, effects, and receipts. For compatible programs `p` and `q`,

\[
p\equiv_{\mathfrak D}q
\quad\Longleftrightarrow\quad
\operatorname{Law}(C[p])=\operatorname{Law}(C[q])
\text{ for every }C\in\mathfrak D.
\]

When the context grammar is closed under well-typed substitution, this is a congruence. The quotient

\[
\mathcal Q_{\mathfrak D}=\mathcal P/\!\equiv_{\mathfrak D}
\]

therefore has well-defined composition. Task, causal, audit, and safety doctrines may induce different quotients. Task equivalence must not erase provenance or authorization differences that remain visible to a stronger doctrine.

## Finite minimum-code principle

Suppose a bounded program family has `N` contextual classes and a finite characteristic context set. Any exact code that decodes all characteristic observations must use at least `N` distinct codes. If it uses exactly `N` codes and admits exact composition, its symbolic algebra is isomorphic to the contextual quotient up to symbol renaming.

This is a finite identifiability statement. It does not say that gradient descent finds the minimum code.

## Hard and soft quotients

Let `P_g` be a concrete finite transition matrix, `W` a state-to-symbol membership matrix, and `M_g` a learned symbolic transition. Operator closure is

\[
P_gW\approx WM_g.
\]

Exact closure on every generator implies exact closure on every operator word. With norm-one transitions and primitive residuals `epsilon_g`, the word residual is at most the sum of its primitive residuals.

A constant `W` closes trivially, so closure must be paired with observable reconstruction:

\[
O\approx WD.
\]

The basic optimization target is

\[
L_{\mathrm{obs}}(O,WD)
+\lambda\sum_g\lVert P_gW-WM_g\rVert_F^2
+\beta\,\operatorname{Complexity}(W).
\]

The first term prevents collapse. The second encourages symbolic closure. The third rewards compression. Row-stochastic `W` supplies fuzzy membership, while a one-hot `W` supplies a hard quotient.

## Gauge and identifiability

Operator meaning is tested by relations and causal consequences, not by a preferred neuron basis. Cross-model alignment must be evaluated on reachable and observable semantic subspaces. A valid intertwiner must be nonzero and appropriately full rank, isometric, or invertible on that subspace.

Primary evidence should include held-out relation residuals, multiplication-table recovery up to permutation, arbitrary operator renaming, counterfactual specificity, and causal activation interchange. Coordinate similarity remains secondary.

## Stable symbols versus role binding

The v0.1.0 result suggests a useful distinction between learning stable token-to-operator associations and learning the higher-order operation “bind this episode's name to this demonstrated transition.” Canonical state supervision can strengthen the first while harming arbitrary renaming. The v0.1.1 contrast therefore freezes training volume, architecture, tokenizer, initialization, and optimization budget, then compares correct binding episodes with token-matched episodes whose demonstrated meanings are scrambled. Evaluation uses a disjoint nonce vocabulary and a within-model correct-versus-scrambled calibration intervention. If the correct arm improves only on renamed members while canonical performance collapses, it has learned a narrow workaround. If it reliably beats the scrambled arm on paired correctness and calibration-content use while retaining lexical and compositional behavior, that is evidence for a reusable binding mechanism—but still an induced one.

## Evidence ladder

| Level | Requirement |
|---|---|
| E0 | Operator labels are decodable |
| E1 | Structure survives lexical and frozen-random controls |
| E2 | Equivalent execution paths share a reusable representation |
| E3 | Unseen compositions and episodic renaming work |
| E4 | Internal interventions produce the complete predicted counterfactual |
| E5 | A discovered operator passes independent synthesis and admission checks |

Only answer-only training that reaches E3 and E4 supports a strong spontaneous-emergence interpretation. Success requiring state, trace, equivalence, or law supervision supports engineered symbolic induction.

This table is the forward research ladder, not a list of claims implemented by v0.1. The current package provides majority and TF-IDF controls plus behavioral input counterfactuals. It does not provide a frozen-random neural control, activation interchange, targeted hidden-state ablation or rescue, or an independent operator-admission registry; consequently it cannot establish E4 or E5 by itself.

## Claim boundary

Successful finite experiments can establish an approximate operator calculus within the tested doctrine, state space, architecture, and distribution. They cannot establish a universal machine language, architecture-independent emergence, awareness, consciousness, or subjective experience.
