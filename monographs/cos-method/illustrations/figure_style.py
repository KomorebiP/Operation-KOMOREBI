"""Publication figure grammar for the K-COS monograph.

Each output is a separate vector figure. Colors are paired with line styles,
markers, or explicit labels. Do not use this module to change measured values.
"""
from pathlib import Path
import hashlib
import json
import warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.ticker import ScalarFormatter, LogLocator, NullLocator, MaxNLocator
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'book/figures_production'
QA = ROOT/'verification/figure_pass'
OUT.mkdir(exist_ok=True); QA.mkdir(parents=True, exist_ok=True)
EXACT = '#403348'
APPROX = '#34777A'
BOUND = '#9D742D'
FAIL = '#A24E46'
GRAY = '#706D75'
RULE = '#DAD6DD'
PALE = '#F4F1F5'
INK = '#302D34'
COLORS=[EXACT,APPROX,BOUND,FAIL]
MARKERS=['o','s','D','^']
STYLES=['-','--','-.',':']
plt.rcParams.update({
 'font.family':'DejaVu Sans','font.size':9.5,'mathtext.fontset':'dejavuserif',
 'axes.labelsize':9.4,'xtick.labelsize':8.5,'ytick.labelsize':8.5,
 'axes.labelcolor':INK,'text.color':INK,'axes.edgecolor':RULE,
 'xtick.color':GRAY,'ytick.color':GRAY,'axes.linewidth':.65,
 'axes.spines.top':False,'axes.spines.right':False,
 'axes.axisbelow':True,'axes.grid':False,'grid.color':RULE,'grid.linewidth':.55,
 'lines.linewidth':1.65,'lines.markersize':4.7,
 'legend.fontsize':8.2,'legend.frameon':False,'legend.handlelength':2.4,
 'savefig.facecolor':'white','figure.facecolor':'white',
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
 'axes.formatter.use_mathtext':True,'axes.unicode_minus':True,
 'hatch.linewidth':.45,
})
RECORDS=[]

def canvas(title, tag='RECORDED CONTROL', note='', *, height=3.5, rect=None, diagram=False):
    fig=plt.figure(figsize=(6.37,height))
    fig.text(.035,.965,tag,fontsize=7.1,fontweight='bold',color=APPROX,va='top')
    fig.text(.035,.895,title,fontsize=12.0,fontweight='medium',color=EXACT,va='top')
    if diagram:
        ax=fig.add_axes([.035,.12,.93,.64]); ax.set(xlim=(0,10),ylim=(0,5)); ax.axis('off')
    else:
        ax=fig.add_axes(rect or [.135,.22,.81,.54])
        ax.grid(axis='y',color=RULE,linewidth=.55)
        ax.tick_params(length=3,width=.6,pad=4)
        ax.minorticks_off()
    if note: fig.text(.035,.025,note,fontsize=7.8,color=GRAY,va='bottom',linespacing=1.35)
    return fig,ax

def legend(ax, ncol=2, *, anchor=(0,1.02), fontsize=8.1):
    handles,labels=ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles,labels,loc='lower left',bbox_to_anchor=anchor,ncol=ncol,
                  borderaxespad=0,columnspacing=1.5,handletextpad=.6,fontsize=fontsize)

def series(ax,x,y,label='',index=0,**kw):
    spec=dict(color=COLORS[index%4],marker=MARKERS[index%4],ls=STYLES[index%4],
              markerfacecolor='white',markeredgewidth=1.2,label=label)
    spec.update(kw)
    return ax.plot(x,y,**spec)

def sci(ax,axis='y'):
    ax.ticklabel_format(axis=axis,style='sci',scilimits=(0,0),useMathText=True)

def logaxis(ax,axis='y'):
    getattr(ax,'set_'+axis+'scale')('log')
    getattr(ax,axis+'axis').set_major_locator(LogLocator(base=10,numticks=6))
    getattr(ax,axis+'axis').set_minor_locator(NullLocator())

def callout(ax,text,xy,xytext,**kw):
    spec=dict(ha='left',va='center',fontsize=8.2,color=INK,
       arrowprops=dict(arrowstyle='-',lw=.75,color=GRAY),
       bbox=dict(facecolor='white',edgecolor='none',pad=2))
    spec.update(kw);return ax.annotate(text,xy=xy,xytext=xytext,**spec)

def number(ax,x,y,text,*,color=INK,ha='center',va='center',size=9.4,weight='normal',**kw):
    return ax.text(x,y,text,ha=ha,va=va,fontsize=size,color=color,fontweight=weight,**kw)

def card(ax,x,y,w,h,title,body='',color=EXACT,small=False):
    ax.add_patch(Rectangle((x,y),w,h,fc='white',ec=RULE,lw=.7))
    ax.add_patch(Rectangle((x,y+h-.06),w,.06,fc=color,ec='none'))
    number(ax,x+.15,y+h-.28,title,color=color,ha='left',va='top',size=9.0 if small else 10.0,weight='bold')
    if body: number(ax,x+.15,y+h-.95,body,ha='left',va='top',size=8.2,linespacing=1.65)

