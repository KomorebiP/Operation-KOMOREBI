import {defaults,rational,short,settings,sample,certificate,plot} from './chemistry-responses-core.mjs';
const root=document.querySelector('#chemistry-responses'),get=id=>document.querySelector('#cr-'+id);
let data,state=settings(location.hash),current;
const controls=()=>{get('eta').value=state.eta;get('order').value=state.order;get('energy').value=state.index;};
function update(){
  const {point,reduced}=sample(data,state),chart=plot(data,state,matchMedia('(max-width:600px)').matches);get('plot').innerHTML=chart.svg;
  get('plot-note').textContent='Vertical marks show full-target response radii at the sampled energies. '+(chart.capped?`${chart.capped} intervals extend beyond this plot scale; the readout retains the whole bound.`:'The intervals fit this plot scale; small radii may be hidden by the line width.')+' Lines between centers are visual interpolation. The reduced curve has a separate numerical certificate.';
  const strength=-rational(point.center.imaginary),radius=rational(point.radius),rs=-rational(reduced.center.imaginary),rr=rational(reduced.radius);
  get('energy-value').textContent=`ω = ${short(rational(point.omega))} Ha; sample ${state.index+1} of 41`;
  get('result').textContent=`Full finite-model response strength ≈ ${short(strength)} ± ${short(radius)} per Hartree.`;
  get('values').replaceChildren();
  for(const [label,value]of [['Full-target response center, Re(g) + i Im(g)',`${short(rational(point.center.real))} ${rational(point.center.imaginary)<0?'−':'+'} ${short(Math.abs(rational(point.center.imaginary)))} i`],['Full-target response radius upper bound',`≈ ${short(radius)} per Ha`],['Nine-state response strength',`≈ ${short(rs)} ± ${short(rr)} per Ha`],['Full-target actions for this scan',String(state.order)],['New H actions for this energy','0'],['Ionic electronic energy',`≈ ${short(rational(point.energy))} Ha`]]){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;get('values').append(dt,dd);}
  const lower=rational(point.imaginary_discrepancy_lower);
  get('discrepancy').textContent=lower>0?`The full and reduced imaginary responses differ by at least ≈ ${short(lower)} per Hartree at this sample. This certifies disagreement between these two finite-model responses.`:'This sample does not certify a nonzero discrepancy with the reduced response. A wide error interval can prevent that conclusion.';
  current=certificate(data,{...state},root.dataset.sha256);get('certificate').textContent=JSON.stringify(current,null,2);
  const hash=new URLSearchParams({eta:state.eta,k:String(state.order),i:String(state.index)}).toString();get('link').href='chemistry-responses.html#'+hash;
}
async function load(){
  get('retry').hidden=true;get('status').textContent='Loading the response data and checking SHA-256…';
  try{const response=await fetch(root.dataset.source);if(!response.ok)throw Error('Response data unavailable');const bytes=await response.arrayBuffer(),digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(digest!==root.dataset.sha256)throw Error('Response data identity mismatch');data=JSON.parse(new TextDecoder().decode(bytes));if(data.version!==1||data.points.length!==984||data.reduced_points.length!==123)throw Error('Unexpected response data');controls();update();get('explorer').hidden=false;get('status').textContent='Recorded response data verified. Controls select samples from the saved calculation.';}
  catch(error){get('explorer').hidden=true;get('status').textContent='The interactive scan could not be verified. The static results and replay remain available.';get('retry').hidden=false;}
}
get('eta').addEventListener('change',()=>{state.eta=get('eta').value;update();});get('order').addEventListener('change',()=>{state.order=Number(get('order').value);update();});get('energy').addEventListener('input',()=>{state.index=Number(get('energy').value);update();});
get('reset').addEventListener('click',()=>{state={...defaults};controls();update();});
get('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(current,null,2)+'\n'],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=`chemistry-response-k${state.order}-sample${state.index+1}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
get('retry').addEventListener('click',load);window.addEventListener('hashchange',()=>{state=settings(location.hash);controls();if(data)update();});matchMedia('(max-width:600px)').addEventListener('change',()=>{if(data)update();});load();
