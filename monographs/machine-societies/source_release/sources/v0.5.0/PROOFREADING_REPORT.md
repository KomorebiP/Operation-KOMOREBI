# Proofreading and validation report — v0.5.0

**Machine Societies: A Theory of Persistent Plural Computational Organization**  
**Komorebi P. · Manuscript dated 7 October 2026 · 64 pages**

## Review scope

This is an in-session authoring and revision review, not independent peer review. The eight requested additions have been integrated into the theoretical manuscript. The new definitions, proofs, and counterexamples were reviewed against their stated assumptions. The retained source was checked for integration, notation, references, and layout, and its finite regression suite was rerun. This is not a fresh independent proof audit of every retained theorem.

The manuscript contains no results from the author's agent experiments. The exact checks described below are companion checks of finite mathematical constructions, kept in the source package rather than presented as empirical society evidence.

## Recorded outcome

| Item | Result |
|---|---|
| Reading edition | 64 PDF pages, including cover, contents, appendices, and references |
| Prose proofs | 41 theorem/proposition statements: 6 theorems and 35 propositions |
| New proved statements | 12 added relative to v0.4.0; not twelve claims of mathematical priority |
| Other formal material | 6 definitions and 11 counterexamples |
| Figures | 8 programmatic vector figures; 3 added in this edition |
| Bibliography | 40 entries, including 7 additions |
| Exact companion checks | 39 groups and 325,054 assertions passed |
| Final clean LaTeX build | Completed successfully from a deleted build directory |
| Final compiler diagnostics | No LaTeX warnings, overfull/underfull boxes, undefined references, or missing-character diagnostics |
| Source cross-references | No duplicate labels, unresolved references, unresolved bibliography keys, or unused bibliography entries |
| PDF geometry and text | All pages rendered; no words outside page bounds, unresolved `??`, or replacement-character markers detected |
| Visual review | All pages inspected through contact sheets; selected figures, mathematical pages, cover, and final bibliography inspected at full-page scale |
| Computation record | Code, extension module, manuscript, and result hashes checked against the recorded legacy v1 manifest |
| Extracted-source rebuild | Shipped source and figures rebuilt in a clean extraction; 64 pages and identical extracted PDF text; exact checks reran successfully |
| Predecessor | Original v0.4.0 source and delivered files preserved; SHA-256 lineage recorded |

The Python checks use integers and `fractions.Fraction`, not floating-point tolerances or random sampling. Their exact domains are recorded individually in `validation/finite_checks.json` and `validation/computation_manifest.json`. The 28 inherited groups contribute 173,231 assertions. The 11 new groups contribute 151,823 assertions. Counts describe the implementation's finite assertions, not independent scientific observations.

## Substantive corrections and distinctions

**1. Membership does not identify independent control.** The boundary model separates executing copies, credentials, members, voting positions, and effective decision centers. Weight conservation preserves approval for coalitions of the stipulated controllers, not for every subset of newly created identities. An admission-induced majority example is conditional on the admission actually being authorized.

**2. Overlapping rosters are not intersecting quorums.** The reconfiguration lemma uses intersection of every relevant certificate quorum and a cross-epoch constraint against conflicting witness endorsements. A shared member in two rosters does not suffice. The result is not presented as a complete asynchronous consensus or fault-tolerance theorem.

**3. Translation must preserve social acts.** The language contract includes definedness, transitions, and event records. It applies to the translated conversations, not arbitrary messages in the target language, and it does not grant access to hidden information needed by a context-dependent translator.

**4. Confluence requires both hypotheses and a declared state.** The amendment theorem explicitly assumes termination and local confluence. The proof uses well-founded induction. Equal final policy text is weaker than confluence of states that also record resource transfers and procedural harms. Literal append-only histories require a justified semantic quotient before commuting orders are identified.

**5. Finite verification is separated from undecidability.** The unbounded-program extension is explicitly marked as leaving the finite model. Its safety result follows by a written halting reduction. Neither the finite tests nor a finite prefix establishes undecidability or unlimited safety. The proof does not rule out finite-state checking, restricted languages, or sound but incomplete certificate systems.

**6. A finite agenda closure is not open-ended culture.** Monotonicity, positive prerequisites, and finite record universes are stated. Sequential convergence requires a fair schedule; retaining a question without ever allocating resources to it does not satisfy that assumption. Replacing hard questions with easy ones is separated from increased ability on a preserved contract.

