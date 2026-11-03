import {analyzeRecovery,validateExperiment,repairExperiment,encodeRecovery,decodeRecovery,PRESETS,presetExperiment} from './recovery-lab-core.mjs';

const byId=id=>document.getElementById(id);
const write=(id,value)=>{byId(id).textContent=value;};
const root=byId('recovery-lab');
const subscript=value=>String(value).replace(/\d/g,v=>'₀₁₂₃₄₅₆₇₈₉'[Number(v)]);
const vector=values=>'('+values.join(', ')+')';
let state=presetExperiment('sum'), result, undo=null, invalid=false, activePreset='sum';
function node(tag,content,className) {
  const element=document.createElement(tag);
  if (content!==undefined) element.textContent=content;
  if (className) element.className=className;
  return element;
}
function button(label,attrs={}) {
  const element=node('button',label);element.type='button';
  for (const [key,value] of Object.entries(attrs)) element.setAttribute(key,value);
  return element;
}
function status(message) { write('rl-status',message);byId('rl-share-fallback').hidden=true; }
function formula(text) { return node('div',text,'rl-formula'); }
function expression(coefficients,names) {
  const terms=coefficients.map((v,i)=>v==='0' ? null : `${v.includes('/') || v.startsWith('-') ? '('+v+')' : v}·${names[i]}`).filter(Boolean);
  return terms.length ? terms.join(' + ').replace(/\+ \(-/g,'− (') : '0';
}
function table(headers,rows,caption) {
  const element=node('table'),head=node('thead'),body=node('tbody'),tr=node('tr');
  element.append(node('caption',caption));
  headers.forEach(text=>{const th=node('th',text);th.scope='col';tr.append(th);});head.append(tr);
  rows.forEach(values=>{
    const row=node('tr');values.forEach((value,i)=>{const cell=node(i===0?'th':'td',value);if(i===0)cell.scope='row';row.append(cell);});body.append(row);
  });element.append(head,body);return element;
}
function editMatrix(kind) {
  const rows=state[kind], element=node('table'),head=node('thead'),body=node('tbody'),tr=node('tr');
  const title=kind==='R'?'Measurement':'Question';
  const caption=node('caption',kind==='R'?'Measurement coefficients · R':'Question coefficients · F');
  element.append(caption);
  const headers=[title,...Array.from({length:state.n},(_,j)=>'x'+subscript(j+1)),'Remove'];
  if(kind==='R') headers.splice(1,0,'Keep');
  headers.forEach(label=>{const cell=node('th',label);cell.scope='col';tr.append(cell);});head.append(tr);
  rows.forEach((values,i)=>{
    const row=node('tr'),label=node('th',(kind==='R'?'y':'F')+subscript(i+1));label.scope='row';row.append(label);
    if(kind==='R') {
      row.dataset.enabled=String(state.enabled[i]);
      const cell=node('td'),check=node('input');check.type='checkbox';check.checked=state.enabled[i];
      check.id=`rl-keep-${i}`;check.dataset.keep=i;check.setAttribute('aria-label',`Use measurement ${i+1}`);
      cell.append(check);row.append(cell);
    }
    values.forEach((value,j)=>{
      const cell=node('td'),input=node('input');input.type='text';input.value=value;input.maxLength=9;
      input.id=`rl-${kind}-${i}-${j}`;input.dataset.matrix=kind;input.dataset.row=i;input.dataset.column=j;
      input.setAttribute('aria-label',`${title} ${i+1}, coefficient of input ${j+1}`);
      input.setAttribute('aria-describedby','rl-entry-help rl-error');input.autocomplete='off';input.spellcheck=false;
      cell.append(input);row.append(cell);
    });
    const cell=node('td'),remove=button('×',{'aria-label':`Remove ${title.toLowerCase()} ${i+1}`,'data-remove':kind,'data-row':i});
    remove.className='rl-remove';
    remove.disabled=rows.length===1;cell.append(remove);row.append(cell);body.append(row);
  });element.append(head,body);
  byId(kind==='R'?'rl-r-matrix':'rl-f-matrix').replaceChildren(element);
}
function baseControls() {
  byId('rl-base-inputs').replaceChildren(...state.x.map((value,i)=>{
    const host=node('div',undefined,'lab-slider'),label=node('label','Base input x'+subscript(i+1));
    label.htmlFor='rl-base-'+i;const output=node('output',value);output.id='rl-base-value-'+i;output.setAttribute('for',label.htmlFor);
    const input=node('input');input.type='range';input.id=label.htmlFor;input.min=-4;input.max=4;input.step=1;input.value=value;input.dataset.base=i;
    label.append(output);host.append(label,input);return host;
  }));
  byId('rl-offset').value=state.t;write('rl-offset-value',state.t);
}
function setControls() {
  byId('rl-dimension').value=state.n;editMatrix('R');editMatrix('F');baseControls();
  byId('rl-controls').disabled=false;
  byId('rl-error').hidden=true;invalid=false;
  render();
}
function updateAvailability() {
  for (const id of ['rl-share','rl-export']) byId(id).disabled=invalid;
  byId('rl-dimension').disabled=invalid;
  byId('rl-add-measurement').disabled=invalid||state.R.length>=4;
  byId('rl-add-question').disabled=invalid||state.F.length>=3;
  root.querySelectorAll('[data-remove]').forEach(b=>{b.disabled=invalid||state[b.dataset.remove].length===1;});
  root.querySelectorAll('[data-rl-question]').forEach(b=>{b.disabled=invalid;});
  byId('rl-repair').disabled=invalid||result.repair.additional===0;
  byId('rl-undo').disabled=invalid||undo===null;
  byId('rl-motion-controls').disabled=invalid;
  byId('rl-offset').disabled=invalid||result.nullity===0;
}
function readDraft() {
  const candidate={...state,R:state.R.map(r=>r.slice()),F:state.F.map(r=>r.slice()),enabled:state.enabled.slice()};
  let bad=false;
  root.querySelectorAll('[data-matrix]').forEach(input=>{
    candidate[input.dataset.matrix][Number(input.dataset.row)][Number(input.dataset.column)]=input.value;
    const valid=input.value.length<=9 && /^-?\d{1,2}(?:\/[1-9]\d?)?$/.test(input.value.trim());
    input.setAttribute('aria-invalid',String(!valid));bad ||= !valid;
  });
  root.querySelectorAll('[data-keep]').forEach(input=>{candidate.enabled[Number(input.dataset.keep)]=input.checked;input.closest('tr').dataset.enabled=String(input.checked);});
  try {
    if(bad) throw new RangeError('Use integers from −99 to 99, or fractions with denominator 1–99.');
    state=validateExperiment(candidate);invalid=false;activePreset=null;undo=null;
    byId('rl-error').hidden=true;write('rl-repair-status','');render();
  } catch(error) {
    invalid=true;write('rl-error',error.message+' Results keep the last valid calculation. Complete the entries to update or share it.');
    byId('rl-error').hidden=false;updateAvailability();
  }
}
function renderCertificate() {
  const selected=result.questions[state.question],host=byId('rl-certificate');
  const names=state.R.map((_,i)=>'y'+subscript(i+1));
  const heading=node('h3',selected.recoverable?'An exact recovery rule':'An explicit obstruction');
  if(selected.recoverable) {
    host.replaceChildren(heading,formula('F'+subscript(state.question+1)+'(x) = '+expression(selected.weights,names)),
      node('p','The displayed weights multiply the original measurement rows to give this question row exactly. Disabled measurements have weight zero.'),
      formula(vector(selected.weights)+' R = '+vector(state.F[state.question])));
  } else {
    host.replaceChildren(heading,formula('w = '+vector(selected.witness)),
      formula('R_active w = 0\nF'+subscript(state.question+1)+' w = '+selected.change+' ≠ 0'),
      node('p','Your measurements erase this direction, while the selected question changes along it. For any x, the inputs x and x + w have identical measurements and different answers.'));
  }
}
function chart(id,labels,first,second) {
  const ns='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(ns,'svg');const width=480,height=Math.max(125,labels.length*56+36);
  svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
  const numeric=values=>values.map(v=>{const [n,d=1]=v.split('/');return Number(n)/Number(d);});
  const a=numeric(first),b=numeric(second),bound=Math.max(1,...a.map(Math.abs),...b.map(Math.abs));
  const px=value=>245+value/bound*185;
  function shape(tag,attrs,text) {const element=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))element.setAttribute(k,v);if(text!==undefined)element.textContent=text;svg.append(element);}
  shape('line',{x1:px(0),x2:px(0),y1:10,y2:height-25,class:'rl-plot-axis'});
  labels.forEach((label,i)=>{
    const y=30+i*56;shape('text',{x:5,y:y+4},label);
    shape('line',{x1:60,x2:430,y1:y,y2:y,class:'rl-plot-axis'});
    shape('line',{x1:px(a[i]),x2:px(b[i]),y1:y,y2:y,class:'rl-plot-line'});
    shape('circle',{cx:px(a[i]),cy:y,r:6,class:'rl-plot-base'});
    shape('circle',{cx:px(b[i]),cy:y,r:10,class:'rl-plot-moved'});
  });
  if(!labels.length)shape('text',{x:20,y:50},'No measurements enabled. Every input looks the same.');
  shape('text',{x:245,y:height-5,'text-anchor':'middle'},'0');
  const container=byId(id);container.setAttribute('aria-label',labels.length?labels.map((v,i)=>`${v}: ${first[i]} at x; ${second[i]} at the moved input.`).join(' '):'No enabled measurements.');container.replaceChildren(svg);
}
function renderMotion() {
  const m=result.motion,selected=result.questions[state.question];
  const note=result.nullity===0?'There are no invisible directions: these measurements determine the entire input. The two displayed inputs coincide.':
    `Direction w = ${vector(m.direction)}. ${selected.recoverable?'The selected question stays fixed along every invisible direction.':'The selected question changes by t × ('+selected.change+').'}`+
    (state.t===0?' At t = 0 the two inputs coincide; move the slider to separate them.':'');
  write('rl-motion-note',note);
  chart('rl-input-chart',state.x.map((_,i)=>'x'+subscript(i+1)),m.x,m.moved);
  chart('rl-summary-chart',result.active.map(i=>'y'+subscript(i+1)),m.summary,m.movedSummary);
  const rows=[['Input vector',vector(m.x),vector(m.moved)],['Enabled summary',vector(m.summary),vector(m.movedSummary)],
    ...state.F.map((_,i)=>['Question F'+subscript(i+1),m.answers[i],m.movedAnswers[i]])];
  byId('rl-values').replaceChildren(...rows.map(values=>{const row=node('tr');values.forEach((v,i)=>{const cell=node(i===0?'th':'td',v);if(i===0)cell.scope='row';row.append(cell);});return row;}));
}
function render() {
  result=analyzeRecovery(state);
  const complete=result.recoverable===state.F.length;
  const verdict=byId('rl-verdict');verdict.dataset.loss=String(!complete);
  verdict.replaceChildren(node('strong',`${result.recoverable} of ${state.F.length} question${state.F.length===1?'':'s'} recoverable`),
    node('p',complete?'Every requested answer follows from the enabled measurements, for every real input.':
      'At least one requested answer changes between inputs with the same enabled measurements.'));
  write('rl-rank',`${result.rank} / ${state.n}`);write('rl-nullity',result.nullity);write('rl-missing',result.repair.additional);
  const tabs=state.F.map((_,i)=>button('F'+subscript(i+1)+(result.questions[i].recoverable?' · recoverable':' · obstructed'),{'data-rl-question':i,'aria-pressed':String(i===state.question)}));
  // Keep focus on the chosen question when a tab is activated.
  const focused=document.activeElement?.dataset?.rlQuestion;
  byId('rl-question-tabs').replaceChildren(...tabs);
  if(focused!==undefined)tabs[Number(focused)]?.focus();
  renderCertificate();renderMotion();
  write('rl-repair-note',complete?'These measurements already answer every question. You can remove a measurement to investigate which answers survive.':
    `Add ${result.repair.additional} independent measurement${result.repair.additional===1?'':'s'}: ${result.repair.addedQuestions.map(i=>'F'+subscript(i+1)).join(', ')}. The new summary keeps an independent subset of the enabled rows and adds these question rows.`);
  write('rl-kernel-note',result.nullity?`${result.nullity} independent invisible direction${result.nullity===1?'':'s'} span ker R. Every enabled measurement vanishes on each direction.`:'The kernel contains only zero. No information about the input is lost.');
  byId('rl-kernel').replaceChildren(...result.kernel.map((w,i)=>formula('w'+subscript(i+1)+' = '+vector(w))));
  write('rl-row-note',`Row reduction uses ${result.active.length} enabled measurement${result.active.length===1?'':'s'}, in their displayed order, relabelled from 1. ${result.rank} pivot${result.rank===1?'':'s'} give the rank.`);
  const headers=['Row',...Array.from({length:state.n},(_,i)=>'x'+subscript(i+1))];
  byId('rl-rref').replaceChildren(table(headers,result.rref.map((r,i)=>[i+1,...r]),'Reduced measurement matrix'));
  byId('rl-transform').replaceChildren(table(['Row',...result.active.map(i=>'y'+subscript(i+1))],result.transform.map((r,i)=>[i+1,...r]),'Exact row-operation matrix E'));
  byId('rl-operations').replaceChildren(...(result.operations.length?result.operations:['No row operations are needed.']).map(v=>node('li',v)));
  root.querySelectorAll('[data-rl-preset]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.rlPreset===activePreset)));
  updateAvailability();
}

root.addEventListener('input',event=>{
  const input=event.target;
  if(input.matches('[data-matrix]')) { readDraft();return; }
  if(input.matches('[data-base]')) {
    state.x[Number(input.dataset.base)]=Number(input.value);
    write('rl-base-value-'+input.dataset.base,input.value);render();
  } else if(input.id==='rl-offset') {
    state.t=Number(input.value);write('rl-offset-value',input.value);render();
  }
});
root.addEventListener('change',event=>{
  const input=event.target;
  if(input.matches('[data-keep]')) { readDraft();return; }
  if(input.id==='rl-dimension') {
    const n=Number(input.value),resize=rows=>rows.map(row=>Array.from({length:n},(_,i)=>row[i]??'0'));
    state=validateExperiment({...state,n,R:resize(state.R),F:resize(state.F),x:Array.from({length:n},(_,i)=>state.x[i]??0)});
    activePreset=null;undo=null;write('rl-repair-status','');status('Input dimension changed. Existing coordinates are kept; added coordinates start at zero.');setControls();
  }
});
root.addEventListener('click',event=>{
  const target=event.target.closest('button');if(!target||target.disabled)return;
  if(target.dataset.rlPreset) {
    state=presetExperiment(target.dataset.rlPreset);activePreset=target.dataset.rlPreset;undo=null;
    write('rl-repair-status','');status('Opened: '+PRESETS[activePreset].title+'.');setControls();
  } else if(target.dataset.rlQuestion!==undefined) {
    state.question=Number(target.dataset.rlQuestion);render();
  } else if(target.dataset.remove) {
    const kind=target.dataset.remove,index=Number(target.dataset.row);
    state[kind].splice(index,1);if(kind==='R')state.enabled.splice(index,1);
    state.question=Math.min(state.question,state.F.length-1);activePreset=null;undo=null;write('rl-repair-status','');setControls();
    byId(kind==='R'?'rl-add-measurement':'rl-add-question').focus();
  } else if(target.id==='rl-add-measurement'||target.id==='rl-add-question') {
    const kind=target.id==='rl-add-measurement'?'R':'F';
    state[kind].push(Array(state.n).fill('0'));if(kind==='R')state.enabled.push(true);
    activePreset=null;undo=null;write('rl-repair-status','');setControls();byId(`rl-${kind}-${state[kind].length-1}-0`).focus();
  } else if(target.id==='rl-repair') {
    const previous=validateExperiment(state),plan=result.repair;
    state=repairExperiment(state);undo=previous;activePreset=null;setControls();
    write('rl-repair-status',`Summary repaired: kept ${plan.retainedRows.length} independent measurement${plan.retainedRows.length===1?'':'s'} and added ${plan.additional}. Every question is now recoverable. Undo restores all original rows and selections.`);
    byId('rl-undo').focus();
  } else if(target.id==='rl-undo'&&undo) {
    state=undo;undo=null;activePreset=null;setControls();write('rl-repair-status','Original summary restored.');byId('rl-repair').focus();
  } else if(target.id==='rl-reset') {
    state=presetExperiment('sum');undo=null;activePreset='sum';write('rl-repair-status','');status('Reset to the sum experiment.');setControls();
  } else if(target.id==='rl-share') {
    void share();
  } else if(target.id==='rl-export') {
    const record={format:'komorebi-recovery-calculation',version:1,
      conventions:'Real-linear maps; rational matrix entries; column inputs; enabled R rows only; exact BigInt fractions.',
      ...analyzeRecovery(state),
      scope:'Exact certificates for these matrices. No manuscript proof audit or Lean execution.'};
    const url=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)+'\n'],{type:'application/json'}));
    const link=node('a');link.href=url;link.download='komorebi-recovery-calculation.json';document.body.append(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);status('Downloaded settings, recovery rules, witnesses, kernel basis, row reduction, repair plan, and exact values.');
  }
});
async function share() {
  const url=new URL(window.location.href);url.hash='recovery='+encodeRecovery(state);
  try {await navigator.clipboard.writeText(url.href);status('Copied the complete experiment link.');}
  catch {
    const input=byId('rl-share-link');input.value=url.href;byId('rl-share-fallback').hidden=false;
    write('rl-status','Copy the experiment link from the field below.');input.focus();input.select();
  }
}
function readLink() {
  if(!window.location.hash.startsWith('#recovery='))return;
  try {
    state=decodeRecovery(window.location.hash.slice(10));undo=null;activePreset=null;write('rl-repair-status','');
    status('Restored all matrices, measurement selections, and inspection settings from the link.');setControls();
  } catch(error) {status(error.message+' The current experiment is kept.');}
}
window.addEventListener('hashchange',readLink);
try {
  setControls();
  root.querySelectorAll('[data-rl-preset],#rl-reset').forEach(b=>{b.disabled=false;});
  readLink();
} catch(error) {
  write('rl-status','The laboratory could not start. Reload the page or use the linked worked calculation.');
  byId('rl-controls').disabled=true;byId('rl-motion-controls').disabled=true;
  for(const id of ['rl-share','rl-export','rl-repair','rl-undo'])byId(id).disabled=true;
}
