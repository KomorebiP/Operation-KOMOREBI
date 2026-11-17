const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'sequence-transfer-browser';
fs.mkdirSync(output,{recursive:true});

async function saveDownload(page,label,file){
  const pending=page.waitForEvent('download');
  await page.getByRole('button',{name:label,exact:true}).click();
  const item=await pending;
  const destination=path.join(output,file);
  await item.saveAs(destination);
  return fs.readFileSync(destination,'utf8');
}
async function run(){
  const browser=await chromium.launch({headless:true});
  const report={status:'passed',widths:[],noJavaScript:false};
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940},permissions:['clipboard-read','clipboard-write']});
      const page=await context.newPage();
      const errors=[];
      page.on('pageerror',error=>errors.push(error.message));
      await page.goto(new URL('sequence-library.html#transfers',base).href);
      await page.locator('[data-transfer-ready=true]').waitFor({timeout:90000});
      assert.match(await page.locator('#transfers h2').textContent(),/Transfer between sequences/);
      assert.equal(await page.locator('.sr-transfer-overview>div').count(),2);
      assert.equal(await page.locator('#tr-certificate .sr-transfer-fact').count(),3);
      assert.match(await page.locator('#tr-summary').textContent(),/12 coefficients verified exactly/);
      assert.match(await page.locator('#tr-window-help').textContent(),/Source anchor/);
      assert.match(await page.locator('#tr-certificate').textContent(),/H · K = 1/);
      assert.equal(await page.locator('.sr-transfer-algebra [data-math-latex]').count(),4);
      await page.locator('#tr-certificate .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      assert.equal(await page.locator('#tr-certificate .math-pair').count(),3);
      await page.locator('#site-math-display').selectOption('plain');
      assert.equal(await page.locator('#tr-certificate [data-math-plain]').first().isVisible(),true);
      await page.locator('#site-math-display').selectOption('typeset');
      assert.equal(await page.locator('#tr-certificate [data-math-tex]').first().isVisible(),true);
      assert.equal(await page.locator('#tr-result table tbody tr').first().count(),1);
      assert.equal(await page.locator('#tr-matrices').evaluate(el=>el.open),true);
      assert.equal(await page.locator('#tr-matrix-size').inputValue(),'4');
      await page.locator('#tr-matrices .sr-matrices .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      assert.match(await page.locator('#tr-matrices .sr-matrices [data-math-plain]').first().textContent(),/53, -1, 2, 1/);
      assert.equal(await page.locator('#tr-matrices .sr-matrices table').first().locator('tbody tr').count(),8);
      await page.selectOption('#tr-matrix-size','8');
      await page.locator('#tr-matrices .sr-matrices .math-pair[data-math-pair-ready=true]').first().waitFor({timeout:30000});
      assert.match(await page.locator('#tr-matrices .sr-matrices [data-math-plain]').first().textContent(),/53, -1, 2, 1/);
      assert.equal(await page.locator('#tr-matrices .sr-matrices mjx-container').count(),2);
      assert.equal(await page.locator('#tr-matrices [data-mml-node=merror],#tr-matrices mjx-merror').count(),0);
      await page.getByRole('button',{name:'Copy displayed matrices as LaTeX',exact:true}).click();
      assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).includes("L(H)=\\begin{pmatrix}"));
      assert.ok((await page.evaluate(()=>navigator.clipboard.readText())).includes("L_{8}(K)L_{8}(H)=I_{8}"));
      await page.selectOption('#site-math-display','plain');
      assert.equal(await page.locator('#tr-matrices .sr-matrices [data-math-plain]').first().isVisible(),true);
      await page.selectOption('#site-math-display','typeset');
      await page.selectOption('#tr-matrix-size','4');
      await page.locator('#tr-convolution-witness summary').click();
      assert.match(await page.locator('#tr-convolution-witness').textContent(),/At tail position 2/);
      const certificate=JSON.parse(await saveDownload(page,'Download certificate JSON','transfer-'+width+'.json'));
      assert.equal(certificate.schema,1);
      assert.equal(certificate.verified,true);
      assert.equal(certificate.coefficients,12);
      assert.deepEqual(certificate.certificate_conditions,['H*A=B','K*B=A','H*K=1']);
      assert.equal(certificate.rows[0].kernel,'1');
      assert.equal(certificate.rows[0].inverse,'1');
      await page.getByRole('button',{name:'Check identity transfer',exact:true}).click();
      assert.equal(await page.locator('#tr-error').isVisible(),false);
      assert.match(await page.locator('#tr-kernel-preview .sr-transfer-values').first().textContent(),/^1, 0, 0/);
      await page.getByRole('button',{name:'Fibonacci to Euler',exact:true}).click();
      assert.match(await page.locator('#tr-indices').textContent(),/Original index shift: -1/);
      await page.fill('#tr-count','999');
      await page.getByRole('button',{name:'Build exact transfer',exact:true}).click();
      assert.equal(await page.locator('#tr-error').isVisible(),true);
      assert.match(await page.locator('#tr-error').textContent(),/Choose 1/);
      await page.fill('#tr-count','8');
      await page.getByRole('button',{name:'Build exact transfer',exact:true}).click();
      assert.equal(await page.locator('#tr-error').isVisible(),false);
      assert.match(await page.locator('#tr-summary').textContent(),/8 coefficients verified exactly/);
      await page.fill('#tr-count','1');
      await page.getByRole('button',{name:'Build exact transfer',exact:true}).click();
      assert.equal(await page.locator('#tr-matrix-size').inputValue(),'1');
      assert.equal(await page.locator('#tr-matrices .sr-matrices table').first().locator('tbody tr').count(),1);
      assert.equal(await page.locator('#tr-error').isVisible(),false);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true);
      assert.deepEqual(errors,[]);
      report.widths.push({width,exactCertificate:true,presets:true,validation:true,noOverflow:true});
      await context.close();
    }
    const staticContext=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:900}});
    const page=await staticContext.newPage();
    await page.goto(new URL('sequence-library.html#transfers',base).href);
    assert.match(await page.locator('.sr-transfer-example').textContent(),/Euler values to shifted Fibonacci values/);
    assert.match(await page.locator('.sr-transfer-overview').textContent(),/formal division over the rationals/);
    assert.equal(await page.locator('.sr-transfer-static-matrices [data-math-latex]').count(),2);
    assert.match(await page.locator('.sr-transfer-static-matrices').textContent(),/53,-1,2,1/);
    assert.match(await page.locator('.sr-transfer-static-matrices').textContent(),/-65,5,-2,1/);
    assert.equal(await page.locator('#tr-form').count(),0);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true);
    report.noJavaScript=true;
    await staticContext.close();
  }finally{
    await browser.close();
  }
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
}
run().catch(error=>{console.error(error);process.exitCode=1;});
