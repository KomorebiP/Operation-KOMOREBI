/* Komorebi browser inference. Frozen float32 checkpoint weights, no dependencies.
 * Ported from selective.py, gated_selective.py, working.py, access_repair.py.
 * GRU gate order: reset, update, new. Numerical validation accompanies this file.
 * Truth is used by the separate evaluator only; it never enters neural readouts.
 */
(function(global){
'use strict';
const f=Math.fround, sig=x=>1/(1+Math.exp(-x)), H=64;
function cat(...a){let n=a.reduce((s,x)=>s+x.length,0),r=new Float32Array(n),o=0;for(const x of a){r.set(x,o);o+=x.length;}return r;}
function map(a,fn){const r=new Float32Array(a.length);for(let i=0;i<a.length;i++)r[i]=fn(a[i],i);return r;}
function add(a,b){return map(a,(x,i)=>x+b[i]);}
function mul(a,b){return map(a,(x,i)=>x*b[i]);}
function argmax(a){let j=0;for(let i=1;i<a.length;i++)if(a[i]>a[j])j=i;return j;}
function linear(x,w,b){const r=new Float32Array(w.shape[0]),v=w.data,n=w.shape[1];for(let i=0;i<r.length;i++){let s=0,o=i*n;for(let j=0;j<n;j++)s+=v[o+j]*x[j];r[i]=f(f(s)+(b?b.data[i]:0));}return r;}
function gru(x,h,wi,wh,bi,bh){const a=linear(x,wi,bi),b=linear(h,wh,bh),out=new Float32Array(H);for(let i=0;i<H;i++){const r=f(sig(f(a[i]+b[i]))),z=f(sig(f(a[H+i]+b[H+i]))),n=f(Math.tanh(f(a[2*H+i]+f(r*b[2*H+i]))));out[i]=f(n+f(z*f(h[i]-n)));}return out;}
class Network{
 constructor(store,prefix,basePrefix=null){this.store=store;this.p=prefix;this.cache=new Map();this.basePrefix=basePrefix;}
 t(k){const t=this.store[this.p+k];if(!t)throw Error('Missing tensor '+this.p+k);return t;}
 emb(k,index){let t=this.t(k+'.weight'),n=t.shape[1];if(!Number.isInteger(index)||index<0||index>=t.shape[0])throw Error('Invalid embedding '+k+': '+index);return t.data.subarray(index*n,(index+1)*n);}
 lin(k,x){return linear(x,this.t(k+'.weight'),this.t(k+'.bias'));}
 cell(k,x,h){return gru(x,h,this.t(k+'.weight_ih'),this.t(k+'.weight_hh'),this.t(k+'.bias_ih'),this.t(k+'.bias_hh'));}
 input(x){return map(this.lin('input',x),Math.tanh);}
 blank(){if(!this.cache.has('blank'))this.cache.set('blank',this.input(cat(this.emb('command',10),new Float32Array(36))));return this.cache.get('blank');}
 eventInput(e){const [k,d,s,v,fresh,alias]=e,key='e'+e.slice(0,6).join(',');if(!this.cache.has(key))this.cache.set(key,this.input(cat(this.emb('command',2*k+alias),this.emb('name',d),this.emb('name',s),this.emb('value',v+2*fresh))));return this.cache.get(key);}
 cueInput(c,alias){const key='c'+c.join(',')+':'+alias;if(!this.cache.has(key))this.cache.set(key,this.input(cat(this.emb('command',8+alias),this.emb('name',c[0]),this.emb('name',c[1]),new Float32Array(12))));return this.cache.get(key);}
 cue(h,c,alias){const x=this.cueInput(c,alias),r=add(h,this.lin('route_out',mul(map(this.lin('route_state',h),Math.tanh),map(this.lin('route_context',x),sig))));return this.cell('observe',x,r);}
 send(h){const gate=f(sig(this.lin('gate',h)[0]));return map(this.lin('emit',h),x=>gate*f(Math.tanh(x)));}
 work(h,op,alias){if(op<0)return h;let c=this.emb('work_embedding',2*op+alias);return add(h,this.lin('work_out',mul(map(this.lin('work_state',h),Math.tanh),map(this.lin('work_context',c),sig))));}
 read(h,q,arg){return this.lin('answer.2',map(this.lin('answer.0',cat(h,this.emb('query',q),this.emb('argument',arg))),Math.tanh));}
 private(h){return this.lin('private',h);}
}
class Dyad{
 constructor(store,meta,lineage='A',variant='calibrated'){
  if(!['A','B'].includes(lineage)||!['parent','access','calibrated'].includes(variant))throw Error('Unknown model');
  this.lineage=lineage;this.variant=variant;this.c=meta.lineages[lineage].config;
  this.agents=[0,1].map(i=>new Network(store,`${lineage}.parent.agents.${i}.`));
  this.retrievers=variant==='parent'?this.agents:[0,1].map(i=>new Network(store,`${lineage}.${variant}.access.${i}.`));
 }
 initial(roles){return this.agents.map((a,i)=>map(a.emb('role',roles[i]),Math.tanh));}
 exchange(h,nets=this.agents,mode='intact'){
  if(!['intact','cut','cut_AtoB','cut_BtoA','skip_exchange'].includes(mode))throw Error('Unsupported access mode');
  let m=nets.map((a,i)=>a.send(h[i]));if(mode==='cut'||mode==='cut_AtoB')m[0]=new Float32Array(8);if(mode==='cut'||mode==='cut_BtoA')m[1]=new Float32Array(8);
  return mode==='skip_exchange'?h:nets.map((a,i)=>a.cell('receive',m[1-i],h[i]));
 }
 event(h,e){h=this.agents.map((a,i)=>a.cell('observe',a.eventInput(e),h[i]));for(let i=0;i<this.c.event_exchanges;i++)h=this.exchange(h);return h;}
 encode(events,roles){let h=this.initial(roles);for(const e of events)h=this.event(h,e);return h;}
 silent(h,n=this.c.delay){for(let j=0;j<n;j++)h=this.agents.map((a,i)=>a.cell('observe',a.blank(),h[i]));return h;}
 cue(h,c,alias=0,mode='intact',delay=this.c.delay,access=false){const nets=access?this.retrievers:this.agents;h=nets.map((a,i)=>a.cue(h[i],c,alias));for(let j=0;j<this.c.cue_exchanges;j++)h=this.exchange(h,nets,mode);return this.silent(h,delay);}
 retrieve(h,c,alias=0,mode='intact',delay=this.c.delay){/* Legacy base treats this unsupported mode as an intact exchange. */ if(this.variant==='parent' && mode==='skip_exchange')mode='intact';return this.cue(h,c,alias,mode,delay,true);}
 operate(h,op,alias=0){if(op<0)return h;h=this.agents.map((a,i)=>a.work(h[i],op,alias));for(let j=0;j<this.c.work_exchanges;j++)h=this.exchange(h);return h;}
 program(h,ops,aliases){for(let j=0;j<ops.length;j++)h=this.operate(h,ops[j],aliases[j]);return h;}
 outputs(h,q=0,arg=0){return this.agents.map((a,i)=>{const logits=a.read(h[i],q,arg),privateLogits=a.private(h[i]);return {logits:Array.from(logits),prediction:argmax(logits),privateLogits:Array.from(privateLogits),privatePrediction:argmax(privateLogits)};});}
}
function load(meta,buffer){if(buffer.byteLength!==meta.byte_length)throw Error('Weight length mismatch');const out={};for(const [k,t] of Object.entries(meta.tensors)){out[k]={shape:t.shape,data:new Float32Array(buffer,t.offset,t.length)};}return out;}
function truthOp(v,op){if(op===1)return [1-v[0],v[1]];if(op===2)return [v[0],1-v[1]];if(op===3)return [v[1],v[0]];return v.slice();}
function target(v,q=0,arg=0){const z=v[0]+2*v[1];return q===0?z:q===1?v[0]^v[1]:q===2?z^arg:Number(z===arg);}
function exactWorld(events){const m=Array(8).fill(0);for(const [k,d,s,v,fresh]of events){if(!fresh)continue;if(k===0)m[d]=v;else if(k===1)m[d]=1-m[d];else if(k===2)m[d]=m[s];else if(k===3)[m[d],m[s]]=[m[s],m[d]];else throw Error('event opcode');}return m;}
function runCase(d,spec){let h=d.encode(spec.events,spec.roles);h=d.cue(h,spec.cue,spec.alias, 'intact',0);h=d.program(h,spec.ops,spec.opAliases);h=d.silent(h);
 const phases=[{name:'post_work',state:h.map(x=>Array.from(x)),outputs:[0,1,2,3].map(q=>d.outputs(h,q,q===2?3:q===3?1:0))}];
 for(let t=0;t<spec.recalls.length;t++){const r=spec.recalls[t];h=d.retrieve(h,r.cue,r.alias,spec.mode);phases.push({name:'recall_'+t,state:h.map(x=>Array.from(x)),outputs:[0,1,2,3].map(q=>d.outputs(h,q,q===2?3:q===3?1:0))});}
 return phases;
}
const API={load,Dyad,truthOp,target,exactWorld,argmax,runCase};
if(typeof module!=='undefined'&&module.exports)module.exports=API;global.KomorebiEngine=API;
})(typeof globalThis==='undefined'?window:globalThis);
