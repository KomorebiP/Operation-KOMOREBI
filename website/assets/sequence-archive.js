import './sequence-reading-theme.mjs';
import {archiveDestination} from './sequence-navigation.mjs';
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
  const names=['query','family','review','sort','match'],reviews=new Map(entries.map(entry=>[entry.classification,entry.status]));
  for(const key of names)if(params.has(key))$(key).value=key==='review'?(reviews.get(params.get(key))||params.get(key)):params.get(key);
  const filters=()=>Object.fromEntries(names.map(key=>[key,$(key).value]));
  const destination=()=>archiveDestination(location.href,filters());
  $('search').hidden=false;
  $('search').addEventListener('submit',event=>{event.preventDefault();location.assign(destination());});
  $('clear').addEventListener('click',()=>{for(const key of ['query','family','review'])$(key).value='';$('sort').value='id';$('match').value='any';$('query').focus();});
  $('share').addEventListener('click',()=>copy(destination(),$('count'),$('share-fallback'),$('share-value')));
  if(names.some(key=>params.has(key)))location.replace(destination());
}


try {
  const response=await fetch(new URL('./sequence-archive-data.json',import.meta.url));if(!response.ok)throw Error('Archive data could not be loaded.');const {entries}=await response.json();
  if($('search'))setupSearch(entries);
  const selected=root.querySelector('[data-archive-id]');if(selected)setupArchivePlot(entries.find(x=>x.id===selected.dataset.archiveId));
  root.dataset.archiveReady='true';
}catch(error){const note=make('p','Interactive tools could not be loaded. All definitions, exact tables, and downloads remain available. '+error.message);note.setAttribute('role','status');root.prepend(note);}
