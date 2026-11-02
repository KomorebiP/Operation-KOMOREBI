"""Render the 32 original catalytic figures for their 34 manuscript uses."""
from render_symmetry_figures import BASE,render


if __name__=='__main__':
    render(BASE+'generated/g_main.tex','assets/figures/quantum-catalytic/',32,34,'catalytic')
