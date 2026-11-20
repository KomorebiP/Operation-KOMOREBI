// Browser checks for the progressive exact Closed Forms worksheet.
// Author: Komorebi P.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'.sequence-checks/reports/closed-forms-browser';
fs.mkdirSync(output,{recursive:true});
const url=name=>new URL(name,base).href;
const clipboardText=async page=>(await page.evaluate(()=>navigator.clipboard.readText())).replace(/\r\n/g,'\n');
async function fit(page,staticOnly=false){
  if(!staticOnly)await page.evaluate(async()=>{await document.fonts.ready;await new Promise(ok=>requestAnimationFrame(()=>requestAnimationFrame(ok)));});
  const dims=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));
  assert.ok(dims.scroll<=dims.client+1,'Unexpected horizontal page overflow: '+JSON.stringify(dims));
}
async function openCalculator(page){
  await page.locator('[data-library-ready=true]').waitFor();
  const details=page.locator('#closed-calculator-panel');
  assert.equal(await details.count(),1);
  if(!await details.evaluate(node=>node.open))await details.locator(':scope > summary').click();
  await page.locator('#cf-mode').waitFor({state:'visible'});
  return details;
}
async function valueRows(page){
  return page.locator('#cf-table-values tr td code').allTextContents();
}
(async()=>{
  const browser=await chromium.launch({headless:true,
    ...(process.env.PLAYWRIGHT_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH}:{})});
  const report={status:'running',widths:[],errors:[],noJavaScript:false};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:950},isMobile:width<500,
        hasTouch:width<500,permissions:['clipboard-read','clipboard-write'],acceptDownloads:true});
      const page=await context.newPage();
      page.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await page.goto(url('sequence-closed-forms.html'));
      const panel=page.locator('#closed-calculator-panel');
      assert.equal(await panel.evaluate(node=>node.open),false,'Worksheet should be collapsed on arrival');
      await openCalculator(page);
      assert.equal(await page.locator('#cf-mode option').count(),12);
      assert.deepEqual((await valueRows(page)).slice(0,12),
        ['1','0','1','0','1','1','1','2','1','3','2','4']);
      await fit(page);
      await page.selectOption('#cf-mode','padovan');
      assert.deepEqual((await valueRows(page)).slice(0,8),['1','0','0','1','0','1','1','1']);
      await page.selectOption('#cf-mode','fourblock');
      assert.deepEqual((await valueRows(page)).slice(0,4),['1','34','11056','14873104']);
      assert.equal(await page.locator('#cf-start').inputValue(),'1');

      await page.selectOption('#cf-mode','central_binomial');
      assert.deepEqual((await valueRows(page)).slice(0,8),
        ['1','-3','14','-57','246','-1038','4424','-18777']);
      assert.equal(await page.locator('#cf-central_binomial-r-label').textContent(),'Parameter r');
      assert.equal(await page.locator('#cf-central').isVisible(),true);
      assert.equal(await page.locator('#cf-central').evaluate(el=>el.open),false);
      await page.locator('#cf-central > summary').focus();await page.keyboard.press('Enter');
      const centralFormula=await page.locator('#cf-central-formula').textContent();
      assert.match(centralFormula,/^r = 4\n/);
      assert.match(centralFormula,/G_r\(x\)/);
      assert.match(centralFormula,/n >= 3/);
      assert.equal(await page.locator('#cf-central-proof').getAttribute('href'),'sequence-central-binomial.html');
      await page.locator('#cf-central-copy').click();
      assert.equal(await clipboardText(page),centralFormula+'\n');
      await fit(page);
      await page.locator('#cf-central').screenshot({path:path.join(output,'central-binomial-formulas-'+width+'.png')});
      if(width===320){
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        await fit(page);
        await page.locator('#cf-central').screenshot({path:path.join(output,'central-binomial-formulas-enlarged-320.png')});
        await page.evaluate(()=>document.documentElement.style.removeProperty('font-size'));
      }
      await page.locator('#cf-central_binomial-r').fill('0');
      assert.equal(await page.locator('#cf-central-copy').isVisible(),false,'Parameter edits must hide stale central formulas');
      await page.locator('#cf-count').fill('8');
      await page.locator('#cf-calculate').click();
      assert.deepEqual(await valueRows(page),['1','1','2','3','6','10','20','35']);
      assert.match(await page.locator('#cf-central-info').textContent(),/direct central binomial specialization/);
      assert.match(await page.locator('#cf-verification').textContent(),/without division by r/);
      // Closing and reopening a disclosure invalidates its pending copy.
      await page.evaluate(()=>{
        window.__centralOriginalClipboard=navigator.clipboard;window.__centralRequests=[];
        Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:text=>
          new Promise((resolve,reject)=>window.__centralRequests.push({text,resolve,reject}))}});
      });
      await page.locator('#cf-central-copy').click();
      await page.locator('#cf-central > summary').click();
      await page.locator('#cf-central > summary').click();
      await page.locator('#cf-central_binomial-r').focus();
      await page.evaluate(async()=>{
        window.__centralRequests[0].reject(new Error('Delayed central formula copy rejection'));
        await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      });
      assert.equal(await page.locator('#cf-fallback').isVisible(),false);
      assert.equal(await page.evaluate(()=>document.activeElement.id),'cf-central_binomial-r');
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{
        configurable:true,value:window.__centralOriginalClipboard}));
      await page.locator('#cf-central_binomial-r').fill('-1');
      await page.locator('#cf-calculate').click();
      assert.deepEqual(await valueRows(page),['1','2','4','8','16','32','64','128']);
      await page.locator('#cf-link').click();
      const centralLink=await clipboardText(page);
      assert.equal(new URL(centralLink).searchParams.get('cf-mode'),'central_binomial');
      assert.equal(new URL(centralLink).searchParams.get('cf-r'),'-1');
      const centralRestored=await context.newPage();
      centralRestored.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await centralRestored.goto(centralLink);
      await centralRestored.locator('#cf-mode').waitFor();
      assert.equal(await centralRestored.locator('#cf-central_binomial-r').inputValue(),'-1');
      assert.deepEqual(await valueRows(centralRestored),['1','2','4','8','16','32','64','128']);
      await fit(centralRestored);await centralRestored.close();
      const centralCSVPromise=page.waitForEvent('download');
      await page.locator('#cf-download').click();
      const centralCSV=await centralCSVPromise;
      const centralCSVName=path.join(output,'central-binomial-'+width+'.csv');
      await centralCSV.saveAs(centralCSVName);
      assert.ok(fs.readFileSync(centralCSVName,'utf8').includes('"central_binomial","7","128"'));
      await page.locator('#cf-central_binomial-r').fill('13');
      await page.locator('#cf-calculate').click();
      assert.match(await page.locator('#cf-status').textContent(),/Parameter r must be between -12 and 12/);
      assert.equal(await page.locator('#cf-results').isVisible(),false);
      await page.locator('#cf-reset').click();
      assert.equal(await page.locator('#cf-central_binomial-r').inputValue(),'4');
      assert.equal(await page.locator('#cf-count').inputValue(),'12');
      const centralProof=await context.newPage();
      centralProof.on('pageerror',error=>report.errors.push({width,message:error.message}));
      const centralResponse=await centralProof.goto(url('sequence-central-binomial.html'));
      assert.equal(centralResponse.ok(),true);
      assert.equal(await centralProof.locator('main h1').count(),1);
      assert.equal(await centralProof.locator('.sl-math-display').count()>=3,true);
      assert.equal(await centralProof.locator('a[href*="cf-mode=central_binomial"]').count()>=1,true);
      await fit(centralProof);await centralProof.close();

      await page.selectOption('#cf-mode','jet');
      assert.equal(await page.locator('#cf-central').isVisible(),false);
      await page.locator('#cf-jet-d').fill('0');
      await page.locator('#cf-calculate').click();
      assert.deepEqual((await valueRows(page)).slice(0,7),
        ['1','2','5','16','47','146','447']);

      await page.selectOption('#cf-mode','hankel');
      assert.deepEqual((await valueRows(page)).slice(0,8),
        ['1','0','0','-8','1680','-271488','-2874880','1840174080']);
      await page.locator('#cf-hankel-d').fill('0');
      await page.locator('#cf-calculate').click();
      assert.deepEqual((await valueRows(page)).slice(0,8),
        ['1','1','1','-14','-100','56','6112','58304']);
      assert.match(await page.locator('#cf-verification').textContent(),/independent terminating 4F3/);

      await page.selectOption('#cf-mode','beta_moments');
      assert.deepEqual((await valueRows(page)).slice(0,3),['120','240','720']);
      await page.selectOption('#cf-mode','beta_hankel');
      assert.deepEqual((await valueRows(page)).slice(0,3),['1','120','28800']);
      await page.selectOption('#cf-mode','differential_hankel');
      assert.deepEqual((await valueRows(page)).slice(0,6),
        ['1','1','2','-84','-456','52197296']);
      assert.equal(await page.locator('#cf-differential_hankel-c2').inputValue(),'1');
      await page.selectOption('#cf-mode','differential_moments');
      assert.deepEqual((await valueRows(page)).slice(0,10),
        ['1','2','6','24','66','180','620','1120','4830','6300']);
      assert.equal(await page.locator('#cf-parity').isVisible(),true);
      assert.equal(await page.locator('#cf-parity').evaluate(el=>el.open),false);
      await page.locator('#cf-parity > summary').focus();await page.keyboard.press('Enter');
      const parityFormula=await page.locator('#cf-parity-formula').textContent();
      assert.equal(parityFormula,'mu_(2m) = binom(2m,m) * (1 + m + m^3)\n'+
        'mu_(2m+1) = (2m+1) * binom(2m,m) * (2 + 2*m)\nFor every integer m >= 0.');
      assert.match(await page.locator('#cf-parity-info').textContent(),/polynomial of degree 3/);
      await page.locator('#cf-parity-formula').focus();
      assert.notEqual(await page.locator('#cf-parity-formula').evaluate(el=>getComputedStyle(el).outlineStyle),'none');
      await page.locator('#cf-parity-copy').click();
      assert.equal(await clipboardText(page),parityFormula+'\n');
      await fit(page);
      await page.locator('#cf-parity').screenshot({path:path.join(output,'moment-formulas-'+width+'.png')});
      if(width===320){
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        await fit(page);
        await page.locator('#cf-parity').screenshot({path:path.join(output,'moment-formulas-enlarged-320.png')});
        await page.evaluate(()=>document.documentElement.style.removeProperty('font-size'));
      }
      assert.equal(await page.locator('#cf-ogf').isVisible(),true);
      await page.locator('#cf-ogf > summary').click();
      assert.match(await page.locator('#cf-ogf-formula').textContent(),
        /1 \+ 2\*z - 8\*z\^2 - 4\*z\^3 \+ 52\*z\^4 - 16\*z\^5 - 24\*z\^6/);
      assert.match(await page.locator('#cf-ogf-info').textContent(),
        /Numerator degree ≤ 6/);
      await page.locator('#cf-ogf-copy').click();
      assert.match(await clipboardText(page),
        /M\(z\) =/);
      // A newer copy on the same calculation supersedes a pending old one.
      await page.evaluate(()=>{
        window.__cfOriginalClipboard=navigator.clipboard;window.__cfCopyRequests=[];
        Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:text=>
          new Promise((resolve,reject)=>window.__cfCopyRequests.push({text,resolve,reject}))}});
      });
      await page.locator('#cf-parity-copy').click();
      await page.locator('#cf-ogf-copy').click();
      await page.evaluate(()=>window.__cfCopyRequests[1].resolve());
      await page.locator('#cf-mode').focus();
      await page.evaluate(async()=>{
        window.__cfCopyRequests[0].reject(new Error('Delayed clipboard rejection'));
        await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      });
      assert.equal(await page.locator('#cf-fallback').isVisible(),false);
      assert.equal(await page.locator('#cf-status').textContent(),'Copied the generating function.');
      assert.equal(await page.evaluate(()=>document.activeElement.id),'cf-mode');
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{
        configurable:true,value:window.__cfOriginalClipboard}));
      await page.locator('#cf-start').fill('150');
      assert.equal(await page.locator('#cf-parity-copy').isVisible(),false,'Parameter edits must hide stale formula exports');
      await page.locator('#cf-count').fill('11');
      await page.locator('#cf-calculate').click();
      assert.equal((await valueRows(page)).length,11);
      assert.equal((await valueRows(page))[10].length>45,true);
      assert.match(await page.locator('#cf-ogf-formula').textContent(),/7\/2/);
      await fit(page);
      await page.selectOption('#cf-mode','differential_hankel');
      assert.equal(await page.locator('#cf-ogf').isVisible(),true);
      await fit(page);
      const proofPage=await context.newPage();
      proofPage.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await proofPage.goto(url('sequence-differential-hankel.html'));
      assert.equal(await proofPage.locator('#differential-hankel-reading').count(),1);
      assert.equal(await proofPage.locator('#differential-hankel-reading h2').count()>=5,true);
      assert.equal(await proofPage.locator('#differential-hankel-reading .sl-math-display').count()>=12,true);
      assert.equal(await proofPage.locator('#math-proof-algebraic-ordinary-generating-function-for-every-finite-differential-operator').count(),1);
      assert.equal(await proofPage.locator('main h1').count(),1);
      assert.equal(await proofPage.locator('a[href*="cf-mode=differential_hankel"]').count()>=1,true);
      await fit(proofPage);
      await proofPage.close();
      const worked=page.locator('#differential-hankel-theorem');
      assert.equal(await worked.count(),1);
      const example=worked.locator('a[href*="cf-mode=differential_hankel"]');
      assert.equal(await example.count(),1);
      assert.match(await example.getAttribute('href'),/cf-a1=1/);
      await fit(page);
      await page.selectOption('#cf-mode','meixner');
      assert.equal(await page.locator('#cf-parity').isVisible(),false);
      assert.deepEqual((await valueRows(page)).slice(0,9),
        ['1','2','3','-2','-31','-30','715','2510','-30015']);

      await page.selectOption('#cf-mode','sparse');
      for(const [key,value] of Object.entries({p:'1',q:'1',r:'1',u:'12',v:'12'}))
        await page.locator('#cf-sparse-'+key).fill(value);
      await page.locator('#cf-start').fill('72');
      await page.locator('#cf-count').fill('2');
      await page.locator('#cf-calculate').click();
      assert.deepEqual(await valueRows(page),[(24n**72n).toString(),(24n**73n).toString()]);

      const csvPromise=page.waitForEvent('download');
      await page.locator('#cf-download').click();
      const csv=await csvPromise;
      const name=path.join(output,'closed-forms-'+width+'.csv');
      await csv.saveAs(name);
      const downloaded=fs.readFileSync(name,'utf8');
      assert.ok(downloaded.includes((24n**72n).toString()));
      assert.ok(downloaded.includes('"sparse","72"'));
      assert.match(downloaded,/family,index,exact_integer,parameters/);

      await page.locator('#cf-link').click();
      const shared=await clipboardText(page);
      assert.equal(new URL(shared).searchParams.get('cf-version'),'1');
      assert.equal(new URL(shared).searchParams.get('cf-v'),'12');
      assert.ok(shared.includes('cf-count=2'));
      assert.ok(!shared.includes((24n**72n).toString()));
      const restored=await context.newPage();
      restored.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await restored.goto(shared);
      assert.equal(await restored.locator('#closed-calculator-panel').evaluate(node=>node.open),true);
      await restored.locator('#cf-mode').waitFor();
      assert.deepEqual(await valueRows(restored),[(24n**72n).toString(),(24n**73n).toString()]);
      await fit(restored);

      const rejected=await context.newPage();
      rejected.on('pageerror',error=>report.errors.push({width,message:error.message}));
      const badLink=new URL(shared);badLink.searchParams.append('cf-count','3');
      await rejected.goto(badLink.href);
      await rejected.locator('#cf-mode').waitFor();
      assert.match(await rejected.locator('#cf-status').textContent(),/shared calculator view was rejected/i);
      assert.equal(await rejected.locator('#cf-count').inputValue(),'12');
      await rejected.close();
      await restored.close();

      await page.locator('#cf-count').fill('44');
      await page.locator('#cf-calculate').click();
      assert.match(await page.locator('#cf-status').textContent(),/between 1 and 32/);
      assert.equal(await page.locator('#cf-results').isVisible(),false);
      await page.locator('#cf-reset').click();
      assert.equal(await page.locator('#cf-count').inputValue(),'12');
      assert.equal(await page.locator('#cf-results').isVisible(),true);
      await fit(page);
      // The central Sequence Library is now the canonical exact workspace.
      // A supported search result must carry the precise source parameters.
      const desk=await context.newPage();
      desk.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await desk.goto(url('sequence-library.html?q='+encodeURIComponent('id:KFOR-CF-S-2-5-1-1-1')+'#library-search'));
      await desk.locator('[data-library-ready=true]').waitFor();
      assert.equal(await desk.locator('#sequence-research-desk').count(),1);
      assert.equal(await desk.locator('#sequence-research-hub').count(),1);
      assert.equal(await desk.locator('#sequence-proof-path').count(),1);
      assert.equal(await desk.locator('#closed-calculator-panel').count(),1);
      assert.equal(await desk.locator('#closed-calculator-panel').evaluate(el=>el.open),false);
      const sparseRecord=desk.locator('#sl-results>li[data-result-id="KFOR-CF-S-2-5-1-1-1"]');
      assert.equal(await sparseRecord.count(),1);
      const action=sparseRecord.locator('a[aria-label^="Recalculate exact integer values"]');
      assert.equal(await action.count(),1);
      const before=await action.getAttribute('href');
      assert.match(before,/cf-mode=sparse/);
      assert.match(before,/q=id%3AKFOR-CF-S-2-5-1-1-1/);
      await action.click();
      await desk.waitForURL(/cf-version=1/);
      await desk.locator('#cf-mode').waitFor({state:'visible'});
      assert.equal(await desk.locator('#closed-calculator-panel').evaluate(el=>el.open),true);
      assert.equal(await desk.locator('#cf-sparse-p').inputValue(),'2');
      assert.equal(await desk.locator('#cf-sparse-q').inputValue(),'5');
      assert.deepEqual((await valueRows(desk)).slice(0,8),
        ['1','0','1','0','1','1','1','2']);
      assert.equal(await desk.locator('#sl-search').count(),1);
      await fit(desk);
      // A formula record also hands off to the same central worksheet.
      const sourceRecord=await context.newPage();
      await sourceRecord.goto(url('sequence-families/KFOR-CF-JET-01.html'));
      const handoff=sourceRecord.locator('#definition a[href*="cf-mode=jet"]');
      assert.equal(await handoff.count(),1);
      assert.match(await handoff.getAttribute('href'),/cf-lambda=1/);
      await sourceRecord.close();
      await desk.close();

      report.widths.push({width,exactIntegers:true,centralBinomial:true,plotIndependence:true,downloads:true,
        links:true,invalidLinkRejected:true,overflow:false});
      await context.close();
    }
    const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:950}});
    const page=await noJs.newPage();
    await page.goto(url('sequence-closed-forms.html'));
    assert.equal(await page.locator('#differential-hankel-theorem').count(),1);
    assert.equal(await page.locator('#closed-calculator-panel').count(),1);
    assert.ok(await page.locator('noscript').count()>0);
    assert.equal(await page.locator('#cf-form').count(),0);
    await page.locator('#closed-calculator-panel>summary').click();
    assert.match(await page.locator('#closed-calculator-panel').textContent(),/static 24-term table/);
    await fit(page,true);
    await page.goto(url('sequence-differential-hankel.html'));
    assert.equal(await page.locator('#differential-hankel-reading').count(),1);
    assert.equal(await page.locator('.sl-math-display').count()>=12,true);
    assert.equal(await page.locator('#math-proof-algebraic-ordinary-generating-function-for-every-finite-differential-operator').count(),1);
    await fit(page,true);
    const centralNoJs=await page.goto(url('sequence-central-binomial.html'));
    assert.equal(centralNoJs.ok(),true);
    assert.equal(await page.locator('main h1').count(),1);
    assert.equal(await page.locator('.sl-math-display').count()>=3,true);
    assert.equal(await page.locator('a[href*="cf-mode=central_binomial"]').count()>=1,true);
    await fit(page,true);
    await page.goto(url('sequence-library.html'));
    assert.equal(await page.locator('#sequence-research-desk').count(),1);
    assert.equal(await page.locator('#closed-calculator-panel').count(),1);
    assert.equal(await page.locator('#sl-theorem-disclosure').count(),1);
    assert.equal(await page.locator('#cf-form').count(),0);
    await page.locator('#closed-calculator-panel>summary').click();
    assert.match(await page.locator('#closed-calculator-panel').textContent(),/static 24-term table/);
    await fit(page,true);
    report.noJavaScript=true;
    await noJs.close();
    assert.deepEqual(report.errors,[]);
    report.status='passed';
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
