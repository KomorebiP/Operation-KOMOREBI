// Focused search, inspection and accessibility regressions for the Sequence Library.
// Author: Komorebi P. These checks are not a conformance certification.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'.sequence-checks/reports/search-accessibility-browser';
fs.mkdirSync(output,{recursive:true});
const url=name=>new URL(name,base).href;
const report={status:'running',widths:[],errors:[],
  coverage:'Focused interaction and layout checks, not a WCAG conformance assessment.'};
let browser,activePage;

async function ready(page){
  await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
}
async function settle(page){
  await page.evaluate(async()=>{
    await window.MathJax?.startup?.promise;
    await window.KomorebiMath?.ready;
    await document.fonts.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
}
async function fit(page){
  await settle(page);
  const geometry=await page.evaluate(()=>{
    const width=document.documentElement.clientWidth,scroll=document.documentElement.scrollWidth;
    if(scroll<=width+1)return {width,scroll};
    const describe=el=>el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+
      (typeof el.className==='string'&&el.className?'.'+el.className.trim().replace(/\s+/g,'.'):'');
    const offenders=[];
    for(const el of document.body.querySelectorAll('*')){
      if(!el.getClientRects().length)continue;
      const rect=el.getBoundingClientRect();let right=rect.right;
      for(let ancestor=el.parentElement;ancestor&&ancestor!==document.body;ancestor=ancestor.parentElement){
        if(['auto','scroll','hidden','clip'].includes(getComputedStyle(ancestor).overflowX))
          right=Math.min(right,ancestor.getBoundingClientRect().right);
      }
      if(right>width+1)offenders.push({element:describe(el),right,width:rect.width,
        fontSize:getComputedStyle(el).fontSize,text:el.textContent.trim().slice(0,100)});
    }
    return {width,scroll,offenders:offenders.sort((a,b)=>b.right-a.right).slice(0,20)};
  });
  assert.ok(geometry.scroll<=geometry.width+1,'Page-wide overflow: '+JSON.stringify(geometry));
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0,
    'A displayed formula contains a MathJax error');
}
async function focusIs(page,selector){
  assert.equal(await page.locator(selector).evaluate(el=>document.activeElement===el),true,
    'Expected focus on '+selector);
}
async function submit(page,value){
  if(value!==undefined)await page.locator('#sl-query').fill(value);
  await page.locator('#sl-search > .sl-query > button[type=submit]').click();
}
async function resultIds(page){
  return page.locator('#sl-results>li').evaluateAll(nodes=>nodes.map(node=>node.dataset.resultId));
}
async function denyCopy(page,deny){
  await page.evaluate(value=>{window.__searchClipboard.deny=value;},deny);
}
async function failedSearchCopy(page){
  await denyCopy(page,true);
  await page.locator('#sl-share').click();
  await page.locator('#sl-link-wrap').waitFor({state:'visible'});
  await focusIs(page,'#sl-link');
  const selection=await page.locator('#sl-link').evaluate(el=>({
    text:el.value,start:el.selectionStart,end:el.selectionEnd}));
  assert.ok(selection.text.includes('sequence-library.html'));
  assert.equal(selection.start,0);assert.equal(selection.end,selection.text.length);
  return selection.text;
}
async function fallbackCleared(page){
  assert.equal(await page.locator('#sl-link-wrap').isVisible(),false,'A stale search link remains visible');
  assert.equal(await page.locator('#sl-link').inputValue(),'','A hidden fallback retains stale search settings');
}
async function openInspector(page){
  const definition=page.locator('#sl-results .sl-result-definition').first();
  if(!await definition.evaluate(el=>el.open))await definition.locator(':scope > summary').click();
  const inspector=definition.locator('.sl-term-inspector');
  await inspector.waitFor({state:'attached'});
  if(!await inspector.evaluate(el=>el.open))await inspector.locator(':scope > summary').click();
  await inspector.locator('tbody tr').first().waitFor({state:'attached'});
  return {definition,inspector};
}
async function firstIndex(inspector){
  return Number(await inspector.locator('tbody tr').first().locator('th').textContent());
}
async function containedControls(page){
  const measurements=await page.evaluate(()=>{
    const selectors=['#sl-search > .sl-query > input','#sl-search > .sl-query > button',
      '#sl-results .sl-term-controls input','#sl-results .sl-term-controls button',
      '.sl-search-rules>div'];
    return selectors.flatMap(selector=>[...document.querySelectorAll(selector)]
      .filter(el=>el.getClientRects().length).map(el=>{
        const parent=el.closest('.sl-term-controls,.sl-query,.sl-search-rules');
        const box=el.getBoundingClientRect(),container=parent.getBoundingClientRect();
        return {selector,text:(el.textContent||el.value||'').trim().slice(0,50),
          left:box.left,right:box.right,parentLeft:container.left,parentRight:container.right};
      }));
  });
  for(const item of measurements)assert.ok(item.left>=item.parentLeft-1&&item.right<=item.parentRight+1,
    'A control exceeds its containing row: '+JSON.stringify(item));
  return measurements;
}
async function readableLabel(page){
  const label=await page.locator('#sl-results .sl-definition-label').first().evaluate(el=>{
    const summary=el.closest('summary'),box=summary.getBoundingClientRect();
    const range=document.createRange();range.selectNodeContents(el);
    return {text:el.textContent,whiteSpace:getComputedStyle(summary).whiteSpace,
      left:box.left,right:box.right,top:box.top,bottom:box.bottom,
      lines:[...range.getClientRects()].map(rect=>({left:rect.left,right:rect.right,top:rect.top,bottom:rect.bottom}))};
  });
  assert.ok(label.lines.length>0,'The formula summary label is not displayed');
  for(const line of label.lines)assert.ok(line.left>=label.left-1&&line.right<=label.right+1&&
    line.top>=label.top-1&&line.bottom<=label.bottom+1,
    'The formula summary label is clipped: '+JSON.stringify(label));
  return label;
}
async function contrast(page){
  return page.evaluate(()=>{
    const parse=color=>{const values=color.match(/[\d.]+/g)?.map(Number);return values&&values.length>=3?values:null;};
    const luminance=rgb=>rgb.slice(0,3).map(value=>value/255)
      .map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4)
      .reduce((sum,value,i)=>sum+value*[.2126,.7152,.0722][i],0);
    return ['#sl-query','#sl-search > .sl-query > button[type=submit]',
      '#sl-count','#sl-results .sl-variant-select','#sl-results .sl-term-status',
      '#sl-results .sl-definition-label'].map(selector=>{
      const element=document.querySelector(selector),foreground=parse(getComputedStyle(element).color);
      let ancestor=element,background;
      while(ancestor){
        const color=parse(getComputedStyle(ancestor).backgroundColor);
        if(color&&(color.length<4||color[3]===1)){background=color;break;}
        ancestor=ancestor.parentElement;
      }
      if(!foreground||!background)throw Error('No opaque contrast sample for '+selector);
      const a=luminance(foreground),b=luminance(background);
      return {selector,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
    });
  });
}

(async()=>{
  try{
    browser=await chromium.launch({headless:true});
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:950}});
      // Exercise both clipboard branches without depending on host permissions.
      // The rest of the page uses the production browser APIs and data.
      await context.addInitScript(()=>{
        window.__searchClipboard={deny:false,last:null,hold:false,pending:null};
        Object.defineProperty(navigator,'clipboard',{configurable:true,value:{
          writeText:async text=>{
            if(window.__searchClipboard.hold)return new Promise((resolve,reject)=>{
              window.__searchClipboard.pending={text:String(text),resolve,reject};
            });
            if(window.__searchClipboard.deny)throw Error('Clipboard denied for this regression');
            window.__searchClipboard.last=String(text);
          }
        }});
      });
      const page=await context.newPage();activePage=page;
      page.on('pageerror',error=>report.errors.push({width,url:page.url(),message:error.message}));
      const stage=name=>{report.stage={width,name};};
      stage('search link lifecycle');
      await page.goto(url('sequence-library.html'));await ready(page);
      assert.equal(await page.locator('#sl-results>li').count(),24);
      await failedSearchCopy(page);
      await page.locator('#sl-next').focus();await page.keyboard.press('Enter');
      await fallbackCleared(page);await focusIs(page,'#sl-count');
      assert.match(await page.locator('#sl-page').textContent(),/Page 2 of/);
      await failedSearchCopy(page);
      await page.locator('#sl-query').fill('id:KFOR-P-03-02');
      await fallbackCleared(page);
      await submit(page);
      assert.deepEqual(await resultIds(page),['KFOR-P-03-02']);
      // Repeating a valid submission also clears a previously shown fallback.
      await failedSearchCopy(page);await submit(page);await fallbackCleared(page);
      await failedSearchCopy(page);await denyCopy(page,false);
      await page.locator('#sl-share').click();
      await page.waitForFunction(()=>document.querySelector('#sl-link-wrap').hidden);
      await fallbackCleared(page);
      const successfulLink=await page.evaluate(()=>window.__searchClipboard.last);
      assert.equal(new URL(successfulLink).searchParams.get('q'),'id:KFOR-P-03-02');
      // A delayed clipboard rejection must not restore a link from an older search.
      await page.evaluate(()=>{window.__searchClipboard.hold=true;});
      await page.locator('#sl-share').click();
      await page.waitForFunction(()=>Boolean(window.__searchClipboard.pending));
      await submit(page,'id:KSEQ-000025');
      const statusAfterSearch=await page.locator('#sl-action-status').textContent();
      await page.evaluate(async()=>{
        const pending=window.__searchClipboard.pending;
        window.__searchClipboard.hold=false;window.__searchClipboard.pending=null;
        pending.reject(Error('Delayed clipboard denial from the previous search'));
        await new Promise(resolve=>requestAnimationFrame(resolve));
      });
      await fallbackCleared(page);
      assert.equal(await page.locator('#sl-action-status').textContent(),statusAfterSearch);
      assert.notEqual(await page.evaluate(()=>document.activeElement?.id),'sl-link');
      assert.deepEqual(await resultIds(page),['KSEQ-000025']);
      await submit(page,'id:KFOR-P-03-02');

      stage('invalid search preserves the completed result');
      await page.locator('[data-collection=formulas]').click();
      const oldIds=await resultIds(page),oldCount=await page.locator('#sl-count').textContent();
      const oldChips=await page.locator('#sl-active-filters button').allTextContents();
      assert.equal(await page.locator('#sl-collection').inputValue(),'formulas');
      await submit(page,'unknown:value');
      await focusIs(page,'#sl-query');
      assert.equal(await page.locator('#sl-query').getAttribute('aria-invalid'),'true');
      assert.equal(await page.locator('#sl-query').getAttribute('aria-errormessage'),'sl-error');
      assert.equal(await page.locator('#sl-error').isVisible(),true);
      assert.deepEqual(await resultIds(page),oldIds);
      assert.equal(await page.locator('#sl-count').textContent(),oldCount);
      assert.equal(await page.locator('#sl-result-state').isVisible(),true);
      assert.match(await page.locator('#sl-result-state').textContent(),/previous successful search/i);
      // A scope/filter action with the invalid draft must retain the successful view.
      await page.locator('[data-scope=families]').click();
      assert.equal(await page.locator('#sl-scope').inputValue(),'records');
      assert.equal(await page.locator('[data-scope=records]').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('[data-scope=families]').getAttribute('aria-pressed'),'false');
      assert.deepEqual(await resultIds(page),oldIds);
      assert.equal(await page.locator('#sl-count').textContent(),oldCount);
      assert.equal(await page.locator('#sl-query').inputValue(),'unknown:value');
      await page.locator('[data-collection=atlas]').click();
      assert.equal(await page.locator('#sl-collection').inputValue(),'formulas');
      assert.equal(await page.locator('[data-collection=formulas]').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('[data-collection=atlas]').getAttribute('aria-pressed'),'false');
      assert.deepEqual(await page.locator('#sl-active-filters button').allTextContents(),oldChips);
      assert.deepEqual(await resultIds(page),oldIds);
      await page.locator('#sl-query').screenshot({path:path.join(output,'invalid-query-'+width+'.png')});
      await page.locator('#sl-clear').click();
      assert.equal(await page.locator('#sl-scope').inputValue(),'records');
      assert.equal(await page.locator('#sl-result-state').isVisible(),false);
      assert.equal(await page.locator('#sl-error').isVisible(),false);
      assert.equal(await page.locator('#sl-query').getAttribute('aria-invalid'),null);
      await submit(page,'unknown:value');await submit(page,'id:KFOR-P-03-02');
      assert.deepEqual(await resultIds(page),['KFOR-P-03-02']);
      assert.equal(await page.locator('#sl-result-state').isVisible(),false);
      assert.equal(await page.locator('#sl-query').getAttribute('aria-errormessage'),null);

      stage('first invalid family query has coherent empty state');
      await page.goto(url('sequence-library.html?scope=families&q=unknown%3Avalue'));await ready(page);
      assert.equal(await page.locator('#sl-scope').inputValue(),'families');
      assert.equal(await page.locator('[data-scope=families]').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('#sl-search .sl-collections').isVisible(),false);
      for(const key of ['collection','kind','representation','status','hits','saved','match']){
        assert.equal(await page.locator('#sl-'+key).isDisabled(),true);
        assert.equal(await page.locator('#sl-'+key).evaluate(el=>el.closest('label').hidden),true);
      }
      for(const key of ['mode','paper']){
        assert.equal(await page.locator('#sl-'+key).isDisabled(),false);
        assert.equal(await page.locator('#sl-'+key).evaluate(el=>el.closest('label').hidden),false);
      }
      assert.equal(await page.locator('#sl-results>li').count(),0);
      assert.equal(await page.locator('#sl-share').isDisabled(),true);
      assert.equal(await page.locator('#sl-export').isDisabled(),true);
      assert.match(await page.locator('#sl-result-state').textContent(),/No search results yet/i);
      assert.equal(await page.locator('#sl-result-state').isVisible(),true);
      await submit(page,'Hankel');
      assert.ok(await page.locator('#sl-results>li.sl-family-result').count()>0);
      assert.equal(await page.locator('#sl-result-state').isVisible(),false);
      assert.equal(await page.locator('#sl-share').isDisabled(),false);
      await fit(page);

      stage('keyboard scope transition');
      await page.goto(url('sequence-library.html'));await ready(page);
      await page.locator('#sl-generalized').focus();await page.keyboard.press('Enter');
      assert.equal(await page.locator('#sl-generalized').isVisible(),false);
      await focusIs(page,'#sl-count');
      assert.equal(await page.locator('#sl-scope').inputValue(),'families');

      stage('inspector labels and keyboard page boundaries');
      await page.goto(url('sequence-library.html?q=id%3AKFOR-P-03-02'));await ready(page);
      let {definition,inspector}=await openInspector(page);
      const picker=definition.locator('.sl-variant-select'),summary=definition.locator(':scope > summary');
      assert.match(await summary.getAttribute('aria-label'),/^Defining formula for /);
      await picker.selectOption('1');
      assert.equal(await definition.locator('.sl-definition-label').textContent(),'Alternative formula');
      assert.match(await summary.getAttribute('aria-label'),/^Alternative formula for /);
      await picker.selectOption('0');
      assert.equal(await definition.locator('.sl-definition-label').textContent(),'Defining formula');
      assert.match(await summary.getAttribute('aria-label'),/^Defining formula for /);
      const offset=await firstIndex(inspector);
      assert.equal(offset,2);
      const next=inspector.getByRole('button',{name:'Next 8',exact:true});
      const previous=inspector.getByRole('button',{name:'Previous 8',exact:true});
      await next.focus();await page.keyboard.press('Enter');
      assert.equal(await firstIndex(inspector),offset+8);
      assert.equal(await next.evaluate(el=>document.activeElement===el),true);
      await page.keyboard.press('Enter');
      assert.equal(await firstIndex(inspector),offset+16);assert.equal(await next.isDisabled(),true);
      await focusIs(page,'#sl-results .sl-term-scroll');
      assert.notEqual(await inspector.locator('.sl-term-scroll').evaluate(el=>getComputedStyle(el).outlineStyle),'none');
      await previous.focus();await page.keyboard.press('Enter');
      assert.equal(await previous.evaluate(el=>document.activeElement===el),true);
      await page.keyboard.press('Enter');
      assert.equal(await firstIndex(inspector),offset);assert.equal(await previous.isDisabled(),true);
      await focusIs(page,'#sl-results .sl-term-scroll');

      stage('blank jump preserves an offset-zero record window');
      await page.goto(url('sequence-library.html?q=id%3AKSEQ-000001'));await ready(page);
      ({definition,inspector}=await openInspector(page));
      assert.equal(await firstIndex(inspector),0);
      await inspector.getByRole('button',{name:'Next 8',exact:true}).click();
      const previousRows=await inspector.locator('tbody').textContent();
      const previousStatus=await inspector.locator('.sl-term-status').textContent();
      const jump=inspector.getByLabel('Go to stored n');
      await jump.fill('');await inspector.getByRole('button',{name:'Go',exact:true}).click();
      assert.equal(await jump.evaluate(el=>el.required&&el.validity.valueMissing),true);
      assert.equal(await jump.evaluate(el=>document.activeElement===el),true);
      assert.equal(await inspector.locator('tbody').textContent(),previousRows);
      assert.equal(await inspector.locator('.sl-term-status').textContent(),previousStatus);
      // The handler also rejects a blank value when native form validation is bypassed.
      await inspector.locator('form').evaluate(el=>el.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
      assert.equal(await jump.evaluate(el=>el.validity.customError),true);
      assert.equal(await inspector.locator('tbody').textContent(),previousRows);

      stage('cross-tab saved state preserves current inspection and draft');
      await page.goto(url('sequence-library.html?q=id%3AKFOR-P-03-02'));await ready(page);
      ({definition,inspector}=await openInspector(page));
      await definition.locator('.sl-variant-select').selectOption('1');
      await inspector.getByRole('button',{name:'Next 8',exact:true}).click();
      await inspector.getByRole('button',{name:'Next 8',exact:true}).click();
      await inspector.getByRole('button',{name:'Copy inspection link',exact:true}).click();
      await page.waitForFunction(()=>window.__searchClipboard.last?.includes('sl-record='));
      const inspectionLink=await page.evaluate(()=>window.__searchClipboard.last);
      assert.equal(new URL(inspectionLink).searchParams.get('sl-start'),'18');
      await page.goto(inspectionLink);await ready(page);
      ({definition,inspector}=await openInspector(page));
      assert.equal(await definition.locator('.sl-variant-select').inputValue(),'1');
      assert.equal(await firstIndex(inspector),18);
      await definition.locator('.sl-variant-select').selectOption('2');
      await inspector.getByRole('button',{name:'Previous 8',exact:true}).click();
      await page.locator('#sl-query').fill('theta unfinished draft');
      await inspector.getByLabel('Go to stored n').focus();
      await page.evaluate(()=>{window.__inspectionBeforeStorage=document.querySelector('#sl-results .sl-term-inspector');});
      const saveButton=page.locator('[data-save-sequence="KFOR-P-03-02"]');
      assert.equal(await saveButton.getAttribute('aria-pressed'),'false');
      const other=await context.newPage();
      other.on('pageerror',error=>report.errors.push({width,url:other.url(),message:error.message}));
      await other.goto(url('sequence-library.html'));await ready(other);
      await other.evaluate(()=>localStorage.setItem('komorebi.sequence-atlas.saved.v1',JSON.stringify(['KFOR-P-03-02'])));
      await page.waitForFunction(()=>document.querySelector('[data-save-sequence="KFOR-P-03-02"]')?.getAttribute('aria-pressed')==='true');
      assert.equal(await page.evaluate(()=>window.__inspectionBeforeStorage===document.querySelector('#sl-results .sl-term-inspector')),true,
        'A cross-tab save rebuilt the active inspector');
      assert.equal(await definition.locator('.sl-variant-select').inputValue(),'2');
      assert.equal(await firstIndex(inspector),10);
      assert.equal(await page.locator('#sl-query').inputValue(),'theta unfinished draft');
      assert.equal(await inspector.getByLabel('Go to stored n').evaluate(el=>document.activeElement===el),true);
      await other.close();

      stage('search and inspector presentation');
      await page.locator('#sl-query').fill('id:KFOR-P-03-02');
      const help=page.locator('.sl-search-guide');
      await help.locator(':scope > summary').focus();await page.keyboard.press('Enter');
      assert.equal(await help.evaluate(el=>el.open),true);
      assert.equal(await help.locator('.sl-search-rules>div').count(),5);
      await page.selectOption('#site-math-display','typeset');await settle(page);
      const math=definition.locator('.math-typeset mjx-container svg').first();
      await math.waitFor({state:'visible'});
      assert.equal(await math.evaluate(el=>getComputedStyle(el).maxWidth),'none',
        'A long result formula must retain its natural glyph size');
      await fit(page);await containedControls(page);await readableLabel(page);
      await help.screenshot({path:path.join(output,'search-help-'+width+'.png')});
      await page.locator('#sl-results>li').screenshot({path:path.join(output,'opened-record-'+width+'.png')});
      const original=await definition.locator('p.sar-formula').first().textContent();
      await page.selectOption('#site-math-display','plain');
      assert.equal(await definition.locator('p.sar-formula').first().isVisible(),true);
      assert.equal(await definition.locator('p.sar-formula').first().textContent(),original);
      await fit(page);
      await page.selectOption('#site-math-display','typeset');await settle(page);

      const palette=[];
      for(const theme of ['light','dark']){
        await page.selectOption('#sq-page-theme',theme);
        const samples=await contrast(page);
        for(const sample of samples)assert.ok(sample.ratio>=4.5,
          'Insufficient search text contrast in '+theme+': '+JSON.stringify(sample));
        palette.push({theme,samples});
      }
      await page.selectOption('#sq-page-theme','light');
      await page.emulateMedia({forcedColors:'active',reducedMotion:'reduce'});await fit(page);
      await inspector.locator('.sl-term-scroll').focus();
      await page.keyboard.press('ArrowRight');
      assert.notEqual(await inspector.locator('.sl-term-scroll').evaluate(el=>getComputedStyle(el).outlineStyle),'none');
      if(width===320)await page.locator('#sl-results>li').screenshot({path:path.join(output,'forced-colors-record.png')});
      await page.emulateMedia({forcedColors:'none',reducedMotion:'no-preference'});

      let enlarged;
      if(width<500){
        stage('enlarged search and inspector presentation');
        await page.evaluate(()=>document.documentElement.style.fontSize='200%');await settle(page);
        const inputs=await page.locator('#sl-query,#sl-results .sl-term-controls input').evaluateAll(elements=>{
          const canvas=document.createElement('canvas'),context=canvas.getContext('2d');
          return elements.map(element=>{
            const style=getComputedStyle(element),sample=element.id==='sl-query'?'id:KFOR-':'999';
            context.font=[style.fontStyle,style.fontWeight,style.fontSize,style.fontFamily].join(' ');
            const nativeRoom=20; // Native search clear control or number steppers.
            return {name:element.id||'stored-index',fontSize:parseFloat(style.fontSize),
              usable:element.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight)-nativeRoom,
              needed:context.measureText(sample).width+8,sample};
          });
        });
        for(const input of inputs){
          assert.ok(input.fontSize>=31.5,'An active input failed to retain 200% text: '+JSON.stringify(input));
          assert.ok(input.usable>=input.needed,'An enlarged input has insufficient editing room: '+JSON.stringify(input));
        }
        await fit(page);await containedControls(page);
        enlarged={inputs,summary:await readableLabel(page)};
        await help.screenshot({path:path.join(output,'search-help-enlarged-'+width+'.png')});
        await page.locator('#sl-search').screenshot({path:path.join(output,'search-controls-enlarged-'+width+'.png')});
        await page.locator('#sl-results>li').screenshot({path:path.join(output,'opened-record-enlarged-'+width+'.png')});
        await page.evaluate(()=>document.documentElement.style.removeProperty('font-size'));
      }
      report.widths.push({width,searchFallbackLifecycle:true,staleClipboardCompletionIgnored:true,
        invalidSearchRetainsResults:true,failedScopeAndFilterPreserved:true,
        initialInvalidFamilyScope:true,keyboardScopeFocus:true,formulaAccessibleName:true,
        inspectorBoundaryFocus:true,blankIndexPreservesWindow:true,crossTabInspectionPreserved:true,
        draftPreserved:true,naturalFormulaSize:true,plainTextPreserved:true,palette,
        forcedColors:true,reducedMotion:true,enlarged:enlarged||null,overflow:false});
      await context.close();activePage=null;
    }
    assert.deepEqual(report.errors,[]);report.status='passed';delete report.stage;
  }catch(error){
    report.status='failed';report.failure=error.stack||String(error);
    if(activePage&&!activePage.isClosed()){
      report.failureUrl=activePage.url();
      try{await activePage.screenshot({path:path.join(output,'failure.png')});}
      catch(screenshotError){report.screenshotError=String(screenshotError);}
      try{fs.writeFileSync(path.join(output,'failure.html'),await activePage.content());}
      catch(contentError){report.contentError=String(contentError);}
    }
    throw error;
  }finally{
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
    if(browser)await browser.close();
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
