"""Regenerate the Smith reading's vector artwork from its retained sources.

Run with Matplotlib 3.10.8, NumPy 2.x and SymPy 1.14. The source ZIP is
verified before its plotting programs are run in a fresh temporary directory.
No archived pickle is loaded. New drawings use the component lists in the
exact nodal generator, not the old illustrative graph.
"""
from __future__ import annotations

import contextlib
import base64
import hashlib
import html
import io
import json
from pathlib import Path
import re
import runpy
import sys
import tempfile
import zipfile

from diagram_redesign import drawings

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ARCHIVE_SHA = '39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
INK, MUTED, GREEN, BLUE, GOLD, RED = '#183831', '#62736c', '#167467', '#396c9c', '#b2742e', '#af4d51'
PALE, LINE = '#eef5f2', '#d8e4de'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def svg(title, description, content, width=1000, height=500):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="'+str(width)+'" height="'+str(height)+
            '" viewBox="0 0 '+str(width)+' '+str(height)+'" role="img" aria-labelledby="title desc">'
            '<title id="title">'+html.escape(title)+'</title><desc id="desc">'+html.escape(description)+'</desc>'
            '<style>text{font-family:Arial,Helvetica,sans-serif;fill:'+INK+'}.muted{fill:'+MUTED+
            '}.title{font-size:26px;font-weight:600}.label{font-size:19px}.small{font-size:16px}'
            '.kicker{font-size:14px;font-weight:700;letter-spacing:1.7px}</style>'
            '<rect width="100%" height="100%" fill="white"/>'+content+'</svg>')


def text(x, y, value, cls='label', **attrs):
    options=' '.join(k.replace('_','-')+'="'+html.escape(str(v), quote=True)+'"' for k,v in attrs.items())
    return f'<text x="{x}" y="{y}" class="{cls}" {options}>{html.escape(value)}</text>'


def line(x1,y1,x2,y2,color=INK,width=2,**attrs):
    options=' '.join(k.replace('_','-')+'="'+str(v)+'"' for k,v in attrs.items())
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {options}/>'


def component(x1,y1,x2,y2,kind,color):
    """An actual R, L or C symbol on a straight branch, including leads."""
    import math
    length=math.hypot(x2-x1,y2-y1)
    angle=math.degrees(math.atan2(y2-y1,x2-x1))
    mid=length/2
    body=line(0,0,mid-22,0,color)+line(mid+22,0,length,0,color)
    if kind=='R':
        body+=f'<rect x="{mid-22}" y="-7" width="44" height="14" fill="white" stroke="{color}" stroke-width="2"/>'
    elif kind=='C':
        body+=line(mid-5,-15,mid-5,15,color,2.5)+line(mid+5,-15,mid+5,15,color,2.5)
        body+=line(mid-22,0,mid-5,0,color)+line(mid+5,0,mid+22,0,color)
    else:
        body+=f'<path d="M {mid-22} 0 '+ ' '.join('a 5.5 8 0 0 1 11 0' for _ in range(4))+f'" fill="none" stroke="{color}" stroke-width="2.3"/>'
    return f'<g transform="translate({x1} {y1}) rotate({angle})">{body}</g>'


def construction_map():
    c=text(42,42,'EXACT SYNTHESIS', 'kicker')+text(42,86,'Seven storage elements; degree six at the port','title')
    for x,label,detail,resistors,color in [(42,'Section A','2 inductors + 1 capacitor','4 positive resistors',GREEN),
                                           (538,'Section B','2 inductors + 2 capacitors','10 positive resistors',BLUE)]:
        c+=f'<rect x="{x}" y="124" width="420" height="172" rx="10" fill="{PALE}" stroke="{LINE}"/>'
        c+=f'<rect x="{x}" y="124" width="5" height="172" rx="2" fill="{color}"/>'
        c+=text(x+24,159,label,'kicker')+text(x+24,199,detail)+text(x+24,232,resistors,'small')
        c+=text(x+24,270,'Reduced input degree 3','small',fill=color)
    c+=line(464,210,536,210,GREEN,2)+text(500,197,'series','small',text_anchor='middle')
    c+=f'<rect x="42" y="332" width="916" height="108" rx="8" fill="#f7f8fa" stroke="{LINE}"/>'
    c+=text(64,365,'ONE COMMON FACTOR IN SECTION B','kicker')
    c+=text(64,402,'N(s) = H(s) T(s)       D(s) = H(s) B(s)')
    c+=text(630,365,'PHYSICAL COUNT','kicker')+text(630,402,'3 + 4 = 7')
    c+=text(808,365,'PORT DEGREE','kicker')+text(808,402,'3 + 3 = 6')
    c+=text(42,477,'The canceled factor hides one internal mode. All seven reactive components remain.','small')
    return svg('Physical storage and observable degree', 'Two passive sections in series use seven reactive elements. A common linear factor reduces section B to degree three.',c)