def arrow(ax,a,b,color=GRAY,lw=1.1,style='-|>'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=10,color=color,lw=lw))

def matrix(ax,M,xy,size=1.6,label='',vmax=None,negative=False):
    M=np.asarray(M);nr,nc=M.shape;vmax=vmax or max(1,np.max(abs(M)))
    for i in range(nr):
      for j in range(nc):
        v=float(M[i,j]);c=FAIL if v<0 else APPROX
        ax.add_patch(Rectangle((xy[0]+j*size/nc,xy[1]+(nr-i-1)*size/nr),size/nc,size/nr,
            facecolor=c if v else PALE,alpha=(.18+.82*abs(v)/vmax) if v else 1,
            edgecolor='white',lw=.45))
    ax.add_patch(Rectangle(xy,size,size,fill=False,ec=RULE,lw=.5))
    if label:number(ax,xy[0]+size/2,xy[1]+size+.28,label,size=11,color=EXACT)

def save(fig,stem,*,sources=(),scope='',checks=None,caption=''):
    """Save full-page vector content and a preview; fail on off-canvas text."""
    # Reserve a measurable gap between the title and an outside legend.
    # Multiple legend rows must not consume the title band.
    fig.canvas.draw()
    title = fig.texts[1] if len(fig.texts)>1 else None
    if title is not None:
        for ax in fig.axes:
            leg=ax.get_legend()
            if leg is None: continue
            renderer=fig.canvas.get_renderer()
            tb=title.get_window_extent(renderer); lb=leg.get_window_extent(renderer)
            gap=5*fig.dpi/72
            overlap=lb.y1-(tb.y0-gap)
            if overlap>0:
                pos=ax.get_position()
                delta=overlap/fig.bbox.height
                ax.set_position([pos.x0,pos.y0,pos.width,pos.height-delta])
                fig.canvas.draw()
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer(); bounds=fig.bbox
    outside=[]
    ignored=set()
    for axis in fig.axes:
        for coord,lim in [(axis.xaxis,axis.get_xlim()),(axis.yaxis,axis.get_ylim())]:
            lo,hi=sorted(lim)
            for tick in coord.get_major_ticks()+coord.get_minor_ticks():
                if not lo<=tick.get_loc()<=hi:
                    ignored.update([id(tick.label1),id(tick.label2)])
    for artist in fig.findobj(matplotlib.text.Text):
        if id(artist) in ignored or not artist.get_visible() or not artist.get_text().strip(): continue
        # Clipped tick labels need not lie in the canvas when their tick is outside the view.
        bbox=artist.get_window_extent(renderer)
        if bbox.width<=0 or bbox.height<=0:continue
        if bbox.x0 < -1.5 or bbox.x1>bounds.x1+1.5 or bbox.y0< -1.5 or bbox.y1>bounds.y1+1.5:
            outside.append(artist.get_text())
    if outside: raise ValueError(f'{stem}: text outside figure: {outside}')
    clipped=[]
    data_points=0
    for ax in fig.axes:
        if not ax.axison: continue
        xlo,xhi=sorted(ax.get_xlim());ylo,yhi=sorted(ax.get_ylim())
        tx=(xhi-xlo)*1e-8;ty=(yhi-ylo)*1e-8
        arrays=[]
        for ln in ax.lines:
            if ln.get_transform()==ax.transData:
                arrays.append((np.asarray(ln.get_xdata(orig=False),dtype=float),np.asarray(ln.get_ydata(orig=False),dtype=float)))
        for col in ax.collections:
            if isinstance(col,matplotlib.collections.PathCollection):
                pts=np.asarray(col.get_offsets(),dtype=float)
                if pts.ndim==2 and pts.shape[1]==2: arrays.append((pts[:,0],pts[:,1]))
        for xx,yy in arrays:
            finite=np.isfinite(xx)&np.isfinite(yy)
            data_points+=int(finite.sum())
            mask=finite&((xx<xlo-tx)|(xx>xhi+tx)|(yy<ylo-ty)|(yy>yhi+ty))
            if mask.any():clipped.extend(zip(xx[mask].tolist(),yy[mask].tolist()))
    if clipped: raise ValueError(f'{stem}: data outside axes: {clipped[:8]}')
    meta={'Title':caption or stem,'Author':'Komorebi P.','Subject':scope,'Creator':'Matplotlib / K-COS publication figure source'}
    fig.savefig(OUT/(stem+'.pdf'),metadata=meta)
    fig.savefig(OUT/(stem+'.svg'))
    fig.savefig(OUT/(stem+'.png'),dpi=160)
    plt.close(fig)
    src=[]
    for s in sources:
        p=Path(s) if Path(s).is_absolute() else ROOT/s
        src.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    RECORDS.append({'figure':stem,'scope':scope,'sources':src,'checks':checks or {},'caption':caption,
                    'canvas_inches':[6.37,float(fig.get_figheight())],'text_bounds':'pass','data_bounds':'pass','line_scatter_points_checked':data_points})

def manifest():
    (QA/'figure_manifest.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
