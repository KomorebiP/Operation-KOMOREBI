from pathlib import Path
import os
import json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
html=(Path(__file__).resolve().parents[1]/'Komorebi_JSpace_Interactive_Lab.html').read_text()
ref=json.loads((R/'checks/pytorch_reference.json').read_text())
with sync_playwright()as p:
 b=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
 page=b.new_page();page.set_content(html);page.wait_for_function('window.KomorebiLab !== undefined')
 result=page.evaluate('''ref=>{const L=KomorebiLab;let maxState=0,maxLogit=0,count=0,mismatch=0;
 for(const r of ref.results){const d=new L.engine.Dyad(L.store,L.metadata,r.lineage,r.variant),a=L.engine.runCase(d,ref.specs[r.specId]);
 for(let p=0;p<a.length;p++){for(let i=0;i<2;i++)for(let j=0;j<64;j++)maxState=Math.max(maxState,Math.abs(a[p].state[i][j]-r.phases[p].state[i][j]));
 for(let q=0;q<4;q++)for(let i=0;i<2;i++){const x=a[p].outputs[q][i],y=r.phases[p].outputs[q][i];for(const k of ['logits','privateLogits'])for(let j=0;j<4;j++)maxLogit=Math.max(maxLogit,Math.abs(x[k][j]-y[k][j]));for(const k of ['prediction','privatePrediction']){count++;mismatch+=Number(x[k]!==y[k]);}}}}
 return{runs:ref.results.length,decisions:count,decision_mismatches:mismatch,max_state_abs_error:maxState,max_logit_abs_error:maxLogit,user_agent:navigator.userAgent};}''',ref)
 # Test that the independent audit truly does not mutate the live state.
 page.evaluate('()=>KomorebiLab.finishProgram()')
 before=page.evaluate('JSON.stringify(KomorebiLab.getSession().states.map(h=>h.map(x=>Array.from(x))))')
 page.evaluate('()=>KomorebiLab.auditFacts()')
 after=page.evaluate('JSON.stringify(KomorebiLab.getSession().states.map(h=>h.map(x=>Array.from(x))))')
 result['audit_nonmutation']=before==after
 result['status']='PASS'if result['decision_mismatches']==0 and result['max_logit_abs_error']<.002 and before==after else 'FAIL'
 b.close()
(R/'checks/browser_numeric_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert result['status']=='PASS'
