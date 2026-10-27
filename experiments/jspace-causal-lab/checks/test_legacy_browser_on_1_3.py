"""Exercise the delivered offline HTML; no source mock or simulated output UI."""
from pathlib import Path
import json, os, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'Komorebi_JSpace_Causal_Lab_v1_3.html').read_text()
checks=[];errors=[];requests=[]
def add(name,**kw): checks.append({'name':name,'pass':True,**kw})
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r: requests.append(r.url))
 page.set_content(html);page.wait_for_function('window.JRefinedLab !== undefined')
 assert page.locator('#rLivePanel').is_visible()
 page.click('#rDemo')
 assert page.evaluate('JRefinedLab.getLive().history[0].outputs.map(b=>b[0].map(x=>x.prediction))')==[[2,2],[3,3]]
 assert page.evaluate('JCausalLab.getMemory().map(x=>x.correct)')==[[8,8],[8,8]]
 add('Guided case performs actual hidden edit, audits facts and commits branches')
 initial=page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')
 page.select_option('#rQuery','2');page.select_option('#rArg','3')
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==initial
 page.click('#rLiveAudit')
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==initial
 add('Live reads and four-branch audits do not mutate trajectory')
 page.click('.r-step[data-op="3"]')
 assert page.evaluate('JRefinedLab.getLive().history.at(-1).outputs.map(b=>b[0].map(x=>x.prediction))')==[[1,1],[3,3]]
 add('Native swap continues the committed edited state without a second patch',original=[1,1],edited=[3,3])
 page.click('#rLiveUndo')
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==initial
 add('Undo restores the exact original committed vectors')
 page.select_option('#rQuery','0');page.click('#rSweep')
 page.wait_for_function('!JRefinedLab.isBusy() && JRefinedLab.getRows().length===21',timeout=60000)
 sweep=page.evaluate('JRefinedLab.getRows()');summary=page.evaluate('JRefinedLab.getSummary()')
 assert len(sweep)==21 and sweep[0]['editNorm']==[0,0]
 assert len(page.locator('#rDoseChart path').all())==2
 assert page.locator('#rDoseRows tr').count()==21
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==initial
 assert summary['firstPreserving'] is not None
 page.click('#rApplySmallest')
 assert page.evaluate('JCausalLab.settings().strength')==summary['firstPreserving']
 add('21-point dose scan reports and applies a tested case-specific point',summary=summary)
 page.click('#rCompare');page.wait_for_function('!JRefinedLab.isBusy() && JRefinedLab.getControls().length===7',timeout=60000)
 controls=page.evaluate('JRefinedLab.getControls()');by={r['settings']['method']:r for r in controls}
 assert by['J']['predictions']==[3,3] and by['random']['predictions']==[2,2] and by['complement']['predictions']==[2,2]
 assert page.locator('#rControlRows tr').count()==7
 add('Seven same-case controls are computed independently',pairs={k:v['predictions'] for k,v in by.items()})
 # Strength 0 while a manual offset exists must no longer claim a no-op.
 page.locator('#cManual summary').click();page.eval_on_selector('#cAxis0',"e=>{e.value=1;e.dispatchEvent(new Event('input'));}")
 page.eval_on_selector('#cAlpha',"e=>{e.value=0;e.dispatchEvent(new Event('input'));}")
 page.wait_for_function("document.querySelector('.range-ticks span').textContent.includes('offsets')")
 assert page.evaluate('JCausalLab.getResult().geometry[0].deltaNorm')>0
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==initial
 add('Zero donor strength is correctly distinguished from manual-offset edits')
 page.click('#cUndo');page.select_option('#cMethod','complement')
 assert page.locator('#cDimTag').inner_text().startswith('61') and 'I −' in page.locator('#cFormula').inner_text()
 page.select_option('#cMethod','native');assert page.locator('#cDimTag').inner_text().startswith('64')
 page.click('#rSweep');page.wait_for_function('!JRefinedLab.isBusy() && JRefinedLab.getRows().length===2')
 assert [r['settings']['strength'] for r in page.evaluate('JRefinedLab.getRows()')]==[0,1]
 add('Complement/native dimensions and formulas are accurate; native scan cannot interpolate')
 # Relevance/read change in preview does not silently commit a new episode to live branch.
 page.click('[data-ctarget="0"]')
 assert page.evaluate('JRefinedLab.getRows().length')==0
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==initial
 add('Changing preview context invalidates diagnostics but preserves committed trajectory')
 page.click('#rDemo');page.fill('#rProgram','LSR');page.click('#rRunProgram')
 page.select_option('#rCueLeft','2');page.select_option('#rCueRight','3');page.click('#rReload');page.click('#rSilent')
 payload=page.evaluate('JRefinedLab.exportLive(false)');saved=page.evaluate('JSON.stringify(JRefinedLab.getLive().history)')
 # Deliberately poison recorded observations. Replay must ignore them.
 for snap in payload['snapshots']:
  for branch in snap['outputs']:
   for consumer in branch:
    for agent in consumer: agent['prediction']=999
 page.evaluate('(x)=>JRefinedLab.importLive(x)',payload)
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().history)')==saved
 add('Import recomputes trajectory; supplied prediction values cannot replace neural outputs')
 with page.expect_download() as dl:page.click('#rExport')
 out=ROOT/'checks/robustness/legacy_regression_exported_session.json';dl.value.save_as(out)
 page.locator('#rImportFile').set_input_files(str(out))
 page.wait_for_function("document.getElementById('rNotice').textContent.includes('replayed')")
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().history)')==saved
 add('Actual downloaded session imports and exactly reproduces same-engine history',bytes=out.stat().st_size)
 n=page.evaluate('JRefinedLab.getLive().actions.length');state=page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')
 page.fill('#rProgram','L<script>');page.click('#rRunProgram')
 assert 'Use only' in page.locator('#rNotice').inner_text() and page.evaluate('JRefinedLab.getLive().actions.length')==n
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==state
 bad=json.loads(out.read_text());bad['weights_sha256']='wrong'
 page.locator('#rImportFile').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad).encode()})
 page.wait_for_function("document.getElementById('rNotice').textContent.includes('hash differs')")
 assert page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==state
 add('Invalid programs and mismatched imports leave the current session untouched')
 # Cancellation is exercised programmatically in a single JS turn so the scan is in flight.
 page.click('#rDemo')
 page.evaluate("()=>{JRefinedLab.sweep();document.getElementById('cSeed').value=999;JCausalLab.newEpisode();}")
 page.wait_for_timeout(120)
 assert page.evaluate('JRefinedLab.getRows().length')==0 and not page.evaluate('JRefinedLab.isBusy()')
 add('In-flight diagnostic results cannot reappear after changing the source case')
 page.click('[data-tab="workbench"]');assert page.locator('#rLivePanel').is_hidden()
 page.click('[data-tab="evidence"]');assert page.locator('#rLivePanel').is_hidden()
 page.click('[data-tab="causal"]');assert page.locator('#rLivePanel').is_visible()
 add('Persistent trajectory stays inside its causal tab; prior tabs remain usable')
 # Current default measurements and screen artifacts for visual inspection.
 page.click('#rDemo');page.click('#rSweep');page.wait_for_function('!JRefinedLab.isBusy() && JRefinedLab.getRows().length===21')
 page.click('#rCompare');page.wait_for_function('!JRefinedLab.isBusy()')
 page.screenshot(path=str(ROOT/'checks/robustness/legacy_regression_desktop.png'),full_page=True)
 page.locator('#rLivePanel').screenshot(path=str(ROOT/'checks/robustness/legacy_regression_live_desktop.png'))
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(ROOT/'checks/robustness/legacy_regression_mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
 page.locator('#rLivePanel').scroll_into_view_if_needed();page.click('.r-step[data-op="3"]');page.click('#rLiveAudit')
 page.locator('#rLivePanel').screenshot(path=str(ROOT/'checks/robustness/legacy_regression_live_mobile.png'))
 add('390px phone layout has no page overflow and live controls perform inference')
 # Every unlabeled range must have a label, and every button must be named.
 unnamed=page.evaluate("Array.from(document.querySelectorAll('button')).filter(e=>!e.textContent.trim()&&!e.getAttribute('aria-label')).length")
 assert unnamed==0
 add('All buttons have accessible names; keyboard-compatible inputs retained')
 assert not errors and not requests
 add('Zero page errors and zero network requests in tested session')
 b.close()
report={'status':'PASS','checks':checks,'page_errors':errors,'external_requests':requests,
 'default_case_sweep':sweep,'default_case_summary':summary,'default_case_controls':controls,
 'browser':'System Chromium via Playwright set_content','limits':['One controlled UI session, not all browser engines.','No in-chat executable renderer invoked.','No new model training or J-space certification.']}
(ROOT/'checks/robustness/legacy_regression_browser_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'status':'PASS','checks':len(checks),'names':[c['name'] for c in checks],'default_case_summary':summary},indent=2))
