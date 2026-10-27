# Constructive Repair 1.0.0rc3

## Result

The standalone component is technically ready within its tested Linux x86_64 /
CPython 3.13.5 scope. Public code and document licenses remain unselected and no
public upload has been made. No new mathematical theorem or repair algorithm
was introduced in this pass.

## The two changes

The current package no longer embeds prior ZIPs recursively. It retains all
active sources, proof modules, inputs, examples and ordinary logs. Exact proof
snapshots preserve the source comparisons from 10/23/37/51-module historical
releases. Their original archive hashes are recorded. This is an explicit compact
distribution, not a claim that every prior binary archive is still inside it.

The new gate binds the current code and wheel to their test receipts, the current
proof sources to the complete formal receipt, and the current PDF to the LaTeX
build. It detects stale or modified files even when an ordinary checksum manifest
is regenerated. It is not a signature, independent proof checker, or proof that
untrusted supplied logs are genuine.

## Fresh results

- 51 unchanged Lean proof modules rebuilt and replayed.
- 526 declaration axiom lists audited. The permitted set remains propext,
  Classical.choice, Quot.sound only.
- 141 verification commands and 230 passing checks.
- 24 paired false-certificate rejections and one forbidden-axiom policy control.
- 100 API/portability/artifact unit tests, including 32 new artifact-binding tests.
- 134 retained engine tests and the original 20-test, 3,307-record audit replayed.
- 72 installed input/certificate pairs, 369 installed assertions, 24 platform checks.
- Two clean local wheel builds produce identical bytes.
- A clean 73-page monograph build. All pages rendered and inspected.

The ordinary mathematical chapters and declaration registers were not shortened.
The reduction from 77 to 73 pages consolidates repetitive engineering appendices.
Historical details and failed attempts remain in the development records.

## Failure record

The initial container streaming session was unavailable, so runtime recovery was
launched with a normal subprocess. The first test attempt revealed the obsolete
archive-bound regression after compact packaging, one implicit test-file encoding,
and missing imports from invoking tests without PYTHONPATH. Those were corrected
and the tests rerun. A passing acceptance before the final document-builder change
was explicitly superseded and repeated. No failed attempt is counted as a PASS.

## Final-artifact scope

The final ZIP has a separate checksum and extracted verification report. The
included fault-injection runner checks a disposable copy and restores its files.
Licensing remains the author decision. Existing parser, platform, runtime and
integration limitations remain explicit. The original rc2 ZIP is preserved as a
separate historical artifact, not recursively doubled inside this one.

The provisional compact archive passed all 14 manifest-refreshed corruption controls, plus the unmodified and restored release gates. The final frozen archive is checked separately after these logs are packaged.