def exact_graphs():
    import itertools
    c=text(36,42,'COMPONENT TOPOLOGY','kicker')+text(36,82,'The certified seven-reactive circuit','title')
    c+=text(36,116,'Series-connect the two input one-ports. Labels are node numbers.','small')
    # Section A's (1,3) branch is capacitor-only. The old illustration also
    # drew a faint resistor there; generate_exact_systems.py specifies no such R.
    A={0:(78,405),1:(78,210),2:(374,210),3:(374,405)}
    B={0:(576,405),1:(576,210),2:(807,184),3:(936,307),4:(807,429)}
    c+=text(44,160,'A · 3 reactive elements','label',fill=GREEN)+text(542,160,'B · 4 reactive elements','label',fill=BLUE)
    for points,edges in [(A,[(0,2),(0,3),(1,2),(2,3)]),(B,list(itertools.combinations(range(5),2)))]:
        for u,v in edges:
            c+=component(*points[u],*points[v],'R','#aebeb6')
    # Curved independent parallel branches, explicitly labeled by component type.
    branches=[(A,0,3,'L₁',[(78,440),(374,440)],GREEN),
              (A,1,2,'L₂',[(78,177),(374,177)],GREEN),
              (A,1,3,'C₁',[(252,255),(344,365)],BLUE),
              (B,2,4,'L₃',[(730,230),(730,386)],GREEN),
              (B,0,3,'L₄',[(660,390),(885,345)],GREEN),
              (B,3,4,'C₂',[(928,382),(858,442)],BLUE),
              (B,1,2,'C₃',[(640,241),(731,231)],BLUE)]
    for points,u,v,label,midpoints,color in branches:
        x,y=points[u];X,Y=points[v];(p,q),(r,t)=midpoints
        c+=line(x,y,p,q,color,2.4)+component(p,q,r,t,'C' if label.startswith('C') else 'L',color)+line(r,t,X,Y,color,2.4)
        label_positions={'L₃':(704,299),'L₄':(788,392)}
        lx,ly=label_positions.get(label,((p+r)/2,(q+t)/2-17))
        c+=text(lx,ly,label,'small',fill=color,text_anchor='middle')
    for points in (A,B):
        for n,(x,y) in points.items():
            c+=f'<circle cx="{x}" cy="{y}" r="14" fill="white" stroke="{INK}" stroke-width="1.8"/>'
            c+=text(x,y+5,str(n),'small',text_anchor='middle')
    c+=text(44,490,'4 resistors · 2 inductors · 1 capacitor','small')+text(542,490,'10 resistors · 2 inductors · 2 capacitors','small')
    c+=text(44,530,'Gray symbols: resistors','small')+text(350,530,'Green coils: inductors','small')+text(670,530,'Blue plates: capacitors','small')
    return svg('Exact circuit component graphs','Section A has resistors on 02, 03, 12, 23; inductors on 03, 12; capacitor on 13. Section B has resistors on all ten pairs; inductors on 24, 03; capacitors on 34, 12.',c,height=560)


