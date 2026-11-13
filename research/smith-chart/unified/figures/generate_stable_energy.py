"""Desktop and phone vector figures for the physical constraints.
Author: Komorebi P. Triangle coordinates derive from exact scaled fiber vertices.
"""
from fractions import Fraction as F
from html import escape
from pathlib import Path

def text(x,y,value,style='body'):
    return f'<text x="{x}" y="{y}" class="{style}">{escape(value)}</text>'

def card(x,y,w,h):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="card"/>'

def triangle(x,y,scale):
    def point(a,c):return f'{float(F(x)+scale*a):.5f},{float(F(y)-scale*c):.5f}'
    A=point(1,0);B=point(0,0);C=point(0,1);N=point(F(9,13),F(6,13));I=point(F(1,2),F(1,2))
    ix,iy=I.split(',')
    return (f'<polygon points="{A} {N} {C}" fill="#fff0d2" stroke="#b18a43" stroke-width="2"/>'
      f'<polygon points="{B} {A} {C}" fill="#dcefe5" stroke="#3e7564" stroke-width="2"/>'
      f'<circle cx="{ix}" cy="{iy}" r="5" fill="#a34c40"/>'
      +text(x-5,y+25,'b only','small')+text(x+scale-37,y+25,'a only','small')
      +text(x-7,y-scale-12,'c only','small')
      +text(x+int(scale*.23),y-30,'stable triangle','small')
      +text(x+int(scale*.54),y-int(scale*.53),'m(i) = 0','small'))

def build(mobile=False):
    w,h=(360,1420) if mobile else (1050,790)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
      '<title id="title">Physical constraints on near-target Smith/RLC circuits</title>',
      '<desc id="desc">Natural graph stability cuts the coefficient quadrilateral to a triangle. Root constraints, energy, endpoints and positive-real rounding give whole one-L and one-C margins at budgets three and four, with arbitrary resistors and no endpoint or resonant guard. Coverage is 1334 of 2130. The 796 balanced two-L/two-C placements remain. The tiny structural bounds are not hardware tolerances.</desc>',
      '<style>text{font-family:Arial,sans-serif;fill:#16362f}.title{font-size:26px;font-weight:700}.head{font-size:21px;font-weight:700}.body{font-size:19px}.small{font-size:17px}.card{fill:#f4f8f4;stroke:#739686;stroke-width:2}</style>',
      f'<rect width="{w}" height="{h}" rx="15" fill="#fcfdfb"/>']
    if mobile:out.append('<style>.head{font-size:19px}</style>')
    if mobile:
        out += [text(20,36,'Physical constraints','title'),text(20,68,'on near-target circuits','head'),
          card(20,90,320,390),text(36,122,'Graph stability cuts the fiber','head'),triangle(52,405,235),
          text(36,457,'a, b, c ≥ 0; a + b + c = 1/30','small'),
          card(20,500,320,225),text(36,535,'Whole three-reactive margins','head'),
          text(36,570,'One L: error > 10⁻¹¹'),text(36,600,'One C: error > 10⁻¹³','small'),
          text(36,640,'Every placement; arbitrary R.'),text(36,670,'No endpoint or resonance guard.','small'),text(36,700,'Positive-real samples only.','small'),
          card(20,745,320,195),text(36,780,'Whole four-reactive margins','head'),
          text(36,814,'One L: error > 10⁻³⁰'),text(36,846,'One C: error > 10⁻³⁷','small'),
          text(36,873,'Arbitrary resistor count/values.','small'),text(36,911,'Tiny structural separation bounds.','small'),
          card(20,960,320,220),text(36,995,'Every fit at error ≤ 10⁻⁷:','head'),
          text(36,1030,'3 reactives: all values bounded.','small'),text(36,1060,'4 reactives: at least 3 bounded.','small'),
          text(36,1092,'Normalized interval [10⁻⁷, 10⁷].','small'),text(36,1124,'R values remain unbounded.','small'),
          text(36,1155,'Positive-real samples only.','small'),
          card(20,1200,320,185),text(36,1236,'Only balanced cases remain','head'),
          text(36,1271,'796 two-L/two-C placements.'),text(36,1303,'Covered: 1,334 / 2,130.','small'),
          text(36,1333,'Selected Lean scope stays 41.','small'),text(36,1363,'Written self-review + exact replay.','small')]
    else:
        out += [text(35,47,'Physical constraints tighten the remaining Smith/RLC problem','title'),
          card(35,80,475,465),text(58,119,'Graph stability cuts the coefficient fiber','head'),triangle(100,460,280),
          text(280,195,'Removed unstable factor','small'),
          text(58,520,'Stable triangle: a, b, c ≥ 0; a + b + c = 1/30','small'),
          card(535,80,480,225),text(558,119,'Whole three-reactive margins','head'),
          text(558,160,'One L: error > 10⁻¹¹'),text(558,193,'One C: error > 10⁻¹³','small'),
          text(558,233,'Every placement; arbitrary resistor count.'),text(558,270,'No endpoint or resonant-denominator guard.','small'),
          card(535,325,480,220),text(558,365,'Whole four-reactive margins','head'),
          text(558,408,'One L: error > 10⁻³⁰'),text(558,445,'One C: error > 10⁻³⁷'),
          text(558,490,'Every one-kind placement, arbitrary R.','small'),text(558,520,'Tiny structural bounds; not hardware tolerances.','small'),
          card(35,570,475,180),text(58,608,'Every fit at error ≤ 10⁻⁷:','head'),
          text(58,643,'3 reactives: all values lie in [10⁻⁷, 10⁷].','small'),text(58,675,'4 reactives: at least three values lie there.','small'),
          text(58,707,'Normalized L/C values; resistor values unbounded.','small'),text(58,735,'Positive-real Laplace samples only.','small'),
          card(535,570,480,180),text(558,608,'The balanced class remains open','head'),
          text(558,643,'796 remain; 1,334 / 2,130 covered.','small'),text(558,675,'Selected Lean coverage remains 41 statements.','small'),
          text(558,707,'New results: written self-review and exact replay.','small'),text(558,735,'No hardware or historical priority claim.','small')]
    return '\n'.join(out+['</svg>'])+'\n'

if __name__=='__main__':
    for mobile in (False,True):
        Path(__file__).with_name('stable-energy'+('.mobile' if mobile else '')+'.svg').write_text(build(mobile),encoding='utf-8',newline='\n')
