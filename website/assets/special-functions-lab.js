import {rational, parse, parameters, validateState, defaultState, coefficients, contributions,
  tailBound, evaluateExact, evaluatePlot, text, decimal, mul, sub, encodeState, decodeState, coefficientCSV} from './special-functions-lab-core.mjs';

const root=document.getElementById('special-functions-lab');
if(root) {
  const el=id=>document.getElementById('sf-'+id), names=['q','r','a','b'];
  let state=defaultState(), current, comparison, bound;
  const say=message=>{el('status').textContent=message;};
  const fmt=n=>Math.abs(n)<0.0001 && n!==0 ? n.toExponential(3) : Number(n.toPrecision(6)).toString();
  function fraction(value) {
    const full=text(value), code=document.createElement('code');code.textContent=full;
    if(full.length<=38)return code;
    const details=document.createElement('details'),summary=document.createElement('summary');
    details.className='sf-fraction';summary.textContent='≈ '+fmt(decimal(value))+' · exact fraction';
    details.append(summary,code);return details;
  }
  function cell(row,value,header=false) {
    const c=document.createElement(header?'th':'td');if(header)c.scope='row';
    if(typeof value==='object')c.append(fraction(value));else c.textContent=String(value);
    row.append(c);return c;
  }
  function row(table,values) {const tr=document.createElement('tr');values.forEach((v,i)=>cell(tr,v,i===0));table.append(tr);return tr;}
  function error(message) {el('error').textContent=message;el('error').hidden=!message;}
  function showState() {
    names.forEach((n,i)=>{el(n).value=state.current[i];el('c'+n).value=state.comparison[i];});
    el('count').value=state.count;el('radius').value=state.radius;el('compare').checked=state.compare;
    if(state.compare)el('comparison').open=true;
    const select=el('term');select.replaceChildren();
    for(let n=0;n<state.count;n++){const option=document.createElement('option');option.value=n;option.textContent=`Index ${n} · degree ${2*n+1}`;select.append(option);}
    select.value=state.term;
  }
  function inputState() {
    const count=Number(el('count').value),compare=el('compare').checked;
    return {v:1,current:names.map(n=>el(n).value),comparison:compare?names.map(n=>el('c'+n).value):state.comparison.slice(),
      compare,count,radius:el('radius').value,term:Math.max(0,Math.min(Number(el('term').value),count-1))};
  }
  function markInvalid() {
    for(const name of [...names,...names.map(n=>'c'+n),'count','radius'])el(name).removeAttribute('aria-invalid');
    for(const prefix of el('compare').checked?['','c']:[''])for(const name of names){try{const q=parse(el(prefix+name).value);if(q.n<=0n||q.n>=q.d)throw new Error();}catch{el(prefix+name).setAttribute('aria-invalid','true');}}
    const n=Number(el('count').value);if(!Number.isInteger(n)||n<1||n>16)el('count').setAttribute('aria-invalid','true');
    try{tailBound(el('radius').value,12);}catch{el('radius').setAttribute('aria-invalid','true');}
  }
  function apply(event) {
    event?.preventDefault();
    try {const next=validateState(inputState());const nextCurrent=coefficients(next.current,next.count),nextComparison=next.compare?coefficients(next.comparison,next.count):null;
      state=next;current=nextCurrent;comparison=nextComparison;error('');markInvalid();showState();render();say('Updated: '+state.count+' coefficients per component, radius '+state.radius+'.');
    } catch(e){markInvalid();error(e.message+' The last valid experiment is still displayed.');}
  }
  function draw() {
    const radius=decimal(parse(state.radius)),width=Math.max(280,Math.min(720,el('plot').clientWidth||720)),height=Math.max(280,width*380/720),pad={l:55,r:25,t:24,b:44};
    const extent=radius||1, series=[{data:current.u,color:'#2f5542',component:'u',dashed:false},{data:current.v,color:'#9a632b',component:'v',dashed:false}];
    if(comparison)series.push({data:comparison.u,color:'#2f5542',component:'u',dashed:true},{data:comparison.v,color:'#9a632b',component:'v',dashed:true});
    const ymax=Math.max(...series.map(s=>Math.abs(evaluatePlot(s.data,radius))),0.1)*1.12;
    const px=x=>pad.l+(x+extent)/(2*extent)*(width-pad.l-pad.r),py=y=>height-pad.b-(y+ymax)/(2*ymax)*(height-pad.t-pad.b);
    let svg=`<svg viewBox="0 0 ${width} ${height}" aria-hidden="true" focusable="false"><rect x="${pad.l}" y="${pad.t}" width="${width-pad.l-pad.r}" height="${height-pad.t-pad.b}" fill="#f9faf4"/>`;
    for(let i=-2;i<=2;i++){const x=extent*i/2,y=ymax*i/2;
      svg+=`<path d="M${px(x)},${pad.t}V${height-pad.b}" stroke="#dce1d4"/><path d="M${pad.l},${py(y)}H${width-pad.r}" stroke="#dce1d4"/>`;
      svg+=`<text x="${px(x)}" y="${height-18}" text-anchor="middle">${fmt(x)}</text><text x="${pad.l-9}" y="${py(y)+4}" text-anchor="end">${fmt(y)}</text>`;
    }
    svg+=`<path d="M${pad.l},${py(0)}H${width-pad.r}M${px(0)},${pad.t}V${height-pad.b}" stroke="#718570" stroke-width="1.3"/><text x="${width-12}" y="${height-18}">x</text>`;
    for(const s of series) {
      const points=Array.from({length:161},(_,i)=>{const x=-radius+2*radius*i/160;return [px(x),py(evaluatePlot(s.data,x))];});
      svg+=`<path d="${points.map((p,i)=>(i?'L':'M')+p.map(v=>v.toFixed(3)).join(',')).join(' ')}" fill="none" stroke="${s.color}" stroke-width="${s.dashed?2:2.6}"${s.dashed?' stroke-dasharray="7 5"':''}/>`;
      for(const factor of [-1,-0.5,0,0.5,1]){const x=px(radius*factor),y=py(evaluatePlot(s.data,radius*factor));
        svg+=s.component==='u'?`<circle cx="${x}" cy="${y}" r="3.4" fill="${s.dashed?'#faf8f1':s.color}" stroke="${s.color}" stroke-width="1.4"/>`:`<rect x="${x-3}" y="${y-3}" width="6" height="6" fill="${s.dashed?'#faf8f1':s.color}" stroke="${s.color}" stroke-width="1.4"/>`;
      }
    }
    el('plot').innerHTML=svg+'</svg>';
    el('comparison-key').hidden=!state.compare;
    el('plot-description').textContent=radius===0?'Radius zero: both polynomials are zero at the only displayed address x = 0. The disk tail bound is zero.':
      `Current pair at x = ${state.radius}: U ≈ ${fmt(evaluatePlot(current.u,radius))}, V ≈ ${fmt(evaluatePlot(current.v,radius))}. Both are odd, so their values at −${state.radius} have opposite signs. Circles mark U and squares mark V.`;
  }
  function inspect() {
    const n=state.term, terms=contributions(state.current,current,n);el('terms').replaceChildren();
    el('term-description').textContent=n===0?'The initial slope supplies u₀ = v₀ = 1. No earlier products are needed.':`Index n = ${n} contributes to degree ${2*n+1}. There are ${n} products with i + j = ${n-1}; each weighted product is divided by ${2*n+1}.`;
    for(const t of terms)row(el('terms'),[t.i,t.j,t.shared,t.u,t.v]);
    if(!terms.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent='Initial condition: unit slope in both equations.';tr.append(td);el('terms').append(tr);}
    el('sum-u').replaceChildren(fraction(current.u[n]));el('sum-v').replaceChildren(fraction(current.v[n]));
  }
  function render() {
    bound=tailBound(state.radius,state.count);draw();inspect();
    el('degree').textContent=String(2*state.count-1);el('bound').replaceChildren(fraction(bound));
    el('bound-decimal').textContent='≈ '+fmt(decimal(bound))+' for each component';
    el('coefficient-rows').replaceChildren();
    for(let n=0;n<state.count;n++){const values=[n,2*n+1,current.u[n],current.v[n]];if(comparison)values.push(comparison.u[n],comparison.v[n]);row(el('coefficient-rows'),values);}
    root.querySelectorAll('.sf-comparison-column').forEach(c=>c.hidden=!state.compare);
    el('samples').replaceChildren();const radius=parse(state.radius);
    for(const t of [rational(-1n),rational(-1n,2n),rational(0n),rational(1n,2n),rational(1n)]){
      const x=mul(radius,t),values=[text(x),evaluateExact(current.u,x),evaluateExact(current.v,x)];
      if(comparison)values.push(evaluateExact(comparison.u,x),evaluateExact(comparison.v,x));row(el('samples'),values);
    }
    el('difference').hidden=!comparison;
    if(comparison){const du=sub(evaluateExact(current.u,radius),evaluateExact(comparison.u,radius)),dv=sub(evaluateExact(current.v,radius),evaluateExact(comparison.v,radius));
      el('difference').textContent=`At x = ${state.radius}, current minus comparison is approximately ${fmt(decimal(du))} for U and ${fmt(decimal(dv))} for V. For the difference of either pair of true functions, the combined truncation bound is ${text(mul(rational(2n),bound))}. This compares local series, not their asymptotic growth.`;
    }
  }
  function load(next,message) {
    state=validateState(next);current=coefficients(state.current,state.count);comparison=state.compare?coefficients(state.comparison,state.count):null;
    showState();markInvalid();error('');render();say(message);
  }
  el('form').addEventListener('submit',apply);el('form').addEventListener('change',apply);
  el('term').addEventListener('change',()=>{state.term=Number(el('term').value);inspect();});
  el('pin').addEventListener('click',()=>{try{const values=parameters(names.map(n=>el(n).value)).map(text);names.forEach((n,i)=>el('c'+n).value=values[i]);el('compare').checked=true;apply();}catch(e){markInvalid();error(e.message);}});
  el('reset').addEventListener('click',()=>{load(defaultState(),'Reset to the worked pair.');el('lesson').textContent='Start at degree three: u₁ = qr/3 and v₁ = ab/3. Then inspect degree five to see both components\' earlier coefficients contribute.';el('share-fallback').hidden=true;});
  root.querySelectorAll('[data-sf-preset]').forEach(button=>button.addEventListener('click',()=>{
    const next=defaultState(),which=button.dataset.sfPreset;
    if(which==='symmetric'){next.current=['1/2','1/2','1/2','1/2'];next.term=3;el('lesson').textContent='Every scale is 1/2. Both series equal √2 sinh(z/√2): check uₙ = vₙ = 1/(2ⁿ(2n + 1)!).';}
    else if(which==='compare'){next.compare=true;next.comparison=next.current.slice();next.current[0]='2/3';next.term=1;el('lesson').textContent='Only q changed, from 1/3 to 2/3. Degree three changes in U; inspect the next degree to see the shared history carry that change into V.';}
    else el('lesson').textContent='The two functions share their initial slope. Their cubic coefficients already distinguish qr from ab; degree five uses the histories of both components.';
    load(next,'Loaded '+button.querySelector('strong').textContent.toLowerCase()+'.');
  }));
  el('share').addEventListener('click',async()=>{
    const url=new URL(location.href);url.hash=encodeState(state);
    el('share-link').value=url.href;
    try{if(!navigator.clipboard?.writeText)throw new Error();await navigator.clipboard.writeText(url.href);el('share-fallback').hidden=true;say('Experiment link copied. It includes both scale sets and inspection settings.');}
    catch{el('share-fallback').hidden=false;el('share-link').focus();el('share-link').select();say('Copy the experiment link from the field below.');}
  });
  el('csv').addEventListener('click',()=>{const blob=new Blob([coefficientCSV(state)],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='coupled-function-coefficients.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);say('Downloaded the exact coefficients, parameters and bound.');});
  window.addEventListener('hashchange',()=>{if(location.hash.startsWith('#sf=')){try{load(decodeState(location.hash),'Loaded the shared experiment.');}catch(e){error('Could not load experiment: '+e.message);}}});
  window.addEventListener('resize',()=>{if(current)draw();});
  try{const linked=location.hash.startsWith('#sf=');load(linked?decodeState(location.hash):defaultState(),linked?'Loaded the shared experiment.':'Ready. Change a scale or choose a question.');}
  catch(e){load(defaultState(),'Loaded the default experiment.');error('Could not load experiment link: '+e.message);}
  el('fields').disabled=false;el('term').disabled=false;
  root.querySelectorAll('[data-sf-preset],#sf-share,#sf-csv,#sf-reset').forEach(button=>button.disabled=false);
}
