# Runtime recovery record

The seven offline archive parts and their combined compressed archive passed the assembler's SHA-256 checks. The initial combined assembly/extraction command was interrupted by the host command limit. Extraction was then rerun to completion from the verified combined archive. `lean_extract.exit` records exit code zero, and the successful fresh Lean run verifies the recovered runtime version and pinned Mathlib revision.

The nine failed Lean development checks are separately preserved in `verification/development/`. They concern import paths, visibility, notation/elaboration, and warnings or typeclass instances. They are not successful proofs. The final active sources and all six fresh final checks pass without those diagnostics.
