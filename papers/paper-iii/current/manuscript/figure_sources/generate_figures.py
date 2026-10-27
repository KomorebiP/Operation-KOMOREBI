#!/usr/bin/env python3
"""Regenerate six exact Paper III figures as fixed-width vector PDF/PNG pairs.

Usage: python3 editable/traditional/figure_sources/generate_figures.py
Only the two new finite models are plotted numerically; all identities are
checked symbolically or with Fraction before authoring begins.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import matplotlib
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, Arc
from matplotlib.text import Text
from common import INK, MUTED, TEAL, GOLD, LIGHT, GRID, OUT, canvas, footer, save
from models import DATA, exact_checks, sp

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
QA = ROOT / 'tmp' / 'figure_qa'
LAYOUT = []


def panel(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')


def text(ax, x, y, label, size=10.5, color=INK, weight='normal', ha='center', va='center', **kwargs):
    return ax.text(x, y, label, fontsize=size, color=color, weight=weight,
                   ha=ha, va=va, linespacing=1.3, **kwargs)


def node(ax, xy, label, radius=.061, color=TEAL):
    ax.add_patch(Circle(xy, radius, facecolor='white', edgecolor=color, lw=1.5, zorder=4))
    text(ax, *xy, label, size=11, color=color, weight='bold', zorder=5)


def arrow(ax, start, end, label=None, color=TEAL, shrink=0, label_xy=None, dashed=False):
    patch = FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=12,
                            color=color, lw=1.5, shrinkA=shrink, shrinkB=shrink,
                            linestyle=(0, (3, 2)) if dashed else '-', zorder=2)
    ax.add_patch(patch)
    if label:
        if label_xy is None:
            label_xy = ((start[0]+end[0])/2, (start[1]+end[1])/2+.09)
        text(ax, *label_xy, label, color=color, size=10)
    return patch


def box(ax, xy, width, height, face=LIGHT, edge='none'):
    ax.add_patch(Rectangle(xy, width, height, facecolor=face, edgecolor=edge, lw=.7, zorder=0))


def emit(fig, stem):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    artists = []
    for a in fig.findobj(Text):
        if a.get_visible() and a.get_text().strip() and a not in artists:
            artists.append(a)
    bounds = []
    overlaps = []
    for a in artists:
        b = a.get_window_extent(renderer)
        if b.x0 < 0 or b.y0 < 0 or b.x1 > W or b.y1 > H:
            bounds.append(a.get_text())
    for i, a in enumerate(artists):
        ba = a.get_window_extent(renderer)
        for b in artists[i+1:]:
            bb = b.get_window_extent(renderer)
            dx = min(ba.x1, bb.x1)-max(ba.x0, bb.x0)
            dy = min(ba.y1, bb.y1)-max(ba.y0, bb.y0)
            if dx > 1.2 and dy > 1.2:
                overlaps.append([a.get_text(), b.get_text()])
    LAYOUT.append({'figure': stem, 'width_inches': 6.7, 'height_inches': fig.get_size_inches()[1],
                   'text_outside_page': bounds, 'text_overlap_candidates': overlaps})
    if bounds or overlaps:
        raise AssertionError(f'{stem}: bounds={bounds}, overlaps={overlaps}')
    save(fig, stem)


def typed_edge_walks():
    fig = canvas('Typed edge words and directed packet walks',
                 'Target row, source column. The rightmost edge acts first.', height=4.0)
    left = fig.add_axes([.035, .22, .445, .55]); panel(left)
    right = fig.add_axes([.545, .22, .42, .55]); panel(right)
    text(left, .5, .98, 'Composable word', size=11, color=TEAL, weight='bold')
    pts = [(.075+i*.28, .63) for i in range(4)]
    for i, p in enumerate(pts): node(left, p, rf'$P_{i}$')
    for i in range(3):
        arrow(left, (pts[i][0]+.067, .63), (pts[i+1][0]-.067, .63),
              rf'$e_{i+1}$', label_xy=((pts[i][0]+pts[i+1][0])/2, .78))
    box(left, (.02, .15), .96, .25)
    text(left, .5, .31, r'$L_{e_3}L_{e_2}L_{e_1}$', size=13, color=TEAL)
    text(left, .5, .19, r'Executes $e_1$, then $e_2$, then $e_3$.', size=9.5)
    text(left, .5, .035, r'Only the $(3,0)$ endpoint block survives.', size=9.5, color=MUTED)
    text(right, .5, .98, 'Broken interface', size=11, color=TEAL, weight='bold')
    for p, lab in [((.13, .72), r'$P_i$'), ((.86, .72), r'$P_j$'),
                   ((.13, .41), r'$P_\ell$'), ((.86, .41), r'$P_k$')]:
        node(right, p, lab, color=GOLD if 'ell' in lab or 'k' in lab else TEAL)
    arrow(right, (.20, .72), (.79, .72), '$e$', label_xy=(.49,.84))
    arrow(right, (.20, .41), (.79, .41), '$f$', color=GOLD, label_xy=(.49,.53))
    text(right, .92, .565, r'$j\ne\ell$', size=10, color=GOLD)
    box(right, (.08, .11), .84, .19)
    text(right, .5, .21, r'$L_fL_e=0$', size=14, color=GOLD)
    text(right, .5, .035, 'One mismatched interface kills the product.', size=9.3, color=MUTED)
    fig.lines.append(matplotlib.lines.Line2D([.51,.51],[.24,.77], transform=fig.transFigure, color=GRID, lw=.8))
    footer(fig, 'Directions follow packet types. A surviving product retains its outer source and target.')
    emit(fig, 'typed_edge_walks')


def triangle(ax, prefix, color):
    panel(ax)
    p = {'a': (.15,.23), 'b': (.85,.23), 'c': (.5,.91)}
    for lab, xy in p.items(): node(ax, xy, lab, radius=.067, color=color)
    arrow(ax, (.225,.23), (.775,.23), rf'${prefix}_{{b\leftarrow a}}$', color=color, label_xy=(.5,.09))
    arrow(ax, (.812,.303), (.538,.837), rf'${prefix}_{{c\leftarrow b}}$', color=color, label_xy=(.84,.64))
    arrow(ax, (.462,.837), (.188,.303), rf'${prefix}_{{a\leftarrow c}}$', color=color, label_xy=(.16,.64))


def transport_vs_connection():
    fig = canvas('Exact coordinate transport and chosen connection data',
                 'The same directed loop carries two different kinds of transport.', height=4.6)
    for x, label in [(.035,'Canonical coordinate transport'),(.535,'Chosen connection')]:
        fig.text(x+.21,.785,label, ha='center', fontsize=11, color=TEAL if x<.1 else GOLD, weight='bold')
    left = fig.add_axes([.035,.375,.43,.36]); triangle(left,'J',TEAL)
    right = fig.add_axes([.535,.375,.43,.36]); triangle(right,r'\Gamma',GOLD)
    bottom_l = fig.add_axes([.04,.12,.425,.19]); panel(bottom_l)
    bottom_r = fig.add_axes([.535,.12,.425,.19]); panel(bottom_r)
    box(bottom_l,(0,0),1,1)
    box(bottom_r,(0,0),1,1)
    text(bottom_l,.5,.72,r'$J_{a\leftarrow c}J_{c\leftarrow b}J_{b\leftarrow a}=\mathrm{id}$',size=11,color=TEAL)
    text(bottom_l,.5,.31,'Exact analysis and synthesis\nforce the factors to telescope.',size=9.5,color=MUTED)
    text(bottom_r,.5,.75,r'$H_{c,b,a}=\Gamma_{a\leftarrow c}\Gamma_{c\leftarrow b}\Gamma_{b\leftarrow a}$',size=10.6,color=GOLD)
    text(bottom_r,.5,.36,r'$H^G=G_aHG_a^{-1}$',size=11)
    fig.lines.append(matplotlib.lines.Line2D([.5,.5],[.15,.8],transform=fig.transFigure,color=GRID,lw=.8))
    footer(fig,'Canonical loops are identities. Connection holonomy is additional data and changes by conjugation.')
    emit(fig,'transport_vs_connection')


def holonomy_obstruction_blocks():
    fig = canvas('Holonomy obstruction resolved by packets',
                 'Complete projectors resolve both input and output. Off diagonal blocks record mixing.',height=4.8)
    ax = fig.add_axes([.09,.265,.37,.47]); panel(ax)
    n=4; cell=.225; origin=.10
    for row in range(n):
        for col in range(n):
            x=origin+col*cell; y=origin+(3-row)*cell
            hi=(row,col)==(1,3)
            ax.add_patch(Rectangle((x,y),cell,cell,facecolor='#F3E9D6' if hi else LIGHT,
                                   edgecolor=GOLD if hi else 'white',lw=1.5))
            text(ax,x+cell/2,y+cell/2,rf'$\mathrm{{Ob}}^{{{row}{col}}}$',size=10,color=GOLD if hi else INK)
    for i in range(n):
        text(ax,origin+(i+.5)*cell,.035,rf'${i}$',size=9.5,color=MUTED)
        text(ax,.052,origin+(3-i+.5)*cell,rf'${i}$',size=9.5,color=MUTED)
    fig.text(.283,.22,r'Input packet $\nu$',fontsize=10,ha='center',color=MUTED)
    fig.text(.029,.51,r'Output packet $\mu$',fontsize=10,rotation=90,ha='center',va='center',color=MUTED)
    ax.set_xlim(0,1.015); ax.set_ylim(0,1.015)
    right = fig.add_axes([.545,.265,.42,.47]); panel(right)
    text(right,.5,.95,'Reconstruction and detection',size=11,color=TEAL,weight='bold')
    for y,line in [(.73,r'$\mathrm{Ob}=H-\mathrm{id}$'),
                   (.47,r'$\mathrm{Ob}^{\mu\nu}=\Pi_\mu\mathrm{Ob}\Pi_\nu$'),
                   (.20,r'$\mathrm{Ob}=\sum_{\mu,\nu}\mathrm{Ob}^{\mu\nu}$')]:
        box(right,(.01,y-.10),.98,.2)
        text(right,.5,y,line,size=13,color=TEAL)
    band = fig.add_axes([.075,.105,.89,.095]); panel(band)
    text(band,.5,.78,r'If $\mathrm{Ob}^{13}\ne0$: an input in packet $3$ has a nonzero output in packet $1$.',size=10,color=GOLD)
    text(band,.5,.28,'All blocks vanish if and only if the total obstruction vanishes.',size=10,color=INK)
    footer(fig,'The highlighted block is a conditional mixing witness. Shading does not assign numerical block values.')
    emit(fig,'holonomy_obstruction_blocks')


def hessian_grid(ax, matrix, output):
    panel(ax)
    text(ax,.5,.98,f'Output {output}',size=11,color=TEAL,weight='bold')
    origin=.24; size=.27
    for row in range(2):
        for col in range(2):
            x=origin+col*size; y=.19+(1-row)*size
            v=matrix[row][col]
            ax.add_patch(Rectangle((x,y),size,size,facecolor=TEAL if v else LIGHT,edgecolor='white',lw=2))
            text(ax,x+size/2,y+size/2,str(v),size=16,color='white' if v else MUTED,weight='bold' if v else 'normal')
    for i,lab in enumerate(['x','y']):
        text(ax,.15,.19+(1-i+.5)*size,rf'${lab}$',size=10,color=MUTED)
        text(ax,origin+(i+.5)*size,.105,rf'${lab}$',size=10,color=MUTED)
    text(ax,.51,.84,rf'$H_{output}$',size=12)


def packet_jet_worked_example():
    fig = canvas('An exact jet model with two packets',
                 r'$F(x,y)=(x+xy,\ y+x^2)$ at $(0,0)$. Coordinate packets in both input and output.',height=5.15)
    fig.text(.05,.785,r'$DF(0)=I:\quad DF(0)e_x=(1,0),\qquad DF(0)e_y=(0,1).$',fontsize=11)
    left = fig.add_axes([.06,.385,.40,.33]); hessian_grid(left,DATA['packet_jets']['H1'],1)
    right = fig.add_axes([.55,.385,.40,.33]); hessian_grid(right,DATA['packet_jets']['H2'],2)
    fig.text(.26,.355,r'$D^2F_1(0)[e_x,e_y]=D^2F_1(0)[e_y,e_x]=1$',ha='center',fontsize=9.6,color=TEAL)
    fig.text(.75,.355,r'$D^2F_2(0)[e_x,e_x]=2$',ha='center',fontsize=10.4,color=TEAL)
    ax=fig.add_axes([.055,.105,.90,.205]); panel(ax); box(ax,(0,0),1,1)
    text(ax,.5,.81,r'$D^2F(0)[h,k]=(h_xk_y+h_yk_x,\ 2h_xk_x)$',size=12,color=TEAL)
    text(ax,.5,.49,r'$\frac{1}{2} D^2F(0)[h,h]=(h_xh_y,\ h_x^2)$',size=12)
    text(ax,.5,.18,r'$F(h)=h+\frac{1}{2}D^2F(0)[h,h]$ exactly. All higher jets vanish.',size=10.7)
    footer(fig,'Cells are ordered Hessian responses: the two mixed slots and the Taylor factor 1/2 are both retained.')
    emit(fig,'packet_jet_worked_example')


def correction_cokernel_plane():
    fig=canvas('Correctable defect and cokernel residual',
               r'$L:\mathbb{R}^2\to\mathbb{R}^2$, $L(a,b)=(a,0)$. Defect $d=(2,3)$.',height=4.7)
    ax=fig.add_axes([.08,.265,.455,.48])
    ax.set_xlim(-.5,3.0);ax.set_ylim(-.45,3.7);ax.set_aspect('equal');ax.axis('off')
    ax.add_patch(Rectangle((-.5,-.12),3.5,.24,facecolor=LIGHT,zorder=0))
    arrow(ax,(-.45,0),(2.85,0),color=TEAL)
    arrow(ax,(0,-.35),(0,3.55),color=GRID)
    arrow(ax,(0,0),(2,3),color=INK)
    arrow(ax,(0,0),(2,0),color=TEAL)
    arrow(ax,(0,0),(0,3),color=GOLD)
    ax.plot([0,2],[3,3],color=GRID,lw=1.2,linestyle=(0,(3,2)))
    ax.plot([2,2],[0,3],color=GOLD,lw=1.2,linestyle=(0,(3,2)))
    ax.scatter([0,2,2],[3,0,3],s=17,c=[GOLD,TEAL,INK],zorder=5)
    text(ax,2.15,3.15,r'$d=(2,3)$',size=10,ha='left')
    text(ax,1.45,-.27,r'$d_{\rm im}=(2,0)$',size=10,color=TEAL)
    text(ax,-.18,2.5,r'$d_\perp=(0,3)$',size=10,color=GOLD,ha='right')
    text(ax,2.7,.25,r'$\mathrm{im}\,L$',size=10,color=TEAL)
    text(ax,-.18,-.21,'0',size=9,color=MUTED)
    right=fig.add_axes([.62,.265,.34,.48]);panel(right)
    text(right,.5,.91,'A chosen scalar detector',size=11,color=TEAL,weight='bold')
    text(right,.5,.69,r'$\ell(x,y)=y$',size=14)
    text(right,.5,.46,r'$\ell L=0$',size=14,color=TEAL)
    text(right,.5,.22,r'$\ell(d)=3\ne0$',size=14,color=GOLD)
    bottom=fig.add_axes([.065,.105,.90,.105]);panel(bottom);box(bottom,(0,0),1,1)
    text(bottom,.5,.70,r'$u=(-2,0):\quad d+Lu=(0,3)\ne0.$',size=12,color=TEAL)
    text(bottom,.5,.23,r'The class $[d]\in\mathbb{R}^2/\mathrm{im}\,L$ is represented by $(0,3)$.',size=10.2)
    footer(fig,'Standard Euclidean splitting is used. The scalar 3 depends on the displayed quotient identification.')
    emit(fig,'correction_cokernel_plane')


def small_matrix(ax, x, y, values, label):
    text(ax,x-.115,y,label,size=13,ha='right')
    for row in range(2):
        for col in range(2):
            text(ax,x+.07+col*.16,y+.075-row*.15,str(values[row][col]),size=13)
    for xx,sgn in [(x-.03,1),(x+.34,-1)]:
        ax.plot([xx+sgn*.025,xx,xx,xx+sgn*.025],[y+.14,y+.14,y-.14,y-.14],color=INK,lw=1)


def rotating_projector_transport():
    fig=canvas('A rotating line and its complementary packet',
               r'$u_\theta=(\cos\theta,\sin\theta)$, $P(\theta)=u_\theta u_\theta^{\mathsf{T}}$, $Q(\theta)=I-P(\theta)$.',height=5.35)
    ax=fig.add_axes([.07,.395,.41,.35])
    ax.set_xlim(-1.28,1.3);ax.set_ylim(-1.22,1.38);ax.set_aspect('equal');ax.axis('off')
    ax.add_patch(Circle((0,0),1,fill=False,edgecolor=GRID,lw=.9))
    for t in [0,np.pi/3]:
        u=np.array([np.cos(t),np.sin(t)]);v=np.array([-np.sin(t),np.cos(t)])
        ax.plot([-u[0],u[0]],[-u[1],u[1]],color=TEAL,lw=1.9)
        ax.plot([-v[0],v[0]],[-v[1],v[1]],color=GOLD,lw=1.4,linestyle=(0,(3,2)))
    arrow(ax,(0,0),(1,0),color=TEAL)
    arrow(ax,(0,0),(.5,np.sqrt(3)/2),color=TEAL)
    arc=Arc((0,0),.8,.8,theta1=0,theta2=60,color=INK,lw=1);ax.add_patch(arc)
    arrow(ax,(.225,.327),(.2,.347),color=INK)
    text(ax,.44,.265,r'$\pi/3$',size=10)
    text(ax,1.10,-.10,r'$u_0$',size=10,color=TEAL)
    text(ax,.57,1.04,r'$u_{\pi/3}$',size=10,color=TEAL)
    text(ax,-.85,.69,r'$\mathrm{im}\,Q(\pi/3)$',size=9.5,color=GOLD,ha='center')
    text(ax,0,-1.14,'Solid: P packet    Dashed: Q packet',size=9.2,color=MUTED)
    right=fig.add_axes([.55,.395,.41,.35]);panel(right)
    text(right,.5,.94,'Canonical continuous transport',size=11,color=TEAL,weight='bold')
    small_matrix(right,.41,.70,[[0,-1],[1,0]],r'$K=[P^\prime,P]=$')
    text(right,.5,.42,r'$U^\prime(\theta)=KU(\theta),\quad U(0)=I$',size=10.7)
    text(right,.5,.21,r'$U(\theta)=R(\theta)$',size=13,color=TEAL)
    band=fig.add_axes([.06,.25,.90,.105]);panel(band);box(band,(0,0),1,1)
    text(band,.5,.72,r'$S=\cos\delta\,R(\delta),\qquad S^{\mathsf{T}}S=\cos^2\delta\,I$',size=11)
    text(band,.5,.25,r'For $|\delta|<\pi/2$: polar$(S)=R(\delta)$ exactly.',size=10.7,color=TEAL)
    table=fig.add_axes([.06,.095,.90,.12]);panel(table)
    xs=[.02,.37,.71]
    for x,label in zip(xs,['Steps N','Each increment','Ordered product']):
        text(table,x,.96,label,size=10,color=MUTED,weight='bold',ha='left')
    for row,n in enumerate([2,4,8]):
        y=.67-row*.28
        table.axhline(y+.13,color=GRID,lw=.7)
        text(table,xs[0],y,str(n),size=10,ha='left')
        text(table,xs[1],y,rf'$\pi/{3*n}$',size=10,ha='left')
        text(table,xs[2],y,r'$R(\pi/3)$',size=10,color=TEAL,ha='left')
    footer(fig,'Every mesh product is exact in this finite model.\nThe general theorem concerns convergence for broader projector paths.')
    emit(fig,'rotating_projector_transport')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.time();stamp=datetime.now(timezone.utc).isoformat()
    checks=exact_checks()
    QA.mkdir(parents=True,exist_ok=True)
    (BASE/'model_data.json').write_text(json.dumps(DATA,indent=2)+'\n')
    for make in [typed_edge_walks,transport_vs_connection,holonomy_obstruction_blocks,
                 packet_jet_worked_example,correction_cokernel_plane,rotating_projector_transport]:
        make()
    (QA/'exact_checks.json').write_text(json.dumps({'checks':checks,'result':'all exact finite checks passed'},indent=2)+'\n')
    (QA/'layout_checks.json').write_text(json.dumps(LAYOUT,indent=2)+'\n')
    outputs=[{'path':str(p.relative_to(ROOT)), 'sha256':sha256(p)} for p in sorted(OUT.glob('*'))
             if p.suffix in {'.pdf','.png'}]
    manifest={'schema_version':1,'claim_id':'paper-III-six-finite-figure-models',
       'repository':{'commit':'no Git revision: authorized standalone publication bundle','dirty':True},
       'command':'python3 editable/traditional/figure_sources/generate_figures.py',
       'environment':{'software':[f'Python {sys.version.split()[0]}',f'SymPy {sp.__version__}',
                                   f'Matplotlib {matplotlib.__version__}',f'NumPy {np.__version__}'],
                      'hardware':platform.machine()},
       'mathematics':{'assertion_tested':'The six depicted finite models and their explicit matrix, jet, quotient, and trigonometric identities.',
         'coefficient_domain':'formal noncommuting coefficients, exact rational Fraction and SymPy symbolic trigonometry; rendering floats only',
         'conventions':json.dumps(DATA['conventions'],sort_keys=True), 'inputs':[DATA],
         'bounds':{'edge_vertices':4,'obstruction_packets':4,'jet_degree':2,'correction_dimension':2,
                   'rotation_dimension':2,'rotation_meshes':[2,4,8],'polar_branch':'abs(delta)<pi/2'},
         'non_claims':['Not a universal proof of the manuscript results.',
                       'Shading of the schematic obstruction matrix does not assert numeric entries.',
                       'Exactness of these circular-path mesh products is special to this model.']},
       'randomness':{'used':False,'generator':'none','seed':None},
       'run':{'started_at':stamp,'runtime_seconds':round(time.time()-started,3),'exit_status':0},
       'outputs':outputs,'checks':checks,'result':'Implementation and exact finite assertions verified.',
       'residual_risks':['The PDF/PNG layout additionally requires rendered visual inspection.',
                         'This version 1 record retains input hashes but does not provide runner-enforced resource caps.'],
       'input_sha256':{p.name:sha256(p) for p in [BASE/'models.py',BASE/'generate_figures.py',BASE/'common.py',BASE/'model_data.json']}}
    (QA/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Generated {len(outputs)} figure assets; {len(checks)} exact checks passed; no text overlaps or clipping detected.')


if __name__=='__main__':
    main()
