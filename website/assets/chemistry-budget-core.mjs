// Exact saved-node planner. Short labels and SVG coordinates are approximate.
import {rational as q,add,sub,mul,div,str,sqrtUpper,approximate} from './chemistry-lab-core.mjs';
import {validate as validateContinuous} from './chemistry-continuous-core.mjs';
export {q,str,approximate};
const Z=q(0),O=q(1),scale=q('1000000000000000000');
const le=(a,b)=>a.n*b.d<=b.n*a.d,eq=(a,b)=>a.n*b.d===b.n*a.d;
const max=(a,b)=>le(a,b)?b:a,abs=a=>a.n<0n?q({n:-a.n,d:a.d}):a;
const ceil=a=>{const x=mul(a,scale),n=x.n/x.d+(x.n%x.d>0n?1n:0n);return div(q(n),scale);};
export const defaults={eta:'1/10',tolerance:'0.1',objective:'actions'};
export function tolerance(value){
  const text=String(value).trim();if(!text||text.length>80)throw Error('Enter a positive decimal or fraction.');
  let a;
  if(/^\d+(?:\/[1-9]\d*)?$/.test(text))a=q(text);
  else{const m=/^(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d{1,2}))?$/.exec(text);if(!m||!(m[1]+(m[2]||'')))throw Error('Enter a positive decimal or fraction.');const digits=m[1]+(m[2]||''),exp=Number(m[3]||0)-(m[2]||'').length;a=exp>=0?mul(q(BigInt(digits)),q(10n**BigInt(exp))):div(q(BigInt(digits)),q(10n**BigInt(-exp)));}
  if(a.n<=0n)throw Error('The radius must be positive.');return a;
}
export function settings(search){
  const p=new URLSearchParams(search),s={...defaults};if(['1/100','1/10','1/2'].includes(p.get('bpeta')))s.eta=p.get('bpeta');if(['actions','energies'].includes(p.get('bpgoal')))s.objective=p.get('bpgoal');
  if(p.has('bptol')){try{tolerance(p.get('bptol'));s.tolerance=p.get('bptol');}catch{}}return s;
}
export function permalink(state){
  tolerance(state.tolerance);
  return 'chemistry-responses.html?'+new URLSearchParams({bpeta:state.eta,bptol:state.tolerance.trim(),bpgoal:state.objective}).toString()+'#cr-plan';
}
export function sharp(r0,r1,C){
  if(!le(Z,r0)||!le(Z,r1)||!le(Z,C))throw Error('Invalid nonnegative radius');const delta=sub(r1,r0);
  return !C.n||le(C,abs(delta))?max(r0,r1):add(add(div(add(r0,r1),q(2)),div(C,q(4))),div(mul(delta,delta),mul(q(4),C)));
}
const memo=new WeakMap();
export function edge(curve,i,j){
  let saved=memo.get(curve);if(!saved){saved=new Map();memo.set(curve,saved);}const key=i+':'+j;if(saved.has(key))return saved.get(key);
  const a=curve.points[i],b=curve.points[j],eta=q(curve.eta),h=sub(q(b.energy),q(a.energy)),r0=q(a.radius),r1=q(b.radius),U0=sub(r0,q(a.center.imaginary)),U1=sub(r1,q(b.center.imaginary));
  if(i>=j||!le(Z,U0)||!le(Z,U1))throw Error('Invalid planning cell');const C=ceil(mul(div(mul(h,h),mul(eta,eta)),sqrtUpper(mul(U0,U1)))),R=ceil(sharp(r0,r1,C));
  const result={coefficient:C,radius:R};saved.set(key,result);return result;
}
export function validate(plans,data){
  validateContinuous(data);if(plans.version!==1||plans.kind!=='saved-node-precision-planner'||plans.extra_hamiltonian_actions!==0||plans.groups.length!==data.groups.length)throw Error('Planner data convention mismatch');
  const seen=new Set();let rows=0;
  for(const g of plans.groups){const key=g.eta+':'+g.order;if(seen.has(key))throw Error('Duplicate planner cache');seen.add(key);const c=data.groups.find(c=>c.eta===g.eta&&c.order===g.order);if(!c||g.saved_nodes!==c.points.length||!g.frontier.length)throw Error('Saved node pool mismatch');let previousNodes=1,previousRadius=null;
    for(const r of g.frontier){const ids=r.indices;if(r.nodes<=previousNodes||ids.length!==r.nodes||ids[0]!==0||ids.at(-1)!==g.saved_nodes-1||ids.some((i,k)=>!Number.isInteger(i)||i<0||i>=g.saved_nodes||(k&&i<=ids[k-1])))throw Error('Planner path ordering mismatch');
      let R=Z;for(let k=1;k<ids.length;k++)R=max(R,edge(c,ids[k-1],ids[k]).radius);if(!eq(R,q(r.radius))||(previousRadius&&le(previousRadius,R)))throw Error('Planner frontier bound mismatch');previousRadius=R;previousNodes=r.nodes;rows++;
    }
  }if(rows!==717)throw Error('Incomplete saved frontier');return rows;
}
export function options(plans,state){const T=tolerance(state.tolerance);return plans.groups.filter(g=>g.eta===state.eta).map(g=>({group:g,plan:g.frontier.find(r=>le(q(r.radius),T))||null}));}
export function select(plans,state){
  if(!['actions','energies'].includes(state.objective))throw Error('Unknown planning objective');const available=options(plans,state).filter(x=>x.plan);
  available.sort((a,b)=>state.objective==='actions'?(a.group.order-b.group.order||a.plan.nodes-b.plan.nodes):(a.plan.nodes-b.plan.nodes||a.group.order-b.group.order));return available[0]||null;
}
export function certificate(plans,data,state,hashes){
  const chosen=select(plans,state);if(!chosen)return null;const {group:g,plan:p}=chosen,c=data.groups.find(c=>c.eta===g.eta&&c.order===g.order),cells=[];
  for(let k=1;k<p.indices.length;k++){const i=p.indices[k-1],j=p.indices[k],e=edge(c,i,j);cells.push({left_saved_index:i,right_saved_index:j,left_energy:c.points[i].energy,right_energy:c.points[j].energy,coefficient:str(e.coefficient),sharp_uniform_radius:str(e.radius)});}
  return {version:1,kind:'saved-node-scan-plan',settings:{eta:state.eta,tolerance:str(tolerance(state.tolerance)),objective:state.objective},source_sha256:hashes,hamiltonian_actions:g.order,endpoint_evaluations:p.nodes,saved_node_pool:g.saved_nodes,maximum_radius:p.radius,new_hamiltonian_actions_performed_by_planner:0,selected_indices:p.indices.slice(),energies:p.indices.map(i=>({energy:c.points[i].energy,omega:c.points[i].omega})),cells,optimality_scope:plans.optimization,browser_check:'Selected edge bounds use exact fractions. Global finite minimality is established by the published recurrence and recorded audit, not by a fresh complete optimization in this browser.',scope:data.scope};
}
export function strip(curve,indices,mobile=false){
  const width=mobile?300:880,left=22,right=width-22,x=i=>left+(approximate(q(curve.points[i].omega))+.7)/.4*(right-left),ticks=[[-.7,'-0.70'],[-.5,'-0.50'],[-.3,'-0.30']];
  return `<svg viewBox="0 0 ${width} 100" role="img" aria-labelledby="bp-grid-title"><title id="bp-grid-title">${indices.length} selected energy nodes from ${curve.points.length} saved nodes</title><path d="M${left} 47H${right}" class="bp-axis"/>${curve.points.map((_,i)=>`<path d="M${x(i)} 36V58" class="bp-saved"/>`).join('')}${indices.map(i=>`<path d="M${x(i)} 24V69" class="bp-selected"/>`).join('')}${ticks.map(([v,label])=>`<text x="${left+(v+.7)/.4*(right-left)}" y="88" text-anchor="middle">${label}</text>`).join('')}</svg>`;
}
export const short=value=>{const x=approximate(q(value));return Number(x.toPrecision(5)).toString();};
