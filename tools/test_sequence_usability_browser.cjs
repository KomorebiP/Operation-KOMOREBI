const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'sequence-usability-browser';
fs.mkdirSync(output,{recursive:true});
const href=name=>new URL(name,base).href;
async function fit(page){
  await page.evaluate(async()=>{
    await document.fonts.ready;
    await window.KomorebiMath?.ready;
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true,'Unexpected page-wide overflow at '+page.url());
  assert.equal(await page.locator('[data-mml-node=merror],mjx-merror').count(),0,'MathJax rendering error at '+page.url());
}
async function ready(page){
  await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
}
async function visit(page,name,kind){
  await page.goto(href(name));await ready(page);
  assert.equal(await page.locator('[data-library]').getAttribute('data-page'),kind);
  assert.equal(await page.locator('.sl-page-tabs a').count(),5);
  assert.equal(await page.locator('.sl-page-tabs [aria-current=page]').count(),1);
  await fit(page);
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  const report={status:'running',widths:[],noJavaScript:false,errors:[]};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940},permissions:['clipboard-read','clipboard-write']});
      const page=await context.newPage();
      page.on('pageerror',error=>report.errors.push(error.message));
      await visit(page,'sequence-library.html','search');
      assert.equal(await page.locator('#sl-results>li').count(),24);
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'compact');
      const unexpected=await page.locator('#tr-form,#sw-form,#sl-oeis-form,#connection-explorer').evaluateAll(nodes=>nodes.map(node=>({id:node.id,visible:!!node.getClientRects().length,parent:node.parentElement?.id||null})));assert.deepEqual(unexpected,[],'Search must not mount unrelated workbenches');
      assert.equal(await page.locator('.sl-search-guide').evaluate(el=>el.open),false);
      await page.locator('.sl-search-guide>summary').click();
      assert.equal(await page.locator('.sl-search-examples a').count(),3);
      assert.equal(await page.locator('.sl-search-rules>div').count(),5);
      await page.locator('#sl-result-layout [data-layout=cards]').focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'cards');
      await page.reload();await ready(page);
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'cards');
      await page.locator('#sl-result-layout [data-layout=compact]').click();
      assert.equal(await page.locator('#sl-results').getAttribute('data-layout'),'compact');
      assert.equal(await page.locator('#sl-results .sl-result-definition:not([open])').count(),24);
      assert.equal(await page.locator('#sl-results .sl-definition-excerpt').count(),24,
        'Each record needs a visible compact source formula preview');
      assert.equal(await page.locator('#sl-results .sl-variant-toolbar').count(),0,
        'Formula selectors are mounted only after a definition is opened');
      assert.equal(await page.locator('#sl-results .sl-term-inspector').count(),0,
        'Exact value inspectors must not mount for collapsed search results');
      assert.ok((await page.locator('#sl-results .sl-definition-excerpt').first().textContent()).trim().length>0);
      assert.equal(await page.locator('#sl-results .sl-result-more:not([open])').count(),24,
        'Secondary actions stay collapsed on a broad search');
      assert.equal(await page.locator('#sl-results .math-pair').count(),0,
        'Collapsed search definitions should not create hidden MathJax nodes');
      assert.equal(await page.locator('#sl-results>li').first().locator(':scope > .sp-actions > *').count(),3,
        'Only Plot, Save and Compare are the default actions');
      await page.locator('#sl-results>li').first().locator(':scope > .sl-result-more > summary').click();
      assert.equal(await page.locator('#sl-results>li').first().locator(':scope > .sl-result-more').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#sl-results>li').first().locator('.sl-result-more .sp-actions a').isVisible(),true);
      await page.locator('#sl-results .sl-result-definition summary').first().click();
      assert.equal(await page.locator('#sl-results .sl-result-definition').first().evaluate(el=>el.open),true);
      await page.waitForFunction(()=>{
        const detail=document.querySelector('#sl-results .sl-result-definition');
        const plain=detail?.querySelector('.sar-formula'),typeset=detail?.querySelector('[data-math-tex]');
        return Boolean(plain?.getClientRects().length||typeset?.getClientRects().length);
      },{timeout:30000});
      await fit(page);
      await page.goto(href('sequence-library.html?q=id%3AKFOR-P-03-02#library-search'));
      await ready(page);
      assert.equal(await page.locator('#sl-results>li').count(),1);
      const recorded=await page.evaluate(async()=>{
        const response=await fetch(new URL('assets/sequence-library-data.json',location.href));
        if(!response.ok)throw Error('Could not read exact formula fixture');
        const data=await response.json();
        return data.entries.find(item=>item.id==='KFOR-P-03-02');
      });
      assert.equal(recorded.formulas.length,4);
      assert.equal(recorded.source_degrees.length,recorded.terms.length);
      assert.equal(recorded.source_degrees[0],6,'The n=2 secancy coefficient has source degree 6');
      const definition=page.locator('#sl-results .sl-result-definition').first();
      const picker=definition.getByLabel('Formula representation');
      assert.equal(await picker.locator('option').count(),4);
      assert.equal(await picker.inputValue(),'0');
      assert.equal(await definition.locator('p.sar-formula').first().textContent(),recorded.formula);
      const sourceDetails=definition.locator('.sl-formula-raw');
      const originalSource=sourceDetails.locator('.sl-formula-source-text');
      assert.equal(await sourceDetails.evaluate(el=>el.open),false);
      await sourceDetails.locator('summary').click();
      assert.equal(await originalSource.textContent(),recorded.formula);
      const inspector=definition.locator('.sl-term-inspector');
      assert.equal(await inspector.evaluate(el=>el.open),false);
      assert.equal(await inspector.locator('tbody tr').count(),0,'Exact tables are constructed on demand');
      await inspector.locator('summary').click();
      await inspector.locator('tbody tr').first().waitFor({state:'attached',timeout:30000});
      assert.equal(await inspector.locator('tbody tr').count(),8);
      assert.deepEqual(await inspector.locator('thead th').allTextContents(),
        ['n','Source degree','Exact stored value']);
      assert.equal(await inspector.locator('tbody tr').first().locator('th').textContent(),String(recorded.offset));
      assert.deepEqual(await inspector.locator('tbody tr').first().locator('td').allTextContents(),
        [String(recorded.source_degrees[0]),recorded.terms[0]]);
      await inspector.getByRole('button',{name:'Next 8'}).click();
      assert.equal(await inspector.locator('tbody tr').first().locator('th').textContent(),String(recorded.offset+8));
      await inspector.getByRole('button',{name:'Previous 8'}).click();
      assert.equal(await inspector.locator('tbody tr').first().locator('th').textContent(),String(recorded.offset));
      await inspector.getByLabel('Go to stored n').fill(String(recorded.offset+20));
      await inspector.getByRole('button',{name:'Go',exact:true}).click();
      assert.equal(await inspector.locator('tbody tr').first().locator('th').textContent(),String(recorded.offset+16));
      assert.equal(await inspector.locator('tbody tr').last().locator('td').last().textContent(),recorded.terms[23]);
      assert.equal(await inspector.getByRole('button',{name:'Next 8'}).isDisabled(),true);
      const pendingWindow=page.waitForEvent('download');
      await inspector.getByRole('button',{name:'Export window CSV'}).click();
      const windowDownload=await pendingWindow;
      assert.equal(windowDownload.suggestedFilename(),
        `sequence-KFOR-P-03-02-${recorded.offset+16}-${recorded.offset+23}.csv`);
      const csvPath=path.join(output,`inspected-window-${width}.csv`);
      await windowDownload.saveAs(csvPath);
      const csvRows=fs.readFileSync(csvPath,'utf8').trim().split(/\r?\n/);
      assert.equal(csvRows.length,9);
      assert.equal(csvRows[0],'"record_id","stored_index","source_degree","exact_stored_value"');
      assert.equal(csvRows[1],
        `"KFOR-P-03-02","${recorded.offset+16}","${recorded.source_degrees[16]}","${recorded.terms[16]}"`);
      assert.equal(csvRows[8],
        `"KFOR-P-03-02","${recorded.offset+23}","${recorded.source_degrees[23]}","${recorded.terms[23]}"`);
      await picker.selectOption('1');
      assert.equal(await definition.locator('p.sar-formula').first().textContent(),recorded.formulas[1].expression);
      assert.equal(await originalSource.textContent(),recorded.formulas[1].expression);
      assert.equal(await inspector.evaluate(el=>el.open),true,'Changing representations preserves the exact value inspector');
      assert.equal(await inspector.locator('tbody tr').last().locator('td').last().textContent(),recorded.terms[23]);
      assert.equal(await definition.locator('.sl-definition-excerpt').textContent(),
        recorded.formulas[1].expression.replace(/\s+/g,' ').trim());
      assert.match(await definition.locator('.sl-variant-kind').textContent(),/finite sum · 2 of 4/);
      assert.equal((await definition.locator('.sl-variant-note').textContent()).trim(),recorded.formulas[1].note);
      assert.equal(await definition.locator('.sl-variant-source a').getAttribute('href'),recorded.formulas[1].source);

      await inspector.getByRole('button',{name:'Copy inspection link'}).click();
      await page.waitForFunction(()=>
        document.querySelector('#sl-results .sl-inspection-link-status')?.textContent.includes('copied')
      );
      const inspectionHref=await page.evaluate(()=>navigator.clipboard.readText());
      const inspectedUrl=new URL(inspectionHref);
      assert.equal(inspectedUrl.pathname.endsWith('/sequence-library.html'),true);
      assert.equal(inspectedUrl.searchParams.get('q'),'id:'+recorded.id);
      assert.equal(inspectedUrl.searchParams.get('sl-record'),recorded.id);
      assert.equal(inspectedUrl.searchParams.get('sl-formula'),'1');
      assert.equal(inspectedUrl.searchParams.get('sl-start'),String(recorded.offset+16));
      assert.equal(inspectedUrl.hash,'#sl-results');
      const recipient=await context.newPage();
      recipient.on('pageerror',error=>report.errors.push(error.message));
      await recipient.goto(inspectionHref);await ready(recipient);
      assert.equal(await recipient.locator('#sl-results>li').count(),1);
      const restoredDefinition=recipient.locator('#sl-results .sl-result-definition');
      const restoredInspector=restoredDefinition.locator('.sl-term-inspector');
      assert.equal(await restoredDefinition.evaluate(el=>el.open),true);
      assert.equal(await restoredDefinition.locator('.sl-variant-select').inputValue(),'1');
      assert.equal(await restoredDefinition.locator('p.sar-formula').first().textContent(),recorded.formulas[1].expression);
      assert.equal(await restoredInspector.evaluate(el=>el.open),true);
      await restoredInspector.locator('tbody tr').first().waitFor({state:'attached',timeout:30000});
      assert.equal(await restoredInspector.locator('tbody tr').first().locator('th').textContent(),String(recorded.offset+16));
      assert.equal(await restoredInspector.locator('tbody tr').first().locator('td').last().textContent(),recorded.terms[16]);
      await fit(recipient);
      if(width===1440){
        await recipient.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined}));
        await restoredInspector.getByRole('button',{name:'Copy inspection link'}).click();
        await restoredInspector.locator('.sl-inspection-link-fallback').waitFor({state:'visible',timeout:30000});
        assert.equal(await restoredInspector.locator('.sl-inspection-link-fallback input').inputValue(),inspectionHref,
          'Clipboard-disabled readers still receive the complete exact view link');
        const bad=new URL(inspectionHref);
        bad.searchParams.set('sl-formula','999');
        const invalid=await context.newPage();
        invalid.on('pageerror',error=>report.errors.push(error.message));
        await invalid.goto(bad.href);await ready(invalid);
        assert.equal(await invalid.locator('#sl-results .sl-variant-select').inputValue(),'0');
        assert.equal(await invalid.locator('#sl-results .sl-term-inspector').evaluate(el=>el.open),false,
          'Invalid formula positions must not restore another inspection view');
        await fit(invalid);await invalid.close();
      }
      await recipient.close();
      await page.selectOption('#site-math-display','plain');
      assert.equal(await definition.locator('p.sar-formula').first().isVisible(),true,
        'The original exact source must remain visible in plain-text mode, including notation fallbacks');
      await picker.selectOption('3');
      assert.equal(await definition.locator('p.sar-formula').first().textContent(),recorded.formulas[3].expression);
      assert.match(await definition.locator('.sl-variant-kind').textContent(),/hypergeometric · 4 of 4/);
      await picker.selectOption('0');
      assert.equal(await definition.locator('p.sar-formula').first().textContent(),recorded.formula);
      assert.equal(await originalSource.textContent(),recorded.formula);
      await page.selectOption('#site-math-display','typeset');
      await page.evaluate(async()=>{await window.KomorebiMath?.ready;});
      await fit(page);
      await page.goto(href('sequence-library.html?q=id%3AKFOR-TRI-P-03#library-search'));
      await ready(page);
      const trianglePanel=page.locator('#sl-results .sl-result-definition .sl-term-inspector');
      await trianglePanel.locator('summary').click();
      await trianglePanel.locator('tbody tr').first().waitFor({state:'attached',timeout:30000});
      assert.deepEqual(await trianglePanel.locator('thead th').allTextContents(),
        ['j','Row n','Column k','Source degree','Exact stored value']);
      assert.deepEqual(await trianglePanel.locator('tbody tr').nth(5).locator('th,td').allTextContents(),
        ['5','2','2','6','10'],'Flat triangle indices must retain row, column and Taylor degree');
      await fit(page);
      if(width===1440){
        await page.goto(href('sequence-library.html?q=id%3AKFOR-C-03-01-02-num#library-search'));
        await ready(page);
        const ratioPanel=page.locator('#sl-results .sl-result-definition .sl-term-inspector');
        await ratioPanel.locator('summary').click();
        await ratioPanel.locator('tbody tr').first().waitFor({state:'attached',timeout:30000});
        const rationalResponse=await page.evaluate(async()=>{
          const result=await fetch(new URL('assets/sequence-library-data.json',location.href));
          const data=await result.json();
          return data.entries.find(x=>x.id==='KFOR-C-03-01-02-num');
        });
        assert.deepEqual(await ratioPanel.locator('thead th').allTextContents(),
          ['n','Source degree','Exact stored value','Original rational value']);
        assert.deepEqual(await ratioPanel.locator('tbody tr').first().locator('td').allTextContents(),
          [String(rationalResponse.source_degrees[0]),rationalResponse.terms[0],rationalResponse.rational_terms[0]]);
        await fit(page);
      }
      await page.goto(href('sequence-library.html?q=id%3AKSEQ-000025#library-search'));
      await ready(page);
      assert.equal(await page.locator('#sl-results>li').count(),1);
      assert.equal(await page.locator('#sl-results .sl-result-more').first().evaluate(el=>el.open),true,
        'A precise record search retains direct access to secondary tools');
      assert.equal(await page.locator('#sl-results .sl-result-definition').first().evaluate(el=>el.open),true);
      assert.match(await page.locator('#sl-results .sl-result-definition summary').first().getAttribute('aria-label'),/Defining formula for/);
      await page.locator('#sl-results .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      await fit(page);
      await page.getByRole('button',{name:'Build a transfer',exact:true}).first().click();
      await page.locator('[data-transfer-ready=true]').waitFor({timeout:90000});
      assert.ok(page.url().includes('sequence-transfers.html'));
      assert.equal(await page.locator('#tr-source').inputValue(),'KSEQ-000025');
      assert.match(await page.locator('#tr-summary').textContent(),/coefficients verified exactly/);
      assert.equal(await page.locator('#sl-search,#sw-form,#sl-oeis-form').count(),0);
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#tr-result-nav a').count(),4);
      await page.locator('#tr-result-nav a[href="#tr-matrices"]').click();
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),true);
      await page.locator('#tr-matrices .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      await fit(page);
      await visit(page,'sequence-compare.html','compare');
      assert.equal(await page.locator('#sl-search,#tr-form,#sl-oeis-form').count(),0);
      assert.equal(await page.locator('#sw-add-form').isVisible(),true);
      await page.fill('#sw-record','KSEQ-000025');
      await page.getByRole('button',{name:'Add record',exact:true}).click();
      assert.equal(await page.locator('#sw-sources>li').count(),1);
      assert.equal(await page.locator('#sw-add-error').isVisible(),false);
      await page.fill('#sw-record','DOES-NOT-EXIST-123');
      await page.getByRole('button',{name:'Add record',exact:true}).click();
      assert.equal(await page.locator('#sw-add-error').isVisible(),true);
      await page.getByRole('button',{name:'Try Fibonacci + Lucas',exact:true}).click();
      assert.equal(await page.locator('#sw-sources>li').count(),2);
      assert.equal(await page.locator('#sw-share-top').isDisabled(),false);
      assert.equal(await page.locator('#sw-chart-labels').evaluate(el=>el.open),false,
        'Chart text settings should be optional rather than cluttering the main comparison');
      const defaultTicks=await page.locator('#sw-chart [data-y-tick]').allTextContents();
      assert.ok(defaultTicks.some(value=>value.startsWith('≈')),
        'Signed-log ticks should show approximate original-value magnitudes by default');
      assert.match(await page.locator('#sw-scale-note').textContent(),/signed logarithmic/);
      await page.locator('#sw-chart-labels>summary').click();
      for(const [field,value] of [['#sw-title-text','Fibonacci versus Lucas'],['#sw-x-title','Step in window'],['#sw-y-title','Approximate magnitude']]){
        await page.locator(field).fill(value);
        await page.locator(field).press('Tab');
      }
      await page.getByLabel('Legend label for KSEQ-000025').fill('Fibonacci');
      await page.getByLabel('Legend label for KSEQ-000025').press('Tab');
      await page.getByLabel('Legend label for KSEQ-000037').fill('Lucas');
      await page.getByLabel('Legend label for KSEQ-000037').press('Tab');
      await page.selectOption('#sw-legend-position','bottom');
      await page.waitForFunction(()=>
        document.querySelector('#sw-chart [data-chart-title]')?.textContent==='Fibonacci versus Lucas'
      );
      assert.equal(await page.locator('#sw-chart [data-x-axis-title]').textContent(),'Step in window');
      assert.equal(await page.locator('#sw-chart [data-y-axis-title]').textContent(),'Approximate magnitude');
      assert.deepEqual(await page.locator('#sw-chart [data-legend-label]').allTextContents(),['1. Fibonacci','2. Lucas']);
      await page.selectOption('#sw-legend','hide');
      assert.equal(await page.locator('#sw-chart [data-legend-label]').count(),0);
      await page.selectOption('#sw-legend','show');
      assert.equal(await page.locator('#sw-chart [data-legend-label]').count(),2);
      await page.selectOption('#sw-tick-mode','log');
      assert.ok((await page.locator('#sw-chart [data-y-tick]').allTextContents()).some(tick=>tick.includes('.')));
      assert.ok((await page.locator('#sw-chart [data-y-tick]').allTextContents()).every(tick=>!tick.includes('≈')));
      assert.match(await page.locator('#sw-scale-note').textContent(),/not sequence values/);
      await page.selectOption('#sw-tick-mode','magnitude');
      assert.ok((await page.locator('#sw-chart [data-y-tick]').allTextContents()).some(tick=>tick.startsWith('≈')));
      if(width===1440){
        const pending=page.waitForEvent('download');
        await page.locator('#sw-svg').click();
        const chartExport=await pending,exportPath=path.join(output,'comparison-custom-labels.svg');
        await chartExport.saveAs(exportPath);
        const exportedSVG=fs.readFileSync(exportPath,'utf8');
        for(const phrase of ['Fibonacci versus Lucas','Step in window','Approximate magnitude','1. Fibonacci','2. Lucas'])
          assert.ok(exportedSVG.includes(phrase),'Exported chart missing '+phrase);
      }
      await fit(page);
      await page.locator('#sw-provenance>summary').click();
      assert.equal(await page.locator('#sw-receipt-list li').count(),2);
      assert.equal(await page.locator('#sw-receipt-list code').count(),2);
      for(const value of await page.locator('#sw-receipt-list code').allTextContents())
        assert.match(value,/^[0-9a-f]{64}$/,'Each local exact source has a full SHA-256 receipt');
      await page.locator('#sw-share-top').click();
      await page.waitForFunction(()=>document.querySelector('#sw-status')?.textContent.includes('Comparison link copied'));
      const comparisonHref=await page.evaluate(()=>navigator.clipboard.readText());
      const comparisonURL=new URL(comparisonHref),receipt=JSON.parse(comparisonURL.searchParams.get('wb'));
      assert.equal(comparisonURL.pathname.endsWith('/sequence-compare.html'),true);
      assert.equal(receipt.schema,2);
      assert.equal(receipt.sources.length,2);
      assert.ok(receipt.sources.every(source=>/^[0-9a-f]{64}$/.test(source.sha256)));
      assert.ok(receipt.sources.every(source=>Number.isInteger(source.offset)&&source.count>0));
      assert.deepEqual(receipt.chartLabels,{
        title:'Fibonacci versus Lucas',xTitle:'Step in window',yTitle:'Approximate magnitude',
        legend:'show',legendPosition:'bottom',ticks:'magnitude',seriesLabels:['Fibonacci','Lucas']
      });
      const restored=await context.newPage();
      restored.on('pageerror',error=>report.errors.push(error.message));
      await restored.goto(comparisonHref);await ready(restored);
      assert.equal(await restored.locator('#sw-sources>li').count(),2);
      assert.match(await restored.locator('#sw-receipt-status').textContent(),/match the current local catalogue/);
      assert.equal(await restored.locator('#sw-chart svg').count(),1);
      assert.equal(await restored.locator('#sw-title-text').inputValue(),'Fibonacci versus Lucas');
      assert.equal(await restored.locator('#sw-x-title').inputValue(),'Step in window');
      assert.equal(await restored.locator('#sw-y-title').inputValue(),'Approximate magnitude');
      assert.equal(await restored.locator('#sw-legend-position').inputValue(),'bottom');
      assert.deepEqual(await restored.locator('#sw-chart [data-legend-label]').allTextContents(),['1. Fibonacci','2. Lucas']);
      assert.equal(await restored.locator('#sw-chart [data-chart-title]').textContent(),'Fibonacci versus Lucas');
      await restored.locator('#sw-provenance>summary').click();
      assert.equal(await restored.locator('#sw-receipt-list code').count(),2);
      await fit(restored);
      const changed=new URL(comparisonHref),changedData=JSON.parse(changed.searchParams.get('wb'));
      changedData.sources[0].sha256='0'.repeat(64);
      changed.searchParams.set('wb',JSON.stringify(changedData));
      const altered=await context.newPage();
      altered.on('pageerror',error=>report.errors.push(error.message));
      await altered.goto(changed.href);await ready(altered);
      assert.match(await altered.locator('#sw-error').textContent(),/no longer matches its exact stored data/);
      assert.equal(await altered.locator('#sw-error').isVisible(),true);
      assert.equal(await altered.locator('#sw-sources>li').count(),0,'Mismatched receipts must not silently show changed data');
      await fit(altered);await altered.close();
      if(width===1440){
        const oldLink=new URL(comparisonHref);
        const legacy=JSON.parse(oldLink.searchParams.get('wb'));
        legacy.schema=1;
        legacy.sources=legacy.sources.map(({type,id})=>({type,id}));
        oldLink.searchParams.set('wb',JSON.stringify(legacy));
        const older=await context.newPage();
        older.on('pageerror',error=>report.errors.push(error.message));
        await older.goto(oldLink.href);await ready(older);
        assert.equal(await older.locator('#sw-sources>li').count(),2);
        assert.match(await older.locator('#sw-receipt-status').textContent(),/Legacy comparison link/);
        await fit(older);await older.close();
      }
      await restored.close();
      await fit(page);
      await visit(page,'sequence-research.html','research');
      assert.equal(await page.locator('#sl-search,#tr-form,#sw-form,#sl-oeis-form').count(),0);
      assert.equal(await page.locator('#research-families .sl-topic-disclosure').evaluate(el=>el.open),true,
        'The dedicated research directory must show its family groups on arrival');
      assert.equal(await page.locator('#research-families .sl-research-group ul a:visible').count(),9);
      assert.equal(await page.locator('#research-families .sl-research-group').count(),4);
      assert.equal(await page.locator('#research-families .sl-research-group ul a').count(),9);
      assert.equal(await page.locator('#generalized').count(),1);
      assert.equal(await page.locator('.sl-research-choices article').count(),4);
      assert.equal(await page.locator('#connection-explorer,#sequence-identification,#modular-explorer,#notebook-explorer').count(),0);
      assert.match(await page.locator('#research-families').textContent(),/359 indexed research records/);
      await fit(page);
      await visit(page,'sequence-connections.html','connections');
      await page.locator('#cg-form').waitFor({timeout:30000});
      assert.equal(await page.locator('#cg-diagram-details').evaluate(el=>el.open),false);
      assert.equal(await page.locator('#cg-chart svg').count(),0,'Graph should not render a large default diagram');
      await page.locator('#cg-diagram-details>summary').click();
      await page.locator('#cg-chart svg').waitFor({timeout:30000});
      const graphLayout=await page.locator('#cg-chart svg').evaluate(svg=>({
        height:Number(svg.getAttribute('viewBox').trim().split(' ').at(-1)),
        neighbors:Math.max(0,svg.querySelectorAll('a').length-1)
      }));
      assert.equal(graphLayout.height,graphLayout.neighbors<=3?280:graphLayout.neighbors<=6?350:440);
      await page.locator('#cg-diagram-details>summary').click();
      await page.locator('#cg-chart svg').first().waitFor({state:'detached',timeout:30000});

      assert.equal(await page.locator('#research-graph>details').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#modular-explorer,#sequence-identification,#sl-search').count(),0);
      await fit(page);
      await visit(page,'sequence-identify.html','identify');
      await page.locator('#di-form').waitFor({timeout:30000});
      assert.equal(await page.locator('#identify>details').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#connection-explorer,#modular-explorer').count(),0);
      await fit(page);
      await visit(page,'sequence-modular.html','modular');
      await page.locator('#md-form').waitFor({timeout:30000});
      assert.equal(await page.locator('#modular-dynamics>details').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#md-current').isDisabled(),true);
      await page.locator('#modular-explorer[data-modular-ready=true]').waitFor({timeout:60000});
      assert.equal(await page.locator('#md-result>.sg-data-panel').count(),3);
      assert.equal(await page.locator('#md-result>.sg-data-panel table').count(),0,
        'Full exact tables should not be built before the reader opens them');
      assert.match(await page.locator('#md-result .sg-plot-note').textContent(),/retained residue samples/);
      assert.equal(await page.locator('#md-plot-controls').isVisible(),false);
      await page.locator('#md-result>.sg-data-panel').nth(1).locator('summary').click();
      await page.locator('#md-result>.sg-data-panel').nth(1).locator('tbody tr').first().waitFor({timeout:30000});
      assert.ok(await page.locator('#md-result>.sg-data-panel').nth(1).locator('tbody tr').count()>1);
      await page.locator('#md-result>.sg-data-panel').nth(2).locator('summary').click();
      await page.locator('#md-result>.sg-data-panel').nth(2).locator('tbody tr').first().waitFor({timeout:30000});
      await page.locator('#md-result>.sg-data-panel').first().locator('summary').click();
      await page.locator('#md-result>.sg-data-panel').first().locator('svg').waitFor({timeout:30000});
      assert.equal(await page.locator('#md-result>.sg-data-panel').first().locator('svg').count(),1);

      await page.locator('#md-result details>summary').first().click();
      await page.locator('#md-result .sr-modular-equation').waitFor({state:'attached',timeout:30000});
      await page.locator('#md-result .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      assert.match(await page.locator('#md-result [data-math-plain]').first().textContent(),/sum_\(j=1\)/);
      await page.fill('#md-modulus','50');
      await page.locator('#md-form button[type=submit]').click();
      await page.locator('#md-plot-controls:visible').waitFor({timeout:60000});
      assert.match(await page.locator('#md-plot-note').textContent(),/retains up to 256 residue samples and 64 initial state snapshots/);
      assert.equal(await page.locator('#md-plot-next').isDisabled(),false);
      await page.locator('#md-plot-next').click();
      assert.equal(await page.locator('#md-plot-start').inputValue(),'128');
      assert.match(await page.locator('#md-plot-note').textContent(),/Plot positions 128–255 of 256 retained residue samples/);
      await page.fill('#md-plot-start','64');
      await page.locator('#md-plot-start').dispatchEvent('change');
      assert.match(await page.locator('#md-plot-note').textContent(),/Plot positions 64–191 of 256 retained residue samples/);
      await page.locator('#md-result>.sg-data-panel').nth(1).locator('summary').click();
      await page.locator('#md-result>.sg-data-panel').nth(1).locator('tbody tr').first().waitFor({timeout:30000});
      assert.equal(await page.locator('#md-result>.sg-data-panel').nth(1).locator('tbody tr').count(),256);

      assert.equal(await page.locator('#connection-explorer,#sequence-identification').count(),0);
      await fit(page);
      await page.goto(href('sequence-research.html#research-graph'));await ready(page);
      assert.ok(page.url().includes('sequence-connections.html'),'Old Research graph link must redirect');
      await page.goto(href('sequence-research.html#identify'));await ready(page);
      assert.ok(page.url().includes('sequence-identify.html'),'Old Research identification link must redirect');
      await page.goto(href('sequence-research.html#modular-dynamics'));await ready(page);
      assert.ok(page.url().includes('sequence-modular.html'),'Old Research modular link must redirect');
      await visit(page,'sequence-oeis.html#oeis','oeis');
      assert.equal(await page.locator('#sl-search,#tr-form,#sw-form').count(),0);
      const oeisAssets=await page.evaluate(()=>performance.getEntriesByType('resource')
        .map(entry=>new URL(entry.name).pathname.split('/').at(-1)));
      assert.ok(oeisAssets.includes('sequence-oeis-meta.json'),
        'The standalone OEIS page needs its small snapshot identifier');
      assert.equal(oeisAssets.includes('sequence-library-data.json'),false,
        'The OEIS finder should not fetch the full integer catalogue before search');
      assert.equal(oeisAssets.includes('sequence-generalized-data.json'),false,
        'The OEIS finder should not fetch generalized family data before search');
      assert.match(await page.locator('[data-library]').getAttribute('data-oeis-snapshot'),/^[0-9a-f]{64}$/);
      assert.equal(await page.locator('#sl-oeis-query').isVisible(),true);
      assert.equal(await page.locator('#oeis>.sl-topic-disclosure').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#sl-oeis-results').count(),1);
      await fit(page);
      await page.goto(href('sequence-library.html#transfers'));
      await page.locator('[data-transfer-ready=true]').waitFor({timeout:90000});
      assert.ok(page.url().includes('sequence-transfers.html'),'Old transfer hash must redirect');
      await page.goto(href('sequence-library.html#research-families'));await ready(page);
      assert.ok(page.url().includes('sequence-research.html'),'Old research hash must redirect');
      await page.goto(href('sequence-library.html#research-graph'));await ready(page);
      assert.ok(page.url().includes('sequence-connections.html'),'Old Search graph hash must redirect');
      await page.goto(href('sequence-library.html?modular='));await ready(page);
      assert.equal(new URL(page.url()).pathname.endsWith('/sequence-modular.html'),true,'Parameterized modular link must reach the dedicated tool');
      assert.equal(new URL(page.url()).hash,'#modular-dynamics');
      await page.goto(href('sequence-research.html?identify='));await ready(page);
      assert.equal(new URL(page.url()).pathname.endsWith('/sequence-identify.html'),true,'Parameterized identification link must reach the dedicated tool');
      assert.equal(new URL(page.url()).hash,'#identify');
      await page.goto(href('sequence-library.html#oeis'));await ready(page);
      assert.ok(page.url().includes('sequence-oeis.html'),'Old OEIS hash must redirect');
      report.widths.push({width,eightPages:true,crossPageTransfer:true,standaloneComparison:true,researchDirectory:true,focusedResearchTools:true,legacyHashes:true,math:true,noOverflow:true});
      await context.close();
    }
    const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:900}});
    const page=await context.newPage();
    await page.goto(href('sequence-library.html'));
    assert.equal(await page.locator('.sl-page-tabs a').count(),5);
    assert.equal(await page.locator('#sl-search').isVisible(),false);
    assert.equal(await page.locator('#sl-count a[href="sequence-library/index.html"]').count(),1);
    await page.goto(href('sequence-library.html#transfers'));
    assert.equal(await page.locator('#transfers .sl-legacy-gateway').count(),0);
    assert.equal(await page.locator('#transfers a[href^="sequence-transfers.html"]').count(),1);
    await page.goto(href('sequence-transfers.html'));
    assert.equal(await page.locator('.sr-transfer-example').count(),1);
    await page.locator('.sr-transfer-example>summary').click();
    assert.equal(await page.locator('.sr-transfer-example').evaluate(el=>el.open),true);
    await page.goto(href('sequence-research.html'));
    assert.equal(await page.locator('#research-families .sl-topic-disclosure').evaluate(el=>el.open),true);
    assert.equal(await page.locator('#research-families .sl-research-group ul a').count(),9);
    assert.equal(await page.locator('.sl-research-choices article').count(),4);
    assert.equal(await page.locator('#research-graph a[href^="sequence-connections.html"]').count(),1);
    await page.goto(href('sequence-connections.html'));
    assert.equal(await page.locator('#research-graph>details').evaluate(el=>el.open),true);
    assert.match(await page.locator('#research-graph').textContent(),/Browse recorded relationships/);
    await page.goto(href('sequence-identify.html'));
    assert.equal(await page.locator('#identify>details').evaluate(el=>el.open),true);
    await page.goto(href('sequence-modular.html'));
    assert.equal(await page.locator('#modular-dynamics>details').evaluate(el=>el.open),true);
    await page.goto(href('sequence-compare.html'));
    assert.match(await page.locator('#comparison').textContent(),/Enable JavaScript to compare/);
    await page.goto(href('sequence-oeis.html'));
    assert.equal(await page.locator('#oeis a[href*="oeis"]').count()>0,true);
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
