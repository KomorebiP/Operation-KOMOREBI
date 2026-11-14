/* Focused reader checks; not a whole-site WCAG or assistive-technology audit. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),crypto=require('node:crypto'),fs=require('node:fs'),path=require('node:path');
const notes=['notation','normal-form','three-queries','spin-comparison','frozen-core','model-error','review','literature','reproduce'];
const routes=['collection/COMPUTATIONAL_CHEMISTRY.html',...notes.map(x=>'read/computational-chemistry/'+x+'.html')];
const frame=page=>page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
const inspect=page=>page.evaluate(()=>{
  const root=document.querySelector('main'),math=[...root.querySelectorAll('.arithmatex')],tables=[...root.querySelectorAll('table')];
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;const raw=[];
  while(node=walker.nextNode())if(!node.parentElement.closest('mjx-container,pre,code,script,style')&&/\\\(|\\\[|\$\$/.test(node.textContent))raw.push(node.textContent.trim().slice(0,100));
  const rgb=s=>(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);
  const lum=c=>c.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const contrasts=[];
  for(const el of root.querySelectorAll('p,li,h1,h2,h3,caption,th,td,summary,a,code')){
    if(!el.getClientRects().length||el.closest('mjx-container'))continue;
    const cs=getComputedStyle(el);let ancestor=el,bg;
    while(ancestor){bg=getComputedStyle(ancestor).backgroundColor;if(bg!=='rgba(0, 0, 0, 0)'&&bg!=='transparent')break;ancestor=ancestor.parentElement;}
    if(!ancestor)bg='rgb(255,255,255)';const fg=rgb(cs.color),back=rgb(bg);if(fg.length!==3||back.length!==3)continue;
    const a=lum(fg),b=lum(back);contrasts.push({ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05),text:el.textContent.trim().slice(0,50)});
  }
  return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,math:math.length,unrendered:math.filter(x=>!x.querySelector('mjx-container')).length,
    mathErrors:root.querySelectorAll('mjx-merror,[data-mjx-error]').length,rawTex:raw,h1:root.querySelector('h1')?.innerText,h1Count:root.querySelectorAll('h1').length,
    tableCount:tables.length,unlabeledTables:tables.filter(x=>!x.querySelector('caption')?.textContent.trim()||!x.querySelector('th[scope="col"]')||!x.closest('[tabindex="0"][aria-label]')).length,
    minimumTextContrast:Math.min(...contrasts.map(x=>x.ratio)),contrastFailures:contrasts.filter(x=>x.ratio<4.5),assistiveMath:root.querySelectorAll('mjx-assistive-mml').length,explorableMath:root.querySelectorAll('mjx-container[tabindex]').length};
});
async function main(){
  const [base,output]=process.argv.slice(2);if(!base||!output)throw Error('Provide root URL and a new QA directory');
  if(fs.existsSync(output))throw Error('Use a new QA directory');fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,executablePath:process.env.CHEMISTRY_CHROME});const pages=[],nojs=[];
  try{
    for(const [viewport,width,height] of [['desktop',1440,1000],['phone',390,844],['narrow',320,800]]){
      const context=await browser.newContext({viewport:{width,height}});
      for(const route of routes){
        const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
        assert.equal((await page.goto(new URL(route,base).href,{waitUntil:'load',timeout:60000})).status(),200,route);
        await page.waitForFunction(()=>window.MathJax?.startup?.promise,{},{timeout:30000});await page.evaluate(()=>MathJax.startup.promise);await frame(page);
        const result=await inspect(page);assert.ok(result.scrollWidth<=width+1,JSON.stringify({route,viewport,result}));
        assert.equal(result.unrendered,0,route);assert.equal(result.mathErrors,0,route);assert.deepEqual(result.rawTex,[],route);assert.equal(result.h1Count,1,route);assert.equal(result.unlabeledTables,0,route);
        assert.deepEqual(result.contrastFailures,[],JSON.stringify({route,viewport,contrast:result.contrastFailures}));assert.deepEqual(errors,[],route);
        if(route.startsWith('read/')){
          const menu=page.locator('.chemistry-reading-nav'),summary=menu.locator('summary');assert.equal(await menu.getAttribute('open'),null);
          await page.keyboard.press('Tab');await summary.focus();await page.keyboard.press('Enter');assert.notEqual(await menu.getAttribute('open'),null);assert.equal(await menu.locator('a[aria-current="page"]').count(),1);
          assert.ok(await summary.evaluate(x=>getComputedStyle(x).outlineWidth!=='0px'),'Missing keyboard focus');
          for(const target of await menu.locator('a').all())assert.ok((await target.boundingBox()).height>=44);
          await page.keyboard.press('Enter');assert.equal(await menu.getAttribute('open'),null);
          const source=page.locator('.chemistry-provenance');await source.locator('summary').focus();await page.keyboard.press('Enter');assert.notEqual(await source.getAttribute('open'),null);
          assert.ok(await source.getByRole('link',{name:'Read the current Markdown source',exact:true}).count());await source.locator('summary').press('Enter');
          for(const link of await page.locator('.chemistry-pagination a').all())assert.ok(notes.includes((await link.getAttribute('href')).replace('.html','')));
        }
        for(const table of await page.locator('.table-scroll').all())if(await table.evaluate(x=>x.scrollWidth>x.clientWidth+4)){
          await table.focus();await page.keyboard.press('ArrowRight');await page.waitForTimeout(120);assert.ok(await table.evaluate(x=>x.scrollLeft>0),'Table keyboard scroll');await table.evaluate(x=>x.scrollLeft=0);
        }
        if(viewport==='narrow'){
          await page.evaluate(()=>document.documentElement.style.fontSize='200%');await frame(page);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'200% text overflow: '+route);
          result.enlargedTextPassed=true;await page.evaluate(()=>document.documentElement.style.fontSize='');await frame(page);
        }
        if(route.includes('COMPUTATIONAL_CHEMISTRY')||route.endsWith('three-queries.html')){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(output,viewport+'-'+(route.includes('COMPUTATIONAL_CHEMISTRY')?'overview':'theorem')+'.png')});}
        if(viewport==='phone'&&route.endsWith('three-queries.html')){await page.getByRole('heading',{name:'Positivity: existence and an all-compatible guarantee',exact:true}).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'phone-positivity.png')});}
        pages.push({viewport,route,...result,scriptErrors:errors});await page.close();
      }
      await context.close();
    }
    const plain=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:800}});
    for(const route of routes){
      const page=await plain.newPage();assert.equal((await page.goto(new URL(route,base).href,{waitUntil:'load'})).status(),200);assert.equal(await page.locator('main h1').count(),1);assert.ok((await page.locator('main').innerText()).length>2000);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
      if(route.startsWith('read/')){const menu=page.locator('.chemistry-reading-nav');await menu.locator('summary').focus();await page.keyboard.press('Enter');assert.notEqual(await menu.getAttribute('open'),null);assert.equal(await menu.locator('a').count(),10);}
      nojs.push(route);await page.close();
    }
    await plain.close();
    const special=await browser.newContext({viewport:{width:320,height:800},reducedMotion:'reduce',forcedColors:'active'});const page=await special.newPage();
    await page.goto(new URL(routes[3],base).href);await page.evaluate(()=>MathJax.startup.promise);await frame(page);
    assert.ok(await page.evaluate(()=>matchMedia('(prefers-reduced-motion:reduce)').matches&&matchMedia('(forced-colors:active)').matches));await page.locator('.chemistry-reading-nav summary').focus();await page.keyboard.press('Enter');assert.notEqual(await page.locator('.chemistry-reading-nav').getAttribute('open'),null);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await special.close();
    const requests=await browser.newContext(),manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../manifests/chemistry-stage14-validation.json'),'utf8'));
    for(const [route,expected] of [['assets/chemistry/validation-v1/Stage14_Validated_Replay.zip',manifest.sha256],['assets/chemistry/stage14/Stage14_Fixed_Spin_Recovery.zip','5957e5a485c54fb76079c36375de5341146113fa2b231d493c5ebc514fcecaf8']]){
      const response=await requests.request.get(new URL(route,base).href);assert.equal(response.status(),200);assert.equal(crypto.createHash('sha256').update(await response.body()).digest('hex'),expected);
    }
    await requests.close();
    fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify({status:'passed',base,pages,noJavaScriptRoutes:nojs,enlargedTextRoutes:10,reducedMotionAndForcedColorsRoutes:1,archiveBytesVerified:true,
      limits:['Chromium automation on Windows, not a complete WCAG audit','No real screen-reader, magnifier or physical touch-device qualification','Without JavaScript, prose and TeX source remain readable; equations are not typeset']},null,2)+'\n');
    console.log(JSON.stringify({status:'passed',pages:pages.length,noJavaScriptRoutes:nojs.length,enlargedTextRoutes:10,minimumTextContrast:Math.min(...pages.map(x=>x.minimumTextContrast)),archiveBytesVerified:true}));
  }finally{await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
