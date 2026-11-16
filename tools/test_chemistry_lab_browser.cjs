/* Focused browser QA; no claim of physical-device or screen-reader testing. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8768/',out=process.argv[3]||'chemistry-lab-browser';
const frames=page=>page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
const certificate=page=>page.locator('#cl-certificate').textContent().then(JSON.parse);
const setRange=(page,id,value)=>page.locator('#cl-'+id).evaluate((x,v)=>{x.value=v;x.dispatchEvent(new Event('input',{bubbles:true}));},String(value));
async function main(){
  fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true,channel:process.env.CHEMISTRY_CHROME?undefined:'msedge',executablePath:process.env.CHEMISTRY_CHROME});const checks=[];
  try{
    for(const [name,width,height]of [['desktop',1440,1000],['phone',390,844],['narrow',320,800]]){
      const context=await browser.newContext({viewport:{width,height},acceptDownloads:true});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
      const response=await page.goto(new URL('chemistry-lab.html',base).href,{waitUntil:'load'});assert.equal(response.status(),200);
      await page.locator('#cl-experiment').waitFor({state:'visible'});await frames(page);
      assert.equal(await page.locator('main h1').count(),1);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'page overflow');
      const first=await certificate(page);assert.equal(first.example,'exact');assert.equal(first.settings.probes,2);assert.equal(first.full_linear_consistent,true);
      assert.ok(Number(first.response_radius_rational_upper.split('/')[0])/Number(first.response_radius_rational_upper.split('/')[1])<.001337);
      assert.ok(Number(await page.locator('#cl-nullity').textContent())>0);
      await page.getByRole('button',{name:'3 probes',exact:true}).focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#cl-nullity').textContent(),'0');
      assert.equal(await page.evaluate(()=>document.activeElement.dataset.probes),'3');assert.equal(await page.getByRole('button',{name:'3 probes',exact:true}).getAttribute('aria-pressed'),'true');
      await page.locator('#cl-error').focus();await page.keyboard.press('ArrowRight');assert.equal((await certificate(page)).settings.error,3);assert.equal(await page.evaluate(()=>document.activeElement.id),'cl-error');
      await page.getByRole('button',{name:'Reset example',exact:true}).click();
      for(const sample of ['h10','zero','unresolved','inconsistent']){
        await page.locator('#cl-example').selectOption(sample);const c=await certificate(page);assert.equal(c.example,sample);
        if(sample==='h10')assert.ok((await page.locator('#cl-cap-note').textContent()).includes('Published H10 arithmetic'));
        if(sample==='zero')assert.equal(c.positive_integral_feasibility,true);
        if(sample==='unresolved'){
          assert.equal(c.positive_integral_feasibility,null);await setRange(page,'error',0);assert.equal((await certificate(page)).positive_integral_feasibility,false);
        }
        if(sample==='inconsistent'){
          assert.equal(c.full_linear_consistent,false);assert.equal(c.response_center,null);assert.equal(c.response_radius_rational_upper,null);
          await setRange(page,'error',7);assert.equal((await certificate(page)).full_linear_consistent,true);
        }
      }
      await page.locator('#cl-example').selectOption('exact');await setRange(page,'error',0);await setRange(page,'source',0);assert.equal((await certificate(page)).response_radius_rational_upper,'0');
      await page.getByRole('button',{name:'Reset example',exact:true}).click();await setRange(page,'eta',1);await setRange(page,'source',2);
      const url=await page.locator('#cl-permalink').getAttribute('href'),before=await certificate(page);await page.goto(url);await page.locator('#cl-experiment').waitFor({state:'visible'});assert.deepEqual((await certificate(page)).settings,before.settings);
      const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Download this experiment’s certificate',exact:true}).click();const download=await downloadPromise;const target=path.join(out,name+'-certificate.json');await download.saveAs(target);assert.deepEqual(JSON.parse(fs.readFileSync(target)),await certificate(page));
      await page.getByRole('button',{name:'Reset example',exact:true}).click();
      await page.locator('#cl-probes-title').scrollIntoViewIfNeeded();await frames(page);await page.screenshot({path:path.join(out,name+'-probes.png')});
      await page.locator('#cl-uncertainty-title').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,name+'-uncertainty.png')});
      for(const summary of await page.locator('.cl-page details>summary').all()){await summary.focus();await page.keyboard.press('Enter');}
      await frames(page);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'expanded page overflow');
      for(const table of await page.locator('.cl-table').all()){
        if(await table.evaluate(x=>x.scrollWidth>x.clientWidth+3)){await table.focus();await page.keyboard.press('ArrowRight');await page.waitForTimeout(100);assert.ok(await table.evaluate(x=>x.scrollLeft>0));}
      }
      assert.equal(await page.locator('.cl-page table:not(:has(caption))').count(),0);
      if(name==='narrow'){await page.evaluate(()=>document.documentElement.style.fontSize='200%');await frames(page);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'200% text overflow');}
      assert.deepEqual(errors,[]);checks.push({viewport:name,width,keyboard:true,examples:5,download:true,permalink:true,expandedTables:true,enlargedText:name==='narrow',scriptErrors:errors});await context.close();
    }
    const plain=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:800}}),p=await plain.newPage();await p.goto(new URL('chemistry-lab.html',base).href);assert.ok((await p.locator('#cl-worked').innerText()).includes('1/4096'));assert.equal(await p.locator('#cl-worked a').count(),6);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await plain.close();
    const forced=await browser.newContext({forcedColors:'active',reducedMotion:'reduce',viewport:{width:320,height:800}}),f=await forced.newPage();await f.goto(new URL('chemistry-lab.html',base).href);await f.locator('#cl-experiment').waitFor({state:'visible'});await f.getByRole('button',{name:'3 probes',exact:true}).click();assert.equal(await f.locator('#cl-nullity').textContent(),'0');await forced.close();
    const broken=await browser.newContext(),b=await broken.newPage();await b.route('**/assets/chemistry/lab-v1.json*',route=>route.fulfill({contentType:'application/json',body:'{}'}));await b.goto(new URL('chemistry-lab.html',base).href);await b.locator('#cl-retry').waitFor({state:'visible'});assert.equal(await b.locator('#cl-experiment').isVisible(),false);await b.unroute('**/assets/chemistry/lab-v1.json*');await b.locator('#cl-retry').click();await b.locator('#cl-experiment').waitFor({state:'visible'});await broken.close();
    const report={status:'passed',base,checks,noJavaScript:true,forcedColorsAndReducedMotion:true,fixtureIdentityFailureAndRetry:true,limits:['Windows Edge automation; no physical phone or real assistive-technology qualification']};fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
