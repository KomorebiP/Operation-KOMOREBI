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
  const browser=await chromium.launch({headless:true});
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
      assert.equal(await page.locator('#cf-mode option').count(),4);
      assert.deepEqual((await valueRows(page)).slice(0,12),
        ['1','0','1','0','1','1','1','2','1','3','2','4']);
      await fit(page);

      await page.selectOption('#cf-mode','jet');
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

      await page.selectOption('#cf-mode','meixner');
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
      const shared=await page.evaluate(()=>navigator.clipboard.readText());
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
      report.widths.push({width,exactIntegers:true,plotIndependence:true,downloads:true,
        links:true,invalidLinkRejected:true,overflow:false});
      await context.close();
    }
    const noJs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:950}});
    const page=await noJs.newPage();
    await page.goto(url('sequence-closed-forms.html'));
    assert.equal(await page.locator('#closed-calculator-panel').count(),1);
    assert.ok(await page.locator('noscript').count()>0);
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
