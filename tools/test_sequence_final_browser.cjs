const {chromium}=require('playwright');const fs=require('node:fs');const path=require('node:path');
const assert=require('node:assert/strict');const crypto=require('node:crypto');
const base=process.argv[2],out=process.argv[3];if(!base||!out)throw Error('Usage: node test_sequence_final_browser.cjs BASE_URL OUTPUT');
fs.mkdirSync(out,{recursive:true});
const receipt=JSON.parse(fs.readFileSync(path.join(__dirname,'../research/sequence-closed-forms/final-edition/v1.0/ARTIFACTS.json'),'utf8'));
const url=name=>new URL(name,base).href;
async function fit(page,math=true){
 if(math)await page.evaluate(async()=>{await MathJax.startup.promise;await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
 else{
  let ready=false;
  for(let attempt=0;attempt<100;attempt++){
   if(await page.evaluate(()=>document.fonts.status==='loaded')){ready=true;break;}
   await new Promise(resolve=>setTimeout(resolve,50));
  }
  assert.ok(ready,'Static document fonts did not settle');
 }
 const size=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
 assert.ok(size.scroll<=size.width+1,JSON.stringify(size));
}
(async()=>{const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH}:{})});
const report={widths:[],errors:[],noJavaScript:false,offlineHTML:false};
const step=name=>{report.phase=name;fs.writeFileSync(path.join(out,'progress.json'),JSON.stringify(report,null,2)+'\n');console.log(name);};
try{
 for(const width of [1440,390,320]){
  step('Reader width '+width);
  const context=await browser.newContext({viewport:{width,height:950},hasTouch:width<500,isMobile:width<500});
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  assert.ok((await page.goto(url('sequence-hankel-final.html'))).ok());await fit(page);
  assert.equal(await page.locator('main h1').count(),1);
  assert.equal(await page.locator('.sf-paper mjx-container').count(),638);
  assert.equal(await page.locator('mjx-merror, merror, [data-mml-node="merror"]').count(),0);
  const anchors=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return {duplicates:ids.length-new Set(ids).size,missing:[...document.querySelectorAll('a[href^="#"]')].map(x=>x.hash.slice(1)).filter(x=>!document.getElementById(x))};});
  assert.equal(anchors.duplicates,0);assert.deepEqual(anchors.missing,[]);
  const outline=page.locator('.sl-proof-outline>summary');
  if(width<500)await outline.tap();else{await outline.focus();await page.keyboard.press('Enter');}
  assert.equal(await page.locator('.sl-proof-outline').evaluate(x=>x.open),true);
  if(width<500)await outline.tap();else await page.keyboard.press('Enter');
  assert.equal(await page.locator('.sl-proof-outline').evaluate(x=>x.open),false);
  await page.locator('.sf-paper h1').evaluate(x=>x.scrollIntoView({block:'start',behavior:'instant'}));await fit(page);
  await page.screenshot({path:path.join(out,'paper-'+width+'.png')});
  await page.locator('#final-4-the-coordinate-boundary').evaluate(x=>x.scrollIntoView({block:'start',behavior:'instant'}));await fit(page);
  await page.screenshot({path:path.join(out,'boundary-'+width+'.png')});
  if(width===320){
   step('Keyboard scroll and enlarged text');
   const index=await page.locator('.sl-math-display').evaluateAll(nodes=>nodes.findIndex(x=>x.scrollWidth>x.clientWidth+8));assert.ok(index>=0);
   const region=page.locator('.sl-math-display').nth(index);await region.focus();await page.keyboard.press('ArrowRight');
   await page.waitForFunction(i=>document.querySelectorAll('.sl-math-display')[i].scrollLeft>0,index,{timeout:5000});
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');await fit(page);
   await page.emulateMedia({forcedColors:'active',reducedMotion:'reduce'});await fit(page);
  }
  report.widths.push(width);await context.close();
 }
 step('No-JavaScript reader');
 const staticContext=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:950}});
 const staticPage=await staticContext.newPage();assert.ok((await staticPage.goto(url('sequence-hankel-final.html'))).ok());
 for(const n of ['K','L','M','N'])assert.ok((await staticPage.locator('.sf-paper').textContent()).includes('Theorem '+n+'.'));
 assert.equal(await staticPage.locator('.sf-downloads a').count(),4);await fit(staticPage,false);report.noJavaScript=true;
 step('Offline HTML');
 const asset=await staticContext.newPage();const requests=[];await asset.route('**/*',route=>{const u=route.request().url();if(u===url('assets/weighted-central-binomial-hankel-v1.0.html'))return route.continue();requests.push(u);return route.abort();});
 assert.ok((await asset.goto(url('assets/weighted-central-binomial-hankel-v1.0.html'))).ok());await fit(asset,false);
 assert.equal(await asset.locator('mjx-container').count(),638);assert.equal(await asset.locator('script').count(),0);assert.deepEqual(requests,[]);
 await asset.keyboard.press('Tab');
 assert.equal(await asset.locator('.sf-skip').evaluate(x=>x===document.activeElement),true);
 await asset.keyboard.press('Enter');
 assert.equal(await asset.locator('#main').evaluate(x=>x===document.activeElement),true);
 await asset.evaluate(()=>document.documentElement.style.fontSize='200%');await fit(asset,false);
 report.offlineHTML=true;
 step('Frozen download hashes');
 for(const [name,key] of [['weighted-central-binomial-hankel-v1.0.pdf','PAPER.pdf'],['weighted-central-binomial-hankel-v1.0.html','PAPER.html'],['weighted-central-binomial-hankel-v1.0.md','PAPER.md']]){
  const response=await staticContext.request.get(url('assets/'+name));assert.ok(response.ok());
  assert.equal(crypto.createHash('sha256').update(await response.body()).digest('hex'),receipt.files[key]);
 }
 await staticContext.close();assert.deepEqual(report.errors,[]);report.status='passed';
}catch(error){report.failure=error.stack||String(error);throw error;}
finally{fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();}
console.log(JSON.stringify(report));
})().catch(error=>{console.error(error.stack||error);process.exit(1)});
