const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8837/',out=process.argv[3]||'sequence-readability-browser';fs.mkdirSync(out,{recursive:true});
async function fits(p){await p.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),'horizontal page overflow');}
async function contrast(p){
 const result=await p.evaluate(()=>{
  const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number),luminance=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0),ratio=(a,b)=>{const x=luminance(a),y=luminance(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
  const failures=[];let checked=0,min=21;
  for(const el of document.querySelectorAll('.sar *, .sequence-atlas *')){
   if(el.namespaceURI!=='http://www.w3.org/1999/xhtml'||!el.getClientRects().length||!Array.from(el.childNodes).some(n=>n.nodeType===3&&n.textContent.trim()))continue;
   const style=getComputedStyle(el);if(style.visibility==='hidden')continue;let bg=[255,255,255];const layers=[];
   for(let ancestor=el;ancestor;ancestor=ancestor.parentElement)layers.push(rgb(getComputedStyle(ancestor).backgroundColor));
   for(const color of layers.reverse()){const alpha=color[3]??1;bg=bg.map((v,i)=>alpha*(color[i]||0)+(1-alpha)*v);}
   const value=ratio(rgb(style.color),bg);min=Math.min(min,value);checked++;if(value<4.5)failures.push({tag:el.tagName,id:el.id,class:el.className,text:el.textContent.trim().slice(0,60),color:style.color,bg,ratio:value});
  }
  for(const plot of document.querySelectorAll('#sw-chart svg,#sar-plot svg,#sa-plot svg')){
   if(!plot.getClientRects().length)continue;const bg=rgb(getComputedStyle(plot.querySelector('rect[width][height]')).fill);
   for(const text of plot.querySelectorAll('text')){const value=ratio(rgb(getComputedStyle(text).fill),bg);min=Math.min(min,value);checked++;if(value<4.5)failures.push({tag:'SVG text',text:text.textContent,ratio:value});}
  }
  return {checked,min,failures};
 });assert.deepEqual(result.failures,[],JSON.stringify(result.failures));assert.ok(result.checked>10);return {checked:result.checked,minimum:result.min};
}
async function query(p,value){await p.fill('#sl-query',value);await p.locator('#sl-search button[type=submit]').click();}
(async()=>{
 const b=await chromium.launch({channel:'msedge',headless:true}),report={widths:[],errors:[]};
 for(const width of [1440,390,320]){
  const c=await b.newContext({viewport:{width,height:1100},colorScheme:'dark',isMobile:width<500,hasTouch:width<500}),p=await c.newPage();p.on('pageerror',e=>report.errors.push(e.message));
  await p.goto(new URL('sequence-library.html',base).href);await p.locator('[data-library-ready=true]').waitFor();assert.equal(await p.inputValue('#sq-page-theme'),'light');assert.equal(await p.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(255, 255, 255)');await fits(p);const light=await contrast(p);
  await p.locator('#sl-research').click();assert.match(await p.locator('#sl-count').textContent(),/112 matching/);await query(p,'tag:research-derived n:3 k:02');assert.equal(await p.locator('#sl-results>li').count(),1);assert.match(await p.locator('#sl-results h3').textContent(),/k=2/);await p.locator('#sl-results h3 a').click();await p.locator('[data-library-ready=true]').waitFor();assert.equal(await p.locator('#exact-data tbody tr').first().locator('th').textContent(),'2');assert.deepEqual(await p.locator('#exact-data tbody tr').first().locator('td').allTextContents(),['6','10']);assert.equal(await p.locator('#exact-data tbody tr').last().locator('th').textContent(),'25');await fits(p);await contrast(p);
  const pending=p.waitForEvent('download');await p.locator('#exact-data a[download]').first().click();const d=await pending;await d.saveAs(path.join(out,`parameter-${width}.csv`));assert.match(fs.readFileSync(path.join(out,`parameter-${width}.csv`),'utf8'),/^n,a\(n\)\n2,10\n3,756\n/);
  await p.selectOption('#sq-page-theme','dark');assert.equal(await p.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(17, 24, 39)');const dark=await contrast(p);await p.reload();await p.locator('[data-library-ready=true]').waitFor();assert.equal(await p.inputValue('#sq-page-theme'),'dark');await p.getByRole('button',{name:'High contrast light plot',exact:true}).click();assert.equal(await p.locator('#sar-plot svg>rect').first().evaluate(el=>getComputedStyle(el).fill),'rgb(255, 255, 255)');await p.getByRole('button',{name:'High contrast dark plot',exact:true}).click();assert.equal(await p.locator('#sar-plot svg>rect').first().evaluate(el=>getComputedStyle(el).fill),'rgb(17, 24, 39)');await fits(p);await contrast(p);await p.locator('#sar-plot').screenshot({path:path.join(out,`parameter-dark-${width}.png`)});
  await p.selectOption('#sq-page-theme','light');await p.goto(new URL('sequence-families/KFOR-HC-04.html',base).href);await p.locator('[data-library-ready=true]').waitFor();assert.deepEqual(await p.locator('#exact-data tbody tr').first().locator('td').allTextContents(),['4','5']);await contrast(p);
  await p.goto(new URL('sequence-families/KFOR-H-02.html',base).href);await p.locator('[data-library-ready=true]').waitFor();assert.deepEqual(await p.locator('#exact-data tbody tr td:last-child').allTextContents().then(x=>x.slice(0,4)),['1','-6','144','-7536']);await contrast(p);
  await p.goto(new URL('sequence-archive/KOM085.html',base).href);await p.locator('#sq-page-theme').waitFor();await contrast(p);await p.selectOption('#sq-page-theme','dark');await contrast(p);await p.selectOption('#sq-page-theme','light');
  await p.goto(new URL('sequences.html',base).href);await p.locator('#sa-query').waitFor();await fits(p);await contrast(p);
  await p.goto(new URL('sequence-library.html',base).href);await p.locator('[data-library-ready=true]').waitFor();await p.locator('#sw-example').click();await fits(p);await contrast(p);await p.locator('#sw-chart').screenshot({path:path.join(out,`comparison-${width}.png`)});await p.screenshot({path:path.join(out,`library-${width}.png`),fullPage:false});report.widths.push({width,systemDarkDefaultsToLight:true,light,dark,researchSearch:true,actualOffsets:true,csv:true,pagePreference:true,plotPresets:true});await c.close();
 }
 const nojs=await b.newContext({javaScriptEnabled:false,viewport:{width:320,height:1000},colorScheme:'dark'}),n=await nojs.newPage();await n.goto(new URL('sequence-library/index.html',base).href);assert.equal(await n.locator('tbody tr').count(),2023);assert.equal(await n.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(255, 255, 255)');await n.goto(new URL('sequence-families/KFOR-P-03-02.html',base).href);assert.equal(await n.locator('#n-2 td').last().textContent(),'10');assert.equal(await n.locator('#exact-data tbody tr').count(),24);assert.ok(await n.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1));await nojs.close();report.noJavaScript=true;
 const forced=await b.newContext({viewport:{width:320,height:1000},forcedColors:'active'}),f=await forced.newPage();await f.goto(new URL('sequence-library.html',base).href);await f.locator('[data-library-ready=true]').waitFor();await f.selectOption('#sq-page-theme','dark');await f.addStyleTag({content:'html{font-size:200%!important}'});await fits(f);await contrast(f);await forced.close();report.enlargedTextForcedColors=true;
 assert.deepEqual(report.errors,[]);fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));await b.close();
})().catch(e=>{console.error(e);process.exit(1);});
