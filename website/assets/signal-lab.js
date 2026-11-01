import {BASES,defaults,settings,referenceSignal,experiment,basisVector,encodeSettings,decodeSettings,parseSamples,signalCsv,curvesCsv,experimentJson,importExperiment} from './signal-lab-core.mjs';
import {MAX_RUNS,customSettings,paintSegment,SampleHistory,readNotebook,writeNotebook,appendRuns,sameObservation,notebookCsv,starterRuns,compareRuns,comparisonCsv} from './signal-lab-workspace.mjs';

const root=document.getElementById('signal-lab');
const byId=id=>document.getElementById(id);
const text=(id,value)=>{byId(id).textContent=value;};
const names={haar:'Haar wavelets',cosine:'Cosine modes',samples:'Sample coordinates'};
const NS='http://www.w3.org/2000/svg';
const format=value=>Math.abs(value)>0 && (Math.abs(value)<.001||Math.abs(value)>=1e7) ? value.toExponential(3).replace('e+','e') : value.toLocaleString('en-US',{maximumSignificantDigits:6});
const tick=value=>value===0 ? '0' : Math.abs(value)>=10000||Math.abs(value)<.01 ? value.toExponential(0).replace('e+','e') : Number(value.toPrecision(3)).toString();
let config=defaults(),result=null,renderFrame;
const editHistory=new SampleHistory(),notebookKey='komorebi-signal-notebook-v1';
let drawing=false,stroke=null,signalPlot=null,runs=[],savedResults=[],pairA=0,pairB=0,pairAddress=32,notebookMemory=false;
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
function drawSignal(reference=result.reference) {
  const a=result.analyses[config.basis],extent=drawing?64:limit([...reference,...result.observed,...a.reconstruction]);
  const description=drawing?'Draw whole-number reference samples from −64 to 64. Use the precise sample editor for keyboard input.':`${names[config.basis]} reconstruction with ${config.budget} of ${config.n} coefficients. Reference error ${format(a.referenceError)}.`;
  const plot=chart('sl-signal-chart',310,description,
    {xMax:config.n-1,yMin:-extent,yMax:extent,xLabel:'Sample address',yLabel:'Amplitude'});
  signalPlot=plot;
  if(!drawing)trace(plot,result.observed,'sl-observed');trace(plot,reference,'sl-reference');if(!drawing)trace(plot,a.reconstruction,'sl-reconstruction');
  guide(plot,config.address);
  for(const values of drawing?[reference]:[reference,result.observed,a.reconstruction])plot.svg.append(node('circle',{cx:plot.x(config.address),cy:plot.y(values[config.address]),r:4,class:'sl-chart-point'}));
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
function drawAll() {if(result){drawSignal(stroke?.values);drawFrontier();drawCoefficients();drawBasis();drawSavedComparison();}}
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
  for(const [id,value] of Object.entries(controls)){const input=byId('sl-'+id);input.value=value;if(input.matches('input'))input.setAttribute('aria-invalid','false');}
  for(const id of ['budget','noise','amplitude','cycles','address','coefficient'])text('sl-'+id+'-value',controls[id]);
  text('sl-controls-summary',`${config.n} samples · ${config.budget} kept · noise ±${config.noise}`);
  text('sl-seed-note',`Seed ${config.seed} · bounded integer noise.`);
  byId('sl-size').disabled=config.shape==='custom';byId('sl-amplitude').disabled=config.shape==='custom';
  byId('sl-cycles').disabled=!['wave','chirp','mixed'].includes(config.shape);
  text('sl-shape-note',config.shape==='custom'?'The sample count and amplitude follow the imported data. Choose a preset to generate a different size.':
    'For cosine waves and mixed signals, frequency is the cosine mode index; for chirps, it is the maximum local cycle rate. Preset samples are rounded to integers.');
  root.querySelectorAll('[data-sl-basis]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.slBasis===config.basis)));
  byId('sl-edit-value').value=referenceSignal(config)[config.address];
  byId('sl-edit-value').setAttribute('aria-invalid','false');
  byId('sl-undo').disabled=!editHistory.past.length;byId('sl-redo').disabled=!editHistory.future.length;
  root.dataset.editing=String(drawing);byId('sl-draw').setAttribute('aria-pressed',String(drawing));
  text('sl-draw',drawing?'Finish drawing':'Draw reference');byId('sl-draw-help').hidden=!drawing;
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
  text('sl-main-title',drawing?'Draw the reference':'Signal reconstruction');
  text('sl-active-name',drawing?'': '· '+names[config.basis]);
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
function ensureResult() {if(stroke)throw new RangeError('Finish or cancel the current stroke first.');cancelAnimationFrame(renderFrame);config=readControls();render();return result;}
function updateFromControls(event) {try{const next=readControls();cancelStroke();config=next;if(['sl-shape','sl-size','sl-amplitude','sl-cycles'].includes(event.target.id)){editHistory.clear();text('sl-edit-status','');}clearError();schedule();}catch(error){cancelAnimationFrame(renderFrame);if(result)root.dataset.ready='true';showError(error.message);}}
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
    if(id==='sl-signal-chart'&&drawing)return;
    try{const next=readControls();config={...next,[key]:clickedIndex(event,id,key==='budget'?config.n:config.n-1,cells)};clearError();schedule();}catch(error){showError(error.message);}
  });
}
byId('sl-best').addEventListener('click',()=>{
  try{const current=ensureResult();config={...config,budget:current.analyses[config.basis].bestBudget};schedule();clearError();}catch(error){showError(error.message);}
});
byId('sl-reset').addEventListener('click',()=>{
  cancelStroke();editHistory.clear();drawing=false;text('sl-edit-status','');
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
  cancelStroke();editHistory.clear();drawing=false;text('sl-edit-status','');
  config=settings({...config,n:values.length,shape:'custom',custom:values,cycles:Math.min(config.cycles,values.length/4),budget:Math.min(config.budget,values.length),coefficient:0,address:0});
  clearError();status(`${values.length} reference samples imported. Noise is added using the current seed.`);render();
}
byId('sl-apply').addEventListener('click',()=>{try{applySamples(parseSamples(byId('sl-paste').value));}catch(error){showError(error.message);}});
byId('sl-file').addEventListener('change',async()=>{
  const file=byId('sl-file').files[0];if(!file)return;
  try{
    if(file.size>65536)throw new RangeError('Use a file under 64 KiB.');
    const content=await file.text();
    if(file.name.toLowerCase().endsWith('.json')){const next=importExperiment(content);cancelStroke();editHistory.clear();drawing=false;config=next;clearError();status('Saved experiment restored. Results were recomputed from its settings.');render();}
    else applySamples(parseSamples(content));
  }catch(error){showError(error.message);}
});
byId('sl-table-details').addEventListener('toggle',()=>{if(byId('sl-table-details').open){try{ensureResult();}catch(error){showError(error.message);}}});

function cancelStroke() {
  if(!stroke)return;
  const pointer=stroke.pointerId;stroke=null;
  if(byId('sl-signal-chart').hasPointerCapture(pointer))byId('sl-signal-chart').releasePointerCapture(pointer);
  text('sl-edit-status','Stroke cancelled.');render();
}
function setDrawing(value) {cancelStroke();drawing=value;clearError();render();}
byId('sl-draw').addEventListener('click',()=>{try{ensureResult();setDrawing(!drawing);}catch(error){showError(error.message);}});
function samplePoint(event,inside=false) {
  const p=signalPlot,box=p.svg.getBoundingClientRect(),x=(event.clientX-box.left)*p.width/box.width,y=(event.clientY-box.top)*p.height/box.height;
  if(inside&&(x<p.left-1||x>p.right+1||y<p.top-1||y>p.bottom+1))return null;
  return {index:Math.max(0,Math.min(config.n-1,Math.round((x-p.left)/(p.right-p.left)*(config.n-1)))),
    value:Math.max(-64,Math.min(64,Math.round(64-(y-p.top)/(p.bottom-p.top)*128)))||0};
}
function paintPoint(point) {
  stroke.values=paintSegment(stroke.values,stroke.last,point);stroke.last=point;config.address=point.index;
  byId('sl-address').value=point.index;text('sl-address-value',point.index);byId('sl-edit-value').value=point.value;
  text('sl-edit-status',`Drawing address ${point.index} · reference ${point.value}. Release to apply the stroke.`);drawSignal(stroke.values);
}
const signalHost=byId('sl-signal-chart');
signalHost.addEventListener('pointerdown',event=>{
  if(!drawing||!event.isPrimary||event.button!==0)return;
  try{
    ensureResult();const point=samplePoint(event,true);if(!point)return;
    event.preventDefault();stroke={pointerId:event.pointerId,before:result.reference.slice(),values:result.reference.slice(),last:point};
    signalHost.setPointerCapture(event.pointerId);paintPoint(point);
  }catch(error){showError(error.message);}
});
signalHost.addEventListener('pointermove',event=>{if(stroke?.pointerId===event.pointerId){event.preventDefault();paintPoint(samplePoint(event));}});
signalHost.addEventListener('pointerup',event=>{
  if(stroke?.pointerId!==event.pointerId)return;
  paintPoint(samplePoint(event));const finished=stroke;stroke=null;
  if(signalHost.hasPointerCapture(event.pointerId))signalHost.releasePointerCapture(event.pointerId);
  const changed=finished.before.reduce((n,v,i)=>n+Number(v!==finished.values[i]),0);
  if(editHistory.record(finished.before,finished.values))config=customSettings(config,finished.values);
  clearError();render();text('sl-edit-status',changed?`${changed} reference samples updated. The experiment was recomputed.`:'Reference unchanged.');
});
signalHost.addEventListener('pointercancel',event=>{if(stroke?.pointerId===event.pointerId)cancelStroke();});
signalHost.addEventListener('lostpointercapture',event=>{if(stroke?.pointerId===event.pointerId)cancelStroke();});
root.addEventListener('keydown',event=>{if(event.key==='Escape'&&drawing){event.preventDefault();setDrawing(false);byId('sl-draw').focus();}});
byId('sl-set-sample').addEventListener('click',()=>{
  try{
    const input=byId('sl-edit-value'),valid=input.value.trim()!==''&&input.checkValidity();input.setAttribute('aria-invalid',String(!valid));
    if(!valid)throw new RangeError('Use a whole-number reference value from −64 to 64.');
    const value=Number(input.value),current=ensureResult(),before=current.reference,after=before.slice();after[config.address]=value||0;
    if(editHistory.record(before,after))config=customSettings(config,after);
    clearError();render();text('sl-edit-status',`Reference at address ${config.address} set to ${value}.`);
  }catch(error){showError(error.message);}
});
for(const action of ['undo','redo'])byId('sl-'+action).addEventListener('click',()=>{
  try{const current=ensureResult(),values=editHistory[action](current.reference);if(values){config=customSettings(config,values);render();clearError();text('sl-edit-status',action==='undo'?'Signal edit undone.':'Signal edit restored.');}}
  catch(error){showError(error.message);}
});

function saveNotebook() {
  try{localStorage.setItem(notebookKey,writeNotebook(runs));notebookMemory=false;text('sl-notebook-status','Notebook saved in this browser.');}
  catch{notebookMemory=true;text('sl-notebook-status','Browser storage is unavailable. This notebook is kept for this tab; download JSON to keep it.');}
}
function notebookButton(label,action,index) {
  const button=document.createElement('button');button.type='button';button.textContent=label;button.dataset.notebookAction=action;button.dataset.run=index;return button;
}
function renderNotebook(resetPair=false) {
  savedResults=runs.map(entry=>experiment(entry.settings));
  text('sl-notebook-count',`${runs.length} / ${MAX_RUNS} saved runs`);
  byId('sl-save-run').disabled=runs.length===MAX_RUNS;
  root.querySelectorAll('[data-sl-starter]').forEach(button=>{button.disabled=runs.length>MAX_RUNS-2;});
  text('sl-starter-note',runs.length>MAX_RUNS-2?'Free two notebook slots to open a starter experiment. Your saved runs are kept.':'Each starter opens a reference experiment and adds two named runs to your notebook. Existing saved runs are kept.');
  byId('sl-notebook-export').disabled=!runs.length;byId('sl-notebook-csv').disabled=!runs.length;
  byId('sl-notebook-empty').hidden=Boolean(runs.length);byId('sl-notebook-table-wrap').hidden=!runs.length;
  byId('sl-notebook-comparison').hidden=runs.length<2;
  byId('sl-notebook-rows').replaceChildren(...runs.map((entry,i)=>{
    const s=entry.settings,a=savedResults[i].analyses[s.basis],row=document.createElement('tr');row.dataset.run=i;
    const cell=tag=>{const item=document.createElement(tag);row.append(item);return item;};
    const title=cell('th');title.scope='row';const input=document.createElement('input');input.type='text';input.maxLength=48;input.value=entry.label;input.dataset.runName=i;input.setAttribute('aria-label',`Name of saved run ${i+1}`);title.append(input);
    const setup=cell('td');setup.textContent=`${names[s.basis]} · ${s.n} samples · noise ±${s.noise} · seed ${s.seed} · ${s.policy}`;
    cell('td').textContent=`${s.budget} / ${s.n}`;cell('td').textContent=format(a.referenceError);cell('td').textContent=format(a.observedError);
    const actions=cell('td');actions.append(notebookButton('Restore','restore',i),notebookButton('Remove','remove',i));return row;
  }));
  if(resetPair){pairA=0;pairB=Math.max(0,runs.length-1);}
  for(const [id,selected] of [['sl-compare-a',pairA],['sl-compare-b',pairB]]) {
    const select=byId(id);select.replaceChildren(...runs.map((entry,i)=>{const option=document.createElement('option');option.value=i;option.textContent=entry.label;return option;}));select.value=selected;
  }
  drawSavedComparison();
}
function drawSavedComparison() {
  if(runs.length<2){byId('sl-pair-chart').replaceChildren();byId('sl-pair-table').replaceChildren();return;}
  const a=savedResults[pairA],b=savedResults[pairB],same=sameObservation(a,b);byId('sl-pair-plot').hidden=!same;
  byId('sl-pair-inspector').disabled=!same;
  if(!same){text('sl-pair-summary','These runs use different reference or observed samples. Their errors describe different experiments. Save two runs of the same observations to overlay their reconstructions.');byId('sl-pair-chart').replaceChildren();byId('sl-pair-table').replaceChildren();return;}
  const aa=a.analyses[a.config.basis],bb=b.analyses[b.config.basis],delta=bb.referenceError-aa.referenceError;
  const data=compareRuns(a,b),view=byId('sl-pair-view').value;
  pairAddress=Math.min(pairAddress,a.config.n-1);byId('sl-pair-address').max=a.config.n-1;byId('sl-pair-address').value=pairAddress;text('sl-pair-address-value',pairAddress);
  const selected=data.rows[pairAddress];
  for(const [id,key] of [['sample','address'],['reference','reference'],['observed','observed'],['a','a'],['b','b'],['error-a','errorA'],['error-b','errorB'],['difference','difference']])text('sl-pair-'+id,format(selected[key]));
  text('sl-pair-gap',`Largest absolute difference: ${format(data.maximum)} at address ${data.maximumAddress}. Ties use the first address.`);
  text('sl-pair-summary',`Identical reference and observed samples. A keeps ${a.config.budget} coefficients; B keeps ${b.config.budget}. Reference error B − A: ${format(delta)}${delta<0?' · B is lower.':delta>0?' · A is lower.':' · equal.'}`);
  text('sl-pair-a-label','A · '+runs[pairA].label);text('sl-pair-b-label','B · '+runs[pairB].label);
  byId('sl-pair-reference-label').hidden=view!=='overlay';byId('sl-pair-a-label').hidden=view==='difference';byId('sl-pair-b-label').hidden=view==='difference';byId('sl-pair-difference-label').hidden=view!=='difference';
  text('sl-pair-view-note',view==='error'?'Signed error is reconstruction minus reference. Zero means an exact match at that sample. Click the plot or use the sample slider.':view==='difference'?'Signed difference is reconstruction B minus reconstruction A. Zero means the reconstructions agree at that sample. Click the plot or use the sample slider.':'Click the plot or use the sample slider to inspect both reconstructions against the same reference.');
  if(byId('sl-pair-table-details').open)byId('sl-pair-table').replaceChildren(...data.rows.map(point=>{
    const row=document.createElement('tr');
    [point.address,point.reference,point.observed,point.a,point.b,point.errorA,point.errorB,point.difference].forEach((value,i)=>{const cell=document.createElement(i===0?'th':'td');if(i===0)cell.scope='row';cell.textContent=format(value);row.append(cell);});return row;
  }));
  if(!byId('sl-notebook').open)return;
  const series=view==='difference'?[[data.rows.map(row=>row.difference),'sl-difference']]:view==='error'?[[data.rows.map(row=>row.errorA),'sl-cosine'],[data.rows.map(row=>row.errorB),'sl-samples']]:[[a.reference,'sl-reference'],[aa.reconstruction,'sl-cosine'],[bb.reconstruction,'sl-samples']];
  const extent=limit(series.flatMap(([values])=>values));
  const yLabel=view==='error'?'Signed error':view==='difference'?'Difference B − A':'Amplitude';
  const plot=chart('sl-pair-chart',280,`${yLabel} at every address for saved reconstructions of identical reference and observed samples. Inspecting address ${pairAddress}.`,
    {xMax:a.config.n-1,yMin:-extent,yMax:extent,xLabel:'Sample address',yLabel});
  for(const [values,style] of series){trace(plot,values,style);plot.svg.append(node('circle',{cx:plot.x(pairAddress),cy:plot.y(values[pairAddress]),r:4,class:'sl-chart-point'}));}
  guide(plot,pairAddress);
}
byId('sl-pair-view').addEventListener('change',drawSavedComparison);
byId('sl-pair-address').addEventListener('input',event=>{pairAddress=Number(event.target.value);drawSavedComparison();});
byId('sl-pair-chart').addEventListener('click',event=>{if(runs.length<2||byId('sl-pair-plot').hidden)return;pairAddress=clickedIndex(event,'sl-pair-chart',savedResults[pairA].config.n-1);drawSavedComparison();});
byId('sl-pair-table-details').addEventListener('toggle',()=>{if(byId('sl-pair-table-details').open)drawSavedComparison();});
byId('sl-pair-largest').addEventListener('click',()=>{pairAddress=compareRuns(savedResults[pairA],savedResults[pairB]).maximumAddress;drawSavedComparison();byId('sl-pair-address').focus();});
byId('sl-pair-csv').addEventListener('click',()=>{
  try{const href=URL.createObjectURL(new Blob([comparisonCsv(savedResults[pairA],savedResults[pairB])],{type:'text/csv'})),link=document.createElement('a');
    link.href=href;link.download=`komorebi-comparison-${savedResults[pairA].config.n}.csv`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(href),1000);text('sl-notebook-status','Comparison CSV downloaded with reconstructions, signed errors, and B minus A at every address.');
  }catch(error){showError(error.message);}
});
root.querySelectorAll('[data-sl-starter]').forEach(button=>button.addEventListener('click',()=>{
  try{ensureResult();const entries=starterRuns(button.dataset.slStarter),first=runs.length,next=appendRuns(runs,entries);
    cancelStroke();editHistory.clear();drawing=false;config=settings(entries[0].settings);runs=next;pairA=first;pairB=first+1;pairAddress=Math.min(32,config.n-1);byId('sl-pair-view').value='overlay';
    saveNotebook();byId('sl-starters').open=false;byId('sl-notebook').open=true;renderNotebook();render();clearError();text('sl-edit-status','');status('Starter opened. Two comparison runs were added to the notebook.');byId('sl-compare-a').focus();
  }catch(error){showError(error.message);}
}));
byId('sl-save-run').addEventListener('click',()=>{
  try{const current=ensureResult();runs=appendRuns(runs,[{label:`${names[config.basis]} · ${config.budget}/${config.n} · run ${runs.length+1}`,settings:current.config}]);saveNotebook();byId('sl-notebook').open=true;renderNotebook(true);clearError();status(`Run ${runs.length} saved to the notebook.`);}
  catch(error){showError(error.message);}
});
byId('sl-notebook-rows').addEventListener('change',event=>{
  if(!event.target.matches('[data-run-name]'))return;
  const i=Number(event.target.dataset.runName);
  try{const next=runs.map((entry,j)=>j===i?{...entry,label:event.target.value}:entry);runs=readNotebook(writeNotebook(next));event.target.value=runs[i].label;saveNotebook();for(const id of ['sl-compare-a','sl-compare-b'])byId(id).options[i].textContent=runs[i].label;drawSavedComparison();clearError();}
  catch(error){showError(error.message);event.target.value=runs[i].label;}
});
byId('sl-notebook-rows').addEventListener('click',event=>{
  const button=event.target.closest('[data-notebook-action]');if(!button)return;const i=Number(button.dataset.run);
  if(button.dataset.notebookAction==='remove'){runs=runs.filter((_,j)=>j!==i);saveNotebook();renderNotebook(true);text('sl-notebook-status',notebookMemory?'Run removed from this tab. Download JSON to keep the notebook.':'Run removed. Notebook saved in this browser.');(byId('sl-notebook-rows').querySelector('[data-notebook-action=restore][data-run="'+Math.min(i,runs.length-1)+'"]')||byId('sl-save-run')).focus();return;}
  cancelStroke();editHistory.clear();drawing=false;config=settings(runs[i].settings);clearError();render();text('sl-edit-status','');status(`Restored ${runs[i].label}. Results were recomputed.`);byId('sl-draw').focus();
});
for(const [id,key] of [['sl-compare-a','a'],['sl-compare-b','b']])byId(id).addEventListener('change',event=>{if(key==='a')pairA=Number(event.target.value);else pairB=Number(event.target.value);drawSavedComparison();});
byId('sl-notebook').addEventListener('toggle',()=>{if(byId('sl-notebook').open)drawSavedComparison();});
function downloadNotebook(kind) {
  const content=kind==='json'?writeNotebook(runs):notebookCsv(runs,savedResults),href=URL.createObjectURL(new Blob([content],{type:kind==='json'?'application/json':'text/csv'}));
  const link=document.createElement('a');link.href=href;link.download='komorebi-signal-notebook.'+kind;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(href),1000);
  text('sl-notebook-status',kind==='json'?'Notebook JSON downloaded. Import it to restore all saved runs.':'Saved-run results CSV downloaded.');
}
byId('sl-notebook-export').addEventListener('click',()=>downloadNotebook('json'));
byId('sl-notebook-csv').addEventListener('click',()=>downloadNotebook('csv'));
byId('sl-notebook-file').addEventListener('change',async()=>{
  const input=byId('sl-notebook-file'),file=input.files[0];if(!file)return;
  try{if(file.size>65536)throw new RangeError('Use a notebook JSON file under 64 KiB.');const entries=readNotebook(await file.text());runs=appendRuns(runs,entries);saveNotebook();renderNotebook(true);clearError();text('sl-notebook-status',`${entries.length} runs imported and recomputed.`+(notebookMemory?' Download JSON to keep this tab’s notebook.':' Notebook saved in this browser.'));}
  catch(error){showError(error.message);}finally{input.value='';}
});
try{const saved=localStorage.getItem(notebookKey);if(saved)runs=readNotebook(saved);}
catch{notebookMemory=true;text('sl-notebook-status','The browser notebook could not be read. Import a notebook JSON file or save new runs for this tab.');}
window.addEventListener('storage',event=>{
  if(event.key!==notebookKey)return;
  try{runs=event.newValue?readNotebook(event.newValue):[];renderNotebook(true);text('sl-notebook-status','Notebook updated from another tab.');}
  catch{showError('A notebook update from another tab could not be read. The current runs are kept.');}
});
const shared=new URL(location.href).searchParams.get('lab');
if(shared!==null){try{config=decodeSettings(shared);status('Experiment restored from the link.');}catch(error){showError(error.message+' Default settings are shown.');}}
if(matchMedia('(max-width: 760px)').matches)byId('sl-setup').open=false;
root.querySelectorAll('fieldset,[data-sl-action],[data-sl-basis],#sl-export-kind').forEach(element=>{element.disabled=false;});
byId('sl-notebook-file').disabled=false;renderNotebook(true);render();
let resizeFrame;
const widths=new WeakMap();
const observer=new ResizeObserver(entries=>{
  let changed=false;
  for(const entry of entries){const width=Math.floor(entry.contentRect.width);if(width>0&&widths.get(entry.target)!==width)changed=true;widths.set(entry.target,width);}
  if(changed){cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>{if(root.dataset.ready==='true')drawAll();});}
});
root.querySelectorAll('.lab-diagram').forEach(element=>observer.observe(element));
