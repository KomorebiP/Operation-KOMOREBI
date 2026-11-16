import './sequence-reading-theme.mjs';
import {searchEntries} from './sequence-atlas-search.mjs';
import {archiveLink} from './sequence-archive-core.mjs';
import {setupArchivePlot} from './sequence-archive-plot.mjs';

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
      $('count').textContent=`${found.length} of ${entries.length} research records. Matches use all stored exact terms and preserve each record's offset.`;
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


try {
  const response=await fetch(new URL('./sequence-archive-data.json',import.meta.url));if(!response.ok)throw Error('Archive data could not be loaded.');const {entries}=await response.json();
  if($('search'))setupSearch(entries);
  const selected=root.querySelector('[data-archive-id]');if(selected)setupArchivePlot(entries.find(x=>x.id===selected.dataset.archiveId));
  root.dataset.archiveReady='true';
}catch(error){const note=make('p','Interactive tools could not load. All definitions, exact tables, and downloads remain available. '+error.message);note.setAttribute('role','status');root.prepend(note);}
