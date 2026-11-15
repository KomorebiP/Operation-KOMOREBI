// Presentation preferences are separate from sequence data and arithmetic.
export const PLOT_DEFAULTS=Object.freeze({palette:'forest',point:'4',width:'1.5',height:'standard',grid:'on',baseline:'zero',labels:'none',custom:'#176258'});
export const PLOT_PALETTES=Object.freeze({
  forest:['#185a43','#a44916','#3d5eaa','#854799','#8b6a0c','#167482','#b13c60','#4e7130'],
  ocean:['#075985','#b45309','#0f766e','#7e22ce','#9f1239','#334155','#4d7c0f','#3730a3'],
  ember:['#9a3412','#6b21a8','#166534','#1e40af','#a16207','#9f1239','#0e7490','#475569'],
  contrast:['#006da8','#b44700','#006f55','#8b3b80','#264653','#795800','#6d3b19','#353535'],
  ink:['#222222','#666666','#333333','#777777','#444444','#555555','#111111','#888888']
});
const choices={palette:[['forest','Forest'],['ocean','Ocean'],['ember','Ember'],['contrast','Blue / orange'],['ink','Monochrome'],['custom','Custom main color']],point:[['3','Small'],['4','Standard'],['6','Large'],['8','Extra large']],width:[['1','Fine'],['1.5','Standard'],['2.5','Bold'],['4','Extra bold']],height:[['compact','Compact'],['standard','Standard'],['tall','Tall']],grid:[['on','Show grid'],['off','Hide grid']],baseline:[['zero','Include zero'],['fit','Fit observed values']],labels:[['none','None'],['ends','First and last indices'],['sparse','Sparse index labels']]};
const labels={palette:'Color palette',point:'Point size',width:'Line weight',height:'Chart height',grid:'Grid lines',baseline:'Value-axis range',labels:'Point labels',custom:'Custom main color'};
const KEY='komorebi.sequence-plot-style.v1';
export function validateAppearance(options={}){
  const state={...PLOT_DEFAULTS};
  for(const key of Object.keys(state))if(Object.hasOwn(options,key)){
    const value=String(options[key]);
    if(key==='custom'?!/^#[\da-f]{6}$/i.test(value):!choices[key].some(([id])=>id===value))throw Error(`Choose a valid ${labels[key].toLowerCase()}.`);
    state[key]=key==='custom'?value.toLowerCase():value;
  }
  return state;
}
export function readAppearance(href,storage){
  const url=new URL(href),linked=Object.keys(PLOT_DEFAULTS).some(key=>url.searchParams.has('plot-'+key))||url.searchParams.has('plot-style');
  try{
    if(linked)return {state:validateAppearance(Object.fromEntries(Object.keys(PLOT_DEFAULTS).filter(key=>url.searchParams.has('plot-'+key)).map(key=>[key,url.searchParams.get('plot-'+key)]))),note:''};
    const raw=storage?.getItem(KEY);if(!raw)return {state:{...PLOT_DEFAULTS},note:''};
    const stored=JSON.parse(raw);if(stored.schema!==1)throw Error('Unknown preference version.');
    return {state:validateAppearance(stored.appearance),note:'Using your saved palette and layout.'};
  }catch{return {state:{...PLOT_DEFAULTS},note:'Saved or linked appearance options were unavailable. Showing the default appearance.'};}
}
export function appearanceLink(href,state){
  state=validateAppearance(state);const url=new URL(href);url.searchParams.set('plot-style','1');
  for(const [key,value] of Object.entries(state))url.searchParams.set('plot-'+key,value);
  return url.href;
}
export function plotColors(state){state=validateAppearance(state);return state.palette==='custom'?[state.custom,...PLOT_PALETTES.forest.slice(1)]:PLOT_PALETTES[state.palette].slice();}
export function plotHeight(width,state){return state.height==='compact'?(width<560?280:340):state.height==='tall'?(width<560?520:660):(width<560?360:480);}
export function showIndexLabel(index,count,state,width){
  if(state.labels==='none')return false;
  if(index===0||index===count-1)return true;
  return state.labels==='sparse'&&index%Math.max(1,Math.ceil(count/Math.max(3,Math.floor(width/65))))===0;
}
export function mergePlotLabels(labels){
  const groups=new Map();
  for(const label of labels){const key=label.x.toFixed(2)+':'+label.y.toFixed(2);if(!groups.has(key))groups.set(key,{...label,values:new Set()});groups.get(key).values.add(label.text);}
  return [...groups.values()].map(group=>{const values=[...group.values];return {x:group.x,y:group.y,text:values.length>3?values[0]+' +'+(values.length-1):values.join(', '),full:values.join(', ')};});
}
export function mountPlotOptions({host,prefix,href=location.href,onChange}){
  const storage={getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value),removeItem:key=>localStorage.removeItem(key)};
  const restored=readAppearance(href,storage);let state=restored.state;
  const node=(tag,text)=>{const el=document.createElement(tag);if(text)el.textContent=text;return el;};
  const details=node('details');details.className='sp-options';details.append(node('summary','Customize appearance and layout'));
  const grid=node('div');grid.className='sp-grid';while(host.firstChild)grid.append(host.firstChild);
  const fields={};
  for(const key of Object.keys(PLOT_DEFAULTS)){
    const label=node('label',labels[key]),control=node(key==='custom'?'input':'select');control.id=prefix+'-plot-'+key;label.htmlFor=control.id;
    if(key==='custom')control.type='color';else for(const [value,text]of choices[key]){const option=node('option',text);option.value=value;control.append(option);}
    control.value=state[key];fields[key]=control;label.append(control);grid.append(label);
    control.addEventListener('change',()=>{state=validateAppearance(Object.fromEntries(Object.keys(fields).map(name=>[name,fields[name].value])));fields.custom.disabled=state.palette!=='custom';onChange({...state});});
  }
  fields.custom.disabled=state.palette!=='custom';details.append(grid);
  const context=node('p');context.className='sp-note';details.append(context);
  const actions=node('div');actions.className='sp-actions';const save=node('button','Remember palette and layout'),reset=node('button','Restore appearance defaults');save.type=reset.type='button';actions.append(save,reset);details.append(actions);
  details.append(node('p','Preferences stay in this browser. Copied view links include the full appearance and override saved preferences. View and mark choices stay with the view link.'));
  const status=node('p',restored.note);status.id=prefix+'-plot-style-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');details.append(status);host.append(details);
  save.addEventListener('click',()=>{try{storage.setItem(KEY,JSON.stringify({schema:1,appearance:state}));status.textContent='Palette and layout remembered for this browser.';}catch{status.textContent='Browser storage is unavailable. Your current appearance still works; copy a view link to keep it.';}});
  const set=values=>{state=validateAppearance({...state,...values});for(const key of Object.keys(fields))fields[key].value=state[key];fields.custom.disabled=state.palette!=='custom';onChange({...state});};
  reset.addEventListener('click',()=>{set(PLOT_DEFAULTS);try{storage.removeItem(KEY);status.textContent='Default appearance restored; saved preferences cleared.';}catch{status.textContent='Default appearance restored. Browser storage could not be cleared.';}});
  return {get state(){return {...state};},set,link:href=>appearanceLink(href,state),context:locked=>{fields.baseline.disabled=locked;context.textContent=locked?'Modular plots and bars/stems retain their defined zero baseline.':'Fit observed values reveals variation without forcing the value axis to include zero. Index labels identify samples; exact values remain available by focusing a point.';}};
}

