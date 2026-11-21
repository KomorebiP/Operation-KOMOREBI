// Responsive reading and exact preset checks for the compression continuation.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8859/';
const output=process.argv[3]||'.compression-checks/browser';
fs.mkdirSync(output,{recursive:true});
const url=name=>new URL(name,base).href;
async function fit(page,staticOnly=false){
  if(!staticOnly)await page.evaluate(async()=>{
    if(window.MathJax?.startup?.promise)await window.MathJax.startup.promise;
    await document.fonts.ready;
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  });
  const size=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
  assert.ok(size.scroll<=size.width+1,'Page overflow '+JSON.stringify(size));
}
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH}:{})});
  const report={widths:[],errors:[],noJavaScript:false};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:950},isMobile:width<500,hasTouch:width<500});
      const page=await context.newPage();page.on('pageerror',error=>report.errors.push({width,message:error.message}));
      assert.ok((await page.goto(url('sequence-hankel-compression.html'))).ok());
      await fit(page);assert.equal(await page.locator('main h1').count(),1);
      assert.equal(await page.locator('mjx-merror').count(),0);
      assert.ok(await page.locator('mjx-container').count()>35);
      const ids=await page.locator('[id]').evaluateAll(nodes=>nodes.map(node=>node.id));
      assert.equal(new Set(ids).size,ids.length);
      for(const href of await page.locator('a[href^="#"]').evaluateAll(nodes=>nodes.map(node=>node.getAttribute('href'))))
        assert.equal(await page.locator('[id="'+href.slice(1)+'"]').count(),1,href);
      const examples=await page.locator('#hankel-compression-intro tbody th a').evaluateAll(nodes=>nodes.map(node=>node.href));
      assert.equal(examples.length,2);
      await page.locator('#hankel-compression-intro').screenshot({path:path.join(output,'reading-'+width+'.png')});
      const outline=page.locator('#parity-compression-proof .sl-proof-outline>summary');
      await outline.focus();await page.keyboard.press('Enter');
      assert.equal(await page.locator('#parity-compression-proof .sl-proof-outline').evaluate(node=>node.open),true);
      await page.locator('#parity-proof-4-uniform-full-sequence-order-at-most-126').scrollIntoViewIfNeeded();
      await fit(page);
      if(width===320){await page.evaluate(()=>document.documentElement.style.fontSize='200%');await fit(page);}
      for(const [i,preset] of examples.entries()){
        const worksheet=await context.newPage();worksheet.on('pageerror',error=>report.errors.push({width,message:error.message}));
        await worksheet.goto(preset);await worksheet.locator('#cf-mode').waitFor({state:'visible'});
        await worksheet.waitForFunction(()=>document.querySelectorAll('#cf-table-values tr').length===12);
        const values=await worksheet.locator('#cf-table-values tr td code').allTextContents();
        assert.deepEqual(values.slice(0,8),i===0?['1','1','4','56','-1400','234000','92664000','13067049600']:
          ['1','1','0','-256','44536','3886128','-567844864','-82121781248']);
        assert.equal(await worksheet.locator('#cf-differential_hankel-c2').inputValue(),'0');
        await fit(worksheet);await worksheet.close();
      }
      if(width===320){await page.emulateMedia({forcedColors:'active',reducedMotion:'reduce'});await fit(page);}
      report.widths.push(width);await context.close();
    }
    const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:950}});
    const page=await context.newPage();assert.ok((await page.goto(url('sequence-hankel-compression.html'))).ok());
    assert.ok(await page.locator('#parity-compression-proof').textContent());
    assert.ok(await page.locator('#mixed-recurrence-proof').textContent());
    assert.equal(await page.locator('#hankel-compression-intro tbody tr').count(),2);
    assert.ok(await page.locator('.sl-math-display').count()>25);await fit(page,true);
    report.noJavaScript=true;await context.close();assert.deepEqual(report.errors,[]);report.status='passed';
  }finally{fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();}
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error.stack||error);process.exit(1)});
