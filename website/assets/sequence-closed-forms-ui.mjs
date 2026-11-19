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
  beta_moments:'Integer unnormalized ordinary moments, not rational probability moments. Parameter a must be positive.',
  beta_hankel:'Hankel transforms of integer unnormalized moments. Determinants vanish above support rank L+1.',
  differential_hankel:'Choose P(m)=a₀+a₁m+a₂m(m−1)+a₃m(m−1)(m−2) and L=ΣcₖF_P[dᵏ/dxᵏ]. Exact sizes 0–12; the general theorem covers arbitrary finite orders.',
  meixner:'Integer polynomial specializations of the classical Meixner–Pollaczek recurrence.'
};
function node(tag,text){
  const el=document.createElement(tag);
  if(text!==undefined)el.textContent=text;
  return el;
}
function numberField(key,title,min,max,value){
  const label=node('label'),caption=node('span',title),input=node('input');
  input.type='number';input.id='cf-'+key;input.name=key;input.step='1';
  input.min=String(min);input.max=String(max);input.value=String(value);
  label.htmlFor=input.id;label.className='cf-field';
  label.append(caption,input);
  return {label,input};
}
export function mountClosedFormsCalculator(root,{href=location.href}={}){
  if(!root)throw Error('The exact calculator root is missing.');
  if(root.dataset.mounted==='true')return;
  root.dataset.mounted='true';
  const form=node('form');form.id='cf-form';form.noValidate=true;
  const headline=node('p','All values are computed as exact decimal integers in this browser. No OEIS request or network calculation is made.');
  headline.className='cf-note';
  const modeLabel=node('label'),modeTitle=node('span','Construction'),modeSelect=node('select');
  modeSelect.id='cf-mode';modeSelect.name='mode';
  modeLabel.htmlFor=modeSelect.id;modeLabel.className='cf-field';
  for(const [value,title] of modes){
    const option=node('option',title);option.value=value;modeSelect.append(option);
  }
  modeLabel.append(modeTitle,modeSelect);
  const helper=node('p');helper.className='cf-note';helper.id='cf-family-note';
  form.append(headline,modeLabel,helper);
  const controls={},groups={};
  for(const [mode] of modes){
    const fieldset=node('fieldset'),legend=node('legend','Parameters');
    fieldset.className='cf-parameter-group';fieldset.dataset.mode=mode;
    const grid=node('div');grid.className='cf-grid';
    for(const key of MODE_FIELDS[mode]){
      const [title,min,max]=descriptions[key];
      const field=numberField(key,title,min,max,MODE_DEFAULTS[mode][key]);
      // The same symbolic parameter may occur in multiple families.
      field.input.id='cf-'+mode+'-'+key;
      field.label.htmlFor=field.input.id;
      controls[mode+':'+key]=field.input;
      grid.append(field.label);
    }
    fieldset.append(legend,grid);groups[mode]=fieldset;form.append(fieldset);
  }
  const windowRow=node('div');windowRow.className='cf-grid cf-window';
  for(const [key,title,max,value] of [
    ['start','First index',96,'0'],['count','Number of values',32,'12']
  ]){
    const field=numberField(key,title,key==='start'?0:1,max,value);
    controls[key]=field.input;windowRow.append(field.label);
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
  status.setAttribute('aria-live','polite');
  const result=node('section');result.id='cf-results';result.hidden=true;
  result.setAttribute('aria-label','Exact calculated sequence values');
  const resultTitle=node('h3','Exact indexed values'),explain=node('p'),verified=node('p');
  explain.className='cf-note';verified.className='cf-note';verified.id='cf-verification';
  const region=node('div');region.className='cf-table-scroll';
  region.tabIndex=0;region.setAttribute('role','region');
  region.setAttribute('aria-label','Scrollable exact integer sequence table');
  const table=node('table');
  const head=node('thead'),headers=node('tr');
  for(const title of ['Index','Exact integer']){const th=node('th',title);th.scope='col';headers.append(th);}
  head.append(headers);
  const body=node('tbody');body.id='cf-table-values';
  table.append(head,body);region.append(table);
  const exports=node('div');exports.className='cf-actions';
  const csv=node('button','Download exact CSV');csv.type='button';csv.id='cf-download';
  const copy=node('button','Copy exact values');copy.type='button';copy.id='cf-copy';
  const link=node('button','Copy reproducible link');link.type='button';link.id='cf-link';
  exports.append(csv,copy,link);
  const fallback=node('textarea');fallback.id='cf-fallback';fallback.readOnly=true;fallback.hidden=true;
  fallback.setAttribute('aria-label','Select and copy the exact values or link');
  fallback.rows=4;
  const warning=node('p','Spreadsheet programs may round large integers. Import the exact_integer column as text.');
  warning.className='cf-note';
  result.append(resultTitle,explain,verified,region,exports,fallback,warning);
  root.append(form,status,result);
  let latest=null;
  function rawValues(){
    const mode=modeSelect.value,raw={mode,start:controls.start.value,count:controls.count.value};
    for(const key of MODE_FIELDS[mode])raw[key]=controls[mode+':'+key].value;
    return raw;
  }
  function sync(){
    const mode=modeSelect.value,limits=MODE_LIMITS[mode];
    for(const [key,group] of Object.entries(groups))group.hidden=key!==mode;
    helper.textContent=subtitle[mode];
    bounds.textContent='Original indices, not inferred Taylor degrees. Maximum index: '+
      limits.maxIndex+'. Maximum window: '+limits.maxCount+' values.';
    controls.start.min=mode==='fourblock'?'1':'0';
    controls.start.max=String(limits.maxIndex);
    controls.count.max=String(limits.maxCount);
  }
  function render(data){
    latest=data;body.replaceChildren();
    for(const row of data.rows){
      const tr=node('tr'),index=node('th',String(row.index)),value=node('td');
      index.scope='row';const code=node('code',row.value);value.append(code);
      tr.append(index,value);body.append(tr);
    }
    resultTitle.textContent=data.rows.length+' exact indexed value'+(data.rows.length===1?'':'s');
    explain.textContent=data.description;
    verified.textContent=data.verification;
    fallback.hidden=true;result.hidden=false;
    status.textContent='Computed '+data.rows.length+' exact integers. First index '+data.start+
      ', final index '+(data.start+data.count-1)+'.';
  }
  function calculate(){
    try{
      const data=computeExactWindow(rawValues());
      render(data);
    }catch(error){
      latest=null;result.hidden=true;
      status.textContent=error.message;
    }
  }
  form.addEventListener('submit',event=>{event.preventDefault();calculate();});
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
  async function doCopy(text){
    try{
      if(!navigator.clipboard?.writeText)throw Error('Clipboard permission is unavailable.');
      await navigator.clipboard.writeText(text);
      fallback.hidden=true;
      status.textContent='Copied exact values or the reproducible view link.';
    }catch{
      fallback.value=text;fallback.hidden=false;fallback.focus();fallback.select();
      status.textContent='Clipboard access is unavailable. The text is selected below for manual copying.';
    }
  }
  copy.addEventListener('click',()=>{
    if(!latest)return;
    doCopy('index\texact_integer\n'+latest.rows.map(row=>row.index+'\t'+row.value).join('\n')+'\n');
  });
  link.addEventListener('click',()=>{
    if(!latest)return;
    doCopy(exactViewURL(location.href,rawValues()));
  });
  csv.addEventListener('click',()=>{
    if(!latest)return;
    try{
      const blob=new Blob([exactWindowCSV(latest)],{type:'text/csv;charset=utf-8'});
      const url=URL.createObjectURL(blob),anchor=node('a');
      anchor.href=url;anchor.download='komorebi-exact-'+latest.mode+'-'+latest.start+'.csv';
      document.body.append(anchor);anchor.click();anchor.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      status.textContent='Exact CSV export prepared. Decimal integer strings are preserved.';
    }catch(error){status.textContent='CSV export failed: '+error.message;}
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
  if(linkedError)status.textContent='The shared calculator view was rejected: '+linkedError+
    ' Showing the default exact construction.';
}
