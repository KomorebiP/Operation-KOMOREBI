import {mountFamilies} from './sequence-families-ui.mjs';
import {mountConnections} from './sequence-connections-ui.mjs';
import {mountIdentification} from './sequence-identification-ui.mjs';
import {mountModular} from './sequence-modular-ui.mjs';
import {mountNotebooks} from './sequence-notebooks-ui.mjs';
import {familySource,workbenchLink,WORKBENCH_DEFAULTS} from './sequence-workbench-core.mjs';

export function familySearchEntries(entries,families){
  const memberships=new Map();for(const family of families)for(const id of family.record_ids){if(!memberships.has(id))memberships.set(id,[]);memberships.get(id).push(family);}
  return entries.map(entry=>{const groups=memberships.get(entry.id)||[],copy={...entry,generalized_family_ids:groups.map(g=>g.id),family_names:groups.map(g=>g.title),paper_refs:[...new Set(groups.flatMap(g=>g.paper_refs))],paper_titles:groups.map(g=>g.paper_title)};if(entry.id==='KSEQ-000025')copy.recurrence_order=2;if(/^KOM01[3-6]$/.test(entry.id))copy.recurrence_order=Number(entry.id.slice(3))-10;return copy;});
}
function displaySettings(){return {theme:document.querySelector('#sq-page-theme')?.value||'light',scheme:document.documentElement.dataset.sequenceScheme||'green',math:document.querySelector('#site-math-display')?.value||'typeset'};}
function validateDisplay(s){if(!s||!['light','dark','system'].includes(s.theme)||!['green','mono'].includes(s.scheme)||!['plain','typeset'].includes(s.math))throw Error('Choose supported notebook display settings.');return s;}
export function mountStudio({root,entries,data,referenceClient,workbench,transfers,search}){
  const addFamily=workbench?.addFamily||((engine,params)=>{location.href=workbenchLink(new URL('../sequence-library.html',location.href).href,[familySource(engine,params)],WORKBENCH_DEFAULTS);});
  const family=mountFamilies(root.querySelector('#family-explorer-controls')||root.querySelector('#family-explorer'),data.families,{initialFamily:root.dataset.family,addFamily}),graph=mountConnections(root.querySelector('#connection-explorer'),entries,data.relations),identification=mountIdentification(root.querySelector('#sequence-identification'),entries,{referenceClient,workbench}),modular=mountModular(root.querySelector('#modular-explorer'),{family});
  const display={snapshot:displaySettings,validate:validateDisplay,restore(s){validateDisplay(s);const theme=document.querySelector('#sq-page-theme'),math=document.querySelector('#site-math-display');if(theme){theme.value=s.theme;theme.dispatchEvent(new Event('change'));}document.querySelector('#sq-scheme-'+s.scheme)?.click();if(math){math.value=s.math;math.dispatchEvent(new Event('change'));}}};
  const tools={search,comparison:workbench,transfer:transfers,family,graph,identification,modular,display};mountNotebooks(root.querySelector('#notebook-explorer'),Object.fromEntries(Object.entries(tools).filter(([,v])=>v)));
  function reveal(){let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1).split('?')[0]));}catch{return;}if(!target)return;let ancestor=target.closest('details');while(ancestor){ancestor.open=true;ancestor=ancestor.parentElement.closest('details');}if(['family-explorer','research-graph','identify','modular-dynamics','research-notebooks'].includes(target.id)){target.querySelector('details')?.setAttribute('open','');requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));}}
  addEventListener('hashchange',reveal);reveal();return tools;
}
