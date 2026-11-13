"""Accessible vector map of this phase's scope. Author: Komorebi P."""
from pathlib import Path

SVG='''<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="640" viewBox="0 0 1050 640" role="img" aria-labelledby="title desc">
<title id="title">Series margins and the remaining physical separator</title>
<desc id="desc">Two proven series classes have reflection margins one over two thousand and one over five hundred thousand. Seven real samples reduce degree three to a coefficient segment and degree four to a coefficient polygon. Five common graph templates retain every mixed placement through open and wire resistor faces. A uniform physical separator is still needed for 1,992 placements.</desc>
<style>text{font-family:Arial,sans-serif;fill:#15302c}.title{font-size:27px;font-weight:700}.head{font-size:22px;font-weight:700}.body{font-size:19px}.small{font-size:17px}.card{fill:#f1f7f4;stroke:#789c8d;stroke-width:2}.open{fill:#fff7e8;stroke:#be9449;stroke-width:2}.rule{stroke:#437c6e;stroke-width:3;fill:none}</style>
<rect width="1050" height="640" rx="16" fill="#fcfdfb"/>
<text x="35" y="48" class="title">Two margins proved; one physical bridge still needed</text>
<rect x="35" y="75" width="475" height="145" rx="12" class="card"/>
<text x="58" y="110" class="head">Series inductor + RC body</text><text x="58" y="145" class="body">Reflection error &gt; 1 / 2,000</text><text x="58" y="180" class="small">Convex impedance at three real samples</text><text x="58" y="204" class="small">Requires an actual series connection</text>
<rect x="535" y="75" width="480" height="145" rx="12" class="card"/>
<text x="558" y="110" class="head">Series capacitor + RL body</text><text x="558" y="145" class="body">Reflection error &gt; 1 / 500,000</text><text x="558" y="180" class="small">Sixth difference at seven real samples</text><text x="558" y="204" class="small">Arbitrary body resistor/storage counts</text>
<rect x="35" y="245" width="475" height="185" rx="12" class="card"/>
<text x="58" y="280" class="head">Coefficient reduction</text><path d="M74 330H210" class="rule"/><circle cx="74" cy="330" r="5" fill="#437c6e"/><circle cx="210" cy="330" r="5" fill="#437c6e"/><text x="68" y="366" class="small">degree 3: segment</text>
<path d="M300 330L359 298L424 330L361 384Z" fill="#cce5dc" stroke="#437c6e" stroke-width="2"/><text x="276" y="410" class="small">degree 4: polygon</text>
<text x="58" y="407" class="small">Exact rational bounds</text>
<rect x="535" y="245" width="480" height="185" rx="12" class="open"/>
<text x="558" y="280" class="head">Five common graph templates</text><text x="558" y="315" class="body">2 mixed kinds at budget 3</text><text x="558" y="347" class="body">3 mixed kinds at budget 4</text><text x="558" y="382" class="small">Every placement is an open/wire face</text><text x="558" y="410" class="small">Boundary cases are part of the obligation</text>
<rect x="35" y="460" width="980" height="140" rx="12" class="open"/>
<text x="58" y="496" class="head">Remaining: a uniform physical inequality across the entire fiber</text><text x="58" y="531" class="body">1,992 placements remain: 220 with three reactives; 1,772 with four.</text><text x="58" y="563" class="small">Coefficient proximity alone cannot control a hidden resonance.</text><text x="58" y="588" class="small">Whole-skeleton coverage remains 138 / 2,130. Selected Lean scope remains 41 statements.</text>
</svg>'''

if __name__=='__main__':
    Path(__file__).with_name('coefficient-routes.svg').write_text(SVG,encoding='utf-8',newline='\n')
