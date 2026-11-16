// Syntax coverage of each distinct formula layout, including its first/last parameter instance.
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url'),assert=require('node:assert/strict');
const base=process.argv[2]||'http://127.0.0.1:8840/',out=process.argv[3]||'sequence-typesetting.json';
(async()=>{
 const {formulaLatex}=await import(pathToFileURL(path.resolve('website/assets/math-display.mjs')).href);
 const data=await(await fetch(new URL('assets/sequence-library-data.json',base))).json(),shapes=new Map(),literal=[];let supported=0,total=0;
 for(const entry of data.entries)for(const formula of entry.formulas){
  total++;const tex=formulaLatex(formula.expression);if(!tex){literal.push({id:entry.id,title:formula.title});continue;}supported++;
  const shape=tex.replace(/\d+/g,'#'),item={id:entry.id,title:formula.title,tex};if(!shapes.has(shape))shapes.set(shape,{first:item,last:item});else shapes.get(shape).last=item;
 }
 const samples=[...shapes.values()].flatMap(({first,last})=>first.id===last.id&&first.tex===last.tex?[first]:[first,last]);
 const browser=await chromium.launch({channel:'msedge',headless:true}),page=await browser.newPage();await page.goto(new URL('sequence-library.html?q=id:KSEQ-000025',base).href);await page.locator('[data-library-ready=true]').waitFor();await page.evaluate(()=>window.KomorebiMath.ready);
 const failures=await page.evaluate(async samples=>{const bad=[];for(const item of samples){try{const result=await MathJax.tex2svgPromise(item.tex,{display:true});const error=result.querySelector('[data-mml-node="merror"],[data-mjx-error],mjx-merror');if(error)bad.push({id:item.id,title:item.title,error:error.textContent});}catch(error){bad.push({id:item.id,title:item.title,error:error.message});}}return bad;},samples);
 await browser.close();const report={status:failures.length?'failed':'passed',formula_representations:total,supported_transcriptions:supported,literal_source_representations:literal.length,structural_layouts:shapes.size,compiled_samples:samples.length,failures,literal_sources:literal,renderer_sha256:crypto.createHash('sha256').update(fs.readFileSync('website/assets/math-display.mjs')).digest('hex'),scope:'Syntax and presentation checks, not a proof of formula identities. Unrecognized source notation remains literal.'};
 fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,literal_sources:undefined}));assert.deepEqual(failures,[]);
})().catch(error=>{console.error(error);process.exit(1);});
