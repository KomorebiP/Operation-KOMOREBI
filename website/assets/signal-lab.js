import {BASES,defaults,settings,experiment,basisVector,encodeSettings,decodeSettings,parseSamples,signalCsv,curvesCsv,experimentJson,importExperiment} from './signal-lab-core.mjs';

const root=document.getElementById('signal-lab');
const byId=id=>document.getElementById(id);
const text=(id,value)=>{byId(id).textContent=value;};
const names={haar:'Haar wavelets',cosine:'Cosine modes',samples:'Sample coordinates'};
const NS='http://www.w3.org/2000/svg';
const format=value=>Math.abs(value)>0 && (Math.abs(value)<.001||Math.abs(value)>=1e7) ? value.toExponential(3).replace('e+','e') : value.toLocaleString('en-US',{maximumSignificantDigits:6});
const tick=value=>value===0 ? '0' : Math.abs(value)>=10000||Math.abs(value)<.01 ? value.toExponential(0).replace('e+','e') : Number(value.toPrecision(3)).toString();
let config=defaults(),result=null,renderFrame;
function node(tag,attributes={},value) {
  const item=document.createElementNS(NS,tag);
  for(const [key,val] of Object.entries(attributes))item.setAttribute(key,val);
  if(value!==undefined)item.textContent=value;
  return item;
}
function label(svg,x,y,value,anchor='middle') {svg.append(node('text',{x,y,'text-anchor':anchor},value));}
function chart(id,height,description,{xMax,yMin,yMax,xLabel,yLabel,barDomain=false}) {
  const host=byId(id),width=Math.max(220,Math.floor(host.getBoundingClientRect().width));
  const svg=node('svg',{viewBox:`0 0 ${width} ${height}`,'aria-hidden':'true',focusable:'false'});
  host.setAttribute('aria-label',description);host.replaceChildren(svg);
  const left=58,right=width-16,top=26,bottom=height-46;
  const x=v=>left+(barDomain?(v+.5)/(xMax+1):v/xMax)*(right-left),y=v=>bottom-(v-yMin)/(yMax-yMin)*(bottom-top);
  for(const value of [yMin,(yMin+yMax)/2,yMax]) {
    svg.append(node('line',{x1:left,x2:right,y1:y(value),y2:y(value),class:'sl-chart-grid'}));
    label(svg,left-8,y(value)+4,tick(value),'end');
  }
  svg.append(node('rect',{x:left,y:top,width:right-left,height:bottom-top,class:'sl-chart-frame'}));
  label(svg,left,14,yLabel,'start');
  for(const value of [...new Set([0,Math.round(xMax/3),Math.round(2*xMax/3),xMax])])label(svg,x(value),bottom+18,value);
  label(svg,(left+right)/2,height-7,xLabel);
  return {svg,width,height,left,right,top,bottom,x,y};
}
function trace(plot,values,className) {
  plot.svg.append(node('polyline',{points:values.map((v,i)=>`${plot.x(i)},${plot.y(v)}`).join(' '),class:'sl-trace '+className}));
}
function guide(plot,index) {plot.svg.append(node('line',{x1:plot.x(index),x2:plot.x(index),y1:plot.top,y2:plot.bottom,class:'sl-chart-guide'}));}
function limit(values) {return Math.max(1,Math.ceil(Math.max(...values.map(Math.abs))*1.1));}
function drawSignal() {
  const a=result.analyses[config.basis],extent=limit([...result.reference,...result.observed,...a.reconstruction]);
  const plot=chart('sl-signal-chart',310,`${names[config.basis]} reconstruction with ${config.budget} of ${config.n} coefficients. Reference error ${format(a.referenceError)}.`,
    {xMax:config.n-1,yMin:-extent,yMax:extent,xLabel:'Sample address',yLabel:'Amplitude'});
  trace(plot,result.observed,'sl-observed');trace(plot,result.reference,'sl-reference');trace(plot,a.reconstruction,'sl-reconstruction');
  guide(plot,config.address);
  for(const values of [result.reference,result.observed,a.reconstruction])plot.svg.append(node('circle',{cx:plot.x(config.address),cy:plot.y(values[config.address]),r:4,class:'sl-chart-point'}));
}
function drawFrontier() {
  const maximum=Math.max(1,...BASES.flatMap(b=>result.analyses[b].curve.map(p=>p.referenceError)))*1.06;
  const plot=chart('sl-frontier-chart',280,'Squared reference error at every coefficient budget for Haar wavelets, cosine modes and sample coordinates.',
    {xMax:config.n,yMin:0,yMax:maximum,xLabel:'Retained coefficients',yLabel:'Squared reference error'});
  for(const basis of BASES)trace(plot,result.analyses[basis].curve.map(p=>p.referenceError),'sl-'+basis);
  guide(plot,config.budget);
  for(const basis of BASES)plot.svg.append(node('circle',{cx:plot.x(config.budget),cy:plot.y(result.analyses[basis].referenceError),r:4,class:'sl-chart-point'}));
}
function drawCoefficients() {
  const a=result.analyses[config.basis],energies=a.values.map((v,i)=>a.weights[i]*v*v),maximum=Math.max(1,...energies)*1.06;
  const plot=chart('sl-coefficient-chart',230,`${names[config.basis]} weighted coefficient energies. ${config.budget} coefficients retained. Selected index ${config.coefficient}.`,
    {xMax:config.n-1,yMin:0,yMax:maximum,xLabel:'Coefficient index',yLabel:'Weighted energy',barDomain:true});
  const spacing=(plot.right-plot.left)/config.n;
  energies.forEach((value,i)=>{
    const height=Math.max(1,plot.bottom-plot.y(value));
    plot.svg.append(node('rect',{x:plot.left+i*spacing+.12*spacing,y:plot.bottom-height,width:.76*spacing,height,
      class:(a.chosen[i]?'sl-coefficient-kept':'sl-coefficient-omitted')+(i===config.coefficient?' sl-coefficient-selected':''),'data-coefficient':i}));
  });
}
function drawBasis() {
  const a=result.analyses[config.basis],c=a.values[config.coefficient],values=basisVector(config.n,config.basis,config.coefficient).map(v=>v*c),extent=limit(values);
  const plot=chart('sl-basis-chart',180,`Contribution of coefficient ${config.coefficient} if retained. ${a.metadata[config.coefficient].label}.`,
    {xMax:config.n-1,yMin:-extent,yMax:extent,xLabel:'Sample address',yLabel:'Contribution'});
  trace(plot,values,'sl-'+config.basis);guide(plot,config.address);
}
function drawAll() {if(result){drawSignal();drawFrontier();drawCoefficients();drawBasis();}}
function clearError() {byId('sl-error').hidden=true;}
function showError(message) {text('sl-error',message);byId('sl-error').hidden=false;}
function status(message) {text('sl-status',message);}
function readNumber(id) {
  const input=byId(id),valid=input.value.trim()!==''&&input.checkValidity();
  input.setAttribute('aria-invalid',String(!valid));
  if(!valid)throw new RangeError('Use a whole-number seed from 0 to 4294967295. The plots keep the last valid experiment.');
  return Number(input.value);
}
function readControls() {
  const n=Number(byId('sl-size').value);
  byId('sl-budget').max=n;byId('sl-address').max=n-1;byId('sl-coefficient').max=n-1;byId('sl-cycles').max=Math.min(16,n/4);
  return settings({...config,n,shape:byId('sl-shape').value,amplitude:readNumber('sl-amplitude'),cycles:readNumber('sl-cycles'),noise:readNumber('sl-noise'),seed:readNumber('sl-seed'),
    budget:readNumber('sl-budget'),policy:byId('sl-policy').value,address:readNumber('sl-address'),coefficient:readNumber('sl-coefficient')});
}
function syncControls() {
  const controls={shape:config.shape,size:config.n,policy:config.policy,budget:config.budget,noise:config.noise,seed:config.seed,amplitude:config.amplitude,cycles:config.cycles,address:config.address,coefficient:config.coefficient};
  byId('sl-budget').max=config.n;byId('sl-address').max=config.n-1;byId('sl-coefficient').max=config.n-1;byId('sl-cycles').max=Math.min(16,config.n/4);
  for(const [id,value] of Object.entries(controls))byId('sl-'+id).value=value;
  for(const id of ['budget','noise','amplitude','cycles','address','coefficient'])text('sl-'+id+'-value',controls[id]);
  text('sl-controls-summary',`${config.n} samples · ${config.budget} kept · noise ±${config.noise}`);
  text('sl-seed-note',`Seed ${config.seed} · bounded integer noise.`);
  byId('sl-size').disabled=config.shape==='custom';byId('sl-amplitude').disabled=config.shape==='custom';
  byId('sl-cycles').disabled=!['wave','chirp','mixed'].includes(config.shape);
  text('sl-shape-note',config.shape==='custom'?'The sample count and amplitude follow the imported data. Choose a preset to generate a different size.':
    'For cosine waves and mixed signals, frequency is the cosine mode index; for chirps, it is the maximum local cycle rate. Preset samples are rounded to integers.');
  root.querySelectorAll('[data-sl-basis]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.slBasis===config.basis)));
}
function renderTable() {
  if(!result||!byId('sl-table-details').open)return;
  const a=result.analyses[config.basis];
  byId('sl-sample-table').replaceChildren(...result.reference.map((v,i)=>{
    const row=document.createElement('tr');
    [i,v,result.observed[i],a.reconstruction[i],result.observed[i]-a.reconstruction[i]].forEach((value,column)=>{
      const cell=document.createElement(column===0?'th':'td');if(column===0)cell.scope='row';cell.textContent=format(value);row.append(cell);
    });return row;
  }));
}
function render() {
  result=experiment(config);syncControls();
  text('sl-active-name','· '+names[config.basis]);
  text('sl-budget-summary',`${config.budget} of ${config.n} coefficients retained in each representation`);
  const notes={energy:'Rank by weighted energy. Each representation keeps the components that contribute most to its observed signal.',
    magnitude:'Rank by raw magnitude. Haar coefficients have different support weights, so the largest raw numbers need not carry the most energy.',
    prefix:'Keep a fixed prefix: coarse-to-fine Haar details, low-to-high cosine modes, or the earliest sample addresses.'};
  text('sl-policy-note',notes[config.policy]);text('sl-noise-energy',format(result.noiseEnergy));
  for(const basis of BASES) {
    text('sl-'+basis+'-reference',format(result.analyses[basis].referenceError));
    text('sl-'+basis+'-observed',format(result.analyses[basis].observedError));
  }
  const a=result.analyses[config.basis],address=config.address,i=config.coefficient,c=a.values[i],m=a.metadata[i];
  text('sl-sample-status',`Address ${address} · reference ${format(result.reference[address])} · observed ${format(result.observed[address])} · reconstructed ${format(a.reconstruction[address])} · discarded residual ${format(result.observed[address]-a.reconstruction[address])}`);
  text('sl-coefficient-status',`${m.label} · ${m.start===m.end?'address '+m.start:'addresses '+m.start+'–'+m.end} · ${a.chosen[i]?'kept':'omitted'}. Coefficient ${format(c)}; support weight ${a.weights[i]}; weighted energy ${format(a.weights[i]*c*c)}.`);
  text('sl-best-note',`${names[config.basis]} · reference minimum at ${a.bestBudget} of ${config.n} coefficients, within numerical tolerance. This comparison uses the known clean reference.`);
  drawAll();renderTable();root.dataset.ready='true';
}
function schedule() {syncControls();root.dataset.ready='false';cancelAnimationFrame(renderFrame);renderFrame=requestAnimationFrame(render);}
function ensureResult() {cancelAnimationFrame(renderFrame);config=readControls();render();return result;}
function updateFromControls() {try{config=readControls();clearError();schedule();}catch(error){cancelAnimationFrame(renderFrame);if(result)root.dataset.ready='true';showError(error.message);}}
byId('sl-controls').addEventListener('input',updateFromControls);
byId('sl-sample-inspector').addEventListener('input',updateFromControls);
byId('sl-coefficient-inspector').addEventListener('input',updateFromControls);
root.querySelectorAll('[data-sl-basis]').forEach(button=>button.addEventListener('click',()=>{
  try{config={...readControls(),basis:button.dataset.slBasis};clearError();schedule();}catch(error){showError(error.message);}
}));
byId('sl-new-noise').addEventListener('click',()=>{
  try{config={...readControls(),seed:(readNumber('sl-seed')+1)>>>0};clearError();schedule();}catch(error){showError(error.message);}
});
function clickedIndex(event,id,maximum,cells=false) {
  const svg=byId(id).querySelector('svg'),box=svg.getBoundingClientRect(),width=svg.viewBox.baseVal.width;
  const ratio=((event.clientX-box.left)*width/box.width-58)/(width-74);
  return Math.max(0,Math.min(maximum,cells?Math.floor(ratio*(maximum+1)):Math.round(ratio*maximum)));
}
for(const [id,key,cells] of [['sl-signal-chart','address',false],['sl-frontier-chart','budget',false],['sl-coefficient-chart','coefficient',true]]) {
  byId(id).addEventListener('click',event=>{
    try{const next=readControls();config={...next,[key]:clickedIndex(event,id,key==='budget'?config.n:config.n-1,cells)};clearError();schedule();}catch(error){showError(error.message);}
  });
}
byId('sl-best').addEventListener('click',()=>{
  try{const current=ensureResult();config={...config,budget:current.analyses[config.basis].bestBudget};schedule();clearError();}catch(error){showError(error.message);}
});
byId('sl-reset').addEventListener('click',()=>{
  config=defaults();byId('sl-seed').setAttribute('aria-invalid','false');byId('sl-paste').value='';byId('sl-file').value='';
  byId('sl-link-fallback').hidden=true;clearError();status('Default experiment restored.');
  const url=new URL(location.href);url.searchParams.delete('lab');history.replaceState(null,'',url.href);render();
});
byId('sl-copy').addEventListener('click',async()=>{
  byId('sl-link-fallback').hidden=true;
  let url;
  try{ensureResult();url=new URL(location.href);url.searchParams.set('lab',encodeSettings(config));clearError();}
  catch(error){showError(error.message);return;}
  byId('sl-copy').disabled=true;
  try{await navigator.clipboard.writeText(url.href);status('Experiment link copied. The signal, noise seed, budget, and inspection settings will be restored.');}
  catch{byId('sl-link').value=url.href;byId('sl-link-fallback').hidden=false;byId('sl-link').focus();byId('sl-link').select();status('Select and copy the experiment link below.');}
  finally{byId('sl-copy').disabled=false;}
});
byId('sl-export').addEventListener('click',()=>{
  try{
    const current=ensureResult(),kind=byId('sl-export-kind').value;
    const content=kind==='signal'?signalCsv(current):kind==='curves'?curvesCsv(current):experimentJson(current);
    const href=URL.createObjectURL(new Blob([content],{type:kind==='experiment'?'application/json':'text/csv'}));
    const link=document.createElement('a');link.href=href;link.download=`komorebi-${kind}-${config.n}-${config.basis}.${kind==='experiment'?'json':'csv'}`;
    document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(href),1000);
    status(kind==='experiment'?'Experiment JSON downloaded. Import it to restore this setup.':'CSV downloaded.');clearError();
  }catch(error){showError(error.message);}
});
function applySamples(values) {
  config=settings({...config,n:values.length,shape:'custom',custom:values,cycles:Math.min(config.cycles,values.length/4),budget:Math.min(config.budget,values.length),coefficient:0,address:0});
  clearError();status(`${values.length} reference samples imported. Noise is added using the current seed.`);render();
}
byId('sl-apply').addEventListener('click',()=>{try{applySamples(parseSamples(byId('sl-paste').value));}catch(error){showError(error.message);}});
byId('sl-file').addEventListener('change',async()=>{
  const file=byId('sl-file').files[0];if(!file)return;
  try{
    if(file.size>65536)throw new RangeError('Use a file under 64 KiB.');
    const content=await file.text();
    if(file.name.toLowerCase().endsWith('.json')){config=importExperiment(content);clearError();status('Saved experiment restored. Results were recomputed from its settings.');render();}
    else applySamples(parseSamples(content));
  }catch(error){showError(error.message);}
});
byId('sl-table-details').addEventListener('toggle',()=>{if(byId('sl-table-details').open){try{ensureResult();}catch(error){showError(error.message);}}});
const shared=new URL(location.href).searchParams.get('lab');
if(shared!==null){try{config=decodeSettings(shared);status('Experiment restored from the link.');}catch(error){showError(error.message+' Default settings are shown.');}}
if(matchMedia('(max-width: 760px)').matches)byId('sl-setup').open=false;
root.querySelectorAll('fieldset,[data-sl-action],[data-sl-basis],#sl-export-kind').forEach(element=>{element.disabled=false;});
render();
let resizeFrame;
const widths=new WeakMap();
const observer=new ResizeObserver(entries=>{
  let changed=false;
  for(const entry of entries){const width=Math.floor(entry.contentRect.width);if(width>0&&widths.get(entry.target)!==width)changed=true;widths.set(entry.target,width);}
  if(changed){cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>{if(root.dataset.ready==='true')drawAll();});}
});
root.querySelectorAll('.lab-diagram').forEach(element=>observer.observe(element));
