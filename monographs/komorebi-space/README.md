# Komorebi Space

**Coherent Realizations, Obstructions, and Descent**  
Komorebi P. · Realization Calculus

This is the completed publication package for Komorebi Space. It contains the monograph, visual and Lean guides, worked proofs, editable sources, exact examples and the complete current formal verification record. All sixteen principal theorem groups have formal counterparts under their stated hypotheses.

## Read the work

| Reader | Contents |
|---|---|
| [Monograph](books/Komorebi_Space.pdf) | The continuous mathematical development, proofs, examples and source correspondence. |
| [Visual guide](books/Komorebi_Space_Visual_Guide.pdf) | Sixteen worked visual investigations, including genuine three-dimensional geometry. |
| [Lean guide](books/Komorebi_Space_Lean_Guide.pdf) | Formal interfaces, assumptions and using the source. |
| [Worked proofs](supplements/komorebi-space-worked-proofs-v4/Komorebi_Space_Worked_Proofs.pdf) | Additional calculations, proofs and visual constructions. |

Read [the closeout report](release/CLOSEOUT_REPORT.md) for actual completed checks and [reading and scope](release/READING_AND_SCOPE.md) for their interpretation. Counts of groups, modules, declarations and finite checks are distinct units.

## Verify and reproduce

Before creating local build outputs:

```sh
python3 tools/verify_package.py
```

The strict manifest covers the exact regular-file set, sizes and SHA-256 hashes. `SHA256SUMS` is a convenient additional payload list and excludes itself and the manifest to avoid circular hashing.

The original formal source is under `lean/`. The unchanged integrated runner freshly compiles all 166 targets, audits all exported declarations and checks its 56 mixed acceptance, elaboration-rejection and policy-rejection controls. Follow [the fresh replay guide](verification/closeout/FRESH_REPLAY_GUIDE.md) for the pinned external runtime and offline cache setup. The recorded run used Linux x86-64 and the shipped executable-path adapter. On Windows, the same Linux runtime can be used through a suitable WSL environment; no native Windows run is asserted.

With the pinned toolchain and dependencies prepared, run from this package root:

```sh
python3 verification/runner/runner.py --output ../space-verification-01
```

Choose a new output directory outside the package. A static `--plan-only` result is not proof verification. The external compiler and dependency caches are not bundled. The five saved compact runtime parts can be restored with `tools/restore_runtime.py`; their identities and actual setup are retained with the fresh replay records.

For the current readers, install the TeX and Python dependencies described with the publication sources, then run:

```sh
python3 tools/build_readers.py --book all
```

This builds from `publication/volume_i/source/`. The unchanged older source tree and versioned PDFs are retained as the accepted mathematical and editorial baseline. `tools/build_books.py` belongs to that baseline. Use `tools/build_readers.py` for the current licensed readers.

Start an exact executable example with:

```sh
python3 examples/protected_repair.py --demo
```

[The worked certificate](examples/WORKED_EXAMPLE.md) gives a complete generation and verification route, exact expected values and deliberate rejection cases. These Python implementations are tested examples, not certified extractions from Lean.

## Source and evidence

- `publication/`: current reader sources and shared presentation material.
- `lean/`: unchanged accepted formal development and its pinned dependency manifest.
- `examples/`: exact rational programs and documented inputs.
- `verification/closeout/`: the new completed formal run, logs, objects and setup.
- `verification/readers/` and `verification/examples/`: current publication and bounded-computation checks.
- `verification/current/`: the inherited publication's accepted records, retaining their original names and dates.
- `history/`: intact predecessor publication and Technical Record archives.
- `release/`: closeout, source review, scope and distribution records.

The historical Technical Record intentionally omits its compiled object bytes. Their hashes remain recorded, and this release supplies the new run's compiled objects. Historical status wording is not relabeled as a fresh run. The complete current scope is in [CLOSEOUT_RECORD.json](release/CLOSEOUT_RECORD.json).

## Reuse and citation

Original software and machine-readable project material use MIT. Original writing, figures and editable writing sources use CC BY 4.0. See [LICENSE.md](LICENSE.md), [REUSE.md](REUSE.md), and `licenses/` for full terms and third-party notices.

Cite Komorebi P., *Komorebi Space: Coherent Realizations, Obstructions, and Descent*. Machine-readable records are in `CITATION.bib` and `CITATION.cff`. Distribution 1.16.0 identifies this source-and-evidence package.
