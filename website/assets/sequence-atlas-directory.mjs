import {searchEntries} from './sequence-atlas-search.mjs';

export const DIRECTORY_DEFAULTS={query:'',topic:'',order:'name',connected:false};
const keys={'index-query':'query','index-topic':'topic','index-order':'order','index-connected':'connected'};
export function selectDirectory(entries,options={}){
  const state={...DIRECTORY_DEFAULTS,...options};
  if(!['name','id'].includes(state.order))throw Error('Choose alphabetical or identifier order.');
  if(state.topic&&!entries.some(entry=>entry.tags.includes(state.topic)&&!state.topic.startsWith('N=')&&!state.topic.startsWith('r=')))throw Error('Choose a listed topic.');
  if(typeof state.connected!=='boolean')throw Error('Choose a valid connection filter.');
  const linked=new Set();for(const entry of entries)for(const link of entry.connections){linked.add(entry.id);linked.add(link.id);}
  const results=searchEntries(entries,state.query,{topic:state.topic,sort:state.order}).map(hit=>hit.entry).filter(entry=>!state.connected||linked.has(entry.id));
  return {state,entries:results};
}
export function readDirectoryURL(href,entries){
  const url=new URL(href),state={...DIRECTORY_DEFAULTS};
  for(const [key,name]of Object.entries(keys))if(url.searchParams.has(key)){
    const value=url.searchParams.get(key);state[name]=name==='connected'?(value==='1'?true:value==='0'?false:value):value;
  }
  try{return {...selectDirectory(entries,state),error:null};}catch(error){return {...selectDirectory(entries),error:'Invalid directory link. Showing the full alphabetical index. '+error.message};}
}
export function directoryURL(href,state){
  const url=new URL(href);for(const key of Object.keys(keys))url.searchParams.delete(key);
  for(const [key,name]of Object.entries(keys))if(state[name]!==DIRECTORY_DEFAULTS[name])url.searchParams.set(key,name==='connected'?'1':state[name]);
  url.hash='catalogue';return url;
}
export function setupDirectory(root,entries){
  const $=name=>document.getElementById('sa-directory-'+name),form=$('form'),table=$('table');
  const templates=new Map([...table.querySelectorAll('[data-index-entry]')].map(row=>[row.dataset.indexEntry,row.cloneNode(true)]));
  let current={...DIRECTORY_DEFAULTS};
  function render(result,{announce=true}={}){
    current=result.state;for(const name of ['query','topic','order'])$(name).value=current[name];$('connected').checked=current.connected;
    $('error').hidden=!result.error;$('error').textContent=result.error||'';form.removeAttribute('aria-describedby');$('query').removeAttribute('aria-invalid');$('query').setAttribute('aria-describedby','sa-directory-help');
    const groups=new Map();
    for(const entry of result.entries){const letter=current.order==='name'?entry.title[0].toUpperCase():'';if(!groups.has(letter))groups.set(letter,[]);groups.get(letter).push(entry);}
    const bodies=[];
    for(const [letter,group]of groups){const body=document.createElement('tbody');body.dataset.indexGroup=letter;if(letter){const row=document.createElement('tr'),cell=document.createElement('th');row.className='sa-directory-letter';cell.scope='rowgroup';cell.colSpan=2;cell.id='index-'+letter;cell.tabIndex=-1;cell.textContent=letter;row.append(cell);body.append(row);}for(const entry of group)body.append(templates.get(entry.id).cloneNode(true));bodies.push(body);}
    for(const body of [...table.tBodies])body.remove();table.append(...bodies);
    root.querySelector('.sa-directory-alphabet').hidden=current.order!=='name';
    root.querySelectorAll('[data-index-jump]').forEach(link=>{link.hidden=!groups.has(link.dataset.indexJump);});
    const label=`${result.entries.length} of ${entries.length} entries, ${current.order==='name'?'alphabetically':'by identifier'}.`;
    $('status').textContent=label;table.querySelector('caption').textContent=label;$('empty').hidden=result.entries.length>0;
  }
  function commit(state){
    try{const result=selectDirectory(entries,state);render(result);history.pushState(null,'',directoryURL(location.href,result.state));}
    catch(error){$('error').textContent=error.message;$('error').hidden=false;form.setAttribute('aria-describedby','sa-directory-error');$('query').setAttribute('aria-invalid','true');$('query').setAttribute('aria-describedby','sa-directory-help sa-directory-error');}
  }
  form.hidden=false;form.noValidate=true;
  form.addEventListener('submit',event=>{event.preventDefault();commit({query:$('query').value,topic:$('topic').value,order:$('order').value,connected:$('connected').checked});});
  $('clear').addEventListener('click',()=>commit({...DIRECTORY_DEFAULTS}));
  $('share').addEventListener('click',async()=>{const text=directoryURL(location.href,current).href;try{await navigator.clipboard.writeText(text);$('copy-fallback').hidden=true;$('status').textContent='Directory link copied.';}catch{$('copy-fallback').hidden=false;$('copy-text').value=text;$('copy-text').focus();$('copy-text').select();$('status').textContent='Copy the directory link from the selected field.';}});
  const restore=()=>render(readDirectoryURL(location.href,entries),{announce:false});restore();addEventListener('popstate',restore);root.dataset.directoryReady='true';
}
