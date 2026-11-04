import {analyzeRecovery,validateExperiment,repairExperiment,encodeRecovery,decodeRecovery,PRESETS,presetExperiment} from './recovery-lab-core.mjs';
import {LESSONS,lessonExperiment,linearExpression,workedExplanation,motionSamples,asNumber} from './recovery-lab-guidance.mjs';

const byId=id=>document.getElementById(id);
const write=(id,value)=>{if(byId(id).textContent!==String(value))byId(id).textContent=value;};
const root=byId('recovery-lab');
const subscript=value=>String(value).replace(/\d/g,v=>'₀₁₂₃₄₅₆₇₈₉'[Number(v)]);
const vector=values=>values.length?'('+values.join(', ')+')':'() — no enabled measurements';
let state=presetExperiment('sum'), result, undo=null, invalid=false, activePreset='sum';
let lessonIndex=0, lessonLoaded=true;
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
const expression=linearExpression;
function renderLesson() {
  const lesson=LESSONS[lessonIndex];
  byId('rl-lesson-content').hidden=false;
  write('rl-lesson-title',lesson.title);write('rl-lesson-idea',lesson.idea);
  write('rl-lesson-example','Starting example: '+lesson.example);write('rl-lesson-task',lesson.task);
  write('rl-prediction-prompt',lesson.prompt);write('rl-prediction-feedback','');
  byId('rl-prediction-choices').replaceChildren(...lesson.choices.map((choice,i)=>button(choice,{'data-rl-prediction':i,'aria-pressed':'false'})));
  byId('rl-lesson-next').disabled=lessonIndex===LESSONS.length-1;
  root.querySelectorAll('[data-rl-lesson]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.rlLesson)===lessonIndex)));
  updateLessonNote();
}
function updateLessonNote() {
  write('rl-lesson-state',lessonLoaded?'The workspace is using this step’s starting experiment.':'You changed the experiment. The explanation and prediction above use the starting example. Reload this step to compare them.');
}
function freeExploration() {lessonLoaded=false;updateLessonNote();}
function loadLesson(index,moveFocus=false) {
  lessonIndex=index;state=lessonExperiment(index);lessonLoaded=true;
  activePreset=LESSONS[index].preset;undo=null;write('rl-repair-status','');
  renderLesson();setControls();status('Loaded guided step: '+LESSONS[index].title+'.');
  if(moveFocus)byId('rl-lesson-title').focus();
}
function scrollRegions() {
  root.querySelectorAll('.table-scroll').forEach(host=>{
    host.setAttribute('role','region');host.setAttribute('aria-label',host.querySelector('caption')?.textContent||'Calculation table');
    if(host.scrollWidth>host.clientWidth+1)host.tabIndex=0;else host.removeAttribute('tabindex');
  });
}
function resultStatus() {
  status(`${result.recoverable} of ${state.F.length} questions recoverable. Question ${state.question+1} ${result.questions[state.question].recoverable?'is recoverable':'has an obstruction'}. ${result.repair.additional} extra measurements needed.`);
}
function motionStatus() {
  status(`At t = ${state.t}, enabled measurements stay (${result.motion.movedSummary.join(', ')}). Question ${state.question+1} is ${result.motion.movedAnswers[state.question]}.`);
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
      const target=node('label',undefined,'rl-keep-target');target.append(check);cell.append(target);row.append(cell);
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
    label.htmlFor='rl-base-'+i;const output=node('output',value);output.id='rl-base-value-'+i;output.setAttribute('for',label.htmlFor);output.setAttribute('aria-live','off');
    const input=node('input');input.type='range';input.id=label.htmlFor;input.min=-4;input.max=4;input.step=1;input.value=value;input.dataset.base=i;
    input.setAttribute('aria-describedby','rl-motion-help');label.append(output);host.append(label,input);return host;
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
  byId('rl-step-back').disabled=invalid||result.nullity===0||state.t<=-4;
  byId('rl-step-forward').disabled=invalid||result.nullity===0||state.t>=4;
  root.querySelectorAll('[data-rl-prediction]').forEach(b=>{b.disabled=false;});
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
    state=validateExperiment(candidate);invalid=false;activePreset=null;undo=null;freeExploration();
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
  const worked=workedExplanation(result);
  write('rl-worked-title',worked.title);write('rl-worked-calculation',worked.calculation);write('rl-worked-text',worked.text);
}
function renderEquations() {
  const names=state.x.map((_,i)=>'x'+subscript(i+1));
  write('rl-equation-input','At the base input x = '+vector(result.motion.x)+':');
  const enabledValues=new Map(result.active.map((index,j)=>[index,result.motion.summary[j]]));
  const rows=[...state.R.map((r,i)=>['y'+subscript(i+1)+(state.enabled[i]?'':' (off)'),expression(r,names),state.enabled[i]?enabledValues.get(i):'Not used']),
    ...state.F.map((r,i)=>['F'+subscript(i+1),expression(r,names),result.motion.answers[i]])];
  const host=node('div',undefined,'table-scroll');host.append(table(['Row','Weighted sum','Value at x'],rows,'Your rows in words and numbers'));
  byId('rl-equations').replaceChildren(host);
}
function plot(width,height) {
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox',`0 0 ${width} ${height}`);svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
  const shape=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.append(e);return e;};
  return {svg,shape};
}
function renderResponse() {
  const samples=motionSamples(state),selected=result.questions[state.question],base=result.motion.answers[state.question];
  const {svg,shape}=plot(480,300),numbers=samples.map(s=>asNumber(s.answer));
  const bound=Math.max(1,...numbers.map(Math.abs)),px=t=>62+(t+4)*48,py=v=>132-v/bound*94;
  [-bound,0,bound].forEach(v=>{
    shape('line',{x1:62,x2:446,y1:py(v),y2:py(v),class:'rl-plot-axis'});
    shape('text',{x:55,y:py(v)+4,'text-anchor':'end'},Number(v.toPrecision(3)));
  });
  [-4,-2,0,2,4].forEach(t=>shape('text',{x:px(t),y:250,'text-anchor':'middle'},t));
  shape('text',{x:254,y:281,'text-anchor':'middle'},'Position along w · t');
  shape('text',{x:62,y:19},'Answer F'+subscript(state.question+1));
  shape('line',{x1:px(state.t),x2:px(state.t),y1:30,y2:230,class:'rl-current-guide'});
  shape('polyline',{points:samples.map((s,i)=>`${px(s.t)},${py(numbers[i])}`).join(' '),class:'rl-response-trace'});
  shape('line',{x1:62,x2:446,y1:py(asNumber(base)),y2:py(asNumber(base)),class:'rl-response-base'});
  samples.forEach((s,i)=>shape('circle',{cx:px(s.t),cy:py(numbers[i]),r:s.t===state.t?7:4,class:'rl-response-dot'}));
  shape('rect',{x:px(0)-5,y:py(asNumber(base))-5,width:10,height:10,class:'rl-base-square'});
  byId('rl-response-chart').replaceChildren(svg);
  write('rl-response-description',`The horizontal axis is t, from −4 to 4; the vertical axis is the selected answer. Every plotted input has the same enabled summary ${vector(result.motion.summary)}. `+
    (result.nullity===0?'There is no invisible direction, so all plotted inputs coincide.':selected.recoverable?
      `This answer stays at ${base} along the displayed direction. The recovery certificate also checks all other invisible directions.`:
      `The answer changes from ${samples[0].answer} to ${samples[8].answer}, by ${selected.change} per step in t. At the current t = ${state.t}, it is ${result.motion.movedAnswers[state.question]}.`));
  byId('rl-samples').replaceChildren(table(['t','Enabled summary','Selected answer'],samples.map(s=>[s.t,vector(s.summary),s.answer]),'Exact answer-graph samples, t from −4 to 4'));
}
function renderFiber() {
  byId('rl-fiber-figure').hidden=state.n!==2;
  if(state.n!==2)return;
  const {svg,shape}=plot(480,300),x=result.motion.x.map(asNumber),moved=result.motion.moved.map(asNumber),w=result.motion.direction.map(asNumber);
  // Keep the axes fixed as t moves through its full range.
  const extremes=x.flatMap((v,i)=>[v-4*w[i],v+4*w[i]]);
  const bound=Math.max(2,...extremes.map(Math.abs))*1.25;
  const px=v=>245+v/bound*112,py=v=>147-v/bound*112;
  if(result.nullity===2)shape('rect',{x:px(-bound),y:py(bound),width:224,height:224,class:'rl-fiber-plane'});
  [-bound,0,bound].forEach(v=>{
    shape('line',{x1:px(-bound),x2:px(bound),y1:py(v),y2:py(v),class:'rl-plot-axis'});
    shape('line',{x1:px(v),x2:px(v),y1:py(-bound),y2:py(bound),class:'rl-plot-axis'});
    shape('text',{x:px(v),y:280,'text-anchor':'middle'},Number(v.toPrecision(3)));
    shape('text',{x:124,y:py(v)+4,'text-anchor':'end'},Number(v.toPrecision(3)));
  });
  if(result.nullity===1) {
    let low=-Infinity,high=Infinity;
    w.forEach((v,i)=>{if(v!==0){const ends=[(-bound-x[i])/v,(bound-x[i])/v].sort((a,b)=>a-b);low=Math.max(low,ends[0]);high=Math.min(high,ends[1]);}});
    shape('line',{x1:px(x[0]+low*w[0]),y1:py(x[1]+low*w[1]),x2:px(x[0]+high*w[0]),y2:py(x[1]+high*w[1]),class:'rl-fiber-line'});
  }
  shape('circle',{cx:px(x[0]),cy:py(x[1]),r:6,class:'rl-plot-base'});
  shape('rect',{x:px(moved[0])-8,y:py(moved[1])-8,width:16,height:16,class:'rl-base-square'});
  shape('text',{x:372,y:151},'x₁');shape('text',{x:239,y:23},'x₂');
  byId('rl-fiber-chart').replaceChildren(svg);
  write('rl-fiber-description',`The axes are input coordinates x₁ and x₂. `+
    (result.nullity===2?'The whole plane shares this summary: no nonzero measurement is enabled. The shaded region is the visible portion of that plane.':result.nullity===1?
      'The line is the full fiber through x: every point on it has this same summary. Only the part inside the plotting window is shown.':
      'The fiber is a single point: these measurements determine both coordinates.')+
    ` Filled circle: x = ${vector(result.motion.x)}. Outlined square: x + tw = ${vector(result.motion.moved)}. Their enabled summaries are both ${vector(result.motion.summary)}.`);
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
  byId('rl-offset').setAttribute('aria-valuetext',`t = ${state.t}; selected answer ${m.movedAnswers[state.question]}; enabled measurements unchanged`);
  renderResponse();renderFiber();
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
  renderCertificate();renderMotion();renderEquations();
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
  requestAnimationFrame(scrollRegions);
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
  if(input.matches('[data-keep]')) { readDraft();if(!invalid)resultStatus();return; }
  if(input.matches('[data-matrix]')) {if(!invalid)resultStatus();return;}
  if(input.matches('[data-base]')||input.id==='rl-offset') {motionStatus();return;}
  if(input.id==='rl-dimension') {
    const n=Number(input.value),resize=rows=>rows.map(row=>Array.from({length:n},(_,i)=>row[i]??'0'));
    state=validateExperiment({...state,n,R:resize(state.R),F:resize(state.F),x:Array.from({length:n},(_,i)=>state.x[i]??0)});
    activePreset=null;undo=null;freeExploration();write('rl-repair-status','');status('Input dimension changed. Existing coordinates are kept; added coordinates start at zero.');setControls();
  }
});
root.addEventListener('click',event=>{
  const target=event.target.closest('button');if(!target||target.disabled)return;
  if(target.dataset.rlLesson!==undefined) {
    loadLesson(Number(target.dataset.rlLesson));
  } else if(target.id==='rl-lesson-reload'||target.id==='rl-lesson-next') {
    loadLesson(lessonIndex+(target.id==='rl-lesson-next'?1:0),true);
  } else if(target.dataset.rlPrediction!==undefined) {
    const answer=Number(target.dataset.rlPrediction),lesson=LESSONS[lessonIndex];
    root.querySelectorAll('[data-rl-prediction]').forEach(b=>b.setAttribute('aria-pressed',String(b===target)));
    write('rl-prediction-feedback',(answer===lesson.correct?'Yes. ':'Try that reasoning again. ')+lesson.explanation);
  } else if(target.id==='rl-step-back'||target.id==='rl-step-forward') {
    state.t+=target.id==='rl-step-back'?-1:1;byId('rl-offset').value=state.t;write('rl-offset-value',state.t);render();motionStatus();
    if(target.disabled)byId('rl-offset').focus();
  } else if(target.dataset.rlPreset) {
    state=presetExperiment(target.dataset.rlPreset);activePreset=target.dataset.rlPreset;undo=null;
    freeExploration();
    write('rl-repair-status','');status('Opened: '+PRESETS[activePreset].title+'.');setControls();
  } else if(target.dataset.rlQuestion!==undefined) {
    state.question=Number(target.dataset.rlQuestion);render();resultStatus();
  } else if(target.dataset.remove) {
    const kind=target.dataset.remove,index=Number(target.dataset.row);
    state[kind].splice(index,1);if(kind==='R')state.enabled.splice(index,1);
    state.question=Math.min(state.question,state.F.length-1);activePreset=null;undo=null;freeExploration();write('rl-repair-status','');setControls();resultStatus();
    byId(kind==='R'?'rl-add-measurement':'rl-add-question').focus();
  } else if(target.id==='rl-add-measurement'||target.id==='rl-add-question') {
    const kind=target.id==='rl-add-measurement'?'R':'F';
    state[kind].push(Array(state.n).fill('0'));if(kind==='R')state.enabled.push(true);
    activePreset=null;undo=null;freeExploration();write('rl-repair-status','');setControls();byId(`rl-${kind}-${state[kind].length-1}-0`).focus();resultStatus();
  } else if(target.id==='rl-repair') {
    const previous=validateExperiment(state),plan=result.repair;
    state=repairExperiment(state);undo=previous;activePreset=null;freeExploration();setControls();
    write('rl-repair-status',`Summary repaired: kept ${plan.retainedRows.length} independent measurement${plan.retainedRows.length===1?'':'s'} and added ${plan.additional}. Every question is now recoverable. Undo restores all original rows and selections.`);
    byId('rl-undo').focus();
  } else if(target.id==='rl-undo'&&undo) {
    state=undo;undo=null;activePreset=null;freeExploration();setControls();write('rl-repair-status','Original summary restored.');byId('rl-repair').focus();
  } else if(target.id==='rl-reset') {
    state=presetExperiment('sum');undo=null;activePreset='sum';lessonIndex=0;lessonLoaded=true;renderLesson();write('rl-repair-status','');status('Reset to the sum experiment.');setControls();
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
    state=decodeRecovery(window.location.hash.slice(10));undo=null;activePreset=null;freeExploration();write('rl-repair-status','');
    status('Restored all matrices, measurement selections, and inspection settings from the link.');setControls();
  } catch(error) {status(error.message+' The current experiment is kept.');}
}
window.addEventListener('hashchange',readLink);
try {
  renderLesson();
  setControls();
  root.querySelectorAll('[data-rl-preset],[data-rl-lesson],#rl-reset').forEach(b=>{b.disabled=false;});
  new ResizeObserver(scrollRegions).observe(root);
  root.addEventListener('toggle',scrollRegions,true);
  readLink();
} catch(error) {
  write('rl-status','The laboratory could not start. Reload the page or use the linked worked calculation.');
  byId('rl-controls').disabled=true;byId('rl-motion-controls').disabled=true;
  for(const id of ['rl-share','rl-export','rl-repair','rl-undo'])byId(id).disabled=true;
}
