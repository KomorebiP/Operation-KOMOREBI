// Focused interaction, display and accessibility regressions for exact sequences.
// Author: Komorebi P. These checks do not constitute a conformance certification.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'.sequence-checks/reports/accessibility-browser';
fs.mkdirSync(output,{recursive:true});
const url=name=>new URL(name,base).href;
const report={status:'running',widths:[],errors:[],coverage:'Focused browser regressions, not a WCAG conformance assessment.'};
let browser,activePage;

async function settle(page){
  await page.evaluate(async()=>{
    await window.MathJax?.startup?.promise;await window.KomorebiMath?.ready;
    await document.fonts.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
}
async function fit(page){
  await settle(page);
  const sizes=await page.evaluate(()=>{
    const width=document.documentElement.clientWidth,scroll=document.documentElement.scrollWidth;
    if(scroll<=width+1)return {width,scroll};
    const describe=el=>el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+
      (typeof el.className==='string'&&el.className?'.'+el.className.trim().replace(/\s+/g,'.'):'');
    const clippedRight=(rect,el,clipSelf=false)=>{
      let right=rect.right;
      for(let parent=clipSelf?el:el.parentElement;parent&&parent!==document.body;parent=parent.parentElement){
        if(['auto','scroll','hidden','clip'].includes(getComputedStyle(parent).overflowX))
          right=Math.min(right,parent.getBoundingClientRect().right);
      }
      return right;
    };
    const offenders=[];
    for(const el of document.body.querySelectorAll('*')){
      if(!el.getClientRects().length)continue;
      const rect=el.getBoundingClientRect(),style=getComputedStyle(el);
      const right=clippedRight(rect,el);
      if(right>width+1)offenders.push({kind:'element',element:describe(el),parent:describe(el.parentElement),
        left:rect.left,right,width:rect.width,fontSize:style.fontSize,minWidth:style.minWidth,
        overflowX:style.overflowX,text:el.textContent.trim().slice(0,90)});
      for(const child of el.childNodes){
        if(child.nodeType!==Node.TEXT_NODE||!child.textContent.trim())continue;
        const range=document.createRange();range.selectNodeContents(child);
        for(const textRect of range.getClientRects()){
          const textRight=clippedRight(textRect,el,true);
          if(textRight>width+1)offenders.push({kind:'text',element:describe(el),parent:describe(el.parentElement),
            right:textRight,fontSize:style.fontSize,text:child.textContent.trim().slice(0,90)});
        }
      }
    }
    return {width,scroll,rootFont:getComputedStyle(document.documentElement).fontSize,
      offenders:offenders.sort((a,b)=>b.right-a.right).slice(0,30)};
  });
  assert.ok(sizes.scroll<=sizes.width+1,'Page overflow: '+JSON.stringify(sizes));
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0,'MathJax reported a rendering error');
}
async function ready(page){
  await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
}
async function openCalculator(page){
  await ready(page);
  const panel=page.locator('#closed-calculator-panel');
  if(!await panel.evaluate(el=>el.open)){
    await panel.locator(':scope > summary').focus();await page.keyboard.press('Enter');
  }
  await page.locator('#cf-mode').waitFor({state:'visible'});
  assert.equal(await page.locator('#closed-calculator-root > .cf-placeholder').count(),0);
}
async function rows(page){return page.locator('#cf-table-values tr td code').allTextContents();}
async function calculate(page){
  await page.locator('#cf-calculate').click();
  await page.waitForFunction(()=>document.querySelector('#cf-form')?.getAttribute('aria-busy')==='false'
    &&!document.querySelector('#cf-results')?.hidden,null,{timeout:30000});
}
async function coefficients(page,mode,a,c){
  for(const [prefix,values] of [['a',a],['c',c]])for(let k=0;k<4;k++)
    await page.locator('#cf-'+mode+'-'+prefix+k).fill(String(values[k]||0));
}
async function focused(page,id){
  assert.equal(await page.evaluate(()=>document.activeElement?.id),id,'Expected keyboard focus on '+id);
}
async function keyboardDisclosure(page,selector){
  const detail=page.locator(selector),summary=detail.locator(':scope > summary');
  if(await detail.evaluate(el=>el.open))await summary.click();
  await summary.focus();await page.keyboard.press('Enter');
  assert.equal(await detail.evaluate(el=>el.open),true,'Keyboard did not open '+selector);
  const outline=await summary.evaluate(el=>getComputedStyle(el).outlineStyle);
  assert.notEqual(outline,'none','Keyboard focus needs a visible outline');
}
async function contrast(page){
  return page.evaluate(()=>{
    const parse=color=>{const v=color.match(/[\d.]+/g)?.map(Number);return v&&v.length>=3?v:null;};
    const luminance=rgb=>rgb.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4)
      .reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
    return ['#cf-mode','#cf-calculate','#cf-status','#cf-family-note','#cf-results td code'].map(selector=>{
      const el=document.querySelector(selector),fg=parse(getComputedStyle(el).color);
      let parent=el,bg;
      while(parent){const value=parse(getComputedStyle(parent).backgroundColor);if(value&&(value.length<4||value[3]===1)){bg=value;break;}parent=parent.parentElement;}
      if(!fg||!bg)throw Error('Could not resolve opaque foreground/background for '+selector);
      const a=luminance(fg),b=luminance(bg);
      return {selector,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
    });
  });
}

(async()=>{
  try{
    browser=await chromium.launch({headless:true});
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:950},permissions:['clipboard-read','clipboard-write']});
      // Hold only this calculator's outgoing messages. Every actual result still
      // comes from a native worker running the production arithmetic module.
      await context.addInitScript(()=>{
        const NativeWorker=window.Worker;
        window.__cfWorkerAudit={hold:false,records:[],messages:0};
        window.Worker=class extends NativeWorker{
          constructor(source,options){
            super(source,options);
            if(String(source).includes('sequence-closed-forms-worker.mjs')){
              this.auditRecord={worker:this,terminated:false,held:null};
              window.__cfWorkerAudit.records.push(this.auditRecord);
              this.addEventListener('message',()=>window.__cfWorkerAudit.messages++);
            }
          }
          postMessage(message,...rest){
            if(this.auditRecord&&window.__cfWorkerAudit.hold){this.auditRecord.held=message;return;}
            return super.postMessage(message,...rest);
          }
          terminate(){if(this.auditRecord)this.auditRecord.terminated=true;return super.terminate();}
        };
      });
      const page=await context.newPage();activePage=page;
      page.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await page.goto(url('sequence-library.html#closed-calculator-panel'));await openCalculator(page);
      assert.equal(await page.locator('#cf-status').getAttribute('aria-atomic'),'true');
      assert.equal(await page.locator('#cf-form fieldset:not([disabled])').count(),1);
      const invalidLabels=await page.locator('#cf-form input').evaluateAll(inputs=>inputs.filter(input=>
        !input.labels?.length||!document.getElementById(input.getAttribute('aria-labelledby'))).map(input=>input.id));
      assert.deepEqual(invalidLabels,[],'Every integer input needs a stable accessible label');

      await page.locator('#cf-sparse-u').fill('2');
      assert.equal(await page.locator('#cf-results').isVisible(),false,'Edits must hide stale values');
      assert.equal(await page.locator('#cf-link').isVisible(),false,'Edits must hide stale exports');
      assert.match(await page.locator('#cf-status').textContent(),/Parameters changed/);
      await calculate(page);
      // An event-free programmatic change must not alter the completed snapshot.
      await page.locator('#cf-sparse-u').evaluate(el=>el.value='3');
      await page.locator('#cf-link').click();
      const shared=await page.evaluate(()=>navigator.clipboard.readText());
      assert.equal(new URL(shared).searchParams.get('cf-u'),'2');

      await page.locator('#cf-count').fill('33');await page.locator('#cf-calculate').click();
      await focused(page,'cf-count');
      assert.equal(await page.locator('#cf-count').getAttribute('aria-invalid'),'true');
      assert.match(await page.locator('#cf-count').getAttribute('aria-describedby'),/cf-count-error/);
      assert.match(await page.locator('#cf-count-error').textContent(),/between 1 and 32/);
      assert.equal(await page.getByRole('spinbutton',{name:'Number of values',exact:true}).count(),1);
      await page.locator('#cf-reset').click();
      assert.equal(await page.locator('#cf-count').getAttribute('aria-invalid'),null);

      await page.selectOption('#cf-mode','differential_hankel');
      await page.locator('#cf-differential_hankel-a1').fill('3');
      await page.locator('#cf-differential_hankel-c3').fill('-2');
      await page.selectOption('#cf-mode','sparse');
      await page.selectOption('#cf-mode','differential_moments');
      assert.equal(await page.locator('#cf-differential_moments-a1').inputValue(),'3');
      assert.equal(await page.locator('#cf-differential_moments-c3').inputValue(),'-2');
      await page.locator('#cf-reset').click();
      await page.selectOption('#cf-mode','differential_hankel');
      assert.equal(await page.locator('#cf-differential_hankel-a1').inputValue(),'1');
      assert.equal(await page.locator('#cf-differential_hankel-c3').inputValue(),'0');
      await coefficients(page,'differential_hankel',[1,0,0,0],[1,0,0,0]);
      await page.locator('#cf-start').fill('63');await page.locator('#cf-count').fill('2');
      await calculate(page);
      assert.deepEqual(await rows(page),[(2n**62n).toString(),(2n**63n).toString()]);
      assert.ok(await page.evaluate(()=>window.__cfWorkerAudit.messages)>0,'The real module worker must return the large window');
      assert.match(await page.locator('#cf-results table caption').textContent(),/indices 63 through 64/);

      // A held request makes cancellation deterministic even on fast runners.
      await page.evaluate(()=>window.__cfWorkerAudit.hold=true);
      await page.locator('#cf-calculate').click();
      assert.equal(await page.locator('#cf-form').getAttribute('aria-busy'),'true');
      await page.locator('#cf-differential_hankel-a1').fill('1');
      assert.equal(await page.evaluate(()=>window.__cfWorkerAudit.records.at(-1).terminated),true);
      assert.equal(await page.locator('#cf-form').getAttribute('aria-busy'),'false');
      const cancellationStatus=await page.locator('#cf-status').textContent();
      await page.evaluate(()=>{
        const record=window.__cfWorkerAudit.records.at(-1);
        record.worker.onerror?.(new ErrorEvent('error',{message:'Delayed cancelled-worker event',cancelable:true}));
        record.worker.onmessage?.({data:{id:record.held.id,error:'Delayed cancelled-worker result'}});
        window.__cfWorkerAudit.hold=false;
      });
      assert.equal(await page.locator('#cf-status').textContent(),cancellationStatus,'A late worker callback must not overwrite current state');
      assert.equal(await page.locator('#cf-results').isVisible(),false);

      await coefficients(page,'differential_hankel',[12,-12,12,12],[12,-12,12,-12]);
      await page.locator('#cf-start').fill('64');await page.locator('#cf-count').fill('1');
      await calculate(page);
      const large=(await rows(page))[0];
      assert.match(large,/^-?\d+$/);assert.equal(large.replace('-','').length,535);
      assert.match(await page.locator('#cf-status').textContent(),/^Computed 1 exact integer\./);
      await keyboardDisclosure(page,'#cf-ogf');
      await keyboardDisclosure(page,'#cf-method');
      await page.locator('.cf-table-scroll').focus();
      assert.equal(await page.locator('.cf-table-scroll').getAttribute('tabindex'),'0');
      await fit(page);
      await page.locator('#closed-calculator-panel').screenshot({path:path.join(output,'calculator-'+width+'.png')});
      const palette=[];
      for(const theme of ['light','dark']){
        await page.selectOption('#sq-page-theme',theme);
        const samples=await contrast(page);
        for(const sample of samples)assert.ok(sample.ratio>=4.5,'Insufficient text contrast '+theme+' '+JSON.stringify(sample));
        palette.push({theme,samples});
      }
      await page.selectOption('#sq-page-theme','light');
      await page.emulateMedia({forcedColors:'active',reducedMotion:'reduce'});await fit(page);
      await page.emulateMedia({forcedColors:'none',reducedMotion:'no-preference'});
      let enlargedEditableWidths;
      if(width<500){
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');
        const legends=await page.locator('#cf-form fieldset:not([disabled]) legend').evaluateAll(elements=>elements.map(el=>{
          const rect=el.getBoundingClientRect(),group=el.parentElement.getBoundingClientRect();
          return {text:el.textContent,left:rect.left,right:rect.right,parentLeft:group.left,parentRight:group.right};
        }));
        for(const legend of legends)assert.ok(legend.left>=legend.parentLeft-1&&
          legend.right<=Math.min(legend.parentRight,width)+1,'An enlarged legend must fit its fieldset: '+JSON.stringify(legend));
        const editableWidths=await page.locator('#cf-form input:not(:disabled)').evaluateAll(inputs=>{
          const canvas=document.createElement('canvas'),context=canvas.getContext('2d');
          return inputs.map(input=>{
            const style=getComputedStyle(input);
            context.font=[style.fontStyle,style.fontWeight,style.fontSize,style.fontFamily].join(' ');
            // Reserve space for native number steppers as well as CSS padding.
            const usable=input.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight)-24;
            const needed=Math.max(context.measureText('-12').width,context.measureText(input.value).width)+8;
            return {id:input.id,usable,needed,fontSize:style.fontSize};
          });
        });
        for(const field of editableWidths){
          assert.ok(parseFloat(field.fontSize)>=31.5,'Input text must retain 200% enlargement: '+JSON.stringify(field));
          assert.ok(field.usable>=field.needed,
            'Enlarged input must show its editable value and sign: '+JSON.stringify(field));
        }
        enlargedEditableWidths=editableWidths;
        await fit(page);
        await page.locator('#closed-calculator-panel').screenshot({path:path.join(output,'calculator-enlarged-'+width+'.png')});
        await page.evaluate(()=>document.documentElement.style.removeProperty('font-size'));
      }
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
      await page.locator('#cf-copy').click();
      await page.locator('#cf-fallback').waitFor({state:'visible'});await focused(page,'cf-fallback');
      const fallback=await page.locator('#cf-fallback').evaluate(el=>({text:el.value,start:el.selectionStart,end:el.selectionEnd}));
      assert.ok(fallback.text.includes(large));assert.equal(fallback.start,0);assert.equal(fallback.end,fallback.text.length);

      const proof=await context.newPage();activePage=proof;
      proof.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await proof.goto(url('sequence-differential-hankel.html'));await ready(proof);await settle(proof);
      assert.equal(await proof.locator('#differential-hankel-reading .sl-math-display').count(),46);
      assert.equal(await proof.locator('.sl-math-reading-intro .sl-math-display').count(),1);
      const introSizing=await proof.locator('.sl-math-reading-intro .sl-math-display').evaluate(el=>({
        width:el.clientWidth,scroll:el.scrollWidth,maxWidth:getComputedStyle(el.querySelector('mjx-container svg')).maxWidth,
        focusable:el.tabIndex===0,label:el.getAttribute('aria-label')}));
      assert.equal(introSizing.maxWidth,'none','Long equations must retain their natural glyph size');
      assert.ok(introSizing.focusable&&introSizing.label,'The equation scroll region needs keyboard access and a label');
      if(width<500)assert.ok(introSizing.scroll>introSizing.width,'A long equation should scroll instead of shrinking on a phone');
      assert.equal(await proof.locator('.sl-math-display:not(:has(mjx-container))').count(),0,'Every display must typeset');
      const inline=proof.locator('#differential-hankel-reading span.arithmatex');
      assert.ok(await inline.count()>0);assert.equal(await inline.locator(':scope > mjx-container').count(),await inline.count(),'Inline TeX must typeset');
      await keyboardDisclosure(proof,'.sl-proof-outline');
      assert.equal(await proof.locator('.sl-proof-outline a').count(),8);
      assert.deepEqual(await proof.locator('.sl-proof-outline a').evaluateAll(links=>links.filter(link=>
        !document.getElementById(decodeURIComponent(link.hash.slice(1)))).map(link=>link.hash)),[]);
      const code=proof.locator('.sl-math-proof-code');assert.equal(await code.count(),1);
      await code.focus();assert.equal(await code.evaluate(el=>document.activeElement===el),true);
      assert.notEqual(await code.evaluate(el=>getComputedStyle(el).outlineStyle),'none');
      await proof.selectOption('#site-math-display','plain');
      assert.equal(await proof.locator('.sl-math-display .math-plain-source').first().isVisible(),true);
      assert.equal(await proof.locator('.sl-math-display mjx-container').first().isVisible(),false);
      await fit(proof);
      await proof.selectOption('#site-math-display','typeset');await settle(proof);
      assert.equal(await proof.locator('.sl-math-display mjx-container').first().isVisible(),true);
      await fit(proof);
      await proof.locator('.sl-math-reading-intro').screenshot({path:path.join(output,'proof-intro-'+width+'.png')});
      await proof.locator('.sl-proof-outline').screenshot({path:path.join(output,'proof-outline-'+width+'.png')});
      report.widths.push({width,staleResults:true,calculatedLinkSnapshot:true,sharedCoefficients:true,
        fieldErrors:true,realWorker:true,workerCancellation:true,longIntegerDigits:535,
        keyboardDisclosures:true,clipboardFallback:true,proofDisplays:40,proofInlineMath:true,
        plainTextToggle:true,forcedColors:true,reducedMotion:true,enlargedText:width<500,
        ...(enlargedEditableWidths?{enlargedEditableWidths}:{}),palette,overflow:false});
      await context.close();activePage=null;
    }
    assert.deepEqual(report.errors,[]);report.status='passed';
  }catch(error){
    report.status='failed';report.failure=error.stack||String(error);
    if(activePage&&!activePage.isClosed()){
      try{await activePage.screenshot({path:path.join(output,'failure.png')});}
      catch(screenshotError){report.screenshotError=String(screenshotError);}
    }
    throw error;
  }
  finally{
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
    if(browser)await browser.close();
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
