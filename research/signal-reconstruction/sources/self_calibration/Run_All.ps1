$ErrorActionPreference = "Stop"
python .\polyphase_gibbs_breakthrough.py --out .
pdflatex -interaction=nonstopmode -halt-on-error .\Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex
pdflatex -interaction=nonstopmode -halt-on-error .\Self_Calibrating_Polyphase_Gibbs_Reconstruction.tex
