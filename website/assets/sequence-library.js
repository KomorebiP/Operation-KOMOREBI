import {searchEntries} from './sequence-atlas-search.mjs';
import {setupArchivePlot} from './sequence-archive-plot.mjs';
import {referenceQuery} from './sequence-oeis-core.mjs';

const root=document.querySelector('[data-library]'),$=id=>document.getElementById('sl-'+id),make=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
const keys=['q','collection','kind','representation','match','sort','hits'];
let results=[],page=0,applied={},worker;
const csv=rows=>rows.map(row=>row.map(value=>'"'+String(value??'').replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
function save(content,type,name){const url=URL.createObjectURL(new Blob([content],{type})),link=make('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function share(){const url=new URL(location.href);url.search='';for(const [key,value]of Object.entries(applied))if(value&&value!=='any'&&value!=='relevance')url.searchParams.set(key,value);if(page)url.searchParams.set('page',String(page+1));url.hash='library-search';return url.href;}
function render(){
  $('results').replaceChildren();page=Math.max(0,Math.min(page,Math.ceil(results.length/24)-1));
  for(const hit of results.slice(page*24,(page+1)*24)){
    const entry=hit.entry,li=make('li'),label=make('p',entry.id+' / '+entry.collection);label.className='sar-kicker';const heading=make('h3'),link=make('a',entry.title);link.href=entry.url;heading.append(link);li.append(label,heading,make('p',entry.kind+' · '+entry.formulas.length+' representations · first index '+entry.offset));
    const expression=make('p',entry.formula);expression.className='sar-formula';li.append(expression,make('p',hit.termMatch?hit.reason:entry.tags.filter(x=>x==='hypergeometric').length?'Includes a hypergeometric representation.':entry.status));
    const links=make('div'),plot=make('a','Plot and inspect →'),formulas=make('a','Read formulas');links.className='sp-actions';plot.href=entry.url+(entry.collection==='atlas'?'#analysis':'#plot');formulas.href=entry.url+'#formulas';links.append(plot,formulas);li.append(links);$('results').append(li);
  }
  $('results').start=page*24+1;$('count').textContent=`${results.length.toLocaleString()} matching local records. ${results.length?`Showing ${page*24+1}–${Math.min(results.length,(page+1)*24)}.`:'Try fewer words or another formula type.'}`;$('page').textContent=`Page ${page+1} of ${Math.max(1,Math.ceil(results.length/24))}`;$('previous').disabled=page===0;$('next').disabled=(page+1)*24>=results.length;$('pages').hidden=results.length<=24;
}
function setupSearch(entries){
  const params=new URL(location.href).searchParams;for(const key of keys){const control=$(key==='q'?'query':key);if(params.has(key))control.value=params.get(key);}page=Math.max(0,(Number(params.get('page'))||1)-1);
  function run(update=false){try{const state=Object.fromEntries(keys.map(key=>[key,$(key==='q'?'query':key).value]));const found=searchEntries(entries,state.q,{sort:state.sort,match:state.match}).filter(({entry})=>(!state.collection||entry.collection===state.collection)&&(!state.kind||entry.kind===state.kind)&&(!state.representation||entry.formulas.some(f=>f.kind===state.representation))&&(!state.hits||(state.hits==='matched')===Boolean(entry.matches.length)));results=found;applied=state;if(update)page=0;render();$('error').hidden=true;$('query').removeAttribute('aria-invalid');if(update)history.replaceState(null,'',share());}catch(error){$('error').textContent=error.message;$('error').hidden=false;$('query').setAttribute('aria-invalid','true');}}
  $('search').hidden=false;$('search').addEventListener('submit',event=>{event.preventDefault();run(true);});
  $('clear').addEventListener('click',()=>{for(const key of keys)$(key==='q'?'query':key).value=key==='sort'?'relevance':key==='match'?'any':'';run(true);$('query').focus();});
  for(const [key,step]of [['previous',-1],['next',1]])$(key).addEventListener('click',()=>{page+=step;render();history.replaceState(null,'',share());$('count').scrollIntoView({block:'nearest'});});
  $('share').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(share());$('count').textContent='Search link copied.';}catch{$('link-wrap').hidden=false;$('link').value=share();$('link').focus();$('link').select();}});
  $('export').addEventListener('click',()=>save(csv([['id','title','family','collection','offset','formulas','url'],...results.map(({entry:e})=>[e.id,e.title,e.kind,e.collection,e.offset,e.formulas.length,new URL(e.url,location.href).href])]),'text/csv;charset=utf-8','sequence-search-results.csv'));
  run();
}
function setupReference(){
  if(!globalThis.Worker){$('oeis-status').textContent='Background workers are unavailable. The snapshot downloads and recorded entry comparisons remain available.';return;}
  $('oeis-form').hidden=false;
  const busy=value=>{$('oeis-search').disabled=value;$('oeis-cancel').disabled=!value;};
  $('oeis-form').addEventListener('submit',event=>{event.preventDefault();try{referenceQuery($('oeis-query').value);}catch(error){$('oeis-status').textContent=error.message;return;}if(!worker){worker=new Worker(new URL('./sequence-oeis-worker.mjs',import.meta.url),{type:'module'});worker.onmessage=event=>{const data=event.data;if(data.type==='progress'){$('oeis-status').textContent=data.message;return;}busy(false);if(data.type==='error'){$('oeis-status').textContent=data.message;return;}$('oeis-results').replaceChildren();for(const hit of data.results){const li=make('li'),link=make('a',hit.id+' · '+(hit.name||'Name not recorded'));link.href='https://oeis.org/'+hit.id;li.append(link,make('p',hit.position===null?'Terms from the exported excerpt; its mathematical offset is not included.':`Pattern at excerpt position ${hit.position}; ${hit.matched_terms} pattern positions (${hit.known_terms} known integers); ${hit.positions} matching position(s) in this excerpt.`));const values=make('p',(hit.values||[]).join(', '));values.className='sar-formula';li.append(values);$('oeis-results').append(li);}$('oeis-status').textContent=`${data.total.toLocaleString()} matching OEIS records. Showing ${data.results.length}; snapshot terms and names only. ${data.query_type==='terms'?'Finite matching does not prove sequence identity.':''}`;root.dataset.referenceReady='true';};worker.onerror=()=>{busy(false);$('oeis-status').textContent='Reference matching could not start. The bulk downloads and recorded comparisons remain available.';worker.terminate();worker=null;};}busy(true);$('oeis-status').textContent='Loading the retained snapshot and comparing in this browser…';root.dataset.referenceReady='false';worker.postMessage({type:'search',query:$('oeis-query').value});});
  $('oeis-cancel').addEventListener('click',()=>{worker?.terminate();worker=null;busy(false);$('oeis-status').textContent='Reference search cancelled. Existing results remain available.';});
}
try{
  if(root.dataset.entry){const response=await fetch(new URL(root.dataset.entry,location.href));if(!response.ok)throw Error('The exact record could not load.');setupArchivePlot(await response.json());}
  else if($('search')){const response=await fetch(new URL('./sequence-library-data.json',import.meta.url));if(!response.ok)throw Error('The local catalogue could not load.');setupSearch((await response.json()).entries);setupReference();}
  root.dataset.libraryReady='true';
}catch(error){const note=make('p',error.message+' Static definitions, exact tables, and the complete index remain available.');note.setAttribute('role','status');root.prepend(note);}
