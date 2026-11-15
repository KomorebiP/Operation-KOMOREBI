import {generate,parseTerms,rowsFor,candidatePeriod,findMatches} from './sequence-atlas-core.mjs';

const $=id=>document.getElementById('sa-'+id);
const ids=['sequence','compare','view','transform','scale','marks','start','count','modulus','color'];
const defaults={sequence:'KSEQ-000007',compare:'',view:'mod',transform:'raw',scale:'linear',marks:'points',start:0,count:32,modulus:7,color:'series'};
const svgNS='http://www.w3.org/2000/svg';
const element=(tag,attrs={},text='')=>{const e=document.createElementNS(svgNS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text)e.textContent=text;return e;};
let data,entries,state={...defaults},timer=null,lastRows=[],plot;
const palette=['#185a43','#a44916','#3d5eaa','#854799','#8b6a0c','#167482','#b13c60','#4e7130'];
const stopAnimation=()=>{clearInterval(timer);timer=null;$('animate').textContent='Animate modulus';$('animate').setAttribute('aria-pressed','false');};
const known=id=>entries.find(e=>e.id===id);
const message=(text,error=false)=>{if(error){$('error').hidden=false;$('error').textContent=text;}else{$('summary').textContent=text;}};
const number=(value,min,max,label)=>{const n=Number(value);if(!Number.isInteger(n)||n<min||n>max)throw Error(`${label} must be an integer from ${min} to ${max}.`);return n;};
function readState(){
  const next=Object.fromEntries(ids.map(id=>[id,$(id).value]));
  next.start=number(next.start,0,999,'First index');next.count=number(next.count,2,1000,'Terms shown');next.modulus=number(next.modulus,2,128,'Modulus');
  return next;
}
function valuesFor(id,count){if(id==='custom')return parseTerms($('custom').value);const entry=known(id);if(!entry)throw Error('Unknown sequence.');return generate(entry,Math.min(entry.cap,count));}
function render(){
  try{
    const next=readState();$('custom-panel').hidden=next.sequence!=='custom';
    const entry=known(next.sequence), values=valuesFor(next.sequence,next.start+next.count+1);
    if(next.start>=values.length-1)throw Error(`First index must be below ${values.length-1} for this sequence.`);
    const series=[{name:entry?entry.title:'Pasted sequence (unreviewed)',values}];
    if(next.compare){const comparison=known(next.compare);series.push({name:comparison.title+' (comparison)',values:valuesFor(next.compare,next.start+next.count+1)});}
    const rows=series.flatMap(s=>rowsFor(s.values,next,s.name));
    if(!rows.some(r=>r.y!==null&&r.x!==null))throw Error('No plottable values in this window. Try linear or signed logarithmic scale, or another starting index.');
    state=next;lastRows=rows;$('error').hidden=true;
    $('custom-panel').hidden=next.sequence!=='custom';
    $('N').disabled=$('power').disabled=entry?.kind!=='reciprocal';
    if(entry?.kind==='reciprocal'){$('N').value=entry.N;$('power').value=entry.power;}
    const modular=['mod','grid','frequency'].includes(state.view);
    $('scale').disabled=modular;
    $('marks').disabled=['grid','frequency'].includes(state.view);
    $('current-formula').textContent=entry?entry.formula:'User-supplied integers. No definition, attribution, or proof has been reviewed.';
    draw(rows,series.map(s=>s.name));
    const shown=rows.filter(r=>r.name===series[0].name), max=shown.at(-1)?.n;
    $('summary').textContent=`${series[0].name} · indices ${state.start}–${max} · ${shown.length} terms${series.length>1?' · comparison overlaid':''}.`;
    $('window').textContent=`Family limit: ${entry?entry.cap:values.length} terms. Sums and running averages include all terms from index 0, even when the displayed window starts later. Differences and ratios use the preceding term. Plot coordinates are approximate; the table and CSV retain exact values.`;
    const p=candidatePeriod(shown.map(r=>r.residue));
    $('period').textContent=modular?(p?`Residues in this window repeat with candidate period ${p} (at least three repetitions). This finite check does not prove a global period.`:'No period with at least three complete repetitions was found in this residue window.'):'Residue-period suggestions appear in modular views.';
    const tbody=$('values');tbody.replaceChildren();
    for(const r of rows){const tr=document.createElement('tr');for(const value of [r.name,r.n,r.raw,r.value,r.residue??'undefined',r.x??'omitted',r.y??'omitted']){const td=document.createElement('td');td.textContent=String(value);tr.append(td);}tbody.append(tr);}
    $('table-caption').textContent='Exact samples for the current view. Residues apply to the selected transform; plot coordinates are approximate.';
  }catch(error){stopAnimation();message(error.message+(plot?' The last valid plot is retained.':''),true);}
}
function draw(rows,names){
  const W=Math.max(320,Math.round($('plot').clientWidth)),H=W<560?360:480,pad={left:W<560?56:82,right:20,top:names.length>1?90:68,bottom:62}, pw=W-pad.left-pad.right,ph=H-pad.top-pad.bottom;
  const modular=['mod','grid','frequency'].includes(state.view), frequency=state.view==='frequency';
  let points=rows.filter(r=>r.x!==null&&r.y!==null).map(r=>({...r,series:names.indexOf(r.name)}));
  if(frequency){points=[];names.forEach((name,series)=>{const selected=rows.filter(r=>r.name===name);for(let i=0;i<state.modulus;i++)points.push({name,n:i,x:i,y:selected.filter(r=>r.residue===i).length,value:'',raw:'',residue:i,series});});}
  let xs=points.map(r=>r.x),ys=points.map(r=>r.y),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(0,...ys),ymax=Math.max(0,...ys);
  if(state.view==='grid'){xmin=0;xmax=state.modulus-1;ymin=0;ymax=state.modulus-1;}
  if(state.view==='mod'){ymin=0;ymax=state.modulus-1;}
  if(xmin===xmax)xmax=xmin+1;if(ymin===ymax)ymax=ymin+1;
  // Normalize before multiplying to keep very large finite values within range.
  const between=(v,a,b)=>{const scale=Math.max(Math.abs(a),Math.abs(b),1);return (v/scale-a/scale)/(b/scale-a/scale);};
  const x=v=>pad.left+between(v,xmin,xmax)*pw,y=v=>H-pad.bottom-between(v,ymin,ymax)*ph;
  const svg=element('svg',{viewBox:`0 0 ${W} ${H}`,role:'group','aria-labelledby':'sa-svg-title sa-svg-description'});
  svg.append(element('rect',{width:W,height:H,fill:'#fafaf5'}));
  svg.append(element('title',{id:'sa-svg-title'},$('view').selectedOptions[0].textContent));
  svg.append(element('desc',{id:'sa-svg-description'},`Discrete samples for ${names.join(' and ')}. Exact values are in the table below. Focus points to inspect them.`));
  const tick=v=>v===0?'0':Math.abs(v)>=1e6||Math.abs(v)<0.001?v.toExponential(1):Number(v.toPrecision(4)).toString();
  const yTicks=modular?[...new Set(Array.from({length:6},(_,i)=>Math.round((1-i/5)*ymax+(i/5)*ymin)))]:Array.from({length:6},(_,i)=>(1-i/5)*ymax+(i/5)*ymin);
  for(const pyValue of yTicks){
    const py=y(pyValue);
    svg.append(element('line',{x1:pad.left,x2:W-pad.right,y1:py,y2:py,stroke:'#d9dfd4','stroke-width':1}));
    svg.append(element('text',{x:pad.left-10,y:py+4,'text-anchor':'end',fill:'#465347','font-size':12},tick(pyValue)));
  }
  const xTicks=[...new Set(Array.from({length:6},(_,i)=>state.view==='pairs'?(1-i/5)*xmin+(i/5)*xmax:Math.round((1-i/5)*xmin+(i/5)*xmax)))];
  for(const pxValue of xTicks){const px=x(pxValue);
    svg.append(element('text',{x:px,y:H-pad.bottom+24,'text-anchor':'middle',fill:'#465347','font-size':12},tick(pxValue)));
  }
  const xLabel=frequency?'Residue':state.view==='grid'?'n mod m':state.view==='pairs'?'Transformed a(n)':'Index n';
  const yLabel=frequency?'Count in window':state.view==='grid'||state.view==='mod'?'Transformed a(n) mod m':state.view==='pairs'?'Transformed a(n+1)':$('transform').selectedOptions[0].textContent;
  svg.append(element('text',{x:W/2,y:H-12,'text-anchor':'middle',fill:'#243d2d','font-size':14},xLabel));
  const fit=text=>{const limit=Math.floor(pw/7.8);return text.length>limit?text.slice(0,limit-1)+'…':text;};
  names.forEach((name,i)=>svg.append(element('text',{x:pad.left,y:23+i*22,fill:palette[i],'font-size':14},fit((i?'□ ':'● ')+name))));
  svg.append(element('text',{x:pad.left,y:names.length>1?67:45,fill:'#243d2d','font-size':12},fit(yLabel+(modular?` · m = ${state.modulus}`:` · ${$('scale').selectedOptions[0].textContent}`))));
  if(state.marks==='line'&&!frequency&&state.view!=='grid'){
    names.forEach((name,i)=>{let d='',connected=false;for(const r of rows.filter(r=>r.name===name)){if(r.x===null||r.y===null){connected=false;continue;}d+=`${connected?'L':'M'}${x(r.x)},${y(r.y)} `;connected=true;}svg.append(element('path',{d,fill:'none',stroke:palette[i], 'stroke-width':1.6,'stroke-dasharray':i?'6 4':'none'}));});
  }
  // Aggregate grid collisions into count-labelled marks.
  if(state.view==='grid'){
    const groups=new Map();for(const r of points){const key=[r.series,r.x,r.y].join(':');const g=groups.get(key);if(g){g.hits++;}else groups.set(key,{...r,hits:1});}points=[...groups.values()];
  }
  for(const r of points){
    const color=palette[state.color==='value'?Number(BigInt(r.raw||r.residue)%BigInt(state.modulus)+BigInt(state.modulus))%state.modulus%palette.length:state.color==='index'?r.n%state.modulus%palette.length:r.series];
    let mark;const attrs={fill:color,stroke:r.series?'#a44916':color,'stroke-width':1.5};
    if(frequency||state.marks==='bars'&&state.view!=='grid'){
      const width=Math.max(1,Math.min(24,pw/(frequency?state.modulus:rows.length)*0.7));const baseline=y(0);
      mark=element('rect',{x:x(r.x)-width/2+(r.series?width/3:0),y:Math.min(baseline,y(r.y)),width,height:Math.max(1,Math.abs(baseline-y(r.y))),...attrs,opacity:r.series?0.6:0.85});
    }else if(r.series){mark=element('rect',{x:x(r.x)-4,y:y(r.y)-4,width:8,height:8,...attrs,fill:'#fafaf5'});
    }else mark=element('circle',{cx:x(r.x),cy:y(r.y),r:r.hits?Math.min(13,4+Math.log2(r.hits)):4,...attrs});
    const label=frequency?`${r.name}: residue ${r.x}, count ${r.y}`:state.view==='grid'?`${r.name}: residue pair (${r.x}, ${r.y}), ${r.hits} occurrence${r.hits===1?'':'s'}`:`${r.name}: n=${r.n}; a(n)=${r.raw}; transformed=${r.value}${modular?`; residue=${r.residue}`:''}`;
    mark.setAttribute('tabindex','0');mark.setAttribute('aria-label',label);mark.append(element('title',{},label));
    const inspect=()=>{$('inspect').textContent=label;};mark.addEventListener('focus',inspect);mark.addEventListener('pointerenter',inspect);mark.addEventListener('click',inspect);svg.append(mark);
  }
  $('plot').replaceChildren(svg);plot=svg;
  $('caption').textContent=`${names.map((name,i)=>`${i?'Outlined squares / dashed line':'Filled circles / solid line'}: ${name}`).join('. ')}. ${state.color==='series'?'':'Colors cycle through eight colors; exact residue labels are available on each point. '}${frequency?'Bars count residues among the selected samples.':state.view==='grid'?'Larger marks indicate repeated residue pairs.':'Use First index and Terms shown to move or zoom the sample window.'} ${modular?`Modulus ${state.modulus}.`:''} ${rows.filter(r=>r.y===null||r.x===null).length} undefined or out-of-range samples omitted.`;
}
function download(content,type,name){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function viewURL(){const url=new URL(location.href);url.search='';for(const [key,value]of Object.entries(state))url.searchParams.set(key,String(value));if(state.sequence==='custom')url.searchParams.set('terms',$('custom').value);url.hash='explorer';return url.href;}
function search(){try{const matches=findMatches(entries,$('query').value,$('filter').value),ids=new Set(matches.map(e=>e.id));document.querySelectorAll('[data-sequence]').forEach(card=>{card.hidden=!ids.has(card.dataset.sequence);});$('search-status').textContent=`${matches.length} of ${entries.length} entries. Term searches cover 64 recorded terms per entry; this search does not query the full OEIS database.`;}catch(error){$('search-status').textContent=error.message;}}
async function init(){
  const response=await fetch(new URL('./sequence-atlas-data.json',import.meta.url));if(!response.ok)throw Error('Catalogue data could not be loaded.');data=await response.json();entries=data.entries;
  const params=new URL(location.href).searchParams;
  if(params.has('seq')&&!params.has('sequence'))params.set('sequence',params.get('seq'));
  for(const id of ids){if(params.has(id))$(id).value=params.get(id);else $(id).value=defaults[id];}
  if(params.has('terms')){$('custom').value=params.get('terms');}
  $('workspace').hidden=false;$('search-controls').hidden=false;$('loading').hidden=true;
  document.querySelectorAll('[data-load]').forEach(button=>{button.hidden=false;button.addEventListener('click',()=>{stopAnimation();$('sequence').value=button.dataset.load;$('start').value=0;$('count').value=32;render();document.getElementById('explorer-title').focus({preventScroll:true});document.getElementById('explorer').scrollIntoView({block:'start',behavior:'auto'});});});
  ids.forEach(id=>$(id).addEventListener('change',()=>{stopAnimation();render();}));
  $('sequence').addEventListener('change',()=>{const entry=known($('sequence').value);if(entry&&Number($('start').value)>=entry.cap-1)$('start').value=0;render();});
  for(const id of ['N','power'])$(id).addEventListener('change',()=>{const match=entries.find(e=>e.kind==='reciprocal'&&e.N===Number($('N').value)&&e.power===Number($('power').value));if(match){$('sequence').value=match.id;render();}});
  $('custom').addEventListener('input',()=>{if($('sequence').value==='custom')render();});
  $('query').addEventListener('input',search);$('filter').addEventListener('change',search);
  $('animate').addEventListener('click',()=>{if(timer)return stopAnimation();if(!['mod','grid','frequency'].includes($('view').value))$('view').value='mod';$('animate').textContent='Stop animation';$('animate').setAttribute('aria-pressed','true');render();timer=setInterval(()=>{$('modulus').value=Number($('modulus').value)>=32?2:Number($('modulus').value)+1;render();},800);});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopAnimation();});
  $('reset').addEventListener('click',()=>{stopAnimation();ids.forEach(id=>$(id).value=defaults[id]);render();});
  $('share').addEventListener('click',async()=>{const url=viewURL();try{await navigator.clipboard.writeText(url);message('View link copied.');}catch{$('share-fallback').hidden=false;$('share-link').value=url;$('share-link').select();message('Copy the view link from the field below the toolbar.');}});
  $('csv').addEventListener('click',()=>{const csv='sequence,n,a_n,transformed,residue,plot_x,plot_y,modulus,transform,view,scale\n'+lastRows.map(r=>[r.name,r.n,r.raw,r.value,r.residue??'',r.x??'',r.y??'',state.modulus,state.transform,state.view,state.scale].map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\n')+'\n';download(csv,'text/csv;charset=utf-8','komorebi-sequence-exact.csv');});
  $('svg').addEventListener('click',()=>{if(plot)download(new XMLSerializer().serializeToString(plot),'image/svg+xml','komorebi-sequence.svg');});
  $('png').addEventListener('click',()=>{if(!plot)return;const source=new Blob([new XMLSerializer().serializeToString(plot)],{type:'image/svg+xml'}),url=URL.createObjectURL(source),img=new Image();img.onload=()=>{const canvas=document.createElement('canvas');canvas.width=plot.viewBox.baseVal.width*2;canvas.height=plot.viewBox.baseVal.height*2;canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);URL.revokeObjectURL(url);canvas.toBlob(blob=>{if(blob)download(blob,'image/png','komorebi-sequence.png');},'image/png');};img.onerror=()=>{URL.revokeObjectURL(url);message('PNG export failed. SVG export remains available.',true);};img.src=url;});
  render();search();
  let observedWidth=$('plot').clientWidth;
  new ResizeObserver(()=>{const width=$('plot').clientWidth;if(Math.abs(width-observedWidth)>2&&lastRows.length){observedWidth=width;draw(lastRows,[...new Set(lastRows.map(r=>r.name))]);}}).observe($('plot'));
}
init().catch(error=>{$('loading').textContent='The interactive explorer could not load. Read the catalogue and term pages below. '+error.message;});
