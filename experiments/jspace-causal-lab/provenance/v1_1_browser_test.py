"""UI, invariance and browser-vs-PyTorch checks for the actual standalone HTML."""
from pathlib import Path
import json,os,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'Komorebi_JSpace_Causal_Lab.html').read_text()
checks=[];errors=[];requests=[]
def add(name,**kw):checks.append({'name':name,'pass':True,**kw})
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1050},accept_downloads=True)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.set_content(html);page.wait_for_function('window.JCausalLab !== undefined')
 assert page.locator('#causal').is_visible() and page.locator('#workbench').is_hidden()
 initial=page.evaluate('JCausalLab.exportTrial(false)')
 page.click('#cApply');after=page.evaluate('JCausalLab.exportTrial(false)')
 assert [x['prediction'] for x in after['result']['baselineOutputs'][0]]==[2,2]
 assert [x['prediction'] for x in after['result']['outputs'][0]]==[3,3]
 assert initial['source']==after['source']
 add('default actual hidden edit changes both neural answers',before=[2,2],after=[3,3])
 saved=page.evaluate('JSON.stringify(JCausalLab.getResult().post)')
 page.select_option('#cQuery','2');page.select_option('#cArg','1')
 assert saved==page.evaluate('JSON.stringify(JCausalLab.getResult().post)')
 add('query and arguments cannot mutate edited or original state')
 page.select_option('#cQuery','0');page.click('#cMemory')
 assert saved==page.evaluate('JSON.stringify(JCausalLab.getResult().post)')
 assert page.evaluate('JCausalLab.getMemory().map(x=>x.correct)')==[[8,8],[8,8]]
 add('default memory survives; audit does not mutate trial')
 page.screenshot(path=str(ROOT/'checks/causal_desktop.png'),full_page=True)
 page.select_option('#cMethod','random');assert page.evaluate('JCausalLab.getResult().outputs[0].map(x=>x.prediction)')==[2,2]
 page.select_option('#cMethod','complement');assert page.evaluate('JCausalLab.getResult().outputs[0].map(x=>x.prediction)')==[2,2]
 add('random and complementary edits are real separate controls')
 page.select_option('#cMethod','J');page.select_option('#cAgent','0')
 assert page.evaluate('JCausalLab.getResult().outputs[0].map(x=>x.prediction)')==[3,2]
 add('one-agent write leaves other state unedited before common continuation')
 page.select_option('#cAgent','both');page.select_option('#cSuffix','S')
 assert page.evaluate('JCausalLab.getResult().baselineOutputs[0].map(x=>x.prediction)')==[1,1]
 assert page.evaluate('JCausalLab.getResult().outputs[0].map(x=>x.prediction)')==[3,3]
 add('edited state controls subsequent native swap operation')
 page.select_option('#cSuffix','');page.click('[data-ctarget="2"]')
 assert page.evaluate('JCausalLab.getResult().outputs[0].map(x=>x.prediction)')==[2,2]
 assert page.evaluate('JCausalLab.getCurrent().experiment.donorOps')==[1,1]
 add('nontrivial same-value native program sham')
 page.click('[data-ctarget="3"]');page.click('#cUndo')
 assert page.evaluate('JSON.stringify(JCausalLab.getResult().edited)===JSON.stringify(JCausalLab.getCurrent().experiment.baseline)')
 page.locator('#cManual summary').click()
 page.eval_on_selector('#cAxis0',"el=>{el.value='1';el.dispatchEvent(new Event('input',{bubbles:true}));}")
 page.wait_for_function('JCausalLab.getResult().geometry[0].deltaNorm>0.01')
 assert page.evaluate('JCausalLab.getResult().geometry.every(x=>x.outsideJNorm<0.00001)')
 add('manual coordinate control edits only candidate directions')
 page.click('#cUndo');page.select_option('#cMethod','native')
 assert page.evaluate('JCausalLab.getResult().nativePairWitness')
 assert page.locator('#cAlpha').is_disabled()
 add('whole native endpoint is actual donor; interpolation disabled')
 page.select_option('#cMethod','J');page.select_option('#cLineage','B');page.select_option('#cVariant','parent');page.click('#cApply')
 assert page.evaluate('JCausalLab.getResult().outputs[0].map(x=>x.prediction)')==[3,3]
 with page.expect_download() as d:
  page.click('#cExport')
 d.value.save_as(ROOT/'checks/causal_exported_trial.json')
 exp=json.loads((ROOT/'checks/causal_exported_trial.json').read_text())
 assert exp['lineage']=='B' and exp['variant']=='parent' and len(exp['result']['post'][0])==64
 add('lineage variant switching and raw-state export')
 # Capture an actual evolved old-workbench state, not the evaluator's array.
 page.click('[data-tab=workbench]');page.select_option('#family','custom');page.fill('#custom','L S R');page.click('#reset');page.wait_for_timeout(50);page.click('#run');page.wait_for_function('KomorebiLab.getSession().t===3')
 page.click('[data-tab=causal]');page.locator('#causal details').first.locator('summary').click();page.click('#cCapture');page.wait_for_function('JCausalLab.getCurrent().captured===true')
 add('captures original live workbench activations')
 # Re-render literal unchanged page for the numerical battery to avoid UI settings.
 references=json.loads((ROOT/'checks/causal_reference.json').read_text());specs=json.loads((ROOT/'checks/causal_specs.json').read_text())
 numeric=page.evaluate('''({references,specs})=>{
 const lab=KomorebiLab,E=KomorebiEngine,C=KomorebiCausal,frames=JCausalLab.frames;
 let decisions=0,mismatches=0,maxLogit=0,maxState=0;
 for(const r of references){
  const d=new E.Dyad(lab.store,lab.metadata,r.lineage,'calibrated'),sp=specs[r.spec_index];let v=sp.cue.map(i=>sp.world[i]);for(const op of sp.ops)v=E.truthOp(v,op);
  const ex=C.prepare(d,C.initial(d,sp),E.target(v),r.target),out=C.evaluate(d,ex,frames.lineages[r.lineage],r);
  for(let a=0;a<2;a++){for(let i=0;i<64;i++)maxState=Math.max(maxState,Math.abs(out.post[a][i]-r.state[a][i]));for(let q=0;q<4;q++){const l=out.outputs[q][a].logits,e=r.logits[a][q];maxLogit=Math.max(maxLogit,...l.map((x,i)=>Math.abs(x-e[i])));decisions++;if(E.argmax(l)!==E.argmax(e))mismatches++;}}
 }return {decisions,mismatches,maxLogit,maxState};
 }''',{'references':references,'specs':specs})
 assert numeric['mismatches']==0 and numeric['maxLogit']<.001 and numeric['maxState']<.0002
 add('browser numeric comparison against PyTorch',**numeric)
 page.click('[data-tab=evidence]');assert '79.98%' in page.inner_text('#evidenceBars')
 add('original saved-evidence tab remains functional')
 mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 mobile.on('pageerror',lambda e:errors.append('mobile '+str(e)));mobile.on('request',lambda r:requests.append(r.url))
 mobile.set_content(html);mobile.wait_for_function('window.JCausalLab !== undefined');mobile.click('#cApply')
 assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 mobile.click('#dockResults');mobile.wait_for_timeout(300)
 assert mobile.locator('#cOutcome').is_visible()
 mobile.screenshot(path=str(ROOT/'checks/causal_mobile.png'),full_page=True)
 for tab in ['workbench','evidence','methods','causal']:
  mobile.click('[data-tab='+tab+']');assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 add('390px mobile layout, inference, dock and tabs')
 assert not requests;assert not errors
 add('zero external requests',requests=requests)
 browser.close()
result={'status':'PASS','checks':checks,'page_errors':errors,'browser':'System Chromium via Playwright set_content',
        'limitations':['HTML attachment execution depends on the user client. No in-chat HTML renderer invoked.','Sampled numerical and UI checks, not universal equivalence.']}
(ROOT/'checks/causal_browser_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
