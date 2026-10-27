# Building the monograph

## Requirements

- A recent TeX Live distribution
- `pdflatex`
- `latexmk`
- The LaTeX packages used by the source: `amsmath`, `amssymb`, `amsthm`, `mathtools`, `bm`, `mathrsfs`, `centernot`, `xcolor`, `enumitem`, `booktabs`, `array`, `tabularx`, `longtable`, `fancyhdr`, `hyperref`, `lmodern`, and `microtype`
- Python 3.11 or later for repository tooling
- `pdfinfo`, `pdffonts`, and `pdftotext` for strict PDF verification

## Standard build

From the repository root:

```bash
python scripts/repo.py build
```

or

```bash
make build
```

The canonical source is `monograph/Stratified_Relational_Workspace_Theory.tex`. It imports the front matter, 26 part files, and the bibliography. Build output is written to `build/`, keeping auxiliary files out of the source tree.

## Windows PowerShell

```powershell
python .\scripts\repo.py build
```

A direct LaTeX invocation is also valid:

```powershell
Set-Location .\monograph; latexmk -r ..\latexmkrc -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=..\build .\Stratified_Relational_Workspace_Theory.tex; Set-Location ..
```

The wrapper script can be used as follows:

```powershell
.\scripts\build.ps1 -Task verify -Strict
```

## Linux and macOS

```bash
./scripts/build.sh verify --strict
```

The shell wrapper invokes the same Python entry point as the PowerShell wrapper.

## Cleaning

```bash
python scripts/repo.py clean
```

## Expected output

A successful canonical build has 209 pages and no unresolved references, citation warnings, overfull boxes, underfull boxes, or LaTeX warnings. The committed PDF remains in `monograph/` so readers can access the work without installing TeX.
