# Block 49 verification and proof boundaries

The principal written routes received fresh independent mathematical
review. These are audits of explicit written arguments and source
applications, not formal proof certificates or independent published
verification of the research program.

| Written result | Independent review | Disposition |
|---|---|---|
| Additional prime on the reducible branch; exact abstract extension-space dimension | `notes/extension_audit.md` | Proved under the explicitly inherited Block48 contract |
| Split local monodromy at three and five | `notes/local_types_review.md` | Proved; RM-factor assertions retain their integral-decomposition hypothesis |
| CM realization of l and its local restrictions | `notes/last_form_audit.md` | Proved with the direct normalized residual-comparison hypothesis and imported complete level data |
| Alternative elliptic representation | `notes/alternative_audit.md` | Proved for 5 divides C; variable conductor is retained |
| Abstract arithmetic normalizer cover and necessary lifting condition | `notes/last_form_cover_audit.md` | Proved with the stated source and finite-group inputs; rational points remain undetermined |

The audit records pin the exact proof revisions and inspected sources.
`STATUS.json` records the current claim boundaries and hashes of the proof
and review files. Any future modification to those files requires revisiting
the affected audit; matching filenames alone do not preserve a review.

## Exact computations

All runs use exact integer, rational, polynomial or finite-field arithmetic;
none uses numerical tolerance or random sampling.

| Run | Tested assertion and range | Limit |
|---|---|---|
| `local_types_run` | Exact translated-polynomial/radicand identities; Newton polygons and discriminant compatibility for c=1,…,100 | Uniform valuations and local geometry are proved separately in writing |
| `lastform_run` | All fourteen q11 fingerprints; exact Frobenius polynomials at 11,19,29,31,41,59,61,71; independent second q11 count | No Sturm theorem; modular existence and conductor are separate proof inputs |
| `alt_elliptic_run` | Four exact polynomial identities; unit residues at 5,7,11,19,29,41; the four classified j-values at five | Does not compute every modular level or prove the isogeny classification |
| `lastform_normalizer_run` | Complete PSL2(F49), order58800; normalizer of order50; generating triangle triple; all1176 cosets and branch permutations | Arithmetic identification is a separate written argument; no rational-point computation |
| `lastform_monodromy_run` | All96 determinant-one trace-compatible pairs, partitioned into four centralizer orbits; every representative generates PSL2(F49) | Arithmetic specialization and descent require their separate written proof |

Each run has a version-two contract/manifest, command, input and output
hashes, exact range, and execution status. The parent checked that every
input hash is unchanged, output hashes match, and the five processes exited
successfully. That check is recorded in
`verification/checkpoint_manifest_checks.json`. Source copies omitted from
the archive are not required by these executable checks.

From the archive root, the substantive scripts can be replayed with:

```bash
python3 work49/computations/local_types_exact.py
python3 work49/computations/lastform_boundary.py --output /tmp/beal49_boundary_replay.json
python3 work49/computations/alt_elliptic_invariants.py
python3 work49/computations/lastform_normalizer.py --output /tmp/beal49_normalizer_replay.json
python3 work49/computations/lastform_monodromy.py --output /tmp/beal49_monodromy_replay.json
```

The first and third commands write their declared results beneath `work49`;
run them in an extracted copy to preserve the frozen checkpoint. The release
check uses such an isolated extraction and compares replayed results.
All five replayed commands passed, with every declared JSON result equal
to the retained result; the receipt is `verification/package_replay.json`.

## Mathematical checks requiring more than successful code

- The opposite-lattice proof uses characteristic-zero local sublines and a
  direct local H1 calculation. It does not assume finite flatness or residual
  ramification survives arbitrary lattice changes.
- The extension-space dimension counts prime ideals of K, not rational primes.
  Its abstract classes are not asserted to come from an abelian variety.
- The CM identification has an explicit endomorphism, local good models,
  sourced Hecke characters and induction, and a distinguishing fingerprint
  inside a complete finite space. Eight agreeing traces alone are insufficient.
- The comparison at seven identifies actual full four-dimensional residual
  modules. Their simplicity makes lattice semisimplification sufficient here;
  Raynaud's theorem then transports the isomorphism to finite-flat models.
- The a-number source is checked separately from the p-rank source. This is
  needed to distinguish 7 divides A from 7 divides B.
- The elliptic representation is different from the original RM system and
  is considered over Q. Its absolute irreducibility supplies no contradiction
  to reducibility of the original system over K.

## Formalization, proofreading and unavailable computations

No new Lean arithmetic theorem is claimed. The inherited local-algebra Lean
checks remain exactly within their old stated scope. No Magma or Sage Hilbert
space calculation ran; the higher-level exporter remains unexecuted.

The parent conservatively self-reviewed the new report, handoff and verification
text for notation, scope, formula transcription and references. No mathematical
tokens in frozen predecessor files or independently reviewed proof files were
changed by that pass. The cover calculation is supported by a separate
arithmetic-cover proof and review. No explicit
equation or rational-point exclusion for that cover is claimed.

The archive builder verifies the predecessor archive hash, every packaged
byte, its internal checksum list and ZIP integrity. Checksums have no
mathematical force.
