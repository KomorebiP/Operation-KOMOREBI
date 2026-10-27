# AVOC v0.8.0 development failures and repairs

The following failures occurred during development and are intentionally
retained as part of the evidence boundary.

1. **Dependent `Finset.max'` rewrite in the history Bellman induction.**
   Rewriting equal image finsets failed because the nonempty proof argument to
   `max'` depends on the finset being rewritten.  The proof was repaired with
   two explicit `max'_le` / `le_max'` bounds rather than dependent rewriting.

2. **Archive append rewrite under proof-dependent conditioning.**
   Directly rewriting the cumulative likelihood in `conditionByWeight` failed
   because nonnegativity and positive-evidence certificates depend on that
   likelihood.  The proof was replaced by a pointwise algebraic argument using
   the evidence-mass factorization.

3. **History replay predictive-mass simplification.**
   `simp` did not automatically identify the singleton archive evidence mass
   with `predictiveProb`.  A dedicated theorem
   `evidenceMass_single_historyFactor` was introduced and used explicitly.

4. **Dependent prior rewrite in one replay step.**
   Rewriting an equality between the replayed prefix belief and compiled prefix
   belief failed inside the type of the positivity certificate.  Two transport
   lemmas, `conditionByWeight_congr_belief` and
   `conditionByWeight_congr_likelihood`, were introduced instead.

5. **Concrete archive example definitional-equality failures.**
   Singleton archive likelihoods were propositionally but not definitionally
   identical to the named retrospective likelihood functions.  Explicit
   likelihood equalities were proved and passed to the transport lemma.  Two
   unused `simp` arguments were also removed because warnings are treated as
   errors.

6. **Clean-build host timeouts.**
   The host wrapper limits individual execution windows.  The clean rebuild was
   therefore run in six resumable slices.  The first five stopped under the
   declared timeout while preserving Lake's completed build graph; the sixth
   completed normally at 1055/1055 jobs.  No AVOC proof failure occurred in the
   clean rebuild.

No surviving mathematical counterexample to the v0.8 theorem statements was
found.  The restrictions listed in `PROOF_BOUNDARY.md` remain deliberate open
boundaries rather than hidden assumptions.

7. **Self-referential packaging manifest.**
   The first packaging pass included `results/SHA256_CHECK_v0.8.0.log` in the
   hash manifest and then overwrote that same log while checking the manifest,
   producing one checksum mismatch.  The manifest boundary was corrected to
   exclude its own generated check/archive-integrity outputs.  The manifest was
   regenerated, `sha256sum -c` then passed, and the final ZIP integrity test
   reported no errors.
