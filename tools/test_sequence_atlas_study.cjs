/* Study controls, exact exports and reading fallbacks against preview or Pages. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8830/',out=process.argv[3]||'atlas-study-browser';
fs.mkdirSync(out,{recursive:true});
const ready=page=>page.locator('[data-study-ready="true"]').waitFor();
async function fits(page,js=true){if(js)await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))});const bounds=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));assert.ok(bounds.scroll<=bounds.width+1,JSON.stringify(bounds));return bounds;}
async function apply(page,mode,start=0,count=12,modulus=7){await page.locator('#sa-study-transform').selectOption(mode);await page.locator('#sa-study-start').fill(String(start));await page.locator('#sa-study-count').fill(String(count));if(mode==='mod')await page.locator('#sa-study-modulus').fill(String(modulus));await page.locator('#sa-study-form button').click();}
async function download(page,name){const event=page.waitForEvent('download');await page.locator('#sa-study-'+name).click();const file=await event,target=path.join(out,file.suggestedFilename());await file.saveAs(target);return fs.readFileSync(target,'utf8');}
async function values(page){return page.locator('#sa-study-values tbody tr td').allTextContents();}
(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true}),report={widths:[],errors:[]};
  for(const width of [1440,390,320]){
    const context=await browser.newContext({viewport:{width,height:1000},permissions:['clipboard-read','clipboard-write'],isMobile:width<500,hasTouch:width<500});
    const page=await context.newPage();page.on('pageerror',error=>report.errors.push(error.message));
    await page.goto(new URL('sequence-explorer.html?q=triangular#find',base).href,{waitUntil:'networkidle'});
    await page.getByRole('link',{name:'Study exact terms for Triangular numbers',exact:true}).click();await ready(page);
    assert.equal(await page.locator('#sa-study-values tbody tr').count(),12);assert.deepEqual((await values(page)).slice(0,5),['0','1','3','6','10']);
    await apply(page,'second-difference');assert.deepEqual((await values(page)).slice(0,4),['undefined','undefined','1','1']);
    await page.locator('.sa-study-differences summary').click();assert.match(await page.locator('#sa-study-observation').textContent(),/Order 2.*constant \(1\).*10 tested indices/);
    await page.locator('#sa-study-copy').click();assert.match((await page.evaluate(()=>navigator.clipboard.readText())).replace(/\r\n/g,'\n'),/^0 undefined\n1 undefined\n2 1/);
    assert.equal(new URL(await page.locator('#sa-study-search').getAttribute('href')).searchParams.get('q'),'1,1,1,1,1,1,1,1');
    await page.locator('#sa-study-plot').click();await page.locator('[data-interface-ready="true"]').waitFor();assert.equal(await page.inputValue('#sa-transform'),'second-difference');assert.equal(await page.inputValue('#sa-view'),'standard');
    await page.goBack();await ready(page);assert.equal(await page.inputValue('#sa-study-transform'),'second-difference');
    await apply(page,'sum',9,16);assert.equal((await values(page))[0],'165');
    const csv=await download(page,'csv');assert.match(csv,/^n,value,defined\n9,165,true\n/);
    const json=JSON.parse(await download(page,'json'));assert.equal(json.entry,'KSEQ-000029');assert.equal(json.rows[0].n,9);assert.equal(json.rows[0].value,'165');assert.match(json.conventions,/finite/);
    await page.locator('#sa-study-share').click();const shared=await page.evaluate(()=>navigator.clipboard.readText());assert.equal(new URL(shared).searchParams.get('from'),'9');
    await page.goto(shared,{waitUntil:'networkidle'});await ready(page);assert.equal((await values(page))[0],'165');
    await apply(page,'raw',0,12);await page.goBack();assert.equal(await page.inputValue('#sa-study-transform'),'sum');assert.equal((await values(page))[0],'165');
    await page.locator('#sa-study-next').click();assert.equal(await page.inputValue('#sa-study-start'),'25');await page.locator('#sa-study-previous').click();assert.equal(await page.inputValue('#sa-study-start'),'9');
    await apply(page,'raw',62,12);assert.equal(await page.locator('#sa-study-error').isVisible(),true);assert.equal(await page.locator('#sa-study-count').getAttribute('aria-invalid'),'true');assert.equal((await values(page))[0],'165');
    await apply(page,'raw');assert.equal(await page.locator('#sa-study-error').isVisible(),false);assert.equal(await page.locator('#sa-study-count').getAttribute('aria-invalid'),null);
    await page.locator('#sa-entry-copy').click();assert.equal((await page.evaluate(()=>navigator.clipboard.readText())).split(', ').length,12);
    await page.locator('#analysis').evaluate(el=>el.scrollIntoView());await fits(page);await page.screenshot({path:path.join(out,`study-${width}.png`)});
    await page.goto(new URL('sequences/KSEQ-000025.html?study=ratio#analysis',base).href,{waitUntil:'networkidle'});await ready(page);
    assert.deepEqual((await values(page)).slice(0,6),['undefined','undefined','1','2','3/2','5/3']);assert.match(await page.locator('#sa-study-facts').textContent(),/noninteger/);
    assert.equal(await page.locator('#sa-study-discover').isVisible(),false);
    await apply(page,'ratio',0,2);assert.equal(await page.locator('#sa-study-plot').isVisible(),false);assert.equal(await page.locator('#sa-study-search').isVisible(),false);assert.deepEqual(await values(page),['undefined','undefined']);
    await page.goto(new URL('sequences/KSEQ-000026.html?study=mod&mod=7#analysis',base).href,{waitUntil:'networkidle'});await ready(page);assert.equal((await values(page))[1],'6');
    await page.goto(new URL('sequences/KSEQ-000007.html?study=raw&from=52&size=12#analysis',base).href,{waitUntil:'networkidle'});await ready(page);assert.equal(await page.locator('#sa-study-discover').isVisible(),false);await fits(page);
    assert.equal(new URL(await page.locator('#sa-study-plot').getAttribute('href')).searchParams.get('scale'),'signed-log');await page.locator('#sa-study-plot').click();await page.locator('[data-interface-ready="true"]').waitFor();assert.equal(await page.inputValue('#sa-scale'),'signed-log');assert.equal(await page.locator('#sa-error').isVisible(),false);assert.equal(await page.locator('#sa-plot [data-point]').count(),12);
    await page.goto(new URL('sequences/KSEQ-000029.html?study=unknown&from=999#analysis',base).href,{waitUntil:'networkidle'});await ready(page);assert.equal(await page.locator('#sa-study-error').isVisible(),true);assert.equal((await values(page))[0],'0');
    for(const mode of ['raw','difference','second-difference','sum','ratio','average','alternating','absolute','binomial','inverse-binomial','mod']){await apply(page,mode);assert.equal(await page.locator('#sa-study-error').isVisible(),false);}
    await page.locator('#sa-study-modulus').fill('');await page.locator('#sa-study-form button').click();assert.equal(await page.locator('#sa-study-error').isVisible(),true);await apply(page,'raw');assert.equal(await page.locator('#sa-study-error').isVisible(),false);
    report.widths.push({width,...await fits(page),transforms:11,copy:true,exactExports:true,shareRestore:true,history:true,searchLink:true,plotLink:true,paging:true,invalidRecovery:true,largeValues:true});
    await context.close();
  }
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:1000}}),plain=await nojs.newPage();
  await plain.goto(new URL('sequences/KSEQ-000029.html#analysis',base).href,{waitUntil:'networkidle'});assert.equal(await plain.locator('#sa-study-form').isVisible(),false);assert.equal(await plain.locator('#sa-study-values tbody tr').count(),12);await plain.locator('.sa-study-differences summary').click();assert.equal(await plain.locator('#sa-study-differences tbody tr').count(),5);await fits(plain,false);report.noJavaScript=true;await nojs.close();
  const hc=await browser.newContext({viewport:{width:320,height:1000},forcedColors:'active',reducedMotion:'reduce'}),enlarged=await hc.newPage();
  await enlarged.goto(new URL('sequences/KSEQ-000007.html#analysis',base).href,{waitUntil:'networkidle'});await ready(enlarged);await enlarged.evaluate(()=>document.documentElement.style.fontSize='200%');await fits(enlarged);await enlarged.locator('#analysis').evaluate(el=>el.scrollIntoView());await enlarged.screenshot({path:path.join(out,'study-high-contrast.png')});report.highContrastEnlarged=true;await hc.close();
  const denied=await browser.newContext({viewport:{width:390,height:1000}});await denied.addInitScript(()=>Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>{throw Error('Denied');}}}));const fallback=await denied.newPage();
  await fallback.goto(new URL('sequences/KSEQ-000029.html#analysis',base).href,{waitUntil:'networkidle'});await ready(fallback);await fallback.locator('#sa-study-copy').click();assert.equal(await fallback.locator('#sa-study-copy-fallback').isVisible(),true);assert.match(await fallback.inputValue('#sa-study-copy-text'),/^0 0\n1 1/);assert.equal(await fallback.evaluate(()=>document.activeElement.id),'sa-study-copy-text');report.deniedClipboardFallback=true;await denied.close();
  assert.deepEqual(report.errors,[]);fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exit(1)});
