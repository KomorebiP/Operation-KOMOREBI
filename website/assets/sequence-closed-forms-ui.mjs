// Progressive exact-coefficient worksheet for the Closed Forms reading page.
// Author: Komorebi P. All arithmetic runs locally using BigInt.
import {MODE_DEFAULTS,MODE_LIMITS,MODE_FIELDS,computeExactWindow,
        exactWindowCSV,exactViewURL,readExactView} from './sequence-closed-forms-core.mjs';

const modes=[
  ['sparse','Sparse two-delay coefficients'],
  ['padovan','Padovan generating-function powers'],
  ['fourblock','Four-block logarithmic polynomials'],
  ['jet','Polynomially weighted binomial transform'],
  ['hankel','Weighted Hankel determinants'],
  ['beta_moments','Beta-binomial integer moments'],
  ['beta_hankel','Beta-binomial Hankel determinants'],
  ['differential_hankel','Higher-order differential Hankel determinants'],
  ['differential_moments','Differential moments and algebraic generating functions'],
  ['meixner','Meixner–Pollaczek integer polynomials']
];
const descriptions={
  p:['First delay p',1,16],q:['Second delay q',1,16],
  r:['Power r',-12,12],u:['Weight u',-12,12],v:['Weight v',-12,12],
  d:['Falling-factorial order d',0,8],lambda:['Binomial shift λ',-12,12],
  c:['Odd derivative weight c',-12,12],s:['Polynomial parameter s',-12,20],
  twox:['Integer coefficient 2x',-20,20],h:['Convolution power h',1,8],
  a:['Integer parameter a',-12,12],b:['Positive shape b',1,12],
  L:['Binomial support size L',0,12],
  a0:['Weight coefficient a₀',-12,12],a1:['Weight coefficient a₁',-12,12],
  a2:['Weight coefficient a₂',-12,12],a3:['Weight coefficient a₃',-12,12],
  c0:['Identity coefficient c₀',-12,12],c1:['First derivative c₁',-12,12],
  c2:['Second derivative c₂',-12,12],c3:['Third derivative c₃',-12,12]
};
const subtitle={
  sparse:'C(n) is a coefficient of (1-u z^p-v z^q)^(-r). Negative integer powers and zero weights are supported.',
  padovan:'The coefficient of ((1-z²)/(1-z²-z³))^h. The h=1 sequence begins 1, 0, 0, 1.',
  fourblock:'T_m(a) is indexed from m=1, with underlying analytic exponent 4m-1.',
  jet:'Exact binomial transforms, including the A163865 specialization at d=0, λ=c=1.',
  hankel:'W(N) is an exact determinant. Its value is invariant under binomial shifts of the moments.',
  beta_moments:'Integer unnormalized ordinary moments. Both shape parameters a and b must be positive.',
  beta_hankel:'Hankel transforms of integer unnormalized moments. Determinants vanish above support rank L+1.',
  differential_hankel:'Choose P(m)=a₀+a₁m+a₂m(m−1)+a₃m(m−1)(m−2) and Dₓ=c₀+c₁∂ₓ+c₂∂ₓ²+c₃∂ₓ³. Coefficients are preserved when switching to differential moments.',
  differential_moments:'Compute the exact moments μₙ=F_P[Dₓxⁿ] and their algebraic generating function. Coefficients are preserved when switching to differential Hankel determinants.',
  meixner:'Integer polynomial specializations of the classical Meixner–Pollaczek recurrence.'
};
function node(tag,text){
  const el=document.createElement(tag);
  if(text!==undefined)el.textContent=text;
  return el;
}
function numberField(key,title,min,max,value){
  const label=node('label'),caption=node('span',title),input=node('input'),error=node('span');
  input.type='number';input.id='cf-'+key;input.name=key;input.step='1';
  input.required=true;input.min=String(min);input.max=String(max);input.value=String(value);
  error.className='cf-field-error';error.hidden=true;
  label.htmlFor=input.id;label.className='cf-field';
  label.append(caption,input,error);
  return {label,caption,input,error,title};
}
export function mountClosedFormsCalculator(root,{href=location.href}={}){
  if(!root)throw Error('The exact calculator root is missing.');
  if(root.dataset.mounted==='true')return;
  root.dataset.mounted='true';
  const form=node('form');form.id='cf-form';form.noValidate=true;
  form.setAttribute('aria-label','Exact sequence calculator');
  const headline=node('p','Calculate exact integer values in your browser. Choose a construction, set its parameters, then calculate.');
  headline.className='cf-note';
  const modeLabel=node('label'),modeTitle=node('span','Construction'),modeSelect=node('select');
  modeSelect.id='cf-mode';modeSelect.name='mode';
  modeSelect.setAttribute('aria-describedby','cf-family-note');
  modeLabel.htmlFor=modeSelect.id;modeLabel.className='cf-field';
  for(const [value,title] of modes){
    const option=node('option',title);option.value=value;modeSelect.append(option);
  }
  modeLabel.append(modeTitle,modeSelect);
  const helper=node('p');helper.className='cf-note';helper.id='cf-family-note';
  form.append(headline,modeLabel,helper);
  const controls={},groups={},fields={};
  for(const [mode] of modes){
    const fieldset=node('fieldset'),legend=node('legend','Parameters');
    fieldset.className='cf-parameter-group';fieldset.dataset.mode=mode;
    const grid=node('div');grid.className='cf-grid';
    for(const key of MODE_FIELDS[mode]){
      const [title,min,max]=descriptions[key];
      const field=numberField(key,key==='a'&&mode.startsWith('beta_')?'Positive shape a':title,
        min,max,MODE_DEFAULTS[mode][key]);
      // The same symbolic parameter may occur in multiple families.
      field.input.id='cf-'+mode+'-'+key;
      field.error.id=field.input.id+'-error';
      field.caption.id=field.input.id+'-label';
      field.input.setAttribute('aria-labelledby',field.caption.id);
      field.label.htmlFor=field.input.id;
      if(key==='a'&&mode.startsWith('beta_'))field.input.min='1';
      controls[mode+':'+key]=field.input;
      fields[mode+':'+key]=field;
      grid.append(field.label);
    }
    fieldset.append(legend,grid);groups[mode]=fieldset;form.append(fieldset);
  }
  const windowRow=node('div');windowRow.className='cf-grid cf-window';
  for(const [key,title,max,value] of [
    ['start','First index',96,'0'],['count','Number of values',32,'12']
  ]){
    const field=numberField(key,title,key==='start'?0:1,max,value);
    field.error.id=field.input.id+'-error';
    field.caption.id=field.input.id+'-label';
    field.input.setAttribute('aria-labelledby',field.caption.id);
    field.input.setAttribute('aria-describedby','cf-bounds');
    controls[key]=field.input;fields[key]=field;windowRow.append(field.label);
  }
  form.append(windowRow);
  const bounds=node('p');bounds.className='cf-note';bounds.id='cf-bounds';
  form.append(bounds);
  const actions=node('div');actions.className='cf-actions';
  const compute=node('button','Calculate exact values');compute.type='submit';compute.id='cf-calculate';
  const reset=node('button','Restore defaults');reset.type='button';reset.id='cf-reset';
  actions.append(compute,reset);form.append(actions);
  const status=node('p');status.id='cf-status';
  status.className='cf-status';status.setAttribute('role','status');
  status.setAttribute('aria-live','polite');status.setAttribute('aria-atomic','true');
  const result=node('section');result.id='cf-results';result.hidden=true;
  result.setAttribute('aria-labelledby','cf-result-title');
  const resultTitle=node('h3','Exact indexed values'),explain=node('p'),verified=node('p');
  resultTitle.id='cf-result-title';
  explain.className='cf-note';verified.className='cf-note';verified.id='cf-verification';
  const region=node('div');region.className='cf-table-scroll';
  region.tabIndex=0;region.setAttribute('role','region');
  region.setAttribute('aria-label','Scrollable exact integer sequence table');
  const table=node('table'),caption=node('caption');caption.className='cf-visually-hidden';
  const head=node('thead'),headers=node('tr');
  for(const title of ['Index','Exact integer']){const th=node('th',title);th.scope='col';headers.append(th);}
  head.append(headers);
  const body=node('tbody');body.id='cf-table-values';
  table.append(caption,head,body);region.append(table);
  const method=node('details');method.id='cf-method';method.className='cf-details';
  method.append(node('summary','How these values are calculated'),verified);
  // Generating-function evidence is optional and hidden for other modes.
  // Keep it collapsible so long polynomial formulas do not crowd results.
  const ogf=node('details');ogf.id='cf-ogf';ogf.hidden=true;
  const ogfTitle=node('summary','Exact algebraic moment generating function');
  const ogfInfo=node('p');ogfInfo.id='cf-ogf-info';ogfInfo.className='cf-note';
  const ogfRegion=node('pre');ogfRegion.id='cf-ogf-formula';
  ogfRegion.tabIndex=0;ogfRegion.setAttribute('role','region');
  ogfRegion.setAttribute('aria-label','Exact moment generating-function formula');
  const ogfCode=node('code');ogfRegion.append(ogfCode);
  const ogfHelp=node('p','The numerator is computed exactly from the displayed parameters. A polynomial-weighted differential moment sequence has an algebraic generating function; that fact alone does not imply a rational generating function for its Hankel determinants.');
  ogfHelp.className='cf-note';
  const ogfActions=node('div');ogfActions.className='cf-actions';
  const ogfCopy=node('button','Copy generating function');ogfCopy.type='button';
  ogfCopy.id='cf-ogf-copy';ogfActions.append(ogfCopy);
  ogf.append(ogfTitle,ogfInfo,ogfRegion,ogfHelp,ogfActions);
  const exports=node('div');exports.className='cf-actions';
  const csv=node('button','Download exact CSV');csv.type='button';csv.id='cf-download';
  const copy=node('button','Copy exact values');copy.type='button';copy.id='cf-copy';
  const link=node('button','Copy reproducible link');link.type='button';link.id='cf-link';
  exports.append(csv,copy,link);
  const fallback=node('textarea');fallback.id='cf-fallback';fallback.readOnly=true;fallback.hidden=true;
  fallback.setAttribute('aria-label','Text selected for manual copying');
  fallback.rows=4;
  const warning=node('p','Spreadsheet programs may round large integers. Import the exact_integer column as text.');
  warning.className='cf-note';
  result.append(resultTitle,explain,region,exports,warning,ogf,method,fallback);
  root.append(form,status,result);
  let latest=null,latestView=null,renderedMode='',generation=0,pendingWorker=null,pendingFallback=null;
  function rawValues(){
    const mode=modeSelect.value,raw={mode,start:controls.start.value,count:controls.count.value};
    for(const key of MODE_FIELDS[mode])raw[key]=controls[mode+':'+key].value;
    return raw;
  }
  function sync(){
    const mode=modeSelect.value,limits=MODE_LIMITS[mode];
    for(const [key,group] of Object.entries(groups)){
      group.hidden=key!==mode;group.disabled=key!==mode;
    }
    helper.textContent=subtitle[mode]+(mode==='differential_hankel'
      ? ' Exact determinant sizes 0–'+limits.maxIndex+'.' : '');
    bounds.textContent=(mode.endsWith('hankel')
      ? 'The index is the determinant size; size 0 has value 1. '
      : mode==='fourblock' ? 'Indices begin at m=1. ' : 'Indices begin at n=0. ')+
      'Maximum index: '+limits.maxIndex+'. Choose up to '+limits.maxCount+
      ' values without exceeding that index.';
    controls.start.min=mode==='fourblock'?'1':'0';
    controls.start.max=String(limits.maxIndex);
    controls.count.max=String(limits.maxCount);
  }
  function setStatus(message,error=false){
    status.textContent=message;status.dataset.error=String(error);
  }
  function clearFieldError(field){
    field.input.removeAttribute('aria-invalid');
    field.input.removeAttribute('aria-errormessage');
    if(field.input===controls.start||field.input===controls.count)
      field.input.setAttribute('aria-describedby','cf-bounds');
    else field.input.removeAttribute('aria-describedby');
    field.error.hidden=true;field.error.textContent='';
  }
  function clearErrors(){for(const field of Object.values(fields))clearFieldError(field);}
  function showFieldError(field,message){
    field.error.textContent=message;field.error.hidden=false;
    field.input.setAttribute('aria-invalid','true');
    field.input.setAttribute('aria-errormessage',field.error.id);
    field.input.setAttribute('aria-describedby',
      [field.input===controls.start||field.input===controls.count?'cf-bounds':'',field.error.id]
      .filter(Boolean).join(' '));
  }
  function validateFields(){
    const mode=modeSelect.value,active=MODE_FIELDS[mode].map(key=>fields[mode+':'+key]);
    active.push(fields.start,fields.count);
    const invalid=[];
    for(const field of active){
      const text=field.input.value,value=Number(text);
      let message='';
      if(!/^-?(0|[1-9][0-9]*)$/.test(text))message=field.title+' must be an integer.';
      else if(!Number.isSafeInteger(value)||value<Number(field.input.min)||value>Number(field.input.max))
        message=field.title+' must be between '+field.input.min+' and '+field.input.max+'.';
      if(message){showFieldError(field,message);invalid.push(field);}
    }
    if(!invalid.length&&Number(controls.start.value)+Number(controls.count.value)-1>MODE_LIMITS[mode].maxIndex){
      const field=fields.count;
      showFieldError(field,'The last index must not exceed '+MODE_LIMITS[mode].maxIndex+
        '. From index '+controls.start.value+', choose at most '+
        (MODE_LIMITS[mode].maxIndex-Number(controls.start.value)+1)+' values.');
      invalid.push(field);
    }
    return invalid;
  }
  function shareDifferentialParameters(){
    const mode=modeSelect.value;
    if(mode!=='differential_hankel'&&mode!=='differential_moments')return;
    const other=mode==='differential_hankel'?'differential_moments':'differential_hankel';
    for(const key of MODE_FIELDS[mode])controls[other+':'+key].value=controls[mode+':'+key].value;
  }
  function setBusy(busy){
    form.setAttribute('aria-busy',String(busy));compute.disabled=busy;
    compute.textContent=busy?'Calculating exact values…':'Calculate exact values';
  }
  function cancelPending(){
    generation++;
    if(pendingWorker){pendingWorker.terminate();pendingWorker=null;}
    if(pendingFallback!==null){clearTimeout(pendingFallback);pendingFallback=null;}
    setBusy(false);
  }
  function invalidate(){
    cancelPending();latest=null;latestView=null;result.hidden=true;fallback.hidden=true;
  }
  function render(data){
    if(renderedMode!==data.mode)ogf.open=false;
    renderedMode=data.mode;
    latest=data;latestView={mode:data.mode,start:data.start,count:data.count,...data.parameters};
    body.replaceChildren();
    for(const row of data.rows){
      const tr=node('tr'),index=node('th',String(row.index)),value=node('td');
      index.scope='row';const code=node('code',row.value);value.append(code);
      tr.append(index,value);body.append(tr);
    }
    resultTitle.textContent=data.rows.length+' exact indexed value'+(data.rows.length===1?'':'s');
    caption.textContent=modes.find(([mode])=>mode===data.mode)[1]+', indices '+data.start+
      ' through '+(data.start+data.count-1)+'.';
    explain.textContent=data.description;
    verified.textContent=data.verification;
    ogf.hidden=!data.generatingFunction;
    if(data.generatingFunction){
      const evidence=data.generatingFunction;
      ogfCode.textContent=evidence.expression;
      ogfInfo.textContent='Numerator degree ≤ '+evidence.degreeBound+
        '; effective polynomial weight degree '+evidence.weightDegree+
        '; effective differential order '+evidence.operatorOrder+'. '+
        (evidence.initialZeroMoments===null
          ? 'The moment sequence is identically zero; no forward division is performed.'
          : 'First nonzero moment index '+evidence.initialZeroMoments+
            '; regularized polynomial recurrence order ≤ '+
            evidence.regularizedRecurrenceOrderBound+'.');
    }
    fallback.hidden=true;result.hidden=false;
    setStatus('Computed '+data.rows.length+' exact integers. First index '+data.start+
      ', final index '+(data.start+data.count-1)+'.');
  }
  function calculate({focusErrors=false}={}){
    invalidate();clearErrors();shareDifferentialParameters();
    const invalid=validateFields();
    if(invalid.length){
      setStatus(invalid[0].error.textContent,true);
      if(focusErrors)invalid[0].input.focus();
      return;
    }
    const raw=rawValues(),id=generation;
    function finish(data,error){
      if(id!==generation)return;
      if(pendingWorker){pendingWorker.terminate();pendingWorker=null;}
      setBusy(false);
      if(error){setStatus('Calculation failed: '+error,true);return;}
      render(data);
    }
    function runHere(){
      if(id!==generation)return;
      try{finish(computeExactWindow(raw));}catch(error){finish(null,error.message);}
    }
    if(raw.mode!=='differential_hankel'||Number(raw.start)+Number(raw.count)-1<=12){runHere();return;}
    setBusy(true);
    setStatus('Calculating exact determinants. You can change the parameters to cancel this calculation.');
    function fallbackHere(){
      if(id!==generation)return;
      if(pendingWorker){pendingWorker.terminate();pendingWorker=null;}
      setStatus('Background execution is unavailable. Calculating exact determinants on this page.');
      pendingFallback=setTimeout(()=>{pendingFallback=null;runHere();},0);
    }
    try{
      pendingWorker=new Worker(new URL('./sequence-closed-forms-worker.mjs',import.meta.url),{type:'module'});
      pendingWorker.onmessage=event=>{
        if(event.data.id===id)finish(event.data.report,event.data.error);
      };
      pendingWorker.onerror=event=>{event.preventDefault();fallbackHere();};
      pendingWorker.postMessage({id,raw});
    }catch{fallbackHere();}
  }
  form.addEventListener('submit',event=>{event.preventDefault();calculate({focusErrors:true});});
  form.addEventListener('input',event=>{
    if(event.target===modeSelect)return;
    shareDifferentialParameters();invalidate();
    const field=Object.values(fields).find(field=>field.input===event.target);
    if(field)clearFieldError(field);
    setStatus('Parameters changed. Calculate exact values to update the results.');
  });
  modeSelect.addEventListener('change',()=>{
    const next=MODE_DEFAULTS[modeSelect.value];
    controls.start.value=next.start;controls.count.value=next.count;
    sync();calculate();
  });
  reset.addEventListener('click',()=>{
    const values=MODE_DEFAULTS[modeSelect.value];
    controls.start.value=values.start;controls.count.value=values.count;
    for(const key of MODE_FIELDS[modeSelect.value])controls[modeSelect.value+':'+key].value=values[key];
    sync();calculate();
  });
  async function doCopy(text,label){
    const id=generation;
    try{
      if(!navigator.clipboard?.writeText)throw Error('Clipboard permission is unavailable.');
      await navigator.clipboard.writeText(text);
      if(id!==generation)return;
      fallback.hidden=true;
      setStatus('Copied '+label+'.');
    }catch{
      if(id!==generation)return;
      fallback.value=text;fallback.hidden=false;fallback.focus();fallback.select();
      setStatus('Clipboard access is unavailable. Use the selected text below to copy '+label+'.');
    }
  }
  ogfCopy.addEventListener('click',()=>{
    if(!latest?.generatingFunction)return;
    doCopy(latest.generatingFunction.expression+'\n','the generating function');
  });
  copy.addEventListener('click',()=>{
    if(!latest)return;
    doCopy('index\texact_integer\n'+latest.rows.map(row=>row.index+'\t'+row.value).join('\n')+'\n','the exact value table');
  });
  link.addEventListener('click',()=>{
    if(!latest)return;
    doCopy(exactViewURL(location.href,latestView),'the reproducible link');
  });
  csv.addEventListener('click',()=>{
    if(!latest)return;
    try{
      const blob=new Blob([exactWindowCSV(latest)],{type:'text/csv;charset=utf-8'});
      const url=URL.createObjectURL(blob),anchor=node('a');
      anchor.href=url;anchor.download='komorebi-exact-'+latest.mode+'-'+latest.start+'.csv';
      document.body.append(anchor);anchor.click();anchor.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      setStatus('Exact CSV export prepared. Decimal integer strings are preserved.');
    }catch(error){setStatus('CSV export failed: '+error.message,true);}
  });
  let linkedError='';
  try{
    const values=readExactView(href);
    if(values){
      modeSelect.value=values.mode;
      controls.start.value=values.start;controls.count.value=values.count;
      for(const key of MODE_FIELDS[values.mode])controls[values.mode+':'+key].value=values[key];
    }else{
      const defaults=MODE_DEFAULTS.sparse;
      modeSelect.value='sparse';controls.start.value=defaults.start;controls.count.value=defaults.count;
    }
  }catch(error){linkedError=error.message;modeSelect.value='sparse';}
  sync();calculate();
  root.querySelector(':scope > .cf-placeholder')?.remove();
  if(linkedError)setStatus('The shared calculator view was rejected: '+linkedError+
    ' Showing the default exact construction.',true);
}
