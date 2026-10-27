# Current-run failures and corrections

None of the failures below is counted as a successful proof.

1. Runtime inspection initially tried the optional Python zstandard package,
   which was absent. The already installed zstd/tar executables successfully
   restored the pinned kit from all seven CRC-checked ZIP members.
2. The container session interface was unavailable. Ordinary process execution
   with durable logs was used instead. No later unattended work was promised.
3. The first supplementary compiler invocation used a working root that did
   not contain the test file. Lean rejected that path before elaboration.
   Compiling from the project root fixed it.
4. The consumer prototype used local notations that lost variable scope in a
   variable declaration. Explicit type expressions fixed those errors.
5. A residue-field surjectivity hypothesis used only in the proof needed an
   explicit Lean include directive. Without it, Lean reported an unresolved
   identifier and sorryAx in the failed declaration. This failed output was
   rejected, not treated as certified. Adding the directive fixed the proof.
6. The exact-kernel test required unfolding kernel membership to an equality
   before simplification. The corrected proof passed.

The production sources were not changed to address these release-test issues.
The final evidence is verification.json plus final_claims_check.json. The
consumer development checks initially used the preserved object tree; the final
consumer check was rerun against all the freshly rebuilt, hash-verified objects.
