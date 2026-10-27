# Paper II computational verification

The existing Paper II finite checks passed on 5 October 2026. This folder contains the raw logs, measured results, input hashes and a portable runner. It does not contain a fresh Lean build or kernel audit.

| Check actually performed | Observed result |
|---|---:|
| Original release pytest suite, warnings treated as errors | 48 passed; 0 failures, errors or skips |
| Existing release JSON/CSV comparison | PASS; all 9 canonical summary rows |
| Original figure regeneration | 13 PDF and 13 PNG files |
| Appendix exact checks | 118 passed |
| Saved appendix record comparison | Identical except timestamp |
| Regenerated appendix TikZ plates | 22 of 22 byte-identical |
| Original release checksum manifest | 96 of 96 entries matched |
| Before/after source hashes | 97 release files and 31 appendix files unchanged |
| Computation-audit v2 manifest validation | Valid evidence record |

The run used the complete original `release_v1.2.1` collection, including its wheel and PNG files. The earlier curated source subset lacked those binary artifacts and was not used as the release-comparison target. No source was modified and no dependency was installed. The observed run lasted 20.158466 seconds.

## Reproduce the same finite checks

Use Python with the dependencies in the original release's `code/python/requirements.lock`. The appendix's exact code requires SymPy 1.14.0; it does not require the PDF-assembly packages for this command.

```sh
python Run-Computational-Checks.py \
  --release-root /path/to/release_v1.2.1 \
  --visual-root /path/to/visual_appendix \
  --output-dir /path/to/new-check-output
```

The output directory must be new and outside both source trees. The runner sets `PYTHONDONTWRITEBYTECODE=1`, disables pytest's cache, uses an isolated Matplotlib configuration directory, and runs the appendix checks and graphic generator in a temporary copy. It records each exact command, working directory, return code, duration, stdout and stderr. It does not install packages. The four commands are the original pytest suite, original `run_all.py --output-root ... --compare-release-root ...`, appendix `verify_examples.py`, and appendix `generate_graphics.py`; no new mathematical tests were introduced.

The recorded run additionally used the computation-audit bounded runner: 600 seconds overall, 240 seconds per child command, 4 GiB address space per process, 480 CPU seconds per process, two CPU cores, and cooperative single-thread numerical-library settings. Its full argv is in `bounded_runner_command.json`; its validated evidence is `run_2026-10-05/manifest.json`. That manifest retains the original workspace-relative paths as historical provenance. To rerun after relocation, use the portable command above with the actual source paths.

## Evidence and limits

`run_2026-10-05/results/verification.json` contains measured counts, software versions, pin differences, command records and output hashes. `source_hashes.json` records inputs before and after; `release_integrity.json` records every original checksum; `tikz_comparison.json` records every plate's two hashes; `EXACT_CHECKS.json` records every named exact assertion and its scope. The corresponding `.stdout.txt` and `.stderr.txt` files are retained. Every command exited with code 0 and all four stderr files were empty.

Python was 3.12.14, NumPy 2.3.5, SymPy 1.14.0 and pytest 9.1.1. This was not an exact replay of the archived environment: Python's release documentation specifies 3.12.13, and the installed `build`, `fonttools`, `kiwisolver`, `matplotlib`, and `pyproject_hooks` versions differed from the release lock. All installed versions and differences are recorded. The exact checks and original numerical comparator passed with that environment.

The release comparator uses relative tolerance `1e-12` and absolute tolerance `1e-14` only for nonintegral real values. Keys, sequence lengths, strings, Boolean values, integral counts and symbolic values must match exactly. Original release figures were regenerated and checked for presence and stem agreement; this run does not claim their PDF/PNG bytes equal the shipped files. Appendix TikZ bytes were compared exactly.

These results reproduce the implemented finite assertions and the documented numerical record comparison. They are not universal mathematical proofs, an independent audit of every implementation, a fresh wheel build/install, or a fresh Lean compiler/kernel replay. Precise tested families and limits are in `COMPUTATIONAL_SCOPE.md` and the original test files.
