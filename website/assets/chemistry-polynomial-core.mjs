// Exact local polynomial bounds. SVG coordinates and short labels are approximate.
import {rational as q,add,sub,mul,div,neg,str,approximate} from './chemistry-lab-core.mjs';
export {q,str,approximate};
const Z=q(0),O=q(1),HALF=q('1/2'),le=(a,b)=>a.n*b.d<=b.n*a.d,lt=(a,b)=>!le(b,a),max=(a,b)=>le(a,b)?b:a,min=(a,b)=>le(a,b)?a:b,abs=a=>a.n<0n?neg(a):a;
const power=(a,n)=>{let x=O;for(let i=0;i<n;i++)x=mul(x,a);return x;};
const choose=(n,k)=>{let x=1;for(let i=1;i<=k;i++)x=x*(n-i+1)/i;return x;};
const sum=a=>a.reduce(add,Z),scale=(a,s)=>a.map(x=>mul(x,s));
const plus=(a,b)=>Array.from({length:Math.max(a.length,b.length)},(_,i)=>add(a[i]||Z,b[i]||Z));
function times(a,b){const out=Array(a.length+b.length-1).fill(Z);a.forEach((x,i)=>b.forEach((y,j)=>out[i+j]=add(out[i+j],mul(x,y))));return out;}
export const evaluatePolynomial=(a,t)=>a.reduceRight((r,x)=>add(mul(r,t),x),Z);
export function bernstein(a,n=a.length-1){if(n<a.length-1)throw Error('Degree too small');return Array.from({length:n+1},(_,k)=>sum(a.slice(0,k+1).map((x,j)=>mul(x,div(q(choose(k,j)),q(choose(n,j)))))));}
function split(b){const levels=[b];while(levels.at(-1).length>1){const r=levels.at(-1);levels.push(r.slice(1).map((x,i)=>mul(add(x,r[i]),HALF)));}return [levels.map(r=>r[0]),levels.map(r=>r.at(-1)).reverse()];}
export function leaves(b,depth=2){if(!depth)return [b];const [a,c]=split(b);return [...leaves(a,depth-1),...leaves(c,depth-1)];}
function extrema(a,n=a.length-1){const v=leaves(bernstein(a,n)).flat();return {lower:v.reduce(min),upper:v.reduce(max)};}
export function cubicEnvelope(input){let b=input,n=b.length-1;
  while(n<3){const degree=n+1;b=[b[0],...Array.from({length:degree-1},(_,j)=>{const k=j+1;return add(mul(q(k+'/'+degree),b[k-1]),mul(q((degree-k)+'/'+degree),b[k]));}),b.at(-1)];n=degree;}
  const c=[b[0],add(b[0],mul(q(n+'/3'),sub(b[1],b[0]))),sub(b.at(-1),mul(q(n+'/3'),sub(b.at(-1),b.at(-2)))),b.at(-1)];
  if(n===3)return {controls:c,padding:Z};if(n!==4)throw Error('Display degree exceeds four');
  const elevated=Array.from({length:5},(_,j)=>sum(c.map((x,k)=>j-k>=0&&j-k<=1?mul(x,q((choose(3,k)*choose(1,j-k))+'/'+choose(4,j))):Z)));
  if([0,1,3,4].some(i=>sub(b[i],elevated[i]).n))throw Error('Cubic endpoint identity failed');return {controls:c,padding:mul(abs(sub(b[2],elevated[2])),q('3/8'))};
}
const geometries=new Map();
function geometry(nodes){const key=nodes.map(str).join(',');if(geometries.has(key))return geometries.get(key);
  const m=nodes.length;if(![2,3,4].includes(m)||new Set(nodes.map(str)).size!==m||!nodes.some(x=>!x.n)||!nodes.some(x=>!sub(x,O).n)||nodes.some(x=>lt(Z,x)&&lt(x,O)))throw Error('Invalid local stencil');
  let P=[O];for(const x of nodes)P=times(P,[neg(x),O]);const L=[],A=[];
  for(let j=0;j<m;j++){let p=[O],den=O;for(let k=0;k<m;k++)if(k!==j){p=times(p,[neg(nodes[k]),O]);den=mul(den,sub(nodes[j],nodes[k]));}p=scale(p,div(O,den));L.push(p);A.push(scale(p,evaluatePolynomial(p,HALF).n>0n?O:q(-1)));}
  P=scale(P,evaluatePolynomial(P,HALF).n>0n?O:q(-1));const result={L,A,P};geometries.set(key,result);return result;
}
function sharp(r0,r1,C){const d=sub(r1,r0);return !C.n||le(C,abs(d))?max(r0,r1):add(add(mul(add(r0,r1),HALF),div(C,q(4))),div(mul(d,d),mul(q(4),C)));}
function compile(points,record,i){const ids=record.stencil,m=ids.length;
  if(![2,3,4].includes(m)||!ids.includes(i)||!ids.includes(i+1)||ids.some((j,k)=>!Number.isInteger(j)||j<0||j>=points.length||(k&&j<=ids[k-1])))throw Error('Polynomial stencil ordering failed');
  const a=q(points[i].energy),h=sub(q(points[i+1].energy),a),eta=q(points[i].eta),C=q(record.coefficient);if(!lt(Z,h)||!lt(Z,eta)||!le(Z,C))throw Error('Invalid polynomial coefficient');
  const U=ids.map(j=>sub(q(points[j].radius),q(points[j].center.imaginary)));if(U.some(x=>!le(Z,x)))throw Error('Invalid endpoint strength');let smallest=null;
  for(let j=0;j<m;j++)for(let k=j+1;k<m;k++)smallest=smallest===null?mul(U[j],U[k]):min(smallest,mul(U[j],U[k]));
  if(!le(mul(power(h,2*m),smallest),mul(mul(C,C),power(eta,2*m))))throw Error('Polynomial interpolation inequality failed');
  const g=geometry(ids.map(j=>div(sub(q(points[j].energy),a),h)));let real=[Z],imag=[Z],radius=scale(g.P,C);
  ids.forEach((j,k)=>{real=plus(real,scale(g.L[k],q(points[j].center.real)));imag=plus(imag,scale(g.L[k],q(points[j].center.imaginary)));radius=plus(radius,scale(g.A[k],q(points[j].radius)));});
  const R=m===2?sharp(q(points[i].radius),q(points[i+1].radius),C):extrema(radius,m).upper;
  if(!le(R,q(record.uniform_radius)))throw Error('Polynomial uniform radius too small');return {real,imag,radius,degree:m-1,record};
}
const compiled=new WeakMap();
function prepare(poly,data){let per=compiled.get(poly);if(!per){per=new WeakMap();compiled.set(poly,per);}if(per.has(data))return per.get(data);const all=new Map();
  if(poly.version!==1||poly.kind!=='local-polynomial-response-certificates'||poly.subdivision_depth!==2||poly.groups.length!==data.groups.length||poly.new_hamiltonian_actions!==0||poly.new_endpoint_evaluations!==0)throw Error('Unexpected polynomial data');
  for(const g of poly.groups){const key=g.eta+':'+g.order,c=data.groups.find(x=>x.eta===g.eta&&x.order===g.order);if(all.has(key)||!c||g.nodes!==c.points.length||g.cells.length!==c.cells.length)throw Error('Polynomial curve coverage failed');let R=Z,Rr=Z,G=null;const cells=[];
    for(let i=0;i<g.cells.length;i++){const saved=g.cells[i],full=compile(c.points,saved.full,i),reduced=compile(c.reduced_points,saved.reduced,i),D=plus(scale(full.imag,q(-1)),reduced.imag),rs=plus(full.radius,reduced.radius),n=Math.max(D.length,rs.length)-1,lower=extrema(plus(D,scale(rs,q(-1))),n).lower,upper=extrema(plus(D,rs),n).upper;
      if(!le(q(saved.gap.signed_lower),lower)||!le(upper,q(saved.gap.signed_upper))||!le(Z,q(saved.gap.absolute_lower))||!le(q(saved.gap.absolute_lower),max(Z,max(q(saved.gap.signed_lower),neg(q(saved.gap.signed_upper))))))throw Error('Polynomial comparison bound failed');
      if(!le(q(saved.full.uniform_radius),q(c.cells[i].uniform_radius)))throw Error('Polynomial fallback is worse than published linear bound');R=max(R,q(saved.full.uniform_radius));Rr=max(Rr,q(saved.reduced.uniform_radius));G=G===null?q(saved.gap.absolute_lower):min(G,q(saved.gap.absolute_lower));cells.push({full,reduced});
    }
    if(!le(R,q(g.maximum_radius))||!le(Rr,q(g.maximum_reduced_radius))||!le(q(g.whole_interval_gap),G))throw Error('Polynomial whole-interval summary failed');all.set(key,{group:g,source:c,cells});
  }per.set(data,all);return all;
}
export function validatePolynomial(poly,data){return [...prepare(poly,data).values()].reduce((s,g)=>s+g.cells.length,0);}
export function polynomialSelection(data,poly,state){const c=prepare(poly,data).get(state.eta+':'+state.order);if(!c)throw Error('Unavailable polynomial curve');const omega=add(q('-7/10'),div(q(state.index),q(1000))),energy=sub(q(data.ground_reference),omega);let i=c.cells.length-1;
  for(let j=0;j<c.cells.length;j++)if(le(energy,q(c.source.points[j+1].energy))){i=j;break;}
  const t=div(sub(energy,q(c.source.points[i].energy)),sub(q(c.source.points[i+1].energy),q(c.source.points[i].energy)));if(!le(Z,t)||!le(t,O))throw Error('Energy outside the polynomial cell');
  const evaluate=p=>({center:{real:str(evaluatePolynomial(p.real,t)),imaginary:str(evaluatePolynomial(p.imag,t))},radius:str(evaluatePolynomial(p.radius,t))}),full=evaluate(c.cells[i].full),reduced=evaluate(c.cells[i].reduced),saved=c.group.cells[i];
  return {curve:{...c.source,maximum_radius:c.group.maximum_radius,whole_interval_gap:c.group.whole_interval_gap},cell:{uniform_radius:saved.full.uniform_radius,gap_lower:saved.gap.absolute_lower},cell_index:i,t:str(t),energy:str(energy),omega:str(omega),full,reduced,point_gap_lower:str(max(Z,sub(abs(sub(q(full.center.imaginary),q(reduced.center.imaginary))),add(q(full.radius),q(reduced.radius))))),degree:c.cells[i].full.degree,polynomial_cell:saved};
}
export function polynomialCertificate(data,poly,state,hashes){const s=polynomialSelection(data,poly,state),c=data.groups.find(c=>c.eta===state.eta&&c.order===state.order),i=s.cell_index;
  return {version:1,kind:'local-polynomial-energy-response',settings:{...state,method:'polynomial'},scope:poly.scope,arithmetic:poly.arithmetic,source_sha256:hashes,actions:state.order,extra_hamiltonian_actions:0,new_endpoint_evaluations:0,energy:s.energy,omega:s.omega,interpolation_fraction:s.t,full_response:s.full,reduced_response:s.reduced,whole_interval_radius:s.curve.maximum_radius,whole_interval_discrepancy_lower:s.curve.whole_interval_gap,cell_discrepancy_lower:s.cell.gap_lower,point_discrepancy_lower:s.point_gap_lower,cell:{...s.polynomial_cell,full_stencil:s.polynomial_cell.full.stencil.map(j=>c.points[j]),reduced_stencil:s.polynomial_cell.reduced.stencil.map(j=>c.reduced_points[j])},evidence:poly.evidence,units:'Hartree for energy and broadening; inverse Hartree for response and radius'};
}
const graphCache=new WeakMap();
export function polynomialPlot(data,poly,state,compact=false){const c=prepare(poly,data).get(state.eta+':'+state.order),s=polynomialSelection(data,poly,state),W=compact?320:800,H=compact?300:340,left=60,right=16,top=20,bottom=55,values=[...c.source.points,...c.source.reduced_points].map(p=>-approximate(q(p.center.imaginary))),hi=Math.max(.01,...values)*1.12,lo=Math.min(0,...values)*1.12,x=omega=>left+(approximate(q(omega))+.7)/.4*(W-left-right),y=v=>top+(hi-v)/(hi-lo)*(H-top-bottom);
  let cache=graphCache.get(c);if(!cache){cache=new Map();graphCache.set(c,cache);}const cacheKey=compact?'small':'large';let drawing=cache.get(cacheKey);
  if(!drawing){let fullBand='',redBand='',fullLine='',redLine='',capped=0;
    const path=(v,xx)=>`M${xx[0]},${y(approximate(v[0]))} C${xx[1]},${y(approximate(v[1]))} ${xx[2]},${y(approximate(v[2]))} ${xx[3]},${y(approximate(v[3]))}`;
    for(let i=0;i<c.cells.length;i++)for(const [field,bandName,lineName]of [['full','full','full'],['reduced','red','red']]){const p=c.cells[i][field],center=scale(p.imag,q(-1)),degree=p.radius.length-1,upper=leaves(bernstein(plus(center,p.radius),degree)),lower=leaves(bernstein(plus(center,scale(p.radius,q(-1))),degree)),middle=leaves(bernstein(center,Math.max(3,center.length-1))),a=q(c.source.points[i].omega),b=q(c.source.points[i+1].omega);
      for(let k=0;k<4;k++){const a0=add(a,mul(sub(b,a),q(k+'/4'))),b0=add(a,mul(sub(b,a),q((k+1)+'/4'))),xx=[0,1,2,3].map(j=>x(str(add(a0,mul(sub(b0,a0),q(j+'/3')))))),up=cubicEnvelope(upper[k]),down=cubicEnvelope(lower[k]),u=up.controls.map(v=>add(v,up.padding)),d=down.controls.map(v=>sub(v,down.padding));
        if(u.some(v=>approximate(v)>hi)||d.some(v=>approximate(v)<lo))capped++;
        const band=path(u,xx)+` L${xx[3]},${y(approximate(d[3]))} C${xx[2]},${y(approximate(d[2]))} ${xx[1]},${y(approximate(d[1]))} ${xx[0]},${y(approximate(d[0]))} Z`,line=path(cubicEnvelope(middle[k]).controls,xx);
        if(field==='full'){fullBand+=band+' ';fullLine+=line+' ';}else{redBand+=band+' ';redLine+=line+' ';}
      }
    }drawing={fullBand,redBand,fullLine,redLine,capped};cache.set(cacheKey,drawing);
  }
  const ticks=(compact?[0,.5,1]:[0,.25,.5,.75,1]).map(t=>{const v=lo+t*(hi-lo);return `<path class="cr-grid" d="M${left},${y(v)}H${W-right}"/><text x="${left-8}" y="${y(v)+4}" text-anchor="end">${Number(v.toPrecision(3))}</text>`;}).join(''),xticks=(compact?['-7/10','-1/2','-3/10']:['-7/10','-3/5','-1/2','-2/5','-3/10']).map(v=>`<text x="${x(v)}" y="${H-bottom+23}" text-anchor="middle">${approximate(q(v))}</text>`).join(''),xx=x(s.omega),full=-approximate(q(s.full.center.imaginary)),red=-approximate(q(s.reduced.center.imaginary));
  return {capped:drawing.capped,svg:`<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="cp-title cp-desc"><title id="cp-title">Local polynomial response enclosures</title><desc id="cp-desc">Bounds cover every energy in each saved cell under the endpoint assumptions. Cubic drawing envelopes include outward padding. Exact readout follows.</desc><defs><clipPath id="cp-window"><rect x="${left}" y="${top}" width="${W-left-right}" height="${H-top-bottom}"/></clipPath></defs>${ticks}${xticks}<g clip-path="url(#cp-window)"><path class="cc-band-full" d="${drawing.fullBand}"/><path class="cc-band-reduced" d="${drawing.redBand}"/><path class="cr-line-full" d="${drawing.fullLine}"/><path class="cr-line-reduced" d="${drawing.redLine}"/><path class="cr-guide" d="M${xx},${top}V${H-bottom}"/><circle class="cr-dot-full" cx="${xx}" cy="${y(full)}" r="5"/><path class="cr-dot-reduced" d="M${xx},${y(red)-5}l5,5l-5,5l-5,-5Z"/></g><text x="${(left+W-right)/2}" y="${H-5}" text-anchor="middle">${compact?'ω (Hartree)':'Removal coordinate ω (Hartree)'}</text></svg>`};
}
export function fullGridAlternative(poly,state,T){const list=poly.groups.filter(g=>g.eta===state.eta&&le(q(g.maximum_radius),T));list.sort((a,b)=>state.objective==='energies'?(a.nodes-b.nodes||a.order-b.order):(a.order-b.order||a.nodes-b.nodes));return list[0]||null;}
export function fullGridCertificate(data,poly,group,T,hashes){const source=data.groups.find(c=>c.eta===group.eta&&c.order===group.order);return {version:1,kind:'polynomial-full-saved-grid',eta:group.eta,tolerance:str(T),hamiltonian_actions:group.order,endpoint_evaluations:group.nodes,new_hamiltonian_actions_performed_by_planner:0,new_endpoint_evaluations:0,maximum_radius:group.maximum_radius,source_sha256:hashes,energies:source.points.map(p=>({energy:p.energy,omega:p.omega})),cells:group.cells,scope:poly.scope,optimality_scope:'Qualifying full saved grids only. No polynomial minimum-node plan or universal solver optimum is claimed.'};}
const downloads=new Map();
export function fetchPolynomial(url,digest){if(!url||!digest)return Promise.reject(Error('Polynomial data not configured'));const key=url+':'+digest;if(downloads.has(key))return downloads.get(key);
  const promise=(async()=>{const r=await fetch(url);if(!r.ok)throw Error('Polynomial data unavailable');const bytes=await r.arrayBuffer(),actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');if(actual!==digest)throw Error('Polynomial data identity mismatch');return JSON.parse(new TextDecoder().decode(bytes));})().catch(e=>{downloads.delete(key);throw e;});downloads.set(key,promise);return promise;
}
