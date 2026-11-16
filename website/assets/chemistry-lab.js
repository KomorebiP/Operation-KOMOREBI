import {rational,mul,str,approximate,decode,analyze,probeView,verifyResponse,certificate,ERROR_FACTORS,SOURCE_ERRORS} from './chemistry-lab-core.mjs';

const root=document.getElementById('chemistry-lab');
const $=id=>document.getElementById('cl-'+id);
const format=value=>{
  const n=typeof value==='number'?value:approximate(value);
  return n===0?'0':Math.abs(n)<.001||Math.abs(n)>=10000?n.toExponential(5):Number(n.toPrecision(7)).toString();
};
const text=(id,value)=>{$(id).textContent=value;};
const node=(tag,value,attrs={})=>{const e=document.createElement(tag);if(value!==undefined)e.textContent=value;for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);return e;};
const descriptions={
  exact:'A published rational example in the positive-integral family. Its error caps are assumptions for the example.',
  h10:'The published nine-state frozen-core model derived from H10 integrals. Its stored action cap was measured against rational reference actions; the source is an exact Slater determinant.',
  zero:'A synthetic zero operator with a normalized source. It illustrates feasible positive-integral recovery when the sufficient all-compatible test fails.',
  unresolved:'A synthetic model with a negative interaction coefficient. With a nonzero remaining error budget, this decoder leaves positive-subclass feasibility unresolved.',
  inconsistent:'A synthetic cache with a nonzero component perpendicular to the model’s action image. Its default error cap is too small to explain that residual.'
};
let data,settings,latest,downloadURL;
const decodedCache=new Map(),verifiedCenters=new Map();

