# Build instructions

## Linux or WSL

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error master.tex
```

## PowerShell

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error .\master.tex
```

## PDF verification

```bash
python /home/oai/skills/pdfs/scripts/pdf_preflight.py master.pdf --json
python /home/oai/skills/pdfs/scripts/render_pdf.py master.pdf --out_dir rendered --dpi 96
```
