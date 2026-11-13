"""Render exact certificate data as a vector illustration; floats draw only.
Author: Komorebi P. Acceptance uses rational squared radii, not this drawing.
"""
from pathlib import Path
from fractions import Fraction as F
from math import sqrt
import json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'solver'))
from loss_certificate import certificate

record=certificate(json.loads((root/'solver/loss_example.json').read_bytes()))
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620" viewBox="0 0 1000 620" role="img" aria-labelledby="title desc">
<title id="title">Guaranteed reflection disks for independent one-percent component errors</title>
<desc id="desc">The normalized mixed RLC example has a positive frequency band from one half to two and nominal branch reactance-to-loss ratio at most ten. The left panel shows the passive reflection disk. The right panel magnifies guaranteed uncertainty disks at three frequencies. At its nominal match, reflected power stays below one divided by 385. These are model guarantees, not measured samples.</desc>
<rect width="1000" height="620" rx="12" fill="#fff"/>
<g font-family="Arial,sans-serif" fill="#18324b">
<text x="40" y="38" font-size="23" font-weight="bold">A guaranteed region, beyond sampled perturbations</text>
<text x="40" y="67" font-size="17">Independent 1% errors in every physical R, L and C; dedicated positive series losses</text>
<circle cx="280" cy="315" r="220" fill="#f7fafb" stroke="#91a3af" stroke-width="2"/>
<path d="M60 315H500 M280 95V535" stroke="#c5d1d8"/>
<text x="80" y="110" font-size="17" font-weight="bold">Passive reflection disk</text>
<text x="475" y="338" font-size="15">Re Γ</text><text x="292" y="112" font-size="15">Im Γ</text>
<rect x="580" y="95" width="370" height="440" rx="8" fill="#f7fafb" stroke="#c5d1d8"/>
<path d="M600 315H930 M760 120V510" stroke="#c5d1d8"/>
<text x="603" y="121" font-size="17" font-weight="bold">Magnified guaranteed disks</text>
''']
for row,color,label in zip(record['sample_disks'],('#087f72','#245ca5','#ad6b15'),('ω = 1/2','ω = 1','ω = 2')):
    cr,ci=float(F(row['center']['re'])),float(F(row['center']['im']))
    gr,gi=float(F(row['nominal_gamma']['re'])),float(F(row['nominal_gamma']['im']))
    radius=sqrt(float(F(row['radius_squared'])))
    for cx,cy,scale in ((280,315,220),(760,315,850)):
        parts.append(f'<circle cx="{cx+scale*cr:.5f}" cy="{cy-scale*ci:.5f}" r="{scale*radius:.5f}" fill="{color}" fill-opacity="0.13" stroke="{color}" stroke-width="1.8"/>')
        parts.append(f'<circle cx="{cx+scale*gr:.5f}" cy="{cy-scale*gi:.5f}" r="3.5" fill="{color}"/>')
    parts.append(f'<text x="820" y="{320-850*gi:.5f}" font-size="16" fill="{color}">{label}</text>')
parts.append('''<text x="40" y="570" font-size="18" font-weight="bold">At the nominal match: reflected power &lt; 1/385 (0.26%)</text>
<text x="40" y="597" font-size="15">Whole-band loss budget κ ≤ 10. Disks shown at three frequencies; ideal lumped model, fixed reference.</text>
</g></svg>
''')
(root/'figures/mixed-loss-disks.svg').write_text('\n'.join(parts),encoding='utf-8',newline='\n')
