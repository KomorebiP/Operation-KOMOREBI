// Responsive publication checks for the rational Hankel continuation.
// Author: Komorebi P. Automated project checks, not accessibility certification.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8857/';
const output=process.argv[3]||'.sequence-checks/rational-browser';
fs.mkdirSync(output,{recursive:true});
const url=name=>new URL(name,base).href;
const preset='sequence-library.html?cf-version=1&cf-mode=linear_hankel&cf-start=0&cf-count=12&cf-a0=1&cf-a1=1#closed-calculator-panel';
async function settled(page){
  await page.evaluate(async()=>{
    if(window.MathJax?.startup?.promise)await window.MathJax.startup.promise;
    await document.fonts.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
}
async function fit(page,staticOnly=false){
  if(!staticOnly)await settled(page);
  const size=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:document.documentElement.clientWidth}));
  assert.ok(size.scroll<=size.width+1,'Horizontal overflow '+JSON.stringify(size));
}
const values=page=>page.locator('#cf-table-values tr td code').allTextContents();
const clipboardText=async page=>(await page.evaluate(()=>navigator.clipboard.readText())).replace(/\r\n/g,'\n');
(async()=>{
  const browser=await chromium.launch({headless:true,
    ...(process.env.PLAYWRIGHT_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH}:{})});
  const report={widths:[],errors:[],noJavaScript:false};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:950},
        isMobile:width<500,hasTouch:width<500,permissions:['clipboard-read','clipboard-write'],
        acceptDownloads:true});
      const page=await context.newPage();
      page.on('pageerror',error=>report.errors.push({width,message:error.message}));
      assert.ok((await page.goto(url('sequence-rational-hankel.html'))).ok());
      await settled(page);
      assert.equal(await page.locator('main h1').count(),1);
      assert.equal(await page.locator('mjx-merror').count(),0);
      assert.ok(await page.locator('mjx-container').count()>20);
      assert.equal(await page.locator('#linear-weight-proof .sl-math-proof-table th[scope=row]').count(),10);
      const ids=await page.locator('[id]').evaluateAll(nodes=>nodes.map(node=>node.id));
      assert.equal(new Set(ids).size,ids.length,'Duplicate page IDs');
      for(const href of await page.locator('a[href^="#"]').evaluateAll(nodes=>nodes.map(node=>node.getAttribute('href'))))
        assert.equal(await page.locator('[id="'+href.slice(1)+'"]').count(),1,'Missing anchor '+href);
      await fit(page);
      await page.locator('#rational-hankel').screenshot({path:path.join(output,'reading-'+width+'.png')});
      if(width===320){
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        await fit(page);
        await page.evaluate(()=>document.documentElement.style.removeProperty('font-size'));
      }
      await page.goto(url(preset));
      await page.locator('#cf-mode').waitFor({state:'visible'});
      assert.equal(await page.locator('#cf-mode').inputValue(),'linear_hankel');
      assert.deepEqual((await values(page)).slice(0,8),['1','1','4','8','-8','48','576','1152']);
      await page.locator('#cf-ogf>summary').focus();await page.keyboard.press('Enter');
      assert.equal(await page.locator('#cf-ogf>summary').textContent(),'Exact rational Hankel generating function and recurrence');
      const formula=await page.locator('#cf-ogf-formula').textContent();
      assert.match(formula,/n >= 1/);assert.ok(!formula.includes('undefined'));
      await page.locator('#cf-ogf-copy').click();
      assert.equal(await clipboardText(page),formula+'\n');
      await fit(page);
      await page.locator('#closed-calculator-panel').screenshot({path:path.join(output,'calculator-'+width+'.png')});
      await page.locator('#cf-linear_hankel-a0').fill('0');
      assert.equal(await page.locator('#cf-results').isVisible(),false);
      await page.locator('#cf-calculate').click();
      assert.deepEqual((await values(page)).slice(0,5),['1','0','0','-8','96']);
      await page.locator('#cf-linear_hankel-a0').fill('2');
      await page.locator('#cf-linear_hankel-a1').fill('0');
      await page.locator('#cf-start').fill('225');await page.locator('#cf-count').fill('32');
      await page.locator('#cf-calculate').click();
      assert.equal((await values(page))[0],String(2n*4n**224n));
      await page.locator('#cf-link').click();
      const shared=await clipboardText(page);
      const restored=await context.newPage();await restored.goto(shared);
      await restored.locator('#cf-mode').waitFor({state:'visible'});
      assert.deepEqual(await values(restored),await values(page));
      await fit(restored);await restored.close();
      const download=page.waitForEvent('download');await page.locator('#cf-download').click();
      const csv=await download;const target=path.join(output,'linear-'+width+'.csv');
      await csv.saveAs(target);assert.ok(fs.readFileSync(target,'utf8').includes(String(2n*4n**224n)));
      await page.locator('#cf-linear_hankel-a1').fill('13');await page.locator('#cf-calculate').click();
      assert.equal(await page.locator('#cf-results').isVisible(),false);
      assert.match(await page.locator('#cf-status').textContent(),/between -12 and 12/);
      await page.selectOption('#cf-mode','differential_moments');
      await page.locator('#cf-kernel>summary').click();
      assert.match(await page.locator('#cf-kernel-formula').textContent(),/Phi\(t\) = 1\+t\^2/);
      await page.locator('#cf-kernel-copy').click();
      assert.equal(await clipboardText(page),
        (await page.locator('#cf-kernel-formula').textContent())+'\n');
      await fit(page);
      if(width===320){
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        await fit(page);
        await page.emulateMedia({forcedColors:'active',reducedMotion:'reduce'});
        await fit(page);
      }
      report.widths.push(width);await context.close();
    }
    const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:950}});
    const page=await context.newPage();await page.goto(url('sequence-rational-hankel.html'));
    assert.ok(await page.locator('#rational-hankel-proof').textContent());
    assert.equal(await page.locator('#linear-weight-proof .sl-math-proof-table').count(),1);
    assert.ok(await page.locator('a[href*="cf-mode=linear_hankel"]').count()>=3);
    await fit(page,true);report.noJavaScript=true;await context.close();
    assert.deepEqual(report.errors,[]);report.status='passed';
  }finally{
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
    await browser.close();
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error.stack||error);process.exit(1);});
