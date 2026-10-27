# Verification contract

Python standard library only. Bytecode writes are disabled. Run from the extracted
root:

    python -B verify.py --report ../Block71_Replay.json

The report must be outside the immutable package. --integrity-only checks payload
hashes and the pinned source lineage without running scientific jobs.
--replay-predecessor additionally runs the immediate Block70 default verifier in a
clean extraction. It does not request the full older historical chain.

The default verifier checks the exact manifest file set, every payload hash,
the original predecessor bytes, and eleven named source members with their copied
contents across18 archive levels (the outer archive included). It then copies the
package to clean scratch, deletes both expected scientific JSONs, runs the primary
and separate programs, and compares the COMPLETE regenerated JSON contents.

Each command's argv, runtime, output and exit code are recorded. Timeouts and
nonzero exits are failures/inconclusive execution, never mathematical exclusions.
Declared negative controls alter a named unit class, the RM comparison matrices,
a Fermat quotient, the accepted classification count, a claimed eight-pattern
exclusion, a Hensel root, and the full-torsion flag. Each must be rejected by the
separate program with its designated diagnostic. A modified README must also be
rejected by the payload-integrity checker. These tests do not invent failed
scientific runs; they are deliberate corruptions in temporary scratch copies.

The primary and separate finite programs have both passed during development.
The observed default Block70 replay passed before this block. Final extracted-ZIP
replay and CRC/member/hash audit are recorded in the external final artifacts after
packaging, so there is no circular self-hashing success claim.

No new point counts, Lean compilation, independent mathematical reviewer, or
fresh full historical-chain execution are claimed. Finite results do not prove
the actual geometric hypotheses or certify the universal analytic argument.

A schema-v1 computation manifest records the observed primary/separate run and
adds exact before/after input hashes. Its preserved project-local v1-only validator
is run during replay. This is not the full plugin validator; the v1 provenance
limitations are explicit. The reported finite execution does not certify the
mathematical source-to-family interpretation.
