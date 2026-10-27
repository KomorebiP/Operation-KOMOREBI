# Verification contract, Block57

Python3.10+, standard library only. Execute from the package root:

    python verify.py --replay-predecessors --report ../Block57_Replay.json

The original Block56 ZIP was restored and replayed first. Its selected nested
predecessors also passed. The successful startup report and the initial
streaming-launch failure are preserved in verification/.

Three new production programs generate exact deterministic JSON records.
The independent program imports no primary arithmetic. Its residue fields,
power symbols, rank certificate and kernel construction use different methods.
All results are compared in full, not by checking a cached status flag.

Coverage:12 residue fields,132 direct-symbol comparisons,2352 normalized
natural F49 directions,2401 independently enumerated F49 kernel parameter
pairs,1024 rational support subsets,28 rational-unit probes,29412 toric trace
congruence cases,84035 separated principal-residue tests,486 nonrational exact
matrix examples. The two nonzero augmented systems and h1 local control are
retained rather than reported as universal exclusions.

The verifier records actual argv, Python/platform, process IDs, timing, exit
codes, stdout/stderr, input hashes before and after, and result hashes. Every
job has a finite wall limit, default180seconds. The predecessor wrapper has a
separately recorded longer limit. No additional memory or CPU cap is imposed
beyond the environment. A timeout is inconclusive and returns a nonpass status.

The source audit pins13 named inherited leaves and the byte-identical copied
arithmetic module. The payload audit checks an exact member set. A negative
control modifies one residue logarithm and requires the independently recomputed
symbol to reject it. Final packaging separately tests an altered payload.

Final ZIP replay and CRC/member/hash audit are external records, avoiding
self-referential checksum claims. Development replay records identify their
own snapshot; the final extracted-ZIP replay is authoritative for final bytes.

A pass verifies the declared exact finite assertions and byte integrity. It
is not a proof of upstream unformalized geometry, a Lean certificate, independent
mathematical review, an unrestricted support theorem, or a proof of Beal.

The observed development replay returned PASS_DECLARED_CHECKS for all new
programs and the altered-log rejection. Its predecessor replay was NOT_REQUESTED;
the separate startup replay covers that step. The final extracted-ZIP replay
requests the full selected predecessor chain again.
