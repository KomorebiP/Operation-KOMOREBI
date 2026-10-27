# Development failures and corrections v0.5.0

The predecessor's reports are preserved under provenance/v0.4.0_documents and its historical verification directory. This file records the current block.

## Runtime and execution

The matching compiler and cache were not extracted in the fresh runtime. The seven existing offline archive parts were reconstructed and checksum-verified before use. A requested streaming container execution failed because streaming was unavailable; the synchronous restore succeeded. This was an environment issue, not a mathematical failure.

The first final clean parallel verification attempt was terminated by the enclosing tool's 200-second timeout during Lake build. It produced no current RESULTS.json verdict or recorded process exit. Cgroup memory-pressure counters increased, but there was no observed OOM kill, so memory pressure is a possible contributing factor, not a demonstrated sole cause. Partial evidence is retained under verification/interrupted_parallel_clean.

The verifier was extended with a serial topological target mode. The subsequent complete clean run and wrapper both exited zero. The final raw output, actual argv, timings and process record are retained. Mathematical source assumptions were not changed to address the execution issue.

## API and elaboration repairs

Initial set-coding attempts used deprecated Set.mem_setOf_eq and incorrect names for filter emptiness/complement helpers. They were replaced with the pinned API's Set.mem_ofPred_eq, Filter.empty_mem_iff_bot, neBot_iff and Ultrafilter.compl_notMem_iff. A namespace qualification for cardinal_sInter_mem was corrected. Cardinal.le_def needed explicit carrier arguments.

The initial first-order formula implementation used incorrect field notation for the membership relation formula constructor. It was replaced by the explicit Relations.formula₂ interface with the declared language and symbol. Binder semantic equivalences needed explicit Iff.of_eq and congruence steps. The singleton finite-variable valuation was simplified explicitly. These were elaboration/representation errors, not counterexamples to the intended statements.

In several new files attributes and theorem declarations initially occupied the same line. Lean accepted them, but the existing source inventory parser expected theorem declarations at the start of a line. The attributes were moved to their own preceding lines in the new files, ensuring all 76 added declarations were included in the 173-name audit. No predecessor mathematical source was edited.

Raw compiler attempts are retained in verification. Compiler-generated diagnostics can mention placeholder terms after failed elaboration, but these failed outputs are not active proof files. The final source scan and #print axioms outputs contain no admitted project theorem.

## Mathematical convention found and tested

A naive use of unbounded ZFSet.sInter for filter completeness would be wrong on the empty family. The actual construction uses relative intersection inside the carrier X. A separate theorem proves the unbounded version incompatible with properness at every positive cardinal. This is a detected and excluded definitional failure, not an axiom added to repair the proof.

## Uncompleted mathematical objectives

The concrete membership-formula interpretation is complete. An internal ZFC derivation, arbitrary-model adequacy, and the closed sentence with a regular-uncountable guard remain unproved. No claim was made that compiler success supplies those results.
