/* Responsive, math-rendering and download checks against built or live pages. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs');
const path=require('node:path');

async function main(){
  const base=process.argv[2];const output=process.argv[3];
  if(!base||!output)throw new Error('Provide a site root URL and new QA directory');
  if(fs.existsSync(output))throw new Error('Use a new QA directory');
  fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHEMISTRY_CHROME});
  const report=[];
  try{
    for(const [name,width,height] of [['desktop',1440,1000],['phone',390,844],['narrow',320,800]]){
      const context=await browser.newContext({viewport:{width,height}});
      const routes=['collection/COMPUTATIONAL_CHEMISTRY.html','read/computational-chemistry/normal-form.html','read/computational-chemistry/three-queries.html'];
      if(name==='desktop')routes.push('read/computational-chemistry/spin-comparison.html','read/computational-chemistry/frozen-core.html','read/computational-chemistry/review.html','read/computational-chemistry/literature.html','read/computational-chemistry/reproduce.html');
      for(const route of routes){
        const page=await context.newPage();const errors=[];page.on('pageerror',error=>errors.push(String(error)));
        const response=await page.goto(new URL(route,base).href,{waitUntil:'load',timeout:60000});assert.equal(response.status(),200);
        await page.waitForFunction(()=>window.MathJax?.startup?.promise,{},{timeout:30000});
        await page.evaluate(async()=>{await MathJax.startup.promise;await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));});
        const layout=await page.evaluate(()=>{
          const math=[...document.querySelectorAll('.arithmatex')];
          const walker=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);let node;const raw=[];
          while(node=walker.nextNode())if(!node.parentElement.closest('mjx-container,pre,code,script,style')&&/\\\(|\\\[|\$\$/.test(node.textContent))raw.push(node.textContent.trim().slice(0,120));
          return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,math:math.length,unrendered:math.filter(el=>!el.querySelector('mjx-container')).length,mathErrors:document.querySelectorAll('mjx-merror,[data-mjx-error]').length,rawTex:raw,h1:document.querySelector('h1')?.innerText};
        });
        assert.ok(layout.scrollWidth<=width+1,JSON.stringify({name,route,layout}));assert.equal(layout.unrendered,0,route);assert.equal(layout.mathErrors,0,route);assert.deepEqual(layout.rawTex,[],route);assert.deepEqual(errors,[],route);
        if(route.includes('COMPUTATIONAL_CHEMISTRY')){
          assert.ok(layout.math>=15);
          await page.screenshot({path:path.join(output,name+'-overview.png')});
          const proof=page.getByRole('link',{name:'Read the normal-form proof',exact:true});assert.equal(await proof.count(),1);
          const download=page.getByRole('link',{name:'Download the focused replay bundle',exact:true}).first();
          const payload=await page.request.get(new URL(await download.getAttribute('href'),page.url()).href);assert.equal(payload.status(),200);
          const data=await payload.body();assert.equal(crypto.createHash('sha256').update(data).digest('hex'),'5957e5a485c54fb76079c36375de5341146113fa2b231d493c5ebc514fcecaf8');
          if(name==='phone'){
            await page.getByRole('heading',{name:'A reduced model from the H10 integrals',exact:true}).scrollIntoViewIfNeeded();
            await page.screenshot({path:path.join(output,'phone-molecular.png')});
          }
          if(name==='narrow'){
            await page.evaluate(()=>document.documentElement.style.fontSize='200%');await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
            assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Enlarged text creates viewport overflow');
          }
        }
        report.push({viewport:name,route,...layout,scriptErrors:errors});await page.close();
      }
      await context.close();
    }
    const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const page=await nojs.newPage();
    assert.equal((await page.goto(new URL('collection/COMPUTATIONAL_CHEMISTRY.html',base).href,{waitUntil:'load'})).status(),200);
    assert.match(await page.locator('main').innerText(),/Novelty/);assert.equal(await page.getByRole('link',{name:'Download the focused replay bundle',exact:true}).count(),2);
    await nojs.close();
    fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify({status:'passed',base,pages:report,noJavaScriptReading:true,enlargedText:true,archiveBytesVerified:true},null,2)+'\n');
    console.log(JSON.stringify({status:'passed',pages:report.length,viewports:[1440,390,320],mathErrors:0,unrendered:0,archiveBytesVerified:true,noJavaScriptReading:true,enlargedText:true}));
  }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
