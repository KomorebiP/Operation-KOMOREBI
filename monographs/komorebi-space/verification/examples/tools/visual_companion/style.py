"""Shared Matplotlib styling for the visual investigations."""
from pathlib import Path
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'source/figures/visual_companion'
OUT.mkdir(parents=True,exist_ok=True)
PINE='#2F6452'; INK='#213B34'; OCHRE='#B27432'; BLUE='#386A94'
MUTED='#66786E'; PALE='#E8EEE8'; RED='#AC4E47'; GRID='#DCE3DC'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,'axes.labelsize':10.5,
 'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'text.color':INK,'axes.labelcolor':INK,
 'axes.edgecolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'axes.spines.top':False,
 'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
 'pdf.fonttype':42,'ps.fonttype':42,'mathtext.fontset':'dejavusans'})

def tidy(ax,grid=True):
    if grid:ax.grid(True,color=GRID,lw=.6,alpha=.8);ax.set_axisbelow(True)
    return ax

def save(fig,name):
    """Persist vector figure and a review preview without automatic cropping."""
    pdf=OUT/(name+'.pdf');png=OUT/(name+'.png')
    fig.savefig(pdf,metadata={'Title':name.replace('_',' '),'Author':'Komorebi P.','Subject':'Komorebi Space visual investigation','CreationDate':None})
    fig.savefig(png,dpi=140)
    plt.close(fig)
    return {'path':str(pdf.relative_to(ROOT)),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}
