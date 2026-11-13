"""Proof pipeline for the uniform resistor-face transfer. Author: Komorebi P."""
from pathlib import Path
from html import escape
import sys
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'solver'))
from backbone_transfer import global_arithmetic_certificate

def text(x,y,s,cls='body',anchor='start'):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(s)}</text>'
def card(x,y,w,h):return f'<rect class="card" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
def arrow(x,y,xx,yy):return f'<path class="arrow" d="M{x} {y} L{xx} {yy}"/><path class="arrow" d="M{xx-5} {yy-8} L{xx} {yy} L{xx+5} {yy-8}"/>'

def build(mobile=False):
    cert=global_arithmetic_certificate();assert cert['R_forest_edges_max']==9
    w,h=(360,1260) if mobile else (1050,940)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
      '<title id="title">Uniform physical transfer through resistor faces</title>',
      '<desc id="desc">Resistor-only elimination retains at most ten vertices and forty-five resistor slots. A maximum-conductance spanning forest has at most nine edges. An empty scale band permits small total-budget opening and contraction while leaving a bounded resistor backbone. A tiny natural driven denominator yields a nearby physical internal mode; a regular denominator yields a repaired zero-loss driven state and a global near-target core chart. The written bound is error greater than ten to the negative power ten to the forty-fifth. It is an extremely small structural bound; a practical global margin, independent review and full formal verification remain open.</desc>',
      '<style>text{font-family:Arial,sans-serif;fill:#16362f}.title{font-size:26px;font-weight:700}.head{font-size:21px;font-weight:700}.body{font-size:19px}.small{font-size:15px}.bound{font-size:27px;font-weight:700}.card{fill:#f4f8f4;stroke:#739686;stroke-width:2}.arrow{fill:none;stroke:#416959;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}</style>',
      f'<rect width="{w}" height="{h}" rx="15" fill="#fcfdfb"/>']
    if mobile:
        out += [text(20,35,'Uniform physical transfer','head'),text(20,65,'Positive-real Laplace samples','small'),
          card(20,90,320,125),text(36,122,'1. Keep every LC endpoint','body'),
          text(36,156,'Eliminate only R-only vertices.','small'),text(36,190,'At most 10 vertices and 45 R slots.','small'),arrow(180,218,180,242),
          card(20,250,320,145),text(36,282,'2. Choose an R backbone','body'),
          text(36,316,'At most 9 spanning-forest edges.','small'),text(36,347,'A gap controls weak cuts and','small'),text(36,375,'strong tree-edge contractions.','small'),arrow(180,398,180,422),
          card(20,430,320,110),text(36,463,'3. Repair actual LC flows','body'),text(36,499,'KCL holds at every original node.','small'),
          arrow(180,543,180,565),
          card(20,575,320,145),text(36,608,'Small source denominator','body'),text(36,643,'Construct a physical internal mode.','small'),
          text(36,678,'Exact-mode error > 10⁻¹³.','small'),text(180,737,'or','small','middle'),
          card(20,745,320,165),text(36,778,'Regular source denominator','body'),text(36,813,'Construct a zero-loss driven state.','small'),
          text(36,848,'Near-target feature chart:','small'),text(36,884,'sample error > 1/300.','body'),arrow(180,914,180,938),
          card(20,950,320,155),text(36,985,'Uniform structural conclusion','body'),text(36,1025,'E > 10⁻ᴺ,  N = 10⁴⁵','bound'),
          text(36,1067,'All ordinary circuits with ≤ 4 LC.','small'),
          card(20,1130,320,110),text(36,1164,'Extremely small global bound.','small'),
          text(36,1194,'Practical global margin remains open.','small'),text(36,1224,'Written self-review; Lean count: 41.','small')]
    else:
        out += [text(30,44,'A physical transfer argument through every resistor face','title'),
          card(25,80,1000,130),text(48,119,'1. Retain both terminals and every reactive endpoint','head'),
          text(48,157,'Resistor-only elimination gives at most 10 vertices, 45 R slots and the same LC branches.','body'),
          text(48,191,'A maximum-conductance R spanning forest has at most 9 edges.','small'),arrow(525,214,525,238),
          card(25,245,1000,125),text(48,283,'2. Use an empty backbone scale band','head'),
          text(48,322,'Short strong tree edges; open weak cuts; retain small redundant R edges inside components.','body'),
          text(48,353,'The surviving backbone controls natural coefficient floors and voltage-level clustering.','small'),
          '<path class="arrow" d="M525 374 V390 M270 390 H780"/>',arrow(270,390,270,398),arrow(780,390,780,398),
          card(25,405,490,230),text(48,446,'Small source denominator','head'),
          text(48,488,'Repair an approximate internal mode.','body'),text(48,528,'Change only positive LC values.','body'),
          text(48,569,'KCL holds at every original node.','small'),text(48,608,'Exact-mode sample error > 10⁻¹³.','body'),
          card(535,405,490,230),text(558,446,'Regular source denominator','head'),
          text(558,488,'Repair a zero-loss unit-current state.','body'),text(558,528,'Recover the two core response charts.','body'),
          text(558,569,'No supplied component box is assumed.','small'),text(558,608,'Near-target chart error > 1/300.','body'),
          '<path class="arrow" d="M270 641 V650 H780 V641 M525 650 V656"/>',arrow(525,656,525,668),
          card(25,675,1000,130),text(48,715,'Uniform structural conclusion for at most four reactives','head'),
          text(48,760,'E > 10⁻ᴺ,  N = 10⁴⁵','bound'),text(505,759,'Arbitrary finite resistor count and values.','body'),
          card(25,830,1000,85),text(48,864,'The bound is extremely small. A practical-sized global margin remains open.','body'),
          text(48,896,'Written project self-review; independent and full formal assurance remain separate. Selected Lean count: 41.','small')]
    return '\n'.join(out+['</svg>'])+'\n'

if __name__=='__main__':
    for mobile in (False,True):
        (here/('global-transfer'+('.mobile' if mobile else '')+'.svg')).write_text(build(mobile),encoding='utf-8',newline='\n')
