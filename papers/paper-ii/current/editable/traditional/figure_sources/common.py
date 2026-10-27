"""Shared, portable drawing style for the ten main-text figures."""
from pathlib import Path
import os
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
for font in (ROOT / "fonts").glob("NimbusSans-*.otf"):
    font_manager.fontManager.addfont(str(font))
plt.rcParams.update({
    "font.family": "Nimbus Sans", "font.size": 10.5,
    "mathtext.fontset": "dejavusans", "pdf.fonttype": 42,
    "ps.fonttype": 42, "axes.labelcolor": "#212B34",
    "text.color": "#212B34", "xtick.color": "#58646B",
    "ytick.color": "#58646B", "axes.linewidth": .7,
    "lines.solid_capstyle": "round",
})
INK = "#212B34"
MUTED = "#58646B"
TEAL = "#245D60"
GOLD = "#9B691F"
LIGHT = "#EEF3F2"
GRID = "#D6E0DE"
HEAT = LinearSegmentedColormap.from_list("komorebi", ["#F2F6F5", "#B6D0CA", TEAL])

def canvas(title, subtitle=None, height=3.9):
    """Use a fixed page box and separate title bands, never tight cropping."""
    fig = plt.figure(figsize=(6.7, height), facecolor="white")
    fig.text(.025, 1-.18/height, title, fontsize=13.5, weight="bold",
             color=TEAL, ha="left", va="top")
    if subtitle:
        fig.text(.025, 1-.49/height, subtitle, fontsize=10,
                 color=MUTED, ha="left", va="top", linespacing=1.25)
    return fig

def clean_axes(ax, grid=True):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(labelsize=10, length=3)
    if grid:
        ax.grid(axis="y", color=GRID, linewidth=.7)
    ax.set_axisbelow(True)

def footer(fig, text):
    fig.text(.025, .035, text, fontsize=9.5, color=MUTED,
             ha="left", va="bottom", linespacing=1.25)

def save(fig, stem):
    OUT.mkdir(exist_ok=True)
    for extension in ("pdf", "png"):
        target = OUT / (stem+"."+extension)
        previous = target.stat().st_mtime if target.exists() else 0
        options = {"dpi": 300} if extension == "png" else {}
        temporary = target.with_name("."+stem+".pending."+extension)
        fig.savefig(temporary, facecolor="white", **options)
        timestamp = max(time.time(), previous+2)
        os.utime(temporary, (timestamp, timestamp))
        os.replace(temporary, target)
    plt.close(fig)