def combiner():
    c=text(42,44,'A DIFFERENT COMPONENT CLASS','kicker')+text(42,88,'Six reactive elements with an ideal transformer','title')
    boxes=[(42,196,190,120,'External port','Reference Z₀',PALE),(302,196,260,120,'Reciprocal combiner','Ideal transformer',PALE),
           (674,126,284,120,'F(s) · degree 2','Series LC · 2 storage elements','#f1f6fa'),
           (674,334,284,120,'H(s) · degree 4','RLC · 4 storage elements','#faf4eb')]
    for x,y,w,h,label,detail,fill in boxes:
        c+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{LINE}"/>'
        c+=text(x+w/2,y+45,label,text_anchor='middle')+text(x+w/2,y+80,detail,'small',text_anchor='middle')
    c+=line(232,256,302,256,GREEN,2.2)+line(562,256,620,256,GREEN,2.2)+line(620,186,620,394,GREEN,2.2)+line(620,186,674,186,GREEN,2.2)+line(620,394,674,394,GREEN,2.2)
    c+=text(42,383,'Reactive count: 2 + 4 = 6','label')+text(42,421,'The ideal transformer is an additional','small')+text(42,447,'static multiport element.','small')
    return svg('Six reactive elements with an ideal transformer','An ideal reciprocal combiner joins a two-state LC section and a four-state RLC section. This construction permits a transformer.',c)


def census():
    c=text(42,42,'FIVE-NODE REACTIVE PLACEMENTS','kicker')+text(42,84,'Graph restrictions reduce the finite catalogue','title')
    stages=[('All labelled placements',14400),('No reactive-only port short',3249),('No same-type reactive cycle',2500),('Both endpoint signs possible',1934)]
    for k,(label,value) in enumerate(stages):
        y=137+74*k
        c+=text(42,y+20,label,'small')
        c+=f'<rect x="325" y="{y}" width="{value/14400*510}" height="30" rx="3" fill="{GREEN if k==3 else BLUE}" opacity="{.55+.15*k}"/>'
        c+=text(345+value/14400*510,y+21,f'{value:,}','small')
    c+=line(42,431,958,431,LINE)+text(42,467,'168 symmetry classes','label',fill=GREEN)+text(380,467,'after internal relabelling and terminal exchange','small')
    c+=text(42,507,'A placement passing these filters still requires positive component values and an exact circuit identity.','small')
    return svg('Exact five-node placement census','14400 labelled placements, 3249 without port shorts, 2500 without same-type cycles, 1934 with both endpoint signs possible; 168 symmetry classes. These are graph counts, not a feasibility proof.',c,height=540)


def kron():
    c=text(42,42,'RESISTOR-ONLY NODE ELIMINATION','kicker')+text(42,84,'The input impedance is preserved exactly','title')
    for dx,label in [(0,'Before: internal resistor node 3'),(500,'After: Kron reduction')]:
        c+=text(42+dx,139,label,'label')
        points={0:(78+dx,382),1:(78+dx,204),2:(395+dx,204),3:(237+dx,296)}
        edges=[(1,3,'2'),(2,3,'3'),(0,3,'5')] if dx==0 else [(1,2,'3/5'),(1,0,'1'),(2,0,'3/2')]
        for u,v,labelvalue in edges:
            x,y=points[u];X,Y=points[v]
            c+=component(x,y,X,Y,'R',MUTED)
            c+=text((x+X)/2+13,(y+Y)/2-14,labelvalue,'small',fill=MUTED)
        # The unaffected inductor and capacitor are shown as separate branches.
        c+=line(78+dx,204,42+dx,204,GREEN)+component(42+dx,204,42+dx,382,'L',GREEN)+line(42+dx,382,78+dx,382,GREEN)
        c+=component(78+dx,382,395+dx,204,'C',BLUE)
        for n in ([0,1,2,3] if dx==0 else [0,1,2]):
            x,y=points[n];c+=f'<circle cx="{x}" cy="{y}" r="13" fill="white" stroke="{INK}" stroke-width="1.7"/>'+text(x,y+5,str(n),'small',text_anchor='middle')
    c+=text(42,442,'Gray labels are conductances. Unchanged branches: C₂₀ = 2 and inductive admittance h₁₀/s = 3/s.','small')
    c+=text(42,478,'Eliminating node 3 adds gᵢ₃ gⱼ₃ / (2 + 3 + 5) between each retained pair.','small')
    return svg('Kron reduction of a resistor-only internal node','A star of conductances 2, 3, 5 is replaced by conductances 3/5, 1, 3/2. The capacitor and inductor branches are unchanged.',c,height=510)


