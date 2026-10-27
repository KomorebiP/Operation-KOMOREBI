$ErrorActionPreference = "Stop"
python .\complex_signal_image_benchmark.py --out .
python .\generate_tables.py
latexmk -pdf -interaction=nonstopmode -halt-on-error .\Complex_Signal_Image_Gibbs_Benchmark.tex
