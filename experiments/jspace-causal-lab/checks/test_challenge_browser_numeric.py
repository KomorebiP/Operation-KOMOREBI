from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];loc=ROOT/'checks/robustness'
rows=json.loads((loc/'numeric_fixtures.json').read_text())
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page();page.set_content((ROOT/'Komorebi_JSpace_Causal_Lab_v1_3.html').read_text());page.wait_for_function('window.JChallengeLab')
 out=page.evaluate('''rows=>{
 const E=KomorebiEngine,C=KomorebiCausal,T=KomorebiChallenge,root=KomorebiLab;
 let decisions=0,bits=0,wrong=0,maxState=0;
 for(const p of rows){const d=new E.Dyad(root.store,root.metadata,p.lineage,p.variant),o=p.initial,exp={baseline:o.baseline.map(v=>Float32Array.from(v)),donor:o.donor.map(v=>Float32Array.from(v)),factualValue:o.factualValue,targetValue:o.targetValue};
 const t=T.begin(d,exp,JCausalLab.frames.lineages[p.lineage],p.settings,p.world,p.roles,p.cue,p.plan);T.run(t,true);
 for(let i=0;i<t.records.length;i++){const a=t.records[i],b=p.records[i];
 for(let branch=0;branch<3;branch++)for(let agent=0;agent<2;agent++){
 for(let j=0;j<64;j++)maxState=Math.max(maxState,Math.abs(a.states[branch][agent][j]-b.states[branch][agent][j]));
 for(let q=0;q<4;q++){decisions++;wrong+=Number(a.outputs[branch][q][agent].prediction!==b.outputs[branch][q][agent].prediction);}
 decisions++;wrong+=Number(a.outputs[branch][0][agent].privatePrediction!==b.outputs[branch][0][agent].privatePrediction);
 for(let j=0;j<8;j++){bits++;wrong+=Number(a.memory[branch].bits[agent][j]!==b.memory[branch].bits[agent][j]);}
 }
 }
 }
 return {status:wrong===0?'PASS':'FAIL',trajectories:rows.length,output_private_decisions:decisions,memory_bit_decisions:bits,mismatches:wrong,max_state_abs_difference:maxState};
}''',rows)
 assert out['mismatches']==0,out
 out['scope']='Browser vs Node reference that was independently checked against original PyTorch definitions; finite sampled paths.'
 b.close()
(loc/'browser_numeric_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
