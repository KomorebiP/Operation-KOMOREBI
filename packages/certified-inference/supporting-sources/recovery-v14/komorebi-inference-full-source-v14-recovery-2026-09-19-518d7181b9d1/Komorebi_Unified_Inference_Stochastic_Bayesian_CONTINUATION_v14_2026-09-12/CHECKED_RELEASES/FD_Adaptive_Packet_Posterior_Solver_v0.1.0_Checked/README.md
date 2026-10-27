# Certified greedy packet-selective inference

Author: Komorebi P. Continuation v13, 2026-09-12.

This release implements a solver that recomputes output-packet residual energies
and updates only the largest packet. Lean proves contraction, a computable finite
iteration budget, successful rounded verification, and returned posterior parameter
intervals for every positive rational distribution and output-radius tolerance,
under the declared valid exact model and packet assumptions.

The new packet updates use **exact rational arithmetic**. Certificate evaluation
and output arrays use the inherited outward-rounded dyadic operations. The v11
rounded full-update solver remains available as a separate checked branch. This
release does not silently transfer its roundoff theorem to packet-selective updates.

The geometry is fixed. Selection changes what is updated; it does not split packets
or alter the model. The reference implementation still scans all output packets
and evaluates full certificates. No performance advantage is claimed.

## Run and certify

Python 3.10+; standard library only. From the release directory:

```bash
python3 checks/adaptive_packet_solver.py examples/adaptive_coordinate.json --output results/my_adaptive.json --try-precisions 4 12 --emit-lean Komorebi/MyAdaptive.lean --namespace MyAdaptive
```

`PASS_ADAPTIVE_PROVISIONAL` must be followed by compilation of the exported Lean
instance before that particular execution is formally certified. The exporter
checks the actual selective-program return, selected labels, represented gain,
score, output precision, all centers/radii, and the final ResultValid statement.
The mathematical data certified are the explicit rationals in the emitted source.
A universal JSON parser/exporter refinement theorem remains outside the contract.

Input `seed` names an output packet and `scan` must cover every output packet.
Duplicates and arbitrary order are permitted; ties preserve the incumbent.
`epsilon` is the posterior distribution tolerance; `output_radius` bounds each
parameter enclosure radius for the certified approximation. Use exact fraction
or decimal strings; raw JSON floating-point numbers are rejected.

Producer caps: dimensions at most 8; at most 16 verification probes; scan length
at most 128; at most 512 fractional bits; default 10,000 updates and 32,768 gain
rational bits. Caps can return `RESOURCE_LIMIT`, which cannot export a success
proof. A mathematical finite-fuel theorem is not a hardware resource guarantee.

## Checked examples

| Example | Selections | Updates | Gain | Certificate bits | Output bits |
|---|---|---:|---|---:|---:|
| Two-state, one observation, coordinate packets | 0,1,0,1,0 | 5 | (228/343, 8/49)^T | 12 | 32 |
| Singular two-state prior, rotated packets | 0,0,0 | 3 | (39/125) times the all-ones matrix | 12 | 32 |

The tolerances are respectively epsilon=1/20 and epsilon=1/4. Both output-radius
tolerances are 1/1000. The second output packet in the rotated example has zero
exact residual and is never updated in this execution. Rounded certificate
upper bounds for zero packets can still be positive.

The sufficient fuel bounds are 410,093 and 4,267, respectively. These conservative
bounds establish termination; the program verifies at each iterate and stops early.
They are not iteration-count predictions or evidence of practical efficiency.

## Reproduce the formal checks

Use the preserved portable runtime: Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d, mathlib
aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Runtime binaries are distributed
separately; restoration metadata is included.

```bash
python3 verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --timeout 120 --clean
python3 checks/negative_controls.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/test_adaptive.py results/local_diagnostics.json
python3 checks/seal.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For new exported instances, run `python3 checks/build_inventory.py`, then compile
the added modules and AdaptiveAxiomAudit and rerun the seal. All Lean processes
use one thread and warnings as errors. No placeholder or custom axioms are used.
The current block compiled 12 new modules, including the all-declaration audit.
The 78 inherited modules retain matching v12 compilation receipts and output
hashes; they were not freshly rebuilt again in this block. All 90 active sources,
compiled outputs, and direct dependencies passed the final provenance seal.

`computations/adaptive-final` is the final bounded diagnostic run, with a validated
Mathbox v2 manifest. Its 911 assertions and eight expected rejections are finite
diagnostics, distinct from the universal Lean theorems. All 455 active theorem/
lemma declarations have audited axiom lists contained in propext, Classical.choice,
and Quot.sound. Counts include support lemmas and regressions, not novel discoveries.

Read PROOF_NOTE.md for the contract, SELF_REVIEW.md for the proof audit, and
FAILURE_LOG.md for unsuccessful attempts. The canonical theorem is
`Komorebi.AdaptivePosterior.runAdaptive_terminates`.
