import {searchEntries} from './sequence-atlas-search.mjs';
import {archiveWindow,archiveLink,windowCSV} from './sequence-archive-core.mjs';

const $=id=>document.getElementById('sar-'+id),root=document.querySelector('[data-archive]');
const make=(tag,text)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el;};
const svg=(tag,attrs,text)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,val]of Object.entries(attrs))el.setAttribute(key,String(val));if(text!==undefined)el.textContent=text;return el;};
const params=new URL(location.href).searchParams;
async function copy(href,status,wrapper,field) {
  try {await navigator.clipboard.writeText(href);status.textContent='Link copied.';}
  catch {wrapper.hidden=false;field.value=href;field.focus();field.select();status.textContent='Copy the selected link.';}
}

function setupSearch(entries) {
  const cards=new Map([...root.querySelectorAll('[data-record]')].map(el=>[el.dataset.record,el]));
  for(const key of ['query','family','review','sort','match'])if(params.has(key))$(key).value=params.get(key);
  let applied={};
  function run(update=false) {
    try {
      const filters={query:$('query').value,family:$('family').value,review:$('review').value,sort:$('sort').value,match:$('match').value};
      const found=searchEntries(entries,filters.query,{sort:filters.sort,match:filters.match}).filter(({entry})=>(!filters.family||entry.kind===filters.family)&&(!filters.review||entry.classification===filters.review));
      for(const card of cards.values())card.hidden=true;
      for(const hit of found) {
        const card=cards.get(hit.entry.id);card.hidden=false;$('records').append(card);
        const note=card.querySelector('.sar-match');note.hidden=!hit.termMatch;
        if(hit.termMatch)note.textContent=hit.reason;
      }
      $('error').hidden=true;$('query').removeAttribute('aria-invalid');
      $('count').textContent=`${found.length} of ${entries.length} recovered records. Matches use all stored exact terms and preserve each record's offset.`;
      $('empty').hidden=found.length!==0;applied=filters;
      if(update)history.replaceState(null,'',archiveLink(location.href,applied));
    }catch(error){$('error').textContent=error.message;$('error').hidden=false;$('query').setAttribute('aria-invalid','true');}
  }
  $('search').hidden=false;
  $('search').addEventListener('submit',event=>{event.preventDefault();run(true);});
  $('clear').addEventListener('click',()=>{for(const key of ['query','family','review'])$(key).value='';$('sort').value='id';$('match').value='any';run(true);$('query').focus();});
  $('share').addEventListener('click',()=>copy(archiveLink(location.href,applied),$('count'),$('share-fallback'),$('share-value')));
  run();
}