export function standaloneSVG(source){
  if(!source)throw Error('Create a plot before exporting it.');
  const copy=source.cloneNode(true),original=[source,...source.querySelectorAll('*')],cloned=[copy,...copy.querySelectorAll('*')];
  const properties=['fill','stroke','stroke-width','stroke-dasharray','opacity','font-family','font-size','font-weight','paint-order'];
  original.forEach((node,i)=>{const style=getComputedStyle(node);for(const key of properties){const value=style.getPropertyValue(key);if(value)cloned[i].style.setProperty(key,value);}cloned[i].removeAttribute('tabindex');cloned[i].removeAttribute('aria-current');if(i)cloned[i].removeAttribute('role');});
  copy.setAttribute('xmlns','http://www.w3.org/2000/svg');copy.setAttribute('role','img');
  const box=source.viewBox.baseVal;copy.setAttribute('width',box.width);copy.setAttribute('height',box.height);
  const description=copy.querySelector('desc');if(description)description.textContent='Static exported chart. Exact indexed values are available in point titles and the source page data downloads.';
  return new XMLSerializer().serializeToString(copy);
}
export async function exportPlot(source,format,filename){
  const serialized=standaloneSVG(source);let blob=new Blob([serialized],{type:'image/svg+xml;charset=utf-8'});
  if(format==='png'){
    const url=URL.createObjectURL(blob),image=new Image();
    try{await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(Error('Image export failed. SVG export is still available.'));image.src=url;});const box=source.viewBox.baseVal,canvas=document.createElement('canvas');canvas.width=Math.round(box.width*2);canvas.height=Math.round(box.height*2);canvas.getContext('2d').drawImage(image,0,0,canvas.width,canvas.height);blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));if(!blob)throw Error('PNG export is unavailable. Use SVG instead.');}finally{URL.revokeObjectURL(url);}
  }else if(format!=='svg')throw Error('Choose SVG or PNG.');
  const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=filename+'.'+format;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
