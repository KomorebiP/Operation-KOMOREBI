# Literature and external-contract check

Date checked: 2026-10-07. This is an attribution and trust-boundary check, not a novelty survey.

The publication reconstructs its mathematical arguments from the delivered AVOC v0.41.0 definitions and proofs. No external paper is substituted for an unchecked implication in the AVOC source.

1. David Blackwell, *Comparison of Experiments*, Proceedings of the Second Berkeley Symposium on Mathematical Statistics and Probability, University of California Press, 1951, pp. 93–102. The original publisher's DOI record (10.1525/9780520411586-009) and Berkeley Digital Collections record https://digicoll.lib.berkeley.edu/record/112749 establish the bibliography and comparison-of-experiments context. Full-text attempts against the Berkeley record and PDF failed HTTP 403. The paper therefore cites Blackwell only for historical context, and supplies the finite garbling-to-decision-rule transport proof itself. It does not claim to have reverified the full 1951 or 1953 characterization theorem.
2. Official *Theorem Proving in Lean 4*, Axioms and Computation, https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/ was opened and read. It explains propext, quotient soundness, classical choice, and the distinction between kernel reduction and compilation. The current documentation is contextual only. AVOC's actual theorem membership, pinned versions and axiom reports are taken from its archived source and receipts.
3. Official *Atomic Commit in SQLite*, https://www.sqlite.org/atomiccommit.html was opened and read, including hardware and fsync assumptions. It supports the source's named external storage contract. It does not establish universal refinement of AVOC's Python/SQLite implementation or certify its behavior under every physical failure.

No broader historical novelty claim is made. Calibration is described by its actual finite cell-envelope construction. It is not renamed Clopper–Pearson and is not asserted to give unrestricted stopping-time coverage. Known finite probability, linear algebra, and dynamic programming arguments are presented as the source's constructions and self-contained proofs.
