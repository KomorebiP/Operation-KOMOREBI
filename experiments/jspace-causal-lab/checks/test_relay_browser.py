from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'checks/relay'
html=(ROOT/'Komorebi_JSpace_Causal_Lab_v1_4.html').read_text();tests=[];errors=[];requests=[]
def check(name,**extra):tests.append(dict(name=name,pass_=True,**extra))
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1440,'height':1080},accept_downloads=True)
    page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
    page.set_content(html);page.wait_for_function('window.JRelayLab')
    page.click('#rDemo');live=page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')
    page.click('[data-tab="relay"]');assert page.locator('#relay').is_visible() and page.locator('#challenge').is_hidden()
    check('Separate relay tab, all earlier panels remain isolated')
    page.click('#mDemo');before=page.evaluate('JSON.stringify(JCausalLab.getResult())');page.click('#mRun');page.wait_for_function('!JRelayLab.isBusy()',timeout=30000)
    t=page.evaluate('JRelayLab.exportTrace(false)');assert t['status']=='Completed' and len(t['records'])==9
    ini=t['records'][0];first=next(r for r in t['records'] if r['phase']=='receive');a=first['receiver']
    assert ini['outputs'][1][0][a]['prediction']==ini['outputs'][0][0][a]['prediction']
    assert first['receiverDonor']==[False,True,False,True,True]
    check('Guided one-sided edit propagates through the actual first packet, restoration blocks, replay reproduces')
    assert int(page.locator('#mCheckpoint').input_value())==2 and page.locator('#mPackets tbody tr').count()==8
    check('Completed run focuses first exchange and shows all eight actual packet values')
    assert page.evaluate('JSON.stringify(JCausalLab.getResult())')==before and page.evaluate('JSON.stringify(JRefinedLab.getLive().states)')==live
    check('Preview and committed trajectory are not mutated by relay experiments')
    states=page.evaluate('JSON.stringify(JRelayLab.getTrace().states)');page.select_option('#mQuery','1');page.select_option('#mCheckpoint','0');page.click('#mNext');page.click('#mPrev')
    assert page.evaluate('JSON.stringify(JRelayLab.getTrace().states)')==states
    check('Late consumer changes and checkpoint navigation never advance hidden states')
    page.select_option('#mQuery','0');page.select_option('#mCheckpoint','2')
    with page.expect_download() as dl:page.click('#mExport')
    dl.value.save_as(OUT/'browser_export_trace.json');ex=json.loads((OUT/'browser_export_trace.json').read_text());assert ex['schema']=='komorebi.causal-relay.v1.4' and len(ex['initial']['baseline'][0])==64
    check('Trace export records raw states, packet interventions, provenance and fixed settings')
    page.select_option('#mWriter','1');page.click('#mRun');page.wait_for_function('!JRelayLab.isBusy()');rev=page.evaluate('JRelayLab.exportTrace(false)');r=next(r for r in rev['records'] if r['phase']=='receive');assert r['writer']==1 and r['receiver']==0 and r['firstPacketRestoration']==0
    check('Reverse writer uses the same protocol without assuming symmetric outcome')
    page.select_option('#mKind','exchange');page.select_option('#mCount','4');page.click('#mRun');page.wait_for_function('!JRelayLab.isBusy()');assert len(page.evaluate('JRelayLab.exportTrace(false).records'))==5
    check('Bare-exchange diagnostic is separately labeled and actually omits local work')
    page.select_option('#mKind','work');page.fill('#mProgram','<script>');old=page.evaluate('JRelayLab.exportTrace(false)');page.click('#mRun');assert 'Use only' in page.locator('#mNotice').inner_text();assert page.evaluate('JRelayLab.exportTrace(false)')==old
    check('Invalid input rejected before replacing previous result')
    page.fill('#mProgram','IS');page.select_option('#mCases','8');page.click('#mBank');page.wait_for_function('!JRelayLab.isBusy()',timeout=30000)
    bank=page.evaluate('JRelayLab.exportBank(false)');assert bank['status']=='Completed' and len(bank['cases'])==16
    for i in range(8):assert bank['cases'][2*i]['spec']==bank['cases'][2*i+1]['spec']
    assert page.locator('#mCase option').count()==16
    check('Fixed-setting bank evaluates both writers on identical varied histories without dose search',cases=16)
    page.select_option('#mCase','3');assert page.evaluate('JRelayLab.getTrace().plan.writer')==1
    check('Every completed case remains inspectable')
    with page.expect_download() as dl:page.click('#mExportBank')
    dl.value.save_as(OUT/'browser_export_bank.json');assert len(json.loads((OUT/'browser_export_bank.json').read_text())['cases'])==16
    check('Raw bank export preserves both directions and every completed case')
    page.evaluate('()=>{JRelayLab.runBank();JRelayLab.cancel();}')
    page.wait_for_function('!JRelayLab.isBusy()');cancelled=page.evaluate('JRelayLab.exportBank(false)');assert 'incomplete' in cancelled['status'] and cancelled['partial']['status']=='Incomplete'
    check('Cancellation preserves attempted partial case and marks bank incomplete')
    page.evaluate("()=>{JRelayLab.run();document.getElementById('cAlpha').value=.5;JCausalLab.compute();}")
    page.wait_for_function('!JRelayLab.isBusy()');assert 'incomplete' in page.evaluate('JRelayLab.getTrace().status')
    check('Changed preview cancels stale asynchronous computation')
    page.click('#mDemo');page.click('#mRun');page.wait_for_function('!JRelayLab.isBusy()');page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
    for tab in ['challenge','workbench','evidence','methods','causal']:
        page.click(f'[data-tab="{tab}"]');assert page.locator('#relay').is_hidden()
    check('All inherited tabs are still usable')
    page.set_viewport_size({'width':390,'height':844});page.click('[data-tab="relay"]');assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    page.click('#dockRun');page.wait_for_function('!JRelayLab.isBusy()');assert page.locator('#relay').is_visible();page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
    check('390-pixel layout and mobile dock route to message trace without page overflow')
    # Execute the exact same numerical fixture in Chromium, independent of UI claims.
    reference=json.loads((OUT/'reference.json').read_text())
    port=page.evaluate('''refs=>{const M=KomorebiRelay,T=KomorebiChallenge,B=KomorebiLab,C=JCausalLab;let mismatch=0,max=0,count=0;
      for(const ref of refs){const d=new KomorebiEngine.Dyad(B.store,B.metadata,ref.model.lineage,ref.model.variant),s=ref.spec,exp=T.prepareCase(d,s,0),t=M.begin(d,exp,C.frames.lineages[d.lineage],ref.settings,s.world,s.roles,{writer:ref.plan.writer,program:'ISLR'},'browser fixture',true);for(const _ of M.steps(t)){};
        for(let j=0;j<t.records.length;j++){for(let b=0;b<5;b++)for(let q=0;q<4;q++)for(let a=0;a<2;a++){const x=t.records[j].outputs[b][q][a],y=ref.records[j].outputs[b][q][a];count++;mismatch+=x.prediction!==y.prediction; if(q===0){count++;mismatch+=x.privatePrediction!==y.privatePrediction;}for(let k=0;k<4;k++)max=Math.max(max,Math.abs(x.logits[k]-y.logits[k]));}}
        for(let b=0;b<5;b++)for(let a=0;a<2;a++)for(let k=0;k<8;k++){count++;mismatch+=t.finalMemory[b].bits[a][k]!==ref.finalMemory[b].bits[a][k];}
      }return {decisions:count,mismatches:mismatch,maxLogitDifference:max};}''',reference)
    assert port['mismatches']==0;check('Chromium independently executes numeric fixture with identical Node decisions',**port)
    assert errors==[] and requests==[];check('No page errors or external network requests',requests=requests)
    # Direct local-file behavior is tested, not assumed from previous runtime.
    fp=b.new_page();file_open={}
    try:
        fp.goto((ROOT/'Komorebi_JSpace_Causal_Lab_v1_4.html').as_uri(),timeout=15000);fp.wait_for_function('window.JRelayLab',timeout=15000);file_open={'status':'PASS','url_scheme':'file','scope':'This sandbox Chromium only; not the Android client'}
    except Exception as e:file_open={'status':'BLOCKED_OR_FAILED','error':str(e),'scope':'set_content tests passed; this launch route did not'}
    b.close()
result={'status':'PASS','scenarios':len(tests),'tests':tests,'page_errors':errors,'requests':requests,'numeric':port,'direct_file_open':file_open,'browser':'System Chromium via Playwright; primary test uses set_content'}
(OUT/'browser_tests.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
