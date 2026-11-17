const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'sequence-usability-browser';
fs.mkdirSync(output,{recursive:true});
const url=relative=>new URL(relative,base).href;
async function fit(page){
  await page.evaluate(async()=>{
    await document.fonts.ready;
    await window.KomorebiMath?.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true,'Page-wide horizontal overflow');
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0,'MathJax error');
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  const report={status:'running',widths:[],noJavaScript:false,errors:[]};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940}});
      const page=await context.newPage();
      page.on('pageerror',error=>report.errors.push(error.message));
      await page.goto(url('sequence-library.html'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('.sl-primary-nav a').count(),3);
      assert.equal(await page.locator('#sl-results>li').count(),24);
      assert.equal(await page.locator('.sl-search-guide').evaluate(el=>el.open),false);
      await page.locator('.sl-search-guide > summary').click();
      assert.equal(await page.locator('.sl-search-examples a').count(),3);
      assert.equal(await page.locator('.sl-search-rules>div').count(),5);
      assert.match(await page.locator('.sl-search-guide').textContent(),/spacing N/);
      assert.match(await page.locator('.sl-search-guide').textContent(),/recurrence order/);
      assert.match(await page.locator('.sl-search-guide').textContent(),/question mark represents one unknown integer/i);
      assert.equal(await page.locator('.sl-search-guide code').filter({hasText:'paper:SF-VI'}).count(),1);

      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'compact');
      assert.equal(await page.locator('#sl-result-layout').isVisible(),true);
      assert.equal(await page.locator('#sl-result-layout [data-layout=compact]').getAttribute('aria-pressed'),'true');
      assert.equal(await page.locator('#sl-results>li .sl-result-main').count(),24);
      assert.equal(await page.locator('#sl-results>li .sl-term-preview').count(),24);
      const compactHeight=await page.locator('#sl-results>li').first().evaluate(el=>el.getBoundingClientRect().height);
      assert.ok(compactHeight>0&&compactHeight<600,'Compact result has unexpected height: '+compactHeight);
      await page.locator('#sl-result-layout [data-layout=cards]').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'cards');
      assert.equal(await page.locator('#sl-result-layout [data-layout=cards]').getAttribute('aria-pressed'),'true');
      await page.reload();await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'cards');
      await page.locator('#sl-result-layout [data-layout=compact]').click();
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'compact');
      assert.equal(await page.locator('#sl-results .sl-result-definition:not([open])').count(),24);
      assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#sl-extra-tools #research-families').count(),1);
      assert.equal(await page.locator('#comparison').evaluate(el=>el.previousElementSibling?.id),'transfers');
      const cardMetrics=await page.locator('#sl-results>li').first().evaluate(el=>({
        align:getComputedStyle(el).alignSelf,margin:getComputedStyle(el.querySelector('.sp-actions')).marginTop,
        height:el.getBoundingClientRect().height
      }));
      assert.equal(cardMetrics.align,'start');
      assert.ok(parseFloat(cardMetrics.margin)<20,'Result actions have an excessive forced margin');
      assert.ok(cardMetrics.height<680,'Collapsed result card uses too much vertical space');
      assert.equal(await page.locator('#research-families>.sl-topic-disclosure').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#library-sources>.sl-topic-disclosure').evaluate(el=>el.open),false);
      await page.locator('#sl-results .sl-result-definition summary').first().click();
      assert.equal(await page.locator('#sl-results .sl-result-definition').first().evaluate(el=>el.open),true);
      await fit(page);
      await page.goto(url('sequence-library.html?q=id%3AKSEQ-000025#library-search'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#sl-results>li').count(),1);
      assert.equal(await page.locator('#sl-results .sl-result-definition').first().evaluate(el=>el.open),true);
      assert.match(await page.locator('#sl-results .sl-result-definition summary').first().getAttribute('aria-label'),/Defining formula for/);
      await page.locator('#sl-results .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      assert.equal(await page.locator('#sl-results [data-math-tex]').first().isVisible(),true);
      await fit(page);
      await page.goto(url('sequence-library.html#oeis'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#sl-oeis-query').isVisible(),true);
      await page.goto(url('sequence-library.html#research-graph'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#research-graph>details').evaluate(el=>el.open),true);
      await fit(page);
      await page.goto(url('sequence-library.html#research-families'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#research-families>.sl-topic-disclosure').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#research-families .sl-research-group').count(),4);
      assert.match(await page.locator('#research-families .sl-research-intro').textContent(),/359 indexed research records/);
      const kinds={
        'secancy parameter column':88,'secancy coefficient triangle':11,
        'Euler-transfer theta':12,'theta polynomial column':12,'theta coefficient triangle':1,
        'block-Appell coefficient triangle':21,'block-Appell coefficient column':84,
        'k-step reciprocal power':120,'k-bonacci':10
      };
      const links=await page.locator('#research-families .sl-research-group ul a').evaluateAll(nodes=>
        nodes.map(node=>({href:node.getAttribute('href'),label:node.textContent.trim()})));
      assert.equal(links.length,9);
      for(const item of links){
        const q=new URL(item.href,url('sequence-library.html')).searchParams.get('q');
        const kind=/^kind:"(.+)"$/.exec(q)?.[1];
        assert.ok(kind&&kinds[kind],item.href);
        assert.ok(item.label.includes('('+kinds[kind]+')'),item.label);
      }
      assert.equal(Object.values(kinds).reduce((sum,n)=>sum+n,0),359);
      await fit(page);
      const exercise=width===1440
        ?['secancy parameter column','block-Appell coefficient column','k-step reciprocal power']
        :[width===390?'theta polynomial column':'secancy coefficient triangle'];
      for(const kind of exercise){
        const match=links.find(item=>new URL(item.href,url('sequence-library.html')).searchParams.get('q')==='kind:"'+kind+'"');
        assert.ok(match);
        await page.goto(new URL(match.href,url('sequence-library.html')).href);
        await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
        assert.match(await page.locator('#sl-count').textContent(),new RegExp('^'+kinds[kind]+' matching records'));
        assert.equal(await page.locator('#sl-error').isVisible(),false);
      }
      if(width===1440){
        await page.goto(url('sequence-library.html#research-families'));
        await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
        const all=await page.locator('#research-families .sl-research-intro a').getAttribute('href');
        assert.equal(new URL(all,url('sequence-library.html')).searchParams.get('q'),'tag:research-derived');
        await page.goto(new URL(all,url('sequence-library.html')).href);
        await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
        assert.match(await page.locator('#sl-count').textContent(),/^359 matching records/);
      }

      await page.goto(url('sequence-library.html#transfers'));
      await page.locator('[data-transfer-ready=true]').waitFor({timeout:90000});
      assert.equal(await page.locator('#tr-form').isVisible(),true);
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#tr-index-map').evaluate(el=>el.open),false);
      await page.locator('#tr-index-map>summary').click();
      await page.locator('#tr-index-map .math-pair[data-math-pair-ready=true]').waitFor({timeout:30000});
      assert.match(await page.locator('#tr-index-map [data-math-plain]').textContent(),/source index/);
      const gap=await page.evaluate(()=>{
        const search=document.getElementById('library-search').getBoundingClientRect(),
              hero=document.querySelector('.sl-hero').getBoundingClientRect();
        return Math.round(search.top-hero.bottom);
      });
      assert.ok(gap<100,'There is too much empty space between the hero and search: '+gap);
      assert.equal(await page.locator('.sr-transfer-method').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#tr-result-nav a').count(),4);
      await page.locator('#tr-result-nav a[href="#tr-matrices"]').click();
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#tr-matrix-size').isVisible(),true);
      const tableHeight=await page.locator('#tr-result>.sar-scroll').evaluate(el=>el.getBoundingClientRect().height);
      assert.ok(tableHeight<=320,'Exact data section too tall: '+tableHeight);
      await fit(page);
      report.widths.push({width,compactResults:true,layoutToggle:true,keyboardLayoutControl:true,layoutPersistence:true,deepLinks:true,accessibleDisclosures:true,transferShortcuts:true,noOverflow:true});
      await page.screenshot({path:path.join(output,'transfer-compact-'+width+'.png')});
      await context.close();
    }
    const context=await browser.newContext({viewport:{width:320,height:900},javaScriptEnabled:false});
    const page=await context.newPage();
    await page.goto(url('sequence-library.html'));
    assert.equal(await page.locator('.sl-primary-nav a').count(),3);
    assert.equal(await page.locator('#sl-result-layout').isVisible(),false);
    assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),false);
    assert.equal(await page.locator('#tr-form').count(),0);
    assert.equal(await page.locator('.sr-transfer-example').count(),1);
    await page.locator('.sr-transfer-example summary').click();
    assert.equal(await page.locator('.sr-transfer-example').evaluate(el=>el.open),true);
    await page.locator('#oeis>.sl-topic-disclosure summary').click();
    assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),true);
    await page.locator('#sl-extra-tools>summary').click();
    assert.equal(await page.locator('#sl-extra-tools').evaluate(el=>el.open),true);
    assert.equal(await page.locator('#research-families .sl-research-group ul a').count(),9);
    await page.locator('#research-families .sl-topic-disclosure>summary').click();
    assert.equal(await page.locator('#research-families .sl-topic-disclosure').evaluate(el=>el.open),true);
    assert.equal(await page.locator('#sl-count a[href="sequence-library/index.html"]').count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true);
    await context.close();
    report.noJavaScript=true;
    assert.deepEqual(report.errors,[]);
    report.status='passed';
  }finally{
    await browser.close();
    fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  }
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
