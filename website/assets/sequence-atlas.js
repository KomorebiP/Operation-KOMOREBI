import './sequence-reading-theme.mjs';
import {generate,parseTerms,rowsFor,candidatePeriod} from './sequence-atlas-core.mjs';
import {searchEntries,suggestions,searchLink} from './sequence-atlas-search.mjs';
import {readSaved,writeSaved,updateSaveButtons} from './sequence-atlas-saved.mjs';
import {discover,analyzeInput,operationLabel,OPERATIONS} from './sequence-atlas-discovery.mjs';
import {setupInterface,workspaceForURL} from './sequence-atlas-interface.mjs';
import {setupDirectory} from './sequence-atlas-directory.mjs';
import {PLOT_DEFAULTS,plotColors,plotHeight,showIndexLabel,mergePlotLabels,mountPlotOptions,exportPlot,plotTheme,finishPlotTheme} from './sequence-plot-options.mjs';
import {mountSinglePlotLabels} from './sequence-chart-labels.mjs';
import {comparisonYAxisTick,comparisonLegendLabel,wrapLegendLabel} from './sequence-comparison-chart.mjs';

const $=id=>document.getElementById('sa-'+id);
const ids=['sequence','compare','view','transform','scale','marks','start','count','modulus','color'];
const defaults={sequence:'KSEQ-000007',compare:'',view:'mod',transform:'raw',scale:'linear',marks:'points',start:0,count:32,modulus:7,color:'series'};
const svgNS='http://www.w3.org/2000/svg';
const element=(tag,attrs={},text='')=>{const e=document.createElementNS(svgNS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text)e.textContent=text;return e;};
let data,entries,state={...defaults},timer=null,lastRows=[],plot,saved=new Set(),resultLimit=6,lastResults=[],pointIndex=0,statusTimer=null,searchErrorTimer=null,lastCustomTerms='',minimumWindow=2;
let showPanel=()=>{};
const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)};
const searchOptions=()=>({filter:$('filter').value,topic:$('topic').value,match:$('match').value,sort:$('sort').value,saved:[...saved]});
const optionLabel=(id,value)=>[...$(id).options].find(o=>o.value===value)?.textContent||value;
const briefValue=value=>{if(value.length<=60)return value;if(value.includes('/'))return value.split('/').map(briefValue).join(' divided by ');return value.slice(0,14)+'…'+value.slice(-8)+` (${value.replace(/[-+]/g,'').length} digits)`;};
let appearance={...PLOT_DEFAULTS},appearanceControls,chartLabelControls;
const stopAnimation=()=>{const running=timer!==null;clearInterval(timer);timer=null;$('animate').textContent='Animate modulus';$('animate').setAttribute('aria-pressed','false');$('summary').setAttribute('aria-live','polite');if(running)$('action-status').textContent='Modulus animation paused.';};
const known=id=>entries.find(e=>e.id===id);
const message=(text,error=false)=>{const target=$(error?'error':'action-status');target.hidden=false;if(target.textContent!==text)target.textContent=text;};
const number=(value,min,max,label,id)=>{const n=Number(value);if(!String(value).trim()||!Number.isInteger(n)||n<min||n>max){$(id).setAttribute('aria-invalid','true');$(id).setAttribute('aria-describedby','sa-error');throw Error(`${label} must be an integer from ${min} to ${max}.`);}return n;};
function readState(){
  ids.forEach(id=>$(id).removeAttribute('aria-invalid'));
  ids.forEach(id=>{if($(id).getAttribute('aria-describedby')==='sa-error')$(id).removeAttribute('aria-describedby');});
  const next=Object.fromEntries(ids.map(id=>[id,$(id).value]));
  for(const id of ids.filter(id=>!['start','count','modulus'].includes(id)))if(![...$(id).options].some(option=>option.value===next[id]))throw Error(`Choose a valid ${id}.`);
  next.start=number(next.start,0,999,'First index','start');next.count=number(next.count,2,1000,'Terms shown','count');next.modulus=number(next.modulus,2,128,'Modulus','modulus');
  return next;
}
function valuesFor(id,count){if(id==='custom'){try{const values=parseTerms($('custom').value);if(values.length<2)throw Error('Paste at least two integer terms.');$('custom').removeAttribute('aria-invalid');$('custom').removeAttribute('aria-describedby');return values;}catch(error){$('custom').setAttribute('aria-invalid','true');$('custom').setAttribute('aria-describedby','sa-error');throw error;}}const entry=known(id);if(!entry)throw Error('Unknown sequence.');return generate(entry,Math.min(entry.cap,count));}
function render(){
  try{
    const next=readState();$('custom-panel').hidden=next.sequence!=='custom';
    const entry=known(next.sequence), values=valuesFor(next.sequence,next.start+next.count+1);
    if(next.start>=values.length-1){$('start').setAttribute('aria-invalid','true');$('start').setAttribute('aria-describedby','sa-error');throw Error(`First index must be below ${values.length-1} for this sequence.`);}
    const series=[{name:entry?entry.title:'Pasted sequence (unreviewed)',values}];
    if(next.compare){const comparison=known(next.compare);series.push({name:comparison.title+' (comparison)',values:valuesFor(next.compare,next.start+next.count+1)});}
    const rows=series.flatMap(s=>rowsFor(s.values,next,s.name));
    if(!rows.some(r=>r.y!==null&&r.x!==null))throw Error('No plottable values in this window. Try a linear or signed logarithmic scale, or another starting index.');
    state=next;lastRows=rows;if(state.sequence==='custom')lastCustomTerms=values.map(String).join(',');$('error').hidden=true;
    $('custom-panel').hidden=next.sequence!=='custom';
    $('N').disabled=$('power').disabled=entry?.kind!=='reciprocal';
    if(entry?.kind==='reciprocal'){$('N').value=entry.N;$('power').value=entry.power;}
    const modular=['mod','grid','frequency','mod-pairs'].includes(state.view);
    $('scale').disabled=modular;
    $('marks').disabled=['grid','frequency','mod-pairs'].includes(state.view);
    $('current-formula').textContent=entry?entry.formula:'User-supplied integers. No definition, attribution, or proof has been reviewed.';
    $('entry-links').replaceChildren();
    if(entry){const link=document.createElement('a');link.href='sequences/'+entry.id+'.html';link.textContent='Read '+entry.id+' · definition, sources, and related entries';$('entry-links').append(link);}
    draw(rows,series.map(s=>s.name));
    const shown=rows.filter(r=>r.name===series[0].name), max=shown.at(-1)?.n;
    minimumWindow=Math.max(2,Math.min(...rows.filter(row=>row.x!==null&&row.y!==null).map(row=>row.n-state.start))+1);
    $('summary').textContent=`${series[0].name} · indices ${state.start}–${max} · ${shown.length} terms${series.length>1?' · comparison overlaid':''}.`;
    $('window').textContent=`Family limit: ${entry?entry.cap:values.length} terms. Sums and running averages include all terms from index 0, even when the displayed window starts later. Differences and ratios use the preceding term. Plot coordinates are approximate; the table and CSV retain exact values.`;
    const p=candidatePeriod(shown.map(r=>r.residue));
    $('period').textContent=modular?(p?`Residues in this window repeat with candidate period ${p} (at least three repetitions). This finite check does not prove a global period.`:'No period with at least three complete repetitions was found in this residue window.'):'Residue-period suggestions appear in modular views.';
    const tbody=$('values');tbody.replaceChildren();
    for(const r of rows){const tr=document.createElement('tr');for(const value of [r.name,r.n,r.raw,r.value,r.residue??'undefined',r.x??'omitted',r.y??'omitted']){const td=document.createElement('td');td.textContent=String(value);tr.append(td);}tbody.append(tr);}
    $('table-caption').textContent='Exact samples for the current view. Residues apply to the selected transform; plot coordinates are approximate.';
    const cap=entry?entry.cap:values.length;
    $('previous-window').disabled=state.start===0;$('next-window').disabled=state.start+state.count>=cap;
    $('fewer').disabled=shown.length<=minimumWindow;$('more').disabled=state.count>=cap-state.start;
    const block=integerBlock();$('search-values').disabled=!block;
    $('oeis-terms').href=block&&block.join(',').length<1800?'https://oeis.org/search?q='+encodeURIComponent('signed:'+block.join(',')):'https://oeis.org/';
    $('oeis-terms').textContent=block&&block.join(',').length<1800?'Look up displayed integers in OEIS':'Open OEIS';
    return true;
  }catch(error){stopAnimation();if(/integer-valued/.test(error.message)){$('transform').setAttribute('aria-invalid','true');$('transform').setAttribute('aria-describedby','sa-error');}message(error.message+(plot?' The last valid plot is retained.':''),true);return false;}
}
function draw(rows,names){
  const palette=plotColors(appearance),W=Math.max(320,Math.round($('plot').clientWidth)),H=plotHeight(W,appearance),pad={left:W<560?56:82,right:20,top:names.length>1?90:68,bottom:62}, pw=W-pad.left-pad.right,ph=H-pad.top-pad.bottom;
  const modular=['mod','grid','frequency','mod-pairs'].includes(state.view), frequency=state.view==='frequency',grid=['grid','mod-pairs'].includes(state.view);
  let points=rows.filter(r=>r.x!==null&&r.y!==null).map(r=>({...r,series:names.indexOf(r.name)}));
  if(frequency){points=[];names.forEach((name,series)=>{const selected=rows.filter(r=>r.name===name);for(let i=0;i<state.modulus;i++)points.push({name,n:i,x:i,y:selected.filter(r=>r.residue===i).length,value:'',raw:'',residue:i,series});});}
  const zero=appearance.baseline==='zero'||frequency||state.marks==='bars'||modular;appearanceControls?.context(modular||state.marks==='bars');
  let xs=points.map(r=>r.x),ys=points.map(r=>r.y),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys,...(zero?[0]:[])),ymax=Math.max(...ys,...(zero?[0]:[]));
  if(grid){xmin=0;xmax=state.modulus-1;ymin=0;ymax=state.modulus-1;}
  if(state.view==='mod'){ymin=0;ymax=state.modulus-1;}
  const expandConstant=(low,high)=>{if(low!==high)return[low,high];const margin=Math.max(1,Math.abs(low)*0.05),left=low-margin,right=high+margin;return[Number.isFinite(left)?left:low,Number.isFinite(right)?right:high];};
  [xmin,xmax]=expandConstant(xmin,xmax);[ymin,ymax]=expandConstant(ymin,ymax);
  // Normalize before multiplying to keep very large finite values within range.
  const between=(v,a,b)=>{const scale=Math.max(Math.abs(a),Math.abs(b),1);return (v/scale-a/scale)/(b/scale-a/scale);};
  const x=v=>pad.left+between(v,xmin,xmax)*pw,y=v=>H-pad.bottom-between(v,ymin,ymax)*ph;
  const hadFocus=$('plot').contains(document.activeElement);
  const svg=element('svg',{viewBox:`0 0 ${W} ${H}`,role:'group','aria-labelledby':'sa-svg-title sa-svg-description','aria-describedby':'sa-plot-help'});
  svg.append(element('rect',{width:W,height:H,fill:'#fafaf5'}));
  svg.append(element('title',{id:'sa-svg-title'},optionLabel('view',state.view)));
  svg.append(element('desc',{id:'sa-svg-description'},`Discrete samples for ${names.join(' and ')}. Exact values are available in the atlas table and CSV export.`));
  svg.append(element('path',{d:`M${pad.left} ${pad.top}V${H-pad.bottom}H${W-pad.right}`,stroke:'#87988b','data-plot-axis':'true','stroke-width':1,fill:'none'}));
  const tick=v=>v===0?'0':Math.abs(v)>=1e6||Math.abs(v)<0.001?v.toExponential(1):Number(v.toPrecision(4)).toString();
  const yTicks=modular?[...new Set(Array.from({length:6},(_,i)=>Math.round((1-i/5)*ymax+(i/5)*ymin)))]:Array.from({length:6},(_,i)=>(1-i/5)*ymax+(i/5)*ymin);
  for(const pyValue of yTicks){
    const py=y(pyValue);
    if(appearance.grid==='on')svg.append(element('line',{x1:pad.left,x2:W-pad.right,y1:py,y2:py,stroke:'#d9dfd4','data-plot-grid':'true','stroke-width':1}));
    svg.append(element('text',{x:pad.left-10,y:py+4,'text-anchor':'end',fill:'#465347','font-size':12},tick(pyValue)));
  }
  const xTicks=[...new Set(Array.from({length:6},(_,i)=>state.view==='pairs'?(1-i/5)*xmin+(i/5)*xmax:Math.round((1-i/5)*xmin+(i/5)*xmax)))];
  for(const pxValue of xTicks){const px=x(pxValue);
    svg.append(element('text',{x:px,y:H-pad.bottom+24,'text-anchor':'middle',fill:'#465347','font-size':12},tick(pxValue)));
  }
  const xLabel=frequency?'Residue':state.view==='grid'?'n mod m':state.view==='mod-pairs'?'Transformed a(n) mod m':state.view==='pairs'?'Transformed a(n)':'Index n';
  const yLabel=frequency?'Count in window':state.view==='mod-pairs'?'Transformed a(n+1) mod m':state.view==='grid'||state.view==='mod'?'Transformed a(n) mod m':state.view==='pairs'?'Transformed a(n+1)':optionLabel('transform',state.transform);
  svg.append(element('text',{x:W/2,y:H-12,'text-anchor':'middle',fill:'#243d2d','font-size':14},xLabel));
  const fit=text=>{const limit=Math.floor(pw/7.8);return text.length>limit?text.slice(0,limit-1)+'…':text;};
  names.forEach((name,i)=>svg.append(element('text',{x:pad.left,y:23+i*22,fill:palette[i],'font-size':14},fit(name))));
  svg.append(element('text',{x:pad.left,y:names.length>1?67:45,fill:'#243d2d','font-size':12},fit(yLabel+(modular?` · m = ${state.modulus}`:` · ${optionLabel('scale',state.scale)}`))));
  if(state.marks==='line'&&!frequency&&!grid){
    names.forEach((name,i)=>{let d='',connected=false;for(const r of rows.filter(r=>r.name===name)){if(r.x===null||r.y===null){connected=false;continue;}d+=`${connected?'L':'M'}${x(r.x)},${y(r.y)} `;connected=true;}svg.append(element('path',{d,fill:'none',stroke:palette[i], 'stroke-width':Number(appearance.width),'stroke-dasharray':i?'6 4':'none'}));});
  }
  // Aggregate grid collisions into count-labelled marks.
  if(grid){
    const groups=new Map();for(const r of points){const key=[r.series,r.x,r.y].join(':');const g=groups.get(key);if(g){g.hits++;}else groups.set(key,{...r,hits:1});}points=[...groups.values()];
  }
  let markIndex=0;const indexLabels=[];
  for(const r of points){
    const color=palette[state.color==='value'?Number(BigInt(r.raw||r.residue)%BigInt(state.modulus)+BigInt(state.modulus))%state.modulus%palette.length:state.color==='index'?r.n%state.modulus%palette.length:r.series];
    let mark;const attrs={fill:color,stroke:r.series?palette[1]:color,'stroke-width':Number(appearance.width)},radius=r.hits?Math.min(16,Number(appearance.point)+Math.log2(r.hits)):Number(appearance.point);
    if(frequency||state.marks==='bars'&&!grid){
      const width=Math.max(1,Math.min(24,pw/(frequency?state.modulus:rows.length)*0.7));const baseline=y(0);
      mark=element('rect',{x:x(r.x)-width/2+(r.series?width/3:0),y:Math.min(baseline,y(r.y)),width,height:Math.max(1,Math.abs(baseline-y(r.y))),...attrs,opacity:r.series?0.6:0.85});
    }else if(r.series){mark=element('rect',{x:x(r.x)-radius,y:y(r.y)-radius,width:radius*2,height:radius*2,...attrs,fill:plotTheme(appearance).background});
    }else mark=element('circle',{cx:x(r.x),cy:y(r.y),r:radius,...attrs});
    const label=frequency?`${r.name}: residue ${r.x}, count ${r.y}`:grid?`${r.name}: residue pair (${r.x}, ${r.y}), ${r.hits} occurrence${r.hits===1?'':'s'}`:`${r.name}: n=${r.n}; a(n)=${r.raw}; transformed=${r.value}${modular?`; residue=${r.residue}`:''}`;
    const index=markIndex++;
    const abbreviated=frequency||grid?label:`${r.name}: n=${r.n}; a(n)=${briefValue(r.raw)}${r.value!==r.raw?'; transformed='+briefValue(r.value):''}${modular?`; residue=${r.residue}`:''}${r.raw.length>60||r.value.length>60?'; full exact values in the atlas table and CSV.':''}`;
    mark.setAttribute('data-point',String(index));mark.setAttribute('tabindex','-1');mark.setAttribute('role','button');mark.setAttribute('aria-label',abbreviated);mark.setAttribute('data-exact-description',label);mark.append(element('title',{},label));
    mark.addEventListener('focus',()=>{if(timer)stopAnimation();inspectPoint(index);});
    mark.addEventListener('pointerenter',()=>{$('inspect').textContent=label;});mark.addEventListener('click',()=>{stopAnimation();inspectPoint(index,{focus:true,announce:true});});svg.append(mark);
    if(showIndexLabel(index,points.length,appearance,pw))indexLabels.push({x:x(r.x),y:Math.max(pad.top-5,y(r.y)-radius-6),text:frequency?'r='+r.x:grid?String(r.hits):String(r.n)});
  }
  for(const label of mergePlotLabels(indexLabels)){const text=element('text',{x:label.x,y:label.y,'text-anchor':'middle','font-size':11,fill:'#243d2d',class:'sp-plot-index'},label.text);text.append(element('title',{},label.full));svg.append(text);}
  finishPlotTheme(svg,appearance);$('plot').replaceChildren(svg);plot=svg;
  inspectPoint(pointIndex,{focus:hadFocus});
  const bars=frequency||state.marks==='bars'&&!grid;
  $('caption').textContent=`${names.map((name,i)=>`${bars?(i?'Translucent bars':'Filled bars'):(i?'Outlined squares'+(state.marks==='line'&&!grid?' / dashed line':''):'Filled circles'+(state.marks==='line'&&!grid?' / solid line':''))}: ${name}`).join('. ')}. ${state.color==='series'?'':'Colors cycle through eight colors; exact residue labels are available on each point. '}${frequency?'Bars count residues among the selected samples.':grid?'Larger marks indicate repeated residue pairs.':'Use First index and Terms shown to move or zoom the sample window.'} ${modular?`Modulus ${state.modulus}.`:''} ${rows.filter(r=>r.y===null||r.x===null).length} undefined or out-of-range samples omitted.`;
}
function download(content,type,name){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function inspectPoint(index,{focus=false,announce=false}={}){
  const marks=[...$('plot').querySelectorAll('[data-point]')];if(!marks.length)return;
  pointIndex=Math.max(0,Math.min(marks.length-1,index));
  marks.forEach((mark,i)=>{mark.setAttribute('tabindex',i===pointIndex?'0':'-1');mark.classList.toggle('sa-active-point',i===pointIndex);if(i===pointIndex)mark.setAttribute('aria-current','true');else mark.removeAttribute('aria-current');});
  const current=marks[pointIndex];$('inspect').textContent=current.getAttribute('data-exact-description');
  $('previous-point').disabled=pointIndex===0;$('next-point').disabled=pointIndex===marks.length-1;
  if(focus)current.focus({preventScroll:true});
  if(announce)$('point-announcement').textContent=`Mark ${pointIndex+1} of ${marks.length}. ${current.getAttribute('aria-label')}`;
}
function integerBlock(){
  if(!lastRows.length)return null;const name=lastRows[0].name,rows=lastRows.filter(row=>row.name===name);let block=[];
  for(const row of rows){if(/^[-+]?\d+$/.test(row.value)){block.push(row.value);if(block.length===8)break;}else{if(block.length>=3)break;block=[];}}
  return block.length>=3?block:null;
}
function viewURL(hash='explorer'){
  const url=new URL(location.href);url.search='';for(const [key,value]of Object.entries(state))url.searchParams.set(key,String(value));
  if(state.sequence==='custom')url.searchParams.set('terms',lastCustomTerms);
  const linked=new URL(searchLink(url.href,$('query').value,searchOptions()));linked.hash=hash;
  const styled=appearanceControls?appearanceControls.link(linked.href):linked.href;
  return chartLabelControls?chartLabelControls.link(styled):styled;
}
async function copyText(text,label,success){
  try{await navigator.clipboard.writeText(text);$('share-fallback').hidden=true;message(success);}
  catch{$('share-fallback').hidden=false;$('share-fallback').firstChild.textContent=label;const field=$('share-link');field.value=text;field.focus();field.select();message('Copy '+label.toLowerCase()+' from the selected field.');}
}
function loadSequence(id){
  if(!known(id))return;showPanel('explorer');stopAnimation();$('sequence').value=id;$('start').value=0;$('count').value=32;pointIndex=0;
  render();document.getElementById('explorer-title').focus({preventScroll:true});document.getElementById('explorer').scrollIntoView({block:'start',behavior:'auto'});
}
function search({reset=false,restoreID=null,deferErrors=false}={}){
  clearTimeout(searchErrorTimer);
  if(reset)resultLimit=6;
  const query=$('query').value,options=searchOptions();
  try{
    lastResults=searchEntries(entries,query,options);
    const archiveLink=new URL('sequence-archive.html',location.href);if(query.trim())archiveLink.searchParams.set('query',query);archiveLink.hash='records';$('archive-search').href=archiveLink.href;
    if(!query.trim()&&options.filter==='all'&&!options.topic&&options.sort==='relevance'){
      const featured=['KSEQ-000007','KSEQ-000025','KSEQ-000022','KSEQ-000023','KSEQ-000001','KSEQ-000026'];
      lastResults.sort((a,b)=>{const order=id=>featured.includes(id)?featured.indexOf(id):100+Number(id.slice(-6));return order(a.entry.id)-order(b.entry.id);});
    }
    $('search-error').hidden=true;$('query').removeAttribute('aria-invalid');$('query').setAttribute('aria-describedby','sa-query-summary sa-search-status');
    const list=$('results');list.replaceChildren();
    list.classList.toggle('sa-featured',!query.trim()&&options.filter==='all'&&!options.topic);
    $('results-title').textContent=!query.trim()&&options.filter==='all'&&!options.topic?'Quick starting points':'Search results';
    for(const result of lastResults.slice(0,resultLimit)){
      const {entry,termMatch}=result,item=document.createElement('li');item.className='sa-search-hit';item.dataset.hitId=entry.id;
      const heading=document.createElement('h4'),link=document.createElement('a');link.href='sequences/'+entry.id+'.html';link.textContent=entry.title;heading.append(link);item.append(heading);
      const detail=document.createElement('p');detail.className='sa-hit-meta';detail.textContent=entry.id+' · '+(entry.status.startsWith('Known')?'Reference sequence':'Published family')+' · '+result.reason;item.append(detail);
      const sample=document.createElement('p');sample.className='sa-hit-terms';const from=termMatch?Math.max(0,termMatch.start-1):0,to=Math.min(entry.terms.length,Math.max(from+8,termMatch?termMatch.start+termMatch.length:8));
      sample.append(document.createTextNode(`n = ${from}: `));
      for(let n=from;n<to;n++){if(n>from)sample.append(document.createTextNode(', '));if(termMatch&&n>=termMatch.start&&n<termMatch.start+termMatch.length){const mark=document.createElement('mark');mark.textContent=entry.terms[n];sample.append(mark);}else sample.append(document.createTextNode(entry.terms[n]));}if(to<entry.terms.length)sample.append(document.createTextNode('…'));item.append(sample);
      const actions=document.createElement('div');actions.className='sa-hit-actions';
      const explore=document.createElement('button');explore.type='button';explore.dataset.load=entry.id;explore.textContent='Plot sequence';explore.setAttribute('aria-label','Plot '+entry.title);
      const study=document.createElement('a');study.href='sequences/'+entry.id+'.html?study=raw&from='+Math.min(termMatch?.start??0,52)+'&size=12#analysis';study.textContent='Study exact terms';study.setAttribute('aria-label','Study exact terms for '+entry.title);
      const save=document.createElement('button');save.type='button';save.dataset.saveSequence=entry.id;actions.append(explore,study,save);item.append(actions);list.append(item);
    }
    $('empty').hidden=lastResults.length!==0;$('suggestions').replaceChildren();
    if(!lastResults.length){for(const suggestion of suggestions(entries,query)){const button=document.createElement('button');button.type='button';button.dataset.suggestion=suggestion;button.textContent='Try '+suggestion;$('suggestions').append(button);}}
    $('more-results').hidden=lastResults.length<=resultLimit;
    $('saved-count').textContent=`${saved.size} saved ${saved.size===1?'entry':'entries'}`;
    $('show-saved').setAttribute('aria-pressed',String(options.filter==='saved'));
    const shown=Math.min(resultLimit,lastResults.length),summary=`${lastResults.length} of ${entries.length} entries. ${shown} quick ${shown===1?'result':'results'} shown. Integer matching uses the 64 recorded terms per entry.`;
    clearTimeout(statusTimer);statusTimer=setTimeout(()=>{$('search-status').textContent=summary;},180);
    updateSaveButtons(document.getElementById('sequence-atlas'),saved);
    if(restoreID){const target=[...$('results').querySelectorAll('[data-save-sequence]')].find(button=>button.dataset.saveSequence===restoreID);(target||$('results-title')).focus({preventScroll:true});}
    return true;
  }catch(error){clearTimeout(statusTimer);const showError=()=>{$('query').setAttribute('aria-invalid','true');$('query').setAttribute('aria-describedby','sa-query-summary sa-search-status sa-search-error');$('search-error').hidden=false;if($('search-error').textContent!==error.message)$('search-error').textContent=error.message;$('search-status').textContent='Search not updated. The catalogue and any previous results remain available.';};if(deferErrors)searchErrorTimer=setTimeout(()=>{if($('query').value===query)showError();},300);else showError();return false;}
}
function investigation(key){
  const presets={
    fibonacci:{sequence:'KSEQ-000025',view:'mod-pairs',modulus:10,count:60,note:'Follow pairs of consecutive Fibonacci residues modulo 10. Which pairs recur within these 60 samples?'},
    euler:{sequence:'KSEQ-000026',view:'standard',scale:'signed-log',count:24,note:'The signed even Euler numbers alternate in sign. Compare the signed logarithmic plot with the exact values.'},
    powers:{sequence:'KSEQ-000007',compare:'KSEQ-000008',view:'standard',scale:'log',count:24,note:'Compare reciprocal powers r=1 and r=2 at spacing N=4. Equal compressed indices correspond to the same ordinary degree 4n.'},
    partitions:{sequence:'KSEQ-000022',compare:'KSEQ-000023',view:'standard',scale:'log',count:24,note:'Compare Bell numbers with ordered Bell numbers. The factorial weighting orders the blocks of each partition.'}
  };
  const preset=presets[key];if(!preset)return;stopAnimation();const next={...defaults,...preset};ids.forEach(id=>$(id).value=next[id]);$('investigation').textContent=preset.note;pointIndex=0;document.querySelector('.sa-advanced').open=Boolean(next.compare||next.scale!=='linear');render();
}
function setupDiscovery(params){
  $('discovery-controls').hidden=false;
  let latest=null;
  const clearError=()=>{$('discovery-error').hidden=true;$('discovery-input').removeAttribute('aria-invalid');$('discovery-input').setAttribute('aria-describedby','sa-discovery-help');};
  const reportError=error=>{$('discovery-error').hidden=false;$('discovery-error').textContent=error.message+(latest?' Previous results remain available.':'');$('discovery-input').setAttribute('aria-invalid','true');$('discovery-input').setAttribute('aria-describedby','sa-discovery-help sa-discovery-error');};
  function run(){
    try{
      const result=discover(entries,$('discovery-input').value,{both:$('discovery-both').checked});latest=result;
      clearError();
      const list=$('discovery-results');list.replaceChildren();
      for(const [i,hit] of result.results.entries()){
        const item=document.createElement('li');item.className='sa-search-hit';
        const heading=document.createElement('h3'),link=document.createElement('a');link.href='sequences/'+hit.id+'.html';link.textContent=hit.title;heading.append(link);item.append(heading);
        const description=document.createElement('p');description.textContent=`${operationLabel(hit.inputOperation)} of your input, indices ${hit.inputStart}–${hit.inputStart+hit.length-1}, matches ${operationLabel(hit.targetOperation).toLowerCase()} of ${hit.id}, indices ${hit.targetStart}–${hit.targetStart+hit.length-1}. All ${hit.length} transformed input terms match.`;item.append(description);
        const sample=document.createElement('p');sample.className='sa-hit-terms';sample.textContent=hit.values.slice(0,8).join(', ')+(hit.length>8?'…':'');item.append(sample);
        const formula=document.createElement('p');formula.className='sa-note';formula.textContent=OPERATIONS.find(([id])=>id===hit.inputOperation)?.[2]||`The first ${hit.inputStart} input terms are omitted.`;if(hit.targetStarts.length>1)formula.textContent+=` It also matches at ${hit.targetStarts.length-1} other target starting ${hit.targetStarts.length===2?'index':'indices'}, recorded in the JSON.`;if(hit.constant)formula.textContent+=' This sample has fewer than three distinct values, so the match may be uninformative.';item.append(formula);
        const actions=document.createElement('div');actions.className='sa-hit-actions';
        const input=document.createElement('button');input.type='button';input.textContent='Plot transformed input';input.dataset.discoveryPlot=String(i);input.disabled=hit.values.join(',').length>20000||hit.values.some(v=>v.replace('-','').length>300);if(input.disabled)input.title='This transform exceeds the plot input capacity; download the exact discovery JSON.';
        const target=document.createElement('button');target.type='button';target.textContent='Plot catalogue match';target.dataset.discoveryTarget=String(i);actions.append(input,target);item.append(actions);list.append(item);
      }
      $('discovery-status').textContent=`Checked ${result.input.length} input terms using ${result.testedOperations} distinct usable input forms against ${entries.length} entries. ${result.total} finite matches; ${result.results.length} shown.${result.total?'':' The explicit OEIS link offers a broader search. No match is not evidence of novelty.'}`;
      $('discovery-export').hidden=false;
      const integers=result.input.join(',');$('discovery-oeis').href=integers.length<1800?'https://oeis.org/search?q='+encodeURIComponent('signed:'+integers):'https://oeis.org/';$('discovery-oeis').textContent=integers.length<1800?'look up the last checked input in OEIS':'open OEIS';
      return true;
    }catch(error){reportError(error);return false;}
  }
  $('discovery-form').addEventListener('submit',event=>{event.preventDefault();run();});
  $('discovery-example').addEventListener('click',()=>{$('discovery-input').value='0, 1, 4, 9, 16, 25, 36, 49';$('discovery-both').checked=true;run();});
  $('random-entry').addEventListener('click',()=>{const word=new Uint32Array(1);crypto.getRandomValues(word);location.href='sequences/'+entries[word[0]%entries.length].id+'.html';});
  $('discovery-share').addEventListener('click',async()=>{
    try{const values=analyzeInput($('discovery-input').value),url=new URL(location.href);clearError();url.search='';url.searchParams.set('discover',values.join(','));if($('discovery-both').checked)url.searchParams.set('dc','1');url.hash='discover';
      try{await navigator.clipboard.writeText(url.href);$('discovery-status').textContent='Discovery link copied. It includes the pasted terms.';}catch{const field=$('discovery-copy-text');$('discovery-copy-fallback').hidden=false;field.value=url.href;field.focus();field.select();$('discovery-status').textContent='Copy the discovery link from the selected field. It includes the pasted terms.';}
    }catch(error){reportError(error);}
  });
  $('discovery-export').addEventListener('click',()=>{if(latest)download(JSON.stringify({schema:1,...latest,scope:'Finite matches in the local catalogue; not identities, proofs, or evidence of novelty.'},null,2)+'\n','application/json','komorebi-sequence-discovery.json');});
  $('discovery-results').addEventListener('click',event=>{
    const button=event.target.closest('button');if(!button||!latest)return;
    const index=button.dataset.discoveryPlot??button.dataset.discoveryTarget;if(index===undefined)return;const hit=latest.results[Number(index)];
    const input=button.dataset.discoveryPlot!==undefined,next={...defaults,view:'standard',sequence:input?'custom':hit.id,transform:input?'raw':hit.targetOperation,start:input?0:hit.targetStart,count:Math.min(32,hit.length),scale:hit.values.some(v=>v.length>15)?'signed-log':'linear'};
    showPanel('explorer');stopAnimation();ids.forEach(id=>$(id).value=next[id]);if(input)$('custom').value=hit.values.join(',');pointIndex=0;
    if(render()){document.querySelector('.sa-advanced').open=true;document.getElementById('explorer-title').focus({preventScroll:true});document.getElementById('explorer').scrollIntoView({block:'start',behavior:'auto'});}
  });
  if(params.has('discover')){$('discovery-input').value=params.get('discover');$('discovery-both').checked=params.get('dc')==='1';run();}
}
function setupRefinements(){
  const root=document.getElementById('sequence-atlas');
  root.addEventListener('click',event=>{
    const target=event.target.closest('button');if(!target)return;
    if(target.dataset.load){loadSequence(target.dataset.load);return;}
    if(target.dataset.saveSequence){const id=target.dataset.saveSequence,wasSaved=saved.has(id),inResults=Boolean(target.closest('[data-hit-id]'));if(wasSaved)saved.delete(id);else saved.add(id);const stored=writeSaved(storage,[...saved],new Set(entries.map(entry=>entry.id)));updateSaveButtons(root,saved);search({restoreID:inResults?id:null});if(target.closest('[data-sequence]')?.hidden)$('results-title').focus({preventScroll:true});message((wasSaved?'Entry removed from saved entries.':'Entry saved.')+(stored?'':' Saved for this page only; browser storage is unavailable.'));return;}
    const query=target.dataset.searchExample||target.dataset.suggestion;if(query){$('query').value=query;$('filter').value='all';$('topic').value='';search({reset:true});$('query').focus();return;}
    if(target.dataset.investigation)investigation(target.dataset.investigation);
  });
  $('search-form').addEventListener('submit',event=>{event.preventDefault();if(search({reset:true}))$('results-title').focus({preventScroll:true});});
  $('query').addEventListener('input',()=>search({reset:true,deferErrors:true}));
  $('query').addEventListener('keydown',event=>{if(event.key==='ArrowDown'){const first=$('results').querySelector('a');if(first){event.preventDefault();first.focus();}}if(event.key==='Escape'){event.preventDefault();$('query').value='';search({reset:true});}});
  for(const id of ['filter','topic','match','sort'])$(id).addEventListener('change',()=>search({reset:true}));
  $('clear-search').addEventListener('click',()=>{$('query').value='';$('filter').value='all';$('topic').value='';$('match').value='any';$('sort').value='relevance';search({reset:true});$('query').focus();});
  $('share-search').addEventListener('click',()=>copyText(viewURL('find'),'Search link','Search link copied.'));
  $('show-saved').addEventListener('click',()=>{$('query').value='';$('topic').value='';$('filter').value=$('filter').value==='saved'?'all':'saved';search({reset:true});});
  $('more-results').addEventListener('click',()=>{const previous=resultLimit;resultLimit+=6;search();$('results').children[previous]?.querySelector('a').focus({preventScroll:true});});
  $('plot').addEventListener('keydown',event=>{if(!event.target.closest('[data-point]'))return;const count=$('plot').querySelectorAll('[data-point]').length;let index=pointIndex;if(['ArrowLeft','ArrowUp'].includes(event.key))index--;else if(['ArrowRight','ArrowDown'].includes(event.key))index++;else if(event.key==='Home')index=0;else if(event.key==='End')index=count-1;else if(['Enter',' '].includes(event.key)){event.preventDefault();inspectPoint(index,{announce:true});return;}else return;event.preventDefault();stopAnimation();inspectPoint(index,{focus:true});});
  $('previous-point').addEventListener('click',()=>{stopAnimation();inspectPoint(pointIndex-1,{announce:true});});$('next-point').addEventListener('click',()=>{stopAnimation();inspectPoint(pointIndex+1,{announce:true});});
  $('table-open').addEventListener('click',()=>{$('table-detail').open=true;$('values-region').focus();});
  const move=(direction)=>{stopAnimation();const cap=state.sequence==='custom'?parseTerms(lastCustomTerms).length:known(state.sequence).cap;const next=direction==='less'?{count:Math.max(minimumWindow,Math.floor(Math.min(state.count,cap-state.start)/2))}:direction==='more'?{count:Math.min(cap-state.start,state.count*2)}:{start:Math.max(0,Math.min(cap-2,state.start+(direction==='next'?state.count:-state.count)))};for(const [key,value]of Object.entries(next))$(key).value=value;pointIndex=0;render();};
  for(const [id,direction]of [['previous-window','previous'],['next-window','next'],['fewer','less'],['more','more']])$(id).addEventListener('click',()=>move(direction));
  $('copy-values').addEventListener('click',()=>{const primary=lastRows[0]?.name;copyText(lastRows.filter(row=>row.name===primary).map(row=>row.value).join(', '),'Displayed values','Displayed transformed values copied. Undefined positions remain labelled.');});
  $('search-values').addEventListener('click',()=>{const block=integerBlock();if(!block)return;showPanel('find');$('query').value=block.join(',');$('filter').value='all';$('topic').value='';$('match').value='any';search({reset:true});$('query').focus({preventScroll:true});document.getElementById('find').scrollIntoView({block:'start',behavior:'auto'});});
  $('json').addEventListener('click',()=>download(JSON.stringify({schema:1,view:state,chartLabels:chartLabelControls?.state||null,customTerms:state.sequence==='custom'?lastCustomTerms:null,rows:lastRows,oeisSnapshotRetrievedAt:data.snapshot?.retrieved_at||null},null,2)+'\n','application/json','komorebi-sequence-view.json'));
  document.addEventListener('keydown',event=>{if(event.key==='/'&&(event.ctrlKey||event.metaKey)&&!event.altKey&&!event.target.isContentEditable&&!['INPUT','TEXTAREA','SELECT'].includes(event.target.tagName)){event.preventDefault();showPanel('find');$('query').focus();}});
  addEventListener('storage',()=>{saved=new Set(readSaved(storage,new Set(entries.map(entry=>entry.id))).ids);updateSaveButtons(root,saved);search();});
}
async function init(){
  const response=await fetch(new URL('./sequence-atlas-data.json',import.meta.url));if(!response.ok)throw Error('Catalogue data could not be loaded.');data=await response.json();entries=data.entries;
  const params=new URL(location.href).searchParams;
  setupDiscovery(params);
  if(params.has('seq')&&!params.has('sequence'))params.set('sequence',params.get('seq'));
  let ignored=false;
  for(const id of ids){const proposed=params.has(id)?params.get(id):String(defaults[id]);const control=$(id),valid=control.tagName==='SELECT'?[...control.options].some(option=>option.value===proposed):proposed.trim()!==''&&Number.isInteger(Number(proposed))&&Number(proposed)>=Number(control.min)&&Number(proposed)<=Number(control.max);control.value=valid?proposed:defaults[id];if(!valid)ignored=true;}
  if(params.has('terms')){$('custom').value=params.get('terms');}
  if($('sequence').value==='custom'){try{if(parseTerms($('custom').value).length<2)throw Error('Too few terms');}catch{$('sequence').value=defaults.sequence;ignored=true;}}
  $('query').value=params.get('q')||'';
  for(const id of ['filter','topic','match','sort'])if(params.has(id)&&[...$(id).options].some(option=>option.value===params.get(id)))$(id).value=params.get(id);
  saved=new Set(readSaved(storage,new Set(entries.map(entry=>entry.id))).ids);
  $('workspace').hidden=false;$('search-controls').hidden=false;$('search-results').hidden=false;$('loading').hidden=true;
  document.querySelectorAll('[data-load]').forEach(button=>{button.hidden=false;});
  setupRefinements();
  ids.forEach(id=>$(id).addEventListener('change',()=>{stopAnimation();if(id==='sequence'){const entry=known($('sequence').value);if(entry&&Number($('start').value)>=entry.cap-1)$('start').value=0;pointIndex=0;}render();}));
  for(const id of ['N','power'])$(id).addEventListener('change',()=>{const match=entries.find(e=>e.kind==='reciprocal'&&e.N===Number($('N').value)&&e.power===Number($('power').value));if(match){stopAnimation();$('sequence').value=match.id;render();}});
  let customTimer=null;$('custom').addEventListener('input',()=>{clearTimeout(customTimer);customTimer=setTimeout(()=>{if($('sequence').value==='custom')render();},180);});
  $('animate').addEventListener('click',()=>{if(timer){stopAnimation();message('Modulus animation stopped.');return;}if(!['mod','grid','frequency','mod-pairs'].includes($('view').value))$('view').value='mod';if(!render())return;$('animate').textContent='Stop animation';$('animate').setAttribute('aria-pressed','true');$('summary').setAttribute('aria-live','off');message('Modulus animation started, cycling from 2 through 128. Inspect a mark or change a control to pause.');timer=setInterval(()=>{$('modulus').value=Number($('modulus').value)>=128?2:Number($('modulus').value)+1;render();},matchMedia('(prefers-reduced-motion: reduce)').matches?1600:800);});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopAnimation();});
  $('reset').addEventListener('click',()=>{stopAnimation();ids.forEach(id=>$(id).value=defaults[id]);render();});
  $('share').addEventListener('click',()=>copyText(viewURL(),'View link','View link copied.'));
  $('csv').addEventListener('click',()=>{const csv='sequence,n,a_n,transformed,residue,plot_x,plot_y,modulus,transform,view,scale\n'+lastRows.map(r=>[r.name,r.n,r.raw,r.value,r.residue??'',r.x??'',r.y??'',state.modulus,state.transform,state.view,state.scale].map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\n')+'\n';download(csv,'text/csv;charset=utf-8','komorebi-sequence-exact.csv');});
  for(const format of ['svg','png'])$(format).addEventListener('click',()=>exportPlot(plot,format,'komorebi-sequence').catch(error=>message(error.message,true)));
  appearanceControls=mountPlotOptions({host:$('plot-options'),prefix:'sa',onChange:style=>{appearance=style;if(lastRows.length)draw(lastRows,[...new Set(lastRows.map(row=>row.name))]);}});appearance=appearanceControls.state;
  chartLabelControls=mountSinglePlotLabels({
    anchor:$('plot-options'),plot:$('plot'),prefix:'sa',
    getSources:()=>[{id:state.sequence==='custom'?'CUSTOM':state.sequence,title:known(state.sequence)?.title||'Pasted sequence'},...(state.compare?[{id:state.compare,title:known(state.compare)?.title||state.compare}]:[])],
    onChange:()=>{if(lastRows.length)draw(lastRows,[...new Set(lastRows.map(row=>row.name))]);}
  });
  for(const [name,label,settings]of [['growth','Growth view',{view:'standard',transform:'raw',scale:'signed-log',marks:'line',color:'series'}],['residues','Residue view',{view:'mod',transform:'raw',scale:'linear',marks:'points',color:'value'}],['changes','Changes',{view:'standard',transform:'difference',scale:'signed-log',marks:'bars',color:'series'}]]){
    const button=document.createElement('button');button.type='button';button.textContent=label;button.dataset.plotPreset=name;button.addEventListener('click',()=>{stopAnimation();for(const [key,value]of Object.entries(settings))$(key).value=value;render();});$('plot-presets').append(button);
  }
  render();search();
  if($('compare').value||$('transform').value!=='raw'||$('scale').value!=='linear')document.querySelector('.sa-advanced').open=true;
  if(ignored)message('Some link settings were invalid and were replaced with defaults.');
  let observedWidth=$('plot').clientWidth;
  new ResizeObserver(()=>{const width=$('plot').clientWidth;if(Math.abs(width-observedWidth)>2&&lastRows.length){observedWidth=width;draw(lastRows,[...new Set(lastRows.map(r=>r.name))]);}}).observe($('plot'));
  setupDirectory(document.getElementById('sequence-atlas'),entries);
  showPanel=setupInterface(document.getElementById('sequence-atlas'),{onLeavePlot:stopAnimation});
  showPanel(workspaceForURL(location.href),{history:false});
  document.getElementById('sequence-atlas').dataset.interfaceReady='true';
}
init().catch(error=>{$('loading').textContent='The interactive explorer could not be loaded. Read the catalogue and term pages below. '+error.message;});
