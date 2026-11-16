/* Browser regressions for the completed family search and recovered archive. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const base=process.argv[2]||'http://127.0.0.1:8846/';
const out=process.argv[3]||'sequence-family-completion';
fs.mkdirSync(out,{recursive:true});
const report={widths:[],errors:[],status:'running'};
const url=relative=>new URL(relative,base).href;
async function ready(page){await page.locator('[data-library-ready=true]').waitFor({timeout:60000});}
async function math(page){
  for(let i=0;i<2;i++)await page.evaluate(async()=>{
    await window.MathJax?.startup?.promise;
    await window.KomorebiMath?.ready;
    await document.fonts.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0);
}
async function fits(page,{staticOnly=false}={}){
  // Disabled page JavaScript cannot resolve a requestAnimationFrame promise.
  // The static check waits for styles/resources, then measures synchronously.
  if(staticOnly)await page.waitForLoadState('load');else await math(page);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),
    `Horizontal overflow at ${page.viewportSize().width}px: ${page.url()}`);
}
async function query(page,text){
  await page.fill('#sl-query',text);
  await page.locator('#sl-search button[type=submit]').click();
  await math(page);
}
async function download(page,selector,name){
  const pending=page.waitForEvent('download');
  await page.locator(selector).click();
  const value=await pending;
  const target=path.join(out,name);
  await value.saveAs(target);
  return fs.readFileSync(target,'utf8');
}
async function factorialEquality(page,family){
  await page.goto(url(`generalized-families/${family}.html`));
  await ready(page);await math(page);
  const formulas=await page.locator('#definition .arithmatex').evaluateAll(elements=>
    elements.flatMap(element=>window.MathJax.startup.document.getMathItemsWithin([element])).map(item=>item.math));
  assert.ok(formulas.some(formula=>formula.includes('!}}=')),`${family}: rendered factorial/equality missing`);
  assert.ok(formulas.every(formula=>!formula.includes('\\ne ')),`${family}: factorial became inequality`);
  assert.equal(await page.locator('#definition mjx-container').count()>0,true);
  assert.equal(await page.locator('#definition mjx-assistive-mml mo').filter({hasText:'≠'}).count(),0);
  await fits(page);
}

(async()=>{
  let browser,active;
  try{
    browser=await chromium.launch({headless:true});
    for(const width of [1440,390,320]){
      const context=await browser.newContext({
        viewport:{width,height:1000},isMobile:width<500,hasTouch:width<500,
        permissions:['clipboard-read','clipboard-write'],
      });
      const page=active=await context.newPage();
      page.on('pageerror',error=>report.errors.push({width,message:error.message}));
      await page.goto(url('sequence-library.html?scope=families#library-search'));
      await ready(page);await math(page);
      assert.match(await page.locator('#sl-count').textContent(),/36 matching families/);
      assert.equal(await page.locator('#sl-results>li').count(),24);
      assert.equal(await page.locator('[data-scope=families]').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('#sl-saved-status').isVisible(),false);
      await fits(page);
      await page.screenshot({path:path.join(out,`family-search-${width}.png`),fullPage:false});

      if(width===1440){
        const response=await page.request.get(url('assets/sequence-generalized-data.json'));
        assert.equal(response.ok(),true);
        const data=await response.json();
        assert.equal(data.families.length,36);
        assert.equal(data.sources.length,12);
        assert.deepEqual(data.archive_coverage,{records:90,assigned:90});
        assert.deepEqual(data.record_coverage,{records:2292,assigned:2292});
        const assignments=data.families.flatMap(family=>family.archive_record_ids);
        const expected=Array.from({length:90},(_,i)=>`KOM${String(i+1).padStart(3,'0')}`);
        assert.deepEqual(assignments.slice().sort(),expected);
        assert.equal(new Set(assignments).size,90);
        assert.equal(data.families.filter(family=>family.engine).length,10);
        report.catalogue={families:36,sources:12,records:2292,assignedRecords:2292,archiveRecords:90,exactEngines:10};
      }

      await page.locator('#sl-next').click();
      assert.match(await page.locator('#sl-count').textContent(),/25–36/);
      await page.reload();await ready(page);
      assert.match(await page.locator('#sl-count').textContent(),/25–36/);
      await query(page,'Hankel');
      assert.equal(await page.locator('#sl-results>li[data-result-id="GF-BLOCK-HANKEL"]').count(),1);
      await page.locator('#sl-clear').click();
      assert.equal(await page.inputValue('#sl-scope'),'families');
      assert.match(await page.locator('#sl-count').textContent(),/36 matching families/);

      await page.locator('#sl-search details').evaluate(element=>{element.open=true;});
      for(const key of ['collection','kind','representation','status','hits','saved','match']){
        assert.equal(await page.locator(`#sl-${key}`).isVisible(),false,key);
      }
      assert.equal(await page.locator('#sl-mode').isVisible(),true);
      assert.equal(await page.locator('#sl-paper').isVisible(),true);
      await page.selectOption('#sl-mode','Source-defined discrete construction');
      assert.match(await page.locator('#sl-count').textContent(),/13 matching families/);
      await page.selectOption('#sl-paper','ARCHIVE');
      assert.match(await page.locator('#sl-count').textContent(),/13 matching families/);
      await fits(page);
      await page.locator('#sl-share').click();
      const shared=await page.evaluate(()=>navigator.clipboard.readText());
      assert.equal(new URL(shared).searchParams.get('scope'),'families');
      assert.equal(new URL(shared).searchParams.get('mode'),'Source-defined discrete construction');
      assert.equal(new URL(shared).searchParams.get('paper'),'ARCHIVE');
      await page.goto(shared);await ready(page);
      assert.match(await page.locator('#sl-count').textContent(),/13 matching families/);
      const exported=await download(page,'#sl-export',`archive-families-${width}.csv`);
      assert.match(exported,/"construction_type","source","indexed_records","url"/);
      assert.match(exported,/"GF-SMITH-POLYNOMIALS"/);
      assert.equal(exported.trim().split(/\r?\n/).length,14);

      await page.locator('#sl-clear').click();
      await page.locator('#sl-search details').evaluate(element=>{element.open=true;});
      await page.selectOption('#sl-paper','SF-VI');
      assert.match(await page.locator('#sl-count').textContent(),/2 matching families/);
      assert.deepEqual((await page.locator('#sl-results>li').evaluateAll(items=>items.map(item=>item.dataset.resultId))).sort(),
        ['GF-CROSS-SHAPE','GF-SHAPE-TRANSFER']);
      await page.locator('#sl-clear').click();
      await query(page,'no_such_family_987654');
      assert.equal(await page.locator('#sl-empty').isVisible(),true);
      assert.equal(await page.locator('#sl-export').isDisabled(),true);
      await page.locator('#sl-reset').click();
      assert.equal(await page.inputValue('#sl-scope'),'families');
      assert.match(await page.locator('#sl-count').textContent(),/36 matching families/);

      await query(page,'id:GF-BLOCK-HANKEL');
      await page.locator('#sl-results a').filter({hasText:'Read construction and examples'}).click();
      await ready(page);await fits(page);
      assert.equal(await page.locator('#archive-records li').count(),4);
      assert.equal(await page.locator('#examples article').count(),3);
      assert.match(await page.locator('#definition').textContent(),/determinant order n\+1/);
      assert.equal(await page.locator('#gf-form').count(),0);
      const generator=page.locator('#reproduce a[download]');
      const bundle=await page.request.get(new URL(await generator.getAttribute('href'),page.url()).href);
      assert.equal(bundle.ok(),true);
      assert.equal((await bundle.body()).subarray(0,2).toString(),'PK');
      assert.match(await page.locator('#reproduce').textContent(),/python reproduce\.py --output regenerated/);
      await page.locator('#definition').screenshot({path:path.join(out,`hankel-definition-${width}.png`)});

      await page.goto(url('sequence-library.html?q=family:GF-BLOCK-HANKEL#library-search'));
      await ready(page);
      assert.match(await page.locator('#sl-count').textContent(),/4 matching records/);
      assert.deepEqual((await page.locator('#sl-results>li').evaluateAll(items=>items.map(item=>item.dataset.resultId))).sort(),
        ['KOM043','KOM044','KOM045','KOM046']);
      assert.equal(await page.inputValue('#sl-scope'),'records');
      await fits(page);

      for(const family of ['GF-RECIPROCAL','GF-THETA','GF-APPELL'])await factorialEquality(page,family);
      await page.goto(url('sequence-archive/KOM002.html'));
      const familyLink=page.locator('#sequence-details a[href*="GF-RECIPROCAL"]');
      assert.equal(await familyLink.count(),1);
      const parameters=JSON.parse(new URL(await familyLink.getAttribute('href'),page.url()).searchParams.get('parameters'));
      assert.equal(parameters.N,3);assert.equal(parameters.r,1);
      await familyLink.click();await ready(page);
      await page.locator('[data-family-ready=true]').waitFor({timeout:60000});
      assert.equal(await page.inputValue('#gf-N'),'3');
      assert.equal(await page.inputValue('#gf-r'),'1');
      assert.deepEqual((await page.locator('#gf-output table tbody tr td:last-child').allTextContents()).slice(0,4),
        ['1','1','19','1513']);
      assert.equal(await page.locator('#family-explorer>p').filter({hasText:'Enable JavaScript'}).count(),0);
      await fits(page);

      report.widths.push({width,scopedSearch:true,filters:true,sharing:true,csv:true,archivePages:true,
        memberLinks:true,factorialEquality:true,exactParameterHandoff:true,noHorizontalOverflow:true});
      await context.close();active=null;
    }

    const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:1000}});
    const page=active=await nojs.newPage();
    await page.goto(url('generalized-families/index.html'));
    assert.equal(await page.locator('[data-library]>ol>li').count(),36);
    assert.equal(await page.locator('#research-coverage article').count(),12);
    await fits(page,{staticOnly:true});
    await page.goto(url('generalized-families/GF-SMITH-POLYNOMIALS.html'));
    assert.equal(await page.locator('#archive-records li').count(),5);
    assert.match(await page.locator('#definition').textContent(),/flat j=n\(n\+1\)\/2\+k/);
    assert.equal(await page.locator('#reproduce a[download]').count(),1);
    await fits(page,{staticOnly:true});await nojs.close();active=null;
    report.noJavaScript=true;
    assert.deepEqual(report.errors,[]);
    report.status='passed';
  }catch(error){
    report.status='failed';report.failure=String(error.stack||error);
    if(active&&!active.isClosed()){
      report.failureURL=active.url();
      await active.screenshot({path:path.join(out,'failure.png'),fullPage:false}).catch(()=>{});
      fs.writeFileSync(path.join(out,'failure.html'),await active.content().catch(()=>''));
    }
    throw error;
  }finally{
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
    await browser?.close();
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
