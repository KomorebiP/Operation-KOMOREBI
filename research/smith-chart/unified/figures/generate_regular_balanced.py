"""Source-bound SVGs of the two regular balanced cores. Author: Komorebi P."""
from pathlib import Path
import importlib.util,sys
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('retained_balanced_figure_helpers',here/'generate_balanced_resonance.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
sys.path.insert(0,str(here.parent/'solver'))
from regular_balanced import CORES,BASE_ERRORS,serialized
text,card,branch=helpers.text,helpers.card,helpers.branch
FIGURE_GRAPHS={kind:serialized(es) for kind,es in CORES.items()}

def route(a,b,y):
    return (f'<path class="wire" d="M{a[0]} {a[1]} V{y} M{b[0]} {b[1]} V{y}"/>'
      +branch((a[0],y),(b[0],y),'R'))

def circuit(kind,x,y,scale):
    if kind=='forest':
        pts={1:(22,170),2:(90,170),3:(158,170),4:(226,170),0:(294,170)}
        out=[branch(pts[u],pts[v],k)+text((pts[u][0]+pts[v][0])/2,150,f'{k}={v0}','small','middle') for k,u,v,v0 in CORES[kind][:4]]
        for (k,u,v,value),height,label_y in zip(CORES[kind][4:],(75,255),(59,279)):
            out += [route(pts[u],pts[v],height),text((pts[u][0]+pts[v][0])/2,label_y,'R='+str(value),'small','middle')]
    else:
        pts={1:(22,180),2:(112,180),3:(202,180),0:(292,180)};out=[]
        for (k,u,v,value),height,label_y in zip(CORES[kind][:2],(125,235),(105,267)):
            out += [f'<path class="wire" d="M{pts[u][0]} 180 V{height} M{pts[v][0]} 180 V{height}"/>',
              branch((pts[u][0],height),(pts[v][0],height),k),text((pts[u][0]+pts[v][0])/2,label_y,f'{k}={value}','small','middle')]
        for k,u,v,value in CORES[kind][2:4]:
            out += [branch(pts[u],pts[v],k),text((pts[u][0]+pts[v][0])/2,160,f'{k}={value}','small','middle')]
        for (k,u,v,value),height,label_y in zip(CORES[kind][4:],(50,305),(34,330)):
            out += [route(pts[u],pts[v],height),text((pts[u][0]+pts[v][0])/2,label_y,'R='+str(value),'small','middle')]
    for px,py in pts.values():out.append(f'<circle cx="{px}" cy="{py}" r="4" fill="#16362f"/>')
    out += [text(10,pts[1][1]+6,'a','small','end'),text(306,pts[0][1]+6,'b','small')]
    return f'<g transform="translate({x} {y}) scale({scale})">'+''.join(out)+'</g>'

def build(mobile=False):
    w,h=(360,1430) if mobile else (1050,1025)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
      '<title id="title">Two exact regular balanced cores and a certified positive-real region</title>',
      '<desc id="desc">Under the exact target endpoint, resonance and first-derivative data, with natural denominator nonzero at i, every at-most-two-L/two-C graph has one of two responses. The first has a four-edge active LC path and two resistor chords. The second has a parallel L equals one half and C equals one cycle, two more unit reactives, and resistor links four fifths and one. All arbitrary resistor subnetworks reduce to these links. A supplied neighborhood with at most one-percent error in all retained components and combined opened conductance plus contracted resistance at most one ten-thousandth has seven-sample reflection error greater than one three-hundredth. This concerns positive-real Laplace samples. All 796 whole balanced placements remain open for a useful uniform margin.</desc>',
      '<style>text{font-family:Arial,sans-serif;fill:#16362f}.title{font-size:26px;font-weight:700}.head{font-size:21px;font-weight:700}.body{font-size:19px}.small{font-size:15px}.bound{font-size:26px;font-weight:700}.card{fill:#f4f8f4;stroke:#739686;stroke-width:2}.wire{fill:none;stroke:#16362f;stroke-width:2.3;stroke-linejoin:round;stroke-linecap:round}</style>',
      f'<rect width="{w}" height="{h}" rx="15" fill="#fcfdfb"/>']
    if mobile:
        out += [text(20,36,'The two regular cores','title'),text(20,68,'Exact data + certified neighborhoods','small'),
          card(20,95,320,380),text(36,129,'F: active LC forest','head'),circuit('forest',20,140,1),
          text(36,451,'E_F = '+str(BASE_ERRORS['forest']),'body'),
          card(20,495,320,470),text(36,529,'C: active LC cycle','head'),circuit('cyclic',20,550,1),
          text(36,921,'E_C = '+str(BASE_ERRORS['cyclic']),'body'),text(36,950,'R labels are effective resistances.','small'),
          card(20,985,320,255),text(36,1023,'Certified neighborhood','head'),
          text(36,1060,'All retained values: error ≤ 1%.','small'),
          text(36,1095,'Opened g + shorted R ≤ 1/10000.','small'),
          text(36,1140,'Sample error > 1/300.','body'),
          text(36,1180,'Positive-real Laplace samples.','small'),text(36,1215,'Nominal graph is supplied and checked.','small'),
          card(20,1260,320,150),text(36,1298,'Whole uniform gap remains','small'),
          text(36,1332,'796 balanced placements remain.','small'),text(36,1365,'Explicit margins: 1,334 / 2,130.','small'),
          text(36,1397,'Project self-review; Lean scope: 41.','small')]
    else:
        out += [text(30,44,'Two exact regular responses and a certified neighborhood','title'),
          card(25,95,495,565),text(47,134,'F: active LC forest','head'),circuit('forest',37,150,1.45),
          text(47,632,'Exact sample error: '+str(BASE_ERRORS['forest']),'body'),
          card(535,95,490,565),text(557,134,'C: active parallel LC cycle','head'),circuit('cyclic',550,150,1.33),
          text(557,632,'Exact sample error: '+str(BASE_ERRORS['cyclic']),'body'),
          card(25,685,1000,210),text(48,725,'One certified region around either supplied nominal response','head'),
          text(48,766,'All retained physical R, L and C values: error ≤ 1%.','body'),
          text(48,805,'Opened conductance + contracted resistance ≤ 1/10000.','small'),
          text(650,767,'Error > 1/300.','bound'),text(650,807,'Positive-real samples.','body'),
          text(48,853,'The exact classification includes disconnected active LC components and arbitrary resistor networks.','small'),
          text(48,879,'The supplied neighborhood does not yet cover all 796 balanced placements.','small'),
          card(25,920,1000,80),text(48,953,'The useful uniform transfer remains open. Explicit whole margins: 1,334 / 2,130.','small'),
          text(48,983,'Project self-review; selected Lean scope stays 41. R labels are effective two-terminal resistances.','small')]
    return '\n'.join(out+['</svg>'])+'\n'

if __name__=='__main__':
    for mobile in (False,True):
        here.joinpath('regular-balanced'+('.mobile' if mobile else '')+'.svg').write_text(build(mobile),encoding='utf-8',newline='\n')
