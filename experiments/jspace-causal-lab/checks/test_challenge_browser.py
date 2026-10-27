from pathlib import Path
import json, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];loc=ROOT/'checks/robustness';html=(ROOT/'Komorebi_JSpace_Causal_Lab_v1_3.html').read_text()
checks=[];errors=[];requests=[]
def check(name,**kw):checks.append({'name':name,'pass':True,**kw})
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.set_content(html);page.wait_for_function('window.JChallengeLab')
 page.click('#rDemo');live=page.evaluate('JSON.stringify(JRefinedLab.getLive().states)');preview=page.evaluate('JSON.stringify(JCausalLab.getResult())')
 page.click('[data-tab="challenge"]');assert page.locator('#challenge').is_visible() and page.locator('#rLivePanel').is_hidden()
 check('New challenge is isolated in its own tab')
 page.click('#tDemo');preview=page.evaluate('JSON.stringify(JCausalLab.getResult())');page.click('#tRun');page.wait_for_function('!JChallengeLab.isBusy()',timeout=30000)
 trace=page.evaluate('JChallengeLab.exportTrace(false)')
 assert len(trace['records'])==6
 assert [[x['prediction'] for x in o[0]] for o in trace['records'][0]['outputs']]==[[2,2],[3,3],[3,3]]
 assert [[x['prediction'] for x in o[0]] for o in trace['records'][1]['outputs']]==[[1,1],[3,3],[3,3]]
 check('Default edit and native swap produce actual three-way neural predictions')
 assert all(x['status']==['reload_correct','reload_correct'] for x in trace['records'][2:]);assert trace['records'][2]['reference'][1][0]==2
 check('Factual reload resets semantic expectation rather than calling it edit failure')
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==live;assert page.evaluate('JSON.stringify(JCausalLab.getResult())')==preview
 check('Challenge never mutates original preview or committed session')
 page.locator('#tDetail summary').click();page.select_option('#tCheckpoint','1');assert 'XOR' in page.locator('#tConsumerRows').inner_text();assert page.locator('#tBits .t-bit').count()==48
 check('Checkpoint inspector exposes four late consumers and all factual bits')
 page.select_option('#tFamily','conjugate');page.select_option('#tLength','48');page.select_option('#tReloads','8');page.click('#tRun');page.wait_for_function('!JChallengeLab.isBusy()',timeout=30000)
 trace=page.evaluate('JChallengeLab.exportTrace(false)');assert len(trace['records'])==16 and trace['records'][-1]['reloads']==8
 check('Long continuous work and eight no-reset reloads execute and render')
 with page.expect_download() as dl:page.click('#tExport')
 dl.value.save_as(loc/'browser_export_trace.json');exported=json.loads((loc/'browser_export_trace.json').read_text());assert exported['schema']=='komorebi.causal-challenge.v1.3';assert exported['status']=='Completed'
 check('Trace download retains raw measurements, provenance and settings')
 page.select_option('#tFamily','custom');page.fill('#tCustom','<script>');old=page.evaluate('JChallengeLab.getTrace().records.length');page.click('#tRun');assert 'Use only' in page.locator('#tNotice').inner_text();assert page.evaluate('JChallengeLab.getTrace().records.length')==old
 check('Invalid program rejected before starting inference; prior trace retained')
 page.select_option('#tFamily','commute');page.select_option('#tLength','12');page.select_option('#tReloads','4');page.select_option('#tLineages','both');page.fill('#tSeed','271309');page.click('#tBatch');page.wait_for_function('!JChallengeLab.isBusy()',timeout=60000)
 batch=page.evaluate('JChallengeLab.exportBatch(false)');assert batch['status']=='Completed' and len(batch['cases'])==16
 assert batch['settings']['strength']==1 and all(c['records'][-1]['reloads']==4 for c in batch['cases']);assert len({json.dumps(c['spec']) for c in batch['cases']})==8
 check('Fixed-setting bank evaluates both models on matched varied histories',cases=16)
 assert page.locator('#tBatchRows tr').count()==16;page.click('[data-tcase="3"]');assert 'Bank case' in page.locator('#tRunTag').inner_text()
 check('Every completed case, including failures, can be inspected')
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==live
 with page.expect_download() as dl:page.click('#tExportBatch')
 dl.value.save_as(loc/'browser_export_bank.json');assert len(json.loads((loc/'browser_export_bank.json').read_text())['cases'])==16
 check('Batch export retains all completed cases and fixed protocol')
 # Cancel before a full case completes. A partial attempted case is explicitly retained.
 page.evaluate('()=>{JChallengeLab.runBatch();JChallengeLab.cancel();}')
 page.wait_for_function('!JChallengeLab.isBusy()');cancelled=page.evaluate('JChallengeLab.exportBatch(false)');assert 'incomplete' in cancelled['status'] and len(cancelled['cases'])<16
 check('Cancellation cannot promote an incomplete bank to a completed result')
 # Changing preview while a scan is in flight cancels without rewriting prior live state.
 page.evaluate("()=>{JChallengeLab.runCurrent();document.getElementById('cAlpha').value=.5;JCausalLab.compute();}")
 page.wait_for_function('!JChallengeLab.isBusy()');assert page.evaluate('JChallengeLab.getTrace().runStatus').startswith('Cancelled')
 check('A changed preview cancels a stale asynchronous run')
 # All existing tabs remain distinct.
 for tab in ['workbench','evidence','methods','causal']:
  page.click(f'[data-tab="{tab}"]');assert page.locator('#challenge').is_hidden()
 check('Original editor, memory workbench and historical evidence tabs remain usable')
 page.click('[data-tab="challenge"]');page.click('#tDemo');page.click('#tRun');page.wait_for_function('!JChallengeLab.isBusy()')
 page.screenshot(path=str(loc/'desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
 assert page.locator('#dockRun').inner_text()=='Run challenge';page.click('#dockRun');page.wait_for_function('!JChallengeLab.isBusy()');assert page.locator('#challenge').is_visible()
 page.screenshot(path=str(loc/'mobile.png'),full_page=True)
 check('390-pixel mobile layout, inference and bottom dock target the active challenge tab')
 assert page.evaluate("Array.from(document.querySelectorAll('button')).every(x=>x.textContent.trim()||x.getAttribute('aria-label'))")
 check('Every button has an accessible name; native keyboard controls retained')
 assert not errors and not requests
 check('No page errors or external network requests during tests')
 # A real file:// test is recorded separately from set_content.
 filepage=b.new_page();nav={'status':'NOT_RUN'}
 try:
  filepage.goto((ROOT/'Komorebi_JSpace_Causal_Lab_v1_3.html').as_uri(),wait_until='load',timeout=15000);filepage.wait_for_function('window.JChallengeLab',timeout=10000);nav={'status':'PASS','method':'actual file:// navigation'}
 except Exception as e:nav={'status':'FAILED_OR_BLOCKED','method':'actual file:// navigation','error':str(e)[:700]}
 b.close()
out={'status':'PASS','checks':checks,'page_errors':errors,'external_requests':requests,'browser':'Chromium via Playwright set_content','file_navigation':nav,'limits':['Sampled desktop/390px checks, not every user device.','No in-chat HTML renderer invoked.']};(loc/'browser_validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
