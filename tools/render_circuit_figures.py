"""Render the twelve original circuit visual-study PDFs, with source receipts."""
from quantum_circuits import VISUAL,FIGURES,normalize_visual
from render_symmetry_figures import render

if __name__=='__main__':
    render(VISUAL,FIGURES.removesuffix('figures.json'),12,12,'circuit',normalize_visual)
