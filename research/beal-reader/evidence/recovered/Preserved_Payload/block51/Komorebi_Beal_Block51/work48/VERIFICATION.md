# Block 48 verification boundaries

The proofs are written arithmetic with named external theorems. Internal
review is separate evidence and is not a formal proof certificate or
external peer review. The eight Lean declarations certify only the exact
local algebra listed in `notes/formal_verification.md`.

| Item | Completed evidence |
|---|---|
| Bad-seven model and sign | Exact finite computation, written uniformization/finite-flat construction, independent source and proof review. |
| Ray characters and prime19 | Full character quotient; bounded fourteen-prime calculation; independent replay of all452 smooth pairs at11 and19. |
| Local inertia at3 and5 | Written scalar-inertia/twist/root-discriminant proof; independent audit; both Liu and an alternative cluster proof verify the subtle3-adic reduction branch. |
| Level lowering at7 | Checked primary theorem statements; independent cyclotomic-restriction and Fontaine–Laffaille review; parent checked the actual Breuil–Diamond hypotheses and GP locators. |
| Complete norm2025 list | All14 ordinary form pages retained; exact Hecke parsing and correlated comparisons; independent complete110/342/812 pair counts at11/19/29. |
| Twisted norm45 | Unique form and a_(2)=-3 read from actual data; independent parser and polynomial calculation; separate written conductor/twist proof. |
| Lean algebra | Eight public theorems compile on the pinned runtime; no sorryAx or added axioms; authoritative successful run `verification/formal_final/`. |

The parent reran provenance validation for `bad7_run`,
`bad7_character_audit_run`, `character_sieve_run`, and `formal_final`.
All four validate against current inputs. The record is
`verification/parent_manifest_validation.json`. Candidate receipts pin
the imported page bytes, scripts and full exact results. Their independent
arithmetic replay is already complete; an additional identical replay was
not needed to establish another claim.

The final cross-route audit is `notes/final_synthesis_audit.md`. It reviews
the logical composition, the type-preserving twist, and the distinction
between representation results and integer-solution exclusions.

The following are deliberately **not** successful mathematical evidence:

- `formal_run` and `formal_verified`: earlier bounded environment failures;
  the final single-thread invocation passed.
- `candidate_failed_sage_export_*.html`: challenge/error responses, not
  Sage exports or Hecke data. No challenge bypass was attempted.
- `computations/candidate_export.m`: unexecuted Magma code, without a
  claimed syntax check or completed higher-level calculation.
- The nonempty norm45 space lookup by itself: its useful conclusion
  comes from the actual eigenvalue and proved twisting comparison.

Conservative self-proofreading covered the report, handoff and new notes.
The substantive scope clarification made during synthesis is explicit:
under the hypothetical solution hypothesis, reducibility iff15|C iff3990|C.
The remaining3990 branch is necessarily reducible, rather than a branch
whose representation status has not yet been determined. No frozen
predecessor proof was changed.

Archive construction verifies the exact predecessor ZIP hash, copies its
bytes unchanged, and checks every newly archived member after writing.
The generated SHA-256 lists authenticate bytes, not mathematical truth.
The Lean runtime and full third-party manuscripts are not bundled.