**7. A compatible state is weaker than a complete reference frame.** Identity holonomy is the condition for exact group frames. A particular shared state needs only a holonomy-fixed point. The permutation counterexample exposes the difference, and the free-action assumption is named where it closes that gap. The quantitative bound requires a bi-invariant metric, counts repeated traversals, and does not certify authorization of repairs.

**8. Everyone knowing is not common knowledge.** Common knowledge uses reachability in the union of indistinguishability relations. The public-announcement example is restricted to stable propositional facts and an ideal public event. A stored record or finite acknowledgments do not automatically implement that event. New members require new knowledge relations and cannot inherit a common-knowledge certificate by name alone.

**9. Epistemic and operational transport have separate obligations.** Bounded morphisms preserve matched atomic, individual-knowledge, and common-knowledge formulas. Operational preservation requires the language contract as an additional premise. Neither certificate establishes truthfulness, consent, moral legitimacy, or all other semantic dimensions.

**10. Founding authorization is not self-generated legitimacy.** The factorization criterion concerns an externally stipulated authorization label and the information retained in records. Existence of a record classifier is not automatically computability or efficiency. Internal procedural consistency, historical authorization, and moral justification are not conflated.

## Presentation corrections

The abstract, contribution map, reading routes, running commons, open problems, and conclusion were rewritten to connect the additions to the main argument. Stable labels were added to three previously unlabelled retained items so the theorem index can cite them accurately. An initial index draft mistakenly treated those unlabelled retained items as additions; title-based predecessor matching corrected this before release. Mathematical statement counts and source labels now agree.

The first successful layout used a third bibliography page for three entries. Reduced inter-entry spacing, without reducing bibliography font size, brought the final references onto two pages and reduced the reading PDF from 65 to 64 pages. No mathematical text was removed to achieve this. A control-character scan also caught a backslash escape in an intermediate README PowerShell example; the literal command was corrected before packaging. All three new diagrams were regenerated and inspected for clipping and label overlap.

## Exact-check scope

New finite tests cover controller-weight refinements, all witness/quorum pairs on four witnesses, context-dependent translations on three states, every order-respecting five-state directed acyclic graph, noncommutative S3 triangles and frame assignments, holonomy error bounds, four-world knowledge models, small bounded morphisms, positive agenda rules, and founding-record factorizations. Negative controls test the failure of weaker assumptions.

These tests are authored alongside the proofs. They are not Lean verification, an independent replication, or evidence that an actual machine population instantiates the framework. The undecidability theorem is deliberately not described as computationally validated over all programs.

## References and retrieval limits

All seven new bibliography entries received targeted checking through author, publisher, or institutional-repository sources. The retained Halpern–Moses source was also checked. Review depth differs by source and is recorded in `validation/reference_review.md`. In particular, the original Newman full text was not retrieved; its bibliographic record was checked, and the manuscript supplies the standard proof directly. The other inherited bibliography entries were checked for internal consistency, not all independently refetched.

Some broad searches returned irrelevant results. Several direct DOI fetches and a FIPA specification retrieval failed. These were not counted as evidence; accessible primary alternatives were used where available. A previously suggested 2026 cultural-evolution reference could not be independently identified and was excluded, rather than filled in from an unsupported citation marker. POET provides an identified precedent for problem–solution coevolution without importing experimental performance claims.

## Reproducibility limits and remaining work

The computation manifest uses the inherited **legacy v1** schema. The package validator checks its required evidence fields and additionally verifies pinned input and output hashes. The record does not provide a Git revision, machine-checkable resource-limit enforcement, or independent attestation. Python version, environment, elapsed execution time, finite domains, and hash provenance are recorded. The tiny CPU-only run was submitted with a 45-second tool timeout; no separate memory or CPU-affinity cap was imposed.

The Bash build was executed. The supplied PowerShell equivalent was inspected but not run on Windows. All fonts used in the PDF are embedded; no separate font files are packaged. The PDF has not been certified as tagged-accessible or PDF/A.

The manuscript remains a publication-style theoretical draft. Independent peer review, a formal-kernel proof build, a comprehensive priority search, and target-venue editorial review have not occurred. Normative legitimacy, open-ended societal formation, and real-world implementation are not claimed settled by these conditional results.
