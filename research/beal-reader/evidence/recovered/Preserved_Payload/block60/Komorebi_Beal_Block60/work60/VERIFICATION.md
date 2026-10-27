# Reproduction and finite-assertion contract

Run from the package root:

    python verify.py --replay-predecessors --report ../Block60_Replay.json

Python3.10+ and only the standard library are required. No network, compiled
extensions, Lean, or SymPy is needed. The optional predecessor flag restores
the original Block59 ZIP and runs its declared selected nested replay chain.
The report must remain outside the immutable package.

The verifier hashes all payload files and seven named immediate inherited
source leaves. Both scientific outputs are deleted and regenerated in a scratch
copy, then compared as complete JSONs. It separately requires rejection of an
altered rational smoothing constant, an altered positive-witness torsion flag,
and an altered proof-note payload. Input hashes before and after are compared.

Primary domains: rational Q(phi), phi^2=phi+1; residue fields for every prime
11<=q<=2000, including both split places; every nonzero pair(A,C0) at the four
survivor primes; integer Hensel lifts modulo q^52. No random sampling or floating
point tolerances occur. The independent implementation uses sqrt5 coordinates,
inverse-conic derivatives, descending-generator discrete logarithms, and
single-digit Hensel lifting. It imports no primary arithmetic code.

The counts are445 residue fields;5,474,280 unit pairs;111,720 positive49-level
residue pairs;12 local root certificates (four positive, four seventh-only,
four failing even7). Every local root is reproduced modulo q^52. The Hensel
existence proof defines a q-adic root, not an integer solution inferred from
a modular zero. The finite computation does not certify analytic uniformization
or the source-to-model smoothing comparison.

Default wall cap is180seconds per job, with a15-times cap for the aggregate
predecessor wrapper. No extra CPU/memory quota is asserted. Timeouts have status
INCONCLUSIVE_TIMEOUT. Execution times, command lines, Python/platform versions,
input and output hashes and actual exit codes are recorded. The final ZIP is
freshly extracted and replayed; its external audit avoids a circular checksum.
No new Lean compilation or independent mathematical review is claimed.
