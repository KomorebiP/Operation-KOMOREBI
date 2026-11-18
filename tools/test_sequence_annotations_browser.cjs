const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'sequence-chart-annotations';
fs.mkdirSync(output,{recursive:true});
const href=relative=>new URL(relative,base).href;
async function fit(page){
  await page.evaluate(async()=>{await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true,'Unexpected plot page overflow: '+page.url());
}
(async()=>{
  const browser=await chromium.launch({headless:true}),report={status:'running',widths:[],errors:[]};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940},permissions:['clipboard-read','clipboard-write']});
      const errors=[],page=await context.newPage();page.on('pageerror',err=>errors.push(err.message));
      await page.goto(href('sequence-explorer.html#explorer'));
      await page.locator('#sequence-atlas[data-interface-ready=true]').waitFor({timeout:90000});
      await page.locator('.sa-advanced>summary').click();
      await page.selectOption('#sa-sequence','KSEQ-000025');
      await page.selectOption('#sa-view','standard');
      await page.selectOption('#sa-scale','signed-log');
      const atlas=page.locator('#sa-plot svg');
      await atlas.waitFor();
      assert.equal(await page.locator('#sa-chart-labels').evaluate(el=>el.open),false);
      await page.locator('#sa-chart-labels>summary').click();
      await page.locator('#sa-chart-title').fill('Fibonacci exact profile');
      await page.locator('#sa-chart-title').press('Tab');
      await page.locator('#sa-chart-xTitle').fill('Recurrence step');
      await page.locator('#sa-chart-xTitle').press('Tab');
      await page.locator('#sa-chart-yTitle').fill('Signed approximate magnitude');
      await page.locator('#sa-chart-yTitle').press('Tab');
      await page.selectOption('#sa-chart-ticks','scientific');
      await page.selectOption('#sa-chart-legendStyle','id');
      assert.equal(await atlas.locator('[data-chart-title]').getAttribute('aria-label'),'Fibonacci exact profile');
      assert.equal(await atlas.locator('[data-x-axis-title]').getAttribute('aria-label'),'Recurrence step');
      assert.equal(await atlas.locator('[data-y-axis-title]').getAttribute('aria-label'),'Signed approximate magnitude');
      assert.ok((await atlas.locator('[data-y-tick]').allTextContents()).some(v=>v.includes('×10^')));
      assert.match(await page.locator('.sp-scale-explanation').textContent(),/scientific notation/);
      assert.match(await atlas.locator('[data-legend-label]').first().textContent(),/KSEQ-000025/);
      await page.locator('#sa-share').click();
      const atlasLink=await page.evaluate(()=>navigator.clipboard.readText());
      assert.equal(new URL(atlasLink).searchParams.get('chart-title'),'Fibonacci exact profile');
      assert.equal(new URL(atlasLink).searchParams.get('chart-ticks'),'scientific');
      const atlasRestored=await context.newPage();atlasRestored.on('pageerror',err=>errors.push(err.message));
      await atlasRestored.goto(atlasLink);
      await atlasRestored.locator('#sequence-atlas[data-interface-ready=true]').waitFor({timeout:90000});
      assert.equal(await atlasRestored.locator('#sa-chart-title').inputValue(),'Fibonacci exact profile');
      assert.equal(await atlasRestored.locator('#sa-chart-ticks').inputValue(),'scientific');
      assert.equal(await atlasRestored.locator('#sa-chart-legendStyle').inputValue(),'id');
      assert.equal(await atlasRestored.locator('#sa-plot [data-chart-title]').getAttribute('aria-label'),'Fibonacci exact profile');
      await fit(atlasRestored);await atlasRestored.close();
      await fit(page);

      await page.goto(href('sequence-archive/KOM067.html#plot'));
      await page.locator('[data-archive-ready=true]').waitFor({timeout:90000});
      await page.selectOption('#sar-view','raw');
      await page.locator('#sar-plot-form button[type=submit]').click();
      await page.selectOption('#sar-scale','signed-log');
      await page.locator('#sar-plot-form button[type=submit]').click();
      await page.locator('#sar-chart-labels>summary').click();
      await page.locator('#sar-chart-title').fill('Archived coefficient profile');
      await page.locator('#sar-chart-title').press('Tab');
      await page.selectOption('#sar-chart-legend','show');
      await page.selectOption('#sar-chart-legendStyle','id');
      await page.selectOption('#sar-chart-ticks','scientific');
      const archived=page.locator('#sar-plot svg');
      assert.equal(await archived.locator('[data-chart-title]').getAttribute('aria-label'),'Archived coefficient profile');
      assert.ok((await archived.locator('[data-y-tick]').allTextContents()).some(v=>v.includes('×10^')));
      assert.match(await archived.locator('[data-legend-label]').first().textContent(),/KOM067/);
      await page.locator('#sar-view-link').click();
      const archiveLink=await page.evaluate(()=>navigator.clipboard.readText());
      const aURL=new URL(archiveLink);
      assert.equal(aURL.searchParams.get('chart-title'),'Archived coefficient profile');
      assert.equal(aURL.searchParams.get('chart-legendStyle'),'id');
      const archiveRestored=await context.newPage();archiveRestored.on('pageerror',err=>errors.push(err.message));
      await archiveRestored.goto(archiveLink);
      await archiveRestored.locator('[data-archive-ready=true]').waitFor({timeout:90000});
      assert.equal(await archiveRestored.locator('#sar-chart-ticks').inputValue(),'scientific');
      assert.equal(await archiveRestored.locator('#sar-chart-title').inputValue(),'Archived coefficient profile');
      assert.match(await archiveRestored.locator('#sar-plot [data-legend-label]').textContent(),/KOM067/);
      await fit(archiveRestored);await archiveRestored.close();
      if(width===1440){
        const download=page.waitForEvent('download');await page.locator('#sar-svg').click();
        const artifact=await download;const destination=path.join(output,'archive-chart-custom.svg');
        await artifact.saveAs(destination);const svg=fs.readFileSync(destination,'utf8');
        assert.match(svg,/Archived coefficient profile/);assert.match(svg,/KOM067/);
      }
      await fit(page);

      await page.goto(href('sequence-compare.html#comparison'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      await page.locator('#sw-example').click();
      await page.locator('#sw-chart-labels>summary').click();
      await page.selectOption('#sw-legend-style','id');
      assert.match(await page.locator('#sw-chart [data-legend-label]').first().textContent(),/KSEQ-000025/);
      await page.selectOption('#sw-legend-style','full');
      assert.match(await page.locator('#sw-chart [data-legend-label]').first().textContent(),/KSEQ-000025/);
      await page.selectOption('#sw-tick-mode','scientific');
      assert.ok((await page.locator('#sw-chart [data-y-tick]').allTextContents()).some(v=>v.includes('×10^')));
      await fit(page);
      report.widths.push({width,atlasShare:true,archiveShare:true,scientificTicks:true,compactLegends:true,noOverflow:true,errors});
      assert.deepEqual(errors,[]);
      await context.close();
    }
    const context=await browser.newContext({viewport:{width:320,height:940},javaScriptEnabled:false});
    const noJS=await context.newPage();await noJS.goto(href('sequence-archive/KOM067.html'));
    assert.ok(await noJS.locator('#exact-data table tbody tr').count()>0,'Exact archive table must work without JavaScript');
    await fit(noJS);await context.close();
    report.noJavaScript=true;report.status='passed';console.log(JSON.stringify(report));
  }finally{fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
