# Revision notes — v0.5.0 to v0.6.0

**Machine Societies: A Theory of Persistent Plural Computational Organization**  
**Komorebi P. · 8 October 2026**

The revision adds the five requested theoretical developments to the main argument. It does not add the author's agent experiments or claim an empirically demonstrated machine society. The atomic four-office commons is retained as a reference realization; its distributed variant is explicitly distinguished rather than silently inheriting the atomic guarantee.

## Integrated additions

**Enforcement, observability, and incentives (Section 18).** Separates access prevention, sanction-based deterrence, and self-enforcing arrangements. Gives an exact single-deviation bounded-sanction discrimination criterion, a false-positive-constrained linear program, a counterexample to separate pairwise monitors for several deviations, and a garbling bound. The enforcer's own incentives and remedy authority remain explicit assumptions.

**Social time and institutional finality (Section 22).** Develops causal event order, quiescent join convergence, invariant-preserving merge conditions, a convergent double-grant counterexample, and an exclusive-service impossibility under unavailable cross-request information. Finality is indexed by admitted continuations and separated from notification and common knowledge.

**Fast interaction and slow institutional dynamics (Section 29).** Adds a finite-block institutional averaging theorem with a path-law coupling bound. A stopping-time counterexample explains why deterministic-time mixing does not validate data-selected review times. A robust deterrence proposition transfers declared observation-model error into an enforcement margin and false-positive bound.

**Rational information cascades (Section 34).** Derives a binary Bayesian model in which action-only records lead to almost-sure locking with positive error. The private-signal tie rule is explicitly distinguished from the random tie-breaking basic example in the cited classical paper. Independent signal disclosure permits a majority consistency bound under a different information contract.

**Adaptive roles and resilient specialization (Section 40).** Models role and network changes as authorized state transitions. Gives an exact bounded-erasure staffing criterion with a complete matching argument. Individual-role backups, joint staffing, feasible reorganization paths, and time-respecting information routes are separated by examples and counterexamples.

## Connecting changes

The abstract, contribution map, reading routes, running example, open problems, integrated commons appendix, and conclusion were revised. The new sections were inserted thematically rather than appended as unrelated essays. The slow-dynamics and enforcement sections share a concrete preservation obligation: an approximate evidence model must carry its error into a sanction certificate.

Four analytical vector figures were added: convergent but invalid grant records, review-epoch averaging bounds, action-only versus signal-preserving error, and a one-erasure-resilient role graph. The eight prior vector figures are retained unchanged.

## Mathematical inventory and preservation

The edition has 50 theorem/proposition statements with 50 prose-proof environments: 8 theorems and 42 propositions. Nine statements are additions; all 41 predecessor statement environments are preserved verbatim. There are 6 definitions, 15 counterexamples, 12 figures, and 50 bibliography entries. The source labels are stable, but section and theorem numbers change with insertion. `THEOREM_INDEX.md` provides the mapping.

The exact suite adds 13 groups and 42,759 assertions to the 39 groups and 325,054 assertions of v0.5. All 52 groups and 367,813 assertions pass in the recorded run. These counts refer to bounded implemented assertions, not independent observations or a general proof.

## Corrections during preparation

The first layout left the glossary and references entries alone on a second contents page. Reducing inter-entry contents spacing from 1.5 pt to 0.5 pt, without changing the contents font size or body font size, placed the complete contents on one page. The final PDF has 79 pages rather than 80. The cascade figure caption was clarified to identify the error of the last action, not an unspecified population statistic. The fixed-contribution convergence caveat and the zero-horizon empty-product convention were stated explicitly.

No mathematical counterexample to a stated new proposition was found in the recorded exact domains. Source-access failures and review limits are recorded separately in `validation/reference_review.md`; successful compilation does not authenticate those sources or establish priority.
