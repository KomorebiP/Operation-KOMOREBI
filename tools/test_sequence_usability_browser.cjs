const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'sequence-usability-browser';
fs.mkdirSync(output,{recursive:true});
const url=relative=>new URL(relative,base).href;
async function fit(page){
  await page.evaluate(async()=>{
    await document.fonts.ready;
    await window.KomorebiMath?.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true,'Page-wide horizontal overflow');
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0,'MathJax error');
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  const report={status:'running',widths:[],noJavaScript:false,errors:[]};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940}});
      const page=await context.newPage();
      page.on('pageerror',error=>report.errors.push(error.message));
      await page.goto(url('sequence-library.html'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('.sl-primary-nav a').count(),3);
      assert.equal(await page.locator('#sl-results>li').count(),24);
      assert.equal(await page.locator('#sl-results .sl-result-definition:not([open])').count(),24);
      assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#research-families>.sl-topic-disclosure').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#library-sources>.sl-topic-disclosure').evaluate(el=>el.open),false);
      await page.locator('#sl-results .sl-result-definition summary').first().click();
      assert.equal(await page.locator('#sl-results .sl-result-definition').first().evaluate(el=>el.open),true);
      await fit(page);
      await page.goto(url('sequence-library.html?q=id%3AKSEQ-000025#library-search'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#sl-results>li').count(),1);
      assert.equal(await page.locator('#sl-results .sl-result-definition').first().evaluate(el=>el.open),true);
      await page.locator('#sl-results .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      assert.equal(await page.locator('#sl-results [data-math-tex]').first().isVisible(),true);
      await fit(page);
      await page.goto(url('sequence-library.html#oeis'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#sl-oeis-query').isVisible(),true);
      await page.goto(url('sequence-library.html#research-graph'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#research-graph>details').evaluate(el=>el.open),true);
      await fit(page);
      await page.goto(url('sequence-library.html#research-families'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#research-families>.sl-topic-disclosure').evaluate(el=>el.open),true);
      await page.goto(url('sequence-library.html#transfers'));
      await page.locator('[data-transfer-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#tr-form').isVisible(),true);
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),false);
      assert.equal(await page.locator('.sr-transfer-method').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#tr-result-nav a').count(),4);
      await page.locator('#tr-result-nav a[href="#tr-matrices"]').click();
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#tr-matrix-size').isVisible(),true);
      const tableHeight=await page.locator('#tr-result>.sar-scroll').evaluate(el=>el.getBoundingClientRect().height);
      assert.ok(tableHeight<=320,'Exact data section too tall: '+tableHeight);
      await fit(page);
      report.widths.push({width,compactResults:true,deepLinks:true,accessibleDisclosures:true,transferShortcuts:true,noOverflow:true});
      await context.close();
    }
    const context=await browser.newContext({viewport:{width:320,height:900},javaScriptEnabled:false});
    const page=await context.newPage();
    await page.goto(url('sequence-library.html'));
    assert.equal(await page.locator('.sl-primary-nav a').count(),3);
    assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),false);
    assert.equal(await page.locator('#tr-form').count(),0);
    assert.equal(await page.locator('.sr-transfer-example').count(),1);
    await page.locator('.sr-transfer-example summary').click();
    assert.equal(await page.locator('.sr-transfer-example').evaluate(el=>el.open),true);
    await page.locator('#oeis>.sl-topic-disclosure summary').click();
    assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),true);
    await page.locator('#sl-extra-tools>summary').click();
    assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),true);
    assert.equal(await page.locator('#sl-count a[href="sequence-library/index.html"]').count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true);
    await context.close();
    report.noJavaScript=true;
    assert.deepEqual(report.errors,[]);
    report.status='passed';
  }finally{
    await browser.close();
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
