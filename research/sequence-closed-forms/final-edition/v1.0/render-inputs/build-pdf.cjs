// Render the common paper HTML, retain a self-contained SVG edition, and print it.
const {chromium}=require('playwright');
const fs=require('node:fs');const path=require('node:path');const crypto=require('node:crypto');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const [url,output]=process.argv.slice(2);
if(!url||!output)throw Error('Usage: node tools/build_sequence_final_pdf.cjs URL OUTPUT_DIRECTORY');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_EXECUTABLE_PATH?{executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH}:{})});
 const errors=[];
 try{
  const page=await browser.newPage({viewport:{width:1000,height:1200}});
  page.on('pageerror',error=>errors.push(error.message));
  assert.ok((await page.goto(url)).ok());
  await page.evaluate(async()=>{await MathJax.startup.promise;await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
  assert.equal(await page.locator('mjx-merror, merror, [data-mml-node="merror"]').count(),0);
  const math=await page.locator('mjx-container').count();assert.ok(math>600,math);
  const audit=await page.evaluate(()=>{
   const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
   const missing=[...document.querySelectorAll('a[href^="#"]')].map(x=>x.getAttribute('href').slice(1)).filter(x=>!document.getElementById(x));
   return {duplicate_ids:ids.length-new Set(ids).size,missing_anchors:missing};
  });
  assert.equal(audit.duplicate_ids,0);assert.deepEqual(audit.missing_anchors,[]);assert.deepEqual(errors,[]);
  await page.evaluate(()=>{document.querySelectorAll('script').forEach(node=>node.remove());document.documentElement.dataset.mathRendered='true';});
  const html='<!DOCTYPE html>\n'+await page.locator('html').evaluate(node=>node.outerHTML);
  fs.writeFileSync(path.join(output,'PAPER.html'),html+'\n');
  await page.emulateMedia({media:'print'});
  const layout=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:document.documentElement.clientWidth}));
  assert.ok(layout.scroll<=layout.width+1,JSON.stringify(layout));
  await page.pdf({path:path.join(output,'PAPER.pdf'),format:'A4',preferCSSPageSize:true,printBackground:true,
   tagged:true,outline:true,displayHeaderFooter:true,headerTemplate:'<div></div>',
   footerTemplate:'<div style="font:8px Georgia,serif;width:100%;margin:0 20mm;color:#555;display:flex;justify-content:space-between"><span>Weighted central-binomial Hankel determinants · Final edition 1.0</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
   margin:{top:'22mm',bottom:'20mm',left:'20mm',right:'20mm'}});
  const offline=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:950}});
  const automaticRequests=[];
  await offline.route(/^https?:/,route=>{automaticRequests.push(route.request().url());return route.abort();});
  const staticPage=await offline.newPage();
  await staticPage.goto(pathToFileURL(path.resolve(output,'PAPER.html')).href);
  assert.equal(await staticPage.locator('script').count(),0);
  assert.equal(await staticPage.locator('mjx-container').count(),math);
  assert.equal(await staticPage.locator('merror, [data-mml-node="merror"]').count(),0);
  const staticSize=await staticPage.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
  assert.ok(staticSize.scroll<=staticSize.width+1,JSON.stringify(staticSize));
  await staticPage.evaluate(()=>document.documentElement.style.fontSize='200%');
  const enlargedSize=await staticPage.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
  assert.ok(enlargedSize.scroll<=enlargedSize.width+1,JSON.stringify(enlargedSize));
  assert.deepEqual(automaticRequests,[]);await offline.close();
  const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(output,file))).digest('hex');
  const report={status:'passed',browser:browser.version(),math_expressions:math,math_errors:0,
   self_contained_html_sha256:sha('PAPER.html'),pdf_sha256:sha('PAPER.pdf'),offline_automatic_requests:0,...audit};
  fs.writeFileSync(path.join(output,'render.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(error=>{console.error(error.stack||error);process.exit(1)});
