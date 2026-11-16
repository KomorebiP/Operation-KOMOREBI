/* Browser reading/workspace checks; run against a focused preview or deployed site. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8829/',out=process.argv[3]||'atlas-interface-browser';
fs.mkdirSync(out,{recursive:true});
const ready=page=>page.locator('[data-interface-ready="true"]').waitFor();
async function mode(page,id){await page.locator(`[data-atlas-mode="${id}"]`).click();assert.equal(await page.locator('[data-atlas-panel]:visible').count(),1);assert.equal(await page.locator(`#${id}`).isVisible(),true);}
async function fits(page){await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))});const b=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));assert.ok(b.scroll<=b.width+1,JSON.stringify(b));return b;}
async function inspect(page,n){await page.locator('#sa-term-index').fill(String(n));await page.locator('#sa-term-form button').click();}
(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true});
  const report={widths:[],entryChecks:[],mathChecks:[],errors:[]};
  let data;
  for(const width of [1440,390,320]){
    const context=await browser.newContext({viewport:{width,height:1000},permissions:['clipboard-read','clipboard-write'],isMobile:width<500,hasTouch:width<500});
    const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
    await page.goto(new URL('sequence-explorer.html',base).href,{waitUntil:'networkidle'});await ready(page);
    if(!data)data=await(await page.request.get(new URL('assets/sequence-atlas-data.json',base).href)).json();
    assert.equal(await page.locator('[data-atlas-panel]:visible').count(),1);assert.equal(await page.locator('#find').isVisible(),true);
    for(const [query,expected]of [['sequence=KSEQ-000025','explorer'],['discover=0,1,4,9,16,25','discover']]){
      await page.goto(new URL('sequence-explorer.html?'+query,base).href,{waitUntil:'networkidle'});await ready(page);assert.equal(await page.locator('#'+expected).isVisible(),true);
      await mode(page,'find');await page.goBack();assert.equal(await page.locator('#'+expected).isVisible(),true);
    }
    await page.goto(new URL('sequence-explorer.html',base).href,{waitUntil:'networkidle'});await ready(page);
    await fits(page);await page.screenshot({path:path.join(out,`browse-${width}.png`)});
    await mode(page,'discover');await page.locator('#sa-discovery-example').click();
    const odd=page.locator('#sa-discovery-results li').filter({has:page.getByRole('heading',{name:'Positive odd numbers',exact:true})}).first();
    await odd.getByRole('button',{name:'Plot catalogue match',exact:true}).click();assert.equal(await page.locator('#explorer').isVisible(),true);assert.equal(await page.inputValue('#sa-sequence'),'KSEQ-000028');
    await page.goBack();assert.equal(await page.locator('#discover').isVisible(),true);assert.ok((await page.locator('#sa-discovery-status').textContent()).includes('8 input terms'));
    await mode(page,'find');await page.locator('#sa-query').fill('n:4 r:2');assert.equal(await page.locator('#sa-results [data-hit-id]').count(),1);
    await page.locator('#sa-results [data-load]').click();assert.equal(await page.locator('#explorer').isVisible(),true);await fits(page);
    await page.locator('#sa-plot').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`plot-${width}.png`)});
    await mode(page,'catalogue');assert.equal(await page.locator('[data-index-entry]:visible').count(),38);
    await mode(page,'reference');assert.ok((await page.locator('#reference').textContent()).includes('CC BY-SA'));
    await page.keyboard.press('Control+/');assert.equal(await page.locator('#find').isVisible(),true);assert.equal(await page.evaluate(()=>document.activeElement.id),'sa-query');
    report.widths.push({width,...await fits(page),workspaceNavigation:true,history:true,shortcut:true,fullCatalogue:true});
    for(const id of ['KSEQ-000007','KSEQ-000026','KSEQ-000034']){
      const entry=data.entries.find(e=>e.id===id);
      await page.goto(new URL(`sequences/${id}.html#definition`,base).href,{waitUntil:'networkidle'});await page.locator('[data-entry-ready="true"]').waitFor();
      await page.locator('[data-math-ready="true"]').waitFor({timeout:20000});assert.equal(await page.locator('.sa-typeset [data-mml-node="merror"]').count(),0);
      assert.equal(await page.locator('#data tbody tr').count(),64);assert.equal(await page.locator('.sa-index-map tbody tr').count(),6);
      assert.equal((await page.locator('.sa-definition-lede').textContent()),entry.reading.definition);
      await inspect(page,2);assert.equal(await page.locator('#sa-term-value').textContent(),entry.terms[2]);
      if(id==='KSEQ-000007')assert.ok((await page.locator('#sa-term-basis').textContent()).includes('23/13440'));
      if(id==='KSEQ-000026')assert.ok((await page.locator('#sa-term-basis').textContent()).includes('E_(4)'));
      await inspect(page,64);assert.equal(await page.locator('#sa-term-index').getAttribute('aria-invalid'),'true');
      await inspect(page,63);assert.equal(await page.locator('#sa-term-error').isVisible(),false);assert.equal(await page.locator('#sa-term-value').textContent(),entry.terms[63]);
      await page.locator('#sa-term-copy').click();assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),entry.terms[63]);
      await page.locator('#sa-term-data-link').click();assert.equal(new URL(page.url()).hash,'#n-63');assert.equal(await page.locator('#n-63').getAttribute('aria-current'),'true');
      await page.locator('#sa-entry-link').click();assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).endsWith('#n-63'));
      await page.locator('[data-copy-entry="sa-entry-formula"]').click();assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),entry.formula);
      await page.goto(new URL(`sequences/${id}.html`,base).href,{waitUntil:'networkidle'});await page.locator('[data-math-ready="true"]').waitFor();
      await fits(page);await page.screenshot({path:path.join(out,`entry-${id}-${width}.png`)});
      if(id==='KSEQ-000007'){await page.locator('#definition').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,`definition-${width}.png`)});}
      report.entryChecks.push({id,width,definition:true,indexMap:true,typeset:true,inspector:true,exactCopy:true,termDeepLink:true});
    }
    await page.locator('#sa-record-query').fill('n:4 r:2');await page.locator('.sa-record-search button').click();await page.locator('[data-library-ready="true"]').waitFor();assert.equal(await page.inputValue('#sl-query'),'n:4 r:2');assert.equal(await page.locator('#sl-results [data-result-id="KSEQ-000008"]').count(),1);
    if(width===1440){
      for(const entry of data.entries){await page.goto(new URL(`sequences/${entry.id}.html`,base).href,{waitUntil:'networkidle'});await page.locator('[data-math-ready="true"]').waitFor({timeout:20000});assert.equal(await page.locator('.sa-typeset [data-mml-node="merror"]').count(),0);assert.equal(await page.locator('.sa-typeset mjx-container').count(),1);report.mathChecks.push(entry.id);}
    }
    await context.close();
  }
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:1000}}),page=await nojs.newPage();
  await page.goto(new URL('sequences/KSEQ-000007.html#definition',base).href);assert.equal(await page.locator('.sa-definition-lede').isVisible(),true);assert.equal(await page.locator('.sa-record-search').isVisible(),false);assert.equal(await page.locator('.sa-plain-formula').getAttribute('open'),'');assert.equal(await page.locator('.sa-index-map tbody tr').count(),6);assert.equal(await page.locator('#data tbody tr').count(),64);const nb=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));assert.ok(nb.scroll<=nb.width+1,JSON.stringify(nb));report.noJavaScript=true;await nojs.close();
  const hc=await browser.newContext({viewport:{width:320,height:1000},forcedColors:'active',reducedMotion:'reduce'}),hp=await hc.newPage();hp.on('pageerror',e=>report.errors.push(e.message));
  await hp.goto(new URL('sequence-explorer.html',base).href,{waitUntil:'networkidle'});await ready(hp);await hp.addStyleTag({content:'html{font-size:200%!important}'});await mode(hp,'discover');await fits(hp);await hp.screenshot({path:path.join(out,'workspace-high-contrast.png')});
  await hp.goto(new URL('sequences/KSEQ-000007.html#definition',base).href,{waitUntil:'networkidle'});await hp.locator('[data-math-ready="true"]').waitFor();await hp.addStyleTag({content:'html{font-size:200%!important}'});await fits(hp);await hp.screenshot({path:path.join(out,'definition-high-contrast.png')});report.highContrastEnlarged=true;await hc.close();
  const fallback=await browser.newContext({viewport:{width:390,height:1000}});await fallback.route('**/assets/mathjax/**',route=>route.abort());const fp=await fallback.newPage();
  await fp.goto(new URL('sequences/KSEQ-000034.html',base).href,{waitUntil:'networkidle'});await fp.locator('[data-entry-ready="true"]').waitFor();assert.equal(await fp.locator('.sa-plain-formula').getAttribute('open'),'');assert.equal(await fp.locator('#sa-entry-formula').isVisible(),true);await inspect(fp,2);assert.equal(await fp.locator('#sa-term-value').textContent(),'2');report.mathRuntimeFallback=true;await fallback.close();
  assert.deepEqual(report.errors,[]);await browser.close();fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({widths:report.widths.length,entryChecks:report.entryChecks.length,mathChecks:report.mathChecks.length,noJavaScript:true,highContrastEnlarged:true,mathRuntimeFallback:true,errors:report.errors}));
})().catch(error=>{console.error(error);process.exit(1)});
