import {rational as q,add,sub,mul,div,neg,str,approximate} from './chemistry-lab-core.mjs';
export {q,str,approximate};
const zero=q(0),one=q(1),four=q(4),lt=(a,b)=>a.n*b.d<b.n*a.d,le=(a,b)=>!lt(b,a),max=(a,b)=>lt(a,b)?b:a,min=(a,b)=>lt(a,b)?a:b,abs=a=>a.n<0n?neg(a):a,sq=a=>mul(a,a);
export const defaults={eta:'1/10',order:128,index:205};
export function settings(search){const p=new URLSearchParams(search);const eta=['1/100','1/10','1/2'].includes(p.get('cceta'))?p.get('cceta'):defaults.eta;let order=Number(p.get('cck'));if(![3,9,16,32,64,128,256,512].includes(order)||order===512&&eta!=='1/100')order=128;const value=p.get('cci');return {eta,order,index:value!==null&&/^\d+$/.test(value)?Math.min(400,Number(value)):205};}
export const short=v=>{v=typeof v==='number'?v:approximate(q(v));return v!==0&&(Math.abs(v)<.001||Math.abs(v)>=1e5)?v.toExponential(4):v.toLocaleString('en',{maximumSignificantDigits:6});};
export function dataset(data,state){const found=data.groups.find(c=>c.eta===state.eta&&c.order===state.order);if(!found)throw Error('Unavailable interval data');return found;}
function strength(p){return neg(q(p.center.imaginary));}
function gap(a,b,ra,rb,C,Cr){const d0=sub(strength(a[0]),strength(b[0])),d1=sub(strength(a[1]),strength(b[1])),r0=add(q(ra[0]),q(rb[0])),r1=add(q(ra[1]),q(rb[1])),bulge=div(add(C,Cr),four);return max(zero,max(sub(min(sub(d0,r0),sub(d1,r1)),bulge),neg(add(max(add(d0,r0),add(d1,r1)),bulge))));}
export function validate(data){
  if(data.version!==1||data.kind!=='continuous-energy-certificates'||data.groups.length!==22)throw Error('Unexpected interval fixture');
  const seen=new Set();let count=0;
  for(const c of data.groups){
    const key=c.eta+':'+c.order;if(seen.has(key)||!['1/100','1/10','1/2'].includes(c.eta)||![3,9,16,32,64,128,256,512].includes(c.order)||c.order===512&&c.eta!=='1/100'||!le(zero,q(c.maximum_radius))||!le(zero,q(c.whole_interval_gap)))throw Error('Invalid curve');seen.add(key);
    if(c.points.length!==c.reduced_points.length||c.cells.length!==c.points.length-1)throw Error('Cell coverage mismatch');
    const eta=q(c.eta);if(!lt(zero,eta))throw Error('Nonpositive broadening');let globalRadius=zero,globalGap=null;
    if(str(q(c.points[0].energy))!==str(add(q(data.ground_reference),q('3/10')))||str(q(c.points.at(-1).energy))!==str(add(q(data.ground_reference),q('7/10'))))throw Error('Wrong interval domain');
    for(let i=0;i<c.cells.length;i++){
      const cell=c.cells[i],h=sub(q(c.points[i+1].energy),q(c.points[i].energy));if(!lt(zero,h))throw Error('Unordered energies');
      for(const [points,coefficient] of [[c.points,cell.coefficient],[c.reduced_points,cell.reduced_coefficient]]){
        const C=q(coefficient),r0=q(points[i].radius),r1=q(points[i+1].radius),u0=add(strength(points[i]),r0),u1=add(strength(points[i+1]),r1);
        if(![C,r0,r1,u0,u1].every(x=>le(zero,x))||!le(mul(sq(sq(h)),mul(u0,u1)),mul(sq(C),sq(sq(eta)))))throw Error('Interpolation inequality failed');
        for(const p of [points[i],points[i+1]])if(p.eta!==c.eta||str(add(q(p.energy),q(p.omega)))!==str(q(data.ground_reference)))throw Error('Mixed energy coordinates');
      }
      if(c.points[i].energy!==c.reduced_points[i].energy||c.points[i+1].energy!==c.reduced_points[i+1].energy)throw Error('Comparison grids differ');
      const C=q(cell.coefficient),Cr=q(cell.reduced_coefficient),radius=add(max(q(c.points[i].radius),q(c.points[i+1].radius)),div(C,four));
      if(!le(radius,q(cell.uniform_radius)))throw Error('Uniform radius too small');globalRadius=max(globalRadius,q(cell.uniform_radius));
      const lower=gap(c.points.slice(i,i+2),c.reduced_points.slice(i,i+2),c.points.slice(i,i+2).map(p=>p.radius),c.reduced_points.slice(i,i+2).map(p=>p.radius),C,Cr);
      if(!le(zero,q(cell.gap_lower))||!le(q(cell.gap_lower),lower))throw Error('Gap lower bound too large');globalGap=globalGap===null?q(cell.gap_lower):min(globalGap,q(cell.gap_lower));count++;
    }
    if(!le(globalRadius,q(c.maximum_radius))||!le(q(c.whole_interval_gap),globalGap))throw Error('Whole-interval summary invalid');
  }
  if(!le(q(dataset(data,{eta:'1/100',order:512}).maximum_radius),q(data.narrow.tolerance)))throw Error('Narrow tolerance was not met');
  return count;
}
function interpolate(a,b,t,C){const u=sub(one,t);return {center:{real:str(add(mul(u,q(a.center.real)),mul(t,q(b.center.real)))),imaginary:str(add(mul(u,q(a.center.imaginary)),mul(t,q(b.center.imaginary))))},radius:str(add(add(mul(u,q(a.radius)),mul(t,q(b.radius))),mul(mul(t,u),C)))};}
export function selection(data,state){
  const c=dataset(data,state),omega=add(q('-7/10'),div(q(state.index),q(1000))),energy=sub(q(data.ground_reference),omega);let i=c.points.length-2;
  for(let j=0;j<c.cells.length;j++)if(le(energy,q(c.points[j+1].energy))){i=j;break;}
  const a=c.points[i],b=c.points[i+1],t=div(sub(energy,q(a.energy)),sub(q(b.energy),q(a.energy)));if(!le(zero,t)||!le(t,one))throw Error('Energy outside the certified cell');
  const cell=c.cells[i],full=interpolate(a,b,t,q(cell.coefficient)),reduced=interpolate(c.reduced_points[i],c.reduced_points[i+1],t,q(cell.reduced_coefficient));
  const lower=max(zero,sub(abs(sub(q(full.center.imaginary),q(reduced.center.imaginary))),add(q(full.radius),q(reduced.radius))));
  return {curve:c,cell_index:i,cell,t:str(t),energy:str(energy),omega:str(omega),full,reduced,point_gap_lower:str(lower)};
}
export function certificate(data,state,digest){const s=selection(data,state),i=s.cell_index;return {version:1,kind:'continuous-energy-response',settings:state,scope:data.scope,arithmetic:data.arithmetic,public_data_sha256:digest,input_view_sha256:data.input_view_sha256,stage15_data_sha256:data.stage15_data_sha256,eta:state.eta,actions:state.order,extra_hamiltonian_actions:0,energy:s.energy,omega:s.omega,interpolation_fraction:s.t,full_response:s.full,reduced_response:s.reduced,point_discrepancy_lower:s.point_gap_lower,cell_discrepancy_lower:s.cell.gap_lower,whole_interval_discrepancy_lower:s.curve.whole_interval_gap,whole_interval_radius:s.curve.maximum_radius,cell:{...s.cell,full_endpoints:s.curve.points.slice(i,i+2),reduced_endpoints:s.curve.reduced_points.slice(i,i+2)},evidence:data.evidence,units:'Hartree for energies and broadening; inverse Hartree for response and radius'};}
export function plot(data,state,compact=false){
  const c=dataset(data,state),s=selection(data,state),W=compact?320:800,H=compact?300:340,left=60,right=16,top=20,bottom=55,values=[...c.points,...c.reduced_points].map(p=>approximate(strength(p))),hi=Math.max(.01,...values)*1.12,lo=Math.min(0,...values)*1.12;
  const x=p=>left+(approximate(q(p.omega))+.7)/.4*(W-left-right),y=v=>top+(hi-v)/(hi-lo)*(H-top-bottom);
  const centerPath=points=>points.map((p,i)=>(i?'L':'M')+x(p)+','+y(approximate(strength(p)))).join(' ');
  function band(points,field){
    let path='M'+x(points[0])+','+y(approximate(strength(points[0]))+approximate(q(points[0].radius)));
    for(let i=0;i<c.cells.length;i++){const a=points[i],b=points[i+1],A=approximate(strength(a))+approximate(q(a.radius)),B=approximate(strength(b))+approximate(q(b.radius)),C=approximate(q(c.cells[i][field]));path+=` Q${(x(a)+x(b))/2},${y((A+B)/2+C/2)} ${x(b)},${y(B)}`;}
    const end=points.at(-1);path+=' L'+x(end)+','+y(approximate(strength(end))-approximate(q(end.radius)));
    for(let i=c.cells.length-1;i>=0;i--){const a=points[i],b=points[i+1],A=approximate(strength(a))-approximate(q(a.radius)),B=approximate(strength(b))-approximate(q(b.radius)),C=approximate(q(c.cells[i][field]));path+=` Q${(x(a)+x(b))/2},${y((A+B)/2-C/2)} ${x(a)},${y(A)}`;}return path+' Z';
  }
  const capped=c.cells.filter((cell,i)=>{const a=values[i],b=values[i+1],R=approximate(q(cell.uniform_radius));return Math.max(a,b)+R>hi||Math.min(a,b)-R<lo;}).length;
  const ticks=(compact?[0,.5,1]:[0,.25,.5,.75,1]).map(t=>{const value=lo+t*(hi-lo);return `<path class="cr-grid" d="M${left},${y(value)}H${W-right}"/><text x="${left-8}" y="${y(value)+4}" text-anchor="end">${Number(value.toPrecision(3))}</text>`;}).join('');
  const xticks=(compact?[-.7,-.5,-.3]:[-.7,-.6,-.5,-.4,-.3]).map(v=>`<text x="${left+(v+.7)/.4*(W-left-right)}" y="${H-bottom+23}" text-anchor="middle">${v}</text>`).join('');
  const xx=x({omega:s.omega}),full=-approximate(q(s.full.center.imaginary)),red=-approximate(q(s.reduced.center.imaginary));
  return {capped,svg:`<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="cc-title cc-desc"><title id="cc-title">Continuous response enclosures</title><desc id="cc-desc">Shaded bounds enclose the responses at all energies in every recorded cell, conditional on the endpoint arithmetic assumptions. ${c.points.length} endpoint energies, ${state.order} full-target actions. The selected energy readout and exact certificate follow.</desc><defs><clipPath id="cc-window"><rect x="${left}" y="${top}" width="${W-left-right}" height="${H-top-bottom}"/></clipPath></defs>${ticks}${xticks}<g clip-path="url(#cc-window)"><path class="cc-band-full" d="${band(c.points,'coefficient')}"/><path class="cc-band-reduced" d="${band(c.reduced_points,'reduced_coefficient')}"/><path class="cr-line-full" d="${centerPath(c.points)}"/><path class="cr-line-reduced" d="${centerPath(c.reduced_points)}"/><path class="cr-guide" d="M${xx},${top}V${H-bottom}"/><circle class="cr-dot-full" cx="${xx}" cy="${y(full)}" r="5"/><path class="cr-dot-reduced" d="M${xx},${y(red)-5}l5,5l-5,5l-5,-5Z"/></g><text x="${(left+W-right)/2}" y="${H-5}" text-anchor="middle">${compact?'ω (Hartree)':'Removal coordinate ω (Hartree)'}</text></svg>`};
}
