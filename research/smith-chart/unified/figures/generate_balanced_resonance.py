"""Native SVG schematics and scope cards for the balanced-mode theorem.
Author: Komorebi P. Circuit edges match the written two-terminal mode block.
"""
from pathlib import Path
from html import escape
from math import atan2,degrees,hypot


def text(x,y,value,style='body',anchor='start'):
    return f'<text x="{x}" y="{y}" class="{style}" text-anchor="{anchor}">{escape(value)}</text>'


def card(x,y,w,h):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="card"/>'


def branch(a,b,kind):
    dx,dy=b[0]-a[0],b[1]-a[1];length=hypot(dx,dy);mid=(length/2);angle=degrees(atan2(dy,dx))
    wires=f'<path d="M0 0 H{mid-30:.4f} M{mid+30:.4f} 0 H{length:.4f}"/>'
    if kind=='L':shape=f'<path d="M{mid-30:.4f} 0 '+''.join(f'a7.5 7.5 0 0 1 15 0 ' for _ in range(4))+'"/>'
    elif kind=='C':shape=f'<path d="M{mid-30:.4f} 0 H{mid-8:.4f} M{mid+8:.4f} 0 H{mid+30:.4f} M{mid-8:.4f} -15 V15 M{mid+8:.4f} -15 V15"/>'
    else:shape=f'<path d="M{mid-30:.4f} 0 l5 -10 10 20 10 -20 10 20 10 -20 10 20 5 -10"/>'
    return f'<g transform="translate({a[0]} {a[1]}) rotate({angle:.6f})" class="wire">{wires}{shape}</g>'


def circuit(mobile=False):
    if mobile:
        a,b,u,v=(50,320),(310,320),(180,190),(180,450)
        labels=[(95,240,'ℓ'),(268,240,'1/ℓ'),(95,418,'1/ℓ'),(268,418,'ℓ'),(225,326,'r'),
          (50,354,'w = 0'),(310,354,'w = 0'),(180,166,'w = 1'),(180,485,'w = 1')]
    else:
        a,b,u,v=(90,320),(480,320),(285,170),(285,470)
        labels=[(160,228,'L = ℓ'),(414,228,'C = 1/ℓ'),(160,428,'C = 1/ℓ'),(414,428,'L = ℓ'),(342,327,'r'),
          (90,357,'w = 0'),(480,357,'w = 0'),(285,144,'w = 1'),(285,505,'w = 1')]
    out=[branch(a,u,'L'),branch(u,b,'C'),branch(a,v,'C'),branch(v,b,'L'),branch(u,v,'R')]
    for x,y in (a,b,u,v):out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#16362f"/>')
    out += [text(x,y,label,'small','middle') for x,y,label in labels]
    out += [text(a[0]-14,a[1]-15,'1','small','middle'),text(b[0]+14,b[1]-15,'0','small','middle')]
    return ''.join(out)


def build(mobile=False):
    w,h=(360,1230) if mobile else (1050,750)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
      '<title id="title">Balanced resonance: exact obstruction and a certified neighborhood</title>',
      '<desc id="desc">A representative four-reactive internal mode has zero voltage at both ports and equal internal mode voltages. The two-terminal bridge is inversion symmetric. All internal-mode balanced graphs either reduce to at most three reactives or have that symmetry. An explicitly certified region with at most one-percent detuning and total opened-resistor conductance at most one hundredth has sample error greater than three fortieths. Positive-real Laplace samples only. The 796 whole balanced placements remain open.</desc>',
      '<style>text{font-family:Arial,sans-serif;fill:#16362f}.title{font-size:26px;font-weight:700}.head{font-size:21px;font-weight:700}.body{font-size:19px}.small{font-size:17px}.card{fill:#f4f8f4;stroke:#739686;stroke-width:2}.wire{fill:none;stroke:#16362f;stroke-width:2.5;stroke-linejoin:round;stroke-linecap:round}</style>',
      f'<rect width="{w}" height="{h}" rx="15" fill="#fcfdfb"/>']
    if mobile:
        out += [text(20,35,'Balanced resonance','title'),text(20,67,'Exact face + certified region','small'),
          card(20,90,320,450),text(36,124,'Representative internal mode','small'),circuit(True),
          text(36,520,'r is an effective resistance.','small'),
          card(20,560,320,235),text(36,597,'Exact-mode dichotomy','head'),
          text(36,632,'At most 3 reactives, or'),text(36,665,'Γ(s) = Γ(1/s).'),
          text(36,704,'Singular-face error > 10⁻¹³.','small'),text(36,735,'Symmetric branch: ≥ 264/2627.','small'),
          text(36,767,'Mode ports both have w = 0.','small'),
          card(20,815,320,220),text(36,852,'Certified neighborhood','head'),
          text(36,886,'Reactive detuning ≤ 1%.','small'),text(36,918,'Opened R conductance ≤ 1/100.','small'),
          text(36,953,'Sample error > 3/40.'),text(36,988,'Retained R values unrestricted.','small'),text(36,1018,'Positive-real Laplace samples.','small'),
          card(20,1055,320,150),text(36,1093,'Whole balanced gap remains','small'),
          text(36,1128,'796 placements still open.'),text(36,1162,'Covered: 1,334 / 2,130.','small'),text(36,1192,'Self-review; Lean count stays 41.','small')]
    else:
        out += [text(30,45,'Balanced resonance: an exact obstruction and a certified region','title'),
          card(25,80,520,495),text(48,119,'Representative internal mode','head'),circuit(False),
          text(48,548,'r represents any internal two-terminal resistor network.','small'),
          card(570,80,455,225),text(593,119,'Exact-mode dichotomy','head'),
          text(593,158,'At most 3 reactives, or Γ(s) = Γ(1/s).'),text(593,198,'Native P(i) = Q(i) = 0 gives error > 10⁻¹³.','small'),
          text(593,235,'Symmetric branch: error ≥ 264/2627.','small'),text(593,274,'w is a source-free mode, with both ports zero.','small'),
          card(570,325,455,250),text(593,365,'Certified neighborhood','head'),
          text(593,405,'Reactive detuning ≤ 1%.'),text(593,443,'Opened R conductance sum ≤ 1/100.','small'),
          text(593,484,'Maximum sample error > 3/40.'),text(593,522,'Retained R count and values unrestricted.','small'),text(593,554,'Positive-real Laplace samples only.','small'),
          card(25,600,1000,115),text(48,641,'The exact stratum and the displayed region are separated.','head'),
          text(48,675,'Whole balanced remainder: 796 placements. Covered: 1,334 / 2,130. Selected Lean scope: 41.','small'),
          text(48,702,'The general near-mode transfer and regular balanced region still need a uniform separator.','small')]
    return '\n'.join(out+['</svg>'])+'\n'


if __name__=='__main__':
    for mobile in (False,True):
        Path(__file__).with_name('balanced-resonance'+('.mobile' if mobile else '')+'.svg').write_text(build(mobile),encoding='utf-8',newline='\n')