function table(destination,caption,headers,rows){
  const wrap=node('div',undefined,{class:'cl-table',tabindex:'0',role:'group','aria-label':caption+'; scroll horizontally if needed'});
  const table=node('table'),thead=node('thead'),tr=node('tr'),tbody=node('tbody');
  table.append(node('caption',caption));for(const h of headers)tr.append(node('th',h,{scope:'col'}));thead.append(tr);table.append(thead);
  for(const row of rows){const tr=node('tr');row.forEach((v,i)=>tr.append(node(i===0?'th':'td',String(v),i===0?{scope:'row'}:{})));tbody.append(tr);}
  table.append(tbody);wrap.append(table);destination.append(wrap);
}
function matrixTable(destination,caption,m){table(destination,caption,['Row',...m[0].map((_,j)=>String(j))],m.map((row,i)=>[i,...row.map(str)]));}
function map(destination,m,label,changes){
  const grid=node('div',undefined,{class:'cl-map',role:'img','aria-label':label+'; exact values in the table below'});
  m.forEach((row,i)=>row.forEach((v,j)=>grid.append(node('span',v.n===0n?'·':v.n<0n?'−':'+',{'data-sign':v.n===0n?'zero':v.n<0n?'negative':'positive','data-changed':String(Boolean(changes?.[i][j].n)),title:`Row ${i}, column ${j}: ${str(v)}`,'aria-hidden':'true'}))));
  destination.replaceChildren(grid);
}
function defaults(sample){return {example:sample.id,probes:2,error:2,source:Math.max(0,SOURCE_ERRORS.indexOf(sample.cache.source_radius||'0')),eta:data.etas.indexOf(sample.cache.eta)};}
function fromURL(){
  const p=new URL(location.href).searchParams,sample=data.samples.find(x=>x.id===p.get('example'))||data.samples[0],s=defaults(sample);
  for(const[k,min,max]of [['probes',1,3],['error',0,7],['source',0,4],['eta',0,4]]){
    const v=p.get(k);if(v!==null&&/^\d+$/.test(v)&&Number(v)>=min&&Number(v)<=max)s[k]=Number(v);
  }return s;
}
function permalink(){
  const url=new URL(location.href);for(const[k,v]of Object.entries(settings))url.searchParams.set(k,String(v));
  $('permalink').href=url.href;
  if(location.href!==url.href)history.replaceState(null,'',url.href);
}
function sync(){
  $('example').value=settings.example;
  for(const k of ['error','source','eta'])$(k).value=settings[k];
  for(const b of root.querySelectorAll('[data-probes]'))b.setAttribute('aria-pressed',String(Number(b.dataset.probes)===settings.probes));
}
function drawDisk(result,center,baseline){
  const box=$('disk');
  if(!result.consistent){box.replaceChildren(node('p','No disk: the observed cache is inconsistent with this error cap.'));text('disk-description','Increase the action-error budget to cover the residual, or correct the data or model.');return;}
  const radius=approximate(result.radius),windowRadius=Math.max(approximate(baseline.radius||rational(0))*2,1e-28);
  const clipped=radius>windowRadius,px=Math.min(1e6,120*radius/windowRadius);
  const svg=`<svg viewBox="0 0 320 290" role="img" aria-labelledby="cl-svg-title cl-svg-desc"><title id="cl-svg-title">Conditional response disk centered on the recovered response</title><desc id="cl-svg-desc">Radius ${format(radius)} per Hartree. The view extends ${format(windowRadius)} from the center in each direction.${clipped?' The disk extends beyond this window.':''}</desc><defs><clipPath id="cl-plot-clip"><rect x="40" y="15" width="240" height="240"/></clipPath></defs><rect x="40" y="15" width="240" height="240" fill="none" stroke="currentColor" opacity=".35"/><path d="M40 135H280M160 15V255" stroke="currentColor" stroke-dasharray="4 5" opacity=".45"/><g clip-path="url(#cl-plot-clip)"><circle cx="160" cy="135" r="${px}" fill="currentColor" fill-opacity=".12" stroke="currentColor" stroke-width="2.5"/></g><path d="M154 135h12M160 129v12" stroke="currentColor" stroke-width="2"/><text x="171" y="126" fill="currentColor" font-size="15">ĝ</text><text x="205" y="278" fill="currentColor" font-size="12">Re(g − ĝ)</text><text x="8" y="12" fill="currentColor" font-size="12">Im(g − ĝ)</text></svg>`;
  box.innerHTML=svg;
  text('disk-description',`Center ≈ ${format(center.real)} ${center.imaginary.n<0n?'−':'+'} ${format(Math.abs(approximate(center.imaginary)))}i per Hartree. Radius ≤ ${format(result.radius)} per Hartree. View: ±${format(windowRadius)} around the center. ${clipped?'The disk extends beyond this fixed window; use the bound below for its full size.':radius===0?'Zero radius gives a single response.':'The circle is an outer error enclosure.'}`);
}
function render(announce=false,probesChanged=true){
  const sample=data.samples.find(x=>x.id===settings.example);
  const decoded=decodedCache.get(sample.id)||decode(data,sample);decodedCache.set(sample.id,decoded);
  const epsilon=mul(rational(sample.cache.raw_error_radius),rational(ERROR_FACTORS[settings.error])),delta=rational(SOURCE_ERRORS[settings.source]),eta=data.etas[settings.eta];
  const result=analyze(data,sample,decoded,{epsilon,delta,eta});
  const centerKey=sample.id+':'+eta;
  if(!verifiedCenters.has(centerKey))verifiedCenters.set(centerKey,verifyResponse(decoded,sample,eta));
  const center=verifiedCenters.get(centerKey);
  sync();permalink();text('context',descriptions[sample.id]);
  text('error-value',`${format(epsilon)} Hartree · ${ERROR_FACTORS[settings.error]} × stored cap`);
  text('source-value',`${format(delta)} · dimensionless`);text('eta-value',`${format(eta)} Hartree`);
  for(const k of ['error','source','eta'])$(k).setAttribute('aria-valuetext',$(k+'-value').textContent);
  text('energy',`Fixed evaluation energy E ≈ ${format(sample.cache.energy)} Hartree. The source vector is the first determinant, with exact norm 1.`);
  const publishedSettings=settings.error===2&&str(delta)===(sample.cache.source_radius||'0')&&eta===sample.cache.eta;
  text('cap-note',sample.id==='h10'?(publishedSettings?'Published H10 arithmetic settings. The stored action cap is measured for this cache; physical approximation error remains unmeasured.':'Modified H10 experiment. The controls supply hypothetical caps. The published arithmetic guarantee applies only when its measured action cap and source assumptions are respected.'):'The chosen caps are assumptions. A small fitted residual does not establish that the true operator belongs to this family or that its error is below the chosen cap.');
  if(probesChanged){
    const view=probeView(data,decoded,settings.probes),stage=view.stage;
    text('rank',`${stage.rank} / 21`);text('nullity',String(stage.nullity));
    text('probe-result',settings.probes<3?`${settings.probes} ${settings.probes===1?'action leaves':'actions leave'} ${stage.nullity} independent hidden directions. Distinct operators can still give every displayed answer.`:'All 21 coefficients are determined. The third action removes every hidden direction in this family.');
    $('rank-track').replaceChildren(...Array.from({length:21},(_,i)=>node('span',undefined,{class:i<stage.rank?'known':'hidden-direction'})));
    map($('h-map'),decoded.h,'Reference operator matrix');map($('alternative-map'),view.alternative,settings.probes<3?'Distinct operator with the same available actions':'Unique recovered operator',view.witness);
    text('alternative-caption',settings.probes<3?'Indistinguishable operator H + ΔH':'The same unique operator H');
    const changed=view.witness.flatMap((row,i)=>row.map((v,j)=>({i,j,v}))).find(x=>x.v.n!==0n);
    text('witness-description',changed?`For example, entry (${changed.i}, ${changed.j}) changes by ${str(changed.v)} Hartree, yet ΔH vⱼ = 0 for every available probe. This pair belongs to the full integral-symmetry linear family; the witness does not certify positivity of both operators.`:'There is no nonzero family perturbation annihilating all three probes. The displayed ambiguity witness is the zero matrix.');
    $('probe-table').replaceChildren();matrixTable($('probe-table'),'The three fixed probe vectors',data.probes.map(r=>r.map(rational)));
    $('action-table').replaceChildren();table($('action-table'),'Exact reference actions; both operators agree on these columns',['Determinant row',...Array.from({length:settings.probes},(_,j)=>'H v'+(j+1))],view.actions.map((row,i)=>[i,...row.map(str)]));
    $('witness-table').replaceChildren();matrixTable($('witness-table'),'Exact ambiguity witness ΔH',view.witness);matrixTable($('witness-table'),'Exact reference operator H',decoded.h);matrixTable($('witness-table'),'Exact alternative operator H + ΔH',view.alternative);
  }
  const baseline=analyze(data,sample,decoded,{epsilon:sample.cache.raw_error_radius,delta:sample.cache.source_radius||'0',eta});
  drawDisk(result,center,baseline);
  text('consistency',!result.consistent?'Inconsistent: the residual exceeds the assumed action-error cap. No response enclosure is reported.':result.singleton?'Consistent singleton: the remaining operator uncertainty is zero.':'Consistent: the full linear family contains operators within this action-error budget.');
  const metrics=[['Cache residual d',format(Math.sqrt(approximate(result.residual2)))+' Hartree'],['Operator radius r_H',result.consistent?'≤ '+format(result.rH)+' Hartree':'No enclosure'],['Response radius R_g',result.consistent?'≤ '+format(result.radius)+' / Hartree':'No enclosure']];
  $('metrics').replaceChildren(...metrics.map(([k,v])=>{const d=node('div');d.append(node('dt',k),node('dd',v));return d;}));
  const feasibility=result.feasibility===true?'A positive-integral representative exists: the decoded estimate is compatible.':result.feasibility===false?'No positive-integral representative is compatible with this cache and cap.':'Positive-integral feasibility is unresolved by this decoder. A negative estimate with remaining uncertainty does not settle it.';
  text('positivity',feasibility+(result.consistent?(result.allPositive?' The sufficient margin also certifies a positive-integral representative for every compatible operator.':' The sufficient all-compatible margin fails; this alone does not decide positivity of every compatible operator.'):'')+' Positive integrals here mean a PSD Gram representative, without establishing actual Coulomb realizability.');
  $('bound-table').replaceChildren();table($('bound-table'),'Exact rational inputs and error bounds',['Quantity','Value'],[['ε',str(epsilon)],['δ',str(delta)],['η',eta],['d²',str(result.residual2)],['r_H² upper bound',result.consistent?str(result.radius2):'not reported'],['r_H rational upper bound',result.consistent?str(result.rH):'not reported'],['Operator contribution to R_g',result.consistent?str(result.operatorPart):'not reported'],['Source contribution to R_g',result.consistent?str(result.sourcePart):'not reported'],['R_g rational upper bound',result.consistent?str(result.radius):'not reported']]);
  latest=certificate(data,sample,decoded,result,center,{...settings});
  $('certificate').textContent=JSON.stringify(latest,null,2);
  const original=$('original-certificate');original.hidden=!sample.certificate_path;if(sample.certificate_path)original.href='assets/chemistry/stage14/'+sample.certificate_path;
  text('certificate-summary',result.consistent?'The experiment certificate includes the model, source identity, exact decoded operator, assumed caps, consistency and positivity results, and a rational response enclosure.':'The experiment certificate records inconsistency and deliberately omits a response enclosure.');
  text('provenance',`Fixture SHA-256: ${root.dataset.sha256}. Source archive SHA-256: ${data.archive_sha256}. ${sample.source_sha256?'Source cache SHA-256: '+sample.source_sha256+'.':'This is a synthetic boundary case generated from the published family.'}`);
  if(announce)text('announcement',`${sample.title}. ${settings.probes} probes. ${result.consistent?'Cache consistent. Response radius at most '+format(result.radius)+' per Hartree.':'Cache inconsistent; no response enclosure.'} ${result.feasibility===null?'Positive-integral feasibility unresolved.':''}`);
}
async function start(){
  $('retry').hidden=true;
  try{
    const response=await fetch(root.dataset.source);if(!response.ok)throw new Error('Fixture request failed.');
    const bytes=await response.arrayBuffer();
    const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
    if(hash!==root.dataset.sha256)throw new Error('Fixture identity mismatch.');
    data=JSON.parse(new TextDecoder().decode(bytes));if(data.version!==1)throw new Error('Unsupported fixture version.');
    settings=fromURL();render();$('experiment').hidden=false;$('load-status').hidden=true;
  }catch(error){text('load-status','The experiment could not load or verify its data. Retry below, or use the worked calculation and replay links.');$('retry').hidden=false;console.error(error);}
}
$('example').addEventListener('change',()=>{settings=defaults(data.samples.find(x=>x.id===$('example').value));render(true);});
$('reset').addEventListener('click',()=>{settings=defaults(data.samples.find(x=>x.id===settings.example));render(true);});
for(const b of root.querySelectorAll('[data-probes]'))b.addEventListener('click',()=>{settings.probes=Number(b.dataset.probes);render(true);});
for(const k of ['error','source','eta'])$(k).addEventListener('input',()=>{settings[k]=Number($(k).value);render(true,false);});
$('download').addEventListener('click',()=>{
  if(downloadURL)URL.revokeObjectURL(downloadURL);
  downloadURL=URL.createObjectURL(new Blob([JSON.stringify(latest,null,2)+'\n'],{type:'application/json'}));
  const a=node('a',undefined,{href:downloadURL,download:'chemistry-'+settings.example+'-certificate.json'});a.click();
});
$('retry').addEventListener('click',start);
addEventListener('popstate',()=>{if(data){settings=fromURL();render(true);}});
start();