def completion_boundary():
    import math
    def point(x,y):return 500+345*x,315-310*y
    upper=[point(x,(5-math.sqrt(9+16*x*x))/4) for x in [-1+2*k/240 for k in range(241)]]
    lower=[point(x,-(5-math.sqrt(9+16*x*x))/4) for x in [1-2*k/240 for k in range(241)]]
    points=' '.join(f'{x:.3f},{y:.3f}' for x,y in upper+lower)
    c=text(42,42,'SINGULAR INTERPOLATION','kicker')+text(42,85,'Two real packets: the complete feasible region','title')
    for value in [-1,-.5,0,.5,1]:
        x,_=point(value,0);c+=line(x,130,x,500,LINE,1)+text(x,527,str(value),'small',text_anchor='middle')
    for value in [-.5,0,.5]:
        _,y=point(0,value);c+=line(155,y,845,y,LINE,1)+text(132,y+6,str(value),'small',text_anchor='end')
    c+=f'<polygon points="{points}" fill="#dceee4" stroke="{GREEN}" stroke-width="2.5"/>'
    c+=line(155,315,845,315,MUTED,1)+line(500,130,500,500,MUTED,1)
    c+=text(500,343,'Feasible Schur data','label',text_anchor='middle',fill=GREEN)
    c+=text(500,567,'Real even packet p₀','label',text_anchor='middle')
    c+=text(90,305,'p₁','label',text_anchor='middle')
    x,y=point(0,.5);c+=f'<circle cx="{x}" cy="{y}" r="6" fill="{GREEN}"/>'
    X,Y=point(.35,.5);c+=line(x,y,X,Y,RED,2,stroke_dasharray='5 4')+f'<circle cx="{X}" cy="{Y}" r="6" fill="{RED}"/>'
    c+=text(650,149,'Keep p₁ = ½ exactly:','small',fill=RED)+text(650,175,'only p₀ = 0 is feasible.','small',fill=RED)
    c+=text(42,610,'Boundary: |p₁| = (5 − √(9 + 16p₀²)) / 4.','small')
    c+=text(42,645,'Every neighborhood of a saturated tip contains infeasible data.','small')
    return svg('Exact real two-packet feasible region','At radius one half, feasible real packets satisfy absolute p0 at most one and absolute p1 at most (5 minus square root of 9 plus 16 p0 squared) divided by four. The saturated tips force p0 to zero.',c,height=675)


def mobile_map():
    c=text(32,38,'EXACT SYNTHESIS','kicker')+text(32,77,'Seven elements; degree six','title')
    for y,label,detail,resistors in [(112,'SECTION A','2 inductors + 1 capacitor','4 positive resistors'),(327,'SECTION B','2 inductors + 2 capacitors','10 positive resistors')]:
        c+=f'<rect x="32" y="{y}" width="516" height="170" rx="8" fill="{PALE}" stroke="{LINE}"/>'
        c+=text(54,y+35,label,'kicker')+text(54,y+76,detail,'label')+text(54,y+111,resistors,'label')+text(54,y+148,'Reduced input degree 3','label')
    c+=line(290,284,290,324,GREEN,2)+text(311,312,'series','small')
    c+=text(32,551,'One common factor in section B','label')+text(32,591,'Physical count: 3 + 4 = 7','label')+text(32,626,'Port degree: 3 + 3 = 6','label')
    c+=text(32,677,'Cancellation hides an internal mode.','small')+text(32,704,'All seven reactive components remain.','small')
    return svg('Physical storage and observable degree, stacked layout','The two passive sections are in series. Section A has three reactive elements and section B has four. A common factor reduces section B to degree three.',c,width=580,height=735)


