(function(){
'use strict';
const $=id=>document.getElementById(id),R=KomorebiRefinement,C=KomorebiCausal,E=KomorebiEngine;
let lab,root,live=null,liveContext=null,rows=[],controls=[],scanInfo=null,token=0,key='',liveAudit=null,busy=false;
const names={none:'No edit',J:'Report-J candidate',interaction:'Activation candidate',PCA:'Same-rank PCA',random:'Random directions',complement:'J complement',native:'Whole donor'};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pair=z=>'['+(z&1)+', '+((z>>1)&1)+']';
const answer=(z,q)=>q===1?String(z):q===3?(z===0?'No':z===1?'Yes':'Class '+z):pair(z);
const pct=p=>(100*p).toFixed(1)+'%';
function notice(s,error=false){$('rNotice').textContent=s;$('rNotice').classList.toggle('bad',error);}
function guard(fn){try{return fn();}catch(e){notice(e.message,true);return null;}}
function current(){const c=lab.getCurrent();return {c,spec:lab.getSpec(),settings:lab.settings(),frame:lab.frames.lineages[c.lineage]};}
function fingerprint(){const {c,spec,settings}=current();return JSON.stringify([c.lineage,c.variant,spec.world,spec.roles,c.experiment,settings.method,settings.agent,settings.suffix]);}
function unchanged(k,t){return key===k&&token===t;}
function controlsBusy(v){busy=v;$('rSweep').disabled=v;$('rCompare').disabled=v;}
function invalidate(){
 const k=fingerprint();if(k===key)return;key=k;token++;controlsBusy(false);rows=[];controls=[];scanInfo=null;
 $('rProgress').textContent='Source context changed. Run a new scan.';$('rDoseChart').replaceChildren();$('rDoseRows').replaceChildren();$('rSweepSummary').textContent='';$('rApplySmallest').disabled=true;
 $('rControlRows').replaceChildren();$('rControlsStatus').textContent='Controls have not been run for this context.';
 if(live)notice('Preview changed. Your committed trajectory is still intact below. Commit again only to start a new trajectory.');
}
function chart(){
 if(!rows.length)return;
 const w=560,h=185,x=a=>40+480*a,y=p=>145-112*p;
 const path=a=>rows.map((r,i)=>(i?'L':'M')+x(r.settings.strength).toFixed(1)+','+y(r.targetScores[a]).toFixed(1)).join(' ');
 const guides=[0,0.5,1].map(p=>`<line x1="40" x2="520" y1="${y(p)}" y2="${y(p)}" class="r-gridline"/><text x="32" y="${y(p)+4}" text-anchor="end">${100*p}%</text>`).join('');
 $('rDoseChart').innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="Measured donor-class softmax versus edit strength, Agent 1 and Agent 2. Data are also in the measured-point table.">${guides}<path d="${path(0)}" class="r-line1"/><path d="${path(1)}" class="r-line2"/>${rows.map(r=>[0,1].map(a=>`<circle cx="${x(r.settings.strength)}" cy="${y(r.targetScores[a])}" r="2.8" class="r-dot${a+1}"><title>α ${r.settings.strength.toFixed(2)}, Agent ${a+1}: ${pct(r.targetScores[a])}</title></circle>`).join('')).join('')}<text x="40" y="165">0</text><text x="280" y="165" text-anchor="middle">Edit strength α</text><text x="520" y="165" text-anchor="end">1</text></svg><div class="r-chart-key"><span class="r-key1">Agent 1</span><span class="r-key2">Agent 2</span><span>Softmax scores, not calibrated confidence</span></div>`;
}
function renderRows(){
 $('rDoseRows').innerHTML=rows.map(r=>`<tr><td>${r.settings.strength.toFixed(2)}</td><td>${r.predictions.map((z,a)=>`<span class="${r.targetMatched[a]?'ok':'bad'}">${pair(z)}</span>`).join(' / ')}</td><td>${r.memoryAfter.correct.join('/8 · ')}/8</td><td>${r.privateCorrect.filter(Boolean).length}/2 correct</td></tr>`).join('');
 const s=R.summary(rows);scanInfo=s;
 const steering=s.firstSteering===null?'No tested strength makes both outputs match the distinct donor.':'First tested strength steering both outputs: '+s.firstSteering.toFixed(2)+'.';
 const preserving=s.firstPreserving===null?'No tested point also passes the full factual/private audit.':'First tested strength also passing the factual/private audit: '+s.firstPreserving.toFixed(2)+'.';
 $('rSweepSummary').textContent=steering+' '+preserving;
 $('rApplySmallest').disabled=s.firstPreserving===null;
 chart();
}
async function sweep(){
 const x=current(),k=key,t=++token;rows=[];scanInfo=null;controlsBusy(true);$('rApplySmallest').disabled=true;
 try{
  const alphas=R.sweepAlphas(x.settings.method);
  for(let i=0;i<alphas.length;i++){
   if(!unchanged(k,t))return;
   rows.push(R.point(x.c.model,x.c.experiment,x.frame,{...x.settings,strength:alphas[i],offsets:[0,0,0]},x.spec.world,x.spec.roles));
   $('rProgress').textContent=`Measured ${i+1}/${alphas.length} strengths. ${x.settings.method==='native'?'Native mode tests endpoints only.':''}`;
   await new Promise(resolve=>setTimeout(resolve,0));
  }
  if(!unchanged(k,t))return;renderRows();notice('Sweep complete. No model weights or live trajectory were changed.');
 }catch(e){notice(e.message,true);}finally{if(unchanged(k,t))controlsBusy(false);}
}
async function compare(){
 const x=current(),k=key,t=++token;controls=[];controlsBusy(true);
 try{
  for(const method of R.METHODS){
   if(!unchanged(k,t))return;
   controls.push(R.point(x.c.model,x.c.experiment,x.frame,{...x.settings,method,strength:method==='none'?0:1,offsets:[0,0,0]},x.spec.world,x.spec.roles));
   $('rControlsStatus').textContent='Measured '+controls.length+'/'+R.METHODS.length+' interventions.';
   await new Promise(resolve=>setTimeout(resolve,0));
  }
  if(!unchanged(k,t))return;
  $('rControlRows').innerHTML=controls.map(r=>`<tr><td>${names[r.settings.method]}</td><td>${r.predictions.map((z,a)=>`<span class="${r.targetMatched[a]?'ok':''}">${pair(z)}</span>`).join(' / ')}</td><td>${r.memoryAfter.correct.join('/8 · ')}/8</td><td class="${r.memoryChange.noNewErrors?'ok':'bad'}">${r.memoryChange.lost.join(' / ')}</td></tr>`).join('');
  $('rControlsStatus').textContent='Seven matched interventions, computed now. Original correct counts: '+controls[0].memoryBefore.correct.join('/8 · ')+'/8. Green pair values match the donor reference, including same-value cases.';
  notice('Control comparison complete. These are measurements of the selected case, not population accuracy.');
 }catch(e){notice(e.message,true);}finally{if(unchanged(k,t))controlsBusy(false);}
}
function renderLive(){
 const enabled=!!live;for(const el of document.querySelectorAll('.r-step, #rSilent, #rLiveUndo, #rRunProgram, #rReload, #rLiveAudit, #rExport'))el.disabled=!enabled;
 if(!live)return;
 $('rLiveUndo').disabled=live.actions.length===0;
 const q=+$('rQuery').value,arg=q<2?0:+$('rArg').value;$('rArg').disabled=q<2;
 const o=R.liveRead(live,q,arg);
 $('rLiveStatus').textContent=`Lineage ${live.model.lineage} · ${live.model.variant} recall · ${live.actions.length} committed action${live.actions.length===1?'':'s'} · initial edit ${live.settings.method}, α ${live.settings.strength.toFixed(2)}. Preview changes do not alter this branch.`;
 $('rLiveReadout').innerHTML=['Original branch','Edited branch'].map((n,b)=>`<div><span class="minilabel">${n}</span><strong>${o.outputs[b].map(v=>answer(v.prediction,q)).join(' / ')}</strong><small>Agent 1 / Agent 2 · ${b===1?'intended donor':'original'} reference ${answer(o.references[b],q)}</small><span class="hint">Private labels ${o.outputs[b].map(v=>v.privatePrediction).join(' / ')} · expected ${live.roles.join(' / ')}</span></div>`).join('');
 $('rHistory').innerHTML=live.history.map(r=>`<tr><td>${r.step}. ${esc(r.label)}</td>${[0,1].map(b=>`<td>${r.outputs[b][0].map(v=>pair(v.prediction)).join(' / ')}</td>`).join('')}<td>${[0,1].map(b=>r.outputs[b][0].filter((v,a)=>v.privatePrediction===live.roles[a]).length+'/2').join(' · ')}</td></tr>`).join('');
 if(!liveAudit)$('rLiveMemory').textContent='This trajectory has not been memory-audited at its current step.';
 else $('rLiveMemory').textContent='All-fact recall: original '+liveAudit.before.correct.join('/8 · ')+'/8; edited '+liveAudit.after.correct.join('/8 · ')+'/8. Newly missed facts: '+liveAudit.change.lost.join(' / ')+'. Independent branches; the live trajectory is unchanged.';
}
function commit(){
 const x=current();live=R.begin(x.c.model,x.c.experiment,x.frame,x.settings,x.spec.world,x.spec.roles);liveContext={spec:R.plain(x.spec),captured:x.c.captured,previewFingerprint:key};liveAudit=null;renderLive();notice('Current edit committed. Future live actions will use that state without applying the edit again.');return live;
}
function advance(a){if(!live)throw Error('Commit an edit first');R.step(live,a);liveAudit=null;renderLive();}
function download(obj,name){const u=URL.createObjectURL(new Blob([JSON.stringify(obj,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),2000);}
function exportLive(save=true){if(!live)throw Error('No trajectory to export');const v=JSON.parse($('causalValidationData').textContent);
 const obj=R.exportSession(live,root.metadata,v.frames_sha256,{initialContext:liveContext,currentAudit:liveAudit});
 if(save)download(obj,'Komorebi_JSpace_Causal_Session_v1_2.json');return obj;}
function importLive(obj){
 const v=JSON.parse($('causalValidationData').textContent),restored=R.replay(obj,root.store,root.metadata,lab.frames,v.frames_sha256);
 live=restored;liveContext={imported:true,provenance:'Recorded activation snapshot; not authenticated native history'};liveAudit=null;renderLive();
 notice('Session replayed from its recorded states and actions. Saved predictions were ignored and recomputed. Native origin is not authenticated.');return live;
}
function setup(){
 lab=window.JCausalLab;root=window.KomorebiLab;
 $('rSweep').onclick=sweep;$('rCompare').onclick=compare;
 $('rApplySmallest').onclick=()=>guard(()=>{if(!scanInfo||scanInfo.firstPreserving===null)throw Error('No qualifying scan point');const r=rows.find(x=>x.settings.strength===scanInfo.firstPreserving);lab.applySettings(r.settings);notice('Applied a case-selected scan point. This is not an independent success test.');});
 $('rCommit').onclick=()=>guard(commit);
 $('rDemo').onclick=()=>guard(()=>{lab.resetDemo();$('rProgram').value='LSR';$('rCueLeft').value=0;$('rCueRight').value=1;$('rWire').value='intact';$('rQuery').value=0;$('rArg').value=0;lab.memoryAudit();commit();notice('Guided case applied: inspect the actual before/after answers, then use Swap below to continue the edited state.');});
 $('rJump').onclick=()=>$('rLivePanel').scrollIntoView({behavior:'smooth'});
 for(const b of document.querySelectorAll('.r-step'))b.onclick=()=>guard(()=>advance({type:'work',ops:[+b.dataset.op]}));
 $('rSilent').onclick=()=>guard(()=>advance({type:'silent',count:1}));
 $('rRunProgram').onclick=()=>guard(()=>advance({type:'work',ops:C.parseProgram($('rProgram').value,12)}));
 $('rLiveUndo').onclick=()=>guard(()=>{if(live){R.undo(live);liveAudit=null;renderLive();}});
 for(const id of ['rCueLeft','rCueRight'])$(id).innerHTML=Array.from({length:8},(_,i)=>`<option value="${i}">Fact ${i+1}</option>`).join('');$('rCueRight').value=1;
 $('rReload').onclick=()=>guard(()=>advance({type:'retrieve',cue:[+$('rCueLeft').value,+$('rCueRight').value],mode:$('rWire').value}));
 $('rQuery').onchange=()=>guard(renderLive);$('rArg').onchange=()=>guard(renderLive);
 $('rLiveAudit').onclick=()=>guard(()=>{liveAudit=R.auditSession(live);renderLive();return liveAudit;});
 $('rExport').onclick=()=>guard(()=>exportLive());$('rImport').onclick=()=>$('rImportFile').click();
 $('rImportFile').onchange=async()=>{const f=$('rImportFile').files[0];if(!f)return;try{if(f.size>4000000)throw Error('Session files are limited to 4 MB');importLive(JSON.parse(await f.text()));}catch(e){notice(e.message,true);}finally{$('rImportFile').value='';}};
 document.addEventListener('komorebi:causal-change',()=>guard(invalidate));key=fingerprint();renderLive();
 window.JRefinedLab={sweep,compare,commit,advance,importLive,exportLive,renderLive,getLive:()=>live,getRows:()=>rows,getControls:()=>controls,getSummary:()=>scanInfo,getAudit:()=>liveAudit,isBusy:()=>busy};
}
function start(){if(!window.JCausalLab){setTimeout(start,30);return;}guard(setup);}start();
})();
