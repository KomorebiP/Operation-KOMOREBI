# Realization Boundaries

## Finite Grammar, Infinite Groups, and the Limits of Reconstruction

**Komorebi P. · Realization Calculus · MIT license**

A monograph, Lean library, and exact Python implementation about what finite observations preserve, what completion forgets, and what information is required to compute a realization.

The central family consists of countable abelian groups

$$
D=\bigoplus_p C_p\subseteq G_A\subseteq P=\prod_p C_p.
$$

Every member has the same full unmarked finite-quotient system and profinite completion. Yet

$$
G_A\cong G_B\iff A\triangle B\text{ is finite},\qquad
G_A\text{ has an }X\text{-computable copy}\iff A\le_T X.
$$

Every ordinary Turing degree occurs as a least presentation degree over one fixed computable observation system. Every fixed countable description grammar misses continuum many pairwise nonisomorphic members. The development also proves subgroup classification, root certificates, exact finite quotients, homomorphism structure, and categorical reconstruction boundaries.

**All 45 registered monograph contracts are complete in the checked Lean companion.**

| Accepted verification | Result |
|---|---:|
| Production modules rebuilt and kernel-replayed | 66 |
| Named source theorems and lemmas | 813 |
| Audited declarations | 2,188 |
| Positive contract declarations | 205 |
| Intended rejection controls | 44 |
| Passing command gates | 183 |

These counts describe the accepted mathematical release. GitHub packaging changes preserve its checked proof inputs and original receipt.

## Start here

- [Read the 66-page monograph](publication/Realization_Boundaries_Monograph.pdf).
- [Browse the Lean entry point](RealizationBoundaries.lean) and [production modules](RealizationBoundaries).
- [See the complete statement coverage map](docs/MONOGRAPH_COVERAGE.md).
- [Inspect exact audited declaration types](docs/ACCEPTED_EXACT_DECLARATIONS.json).
- [Read the verification report](LEAN_VERIFICATION_REPORT.md) and [accepted receipt](verification/accepted_v1.0.0/run.json).
- [Run the worked Python examples](publication/monograph_source/README.md).
- [Build and verify from source](docs/BUILDING.md).

## Quick start

Run commands from the repository root after extracting the ZIP or checking out the repository.

```bash
python3 verify_integrity.py
lake exe cache get
lake build
```

The Lean commands require an installed Lean toolchain manager such as `elan`. The repository's [lean-toolchain](lean-toolchain), [Lake configuration](lakefile.toml), and [dependency manifest](lake-manifest.json) pin the exact compiler and dependency revisions. The cache command downloads the pinned dependencies and their compiled caches. Keep the manifest unchanged when reproducing this release.

For the full Linux or WSL2 audit, once the dependencies are present:

```bash
bash verify_with_lake.sh --output ../realization-boundaries-verification
```

The output directory must be new. This runs the existing strict verifier using the pinned Lean installation on `PATH`. A separately supplied offline portable kit is also supported; see [building instructions](docs/BUILDING.md#offline-portable-kit).

For the exact Python examples, which need only Python 3.10 or later and its standard library:

```bash
cd publication/monograph_source
python3 worked_example.py
python3 src/replay_printed_example.py
```

## Scope and evidence

The coverage registry links every numbered contract to accepted declarations. Computability claims use explicit oracle programs, decidable semantic equality, and genuinely bijective names. The original group, its completion, marked and unmarked copies, and semantic descriptions versus effective presentations are kept distinct.

Accepted proof dependencies are restricted to `propext`, `Classical.choice`, and `Quot.sound`. The production audit accepts no placeholder proof, project axiom, unsafe declaration, or native-decision trust axiom. Replay uses the same Lean implementation and pinned imported caches. It is not independent-kernel checking or external peer review.

The Lean code proves finite-code interpretation, root oracle and loop bounds, and cocycle query locality. Polynomial bit-cost bounds and kernel certification of the separate Python runtime are outside the release's claims. The Python suites passed 189,069 exact finite assertions; those are implementation checks, separate from the universal Lean proofs.

## Repository contents

| Path | Contents |
|---|---|
| `RealizationBoundaries/` | Checked Lean production sources |
| `tests/` | Positive contracts, native examples, and rejection controls |
| `scripts/` | Original accepted verification tooling |
| `publication/` | Monograph PDF, editable source, vector figures, and Python implementation |
| `docs/` | Coverage, proof interfaces, reviews, and historical notes |
| `verification/accepted_v1.0.0/` | Accepted compiler, audit, replay, and identity evidence |
| `verification/development/` | Clearly labeled development attempts and reviews |
| `provenance/` | Preserved predecessor material |

[Citation](CITATION.cff) · [Contributing](CONTRIBUTING.md) · [Release notes](RELEASE_NOTES.md) · [License](LICENSE) · [Progress ledger](PROGRESS_LEDGER_v1.0.0.md)
