# Development and environment failures

No failed attempt below is counted as verification success.

1. The first attempt to use an interactive streaming container session failed
   with StreamingExecNotEnabledContainerError before the command executed. A
   tracked current-turn restoration process was used instead and completed.
2. Four optional direct raw-GitHub source requests failed DNS resolution in the
   container. The offline pinned Mathlib source/cache restored successfully and
   supplied the actual accepted dependency files. Web-tool official documentation
   remained an orientation source, not a substitute dependency.
3. Tagged structure was first registered as a global typeclass instance with an
   uninferable system parameter. It was changed to an explicit instance-reducible
   structure constructor, installed locally for each semantic interpretation.
4. The main translation drafts required explicit tagged carrier annotations,
   dependent Fin.snoc annotations, the pinned tuple lemma conventions, and the
   correct induction-hypothesis arguments. The mathematical binder convention was
   unchanged; failure snapshots and diagnostics are retained.
5. The finite definability proof needed an explicit Formula.Realize call rather
   than an ambiguous BoundedFormula.Realize method elaboration. This was corrected.

Rejected draft compile records:

- `ObservationalMathlibTranslation_01`: exit 1.
- `ObservationalMathlibTranslation_02`: exit 1.
- `StandardObservationConsequences_01`: exit 1.
- `TaggedObservationalLanguage_01`: exit 1.
- `TaggedObservationalLanguage_02`: exit 1.

All accepted new modules subsequently compiled individually and in the recorded
cold audit. The final reference Python audit had no failed mathematical checks.
The guard-erasure, binder mutation, path reversal and stronger-language failures
are intentional negative tests, not bugs silently removed from the test suite.

6. The first packaging helper treated the version suffix `.2` as a filename
   extension and staged `Komorebi_ModelTheory_Normalization_v0.zip`. Its contents
   and cold extracted replay passed, but the filename was wrong. The helper was
   corrected to append `.zip` to the full directory name, this record was added,
   and the exact correctly named final archive was rebuilt and replayed again.