function setupPlot(entry) {
  const keys=['view','scale','start','size','mod'];let current;
  function point(row){$('point').textContent=`Index ${row.n}: a(${row.n}) = ${row.raw}; plotted value ${row.value??'undefined'}${row.next===null?'':`; following residue ${row.next}`}.`;}
  function draw(result) {
    const valid=result.rows.filter(row=>Number.isFinite(row.x)&&Number.isFinite(row.y));
    const width=Math.max(270,Math.min(760,$('plot').clientWidth||760)),right=width-20;
    const picture=svg('svg',{viewBox:`0 0 ${width} 360`,role:'group','aria-labelledby':'sar-plot-title sar-plot-desc'});
    picture.append(svg('title',{id:'sar-plot-title'},entry.title+' — '+result.state.view),svg('desc',{id:'sar-plot-desc'},'Discrete samples from the recorded exact data. Focus points for exact values.'));
    if(valid.length) {
      let minX=Math.min(...valid.map(r=>r.x)),maxX=Math.max(...valid.map(r=>r.x)),minY=Math.min(0,...valid.map(r=>r.y)),maxY=Math.max(...valid.map(r=>r.y));
      if(minX===maxX){minX-=1;maxX+=1;}if(minY===maxY){minY-=1;maxY+=1;}
      // Normalize before multiplying so extreme finite values cannot overflow.
      const unit=Math.max(Math.abs(minY),Math.abs(maxY),1),lo=minY/unit,hi=maxY/unit;
      const xx=v=>65+(v-minX)/(maxX-minX)*(right-65),yy=v=>305-(v/unit-lo)/(hi-lo)*260;
      picture.append(svg('path',{d:`M65 35V305H${right}`,class:'sar-axis'}));
      for(let k=0;k<=4;k++){const y=lo+(hi-lo)*k/4;picture.append(svg('text',{x:57,y:yy(y*unit)+4,'text-anchor':'end'},Number(y*unit).toPrecision(3)));}
      picture.append(svg('text',{x:65,y:327},String(minX)),svg('text',{x:right,y:327,'text-anchor':'end'},String(maxX)),svg('text',{x:(65+right)/2,y:350,'text-anchor':'middle'},result.state.view==='pairs'?`a(${entry.index_symbol}) mod m`:`Sequence index ${entry.index_symbol}`));
      for(const [i,row]of valid.entries()) {
        const dot=svg('circle',{cx:xx(row.x),cy:yy(row.y),r:4.8,tabindex:i===0?'0':'-1',role:'button','aria-label':`Index ${row.n}; exact value ${row.value}${row.next===null?'':`; following residue ${row.next}`}`});
        dot.append(svg('title',{},`n=${row.n}: ${row.value}`));
        dot.addEventListener('focus',()=>point(row));dot.addEventListener('click',()=>{for(const d of picture.querySelectorAll('circle'))d.setAttribute('tabindex','-1');dot.setAttribute('tabindex','0');dot.focus();point(row);});
        dot.addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const dots=[...picture.querySelectorAll('circle')],at=event.key==='Home'?0:event.key==='End'?dots.length-1:Math.max(0,Math.min(dots.length-1,i+(event.key==='ArrowLeft'?-1:1)));dot.setAttribute('tabindex','-1');dots[at].setAttribute('tabindex','0');dots[at].focus();}else if(event.key==='Enter'||event.key===' '){event.preventDefault();point(row);}});
        picture.append(dot);
      }
    }else picture.append(svg('text',{x:35,y:150},'No defined coordinates in this window. Try a different range or scale.'));
    $('plot').replaceChildren(picture);
    const table=$('window-values');table.replaceChildren();for(const row of result.rows){const tr=make('tr');for(const v of [row.n,row.raw,row.value??'undefined',row.next??'—'])tr.append(make('td',v));table.append(tr);}
    $('window').textContent=`${result.rows.length} index positions, ${valid.length} plotted points; indices ${result.state.start}–${result.state.start+result.state.size-1}. Stored range ${entry.offset}–${entry.offset+entry.terms.length-1}.`;
  }
  function run(update=false) {
    try {
      const result=archiveWindow(entry,Object.fromEntries(keys.map(key=>[key,$(key).value])));current=result;draw(result);
      $('plot-error').hidden=true;for(const key of keys)$(key).removeAttribute('aria-invalid');
      if(update)history.replaceState(null,'',archiveLink(location.href,result.state,'plot'));
    }catch(error){$('plot-error').textContent=error.message+' The previous plot remains available.';$('plot-error').hidden=false;if(error.field){$(error.field).setAttribute('aria-invalid','true');if(update)$(error.field).focus();}}
  }
  for(const key of keys)if(params.has(key))$(key).value=params.get(key);
  $('explorer').hidden=false;$('static-note').hidden=true;
  $('plot-form').addEventListener('submit',event=>{event.preventDefault();run(true);});
  $('view-link').addEventListener('click',()=>{if(current)copy(archiveLink(location.href,current.state,'plot'),$('window'),$('plot-fallback'),$('plot-link'));});
  $('export').addEventListener('click',()=>{if(!current)return;const url=URL.createObjectURL(new Blob([windowCSV(current.rows,entry.index_symbol)],{type:'text/csv;charset=utf-8'})),a=make('a');a.href=url;a.download=entry.id+'-'+current.state.view+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  function inspect(){const value=$('inspect').value,n=Number(value),i=n-entry.offset;if(!value.trim()||!Number.isSafeInteger(n)||i<0||i>=entry.terms.length){$('inspect').setAttribute('aria-invalid','true');$('exact').textContent=`Choose a stored index from ${entry.offset} through ${entry.offset+entry.terms.length-1}.`;return;}$('inspect').removeAttribute('aria-invalid');$('exact').replaceChildren(make('strong',`a(${n}) = `),make('code',entry.terms[i]));}
  $('inspect').addEventListener('input',inspect);inspect();run();
  let observedWidth=$('plot').clientWidth;
  new ResizeObserver(()=>{const width=$('plot').clientWidth;if(width!==observedWidth){observedWidth=width;if(current)draw(current);}}).observe($('plot'));
  if(!current){for(const key of keys)if(params.has(key))$(key).value=({view:'mod',scale:'signed-log',start:entry.offset,size:Math.min(32,entry.terms.length),mod:7})[key];run();$('plot-error').hidden=false;$('plot-error').textContent='Invalid plot options in this link. Showing the first recorded window.';}
}

try {
  const response=await fetch(new URL('./sequence-archive-data.json',import.meta.url));if(!response.ok)throw Error('Archive data could not be loaded.');const {entries}=await response.json();
  if($('search'))setupSearch(entries);
  const selected=root.querySelector('[data-archive-id]');if(selected)setupPlot(entries.find(x=>x.id===selected.dataset.archiveId));
  root.dataset.archiveReady='true';
}catch(error){const note=make('p','Interactive tools could not load. All definitions, exact tables, and downloads remain available. '+error.message);note.setAttribute('role','status');root.prepend(note);}
