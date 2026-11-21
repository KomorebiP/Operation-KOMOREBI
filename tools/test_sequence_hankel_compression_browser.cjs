// Responsive reading and exact preset checks for the compression continuation.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8859/';
const output=process.argv[3]||'.compression-checks/browser';
fs.mkdirSync(output,{recursive:true});
const url=name=>new URL(name,base).href;
const interiorSamples=JSON.parse(fs.readFileSync(path.join(__dirname,'../verification/sequence-library/hankel-compression/interior-replay.json'),'utf8')).samples.cases;
const boundaryValues=[
  ['1','0','-1','0','2916','0','-9610000','0'],
  ['1','0','-9','0','15876','0','-291600','0'],
  ['1','0','-9','0','72900','0','-357210000','0'],
  ['1','0','0','-8','1680','-271488','-2874880','1840174080'],
  ['1','1','1','-14','-100','56','6112','58304'],
  ['1','1','6','-36','360','-1200','5600','-15680'],
];
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
      assert.equal(await page.locator('mjx-merror, merror, [data-mml-node="merror"]').count(),0);
      assert.ok(await page.locator('mjx-container').count()>35);
      assert.ok((await page.locator('#hankel-compression-intro').textContent()).includes('uniform bound is optimal'));
      assert.ok(await page.locator('#sharp-quadratic-proof mjx-container').count()>25);
      assert.ok(await page.locator('#uniform-mixed-proof mjx-container').count()>25);
      await page.waitForFunction(()=>document.querySelector('[data-hankel-orders]')?.dataset.ordersReady==='true');
      assert.ok(await page.locator('#interior-orders-proof mjx-container').count()>50);
      assert.equal(await page.locator('#sho-order').getAttribute('data-order'),'98');
      const orderButtons=page.locator('#sho-form [data-order-t]');assert.equal(await orderButtons.count(),8);
      for(let i=0;i<8;i++){
        const button=orderButtons.nth(i),t=await button.getAttribute('data-order-t'),q=await button.getAttribute('data-order-q');
        const expected=interiorSamples.find(row=>row.t===t&&row.q===q);assert.ok(expected);
        if(width<500)await button.tap();else await button.click();
        assert.equal(await page.locator('#sho-order').getAttribute('data-order'),String(expected.order));
        assert.deepEqual(await page.locator('#sho-terms td code').allTextContents(),expected.first_eight);
        assert.equal(await button.getAttribute('aria-pressed'),'true');await fit(page);
      }
      await page.locator('#sho-t').fill('0');await page.locator('#sho-q').focus();await page.keyboard.press('Enter');
      assert.equal(await page.locator('#sho-t').getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#sho-error').isVisible(),true);assert.equal(await page.locator('#sho-results').isVisible(),false);
      assert.equal(await page.locator('#sho-t').evaluate(node=>node===document.activeElement),true);
      await page.locator('#sho-form [data-order-t="8/9"]').click();
      const permalink=await page.locator('#sho-link').getAttribute('href');
      const restored=await context.newPage();restored.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await restored.goto(permalink);await restored.waitForFunction(()=>document.querySelector('[data-hankel-orders]')?.dataset.ordersReady==='true');
      assert.equal(await restored.locator('#sho-order').getAttribute('data-order'),'104');
      assert.equal(await restored.locator('#sho-t').inputValue(),'8/9');assert.equal(await restored.locator('#sho-q').inputValue(),'-16/9');
      await fit(restored);await restored.close();
      await page.locator('#interior-order-calculator').evaluate(node=>node.scrollIntoView({block:'start',behavior:'instant'}));
      await fit(page);await page.screenshot({path:path.join(output,'orders-'+width+'.png')});
      assert.ok(await page.locator('#exceptional-orders-proof mjx-container').count()>70);
      assert.equal(await page.locator('#exceptional-proof-1-statement-and-complete-boundary-table').count(),1);
      const boundaries=await page.locator('#boundary-examples tbody th a').evaluateAll(nodes=>nodes.map(node=>node.href));
      assert.equal(boundaries.length,6);
      assert.deepEqual(await page.locator('#boundary-examples tbody tr td:nth-child(2)').allTextContents(),['42','26','18','28','12','7']);
      const ids=await page.locator('[id]').evaluateAll(nodes=>nodes.map(node=>node.id));
      assert.equal(new Set(ids).size,ids.length);
      for(const href of await page.locator('a[href^="#"]').evaluateAll(nodes=>nodes.map(node=>node.getAttribute('href'))))
        assert.equal(await page.locator('[id="'+href.slice(1)+'"]').count(),1,href);
      const examples=await page.locator('#hankel-compression-intro tbody th a').evaluateAll(nodes=>nodes.map(node=>node.href));
      assert.equal(examples.length,2);
      await page.locator('#hankel-compression-intro').evaluate(node=>node.scrollIntoView({block:'start',behavior:'instant'}));
      await fit(page);await page.screenshot({path:path.join(output,'reading-'+width+'.png')});
      await page.locator('#exceptional-proof-1-statement-and-complete-boundary-table').evaluate(node=>node.scrollIntoView({block:'start',behavior:'instant'}));
      await fit(page);
      await page.screenshot({path:path.join(output,'boundary-'+width+'.png')});
      const outline=page.locator('#parity-compression-proof .sl-proof-outline>summary');
      await outline.focus();await page.keyboard.press('Enter');
      assert.equal(await page.locator('#parity-compression-proof .sl-proof-outline').evaluate(node=>node.open),true);
      await page.locator('#parity-proof-4-uniform-full-sequence-order-at-most-126').evaluate(node=>node.scrollIntoView({block:'start',behavior:'instant'}));
      await fit(page);
      if(width===320){await page.evaluate(()=>document.documentElement.style.fontSize='200%');await fit(page);}
      for(const [i,preset] of [...examples,...boundaries].entries()){
        const worksheet=await context.newPage();worksheet.on('pageerror',error=>report.errors.push({width,message:error.message}));
        await worksheet.goto(preset);await worksheet.locator('#cf-mode').waitFor({state:'visible'});
        await worksheet.waitForFunction(()=>document.querySelectorAll('#cf-table-values tr').length===12);
        const values=await worksheet.locator('#cf-table-values tr td code').allTextContents();
        const expected=i===0?['1','1','4','56','-1400','234000','92664000','13067049600']:
          i===1?['1','1','0','-256','44536','3886128','-567844864','-82121781248']:boundaryValues[i-2];
        assert.deepEqual(values.slice(0,8),expected);
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
    assert.ok((await page.locator('#sharp-quadratic-proof').textContent()).includes('Theorem K'));
    assert.ok((await page.locator('#uniform-mixed-proof').textContent()).includes('Theorem L'));
    assert.ok((await page.locator('#exceptional-orders-proof').textContent()).includes('Theorem M'));
    assert.ok((await page.locator('#interior-orders-proof').textContent()).includes('Theorem N'));
    assert.equal(await page.locator('#sho-form').isVisible(),false);
    assert.equal(await page.locator('#sho-order').getAttribute('data-order'),'98');
    assert.equal(await page.locator('#sho-terms tr').count(),8);
    assert.equal(await page.locator('#boundary-examples tbody tr').count(),6);
    assert.equal(await page.locator('#hankel-compression-intro tbody tr').count(),2);
    assert.ok(await page.locator('.sl-math-display').count()>25);await fit(page,true);
    report.noJavaScript=true;await context.close();assert.deepEqual(report.errors,[]);report.status='passed';
  }catch(error){report.failure=error.stack||String(error);throw error;}
  finally{fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();}
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error.stack||error);process.exit(1)});
