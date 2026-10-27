"""Build the offline causal editor. No external dependencies or network calls."""
from pathlib import Path
import base64,json,hashlib
ROOT=Path(__file__).resolve().parent;APP=ROOT/'app'
meta=json.loads((APP/'weights.json').read_text());raw=(APP/'weights.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest()==meta['weights_sha256']
validation={'port':json.loads((ROOT/'checks/causal_port_validation.json').read_text()),
 'frames_sha256':hashlib.sha256((APP/'frames.json').read_bytes()).hexdigest()}
html=(APP/'layout.html').read_text()
html=html.replace('<title>Komorebi · Interactive J-Space Lab</title>','<title>Komorebi · J-Space Causal Editor</title>')
html=html.replace('</style>',(APP/'causal.css').read_text()+'\n</style>',1)
html=html.replace('WORKSPACE INCUBATOR 0.6 · INTERACTIVE EDITION','FROZEN MODELS · CAUSAL EDITOR 1.1')
html=html.replace('Memory. Access.<br>A working state.','Edit the state.<br>Watch the output.')
html=html.replace('Change the facts, run a temporary calculation, and ask the agents what they still remember. The parent and repaired networks run here, side by side.',
 'Manipulate a candidate J-space inside the saved neural models. Compare the answer before and after the edit, then test whether facts and later computations survive.')
html=html.replace('<button role="tab" aria-selected="true" aria-controls="workbench" data-tab="workbench">Live workbench</button>',
 '<button role="tab" aria-selected="true" aria-controls="causal" data-tab="causal">J → output</button><button role="tab" aria-selected="false" aria-controls="workbench" data-tab="workbench">Memory &amp; work</button>')
html=html.replace('<section id="workbench" role="tabpanel">',(APP/'causal_panel.html').read_text()+'\n<section id="workbench" role="tabpanel" hidden>')
html=html.replace('Browser lab 1.0','Causal editor 1.1')
values={'META':json.dumps(meta,separators=(',',':')),'WEIGHTS':base64.b64encode(raw).decode('ascii'),
 'EVIDENCE':(APP/'evidence.json').read_text(),'VALIDATION':(ROOT/'checks/port_validation.json').read_text(),
 'ENGINE':(APP/'engine.js').read_text(),'UI':(APP/'ui.js').read_text()}
for key,value in values.items():html=html.replace('__'+key+'__',value)
extra='\n<script id="causalFrames" type="application/json">'+(APP/'frames.json').read_text()+'</script>'
extra+='\n<script id="causalValidationData" type="application/json">'+json.dumps(validation,separators=(',',':'))+'</script>'
extra+='\n<script>'+(APP/'causal_engine.js').read_text()+'</script>\n<script>'+(APP/'causal_ui.js').read_text()+'</script>'
html=html.replace('</body>',extra+'\n</body>')
out=ROOT/'Komorebi_JSpace_Causal_Lab.html';out.write_text(html)
print(out.name,len(html.encode()),hashlib.sha256(html.encode()).hexdigest())
