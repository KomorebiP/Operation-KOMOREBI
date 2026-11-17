const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const out=process.argv[3]||'sequence-math-browser';
fs.mkdirSync(out,{recursive:true});
const url=relative=>new URL(relative,base).href;

async function settle(page) {
  await page.evaluate(async()=>{
    await window.MathJax?.startup?.promise;
    await window.KomorebiMath?.ready;
    await document.fonts.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0);
}
async function fit(page) {
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true,'Horizontal overflow');
}
(async()=>{
  const browser=await chromium.launch({headless:true}),report={status:'running',widths:[],noJavaScript:false},pageErrors=[];
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940}});
      const page=await context.newPage();page.on('pageerror',e=>pageErrors.push(e.message));
      await page.goto(url('sequence-library.html#research-graph'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      await page.locator('#cg-form').waitFor();
      await page.locator('#research-graph > details').evaluate(element=>element.open=true);
      await settle(page);
      assert.ok(await page.locator('#cg-relations .math-pair').count()>=1,'No relation equation');
      assert.ok(await page.locator('#cg-relations mjx-container').count()>=1,'Relation was not typeset');
      await page.fill('#cg-focus','KFOR-TRI-P-03');
      await page.locator('#cg-form button[type=submit]').click();
      await settle(page);
      assert.ok(await page.locator('#cg-relations .sr-connection-equation').count()>=1,'Coefficient extraction equations missing');
      await page.fill('#cg-target','KFOR-P-03-02');
      await page.locator('#cg-path-form button[type=submit]').click();
      await settle(page);
      assert.ok(await page.locator('#cg-path .math-pair').count()>=1,'Directed path equation missing');
      await page.selectOption('#site-math-display','plain');
      assert.equal(await page.locator('#cg-path [data-math-plain]').first().isVisible(),true);
      await page.selectOption('#site-math-display','typeset');
      await settle(page);
      assert.equal(await page.locator('#cg-path [data-math-tex]').first().isVisible(),true);
      await fit(page);
      await page.goto(url('sequence-families/KFOR-TRI-P-03.html#triangle'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      await page.locator('#st-index').selectOption('2');
      await settle(page);
      const exact=await page.locator('#st-row-polynomial [data-math-plain]').textContent();
      assert.equal(exact,'P_(3,2)(r) = 9r + 10r^2');
      assert.ok(await page.locator('#st-row-polynomial mjx-container').count()>=1,'Row polynomial was not typeset');
      assert.ok(await page.locator('#triangle .math-pair:has(.sr-triangle-index) mjx-container').count()>=1,'Index map was not typeset');
      await page.selectOption('#site-math-display','plain');
      assert.equal(await page.locator('#st-row-polynomial [data-math-plain]').isVisible(),true);
      await page.selectOption('#site-math-display','typeset');
      await settle(page);await fit(page);
      report.widths.push({width,relations:true,directedPaths:true,exactRowPolynomial:true,indexMap:true,plainFallback:true});
      await context.close();
    }
    const context=await browser.newContext({viewport:{width:320,height:900},javaScriptEnabled:false});
    const page=await context.newPage();await page.goto(url('sequence-families/KFOR-TRI-H.html#triangle'));
    assert.match(await page.locator('#triangle .sr-triangle-index').textContent(),/j=n\^2\+k/);
    assert.equal(await page.locator('.sl-triangle tbody tr').count(),13);
    await fit(page);await context.close();
    report.noJavaScript=true;assert.deepEqual(pageErrors,[]);
    report.status='passed';
  } finally {
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({...report,pageErrors},null,2)+'\n');
    await browser.close();
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
