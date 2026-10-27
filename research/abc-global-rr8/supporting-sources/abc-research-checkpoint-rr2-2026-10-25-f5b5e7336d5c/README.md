# ABC research checkpoint RR2

ABC remains unproved. This package continues the latest square-kernel work and
keeps the full every-epsilon conjecture as the target.

Start with [the current result](abc_work/LATEST.md), then consult
[the claim ledger](abc_work/CLAIM_LEDGER_RR2.md) and
[the continuation handoff](abc_work/HANDOFF.md).

The strongest restricted pointwise result controls all ordinary exponent
lifting in A^n+B^n. Other results strengthen full-radical counting, give exact
arithmetic-derivative image formulas, and disprove two proposed kinds of
radical-escape shortcut. None supplies the remaining unrestricted height bound.

Read [ERRATA.md](abc_work/ERRATA.md): the prior fixed-offset statement must
explicitly retain gcd(h,Q)=1. Its main square-kernel family is unaffected.

The package includes the original latest archive and five nearby input
checkpoints, extracted source records, all five new route derivations,
separate proof reviews, exact verification scripts, and computation records.
The source comparison uses Pasten's primary arithmetic-derivative paper with
its exact exponent dependencies. No copy of the external paper is included.
No historical originality or Lean-verification claim is made.

## Reproduce

Python 3.9 or newer is sufficient. No third-party package is required. From
this directory run:

```bash
python3 abc_work/reproduce.py
python3 abc_work/check_evidence.py
```

On Windows, `python` may be used in place of `python3`.

The first command reruns five explicitly bounded finite contracts and updates
their outputs and manifests. The second verifies their current input/output
hashes. Their tests concern finite arithmetic assertions, not the truth of ABC.
Proof reviews and the written derivations are separate from those tests.
Rerunning changes execution timestamps and runtime fields, so the original
package-root checksum list describes the distributed snapshot.

The distributed records passed the version 2 computation-manifest validator
and all input/output integrity checks. The package-root SHA256SUMS.txt is the
current integrity list. Original input-checkpoint checksums are retained in
their extracted directories. Superseded generated checksums for rerun route
outputs are omitted in favor of the current package-root list.
