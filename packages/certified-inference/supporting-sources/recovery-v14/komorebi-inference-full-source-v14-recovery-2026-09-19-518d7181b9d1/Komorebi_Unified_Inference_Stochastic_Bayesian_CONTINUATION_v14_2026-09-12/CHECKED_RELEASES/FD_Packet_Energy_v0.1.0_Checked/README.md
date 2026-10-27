# Komorebi: packet-resolved posterior error certificates

This checked release closes finite self-adjoint Frobenius energy decomposition and
hierarchical refinement for the previously proved Gaussian posterior-distribution
coupling. It includes exact packet residual stopping conditions and a certified-local-
upper-bound interface. It does not include a certified floating-point implementation.

Start with PROOF_NOTE.md for mathematics, CONTINUE_HERE.md for the next target,
FINAL_VERIFICATION_RECEIPT.json for execution evidence, and FAILURE_LOG.md for
failed or incomplete attempts. Axiom coverage includes every active theorem/lemma.

The ten new proof modules are PacketMatrixEnergy, SelfAdjointPackets,
PacketEnergyDecomposition, PacketVectorEnergy, PacketEnergyRefinement,
PacketCoarsening, PacketEnergyChecks, FDMatrixPacketEnergy,
FDResidualPacketCertificate, and FDPosteriorPacketFactors.

The pinned portable runtime is external to this source release. It is identified
in the full continuation's LEAN_RUNTIME_METADATA. From this directory, run:

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --modules FDKalmanDefs --clean --timeout 40
```

Continue one module at a time in MODULE_ORDER.json without --clean. After all modules:

```bash
python audit_integrity.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python checks/exact_packet_checks.py
```

The integrity auditor checks receipts and live compiled hashes; it does not rerun Lean.
Its default mode is read-only. Use --seal only when intentionally creating a new
verification receipt, then regenerate any affected archive hashes.
The exact Python checks are independent finite diagnostics, not a universal proof.

A snapshot source commit is recorded in the receipt. Repository metadata is omitted
from the distributable ZIP. See BUILD_CONTRACT.md for archive reproduction details.
