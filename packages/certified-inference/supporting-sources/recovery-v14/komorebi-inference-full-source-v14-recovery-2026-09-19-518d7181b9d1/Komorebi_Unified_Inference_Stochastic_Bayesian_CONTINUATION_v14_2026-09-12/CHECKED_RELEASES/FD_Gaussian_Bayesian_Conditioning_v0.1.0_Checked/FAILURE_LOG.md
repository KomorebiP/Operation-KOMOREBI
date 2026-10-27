# Development and execution failures

Failures are retained as development history. Only the final successful clean
checks selected in FINAL_VERIFICATION_RECEIPT.json are accepted as evidence.

## Environment and source paths

An interactive container session request failed with
StreamingExecNotEnabledContainerError. Runtime restoration subsequently completed
through a monitored subprocess during the same turn. The compact runtime's part
hashes and combined archive hash matched. See runtime_restore.log.

The first attempts to check sources used a workspace symlink to the source tree.
Lean rejected the resolved source path as outside the project root. Passing a
relative source argument did not change the symlink's resolved location. Copying
the exact source bytes into a real workspace directory resolved the error. The
proof statements were not weakened to address this failure.

## Lean draft failures

Initial drafts encountered ordinary elaboration and strict-lint errors. These
included unused variables/simp arguments, identity-function syntactic mismatches,
measurability inference requiring an explicit pair type, and matrix-block rewrite
ordering. The final source repairs use explicit typed helper identities and
remove genuinely unused assumptions or tactic arguments. Failed compile logs
and their nonzero return codes remain in audit/.

No failed draft is included among the 51 checked theorem/lemma declarations.
No mathematical counterexample was produced by these errors.

## Outer execution timeout

A clean-rebuild tool call attempted two sequential Gaussian modules. The first
module finished, but the outer tool window ended during the second module before
its driver recorded completion. The incomplete log is retained as
FDGaussianTransport.aborted_outer_timeout.log. It is not evidence of a theorem
failure or a successful check.

The interrupted module was rerun alone and succeeded. All later heavy modules
were checked in individual tool calls. Each Lean process had its own nominal
75-second cap; the outer environment can impose a shorter tool window. The
final clean rebuild has an actual successful receipt for every one of 18 modules.

## Release assembly check

The first receipt assembly script looked up a source-snapshot key by module
name, while the snapshot keys included the .lean extension. It stopped with
KeyError: FDKalmanDefs before producing the receipt. Correcting the key lookup
made the complete source, log, compiled-output, and baseline hash checks pass.
No Lean source changed as a result.

## Verification scope

The retained historical program was not fully recompiled in this turn. Its
archived evidence remains historical. The new claim is backed by the fresh
18-module finite-dimensional rebuild and complete 51-declaration axiom audit.
Hash manifests prove byte consistency, not authenticity against a malicious
replacement of both files and manifests. The pinned toolchain and mathlib cache
remain trusted dependencies.

The initial ZIP naming helper treated the final dotted version component as a
file extension and shortened the focused archive name. It did not alter the
archive contents. The helper was corrected to append `.zip` to the full directory
name, then both archive checksums and packaged manifests were verified again.
