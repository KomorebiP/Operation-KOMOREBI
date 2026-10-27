# Second-block runtime recovery

The runtime was not present in the fresh working container. All seven supplied offline ZIP parts were assembled with the original starter script. Each part SHA-256 and the combined archive SHA-256 passed. Extraction completed with exit code zero. The cumulative verifier then checked the Lean version, manifest Mathlib revision, and actual pinned repository HEAD before compiling all eleven modules.

The first tool request attempted an unsupported interactive streaming session and did not launch the assembler. A noninteractive process invocation was used instead. The successful recovery log and extraction exit code are in verification/. No runtime proof result is inferred solely from the archive hashes.