def mobile_panels(drawing,title,left,right,labels):
    # Nested SVG viewports reflow the original vector geometry without
    # changing component placement or any numerical plotting coordinates.
    inner=drawing.split('<rect width="100%" height="100%" fill="white"/>',1)[1].rsplit('</svg>',1)[0]
    c=text(28,38,'CIRCUIT STRUCTURE','kicker')+text(28,77,title,'title')
    for y,view,label in [(125,left,labels[0]),(555,right,labels[1])]:
        c+=text(28,y,label,'label')
        c+=f'<svg x="0" y="{y+20}" width="600" height="370" viewBox="{view}" overflow="hidden">'+inner+'</svg>'
    c+=text(28,1005,'Use the full-size view for source values and labels.','small')
    return svg(title+'; stacked layout','The two source panels are arranged vertically for a narrow reading width.',c,width=600,height=1040)


def mobile_census():
    c=text(32,38,'FIVE-NODE PLACEMENTS','kicker')+text(32,78,'The finite graph catalogue','title')
    for k,(label,value) in enumerate([('All labelled placements',14400),('No reactive-only port short',3249),('No same-type reactive cycle',2500),('Both endpoint signs possible',1934)]):
        y=126+k*94;c+=text(32,y,label,'label')
        c+=f'<rect x="32" y="{y+17}" width="{value/14400*440}" height="27" rx="3" fill="{GREEN if k==3 else BLUE}"/>'
        c+=text(48+value/14400*440,y+39,f'{value:,}','small')
    c+=line(32,517,568,517,LINE)+text(32,560,'168 symmetry classes','title')+text(32,597,'Component feasibility still requires an exact solution.','small')
    return svg('Five-node placement census, stacked layout','Four labelled-placement counts lead to 1934 survivors, then 168 symmetry classes. Passing the filters does not prove electrical feasibility.',c,width=600,height=635)


def normalize_svg(data):
    """Restyle a retained hand-authored vector diagram without changing geometry."""
    s=data.decode('utf-8')
    # Preserve every path, coordinate and label; only typography and palette change.
    s=re.sub(r'font-family="[^"]+"','font-family="Arial, Helvetica, sans-serif"',s)
    s=re.sub(r"font-family:\s*[^;\"}]+",'font-family: Arial, Helvetica, sans-serif',s)
    palette={'#FAF8F1':'#ffffff','#faf8f1':'#ffffff','#fdfbf5':'#ffffff',
             '#162e41':INK,'#163449':INK,'#233d32':INK,'#2F5542':GREEN,'#2f5542':GREEN,
             '#406176':MUTED,'#116d78':GREEN,'#0e7283':GREEN,'#b26425':GOLD,'#c1813b':GOLD}
    for old,new in palette.items():s=s.replace(old,new)
    return '\n'.join(row.rstrip() for row in s.splitlines())+'\n'


