"""Smoke test the final file through file://, not only set_content."""
from pathlib import Path
import json,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
errs=[];requests=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
 page=b.new_page(viewport={'width':390,'height':844})
 page.on('pageerror',lambda e:errs.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.goto((ROOT/'Komorebi_JSpace_Causal_Lab_v1_2.html').as_uri())
 page.wait_for_function('window.JRefinedLab !== undefined')
 page.click('#rDemo');page.click('.r-step[data-op="3"]')
 predictions=page.evaluate('JRefinedLab.getLive().history.at(-1).outputs.map(b=>b[0].map(x=>x.prediction))')
 assert predictions==[[1,1],[3,3]],predictions
 assert not errs and not any(x.startswith(('https://','http://')) for x in requests)
 result={'status':'PASS','load':'Actual file:// navigation','predictions_after_guided_case_and_swap':predictions,'page_errors':errs,'http_requests':[],'browser':b.version,'limits':['Checked Chromium only. Attachment execution and local HTML handling still depend on the user client.']}
 b.close()
(ROOT/'checks/file_open_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
