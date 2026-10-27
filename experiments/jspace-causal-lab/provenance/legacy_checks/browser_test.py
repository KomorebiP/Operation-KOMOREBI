from pathlib import Path
import os
from playwright.sync_api import sync_playwright
import json,time
ROOT=Path(__file__).resolve().parents[1];url=(Path(__file__).resolve().parents[1]/'Komorebi_JSpace_Interactive_Lab.html').as_uri()
results=[];errors=[];requests=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1360,'height':1100},device_scale_factor=1)
 page.on('pageerror',lambda e: errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.set_content((Path(__file__).resolve().parents[1]/'Komorebi_JSpace_Interactive_Lab.html').read_text());page.wait_for_function('window.KomorebiLab !== undefined')
 page.screenshot(path=str(ROOT/'checks/desktop_initial.png'),full_page=True)
 page.click('#run');page.wait_for_function('KomorebiLab.getSession().ready && KomorebiLab.getSession().t===48');page.wait_for_timeout(200)
 page.click('#audit');page.wait_for_function('KomorebiLab.getSession().audit !== null')
 results.append({'name':'default_run_audit','t':page.evaluate('KomorebiLab.getSession().t'),'parent':page.inner_text('#parentScore'),'repair':page.inner_text('#repairScore')})
 page.screenshot(path=str(ROOT/'checks/desktop_run.png'),full_page=True)
 # Query must not modify live state.
 old=page.evaluate('JSON.stringify(KomorebiLab.getSession().states.map(h=>h.map(x=>Array.from(x))))')
 page.select_option('#query','2');page.select_option('#argument','3');page.wait_for_timeout(30)
 assert old==page.evaluate('JSON.stringify(KomorebiLab.getSession().states.map(h=>h.map(x=>Array.from(x))))')
 results.append({'name':'late_query_barrier','pass':True})
 page.select_option('#query','0');page.click('#recall');page.wait_for_function('KomorebiLab.getSession().retrievals===1')
 page.wait_for_timeout(200);page.click('#cycle');page.wait_for_function('KomorebiLab.getSession().retrievals===9');page.wait_for_timeout(200)
 results.append({'name':'sequential','recalls':page.evaluate('KomorebiLab.getSession().retrievals'),'audit_kind':page.evaluate('KomorebiLab.getSession().audit.kind')})
 page.select_option('#wire','cut_AtoB');page.click('#recall');page.wait_for_function('KomorebiLab.getSession().retrievals===10');page.wait_for_timeout(100)
 page.click('[data-tab=evidence]');page.wait_for_timeout(100);assert '79.98%' in page.inner_text('#evidenceBars')
 page.select_option('#evCondition','swap_conjugation_L96');assert 'No recorded sequential' in page.inner_text('#sequentialChart')
 page.select_option('#evCondition','swap_conjugation_L48');page.screenshot(path=str(ROOT/'checks/desktop_evidence.png'),full_page=True)
 results.append({'name':'saved_data_and_missing_condition','pass':True})
 page.click('[data-tab=workbench]');page.select_option('#lineage','B');page.select_option('#family','custom');page.fill('#custom','I L R S L S');page.click('#reset');page.wait_for_function('KomorebiLab.getSession().lineage==="B"');page.wait_for_timeout(100)
 page.click('#step');page.wait_for_function('KomorebiLab.getSession().t===1');page.wait_for_timeout(100)
 page.click('#run');page.wait_for_function('KomorebiLab.getSession().t===6');page.wait_for_timeout(100)
 with page.expect_download() as di:page.click('#export')
 download=di.value;download.save_as(ROOT/'checks/exported_session.json')
 exp=json.loads((ROOT/'checks/exported_session.json').read_text());assert len(exp['program'])==6 and exp['lineage']=='B'
 results.append({'name':'custom_lineage_step_export','pass':True})
 # Invalid tokens are rejected, not silently coerced.
 page.fill('#custom','L X S');page.click('#reset');page.wait_for_timeout(120);assert not page.locator('#error').is_hidden()
 results.append({'name':'invalid_program_rejected','pass':True})
 # Narrow phone view: no horizontal overflow, all main controls usable.
 mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
 mobile.on('pageerror',lambda e:errors.append('mobile: '+str(e)))
 mobile.set_content((Path(__file__).resolve().parents[1]/'Komorebi_JSpace_Interactive_Lab.html').read_text());mobile.wait_for_function('window.KomorebiLab !== undefined')
 assert mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
 mobile.click('#run');mobile.wait_for_function('KomorebiLab.getSession().t===48');mobile.wait_for_timeout(100)
 mobile.click('#audit');mobile.wait_for_function('KomorebiLab.getSession().audit !== null')
 mobile.screenshot(path=str(ROOT/'checks/mobile.png'),full_page=True)
 mobile.click('[data-tab=evidence]');assert mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
 results.append({'name':'mobile_layout_and_inference','pass':True,'width':390})
 results.append({'name':'no_external_requests','pass':all(x.startswith('file:')for x in requests),'requests':requests})
 browser.close()
# The rejected invalid-program error is intentional and retained in test output.
real_errors=[e for e in errors if 'Programs accept only' not in e]
report={'status':'PASS' if not real_errors else 'FAIL','checks':results,'page_errors':errors,'unexpected_page_errors':real_errors,'browser':'System Chromium via Playwright','html_source':url,'load_method':'set_content; file URL blocked by managed test browser'}
(ROOT/'checks/browser_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if real_errors:raise SystemExit(1)
