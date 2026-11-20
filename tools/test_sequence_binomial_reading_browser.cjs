// Reading, equation layout, and native disclosure checks for the expanded note.
// Author: Komorebi P.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'.sequence-checks/reports/binomial-reading';
fs.mkdirSync(output,{recursive:true});
const url=new URL('sequence-central-binomial.html',base).href;
const report={status:'running',widths:[],errors:[],noJavaScript:false};

async function ready(page){
  await page.waitForFunction(()=>document.documentElement.dataset.mathDisplayReady==='true');
  await page.evaluate(async()=>{
    await window.MathJax?.startup?.promise;
    await window.KomorebiMath?.ready;
    await document.fonts.ready;
  });
}
async function settleLayout(page){
  // ResizeObserver updates the reader's equation containment on the next frame.
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(
    ()=>requestAnimationFrame(resolve))));
}
async function layout(page){
  return page.evaluate(()=>({
    page:{scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth},
    equationOverflow:[...document.querySelectorAll('.sl-math-display')].filter(
      node=>node.getBoundingClientRect().width>0&&node.scrollWidth>node.clientWidth+2
    ).map(node=>({width:node.clientWidth,scroll:node.scrollWidth,
      tex:node.querySelector('mjx-assistive-mml')?.textContent||node.textContent})),
    inlineOverflow:[...document.querySelectorAll('main span.arithmatex')].filter(node=>{
      const math=node.querySelector('mjx-container');
      return node.clientWidth>0&&math&&math.getBoundingClientRect().width>node.clientWidth+2;
    }).map(node=>({width:node.clientWidth,
      mathWidth:node.querySelector('mjx-container').getBoundingClientRect().width,
      tex:node.querySelector('mjx-assistive-mml')?.textContent||node.textContent})),
    pageOverflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1
      ?[...document.querySelectorAll('body *')].filter(node=>{
        const box=node.getBoundingClientRect();
        if(!box.width||box.right<=document.documentElement.clientWidth+1)return false;
        for(let parent=node.parentElement;parent;parent=parent.parentElement){
          if(['auto','scroll','hidden','clip'].includes(getComputedStyle(parent).overflowX))return false;
        }
        return true;
      }).slice(0,20).map(node=>({tag:node.tagName,id:node.id,className:node.className,
        right:node.getBoundingClientRect().right,text:node.textContent.slice(0,180)})):[],
    mathErrors:[...document.querySelectorAll('[data-mml-node="merror"],[data-mjx-error]')]
      .map(node=>node.textContent),
  }));
}
async function textContrast(page){
  return page.evaluate(()=>{
    const rgb=value=>(value.match(/[\d.]+/g)||[]).map(Number);
    const luminance=color=>color.slice(0,3).map(value=>{
      const c=value/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;
    }).reduce((sum,value,i)=>sum+value*[.2126,.7152,.0722][i],0);
    const background=node=>{
      const layers=[];
      for(let current=node;current;current=current.parentElement){
        const color=rgb(getComputedStyle(current).backgroundColor);
        layers.push(color);
        if(color.length===3||color[3]===1)break;
      }
      // System Highlight can be translucent in forced-color mode. Composite
      // every layer instead of treating a translucent control as transparent.
      return layers.reverse().reduce((surface,color)=>{
        const alpha=color[3]??1;
        return color.slice(0,3).map((value,i)=>value*alpha+surface[i]*(1-alpha));
      },[255,255,255]);
    };
    return ['body','.sl-math-display','.sl-example-number','.sl-kernel-example>summary',
      '.sl-example-body p','.sl-binomial-jumps a','#sq-scheme-green','#sq-page-theme'].map(selector=>{
      const node=document.querySelector(selector),style=getComputedStyle(node);
      const color=rgb(style.color),surface=background(node),alpha=color[3]??1;
      const foreground=color.slice(0,3).map((value,i)=>value*alpha+surface[i]*(1-alpha));
      const a=luminance(foreground),b=luminance(surface);
      return {selector,foreground,surface,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
    });
  });
}
(async()=>{
  const browser=await chromium.launch({headless:true,
    ...(process.env.KOMOREBI_CHROMIUM_PATH?{executablePath:process.env.KOMOREBI_CHROMIUM_PATH}:{})});
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:960}});
      const page=await context.newPage();
      page.on('pageerror',error=>report.errors.push({width,message:error.message}));
      const response=await page.goto(url);
      assert.equal(response.ok(),true);
      await ready(page);
      assert.equal(await page.locator('main h1').count(),1);
      assert.equal(await page.locator('.sl-kernel-example').count(),32);
      assert.equal(await page.locator('.sl-kernel-example[open]').count(),0);
      // Leading [x^n] must remain coefficient extraction, not an AMS layout option.
      const residueProof=page.locator('.sl-math-display').filter({hasText:'Res'});
      assert.equal(await residueProof.count(),1);
      const residueMath=await residueProof.locator('mjx-assistive-mml').textContent();
      assert.match(residueMath.replace(/[\s\u2060-\u2064]/g,''),/^\[xn\]R\(x\)=Res/);
      const brokenTargets=await page.evaluate(()=>[...document.querySelectorAll(
        '.sl-binomial-jumps a,.sl-proof-outline a,.sl-example-permalink a'
      )].filter(link=>link.hash&&!document.getElementById(link.hash.slice(1))).map(link=>link.hash));
      assert.deepEqual(brokenTargets,[]);
      await page.locator('[data-example-action="open"]').click();
      assert.equal(await page.locator('.sl-kernel-example[open]').count(),32);
      await settleLayout(page);
      const measured=await layout(page);
      report.widths.push({width,...measured});
      assert.ok(measured.page.scroll<=measured.page.client+1,'Horizontal page overflow');
      assert.deepEqual(measured.mathErrors,[]);
      await page.locator('#math-proof-1-definition-and-universal-recurrence').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(output,'theorem-'+width+'.png')});
      await page.locator('#kernel-example-20').screenshot({path:path.join(output,'weighted-example-'+width+'.png')});
      await page.locator('#kernel-example-23').screenshot({path:path.join(output,'fibonacci-example-'+width+'.png')});
      await page.locator('#kernel-example-32').screenshot({path:path.join(output,'repeated-root-example-'+width+'.png')});
      if(width===390){
        report.palettes=[];
        for(const [scheme,theme,system]of [
          ['green','light','light'],['green','dark','light'],
          ['green','system','dark'],['mono','dark','dark'],['mono','light','light']
        ]){
          await page.emulateMedia({colorScheme:system});
          await page.locator('#sq-scheme-'+scheme).click();
          await page.locator('#sq-page-theme').selectOption(theme);
          const pairs=await textContrast(page);
          report.palettes.push({scheme,theme,system,pairs});
          assert.ok(pairs.every(pair=>pair.ratio>=4.5),'Reading text contrast in '+scheme+'/'+theme);
          if(scheme==='green'&&theme==='dark'){
            await page.locator('#kernel-example-32').screenshot({path:path.join(output,'repeated-root-dark-390.png')});
          }
        }
        await page.locator('#sq-scheme-green').click();
        await page.locator('#sq-page-theme').selectOption('light');
        assert.equal(await page.locator('#sq-scheme-green').textContent(),'Ink & blue');
        await page.emulateMedia({forcedColors:'active'});
        report.forcedColors=await textContrast(page);
        assert.ok(report.forcedColors.every(pair=>pair.ratio>=4.5));
        await page.emulateMedia({forcedColors:'none',colorScheme:'light'});
      }
      await page.locator('[data-example-action="close"]').click();
      assert.equal(await page.locator('.sl-kernel-example[open]').count(),0);
      await page.locator('#kernel-example-1 > summary').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('#kernel-example-1').evaluate(node=>node.open),true);
      await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
      assert.equal(await page.locator('.sl-kernel-example[open]').count(),32);
      await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
      assert.equal(await page.locator('.sl-kernel-example[open]').count(),1);
      await page.goto(url+'#kernel-example-20');
      await ready(page);
      assert.equal(await page.locator('#kernel-example-20').evaluate(node=>node.open),true);
      if(width===320){
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        await settleLayout(page);
        const enlarged=await layout(page);
        report.enlarged=enlarged;
        await page.locator('#kernel-example-20').screenshot({path:path.join(output,'weighted-example-enlarged-320.png')});
        assert.ok(enlarged.page.scroll<=enlarged.page.client+1,'Enlarged text overflows the page');
      }
      await context.close();
    }
    const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:960}});
    const page=await context.newPage();
    await page.goto(url);
    assert.equal(await page.locator('.sl-example-controls').isVisible(),false);
    await page.locator('#kernel-example-20 > summary').click();
    assert.equal(await page.locator('#kernel-example-20').evaluate(node=>node.open),true);
    assert.ok((await page.locator('#kernel-example-20').textContent()).includes('10'));
    const staticLayout=await layout(page);
    assert.ok(staticLayout.page.scroll<=staticLayout.page.client+1);
    report.noJavaScript=true;
    await context.close();
    assert.deepEqual(report.errors,[]);
    // Report all narrow-screen equations before failing, so a line-break repair
    // can be made from the hosted evidence without weakening this reading gate.
    const overflow=report.widths.flatMap(item=>item.equationOverflow.map(
      formula=>({width:item.width,...formula})));
    assert.deepEqual(overflow,[],'Equations should fit without horizontal scrolling at ordinary text size');
    const inlineOverflow=report.widths.flatMap(item=>item.inlineOverflow.map(
      formula=>({width:item.width,...formula})));
    assert.deepEqual(inlineOverflow,[],'Inline equations should fit at ordinary text size');
    report.status='passed';
  }catch(error){
    report.status='failed';report.failure=error.message;
    throw error;
  }finally{
    await browser.close();
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }
})().catch(error=>{console.error(error);process.exit(1);});
