# Block 49 target and ancestry

Original goal: continue toward Beal's conjecture. Active subproblem:
exclude every positive pairwise-coprime solution to A^3+B^5=C^7.
Neither the active subproblem nor full Beal is assumed solved.

Base: Komorebi_Beal_Block48_Arithmetic_Refinement_v4.8.0.zip,
SHA256 bbf78879d4b5714c818dd1521053dcd6b80c0694799b120b440fa850efec091a.
The current saved Block48 report was read before continuation, and the
local archive hash matches. Frozen work48 and earlier releases are not edited.

Inherited written results, with their declared external inputs:
- Residual RM reducibility iff15|C iff3990|C under the solution hypothesis.
- Type-preserving modular attachment conditional on absolute irreducibility.
- Thirteen of fourteen norm2025 forms excluded; l remains with A,C odd,
  418|B and the stated mod11 residues.
- No full proof of signature (3,5,7), and no full Beal proof.

## Executed portfolio and ownership

1. extension: analyze the opposite residual extension after twisting by
   nu_real; test exact ramification and a class-group obstruction.
   Must not assume that changing lattices preserves residual ramification
   or finite flatness.
2. local_types: calculate actual monodromy at3 and5 after the twist.
   Decide whether the full residual extension is ramified, beyond its
   known character semisimplification.
3. last_form: identify or constrain the actual remaining canonical form l
   through inertia/CM/crystalline structure, not further uncorrelated
   divisibility checks or an unproved CM flag.
4. alternative: construct and test a different Frey representation for the
   necessarily reducible branch. Record every new variable conductor prime.
5. parent: pursue complementary global consequences, reconcile results,
   arrange fresh reviews, and preserve a reproducible checkpoint.

Each owner writes uniquely named files under work49. External arithmetic
leaves require exact source hypotheses. Bounded computations require exact
input, range and output provenance. A failed route is not a counterexample
to the conjecture. An unexecuted higher-level modular exporter remains
unexecuted.

Success includes a proved exclusion or necessary condition for an infinite
family, a verified new representation, or a sharp structural obstruction.
Such partial results must not be relabelled as completion of either target.
