(function(){
'use strict';
const $=id=>document.getElementById(id),C=KomorebiCausal,E=KomorebiEngine;
let lab,frames,current=null,result=null,mem=null,spec=null,source=null,target=3,world=[0,1,0,1,1,0,1,0],raf=0;
const chars=['I','L','R','S'];
function random(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function swapShuffle(a,r){for(let i=a.length-1;i;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function pair(z){return '['+(z&1)+', '+((z>>1)&1)+']';}
function answer(z,q){return q===1?String(z):q===3?(z===0?'No':z===1?'Yes':'Class '+z):pair(z);}
function softmax(l){const m=Math.max(...l),p=l.map(x=>Math.exp(x-m)),s=p.reduce((a,b)=>a+b);return p.map(x=>x/s);}
function guard(fn){try{$('error').hidden=true;fn();}catch(e){$('error').textContent=e.message;$('error').hidden=false;console.error(e);}}
function settings(){return {method:$('cMethod').value,strength:+$('cAlpha').value,agent:$('cAgent').value,offsets:[0,1,2].map(i=>+$('cAxis'+i).value),suffix:C.parseProgram($('cSuffix').value,12)};}
function contextFrame(){return frames.lineages[current.lineage];}
function renderFacts(){const cue=[+$('cLeft').value,+$('cRight').value];$('cFacts').innerHTML=world.map((v,i)=>`<button class="bit ${cue.includes(i)?'selected':''}" type="button" aria-label="Fact ${i+1}: ${v}. Toggle" data-cfact="${i}"><span>F${i+1}</span><b>${v}</b></button>`).join('');for(const b of document.querySelectorAll('[data-cfact]'))b.onclick=()=>guard(()=>{world[+b.dataset.cfact]^=1;newEpisode();});}
function makeSpec(){const seed=+$('cSeed').value;if(!Number.isInteger(seed)||seed<0||seed>4294967295)throw Error('Use an unsigned integer case seed.');const r=random(seed),order=swapShuffle([0,1,2,3,4,5,6,7],r),cue=[+$('cLeft').value,+$('cRight').value];if(cue[0]===cue[1])throw Error('Choose two different facts.');const ops=C.parseProgram($('cPrefix').value);return {world:world.slice(),roles:[Math.floor(r()*4),Math.floor(r()*4)],events:order.map(i=>[0,i,i,world[i],1,Math.floor(r()*2),Math.floor(r()*2)]),cue,alias:Math.floor(r()*2),ops,opAliases:ops.map(()=>Math.floor(r()*2)),seed};}
function newEpisode(){spec=makeSpec();const model=new E.Dyad(lab.store,lab.metadata,$('cLineage').value,$('cVariant').value);source=C.initial(model,spec);let value=spec.cue.map(i=>world[i]);for(const op of spec.ops)value=E.truthOp(value,op);current={model,lineage:model.lineage,variant:model.variant,value:E.target(value),captured:false};renderFacts();prepare();$('cSource').textContent=`Same facts and private labels in both branches. Private labels: ${spec.roles.join(' / ')}. ${spec.ops.length} prefix operations. Editing is before the silent delay.`;}
function prepare(){current.experiment=C.prepare(current.model,source,current.value,target);mem=null;renderTargets();compute();}
function renderTargets(){$('cTargets').innerHTML=[0,1,2,3].map(v=>`<button type="button" data-ctarget="${v}" aria-pressed="${v===target}" aria-label="Set donor to ${pair(v)}">${pair(v)}</button>`).join('');for(const b of document.querySelectorAll('[data-ctarget]'))b.onclick=()=>guard(()=>{target=+b.dataset.ctarget;if($('cMethod').value==='none')$('cMethod').value='J';$('cAlpha').value=1;for(let i=0;i<3;i++)$('cAxis'+i).value=0;prepare();});}
function schedule(){if(raf)cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{raf=0;guard(compute);});}
function compute(){if(!current)return;const s=settings();result=C.evaluate(current.model,current.experiment,contextFrame(),s);mem=null;render();document.dispatchEvent(new CustomEvent('komorebi:causal-change'));}
function selectedOutputs(h){const q=+$('cQuery').value,arg=q<2?0:+$('cArg').value;return current.model.outputs(h,q,arg);}
function render(){if(!result)return;const s=settings(),q=+$('cQuery').value,arg=q<2?0:+$('cArg').value,model=current.model;
 const before=selectedOutputs(result.baseline),after=selectedOutputs(result.post),native=selectedOutputs(result.donor),desired=E.target(result.targetPair,q,arg);
 $('cFactual').textContent='['+result.factualPair.join(', ')+']';$('cDesired').textContent='['+result.targetPair.join(', ')+']';$('cArg').disabled=q<2;
 $('cAlphaVal').textContent=s.strength.toFixed(2);document.querySelector('.range-ticks span').textContent=s.offsets.some(v=>v!==0)?'0 · manual offsets still active':'0 · unchanged';const nativeMode=s.method==='native';$('cAlpha').disabled=nativeMode||s.method==='none';
 for(let i=0;i<3;i++){$('cAxisVal'+i).textContent=s.offsets[i].toFixed(2)+' σ';$('cAxis'+i).disabled=s.method!=='J';}
 $('cDimTag').textContent=(s.method==='none'?0:s.method==='native'?64:s.method==='complement'?61:3)+' of 64 directions / agent';
 $('cFormula').textContent=s.method==='none'?'h′ = h':s.method==='native'?'h′ = h_donor (whole state endpoint)':s.method==='complement'?'h′ = h + α (I − UᵀU)(h_donor − h)':'h′ = h + α UᵀU(h_donor − h)'+(s.method==='J'&&s.offsets.some(v=>v!==0)?' + manual J displacement':'');
 const exp=current.experiment,ops=exp.donorOps.map(i=>chars[i]).join(' ');
 $('cDonorInfo').textContent=`Matched native histories: original I I; donor ${ops}. ${exp.targetValue===exp.factualValue?'Different program, same meaning: semantic sham.':'Donor changes temporary content, not the factual input.'}`;
 const changed=after.reduce((n,x,i)=>n+(x.prediction!==before[i].prediction),0),correct=after.filter(x=>x.prediction===desired).length;
 const norm=result.geometry.reduce((s,x)=>s+x.deltaNorm,0),banner=$('cOutcome');banner.classList.toggle('warn',norm>1e-6&&correct<2);
 banner.textContent=norm<1e-6?'No hidden-state change. Choose a different donor value or move the strength slider.':`${changed} of 2 agent outputs changed for this consumer. ${correct} of 2 match the donor counterfactual.`;
 const msg=exp.targetValue===exp.factualValue?' Same-value sham: a semantic answer change is not the intended outcome.':'';
 $('cEditStatus').textContent=result.boundary+msg+(current.captured?' Applied to a captured live state outside the fixed calibration history family.':'');
 for(let a=0;a<2;a++){
   const p0=softmax(before[a].logits),p1=softmax(after[a].logits);
   $('cAgent'+a).innerHTML=`<div class="panelhead"><h3>Agent ${a+1}</h3><span class="tag">Frozen weights</span></div><div class="prediction-pair"><div><small>BEFORE</small><strong>${answer(before[a].prediction,q)}</strong></div><span class="arrow">→</span><div class="after"><small>AFTER EDIT</small><strong>${answer(after[a].prediction,q)}</strong></div></div><div class="prob-legend"><span><b style="background:var(--teal)"></b>Before</span><span><b style="background:var(--purple)"></b>After</span></div>${[0,1,2,3].map(k=>`<div class="prob-row"><span>${q===0||q===2?pair(k):'c'+k}</span><div class="prob-track"><i class="prob-old" style="width:${100*p0[k]}%"></i><i class="prob-new" style="width:${100*p1[k]}%"></i></div><span>${(100*p1[k]).toFixed(1)}%</span></div>`).join('')}<p class="hint">Actual softmax scores, not calibrated confidence.</p><p class="private">Private label: ${before[a].privatePrediction} → <strong class="${after[a].privatePrediction===spec.roles[a]?'ok':'bad'}">${after[a].privatePrediction}</strong> · reference ${spec.roles[a]}<br>Whole-donor network output: ${answer(native[a].prediction,q)}</p>`;
 }
 const names=['Exact pair','Parity','XOR [1, 1]','Verify [1, 0]'];$('cConsumers').innerHTML=names.map((name,k)=>{const y=E.target(result.targetPair,k,k===2?3:k===3?1:0);return `<tr><td>${name}</td><td>${result.baselineOutputs[k].map(x=>answer(x.prediction,k)).join(' / ')}</td><td>${result.outputs[k].map(x=>`<span class="${x.prediction===y?'ok':'bad'}">${answer(x.prediction,k)}</span>`).join(' / ')}</td><td>${answer(y,k)}</td></tr>`;}).join('');
 $('cNorms').textContent=result.geometry.map((g,a)=>`Agent ${a+1}: edit norm ${g.deltaNorm.toFixed(4)}; outside-J norm ${g.outsideJNorm.toFixed(5)}`).join(' · ');
 $('cCoordinates').innerHTML='<div class="coordinate-grid">'+result.geometry.map((g,a)=>`<div><h3>Agent ${a+1} · local coordinates</h3>${g.baseline.map((v,k)=>`<div class="coordinate-row"><span>J${k+1}</span><span>${((v-g.means[k])/g.scales[k]).toFixed(2)} σ → <strong>${((g.edited[k]-g.means[k])/g.scales[k]).toFixed(2)} σ</strong></span></div>`).join('')}</div>`).join('')+'</div>';
 renderMemory();
}
function renderMemory(){if(!mem){$('cMemoryResults').textContent='Not tested for this edit yet. Good output control does not guarantee preserved memory.';return;}
 $('cMemoryResults').innerHTML='<div class="memorycompare">'+['Original','Edited'].map((name,i)=>`<div><h3>${name}</h3>${mem[i].bits.map((bits,a)=>`<div class="memoryrow"><b>${a+1}</b>${bits.map((x,j)=>`<span class="memorybit ${x===spec.world[j]?'':'bad'}" title="Fact ${j+1}; expected ${spec.world[j]}">${x}</span>`).join('')}</div><p class="hint">Agent ${a+1}: ${mem[i].correct[a]}/8 correct</p>`).join('')}</div>`).join('')+'</div><p class="hint mt">Four independent recall branches from each captured state. They do not test a long sequence of successful recalls.</p>';
}
function memoryAudit(){if(!result)return;mem=[result.baseline,result.post].map(h=>C.memory(current.model,h,spec.world));renderMemory();return mem;}
function asArrays(x){if(x instanceof Float32Array)return Array.from(x);if(Array.isArray(x))return x.map(asArrays);if(x&&typeof x==='object')return Object.fromEntries(Object.entries(x).map(([k,v])=>[k,asArrays(v)]));return x;}
function exportTrial(download=true){const obj=asArrays({schema:'komorebi.causal-editor.trial.v1',at:new Date().toISOString(),weights_sha256:lab.metadata.weights_sha256,frames_sha256:JSON.parse($('causalValidationData').textContent).frames_sha256,lineage:current.lineage,variant:current.variant,captured_from_workbench:current.captured,spec,settings:settings(),experiment:current.experiment,source,result,memory:mem,selectedQuery:{q:+$('cQuery').value,arg:+$('cArg').value},boundary:'Artificial candidate intervention unless nativePairWitness is true. No evaluator value replaces model logits.'});if(download){const url=URL.createObjectURL(new Blob([JSON.stringify(obj,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='Komorebi_JSpace_causal_trial.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}return obj;}
async function capture(){await lab.finishProgram();const s=lab.getSession();$('cLineage').value=s.lineage;$('cVariant').value=s.variant;world=s.world.slice();spec={world:world.slice(),roles:s.roles.slice(),events:s.events,ops:s.ops,opAliases:s.opAliases,cue:s.currentCue.slice(),alias:0,source_trace:s.actions,seed:s.seed};const model=new E.Dyad(lab.store,lab.metadata,s.lineage,s.variant);source=C.clone(s.states[1]);current={model,lineage:s.lineage,variant:s.variant,value:E.target(s.value),captured:true};$('cLeft').value=spec.cue[0];$('cRight').value=spec.cue[1];renderFacts();prepare();$('cSource').textContent='Copied the repaired model’s live state. The memory/workbench session itself is unchanged. This phase may be outside frame calibration.';}
function applySettings(s){
 $('cMethod').value=s.method;$('cAgent').value=s.agent;$('cAlpha').value=s.strength;
 for(let i=0;i<3;i++)$('cAxis'+i).value=s.offsets[i];
 const text=s.suffix.map(i=>'ILRS'[i]).join('');
 if(!Array.from($('cSuffix').options).some(o=>o.value===text))$('cSuffix').add(new Option('Custom '+text,text));
 $('cSuffix').value=text;compute();
}
function resetDemo(){
 world=[0,1,0,1,1,0,1,0];target=3;$('cLineage').value='A';$('cVariant').value='calibrated';
 $('cSeed').value=2711;$('cPrefix').value='';$('cLeft').value=0;$('cRight').value=1;
 $('cMethod').value='J';$('cAgent').value='both';$('cAlpha').value=1;$('cSuffix').value='';$('cQuery').value=0;
 for(let i=0;i<3;i++)$('cAxis'+i).value=0;newEpisode();
}
function bind(){
 for(const el of document.querySelectorAll('.causal-fact'))el.innerHTML=Array.from({length:8},(_,i)=>`<option value="${i}">Fact ${i+1}</option>`).join('');$('cLeft').value=0;$('cRight').value=1;
 $('cAxes').innerHTML=[0,1,2].map(k=>`<div class="axis-row"><label for="cAxis${k}">J${k+1} offset <output id="cAxisVal${k}">0.00 σ</output></label><input id="cAxis${k}" type="range" min="-3" max="3" step="0.02" value="0"></div>`).join('');
 for(const id of ['cLineage','cVariant','cSeed','cPrefix'])$(id).onchange=()=>guard(newEpisode);
 for(const id of ['cLeft','cRight'])$(id).onchange=()=>guard(()=>{const other=id==='cLeft'?'cRight':'cLeft';if($(other).value===$(id).value)$(other).value=(+$(id).value+1)%8;newEpisode();});
 $('cNew').onclick=()=>guard(()=>{$('cSeed').value=(+$('cSeed').value+1)>>>0;const r=random(+$('cSeed').value^777);world=world.map(()=>Math.floor(r()*2));newEpisode();});
 $('cApply').onclick=()=>guard(()=>{if($('cMethod').value==='none')$('cMethod').value='J';$('cAlpha').value=1;compute();});
 $('cUndo').onclick=()=>guard(()=>{if($('cMethod').value==='native')$('cMethod').value='J';$('cAlpha').value=0;for(let i=0;i<3;i++)$('cAxis'+i).value=0;compute();});
 $('cAlpha').oninput=schedule;for(let i=0;i<3;i++)$('cAxis'+i).oninput=schedule;
 $('cMethod').onchange=()=>guard(()=>{if($('cMethod').value==='native')$('cAlpha').value=1;for(let i=0;i<3;i++)$('cAxis'+i).value=0;compute();});
 for(const id of ['cAgent','cSuffix'])$(id).onchange=()=>guard(compute);
 for(const id of ['cQuery','cArg'])$(id).onchange=()=>guard(render);
 $('cMemory').onclick=()=>guard(memoryAudit);$('cExport').onclick=()=>guard(exportTrial);$('cCapture').onclick=()=>capture().catch(e=>guard(()=>{throw e;}));
 const v=JSON.parse($('causalValidationData').textContent);$('cMeasured').textContent=`This editor’s numerical port matched ${v.port.decisions.toLocaleString()} tested decisions over ${v.port.paths} intervention paths. The fixed-frame assay used 256 histories per lineage; both lineages reached 100% immediate exact donor answers with bilateral J edits. Factual-memory preservation was imperfect. These are sampled development checks, not a general guarantee.`;
 const oldDock=['dockControls','dockRun','dockResults'].map(id=>$(id).onclick);
 const active=()=>!$('causal').hidden;
 $('dockControls').onclick=()=>active()?$('causal').scrollIntoView({behavior:'smooth'}):oldDock[0]();
 $('dockRun').onclick=()=>active()?$('cApply').click():oldDock[1]();
 $('dockResults').onclick=()=>active()?document.querySelector('.causal-results').scrollIntoView({behavior:'smooth'}):oldDock[2]();
 for(const t of document.querySelectorAll('[data-tab]'))t.addEventListener('click',()=>{$('dockRun').textContent=active()?'Apply J edit':'Run program';});
 $('dockRun').textContent='Apply J edit';
 newEpisode();window.JCausalLab={getCurrent:()=>current,getResult:()=>result,getMemory:()=>mem,getSource:()=>source,getSpec:()=>spec,getTarget:()=>target,applySettings,resetDemo,settings,compute,prepare,newEpisode,memoryAudit,exportTrial,capture,frames,C};
}
function start(){if(!window.KomorebiLab){setTimeout(start,20);return;}guard(()=>{lab=window.KomorebiLab;frames=JSON.parse($('causalFrames').textContent);bind();});}
setTimeout(start,40);
})();
