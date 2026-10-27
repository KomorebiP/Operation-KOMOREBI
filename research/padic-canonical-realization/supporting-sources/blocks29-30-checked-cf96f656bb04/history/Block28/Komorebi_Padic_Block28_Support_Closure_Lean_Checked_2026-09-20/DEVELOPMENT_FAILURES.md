# Block 28 failed attempts and corrections

1. The first generic support definition lacked a decidability instance for testing
nonzero coefficients over an arbitrary ring. Lean rejected its filter elaboration
and downstream uses. A local classical instance repaired the noncomputable finite
set definition. No test or placeholder axiom was used to discharge a theorem.

2. Warning-as-error found unused typeclass hypotheses and simp arguments. Removing
those hypotheses strengthened the generic interfaces (the alphabet need not be
finite for the purely mathematical theorem). Two doc-comments initially preceded
an omit command instead of its theorem; moving omit before the doc-comment fixed
Lean's declaration syntax.

3. The profile adapter's word proof needed explicit normalization after the
inductive rewrite. The mask initial proof needed the least-support abbreviation
unfolded. The output theorem application initially omitted the already available
mask-constant hypothesis. The corrected proofs retain exactly the intended
statements and all old production modules.

4. The finite matrix constructor's scalar-linearity proof needed RingHom.id
normalization before ring arithmetic. Concrete restriction witnesses additionally
needed kernel reduction of finite/modular numeral propositions after normalization.
Warning-as-error caught redundant tactic sequencing and one unreachable tactic;
these were corrected instead of disabling production warnings. Failed development
logs and the first source drafts are retained under results/ and failures/.

No mathematical counterexample to the stated invariant-coordinate closure or
canonical-output theorem was found. The two production counterexamples refute
stronger orbit-support interpretations that were never used as premises.

The current turn's runtime archive assembly, checksum and extraction succeeded.
The baseline and all final command outcomes are recorded individually. The final
result is based on actual completed commands, not on a retained prior build label.

5. The first cumulative ZIP omitted an inherited Block10 Python bytecode file
because the focused release's cache-exclusion rule was also applied to historical
archive content. Fresh extraction caught the missing file through the explicit
predecessor-preservation check. No theorem or computational assertion failed.
The cumulative writer was corrected to include every historical file listed in its
checksum ledger, while the current focused project still excludes generated caches.
Both releases were resealed and extracted into new empty directories for replay.
The initial failed packaging diagnostic is retained in results/packaging_attempt1.log.
