# Building and running

## Current executable checks

Python 3.13.5, NumPy 2.3.5 and pytest 9.0.2 were used in the recorded current check. `requirements-current.txt` pins the latter two. The exact finite interface itself uses only the Python standard library. Actual OSL execution uses the current core and NumPy.

Use a separate virtual environment. The package does not install dependencies automatically:

```text
python -m venv ../osl_env
# Activate this environment using your shell's normal activation command.
python -m pip install -r requirements-current.txt
python verify_release.py
python run_current_checks.py --output ../my_check_results
```

The requested results directory must not exist and must be outside this release. The example virtual environment is also outside the sealed package. Activate it with your shell’s platform-specific command before installing dependencies.

`run_current_checks.py` prints progress and its final report path. It checks subprocess exit codes, preserves logs, kills timed-out process groups on POSIX, and does not classify a timeout as a pass. On Windows it attempts `taskkill /T` before final process termination. Use `--timeout SECONDS` to change the per-command limit.

The direct demo may be run as `python interface/run_demo.py --output ../local_demo`. Always choose an external output location to leave the sealed edition intact.

## TeX

Install a TeX distribution containing pdfLaTeX, latexmk, newpxtext/newpxmath, microtype, booktabs, longtable, tabularx, ragged2e, enumitem, listings, TikZ, tcolorbox, titlesec, fancyhdr, hyperref, and cleveref. Font files come from the local TeX installation; none are redistributed here.

```text
python build_manuscripts.py --output ../rebuilt_papers
```

Each manuscript directory can also be built directly with `latexmk -pdf NAME.tex`, preferably with an external `-outdir`. Its `style.tex` and `public_references.tex` are local, so the LaTeX source bundle does not require the large experiment archives to compile.

A rebuild can differ in PDF bytes across TeX versions or metadata settings. Do not replace frozen PDFs and then claim the old manifest still covers them. The validation target for a portable rebuild is successful compilation and matching content, with a new manifest for a revised release when necessary.

## Historical Neuralese branches

Choose the appropriate original ZIP and extract it into its own directory. Consult its own requirements and current outcome first. Do not run its root scripts merely because another branch uses the same filename. Some scripts perform training or one-shot evaluation, neither of which is part of the safe default edition check. Full pretrained backbones are not supplied by the new edition; only original archive payloads are preserved.
