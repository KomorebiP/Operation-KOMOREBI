import './sequence-reading-theme.mjs';
import {enhanceMath,clearMath} from './math-display.mjs';
import {searchEntries} from './sequence-atlas-search.mjs';
import {setupArchivePlot} from './sequence-archive-plot.mjs';
import {referenceQuery} from './sequence-oeis-core.mjs';
import {createReferenceClient} from './sequence-oeis-client.mjs';
import {mountWorkbench} from './sequence-workbench.mjs';
import {STORAGE_KEY,readSaved,writeSaved,updateSaveButtons} from './sequence-atlas-saved.mjs';

const root=document.querySelector('[data-library]'),$=id=>document.getElementById('sl-'+id),make=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
const collectionLabels={atlas:'Curated sequences',recovered:'Research archive',formulas:'Formula families'};
const keys=['q','collection','kind','representation','status','match','sort','hits','saved'];
let results=[],page=0,applied={},workbench,toggleSaved,saved=new Set();
const csv=rows=>rows.map(row=>row.map(value=>'"'+String(value??'').replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
function save(content,type,name){const url=URL.createObjectURL(new Blob([content],{type})),link=make('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function share(){const url=new URL(location.href);url.search='';for(const [key,value]of Object.entries(applied))if(value&&value!=='any'&&value!=='relevance')url.searchParams.set(key,value);if(page)url.searchParams.set('page',String(page+1));url.hash='library-search';return url.href;}
function render(){
  clearMath($('results'));$('results').replaceChildren();page=Math.max(0,Math.min(page,Math.ceil(results.length/24)-1));
  for(const hit of results.slice(page*24,(page+1)*24)){
    const entry=hit.entry,li=make('li'),label=make('p',entry.id+' / '+(collectionLabels[entry.collection]||'Sequence library'));label.className='sar-kicker';const heading=make('h3'),link=make('a',entry.title);link.href=entry.url;heading.append(link);li.append(label,heading,make('p',entry.kind+' · '+entry.formulas.length+' representations · first index '+entry.offset));
    li.dataset.resultId=entry.id;if(entry.triangle){const tableNote=make('p',`${entry.triangle.row_lengths.length} complete rows · row/column inspection · ${entry.terms.length} exact coefficients`);tableNote.className='sl-match-reason';li.append(tableNote);}
    const expression=make('p',entry.formula);expression.className='sar-formula';li.append(expression);
    const start=hit.termMatch?Math.max(0,hit.termMatch.start-(hit.termMatch.length<8?1:0)):0,count=Math.min(Math.max(6,hit.termMatch?.length||0),8),values=entry.terms.slice(start,start+count),symbol=entry.index_symbol||'n';
    const excerpt=make('div'),caption=make('p',`${symbol} = ${entry.offset+start}–${entry.offset+start+values.length-1} · exact stored terms`),terms=make('div');excerpt.className='sl-term-preview';caption.className='sl-term-caption';terms.className='sl-term-values';terms.tabIndex=0;terms.setAttribute('role','region');terms.setAttribute('aria-label',`Exact term preview for ${entry.id}`);
    values.forEach((value,i)=>{if(i)terms.append(document.createTextNode(', '));const relative=start+i-(hit.termMatch?.start??-1),matched=hit.termMatch&&relative>=0&&relative<hit.termMatch.length&&hit.termMatch.pattern[relative]!==null;const item=make(matched?'mark':'span',value);item.title=`${symbol}=${entry.offset+start+i}`;terms.append(item);});excerpt.append(caption,terms);li.append(excerpt);
    if(hit.termMatch){const reason=make('p',hit.reason);reason.className='sl-match-reason';li.append(reason);}
    const review=make('p',entry.status);review.className='sl-result-status';li.append(review);
    if(entry.tags.includes('hypergeometric')){const badge=make('span','Hypergeometric representation');badge.className='sl-result-badge';li.append(badge);}
    const links=make('div'),plot=make('a','Plot and inspect →'),formulas=make('a','Read formulas'),bookmark=make('button'),compare=make('button','Add to comparison');links.className='sp-actions';plot.href=entry.url+(entry.collection==='atlas'?'#analysis':'#plot');formulas.href=entry.url+(entry.collection==='recovered'?'#definition':'#formulas');bookmark.type=compare.type='button';bookmark.dataset.saveSequence=entry.id;bookmark.addEventListener('click',()=>toggleSaved(entry.id));compare.setAttribute('aria-label','Add '+entry.id+' to comparison');compare.addEventListener('click',()=>workbench.addLocal(entry));links.append(plot,formulas,bookmark,compare);li.append(links);
    const comparisons=make('details'),summary=make('summary',`OEIS comparisons (${entry.match_count.toLocaleString()} ${entry.match_count===1?'match':'matches'})`);comparisons.className='sl-matches';comparisons.append(summary);
    if(entry.matches.length){const list=make('ol');for(const hit of entry.matches.slice(0,3)){const item=make('li'),reference=make('a',hit.id+' · '+hit.name);reference.href='https://oeis.org/'+hit.id;item.append(reference,make('p',`${hit.matched_terms} matching terms, beginning at local index ${entry.offset}; OEIS export position ${hit.position}.`));list.append(item);}comparisons.append(list,make('p',`Showing ${Math.min(3,entry.matches.length)} of ${entry.match_count.toLocaleString()} observed hits; up to 50 are retained in the library data.`));}else comparisons.append(make('p','No eight-term contiguous match recorded. This does not establish novelty.'));
    const credit=make('p','Finite comparisons do not prove infinite identity. Export positions are not mathematical offsets. Reference data: '),oeis=make('a','The Online Encyclopedia of Integer Sequences'),license=make('a','CC BY-SA 4.0');oeis.href='https://oeis.org/';license.href='https://creativecommons.org/licenses/by-sa/4.0/';credit.append(oeis,document.createTextNode(' · '),license);comparisons.append(credit);li.append(comparisons);$('results').append(li);
  }
  enhanceMath($('results'));
  const active=$('active-filters');active.replaceChildren();
  const names={collection:'Collection',kind:'Family',representation:'Formula type',status:'Review status',hits:'OEIS comparisons',saved:'Saved entries',match:'Term matching'};
  for(const key of Object.keys(names))if(applied[key]&&!(key==='match'&&applied[key]==='any')){const field=$(key),text=field.options[field.selectedIndex]?.textContent||applied[key],button=make('button',`${names[key]}: ${text} ×`);button.type='button';button.className='sl-filter-chip';button.setAttribute('aria-label',`Clear ${names[key].toLowerCase()} filter`);button.addEventListener('click',()=>{field.value=key==='match'?'any':'';field.dispatchEvent(new Event('change'));$('count').focus({preventScroll:true});});active.append(button);}
  root.querySelectorAll('[data-collection]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.collection===applied.collection)));
  updateSaveButtons($('results'),saved);$('results').start=page*24+1;$('count').textContent=`${results.length.toLocaleString()} matching record${results.length===1?'':'s'}. ${results.length?`Showing ${page*24+1}–${Math.min(results.length,(page+1)*24)}.`:applied.saved?'Save entries from any collection to find them here.':'Try fewer words or another formula type.'}`;$('page').textContent=`Page ${page+1} of ${Math.max(1,Math.ceil(results.length/24))}`;$('previous').disabled=page===0;$('next').disabled=(page+1)*24>=results.length;$('pages').hidden=results.length<=24;
}
function setupSearch(entries){
  const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value)},allowed=new Set(entries.map(e=>e.id)),loaded=readSaved(storage,allowed);saved=new Set(loaded.ids);
  const label=make('label','Saved entries'),select=make('select');select.id='sl-saved';label.htmlFor=select.id;for(const [value,text]of [['','All entries'],['only','Saved in this browser']]){const option=make('option',text);option.value=value;select.append(option);}label.append(select);$('search').querySelector('.sar-controls').append(label);
  const note=make('p',loaded.available?'Save up to 500 records in this browser, across all collections.':'Saved entries could not be read. Saving still works for this session.');note.id='sl-saved-status';note.setAttribute('role','status');$('search').append(note);
  const params=new URL(location.href).searchParams;for(const key of keys){const control=$(key==='q'?'query':key);if(params.has(key))control.value=params.get(key);}page=Math.max(0,(Number(params.get('page'))||1)-1);
  function run(update=false){try{const state=Object.fromEntries(keys.map(key=>[key,$(key==='q'?'query':key).value]));const found=searchEntries(entries,state.q,{sort:state.sort,match:state.match}).filter(({entry})=>(!state.collection||entry.collection===state.collection)&&(!state.kind||entry.kind===state.kind)&&(!state.representation||entry.formulas.some(f=>f.kind===state.representation))&&(!state.status||entry.status===state.status)&&(!state.hits||(state.hits==='matched')===Boolean(entry.matches.length))&&(!state.saved||saved.has(entry.id)));results=found;applied=state;if(update)page=0;render();$('error').hidden=true;$('action-status').textContent='';$('query').removeAttribute('aria-invalid');if(update)history.replaceState(null,'',share());}catch(error){$('error').textContent=error.message;$('error').hidden=false;$('query').setAttribute('aria-invalid','true');}}
  toggleSaved=id=>{const next=new Set(saved);if(next.has(id))next.delete(id);else if(next.size>=500){note.textContent='You have 500 saved records. Remove one before saving another.';return;}else next.add(id);saved=next;const stored=writeSaved(storage,[...saved],allowed);note.textContent=(saved.has(id)?id+' saved.':id+' removed from saved entries.')+(stored?'':' Browser storage is unavailable; this change lasts for this session.');if(applied.saved){run();$('count').focus({preventScroll:true});}else updateSaveButtons($('results'),saved);};
  $('count').tabIndex=-1;for(const key of keys.filter(key=>key!=='q'))$(key).addEventListener('change',()=>run(true));
  for(const button of root.querySelectorAll('[data-collection]'))button.addEventListener('click',()=>{$('collection').value=button.dataset.collection;run(true);});
  window.addEventListener('storage',event=>{if(event.key===STORAGE_KEY||event.key===null){saved=new Set(readSaved(storage,allowed).ids);run();}});
  $('search').hidden=false;$('search').addEventListener('submit',event=>{event.preventDefault();run(true);});
  $('clear').addEventListener('click',()=>{for(const key of keys)$(key==='q'?'query':key).value=key==='sort'?'relevance':key==='match'?'any':'';run(true);$('query').focus();});
  $('triangles').hidden=false;$('triangles').addEventListener('click',()=>{for(const key of keys)$(key==='q'?'query':key).value=key==='sort'?'relevance':key==='match'?'any':'';$('query').value='tag:triangle';run(true);$('count').focus();$('count').scrollIntoView({block:'start'});});
  $('research').hidden=false;$('research').addEventListener('click',()=>{for(const key of keys)$(key==='q'?'query':key).value=key==='sort'?'relevance':key==='match'?'any':'';$('query').value='tag:research-derived';run(true);$('count').focus();$('count').scrollIntoView({block:'start'});});
  for(const [key,step]of [['previous',-1],['next',1]])$(key).addEventListener('click',()=>{page+=step;render();history.replaceState(null,'',share());$('count').scrollIntoView({block:'nearest'});});
  $('share').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(share());$('action-status').textContent='Search link copied.';}catch{$('link-wrap').hidden=false;$('link').value=share();$('link').focus();$('link').select();}});
  $('export').addEventListener('click',()=>save(csv([['id','title','family','collection','offset','formulas','url'],...results.map(({entry:e})=>[e.id,e.title,e.kind,e.collection,e.offset,e.formulas.length,new URL(e.url,location.href).href])]),'text/csv;charset=utf-8','sequence-search-results.csv'));
  run();
}
function setupTriangleNavigation(){
  const table=root.querySelector('#triangle table');if(!table)return;
  const rows=[...table.tBodies[0].rows].map(row=>[...row.querySelectorAll('td a')]);
  const all=rows.flat();let active=all[0];
  for(const [n,row]of rows.entries())for(const [k,link]of row.entries()){
    const exact=link.textContent,digits=exact.replace('-',''),spoken=digits.length>60?`${exact.startsWith('-')?'negative ':''}${digits.length} digits, beginning ${digits.slice(0,12)}, ending ${digits.slice(-8)}`:exact;
    link.tabIndex=link===active?0:-1;link.setAttribute('aria-label',`Row ${n}, column ${k}; coefficient ${spoken}`);
    link.addEventListener('focus',()=>{if(active)active.tabIndex=-1;active=link;link.tabIndex=0;});
    link.addEventListener('keydown',event=>{
      let r=n,c=k;if(event.key==='ArrowDown')r=Math.min(rows.length-1,n+1);else if(event.key==='ArrowUp')r=Math.max(0,n-1);else if(event.key==='ArrowRight')c=Math.min(row.length-1,k+1);else if(event.key==='ArrowLeft')c=Math.max(0,k-1);else if(event.key==='Home'){r=event.ctrlKey?0:n;c=0;}else if(event.key==='End'){r=event.ctrlKey?rows.length-1:n;c=rows[r].length-1;}else return;
      event.preventDefault();rows[r][Math.min(c,rows[r].length-1)].focus();
    });
  }
  root.querySelector('.sl-triangle-help').hidden=false;table.dataset.keyboardReady='true';
}
function setupReference(client){
  if(!globalThis.Worker){$('oeis-status').textContent='Interactive OEIS search is unavailable in this browser. You can still download the reference data and browse entry comparisons.';return;}
  $('oeis-form').hidden=false;
  const busy=value=>{$('oeis-search').disabled=value;$('oeis-cancel').disabled=!value;};
  $('oeis-form').addEventListener('submit',async event=>{
    event.preventDefault();try{referenceQuery($('oeis-query').value);}catch(error){$('oeis-status').textContent=error.message;return;}
    busy(true);$('oeis-status').textContent='Loading OEIS reference data and searching in this browser…';root.dataset.referenceReady='false';
    try{
      const data=await client.search($('oeis-query').value,message=>{$('oeis-status').textContent=message;});
      $('oeis-results').replaceChildren();for(const hit of data.results){
        const li=make('li'),link=make('a',hit.id+' · '+(hit.name||'Name not recorded'));link.href='https://oeis.org/'+hit.id;
        li.append(link,make('p',hit.position===null?'Terms from the exported excerpt; its mathematical offset is not included.':`Pattern at excerpt position ${hit.position}; ${hit.matched_terms} pattern positions (${hit.known_terms} known integers); ${hit.positions} matching position(s) in this excerpt.`));
        const values=make('p',(hit.values||[]).join(', '));values.className='sar-formula';li.append(values);
        if(hit.values?.length){const compare=make('button','Add excerpt to comparison');compare.type='button';compare.setAttribute('aria-label','Compare '+hit.id+' excerpt');compare.addEventListener('click',()=>workbench.addReference(hit));li.append(compare);}
        $('oeis-results').append(li);
      }
      $('oeis-status').textContent=`${data.total.toLocaleString()} matching OEIS records. Showing ${data.results.length}; reference terms and names only. ${data.query_type==='terms'?'Finite matching does not prove sequence identity.':''}`;root.dataset.referenceReady='true';
    }catch(error){$('oeis-status').textContent=error.message;}finally{busy(false);}
  });
  $('oeis-cancel').addEventListener('click',()=>client.cancel());
}
try{
  if(root.dataset.entry){const response=await fetch(new URL(root.dataset.entry,location.href));if(!response.ok)throw Error('The exact record could not load.');setupArchivePlot(await response.json());setupTriangleNavigation();}
  else if($('search')){const response=await fetch(new URL('./sequence-library-data.json',import.meta.url));if(!response.ok)throw Error('The local catalogue could not load.');const data=await response.json(),client=createReferenceClient();workbench=mountWorkbench({root,entries:data.entries,snapshot:data.snapshot.stripped_sha256,referenceClient:client});setupSearch(data.entries);setupReference(client);}
  root.dataset.libraryReady='true';
}catch(error){const note=make('p',error.message+' Static definitions, exact tables, and the complete index remain available.');note.setAttribute('role','status');root.prepend(note);}
