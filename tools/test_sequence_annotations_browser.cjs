const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createHash}=require('node:crypto');
const base=process.argv[2]||'http://127.0.0.1:8846/';
const output=process.argv[3]||'sequence-chart-annotations';
fs.mkdirSync(output,{recursive:true});
const href=relative=>new URL(relative,base).href;
const longTitles={
  title:'Fibonacci coefficients compared across the complete stored window and their exact growth',
  xTitle:'Recorded local sequence index across the selected window',
  yTitle:'Magnitude of each exact stored sequence coefficient'
};
const largestType={titleSize:'26',xTitleSize:'18',yTitleSize:'18',titleAlign:'left'};
const titleSelectors={title:'[data-chart-title]',xTitle:'[data-x-axis-title]',yTitle:'[data-y-axis-title]'};
const fontStyles={
  title:{Font:'serif',Weight:'bold',Style:'italic',Color:'#7c2d12',family:'Georgia',weight:'700',fill:'rgb(124, 45, 18)'},
  xTitle:{Font:'mono',Weight:'bold',Style:'normal',Color:'#075985',family:'ui-monospace',weight:'700',fill:'rgb(7, 89, 133)'},
  yTitle:{Font:'sans',Weight:'normal',Style:'italic',Color:'#6b21a8',family:'system-ui',weight:'400',fill:'rgb(107, 33, 168)'}
};
const textField=(prefix,key)=>'#'+prefix+'-'+(prefix==='sw'?{title:'title-text',xTitle:'x-title',yTitle:'y-title'}[key]:'chart-'+key);
const fontField=(prefix,key,setting)=>'#'+prefix+'-chart-'+key+setting;
async function openFontDetails(page,prefix,key){
  const panel=page.locator(fontField(prefix,key,'FontDetails'));
  if(!await panel.evaluate(node=>node.open))await panel.locator(':scope > summary').click();
}
async function customizeFonts(page,prefix){
  for(const [key,style]of Object.entries(fontStyles)){
    await openFontDetails(page,prefix,key);
    for(const setting of ['Font','Weight'])await page.selectOption(fontField(prefix,key,setting),style[setting]);
    await page.locator(fontField(prefix,key,'Style')).setChecked(style.Style==='italic');
    await page.selectOption(fontField(prefix,key,'ColorMode'),'custom');
    const color=page.locator(fontField(prefix,key,'Color'));
    await color.fill(style.Color.toUpperCase());await color.press('Tab');
    assert.equal(await color.inputValue(),style.Color,'Valid hex colors must normalize consistently');
    assert.equal(await page.inputValue(fontField(prefix,key,'ColorPicker')),style.Color,'Picker and precise hex input must stay synchronized');
  }
}
async function customizeTitles(page,prefix){
  for(const [key,value]of Object.entries(longTitles)){
    const field=page.locator(textField(prefix,key));await field.fill(value);await field.press('Tab');
  }
  for(const [key,value]of Object.entries(largestType))await page.selectOption('#'+prefix+'-chart-'+key,value);
  await customizeFonts(page,prefix);
}
async function titleGeometry(plot){
  const info=await plot.evaluate(async svg=>{
    await document.fonts.ready;
    const rect=node=>{const b=node.getBoundingClientRect();return {left:b.left,right:b.right,top:b.top,bottom:b.bottom,width:b.width,height:b.height};};
    const area=svg.querySelector('[data-plot-area]');
    if(!area)return {missingArea:true};
    const labels=[...svg.querySelectorAll('[data-chart-title],[data-x-axis-title],[data-y-axis-title],[data-legend-label]')]
      .filter(node=>getComputedStyle(node).display!=='none'&&getComputedStyle(node).visibility!=='hidden')
      .map(node=>({kind:node.hasAttribute('data-chart-title')?'title':node.hasAttribute('data-x-axis-title')?'xTitle':node.hasAttribute('data-y-axis-title')?'yTitle':'legend',text:node.textContent,...rect(node)}));
    return {svg:rect(svg),area:rect(area),plotHeight:area.getBBox().height,labels,
      ticks:[...svg.querySelectorAll('[data-y-tick]')].map(rect)};
  });
  assert.equal(info.missingArea,undefined,'Plot must expose its actual drawing bounds');
  assert.ok(info.plotHeight>=100,'Large labels must leave room for the plotted values');
  const separate=(a,b)=>a.right<=b.left+1||b.right<=a.left+1||a.bottom<=b.top+1||b.bottom<=a.top+1;
  for(const label of info.labels){
    assert.ok(label.width>0&&label.height>0,'Visible chart labels must have measurable text');
    assert.ok(label.left>=info.svg.left-1&&label.right<=info.svg.right+1&&label.top>=info.svg.top-1&&label.bottom<=info.svg.bottom+1,
      'Label lies outside its exported SVG: '+JSON.stringify({label,svg:info.svg}));
    assert.ok(separate(label,info.area),'Label overlaps plotted values: '+JSON.stringify(label));
    if(label.kind==='yTitle')for(const tick of info.ticks)assert.ok(separate(label,tick),'Vertical title overlaps tick labels');
  }
  for(let i=0;i<info.labels.length;i++)for(let j=i+1;j<info.labels.length;j++)
    assert.ok(separate(info.labels[i],info.labels[j]),'Chart annotations overlap: '+JSON.stringify([info.labels[i],info.labels[j]]));
}
async function checkTypography(plot,alignment='left'){
  for(const [key,expected]of Object.entries(longTitles)){
    const label=plot.locator(titleSelectors[key]);
    assert.equal(await label.getAttribute('aria-label'),expected);
    assert.equal((await label.textContent()).replace(/\s/g,''),expected.replace(/\s/g,''),'Visible title text must not be shortened');
    assert.equal(await label.evaluate(node=>parseFloat(getComputedStyle(node).fontSize)),key==='title'?26:18);
    const actual=await label.evaluate(node=>{const style=getComputedStyle(node);return {family:style.fontFamily,weight:style.fontWeight,style:style.fontStyle,fill:style.fill};});
    assert.ok(actual.family.includes(fontStyles[key].family),JSON.stringify(actual));
    assert.equal(actual.weight,fontStyles[key].weight);assert.equal(actual.style,fontStyles[key].Style);
    assert.equal(actual.fill,fontStyles[key].fill,'Each title keeps its own exact color');
  }
  assert.equal(await plot.locator('[data-chart-title]').evaluate(node=>getComputedStyle(node).textAnchor),{left:'start',center:'middle',right:'end'}[alignment]);
  await titleGeometry(plot);
}
async function hideTitles(page,prefix,plot){
  const hidden=new Set();
  for(const key of ['title','xTitle','yTitle']){
    await page.selectOption('#'+prefix+'-chart-'+key+'Display','hide');
    hidden.add(key);
    assert.equal(await plot.locator(titleSelectors[key]).isVisible(),false,'Individual title visibility must be honored');
    for(const other of Object.keys(titleSelectors))if(!hidden.has(other))
      assert.equal(await plot.locator(titleSelectors[other]).isVisible(),true,'Hiding one title must preserve the others');
    assert.ok(await plot.locator('title').first().textContent(),'The SVG must retain an accessible title');
  }
  await titleGeometry(plot);
}
async function showTitles(page,prefix){
  for(const key of ['title','xTitle','yTitle'])await page.selectOption('#'+prefix+'-chart-'+key+'Display','show');
}
async function checkRestoredControls(page,prefix){
  for(const [key,value]of Object.entries(largestType))assert.equal(await page.inputValue('#'+prefix+'-chart-'+key),value);
  for(const key of ['title','xTitle','yTitle'])assert.equal(await page.inputValue('#'+prefix+'-chart-'+key+'Display'),'show');
  for(const [key,style]of Object.entries(fontStyles)){
    for(const setting of ['Font','Weight','Color'])assert.equal(await page.inputValue(fontField(prefix,key,setting)),style[setting]);
    assert.equal(await page.locator(fontField(prefix,key,'Style')).isChecked(),style.Style==='italic');
    assert.equal(await page.inputValue(fontField(prefix,key,'ColorMode')),'custom');
  }
}
async function checkColorControls(page,prefix,plot){
  const color=page.locator(fontField(prefix,'title','Color'));
  await color.fill('#nope');await color.press('Tab');
  assert.equal(await color.getAttribute('aria-invalid'),'true');
  assert.equal(await plot.locator(titleSelectors.title).evaluate(node=>getComputedStyle(node).fill),fontStyles.title.fill,
    'An invalid color must leave the last valid plot unchanged');
  await color.fill('#ffffff');await color.press('Tab');
  assert.equal(await plot.locator(titleSelectors.title).evaluate(node=>getComputedStyle(node).fill),'rgb(255, 255, 255)',
    'A low-contrast explicit color must not be silently rewritten');
  assert.match(await page.locator(fontField(prefix,'title','ColorHint')).textContent(),/contrast|hard to read/i);
  await color.fill(fontStyles.title.Color);await color.press('Tab');
  assert.notEqual(await color.getAttribute('aria-invalid'),'true');
  await page.selectOption(fontField(prefix,'xTitle','ColorMode'),'auto');
  const appearance=page.locator('details.sp-options').filter({has:page.locator('#'+prefix+'-plot-theme')});
  if(!await appearance.evaluate(node=>node.open))await appearance.locator(':scope > summary').click();
  for(const [theme,fill]of [['night','rgb(245, 245, 245)'],['white','rgb(17, 17, 17)']]){
    await page.selectOption('#'+prefix+'-plot-theme',theme);
    assert.equal(await plot.locator(titleSelectors.xTitle).evaluate(node=>getComputedStyle(node).fill),fill,
      'Automatic text colors must follow the actual plot background');
    assert.equal(await plot.locator(titleSelectors.title).evaluate(node=>getComputedStyle(node).fill),fontStyles.title.fill,
      'Theme changes must preserve an explicit title color');
  }
  await page.selectOption(fontField(prefix,'xTitle','ColorMode'),'custom');
  await page.locator(fontField(prefix,'xTitle','Color')).fill(fontStyles.xTitle.Color);
  await page.locator(fontField(prefix,'xTitle','Color')).press('Tab');
  await checkTypography(plot);
}
async function checkReset(page,prefix,plot){
  const panel=page.locator('#'+prefix+'-chart-labels');
  if(!await panel.evaluate(node=>node.open))await panel.locator(':scope > summary').click();
  await openFontDetails(page,prefix,'xTitle');
  await page.locator(fontField(prefix,'xTitle','ResetFont')).click();
  assert.equal(await page.inputValue(textField(prefix,'xTitle')),longTitles.xTitle,'Reset font must preserve wording');
  assert.equal(await page.inputValue(fontField(prefix,'xTitle','Size')),'18','Reset font must preserve size');
  assert.equal(await page.inputValue(fontField(prefix,'xTitle','Display')),'show','Reset font must preserve visibility');
  assert.equal(await page.inputValue(fontField(prefix,'title','Font')),fontStyles.title.Font,'Reset font must preserve other titles');
  assert.equal(await page.inputValue(fontField(prefix,'xTitle','Font')),'sans');
  assert.equal(await page.inputValue(fontField(prefix,'xTitle','Weight')),'auto');
  assert.equal(await page.inputValue(fontField(prefix,'xTitle','ColorMode')),'auto');
  assert.equal(await page.locator(fontField(prefix,'xTitle','Style')).isChecked(),false);
  await openFontDetails(page,prefix,'title');
  await page.locator(fontField(prefix,'title','Color')).fill('#nope');
  await page.locator(fontField(prefix,'title','Color')).press('Tab');
  assert.equal(await page.locator(fontField(prefix,'title','Color')).getAttribute('aria-invalid'),'true');
  await panel.getByRole('button',{name:/Restore.*chart labels/}).click();
  for(const key of ['title','xTitle','yTitle']){
    assert.equal(await page.inputValue(textField(prefix,key)),'');
    assert.equal(await page.inputValue('#'+prefix+'-chart-'+key+'Display'),'show');
    assert.equal(await page.inputValue('#'+prefix+'-chart-'+key+'Size'),'auto');
    assert.equal(await plot.locator(titleSelectors[key]).isVisible(),true);
    assert.equal(await page.inputValue(fontField(prefix,key,'Font')),'sans');
    assert.equal(await page.inputValue(fontField(prefix,key,'Weight')),'auto');
    assert.equal(await page.inputValue(fontField(prefix,key,'ColorMode')),'auto');
    assert.equal(await page.locator(fontField(prefix,key,'Style')).isChecked(),false);
    assert.notEqual(await page.locator(fontField(prefix,key,'Color')).getAttribute('aria-invalid'),'true');
    assert.equal(await page.locator(fontField(prefix,key,'ColorError')).textContent(),'');
  }
  assert.equal(await page.inputValue('#'+prefix+'-chart-titleAlign'),'center');
  await titleGeometry(plot);
}
async function checkImageExports(page,context,prefix,plot,errors){
  const paths={};
  for(const format of ['svg','png']){
    const pending=page.waitForEvent('download');await page.locator('#'+prefix+'-'+format).click();
    const download=await pending;paths[format]=path.join(output,'comparison-styled.'+format);await download.saveAs(paths[format]);
  }
  const svg=fs.readFileSync(paths.svg,'utf8'),png=fs.readFileSync(paths.png);
  assert.equal(png.subarray(1,4).toString(),'PNG');
  const box=await plot.evaluate(node=>({width:node.viewBox.baseVal.width,height:node.viewBox.baseVal.height}));
  assert.equal(png.readUInt32BE(16),Math.round(box.width*2));assert.equal(png.readUInt32BE(20),Math.round(box.height*2));
  const exported=await context.newPage();exported.on('pageerror',err=>errors.push(err.message));
  await exported.setContent(svg);await checkTypography(exported.locator('svg'));
  const mismatch=await exported.evaluate(async ({svg,png})=>{
    const render=async source=>{const image=new Image();image.src=source;await image.decode();const canvas=document.createElement('canvas');canvas.width=image.naturalWidth;canvas.height=image.naturalHeight;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);return {image,canvas,ctx};};
    const raster=await render('data:image/png;base64,'+png),vector=new Image();
    vector.src='data:image/svg+xml;base64,'+svg;await vector.decode();
    const expected=document.createElement('canvas');expected.width=raster.canvas.width;expected.height=raster.canvas.height;
    const ctx=expected.getContext('2d');ctx.drawImage(vector,0,0,expected.width,expected.height);
    const a=ctx.getImageData(0,0,expected.width,expected.height).data,b=raster.ctx.getImageData(0,0,expected.width,expected.height).data;
    let different=0;for(let i=0;i<a.length;i+=4)if(Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2])+Math.abs(a[i+3]-b[i+3])>4)different++;
    return different/(a.length/4);
  },{svg:Buffer.from(svg).toString('base64'),png:png.toString('base64')});
  assert.ok(mismatch<0.001,'PNG must faithfully rasterize the styled SVG: different-pixel fraction '+mismatch);
  await exported.close();
}
async function previousCertificate(){
  const {createComparisonCertificate}=await import('../website/assets/sequence-comparison-certificate.mjs');
  const {localSource,customSource}=await import('../website/assets/sequence-workbench-core.mjs');
  const digest=data=>createHash('sha256').update(JSON.stringify(data),'utf8').digest('hex');
  const record={id:'KSEQ-TEST',title:'Exact reference',collection:'atlas',index_symbol:'n',offset:2,
    terms:['0','-1','9007199254740993','7'],url:'sequences/KSEQ-TEST.html'};
  record.record_sha256=digest([record.id,record.collection,record.offset,record.index_symbol,record.terms,null]);
  const chartLabels={title:'Saved finite comparison',xTitle:'Recorded index',yTitle:'Value',
    legend:'show',legendPosition:'bottom',legendStyle:'id',ticks:'scientific',seriesLabels:['Reference','Input']};
  const current=await createComparisonCertificate([localSource(record,'https://example.test/'),
    customSource({title:'Local unreviewed input',offset:2,terms:['0','-1','9007199254740993','8']})],{skip:1,count:3},{chartLabels});
  const {certificateSha256,...body}=current;body.presentation.chartLabels=chartLabels;
  const receipt=digest(body);
  assert.equal(receipt,'b35a31b3182b3e4cc9fdb43c19d51df2087c2551e7d3ab0c4f3070c944171f97','The legacy fixture must retain its previous-release digest');
  return {name:'previous-chart-certificate.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...body,certificateSha256:receipt}))};
}
async function fit(page){
  // Playwright can inspect geometry even when page JavaScript is disabled.
  // Waiting for requestAnimationFrame on such a page never settles.
  await page.locator('body').waitFor({state:'attached'});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1),true,'Unexpected plot page overflow: '+page.url());
}
(async()=>{
  const legacyFile=await previousCertificate();
  const browser=await chromium.launch({headless:true}),report={status:'running',widths:[],errors:[]};
  let forcedLink;
  try{
    for(const width of [1440,390,320]){
      const context=await browser.newContext({viewport:{width,height:940},permissions:['clipboard-read','clipboard-write']});
      const errors=[],page=await context.newPage();page.on('pageerror',err=>errors.push(err.message));
      await page.goto(href('sequence-explorer.html#explorer'));
      await page.locator('#sequence-atlas[data-interface-ready=true]').waitFor({timeout:90000});
      await page.locator('.sa-advanced>summary').click();
      await page.selectOption('#sa-sequence','KSEQ-000025');
      await page.selectOption('#sa-view','standard');
      await page.selectOption('#sa-scale','signed-log');
      const atlas=page.locator('#sa-plot svg');
      await atlas.waitFor();
      assert.equal(await page.locator('#sa-chart-labels').evaluate(el=>el.open),false);
      await page.locator('#sa-chart-labels>summary').click();
      await page.locator('#sa-chart-title').fill('Fibonacci exact profile');
      await page.locator('#sa-chart-title').press('Tab');
      await page.locator('#sa-chart-xTitle').fill('Recurrence step');
      await page.locator('#sa-chart-xTitle').press('Tab');
      await page.locator('#sa-chart-yTitle').fill('Signed approximate magnitude');
      await page.locator('#sa-chart-yTitle').press('Tab');
      await page.selectOption('#sa-chart-ticks','scientific');
      await page.selectOption('#sa-chart-legendStyle','id');
      assert.equal(await atlas.locator('[data-chart-title]').getAttribute('aria-label'),'Fibonacci exact profile');
      assert.equal(await atlas.locator('[data-x-axis-title]').getAttribute('aria-label'),'Recurrence step');
      assert.equal(await atlas.locator('[data-y-axis-title]').getAttribute('aria-label'),'Signed approximate magnitude');
      assert.ok((await atlas.locator('[data-y-tick]').allTextContents()).some(v=>v.includes('×10^')));
      assert.match(await page.locator('.sp-scale-explanation').textContent(),/scientific notation/);
      assert.match(await atlas.locator('[data-legend-label]').first().textContent(),/KSEQ-000025/);
      await customizeTitles(page,'sa');await checkTypography(atlas);await checkColorControls(page,'sa',atlas);
      await page.selectOption('#sa-chart-legendPosition','bottom');await checkTypography(atlas);
      await hideTitles(page,'sa',atlas);await showTitles(page,'sa');await checkTypography(atlas);
      await page.locator('#sa-share').click();
      const atlasLink=await page.evaluate(()=>navigator.clipboard.readText());
      assert.equal(new URL(atlasLink).searchParams.get('chart-title'),longTitles.title);
      assert.equal(new URL(atlasLink).searchParams.get('chart-ticks'),'scientific');
      const atlasRestored=await context.newPage();atlasRestored.on('pageerror',err=>errors.push(err.message));
      await atlasRestored.goto(atlasLink);
      await atlasRestored.locator('#sequence-atlas[data-interface-ready=true]').waitFor({timeout:90000});
      assert.equal(await atlasRestored.locator('#sa-chart-title').inputValue(),longTitles.title);
      assert.equal(await atlasRestored.locator('#sa-chart-ticks').inputValue(),'scientific');
      assert.equal(await atlasRestored.locator('#sa-chart-legendStyle').inputValue(),'id');
      await checkRestoredControls(atlasRestored,'sa');await checkTypography(atlasRestored.locator('#sa-plot svg'));
      // A newly selected comparison series must not inherit a prior record's legend alias.
      await atlasRestored.locator('#sa-chart-labels>summary').click();
      await atlasRestored.selectOption('#sa-compare','KSEQ-000037');
      assert.equal(await atlasRestored.locator('#sa-chart-labels .sp-chart-series input').count(),2);
      const seriesAlias=atlasRestored.locator('#sa-chart-labels .sp-chart-series input').nth(1);
      await seriesAlias.fill('Temporary Lucas alias');
      await seriesAlias.press('Tab');
      assert.match(await atlasRestored.locator('#sa-plot [data-legend-label="1"]').textContent(),/Temporary Lucas alias/);
      await atlasRestored.selectOption('#sa-compare','KSEQ-000001');
      assert.equal(await atlasRestored.locator('#sa-chart-labels .sp-chart-series input').count(),2);
      assert.equal(await atlasRestored.locator('#sa-chart-labels .sp-chart-series input').nth(1).inputValue(),'');
      assert.doesNotMatch(await atlasRestored.locator('#sa-plot [data-legend-label="1"]').textContent(),/Temporary Lucas alias/);
      await atlasRestored.selectOption('#sa-compare','');
      assert.equal(await atlasRestored.locator('#sa-chart-labels .sp-chart-series input').count(),1);
      await checkReset(atlasRestored,'sa',atlasRestored.locator('#sa-plot svg'));
      await fit(atlasRestored);await atlasRestored.close();
      await fit(page);

      await page.goto(href('sequence-archive/KOM067.html#plot'));
      await page.locator('[data-archive-ready=true]').waitFor({timeout:90000});
      await page.selectOption('#sar-view','raw');
      await page.locator('#sar-plot-form button[type=submit]').click();
      await page.selectOption('#sar-scale','signed-log');
      await page.locator('#sar-plot-form button[type=submit]').click();
      await page.locator('#sar-chart-labels>summary').click();
      await page.locator('#sar-chart-title').fill('Archived coefficient profile');
      await page.locator('#sar-chart-title').press('Tab');
      await page.selectOption('#sar-chart-legend','show');
      await page.selectOption('#sar-chart-legendStyle','id');
      await page.selectOption('#sar-chart-ticks','scientific');
      const archived=page.locator('#sar-plot svg');
      assert.equal(await archived.locator('[data-chart-title]').getAttribute('aria-label'),'Archived coefficient profile');
      assert.ok((await archived.locator('[data-y-tick]').allTextContents()).some(v=>v.includes('×10^')));
      assert.match(await archived.locator('[data-legend-label]').first().textContent(),/KOM067/);
      await customizeTitles(page,'sar');await checkTypography(archived);await checkColorControls(page,'sar',archived);
      await page.selectOption('#sar-chart-legendPosition','bottom');await checkTypography(archived);
      await hideTitles(page,'sar',archived);await showTitles(page,'sar');await checkTypography(archived);
      await page.locator('#sar-view-link').click();
      const archiveLink=await page.evaluate(()=>navigator.clipboard.readText());
      const aURL=new URL(archiveLink);
      assert.equal(aURL.searchParams.get('chart-title'),longTitles.title);
      assert.equal(aURL.searchParams.get('chart-legend-style'),'id');
      assert.equal(aURL.searchParams.get('chart-legend'),'show','Links must override the archive default of hiding the legend');
      const archiveRestored=await context.newPage();archiveRestored.on('pageerror',err=>errors.push(err.message));
      await archiveRestored.goto(archiveLink);
      await archiveRestored.locator('[data-archive-ready=true]').waitFor({timeout:90000});
      assert.equal(await archiveRestored.locator('#sar-chart-ticks').inputValue(),'scientific');
      assert.equal(await archiveRestored.locator('#sar-chart-title').inputValue(),longTitles.title);
      assert.match(await archiveRestored.locator('#sar-plot [data-legend-label]').textContent(),/KOM067/);
      await checkRestoredControls(archiveRestored,'sar');await checkTypography(archiveRestored.locator('#sar-plot svg'));
      await checkReset(archiveRestored,'sar',archiveRestored.locator('#sar-plot svg'));
      await fit(archiveRestored);await archiveRestored.close();
      if(width===1440){
        const download=page.waitForEvent('download');await page.locator('#sar-svg').click();
        const artifact=await download;const destination=path.join(output,'archive-chart-custom.svg');
        await artifact.saveAs(destination);const svg=fs.readFileSync(destination,'utf8');
        assert.match(svg,/KOM067/);
        const exported=await context.newPage();exported.on('pageerror',err=>errors.push(err.message));
        await exported.setContent(svg);await checkTypography(exported.locator('svg'));
        await exported.close();
      }
      await fit(page);

      await page.goto(href('sequence-compare.html#comparison'));
      await page.locator('[data-library-ready=true]').waitFor({timeout:90000});
      await page.locator('#sw-example').click();
      assert.equal(await page.locator('#sw-chart [data-chart-title]').getAttribute('aria-label'),'Original terms · Fibonacci vs Lucas',
        'Uncustomized comparison charts should identify their plotted sequences');
      await page.locator('#sw-chart-labels>summary').click();
      await page.selectOption('#sw-legend-style','id');
      assert.match(await page.locator('#sw-chart [data-legend-label]').first().textContent(),/KSEQ-000025/);
      await page.selectOption('#sw-legend-style','full');
      assert.match(await page.locator('#sw-chart [data-legend-label]').first().textContent(),/KSEQ-000025/);
      await page.selectOption('#sw-tick-mode','scientific');
      assert.ok((await page.locator('#sw-chart [data-y-tick]').allTextContents()).some(v=>v.includes('×10^')));
      const compared=page.locator('#sw-chart svg');
      await customizeTitles(page,'sw');await checkTypography(compared);await checkColorControls(page,'sw',compared);
      await page.selectOption('#sw-legend-position','bottom');await checkTypography(compared);
      await page.selectOption('#sw-chart-xTitleSize','12');
      assert.equal(await compared.locator('[data-x-axis-title]').evaluate(node=>parseFloat(getComputedStyle(node).fontSize)),12);
      assert.equal(await compared.locator('[data-y-axis-title]').evaluate(node=>parseFloat(getComputedStyle(node).fontSize)),18);
      await page.selectOption('#sw-chart-xTitleSize','18');
      await page.selectOption('#sw-chart-titleAlign','right');await checkTypography(compared,'right');
      await page.selectOption('#sw-chart-titleAlign','left');
      await hideTitles(page,'sw',compared);
      if(width===1440){
        const download=page.waitForEvent('download');await page.locator('#sw-svg').click();
        const artifact=await download,destination=path.join(output,'comparison-hidden-titles.svg');
        await artifact.saveAs(destination);
        const exported=await context.newPage();exported.on('pageerror',err=>errors.push(err.message));
        await exported.setContent(fs.readFileSync(destination,'utf8'));
        for(const selector of Object.values(titleSelectors))assert.equal(await exported.locator(selector).isVisible(),false);
        assert.equal(await exported.locator('svg>title').textContent(),longTitles.title);
        await titleGeometry(exported.locator('svg'));await exported.close();
      }
      await page.locator('#sw-share').click();
      const hiddenLink=await page.evaluate(()=>navigator.clipboard.readText());
      const comparisonRestored=await context.newPage();comparisonRestored.on('pageerror',err=>errors.push(err.message));
      await comparisonRestored.goto(hiddenLink);
      await comparisonRestored.locator('[data-library-ready=true]').waitFor({timeout:90000});
      for(const key of ['title','xTitle','yTitle']){
        assert.equal(await comparisonRestored.inputValue('#sw-chart-'+key+'Display'),'hide');
        assert.equal(await comparisonRestored.locator('#sw-chart '+titleSelectors[key]).isVisible(),false);
        assert.equal(await comparisonRestored.inputValue(textField('sw',key)),longTitles[key]);
      }
      await comparisonRestored.locator('#sw-chart-labels>summary').click();
      await showTitles(comparisonRestored,'sw');await checkRestoredControls(comparisonRestored,'sw');
      await checkTypography(comparisonRestored.locator('#sw-chart svg'));
      await checkReset(comparisonRestored,'sw',comparisonRestored.locator('#sw-chart svg'));
      await fit(comparisonRestored);await comparisonRestored.close();
      await showTitles(page,'sw');await checkTypography(compared);
      if(width===1440){
        await checkImageExports(page,context,'sw',compared,errors);
        await page.locator('#sw-share').click();forcedLink=await page.evaluate(()=>navigator.clipboard.readText());
      }
      await page.locator('#sw-verify-certificate>summary').click();
      await page.locator('#sw-verify-file').setInputFiles(legacyFile);
      await page.locator('#sw-verify-submit').click();
      await page.locator('#sw-verify-output').waitFor({state:'visible'});
      assert.match(await page.locator('#sw-verify-summary').textContent(),/2 source prefixes, 6 exact displayed rows, 3 compared positions/);
      assert.equal(await page.locator('#sw-verify-receipt').textContent(),'b35a31b3182b3e4cc9fdb43c19d51df2087c2551e7d3ab0c4f3070c944171f97');
      await checkTypography(compared);
      await fit(page);
      report.widths.push({width,atlasShare:true,archiveShare:true,comparisonShare:true,scientificTicks:true,compactLegends:true,
        fullTitleWrapping:true,titleTypography:true,independentVisibility:true,titleGeometry:true,restoredDefaults:true,
        independentFontStyles:true,preciseColors:true,invalidColorRecovery:true,automaticThemeColors:true,
        perTitleFontReset:true,legacyCertificate:true,noOverflow:true,errors});
      assert.deepEqual(errors,[]);
      await context.close();
    }
    const forced=await browser.newContext({viewport:{width:320,height:940},forcedColors:'active'});
    const forcedPage=await forced.newPage();await forcedPage.goto(forcedLink);
    await forcedPage.locator('[data-library-ready=true]').waitFor({timeout:90000});
    for(const [key,selector]of Object.entries(titleSelectors)){
      const label=forcedPage.locator('#sw-chart '+selector);
      const actual=await label.evaluate(node=>({inline:node.style.fill,family:getComputedStyle(node).fontFamily,style:getComputedStyle(node).fontStyle}));
      assert.equal(actual.inline.toLowerCase(),'canvastext','System high-contrast text colors must override explicit colors');
      assert.ok(actual.family.includes(fontStyles[key].family));assert.equal(actual.style,fontStyles[key].Style);
      assert.equal(await label.getAttribute('data-chart-text-color'),fontStyles[key].Color,'System colors must not erase saved custom choices');
    }
    await fit(forcedPage);await forced.close();report.forcedColors=true;report.styledSVGAndPNG=true;
    const context=await browser.newContext({viewport:{width:320,height:940},javaScriptEnabled:false});
    const noJS=await context.newPage();await noJS.goto(href('sequence-archive/KOM067.html'));
    assert.ok(await noJS.locator('#exact-data table tbody tr').count()>0,'Exact archive table must work without JavaScript');
    await fit(noJS);await context.close();
    report.noJavaScript=true;report.status='passed';console.log(JSON.stringify(report));
  }finally{fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
