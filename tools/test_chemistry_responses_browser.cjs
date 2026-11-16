/* Windows Edge automation; no physical-device or assistive-technology claim. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8769/',out=process.argv[3]||'chemistry-response-browser';
const settled=p=>p.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
const cert=p=>p.locator('#cr-certificate').textContent().then(JSON.parse);
async function main(){
  fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true,channel:'msedge'}),checks=[];
  try{
    for(const [name,width,height]of [['desktop',1440,1000],['phone',390,844],['narrow',320,800]]){
      const context=await browser.newContext({viewport:{width,height},acceptDownloads:true}),p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(String(e)));
      const response=await p.goto(new URL('chemistry-responses.html',base).href);assert.equal(response.status(),200);await p.locator('#cr-explorer').waitFor({state:'visible'});await settled(p);
      assert.equal(await p.locator('main h1').count(),1);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
      assert.equal((await cert(p)).settings.order,128);assert.match(await p.locator('#cr-discrepancy').textContent(),/differ by at least/);
      await p.locator('#cr-energy').focus();await p.keyboard.press('ArrowRight');assert.equal((await cert(p)).settings.index,21);assert.equal(await p.evaluate(()=>document.activeElement.id),'cr-energy');
      await p.locator('#cr-order').selectOption('9');await p.locator('#cr-eta').selectOption('1/100');assert.match(await p.locator('#cr-plot-note').textContent(),/extend beyond/);
      await p.locator('#cr-energy').evaluate(x=>{x.value='40';x.dispatchEvent(new Event('input',{bubbles:true}));});
      const before=(await cert(p)).settings,url=await p.locator('#cr-link').getAttribute('href');await p.goto(new URL(url,base).href);await p.locator('#cr-explorer').waitFor({state:'visible'});assert.deepEqual((await cert(p)).settings,before);
      const pending=p.waitForEvent('download');await p.locator('#cr-download').click();const download=await pending,target=path.join(out,name+'-certificate.json');await download.saveAs(target);assert.deepEqual(JSON.parse(fs.readFileSync(target)),await cert(p));
      await p.locator('#cr-reset').click();await p.locator('.cr-controls').evaluate(x=>window.scrollTo(0,x.getBoundingClientRect().top+scrollY-35));await settled(p);await p.screenshot({path:path.join(out,name+'-scan.png')});
      await p.locator('#cr-reduction').evaluate(x=>window.scrollTo(0,x.getBoundingClientRect().top+scrollY-35));await p.screenshot({path:path.join(out,name+'-reduction.png')});
      for(const summary of await p.locator('.cr-page details>summary').all()){await summary.focus();await p.keyboard.press('Enter');}
      await settled(p);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'expanded overflow');assert.equal(await p.locator('.cr-page table:not(:has(caption))').count(),0);
      for(const table of await p.locator('.cr-table').all())if(await table.evaluate(x=>x.scrollWidth>x.clientWidth+3)){await table.focus();await p.keyboard.press('ArrowRight');await p.waitForTimeout(100);assert.ok(await table.evaluate(x=>x.scrollLeft>0));}
      if(name==='narrow'){await p.evaluate(()=>document.documentElement.style.fontSize='200%');await settled(p);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'enlarged text overflow');}
      assert.deepEqual(errors,[]);checks.push({viewport:name,width,keyboard:true,permalink:true,download:true,overflow:false,scriptErrors:errors});await context.close();
    }
    const plain=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:800}}),p=await plain.newPage();await p.goto(new URL('chemistry-responses.html',base).href);assert.match(await p.locator('main').innerText(),/37.506%/);assert.ok(await p.locator('.cr-table').count()>=5);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await plain.close();
    const forced=await browser.newContext({forcedColors:'active',reducedMotion:'reduce',viewport:{width:320,height:800}}),f=await forced.newPage();await f.goto(new URL('chemistry-responses.html',base).href);await f.locator('#cr-explorer').waitFor({state:'visible'});await f.locator('#cr-energy').focus();await f.keyboard.press('ArrowLeft');assert.equal((await cert(f)).settings.index,19);await forced.close();
    const broken=await browser.newContext(),b=await broken.newPage();await b.route('**/assets/chemistry/responses-v1.json*',r=>r.fulfill({contentType:'application/json',body:'{}'}));await b.goto(new URL('chemistry-responses.html',base).href);await b.locator('#cr-retry').waitFor({state:'visible'});assert.equal(await b.locator('#cr-explorer').isVisible(),false);await b.unroute('**/assets/chemistry/responses-v1.json*');await b.locator('#cr-retry').click();await b.locator('#cr-explorer').waitFor({state:'visible'});await broken.close();
    const report={status:'passed',base,checks,noJavaScript:true,forcedColorsAndReducedMotion:true,identityFailureAndRetry:true,enlargedText320:true};fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