def main():
    archive=(BASE/'SmithChart_Complete.zip').read_bytes()
    if digest(archive)!=ARCHIVE_SHA:raise ValueError('Archive checksum mismatch')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.text import Text
    from matplotlib.colors import to_hex
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import numpy as np
    from fractions import Fraction
    out=HERE/'figures';out.mkdir(exist_ok=True)
    original_save=Figure.savefig
    generated={}
    sources={}
    palette={'#1f77b4':BLUE,'#ff7f0e':GOLD,'#2ca02c':GREEN,'#d62728':RED,
             '#496a98':BLUE,'#b67a3c':GOLD,'#b45850':RED,'#2f5542':GREEN,
             '#116d78':GREEN,'#0e7283':GREEN,'#b26425':GOLD,'#c1813b':GOLD,
             '#233d32':INK,'#162e41':INK,'#163449':INK,'#163e32':INK,
             '#607066':MUTED,'#637a88':MUTED,'#406176':MUTED,
             '#b6c6ba':LINE,'#a8b9c4':LINE,'#e2e8df':'#e8efeb',
             '#faf8f1':'#ffffff','#fdfbf5':'#ffffff','#fffdf8':'#ffffff'}
    active_source=''
    def recolor(value):
        try:return palette.get(to_hex(value).lower(),value)
        except (ValueError,TypeError):return value
    def save(fig,name,*args,**kwargs):
        p=Path(name)
        if p.suffix=='.png':p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(b'');return
        stem={'19_resistive_mixer_obstruction':'22_resistive_mixer_obstruction',
              '20_kron_node_elimination':'21_kron_node_elimination'}.get(p.stem,p.stem)
        if not re.match(r'\d\d_',stem):raise ValueError('Unexpected plotted file: '+stem)
        if stem in generated:return
        fig.set_facecolor('white')
        for artist in fig.findobj():
            if isinstance(artist,Text):
                artist.set_fontfamily('DejaVu Sans');artist.set_color(recolor(artist.get_color()))
                artist.set_fontsize(max(10,artist.get_fontsize()))
            elif isinstance(artist,Line2D):
                artist.set_color(recolor(artist.get_color()))
            elif isinstance(artist,Patch):
                for prop in ('facecolor','edgecolor'):
                    getter=getattr(artist,'get_'+prop,None);setter=getattr(artist,'set_'+prop,None)
                    if getter and setter:
                        try:setter(recolor(getter()))
                        except (TypeError,ValueError):pass
        for ax in fig.axes:
            ax.set_facecolor('white')
            ax.title.set_fontsize(13);ax.title.set_fontweight('semibold')
            if ax.axison:
                for side in ('top','right'):ax.spines[side].set_visible(False)
                for side in ('bottom','left'):ax.spines[side].set_color(LINE)
                ax.tick_params(length=3,color=LINE,labelsize=10)
                ax.xaxis.label.set_fontsize(11);ax.yaxis.label.set_fontsize(11)
        if stem=='07_matrix_pick_certificates':
            for ax in fig.axes:
                for item in ax.texts:
                    if item.get_text().startswith('The negative eigenvalues'):
                        item.set_visible(False)
            fig.text(.5,.015,'Negative eigenvalues reject the jointly specified data.',ha='center',fontsize=10,color=MUTED)
            fig.subplots_adjust(bottom=.16)
        dest=out/(stem+'.svg')
        matplotlib.rcParams['svg.fonttype']='none'
        matplotlib.rcParams['svg.hashsalt']='smith-reading-edition-2026-11'
        original_save(fig,dest,format='svg',bbox_inches='tight',pad_inches=.22,facecolor='white',metadata={'Date':None,'Creator':'Smith chart reading edition; archived equations'})
        generated[stem]=dest.name;sources[stem]=active_source
    Figure.savefig=save
    scripts=['earlier_core/smith_extended_figures_full.py','earlier_core/smith_realization_figures.py',
             'earlier_core/smith_order_growth_figures.py','earlier_core/smith_transformerfree_figures.py',
             'six_state/smith_q6_invariant_figures.py',
             'double_extraction/current_work/smith_q6_pole_split_figures.py',
             'double_extraction/current_work/smith_q6_double_extraction_figures.py',
             'coupled_continuation/coupled_continuation/smith_q6_anchor_figures.py',
             'exact_cubic_continuation/make_cubic_figures.py']
    with tempfile.TemporaryDirectory(prefix='smith-figure-edition-') as temporary:
        scratch=Path(temporary)
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            for info in z.infolist():
                parts=Path(info.filename).parts
                if '..' in parts or Path(info.filename).is_absolute():raise ValueError('Unsafe ZIP path')
                dest=scratch.joinpath(*parts);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(info))
        root=scratch/'Smith_Chart_Research_2026-11-11'
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path((root/'reproduction/earlier_core/smith_realization_checks.py').as_posix(),run_name='__main__')
        for item in scripts:
            active_source='reproduction/'+item
            plt.rcdefaults();plt.rcParams['svg.fonttype']='none'
            with contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path((root/active_source).as_posix(),run_name='__main__')
            plt.close('all')
            print('rendered',item,flush=True)
        # Rebuild the pole-zero illustration directly from rational center values
        # and the exact graph's spanning-tree polynomials; never load a pickle.
        active_source='reproduction/exact_seven/src/generate_exact_systems.py'
        data=root/'reproduction/exact_seven/data'
        solution=json.loads((data/'dark_solution_high_precision.json').read_text())['approximations_160digits']
        y=[float(v) for v in solution];s0=y[14]
        # The reduced cubic factors are stored with the independently checked
        # cubic solution. Its rounded centers are only used to locate markers.
        cubic=json.loads((data/'original_cubic_high_precision.json').read_text())
        vals=[float(v) for v in cubic['components_160digits']]
        B=[1,vals[5],vals[4],vals[3]]
        T=[.8,.8*vals[5]+vals[11],.8*vals[4]+vals[10],.8*vals[3]+vals[9]]
        zeros=np.r_[np.roots(T),s0];poles=np.r_[np.roots(B),s0]
        fig,ax=plt.subplots(figsize=(10,5.1))
        ax.axhline(0,color=LINE,lw=1);ax.axvline(0,color=LINE,lw=1)
        ax.scatter(zeros.real,zeros.imag,facecolors='white',edgecolors=GREEN,s=105,lw=2,label='Numerator zeros',zorder=3)
        ax.scatter(poles.real,poles.imag,marker='x',color=GOLD,s=100,lw=2,label='Denominator poles',zorder=4)
        ax.scatter([s0],[0],s=430,facecolors='none',edgecolors=RED,lw=1.6)
        ax.annotate('One exact common factor\nHidden at the input port',(s0,0),xytext=(-1,-.8),color=INK,ha='center',arrowprops={'arrowstyle':'-','color':RED})
        ax.set(xlim=(-1.62,.16),ylim=(-1.42,1.42),xlabel='Real part of s',ylabel='Imaginary part of s',title='Four physical states; a cubic input impedance')
        ax.legend(frameon=False,loc='upper left');fig.tight_layout();save(fig,'40_dark_pole_cancellation.svg');plt.close(fig)
    Figure.savefig=original_save
    # Hand-authored vector diagrams with unchanged archived geometry.
    for p in (BASE/'figures').glob('*.svg'):
        if p.stem not in generated:
            (out/p.name).write_text(normalize_svg(p.read_bytes()),encoding='utf-8',newline='\n')
            generated[p.stem]=p.name;sources[p.stem]='figures/'+p.name
    for stem,drawing,source in [
        ('17_six_state_ideal_combiner',combiner(),'figures/17_six_state_ideal_combiner.svg'),
        ('21_kron_node_elimination',kron(),'reproduction/earlier_core/smith_transformerfree_figures.py'),
        ('25_five_node_exact_topology_pruning',census(),'reproduction/six_state/smith_q6_graph_pruning.json'),
        ('39_seven_reactive_graphs',exact_graphs(),'reproduction/exact_seven/src/generate_exact_systems.py'),
        ('41_storage_and_observable_order',construction_map(),'reproduction/make_reading_map.py')]:
        (out/(stem+'.svg')).write_text(drawing,encoding='utf-8',newline='\n');generated[stem]=stem+'.svg';sources[stem]=source
    mobile={
        '41_storage_and_observable_order':mobile_map(),
        '39_seven_reactive_graphs':mobile_panels(exact_graphs(),'Certified component graphs','20 170 450 330','530 170 450 330',('A · 2 inductors, 1 capacitor, 4 resistors','B · 2 inductors, 2 capacitors, 10 resistors')),
        '21_kron_node_elimination':mobile_panels(kron(),'Exact Kron reduction','15 170 440 270','515 170 440 270',('Before: resistor-only node 3','After: node 3 is eliminated')),
        '25_five_node_exact_topology_pruning':mobile_census(),
    }
    redesigned = drawings()
    for stem, (draw, source) in redesigned.items():
        (out/(stem+'.svg')).write_text(draw(),encoding='utf-8',newline='\n')
        generated[stem]=stem+'.svg'
        sources[stem]=source
        mobile[stem]=draw(mobile=True)
    for stem,drawing in mobile.items():(out/(stem+'.mobile.svg')).write_text(drawing,encoding='utf-8',newline='\n')
    # A clean analytic error chart, with exact Fraction values from (A5).
    matplotlib.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'svg.fonttype':'none','svg.hashsalt':'smith-reading-edition-2026-11'})
    n=np.arange(4,41);errors=np.array([float(Fraction(44,81)*Fraction(1,3**(int(i)-2))/(1-Fraction(1,3**int(i)))) for i in n])
    fig,ax=plt.subplots(figsize=(10,5.4))
    ax.semilogy(n,errors,color=GREEN,lw=2.4,marker='o',ms=4,label='Sharp full-disk reflection error')
    ax.semilogy(n,44/81*3.0**(-(n-2)),color=GOLD,lw=1.6,ls='--',label='Exponential leading term')
    for k in (10,20,30):
        ax.annotate(f'N = {k}  ·  {errors[k-4]:.2g}',(k,errors[k-4]),xytext=(10,15),textcoords='offset points',fontsize=11,color=INK)
    ax.set(xlim=(3,41),ylim=(1e-20,1),xlabel='Exact reactive-order lower bound N',ylabel='Uniform reflection error',title='One passive RL circuit approximates every order')
    ax.grid(axis='y',color=LINE,lw=.7);ax.legend(frameon=False,loc='lower left',fontsize=11)
    for side in ('top','right'):ax.spines[side].set_visible(False)
    fig.tight_layout();dest=out/'42_exponential_order_gap.svg';original_save(fig,dest,bbox_inches='tight',facecolor='white',metadata={'Date':None});plt.close(fig)
    generated[dest.stem]=dest.name;sources[dest.stem]='reproduction/new_order_separation/plot_order_gap.py'
    # SVG text needs a browser-available fallback, even when Matplotlib's
    # own DejaVu font was available during generation.
    for p in out.glob('*.svg'):
        p.write_text(normalize_svg(p.read_bytes()),encoding='utf-8',newline='\n')
    supplement=HERE.parents[2]/'docs/demonstrations/figures/smith-two-packet-feasibility.svg'
    supplement.write_text(completion_boundary(),encoding='utf-8',newline='\n')
    records=[]
    original_files={}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for name in z.namelist():original_files[name.split('/',1)[1]]=z.read(name)
    figure_hashes={digest(value):name for name,value in original_files.items() if name.startswith('figures/')}
    html_source=original_files['Smith_Chart_Extended_Seven_Reactive_Exact.html'].decode('utf-8')
    names=[figure_hashes[digest(base64.b64decode(data))] for data in
           re.findall(r'src="data:image/(?:png|svg\+xml);base64,([A-Za-z0-9+/=]+)"',html_source)]
    if len(names)!=42 or len(set(names))!=42:raise AssertionError('Unexpected embedded figure identities')
    for name in sorted(names):
        p=BASE/name
        target=out/generated[p.stem];src=sources[p.stem]
        item={'original':name,'original_sha256':digest(p.read_bytes()),
                        'edition':'edition/figures/'+target.name,'edition_sha256':digest(target.read_bytes()),
                        'source':src,'source_sha256':digest(original_files[src]),
                        'method':('structural redraw from archived circuit or certificate' if p.stem in redesigned else
                                  'component-list redraw' if p.stem in {'17_six_state_ideal_combiner','21_kron_node_elimination','25_five_node_exact_topology_pruning','39_seven_reactive_graphs','41_storage_and_observable_order'} else
                                  'archived-equation rendering or geometry-preserving restyle')}
        if p.stem in mobile:
            mob=out/(p.stem+'.mobile.svg')
            item.update(mobile_edition='edition/figures/'+mob.name,mobile_sha256=digest(mob.read_bytes()))
        records.append(item)
    if len(records)!=42:raise AssertionError('Expected exactly 42 source figure identities')
    manifest={'archive_sha256':ARCHIVE_SHA,'generator_sha256':digest(Path(__file__).read_bytes()),
              'diagram_generator_sha256':digest((HERE/'diagram_redesign.py').read_bytes()),
              'matplotlib':matplotlib.__version__,'numpy':np.__version__,
              'scope':'Vector presentation edition. Plots illustrate the archived mathematics; they are not new proof certificates.',
              'additional_figures':[{'repository_path':'docs/demonstrations/figures/smith-two-packet-feasibility.svg','sha256':digest(supplement.read_bytes())}],
              'corrections':['Figure 39 section A: remove the spurious faint resistor on capacitor-only edge (1,3), following the exact nodal generator.'],
              'figures':records}
    (HERE/'figures.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS: 42 vector figures and source bindings')


if __name__=='__main__':main()
