'use strict';
(function(){
const $=id=>document.getElementById(id);
const R=316,CX=450,CY=399;
const svgNS='http://www.w3.org/2000/svg';
const states={r:25,x:25,z0:50,special:null,length:0,N:8,k:0,j:0,rho:.94,sampleCount:96};
let referencePin=null;
const loadUndoStack=[],loadRedoStack=[];
const MAX_LOAD_HISTORY=60;
let activeFieldOrigin=null,dragOrigin=null;
const coefficients=Array.from({length:32},(_,i)=>1/(i+1));
let drag=false,lastTestResults=[];
let gammaDraftDirty=false;
let lastGridKey='';
const adaptiveCache=new Map();
const C=(re=0,im=0)=>({re,im});
const add=(a,b)=>C(a.re+b.re,a.im+b.im),sub=(a,b)=>C(a.re-b.re,a.im-b.im),scale=(a,t)=>C(a.re*t,a.im*t);
const mul=(a,b)=>C(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
function div(a,b){
  const s=Math.max(Math.abs(b.re),Math.abs(b.im));
  if(!Number.isFinite(s)||s===0)return C(NaN,NaN);
  const br=b.re/s,bi=b.im/s,d=br*br+bi*bi,ar=a.re/s,ai=a.im/s;
  return C((ar*br+ai*bi)/d,(ai*br-ar*bi)/d);
}
const abs=a=>Math.hypot(a.re,a.im);
const expi=t=>C(Math.cos(t),Math.sin(t));
const gammaFromZ=z=>div(sub(z,C(1)),add(z,C(1)));
const zFromGamma=g=>div(add(C(1),g),sub(C(1),g));
const phaseMobius=(z,n,k)=>{const w=expi(2*Math.PI*k/n);return div(add(mul(add(C(1),w),z),sub(C(1),w)),add(mul(sub(C(1),w),z),add(C(1),w)))};
function evaluateF(g){let s=C(0),p=C(1);for(let i=0;i<coefficients.length;i++){s=add(s,scale(p,coefficients[i]));p=mul(p,g)}return s}
function packetValue(g,n,j){let s=C(0),p=C(1);for(let i=0;i<coefficients.length;i++){if(i%n===((j%n)+n)%n)s=add(s,scale(p,coefficients[i]));p=mul(p,g)}return s}
function powComplex(z,n){let r=C(1);for(let i=0;i<n;i++)r=mul(r,z);return r}
function exactImpedancePacket(t,n,j){
  const tn=powComplex(t,n),den=sub(C(1),tn);
  return j===0?div(add(C(1),tn),den):div(scale(powComplex(t,j),2),den);
}
function exactAdmittancePacket(t,n,j){
  return exactImpedancePacket(scale(t,-1),n,j);
}
function poissonKernel(q,theta){return (1-q*q)/(1-2*q*Math.cos(theta)+q*q)}
function phaseLift(q,phi,inverse=false){
  const turns=Math.floor(phi/(2*Math.PI)+1e-12),reduced=phi-2*Math.PI*turns,w=expi(reduced);
  const value=inverse?div(add(w,C(q)),add(C(1),scale(w,q))):div(sub(w,C(q)),sub(C(1),scale(w,q)));
  const arg=Math.abs(reduced)<1e-11?0:(Math.atan2(value.im,value.re)+2*Math.PI)%(2*Math.PI);
  return turns*2*Math.PI+arg;
}
function smithQuantile(rho,mass){return phaseLift(rho*rho,4*Math.PI*mass,true)/2}
function smithCdf(rho,theta){return phaseLift(rho*rho,2*theta,false)/(4*Math.PI)}
function filterValue(g,n,j){let sum=C(0);for(let k=0;k<n;k++){const w=expi(2*Math.PI*k/n);const phase=expi(-2*Math.PI*j*k/n);sum=add(sum,mul(phase,evaluateF(mul(w,g))))}return scale(sum,1/n)}
function selectedCoefficients(n,j){return coefficients.map((a,m)=>m%n===((j%n)+n)%n?a:0)}
function appliedFilter(a,n,j){return a.map((v,m)=>m%n===((j%n)+n)%n?v:0)}
const fmt=(x,d=4)=>{if(!Number.isFinite(x))return x>0?'∞':x<0?'−∞':'—';let v=Math.abs(x)<0.5*Math.pow(10,-d)?0:x;return v.toFixed(d)};
const complexString=(z,d=4)=>!z?'∞':(!Number.isFinite(z.re)||!Number.isFinite(z.im)?'undefined':`${fmt(z.re,d)} ${z.im<0?'−':'+'} j${fmt(Math.abs(z.im),d)}`);
const coord=g=>({x:CX+R*g.re,y:CY-R*g.im});
function svgEl(name,attributes={},parent){const el=document.createElementNS(svgNS,name);Object.entries(attributes).forEach(([k,v])=>el.setAttribute(k,String(v)));if(parent)parent.appendChild(el);return el}
function line(x1,y1,x2,y2,stroke,width=1,dash='',parent){return svgEl('line',{x1,y1,x2,y2,stroke,'stroke-width':width,...(dash?{'stroke-dasharray':dash}:{})},parent)}
function circle(x,y,rad,stroke,fill='none',width=1,parent){return svgEl('circle',{cx:x,cy:y,r:rad,stroke,fill,'stroke-width':width},parent)}
function textAt(txt,x,y,className,parent,attrs={}){const t=svgEl('text',{x,y,class:className,...attrs},parent);t.textContent=txt;return t}
function pathFromGs(gs){return gs.map((g,i)=>{const p=coord(g);return (i?'L':'M')+p.x.toFixed(2)+' '+p.y.toFixed(2)}).join(' ')}
function makePath(gs,stroke,width,parent,dash='',opacity=1){return svgEl('path',{d:pathFromGs(gs),fill:'none',stroke,'stroke-width':width,opacity,'stroke-linecap':'round',...(dash?{'stroke-dasharray':dash}:{})},parent)}
function loadGamma(){if(states.special==='open')return C(1,0);return gammaFromZ(C(states.r/states.z0,states.x/states.z0))}
function rotationGamma(){const base=loadGamma();return mul(base,expi(-4*Math.PI*states.length))}
function cyclicGamma(){return mul(rotationGamma(),expi(2*Math.PI*states.k/states.N))}
function safeToZ(g){return abs(sub(C(1),g))<1e-12?null:zFromGamma(g)}
function presetToInputs(){const open=states.special==='open';$('resistance').disabled=open;$('reactance').disabled=open;$('resistance').value=open?'':String(states.r);$('reactance').value=open?'':String(states.x);$('z0').value=String(states.z0);$('length').value=String(states.length)}
function syncGammaEditor(force=false){
  if(gammaDraftDirty&&!force)return;
  const g=loadGamma();
  $('gamma-re').value=String(Number(g.re.toPrecision(11)));
  $('gamma-im').value=String(Number(g.im.toPrecision(11)));
  gammaDraftDirty=false;
}
function discardGammaDraft(){gammaDraftDirty=false;$('gamma-warning').textContent=''}
function setFromGamma(g,snapEndpoints=true){
  const m=abs(g);
  if(m>1)g=scale(g,1/m);
  const open=(g.re===1&&g.im===0)||(snapEndpoints&&abs(sub(g,C(1)))<.006);
  const short=(g.re===-1&&g.im===0)||(snapEndpoints&&abs(add(g,C(1)))<.006);
  if(open){states.special='open';$('preset').value='open'}
  else if(short){states.r=0;states.x=0;states.special=null;$('preset').value='short'}
  else{
    const z=zFromGamma(g);
    if(!Number.isFinite(z.re)||!Number.isFinite(z.im))return;
    states.r=Math.max(0,z.re*states.z0);states.x=z.im*states.z0;
    states.special=null;$('preset').value='custom';
  }
  presetToInputs();$('input-warning').textContent='';discardGammaDraft();render();
}
function buildBase(){const base=$('chart-base');base.replaceChildren();circle(CX,CY,R,'#466c62','#fafdf9',2,base);line(CX-R-17,CY,CX+R+17,CY,'#859f95',1.4,'',base);line(CX,CY-R-16,CX,CY+R+16,'#c9dad0',1,'4 6',base);circle(CX,CY,3.5,'none','#688e7d',0,base);textAt('Im Γ',CX+10,CY-R-23,'corner-label',base);textAt('Re Γ',CX+R+14,CY+5,'corner-label',base);textAt('short',CX-R-9,CY+22,'endpoint-label',base,{'text-anchor':'start'});textAt('open',CX+R-9,CY+22,'endpoint-label',base,{'text-anchor':'end'});textAt('matched',CX+7,CY+22,'endpoint-label',base)}
function drawCoordinateGrid(mode, grid, labels, showLabels){
  // Γ_y = (y−1)/(y+1) = −Γ_z for y = 1/z. Draw admittance loci in Γ_z coordinates.
  const adm=mode==='y', sign=adm?-1:1;
  const vals=[.2,.5,1,2,5,10], prefix=adm?'g':'r';
  if($('show-r').checked){for(const r of vals){
    const rad=R/(1+r), center=CX+sign*R*r/(1+r);
    circle(center,CY,rad,adm?'#d5c9ac':'#bfd5cc','none',r===1?1.55:1,grid);
    if(showLabels&&r<=2){const q=coord(C(sign*(r-1)/(r+1),0));
      textAt(prefix+'='+r,q.x+3,CY-(adm?-12:9),'grid-label',labels,{'text-anchor':'middle'});
    }
  }}
  if($('show-x').checked){for(const x of [.2,.5,1,2,5,10,-.2,-.5,-1,-2,-5,-10]){
    const samples=[];
    for(let i=0;i<=250;i++){const t=i/250,r=1400*t*t/(1+5*(1-t));samples.push(scale(gammaFromZ(C(r,x)),sign))}
    makePath(samples,adm?(x>0?'#c4ac91':'#cbbad3'):(x>0?'#bad0d9':'#d9c8df'),Math.abs(x)===1?1.45:1,grid);
    if(showLabels&&[.5,1,2,5,-.5,-1,-2,-5].includes(x)){
      const p=coord(scale(gammaFromZ(C(0,x)),sign));
      textAt((adm?'b':'x')+'='+x,p.x+(x>0?8:-8),p.y+(x>0?-8:15),'grid-label',labels,{'text-anchor':x>0?'start':'end'});
    }
  }}
}
function drawGrid(){
  const grid=$('chart-grid'), labels=$('chart-labels');grid.replaceChildren();labels.replaceChildren();
  const mode=$('grid-mode').value;
  $('grid-explain').textContent=mode==='z'?'Impedance: r/x curves in the Γz plane.':mode==='y'?'Admittance: g/b curves mapped into the same Γz plane (Γy = −Γz).':'Both r/x and g/b grids in the Γz plane; labels are hidden to reduce clutter.';
  if(mode==='both'){
    drawCoordinateGrid('z',grid,labels,false);
    drawCoordinateGrid('y',grid,labels,false);
  }else drawCoordinateGrid(mode,grid,labels,true);
}
function adaptivePoints(rho=states.rho,count=states.sampleCount){
  const key=`${rho}:${count}`;
  if(adaptiveCache.has(key))return adaptiveCache.get(key);
  const points=Array.from({length:count},(_,j)=>{
    const angle=smithQuantile(rho,(j+.5)/count);
    return {angle,g:scale(expi(angle),rho)};
  });
  if(adaptiveCache.size>32)adaptiveCache.clear();
  adaptiveCache.set(key,points);
  return points;
}
function adaptiveMetrics(samples){
  const sorted=samples.map(x=>x.angle).sort((a,b)=>a-b);
  const steps=sorted.map((a,i)=>((i+1<sorted.length?sorted[i+1]:sorted[0]+2*Math.PI)-a)*180/Math.PI);
  return {min:Math.min(...steps),max:Math.max(...steps)};
}
function renderAdaptiveMetrics(samples){
  const ratio=smithWeight(C(states.rho))/smithWeight(C(0,states.rho));
  const gaps=adaptiveMetrics(samples);
  $('ref-summary').textContent=states.rho.toFixed(2)+' / '+states.sampleCount+' points';
  $('ref-ratio').textContent=fmt(ratio,2)+'×';
  $('ref-min-step').textContent=fmt(gaps.min,3)+'°';
  $('ref-max-step').textContent=fmt(gaps.max,3)+'°';
  const n=states.sampleCount,theta=Array.from({length:n+1},(_,j)=>smithQuantile(states.rho,j/n));
  const mass=theta.slice(0,-1).map((a,j)=>Math.abs(smithCdf(states.rho,theta[j+1])-smithCdf(states.rho,a)-1/n));
  $('ref-mass-error').textContent=Math.max(0,...mass).toExponential(2);
  $('sample-radius-out').textContent=states.rho.toFixed(2);
}
function referenceGammaAt(z0){
  if(!referencePin)return null;
  if(referencePin.special==='open')return C(1,0);
  // Normalize physical A using CURRENT Z0; avoid overflow from R/Z0 near extremes.
  const m=Math.max(referencePin.r,Math.abs(referencePin.x),z0);
  return div(C((referencePin.r-z0)/m,referencePin.x/m),C((referencePin.r+z0)/m,referencePin.x/m));
}
function drawOverlay(){const layer=$('chart-overlay');layer.replaceChildren();$('legend-weight').hidden=!$('show-weight').checked;const g=loadGamma(),gin=rotationGamma(),grot=cyclicGamma();const mag=abs(g);if(mag>1e-8){circle(CX,CY,R*mag,'#8eb5ab','none',1.5,layer).setAttribute('stroke-dasharray','7 6')}
if($('show-rays').checked){for(let k=0;k<states.N;k++){const g1=scale(expi(2*Math.PI*k/states.N),.99),p=coord(g1);line(CX,CY,p.x,p.y,'#b9a9d1',.85,'4 8',layer)}}
if($('show-orbit').checked){for(let k=0;k<states.N;k++){const p=coord(mul(gin,expi(2*Math.PI*k/states.N)));circle(p.x,p.y,k===states.k?5.1:3.3,k===states.k?'#9d6510':'#c3a063',k===states.k?'#ddad52':'#e5d6ac',.9,layer)}}
const adaptive=adaptivePoints();renderAdaptiveMetrics(adaptive);
if($('show-weight').checked){for(const pt of adaptive){const p=coord(pt.g);circle(p.x,p.y,2.2,'none','#bd776e',0,layer)}}
if(states.length>.0001&&mag>1e-7){const samples=[];const count=Math.max(15,Math.ceil(states.length*420));for(let i=0;i<=count;i++){samples.push(mul(g,expi(-4*Math.PI*states.length*i/count)))}makePath(samples,'#356bb0',2.9,layer)}
const referenceGamma=referenceGammaAt(states.z0);
if(referenceGamma&&abs(sub(referenceGamma,g))>1e-7){
  const a=coord(referenceGamma),b=coord(g);
  line(a.x,a.y,b.x,b.y,'#956628',2.1,'6 5',layer).setAttribute('class','comparison-link');
}
const markers=$('chart-markers');markers.replaceChildren();const gp=coord(g);circle(gp.x,gp.y,10,'#fff','#087663',3,markers);circle(gp.x,gp.y,3,'none','#fff',0,markers);if(abs(sub(gin,g))>1e-5){const p=coord(gin);circle(p.x,p.y,8,'#fff','#356bb0',2.5,markers)}if(abs(sub(grot,gin))>1e-5){const p=coord(grot);circle(p.x,p.y,10,'#b27d24','none',3,markers);circle(p.x,p.y,4,'none','#b27d24',0,markers)}
if(referenceGamma){const p=coord(referenceGamma);circle(p.x,p.y,12,'#ac7e38','none',2.5,markers);
if(abs(sub(referenceGamma,g))<.025){textAt('A = B',p.x+14,p.y-13,'marker-label',markers)}
else{textAt('A',p.x+14,p.y-13,'marker-label',markers);textAt('B',gp.x+14,gp.y-13,'marker-label marker-label-b',markers)}}
$('legend-ref').hidden=!referencePin;
// Keep the boundary circle visually on top of clipped interior geometry.
circle(CX,CY,R,'#466c62','none',2.5,markers);
// Mark selected packet index only in text controls, not as a geometric wedge.
}
function renderValues(){const g=loadGamma(),gin=rotationGamma(),grot=cyclicGamma();const zin=safeToZ(gin),zrot=safeToZ(grot);const m=abs(g);const swr=m>=1-1e-12?'∞':fmt((1+m)/(1-m),3);const rl=m<1e-12?'∞':(m>=1-1e-12?'0.00 dB':fmt(-20*Math.log10(m),2)+' dB');const deg=((Math.atan2(g.im,g.re)*180/Math.PI+180)%360)-180;
$('v-load').textContent=states.special==='open'?'∞ Ω':`${fmt(states.r,2)} ${states.x<0?'−':'+'} j${fmt(Math.abs(states.x),2)} Ω`;
$('v-gamma').textContent=complexString(g);$('v-in').textContent=complexString(gin);
$('v-zin').textContent=zin?complexString(scale(zin,states.z0),2)+' Ω':'∞ Ω';
$('v-znorm').textContent=zin?complexString(zin,4):'∞';
const yin=safeToZ(scale(gin,-1));
$('v-yin').textContent=yin?complexString(yin,4):'∞';
$('v-mag').textContent=`${fmt(m,4)} ∠ ${fmt(deg,1)}°`;$('v-swr').textContent=`${swr} / ${rl}`;
$('v-rot').textContent=complexString(grot);$('v-mobius').textContent=zrot?complexString(zrot):'∞';
$('length-out').textContent=fmt(states.length,3)+' λ';$('phase-out').textContent=`${states.k} / ${states.N}`;
const p=packetValue(gin,states.N,states.j),a=packetValue(gin,2*states.N,states.j),b=packetValue(gin,2*states.N,states.j+states.N);const fft=filterValue(gin,states.N,states.j);let rec=C(0);for(let j=0;j<states.N;j++)rec=add(rec,packetValue(gin,states.N,j));
$('p-coarse').textContent=complexString(p,6);$('p-fine-a').textContent=complexString(a,6);$('p-fine-b').textContent=complexString(b,6);
renderPinnedComparison(g);
$('p-error').textContent=abs(sub(p,add(a,b))).toExponential(2);$('p-roots').textContent=abs(sub(p,fft)).toExponential(2);$('p-reconstruct').textContent=abs(sub(rec,evaluateF(gin))).toExponential(2);renderPackets(gin);renderCRT(gin)
}
function renderExactPackets(){
  const t=rotationGamma(),n=states.N,j=states.j;
  const note=$('exact-disk-note');
  if(abs(t)>=1-1e-11){
    for(const id of ['exact-z','exact-y','exact-reconstruction','exact-duality','exact-parseval','exact-energy'])$(id).textContent='interior only';
    note.textContent='|Γ| = 1 lies outside the convergent power-series domain. Individual packets can have artificial boundary poles even where the recombined impedance is finite. Choose a load with R > 0.';
    return;
  }
  const z=exactImpedancePacket(t,n,j),y=exactAdmittancePacket(t,n,j);
  $('exact-z').textContent=complexString(z,6);$('exact-y').textContent=complexString(y,6);
  let zsum=C(0),ysum=C(0),energy=0,pnorm=0,orbitnorm=0;
  const rho=abs(t),tn=rho*rho;
  for(let k=0;k<n;k++){
    const zp=exactImpedancePacket(t,n,k);
    zsum=add(zsum,zp);ysum=add(ysum,exactAdmittancePacket(t,n,k));
    pnorm+=abs(zp)**2;
    const zrot=zFromGamma(mul(t,expi(2*Math.PI*k/n)));
    orbitnorm+=abs(zrot)**2/n;
  }
  const dual=(n%2===0)?scale(z,j%2?-1:1):scale(sub(exactImpedancePacket(t,2*n,j),exactImpedancePacket(t,2*n,j+n)),j%2?-1:1);
  $('exact-reconstruction').textContent=abs(sub(zsum,zFromGamma(t))).toExponential(2);
  $('exact-duality').textContent=abs(sub(y,dual)).toExponential(2);
  $('exact-parseval').textContent=Math.abs(orbitnorm-pnorm).toExponential(2);
  energy=j===0?1+4*rho**(2*n)/(1-rho**(2*n)):4*rho**(2*j)/(1-rho**(2*n));
  $('exact-energy').textContent=energy.toPrecision(6);
  note.textContent=`${n%2?'Odd N: duality requires the 2N parity refinement.':'Even N: duality acts by the scalar sign (−1)^j.'} All displayed identities are subject to finite-precision evaluation; H² energy is a circle-integrated quantity, not the modulus of the packet at this point.`;
}
function render(){
  const key=$('grid-mode').value+':'+String(Number($('show-r').checked)) + ':' + String(Number($('show-x').checked));
  if(key!==lastGridKey){drawGrid();lastGridKey=key}
  drawOverlay();renderValues();renderExactPackets();syncGammaEditor();
}
function validInputs(){
  const z=Number($('z0').value),r=Number($('resistance').value),x=Number($('reactance').value);
  if(!$('z0').value.trim()||!Number.isFinite(z)||z<=0)return 'Z₀ must be a finite positive number.';
  if(states.special==='open'){states.z0=z;return ''}
  if(!$('resistance').value.trim()||!Number.isFinite(r)||r<0)return 'Resistance must be finite and nonnegative.';
  if(!$('reactance').value.trim()||!Number.isFinite(x))return 'Reactance must be finite.';
  if(!Number.isFinite(r/z)||!Number.isFinite(x/z)||Math.max(Math.abs(r/z),Math.abs(x/z))>1e12)
    return 'Normalized impedance is too large for this numerical display. For an ideal open, select Open circuit.';
  states.z0=z;states.r=r;states.x=x;return '';
}
function readInputs(){
  if(states.special==='open')return;
  const error=validInputs();$('input-warning').textContent=error?error+' Previous valid load is still shown.':'';
  if(!error){$('preset').value='custom';discardGammaDraft();render()}
}
$('preset').addEventListener('change',e=>{
  const before=loadHistorySnapshot();
  const q=e.target.value;
  const values={inductive:[25,25],capacitive:[25,-25],high:[100,50],short:[0,0]};
  if(q==='open'){states.special='open'}
  else if(q==='custom'){states.special=null} // Restore the last editable finite load.
  else if(q==='matched'){states.special=null;states.r=states.z0;states.x=0}
  else if(values[q]){states.special=null;[states.r,states.x]=values[q]}
  else return;
  presetToInputs();$('input-warning').textContent='';discardGammaDraft();render();recordLoadHistory(before);
});
$('z0').addEventListener('input',()=>{const error=validInputs();$('input-warning').textContent=error?error+' Previous valid load is still shown.':'';if(!error){if(states.special!=='open')$('preset').value='custom';discardGammaDraft();render()}});
for(const name of ['resistance','reactance'])$(''+name).addEventListener('input',readInputs);
$('length').addEventListener('input',()=>{states.length=Number($('length').value);render()});
$('order').addEventListener('change',()=>{states.N=Number($('order').value);states.k=Math.min(states.k,states.N-1);states.j=Math.min(states.j,states.N-1);syncPacketControls();render()});
$('phase').addEventListener('input',()=>{states.k=Number($('phase').value);render()});
$('packet').addEventListener('change',()=>{states.j=Number($('packet').value);render()});
for(const name of ['show-r','show-x','show-rays','show-orbit','show-weight'])$(name).addEventListener('change',()=>{syncSamplingButton();render()});
for(const id of ['gamma-re','gamma-im']){
  $(id).addEventListener('input',()=>{gammaDraftDirty=true;$('gamma-warning').textContent=''});
  $(id).addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('gamma-apply').click()}});
}
$('gamma-from-load').addEventListener('click',()=>{discardGammaDraft();syncGammaEditor(true);$('gamma-warning').textContent='Current load coordinates restored.'});
$('gamma-apply').addEventListener('click',()=>{
  const before=loadHistorySnapshot();
  const reText=$('gamma-re').value.trim(),imText=$('gamma-im').value.trim();
  const re=Number(reText),im=Number(imText);
  if(!reText||!imText||!Number.isFinite(re)||!Number.isFinite(im)){
    $('gamma-warning').textContent='Enter finite real and imaginary components of Γ.';return;
  }
  const g=C(re,im),m=abs(g);
  if(m>1){$('gamma-warning').textContent='Outside the passive Smith disk: |Γ| must not exceed 1.';return;}
  const distance=abs(sub(C(1),g));
  if(distance>0&&distance<1e-10){$('gamma-warning').textContent='Too close to Γ = 1 for stable impedance conversion. Select the Open preset for the ideal boundary.';return;}
  if(distance>0){const z=zFromGamma(g),scaled=states.z0*Math.max(Math.abs(z.re),Math.abs(z.im));
    if(!Number.isFinite(scaled)||Math.max(Math.abs(z.re),Math.abs(z.im))>1e12||!Number.isFinite(z.re)||!Number.isFinite(z.im)){
      $('gamma-warning').textContent='Converted load exceeds the supported numerical range.';return;
    }
  }
  setFromGamma(g,false);recordLoadHistory(before);
  $('gamma-warning').textContent='Passive Γ applied to the load.';
});
$('grid-mode').addEventListener('change',()=>{render();updateInspection(hoveredGamma)});
$('sample-radius').addEventListener('input',()=>{states.rho=Number($('sample-radius').value);render()});
$('sample-count').addEventListener('change',()=>{states.sampleCount=Number($('sample-count').value);render()});
function syncPacketControls(){const select=$('packet');select.replaceChildren();for(let j=0;j<states.N;j++){const o=document.createElement('option');o.value=String(j);o.textContent=`j = ${j}`;select.appendChild(o)}select.value=String(states.j);$('phase').max=String(states.N-1);$('phase').value=String(states.k)}
$('reset').addEventListener('click',()=>{setChartFocus(false);updateInspection(null);$('copy-status').textContent='';referencePin=null;$('grid-mode').value='z';$('clear-reference').disabled=true;$('swap-reference').disabled=true;Object.assign(states,{r:25,x:25,z0:50,special:null,length:0,N:8,k:0,j:0,rho:.94,sampleCount:96});$('sample-radius').value='.94';$('sample-count').value='96';$('preset').value='inductive';$('order').value='8';for(const id of ['show-r','show-x'])$(id).checked=true;for(const id of ['show-rays','show-orbit'])$(id).checked=false;$('show-weight').checked=false;syncSamplingButton();syncPacketControls();presetToInputs();$('input-warning').textContent='';discardGammaDraft();render();clearLoadHistory()});
function pointerToGamma(e){const svg=$('smith-chart'),point=svg.createSVGPoint();point.x=e.clientX;point.y=e.clientY;const inv=svg.getScreenCTM()?.inverse();if(!inv)return null;const p=point.matrixTransform(inv);const g=C((p.x-CX)/R,-(p.y-CY)/R);return abs(g)<=1.014?g:null}
// Inspection is read-only. Moving the cursor never changes the selected load.
let hoverFrame=0,hoveredGamma=null;
const defaultInspect='Hover or tap inside the disk to inspect Γ, z, or y.';
function updateInspection(g){
  hoveredGamma=g;
  if(!g){$('chart-inspect').textContent=defaultInspect;return}
  const mode=$('grid-mode').value;
  const components=[`Γ = ${complexString(g,3)}`];
  if(mode!=='y')components.push(`z = ${complexString(safeToZ(g),3)}`);
  if(mode!=='z')components.push(`y = ${complexString(safeToZ(scale(g,-1)),3)}`);
  $('chart-inspect').textContent=components.join('  ·  ');
}
$('smith-chart').addEventListener('pointermove',e=>{
  const g=pointerToGamma(e);
  if(hoverFrame)cancelAnimationFrame(hoverFrame);
  hoverFrame=requestAnimationFrame(()=>{hoverFrame=0;updateInspection(g)});
});
$('smith-chart').addEventListener('pointerleave',()=>{
  if(hoverFrame)cancelAnimationFrame(hoverFrame);
  hoverFrame=0;updateInspection(null);
});
function setChartFocus(enabled){
  $('smith-studio').classList.toggle('focus-chart',enabled);
  $('focus-chart').setAttribute('aria-pressed',String(enabled));
  $('focus-chart').textContent=enabled?'Return to workbench':'Expand chart';
}
$('focus-chart').addEventListener('click',()=>{
  const enable=!$('smith-studio').classList.contains('focus-chart');
  setChartFocus(enable);
  if(enable){$('chart-title').scrollIntoView({block:'start'});$('smith-chart').focus({preventScroll:true})}
});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'&&$('smith-studio').classList.contains('focus-chart')){
    setChartFocus(false);$('focus-chart').focus();
  }
});
$('copy-current').addEventListener('click',async()=>{
  const load=loadGamma(),line=rotationGamma(),zin=safeToZ(line);
  const result=['Smith chart · Komorebi',
    `Z0 = ${fmt(states.z0,2)} Ω`,
    `ZL = ${states.special==='open'?'ideal open':complexString(C(states.r,states.x),3)+' Ω'}`,
    `ΓL = ${complexString(load,6)}`,
    `Γin = ${complexString(line,6)}`,
    `Zin = ${zin?complexString(scale(zin,states.z0),3)+' Ω':'ideal open'}`].join('\n');
  try{await copyText(result);$('copy-status').textContent='Copied.'}
  catch(error){$('copy-status').textContent='Copy unavailable; use Save settings.'}
});
$('smith-chart').addEventListener('pointerdown',e=>{const g=pointerToGamma(e);if(!g)return;dragOrigin=loadHistorySnapshot();drag=true;$('smith-chart').setPointerCapture(e.pointerId);setFromGamma(g)});
$('smith-chart').addEventListener('pointermove',e=>{if(!drag)return;const g=pointerToGamma(e);if(g)setFromGamma(g)});
function endDrag(){if(!drag)return;drag=false;recordLoadHistory(dragOrigin);dragOrigin=null}
function cancelDrag(){if(!drag)return;drag=false;if(dragOrigin)applyLoadHistory(dragOrigin);dragOrigin=null}
$('smith-chart').addEventListener('pointerup',endDrag);$('smith-chart').addEventListener('pointercancel',cancelDrag);
$('smith-chart').addEventListener('keydown',e=>{
  const step=e.shiftKey?.05:.015;let dx=0,dy=0;
  switch(e.key){case'ArrowLeft':dx=-step;break;case'ArrowRight':dx=step;break;case'ArrowUp':dy=step;break;case'ArrowDown':dy=-step;break;default:return}
  e.preventDefault();const before=loadHistorySnapshot(),g=loadGamma(),q=C(g.re+dx,g.im+dy),n=abs(q);
  setFromGamma(n>1?scale(q,1/n):q);if(!e.repeat)recordLoadHistory(before);updateInspection(loadGamma());
});
$('export').addEventListener('click',()=>{const svg=$('smith-chart').cloneNode(true);svg.setAttribute('xmlns',svgNS);const embeddedStyle=svgEl('style');embeddedStyle.textContent='svg text{font-family:system-ui,sans-serif}svg .math-label{font-family:Georgia,serif;font-style:italic}svg .grid-label{font-weight:500;font-size:13px;fill:#6e847e}svg .corner-label{fill:#4c6862;font-size:16px}svg .endpoint-label{fill:#384b46;font-size:14px}';svg.prepend(embeddedStyle);const xml=new XMLSerializer().serializeToString(svg);const blob=new Blob([xml],{type:'image/svg+xml;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='komorebi-polyphase-smith-chart.svg';document.body.appendChild(a);a.click();a.remove();window.setTimeout(()=>URL.revokeObjectURL(url),1000)});
function evaluatePolynomial(a,g){
  let value=C(0);
  for(let m=a.length-1;m>=0;m--)value=add(mul(value,g),C(a[m]));
  return value;
}
function convolve(a,b){
  const out=Array(a.length+b.length-1).fill(0);
  for(let i=0;i<a.length;i++)if(a[i]!==0)
    for(let j=0;j<b.length;j++)if(b[j]!==0)out[i+j]+=a[i]*b[j];
  return out;
}
function smithWeight(g){
  return 1/(abs(sub(C(1),g))**2)+1/(abs(add(C(1),g))**2);
}
function maxResidual(values){return Math.max(0,...values)}
function renderPackets(t){
  const n=states.N,values=Array.from({length:n},(_,j)=>packetValue(t,n,j));
  const mags=values.map(abs),maximum=Math.max(...mags,Number.EPSILON);
  const target=$('packet-bars');target.replaceChildren();
  for(let j=0;j<n;j++){
    const bar=document.createElement('button');bar.type='button';bar.className='packet-bar'+(j===states.j?' is-active':'');bar.setAttribute('aria-pressed',String(j===states.j));
    bar.setAttribute('aria-label',`Residue class ${j}: magnitude ${mags[j].toPrecision(6)}${j===states.j?', selected':''}`);
    const head=document.createElement('div');head.className='packet-bar-head';
    const label=document.createElement('b');label.textContent='j = '+j;
    const flag=document.createElement('span');flag.textContent=j===states.j?'selected':'';
    head.append(label,flag);
    const track=document.createElement('div');track.className='packet-track';
    const fill=document.createElement('span');fill.className='packet-fill';
    fill.style.height=(mags[j]/maximum*38).toFixed(2)+'px';track.appendChild(fill);
    const amount=document.createElement('span');amount.className='packet-value';
    amount.textContent=mags[j].toPrecision(4);
    bar.append(head,track,amount);bar.addEventListener('click',()=>{states.j=j;syncPacketControls();render();target.querySelectorAll('.packet-bar')[j]?.focus()});target.appendChild(bar);
  }
  const a=states.j,b=(a+1)%n,c=(a+b)%n;
  const left=selectedCoefficients(n,a),right=selectedCoefficients(n,b);
  const product=convolve(left,right);
  const multiplied=mul(values[a],values[b]);
  $('nl-pair').textContent=`a = ${a}, b = ${b}`;
  $('nl-target').textContent=`c = ${c} (mod ${n})`;
  $('nl-error').textContent=abs(sub(multiplied,evaluatePolynomial(product,t))).toExponential(2);
  $('nl-leak').textContent=maxResidual(product.map((v,m)=>m%n===c?0:Math.abs(v))).toExponential(2);
  const witness=channelSquareError(n,C(.62,.18));
  $('nl-channel-error').textContent=witness.correct.toExponential(2);
  $('nl-naive-error').textContent=witness.naive.toExponential(2);
  $('nl-witness-description').textContent=witness.naive>1e-12
    ?'Nonzero counterexample to the diagonal-only shortcut. The full channel sum reconstructs the correct projected square.'
    :'The diagonal-only error is below 10⁻¹² for this order; the identity must still retain all residue pairs.';
}
function dyadicOdd(n){let d=1,o=n;while(o%2===0){d*=2;o/=2}return {d,o}}
function renderCRT(t){
  const {d,o}=dyadicOdd(states.N),n=states.N,j=states.j;
  const direct=selectedCoefficients(n,j),staged=appliedFilter(appliedFilter(coefficients,d,j%d),o,j%o);
  $('crt-factor').textContent=`${n} = ${d} × ${o}`;
  $('crt-index').textContent=`j mod ${d} = ${j%d}, j mod ${o} = ${j%o}`;
  $('crt-degrees').textContent=direct.flatMap((v,i)=>v!==0?[i]:[]).join(', ')||'none';
  $('crt-mismatch').textContent=String(direct.reduce((total,v,i)=>total+Number(v!==staged[i]),0));
  $('crt-error').textContent=abs(sub(evaluatePolynomial(direct,t),evaluatePolynomial(staged,t))).toExponential(2);
  $('crt-note').textContent=o===1?'Purely dyadic. Select N = 6 or 12 for both factors.':(d===1?'Purely odd cycle. Duality requires the 2N parity refinement.':'Nontrivial coprime dyadic–odd factors.');
}
function channelSquareError(n,t){
  const full=convolve(coefficients,coefficients);
  const c=0,projected=appliedFilter(full,n,c);
  const byProducts=Array.from({length:n},(_,j)=>mul(packetValue(t,n,j),packetValue(t,n,(n-j)%n)));
  let sum=C(0);for(const v of byProducts)sum=add(sum,v);
  const direct=evaluatePolynomial(projected,t),naive=mul(packetValue(t,n,0),packetValue(t,n,0));
  return {correct:abs(sub(sum,direct)),naive:abs(sub(naive,direct))};
}
function runChecks(){
  const z=C(.5,.5),g=gammaFromZ(z),t=C(.31,.24),checks=[];
  const addCheck=(label,residual,tolerance=1e-11,kind='floating')=>{
    checks.push({label,residual:Number.isFinite(residual)?Math.max(0,residual):Infinity,
      tolerance,kind,ok:Number.isFinite(residual)&&residual<=tolerance});
  };
  const compare=(label,a,b,tol=1e-11)=>addCheck(label,abs(sub(a,b)),tol);
  const countDifferent=(a,b)=>a.reduce((n,v,i)=>n+Number(v!==b[i]),0);
  const orders=[2,3,4,5,6,7,8,9,12,16],samples=[C(.1,0),t,C(-.28,.39),C(.82,-.09)];
  compare('Matched load maps to Γ = 0',gammaFromZ(C(1)),C(0),0);
  compare('Short circuit maps to Γ = −1',gammaFromZ(C(0)),C(-1),0);
  addCheck('Open-circuit limit approaches Γ = +1',abs(sub(gammaFromZ(C(1e9)),C(1))),1e-8);
  compare('Cayley inverse round trip',zFromGamma(g),z,1e-12);
  addCheck('Passive samples remain in |Γ| ≤ 1',maxResidual([0,.1,1,4,50].flatMap(r=>[-10,-.3,0,.3,10].map(x=>Math.max(0,abs(gammaFromZ(C(r,x)))-1)))),1e-12);
  addCheck('Passivity identity 1 − |Γ|² = 4r/|z+1|²',maxResidual([0,.1,.8,3].flatMap(r=>[-2,.4,5].map(x=>{
    const q=C(r,x),v=gammaFromZ(q),d=abs(add(q,C(1)));
    return Math.abs(1-abs(v)**2-4*r/d**2);
  }))),1e-12);
  addCheck('Constant-resistance circle equation',Math.abs((g.re-z.re/(1+z.re))**2+g.im**2-1/(1+z.re)**2),1e-12);
  addCheck('Constant-reactance circle equation',Math.abs((g.re-1)**2+(g.im-1/z.im)**2-(1/z.im)**2),1e-12);
  addCheck('Positive reactance plots in the upper half-disk',Math.max(0,-gammaFromZ(C(.4,1.2)).im),0);
  compare('N = 2 normalized impedance/admittance inversion',phaseMobius(z,2,1),div(C(1),z),1e-12);
  compare('Möbius pullback agrees with phase rotation',phaseMobius(z,8,3),zFromGamma(mul(g,expi(2*Math.PI*3/8))),1e-12);
  compare('Cyclic composition law T₂ ∘ T₃ = T₅',phaseMobius(phaseMobius(z,8,2),8,3),phaseMobius(z,8,5),1e-12);
  compare('Inverse cyclic action restores impedance',phaseMobius(phaseMobius(z,8,5),8,3),z,1e-12);
  addCheck('Cyclic actions preserve reflection magnitude',maxResidual(orders.flatMap(n=>samples.flatMap(q=>Array.from({length:n},(_,k)=>Math.abs(abs(mul(q,expi(2*Math.PI*k/n)))-abs(q)))))),1e-12);
  addCheck('Radial seeds map back to themselves',maxResidual([.1,.5,.9].flatMap(rho=>[0,.4,2.1,5].map(theta=>{
    const q=scale(expi(theta),rho);return abs(sub(gammaFromZ(zFromGamma(q)),q));
  }))),1e-12);
  addCheck('Two-child refinement for several N and j',maxResidual(orders.flatMap(n=>Array.from({length:n},(_,j)=>abs(sub(packetValue(t,n,j),add(packetValue(t,2*n,j),packetValue(t,2*n,j+n))))))),1e-12);
  addCheck('Three-child refinement N = 4 to M = 12',maxResidual(Array.from({length:4},(_,j)=>abs(sub(packetValue(t,4,j),add(add(packetValue(t,12,j),packetValue(t,12,j+4)),packetValue(t,12,j+8)))))),1e-12);
  addCheck('Full packet reconstruction for several N',maxResidual(orders.map(n=>{
    let total=C(0);for(let j=0;j<n;j++)total=add(total,packetValue(t,n,j));
    return abs(sub(total,evaluateF(t)));
  })),1e-12);
  const p=selectedCoefficients(8,3);
  addCheck('Projector idempotence on coefficients',countDifferent(appliedFilter(p,8,3),p),0,'count');
  addCheck('Different coefficient projectors are orthogonal',appliedFilter(p,8,4).filter(v=>v!==0).length,0,'count');
  addCheck('Dyadic–odd CRT factorization (12 and 24)',[12,24].reduce((fails,n)=>{
    const odd=3,dyadic=n/odd;
    for(let j=0;j<n;j++)fails+=countDifferent(selectedCoefficients(n,j),appliedFilter(appliedFilter(coefficients,dyadic,j%dyadic),odd,j%odd));
    return fails;
  },0),0,'count');
  addCheck('Roots-of-unity filter equals coefficient selection',maxResidual(orders.flatMap(n=>Array.from({length:n},(_,j)=>abs(sub(filterValue(t,n,j),packetValue(t,n,j)))))),1e-11);
  addCheck('Phase covariance of residue packets',maxResidual(orders.flatMap(n=>Array.from({length:n},(_,j)=>{
    const w=expi(2*Math.PI/n);
    return abs(sub(packetValue(mul(w,t),n,j),mul(expi(2*Math.PI*j/n),packetValue(t,n,j))));
  }))),1e-11);
  const a=selectedCoefficients(8,2),b=selectedCoefficients(8,5),product=convolve(a,b);
  addCheck('Nonlinear product has correct coefficient residue',product.reduce((fail,v,i)=>fail+Number(i%8!==7&&v!==0),0),0,'count');
  addCheck('Nonlinear product equals independently evaluated factors',abs(sub(evaluatePolynomial(product,t),mul(packetValue(t,8,2),packetValue(t,8,5)))),1e-11);
  addCheck('Wrong-residue nonlinear projection vanishes',appliedFilter(product,8,6).filter(v=>v!==0).length,0,'count');
  compare('Half-wavelength line preserves Γ',mul(t,expi(-4*Math.PI*.5)),t,1e-12);
  compare('Quarter-wavelength line reverses Γ',mul(t,expi(-4*Math.PI*.25)),scale(t,-1),1e-12);
  const swr=(1+abs(t))/(1-abs(t));
  addCheck('VSWR invariant under lossless phase',maxResidual(Array.from({length:16},(_,k)=>{
    const q=mul(t,expi(-4*Math.PI*k/32));return Math.abs((1+abs(q))/(1-abs(q))-swr);
  })),1e-11);
  addCheck('Reflected power |Γ|² invariant under lossless phase',maxResidual(Array.from({length:16},(_,k)=>{
    const q=mul(t,expi(-4*Math.PI*k/32));return Math.abs(abs(q)**2-abs(t)**2);
  })),1e-12);
  addCheck('Smith sensitivity is symmetric at ±Γ',maxResidual(samples.map(q=>Math.abs(smithWeight(q)-smithWeight(scale(q,-1))))),1e-11);
  const h=1e-6,q=C(.21,.17),dq=C(h),qplus=add(q,dq),qminus=sub(q,dq);
  const numericalZ=scale(sub(zFromGamma(qplus),zFromGamma(qminus)),1/(2*h));
  const expectedZ=div(C(2),mul(sub(C(1),q),sub(C(1),q)));
  compare('Cayley derivative agrees with central difference',numericalZ,expectedZ,2e-9);
  const admittance=u=>div(sub(C(1),u),add(C(1),u));
  const numericalY=scale(sub(admittance(qplus),admittance(qminus)),1/(2*h));
  const expectedY=div(C(-2),mul(add(C(1),q),add(C(1),q)));
  compare('Admittance derivative agrees with central difference',numericalY,expectedY,2e-9);
  addCheck('Sensitivity favors neighborhoods of open and short',Math.max(0,smithWeight(C(0,.94))-smithWeight(C(.94,0))),0);
  addCheck('Negative resistance lies strictly outside passive disk (control)',Math.max(0,1+1e-6-abs(gammaFromZ(C(-.2,.4)))),0);
  addCheck('Coprime CRT coefficient intersection at N = 6 and 12',
    [6,12].reduce((fails,n)=>{const {d,o}=dyadicOdd(n);
      for(let j=0;j<n;j++)fails+=countDifferent(selectedCoefficients(n,j),appliedFilter(appliedFilter(coefficients,d,j%d),o,j%o));
      return fails;},0),0,'count');
  addCheck('Nonlinear full channel sum reconstructs projected square',maxResidual(orders.map(n=>channelSquareError(n,C(.62,.18)).correct)),1e-11);
  addCheck('Naive diagonal-only product has a counterexample',Math.max(0,1e-5-channelSquareError(8,C(.62,.18)).naive),0);
  const ell=.1234,beta=2*Math.PI*ell,tan=Math.tan(beta),zline=zFromGamma(mul(gammaFromZ(z),expi(-2*beta)));
  const independentLine=div(add(z,C(0,tan)),add(C(1),mul(z,C(0,tan))));
  compare('Lossless line equals tangent impedance formula',zline,independentLine,1e-12);
  addCheck('Adaptive samples have positive, nonduplicate gaps',maxResidual([.70,.84,.94,.97].flatMap(rho=>[32,64,96,128].map(count=>{
    const points=adaptivePoints(rho,count);
    return Math.max(0,1e-5-adaptiveMetrics(points).min*Math.PI/180);
  }))),0);
  addCheck('Weighted sample pairs are half-turn symmetric',maxResidual([.70,.84,.94,.97].flatMap(rho=>[32,64,96,128].map(count=>{
    const p=adaptivePoints(rho,count);
    return maxResidual(p.slice(0,count/2).map((a,j)=>Math.abs(p[j+count/2].angle-a.angle-Math.PI)));
  }))),2*Math.PI/8192+1e-12);
  addCheck('Adaptive sampling allocates unequal angular gaps',maxResidual([.70,.84,.94,.97].map(rho=>{
    const m=adaptiveMetrics(adaptivePoints(rho,96));
    return Math.max(0,m.min*1.1-m.max);
  })),0);
  addCheck('Adaptive weight greater near open than imaginary axis',
    Math.max(0,smithWeight(C(0,.94))-smithWeight(C(.94))),0);
  compare('Half-turn sends open reflection to short',mul(C(1),expi(Math.PI)),C(-1),1e-15);
  // Exact impedance/admittance packets: finite orbits, duality, positivity, and energy.
  addCheck('Exact impedance packets equal roots-of-unity averaging',maxResidual(orders.flatMap(n=>Array.from({length:n},(_,j)=>abs(sub(exactImpedancePacket(t,n,j),
    scale(Array.from({length:n},(_,k)=>mul(expi(-2*Math.PI*j*k/n),zFromGamma(mul(t,expi(2*Math.PI*k/n))))).reduce(add,C(0)),1/n)))))),2e-11);
  addCheck('Exact admittance packets equal roots-of-unity averaging',maxResidual(orders.flatMap(n=>Array.from({length:n},(_,j)=>abs(sub(exactAdmittancePacket(t,n,j),
    scale(Array.from({length:n},(_,k)=>mul(expi(-2*Math.PI*j*k/n),div(sub(C(1),mul(t,expi(2*Math.PI*k/n))),add(C(1),mul(t,expi(2*Math.PI*k/n)))))).reduce(add,C(0)),1/n)))))),2e-11);
  addCheck('Exact z packets reconstruct z for multiple N',maxResidual(orders.map(n=>{
    let total=C(0);for(let j=0;j<n;j++)total=add(total,exactImpedancePacket(t,n,j));
    return abs(sub(total,zFromGamma(t)));
  })),2e-11);
  addCheck('Exact y packets reconstruct y for multiple N',maxResidual(orders.map(n=>{
    let total=C(0);for(let j=0;j<n;j++)total=add(total,exactAdmittancePacket(t,n,j));
    return abs(sub(total,div(sub(C(1),t),add(C(1),t))));
  })),2e-11);
  addCheck('Even N: admittance packet = parity sign × impedance packet',maxResidual([2,4,6,8,12,16].flatMap(n=>Array.from({length:n},(_,j)=>
    abs(sub(exactAdmittancePacket(t,n,j),scale(exactImpedancePacket(t,n,j),j%2?-1:1)))))),2e-11);
  addCheck('Odd N: duality has 2N-parity refinement',maxResidual([3,5,7].flatMap(n=>Array.from({length:n},(_,j)=>
    abs(sub(exactAdmittancePacket(t,n,j),scale(sub(exactImpedancePacket(t,2*n,j),exactImpedancePacket(t,2*n,j+n)),j%2?-1:1)))))),2e-11);
  addCheck('Odd N scalar sign shortcut fails (counterexample)',Math.max(0,1e-3-abs(sub(exactAdmittancePacket(t,3,0),exactImpedancePacket(t,3,0)))),0);
  addCheck('Finite phase orbit Parseval for actual impedance',maxResidual(orders.map(n=>{
    const left=Array.from({length:n},(_,k)=>abs(zFromGamma(mul(t,expi(2*Math.PI*k/n))))**2).reduce((a,b)=>a+b,0)/n;
    const right=Array.from({length:n},(_,j)=>abs(exactImpedancePacket(t,n,j))**2).reduce((a,b)=>a+b,0);
    return Math.abs(left-right);
  })),1e-11);
  addCheck('Angular H² packet energies sum to exact total',maxResidual([.2,.5,.9].flatMap(rho=>orders.map(n=>{
    const sum=1+4*rho**(2*n)/(1-rho**(2*n))+Array.from({length:n-1},(_,k)=>4*rho**(2*(k+1))/(1-rho**(2*n))).reduce((a,b)=>a+b,0);
    return Math.abs(sum-(1+4*rho**2/(1-rho**2)));
  }))),1e-11);
  addCheck('Zero residue impedance packet has positive real part (finite samples)',maxResidual(orders.flatMap(n=>Array.from({length:120},(_,k)=>{
    const q=scale(expi(2*Math.PI*k/120),.92),value=exactImpedancePacket(q,n,0);return Math.max(0,-value.re);
  }))),0);
  addCheck('Nonzero impedance packets can have negative real part',Math.max(0,1e-4+Math.min(...Array.from({length:120},(_,k)=>exactImpedancePacket(scale(expi(2*Math.PI*k/120),.92),8,1).re))),0);
  addCheck('Poisson identity for symmetric sensitivity',maxResidual([.35,.75,.9,.97].flatMap(rho=>Array.from({length:64},(_,k)=>{
    const theta=2*Math.PI*k/64;return Math.abs(smithWeight(scale(expi(theta),rho))-2*poissonKernel(rho*rho,2*theta)/(1-rho*rho));
  }))),2e-10);
  addCheck('Analytic Poisson quantiles invert the cumulative measure',maxResidual([.35,.75,.9,.97].flatMap(rho=>Array.from({length:129},(_,k)=>{
    const u=k/128;return Math.abs(smithCdf(rho,smithQuantile(rho,u))-u);
  }))),2e-11);
  addCheck('Poisson quantile intervals partition exactly equal mass',maxResidual([.35,.75,.9,.97].flatMap(rho=>[32,64,96,128].flatMap(n=>Array.from({length:n},(_,k)=>
    Math.abs(smithCdf(rho,smithQuantile(rho,(k+1)/n))-smithCdf(rho,smithQuantile(rho,k/n))-1/n)
  )))),2e-11);
  addCheck('Spurious packet pole residues cancel away from Γ = 1',maxResidual([2,3,4,8,12].flatMap(n=>Array.from({length:n-1},(_,k)=>{
    const root=expi(2*Math.PI*(k+1)/n);let sum=C(0);
    for(let j=0;j<n;j++)sum=add(sum,scale(powComplex(root,j+1),-2/n));
    return abs(sum);
  }))),1e-12);
  addCheck('Admittance chart coordinate uses Γ_y = −Γ_z',maxResidual(samples.map(q=>{
    const zi=zFromGamma(q),y=div(C(1),zi);
    return abs(sub(gammaFromZ(y),scale(q,-1)));
  })),1e-12);
  addCheck('Admittance grid conductance locus is mirrored resistance circle',maxResidual([.2,.5,1,2,5].map(r=>{
    const g=scale(gammaFromZ(C(r,.65)),-1);
    return Math.abs((g.re+r/(1+r))**2+g.im**2-1/(1+r)**2);
  })),1e-12);
  lastTestResults=checks;
  const passed=checks.filter(c=>c.ok).length,failures=checks.length-passed;
  const floating=checks.filter(c=>c.kind==='floating'),largest=maxResidual(floating.map(c=>c.residual));
  const status=$('test-status');
  status.textContent=`${passed} / ${checks.length} fixed-fixture checks passed · largest floating residual ${largest.toExponential(2)} · ${failures?failures+' failed · ':''}not formal proofs`;
  status.style.color=failures?'var(--red)':'var(--green)';
  $('test-detail-summary').textContent=`${checks.length} individual numerical checks (${failures} failed)`;
  const out=$('test-results');out.replaceChildren();
  checks.forEach((c,i)=>{
    const item=document.createElement('div');item.className='test-result '+(c.ok?'pass':'fail');
    const sign=document.createElement('span');sign.className='symbol';sign.textContent=c.ok?'✓':'✕';
    const body=document.createElement('div');body.textContent=`${i+1}. ${c.label}`;
    const small=document.createElement('small');
    small.textContent=c.kind==='count'?`Coefficient mismatches: ${c.residual} · expected: 0`:`Residual: ${c.residual.toExponential(2)} · tolerance: ${c.tolerance.toExponential(1)}`;
    body.appendChild(small);item.append(sign,body);out.appendChild(item);
  });
  return checks;
}
function downloadReport(){
  if(!lastTestResults.length)runChecks();
  const report={title:'Projector-resolved polyphase Smith chart',status:'finite numerical checks only',
    generated_at:new Date().toISOString(),fixtures:{impedance:'z(t) = (1+t)/(1-t)',admittance:'y(t) = (1-t)/(1+t)',sampling:'closed-form Poisson inverse CDF',coefficients:'separate finite fixture a_m = 1/(m+1), 0 <= m <= 31',orders:[2,3,4,5,6,7,8,9,12,16],sample_points:['0.1+0i','0.31+0.24i','-0.28+0.39i','0.82-0.09i'],line_length:0.1234,weighted_radii:[0.70,0.84,0.94,0.97]},view_state:{cycle_order:states.N,packet_index:states.j,rotation_index:states.k,normalized_line_length:states.length,sample_radius:states.rho,sample_count:states.sampleCount},
    summary:{passed:lastTestResults.filter(c=>c.ok).length,total:lastTestResults.length},checks:lastTestResults};
  const blob=new Blob([JSON.stringify(report,null,2)+'\n'],{type:'application/json'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='smith-polyphase-checks.json';document.body.appendChild(a);a.click();a.remove();window.setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('download-results').addEventListener('click',downloadReport);
$('run-tests').addEventListener('click',runChecks);
$('copy-results').addEventListener('click',async()=>{if(!lastTestResults.length)runChecks();const textReport=['Komorebi Polyphase Smith Chart / browser numerical checks',...lastTestResults.map((c,i)=>`${i+1}. ${c.ok?'PASS':'FAIL'} ${c.label} [${c.kind==='count'?'coefficient mismatches '+c.residual:'residual '+c.residual.toExponential(4)+' / tolerance '+c.tolerance.toExponential(2)}]`),'These are finite browser checks, not formal proof.'].join('\n');try{if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(textReport);else{const a=document.createElement('textarea');a.value=textReport;a.style.position='fixed';a.style.top='-1000px';document.body.appendChild(a);a.select();const copied=document.execCommand('copy');a.remove();if(!copied)throw new Error('Browser denied clipboard access')}$('copy-results').textContent='Report copied';setTimeout(()=>$('copy-results').textContent='Copy test report',1600)}catch(e){$('test-status').textContent='Clipboard failed: '+String(e.message||e)}});
// Guided research views: all examples retain the same live load and packet state.
let activeView='exact';
function switchView(next,focus=false){
  if(!['exact','finite','structure','sampling','verify'].includes(next))return;
  activeView=next;
  $('smith-studio').querySelectorAll('[data-view]').forEach(t=>{
    const selected=t.dataset.view===next;
    t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;
  });
  for(const name of ['exact','finite','structure','sampling','verify'])$('panel-'+name).hidden=name!==next;
  if(focus)$('tab-'+next).focus();
}
for(const t of $('smith-studio').querySelectorAll('[data-view]')){
  t.addEventListener('click',()=>switchView(t.dataset.view));
  t.addEventListener('keydown',e=>{
    if(!['ArrowRight','ArrowLeft','Home','End'].includes(e.key))return;
    e.preventDefault();const views=['exact','finite','structure','sampling','verify'];
    let index=views.indexOf(t.dataset.view);
    if(e.key==='Home')index=0;else if(e.key==='End')index=views.length-1;
    else index=(index+(e.key==='ArrowRight'?1:-1)+views.length)%views.length;
    switchView(views[index],true);
  });
}
function syncSamplingButton(){
  $('show-sampling').textContent=$('show-weight').checked?'Hide weighted samples':'Show weighted samples on chart';
}
$('show-sampling').addEventListener('click',()=>{ $('show-weight').checked=!$('show-weight').checked;syncSamplingButton();render(); });
// Reference A is an immutable physical load snapshot. B is the current selection.
function loadHistorySnapshot(){
  const pin=referencePin?{r:referencePin.r,x:referencePin.x,z0:referencePin.z0,special:referencePin.special}:null;
  return {r:states.r,x:states.x,z0:states.z0,special:states.special,pin};
}
function loadHistoryEqual(a,b){return JSON.stringify(a)===JSON.stringify(b)}
function syncLoadHistory(){
  $('undo-load').disabled=loadUndoStack.length===0;
  $('redo-load').disabled=loadRedoStack.length===0;
}
function recordLoadHistory(before){
  if(!before||loadHistoryEqual(before,loadHistorySnapshot()))return;
  loadUndoStack.push(before);
  if(loadUndoStack.length>MAX_LOAD_HISTORY)loadUndoStack.shift();
  loadRedoStack.length=0;
  syncLoadHistory();
  $('history-status').textContent='Load history available. Line and projector settings are unchanged by undo.';
}
function applyLoadHistory(snapshot){
  states.r=snapshot.r;states.x=snapshot.x;states.z0=snapshot.z0;states.special=snapshot.special;
  referencePin=snapshot.pin?{...snapshot.pin}:null;
  $('preset').value=states.special==='open'?'open':'custom';
  presetToInputs();discardGammaDraft();$('input-warning').textContent='';
  activeFieldOrigin=null;dragOrigin=null;drag=false;
  render();syncLoadHistory();
}
function undoLoad(){
  if(!loadUndoStack.length)return;
  const previous=loadUndoStack.pop();loadRedoStack.push(loadHistorySnapshot());
  applyLoadHistory(previous);$('history-status').textContent='Load or pinned reference restored.';
}
function redoLoad(){
  if(!loadRedoStack.length)return;
  const next=loadRedoStack.pop();loadUndoStack.push(loadHistorySnapshot());
  applyLoadHistory(next);$('history-status').textContent='Load or pinned reference reapplied.';
}
function clearLoadHistory(){
  loadUndoStack.length=0;loadRedoStack.length=0;activeFieldOrigin=null;dragOrigin=null;
  syncLoadHistory();$('history-status').textContent='History cleared. The current load is the new starting point.';
}
$('undo-load').addEventListener('click',undoLoad);
$('redo-load').addEventListener('click',redoLoad);
// Native text editing keeps Ctrl/Cmd+Z inside input fields.
document.addEventListener('keydown',event=>{
  if(!(event.ctrlKey||event.metaKey)||event.altKey)return;
  if(event.target.closest?.('input,textarea,select,[contenteditable="true"]'))return;
  const key=event.key.toLowerCase();
  if(key==='z'){
    if(event.shiftKey){if(loadRedoStack.length){event.preventDefault();redoLoad()}}
    else if(loadUndoStack.length){event.preventDefault();undoLoad()}
  }else if(key==='y'&&loadRedoStack.length){event.preventDefault();redoLoad()}
});
// Commit one history entry per completed physical-input edit, not per keystroke.
for(const id of ['z0','resistance','reactance']){
  const input=$(id);
  input.addEventListener('focus',()=>{activeFieldOrigin=loadHistorySnapshot()});
  input.addEventListener('change',()=>{recordLoadHistory(activeFieldOrigin);activeFieldOrigin=null});
}
function currentLoadSnapshot(){return {gamma:loadGamma(),r:states.r,x:states.x,z0:states.z0,special:states.special}}
function renderPinnedComparison(current){
  $('clear-reference').disabled=!referencePin;
  $('swap-reference').disabled=!referencePin;
  $('comparison-note').hidden=!referencePin;
  $('pin-value').textContent=referencePin?(referencePin.special==='open'?'Ideal open':
    complexString(C(referencePin.r,referencePin.x),2)+' Ω'):'No reference pinned';
  const commonReference=referenceGammaAt(states.z0);
  $('pin-delta').textContent=referencePin?fmt(abs(sub(current,commonReference)),6):'—';
  $('pin-z-delta').textContent=!referencePin?'—':
    (referencePin.special==='open'&&states.special==='open'?'0 Ω':
    (referencePin.special==='open'||states.special==='open'?'unbounded':
    fmt(abs(sub(C(states.r,states.x),C(referencePin.r,referencePin.x))),4)+' Ω'));
}
$('pin-reference').addEventListener('click',()=>{const before=loadHistorySnapshot();referencePin=currentLoadSnapshot();render();recordLoadHistory(before)});
$('clear-reference').addEventListener('click',()=>{const before=loadHistorySnapshot();referencePin=null;render();recordLoadHistory(before)});
$('swap-reference').addEventListener('click',()=>{
  if(!referencePin)return;
  const before=loadHistorySnapshot();
  const priorA=referencePin,priorB=currentLoadSnapshot();
  referencePin=priorB;
  states.r=priorA.r;states.x=priorA.x;states.special=priorA.special;
  $('preset').value=states.special==='open'?'open':'custom';
  presetToInputs();$('input-warning').textContent='';discardGammaDraft();render();recordLoadHistory(before);
});
for(const b of $('smith-studio').querySelectorAll('[data-preset]'))b.addEventListener('click',()=>{
  $('preset').value=b.dataset.preset;$('preset').dispatchEvent(new Event('change',{bubbles:true}));
});
for(const b of $('smith-studio').querySelectorAll('[data-length]'))b.addEventListener('click',()=>{
  const delta=Number(b.dataset.length);states.length=delta===0?0:Math.max(0,Math.min(.5,states.length+delta));
  $('length').value=String(states.length);render();
});
// A portable state file is intentionally limited to validated numeric controls.
function serializeSession(){
  return {kind:'komorebi-smith-session',schema:1,load:{r:states.r,x:states.x,z0:states.z0,special:states.special},
    analysis:{length:states.length,N:states.N,k:states.k,j:states.j,rho:states.rho,sampleCount:states.sampleCount},
    view:{grid:$('grid-mode').value,r:$('show-r').checked,x:$('show-x').checked,rays:$('show-rays').checked,orbit:$('show-orbit').checked,weight:$('show-weight').checked,tab:activeView},
    pin:referencePin?{r:referencePin.r,x:referencePin.x,z0:referencePin.z0,special:referencePin.special}:null};
}
function validateSession(raw){
  if(!raw||raw.kind!=='komorebi-smith-session'||raw.schema!==1)throw new Error('Not a supported Smith chart settings file.');
  const l=raw.load||{},a=raw.analysis||{},v=raw.view||{};
  function number(z,min,max,name){if(typeof z!=='number'||!Number.isFinite(z)||z<min||z>max)throw new Error('Invalid '+name);return z}
  function integer(z,allowed,name){if(!Number.isInteger(z)||!allowed.includes(z))throw new Error('Invalid '+name);return z}
  function boolean(z,name){if(typeof z!=='boolean')throw new Error('Invalid '+name);return z}
  const candidate={r:number(l.r,0,1e12,'R'),x:number(l.x,-1e12,1e12,'X'),z0:number(l.z0,Number.MIN_VALUE,1e12,'Z0'),
    special:l.special===null||l.special==='open'?l.special:(()=>{throw new Error('Invalid ideal load')})(),
    length:number(a.length,0,.5,'line length'),N:integer(a.N,[2,3,4,5,6,7,8,9,12,16],'cycle order'),
    k:integer(a.k,Array.from({length:a.N},(_,i)=>i),'rotation'),j:integer(a.j,Array.from({length:a.N},(_,i)=>i),'packet'),
    rho:number(a.rho,.7,.97,'sampling radius'),sampleCount:integer(a.sampleCount,[32,64,96,128],'sampling count')};
  if(Math.max(Math.abs(candidate.r/candidate.z0),Math.abs(candidate.x/candidate.z0))>1e12)throw new Error('Normalized impedance out of range.');
  if(!['z','y','both'].includes(v.grid))throw new Error('Unknown grid');
  if(!['exact','finite','structure','sampling','verify'].includes(v.tab))throw new Error('Unknown research view');
  for(const key of ['r','x','rays','orbit','weight'])boolean(v[key],key);
  let pin=null;
  if(raw.pin!==null){const p=raw.pin||{};
    pin={r:number(p.r,0,1e12,'pin R'),x:number(p.x,-1e12,1e12,'pin X'),z0:number(p.z0,Number.MIN_VALUE,1e12,'pin Z0'),special:p.special};
    if(![null,'open'].includes(pin.special))throw new Error('Invalid pinned load');
    if(Math.max(Math.abs(pin.r/pin.z0),Math.abs(pin.x/pin.z0))>1e12)throw new Error('Invalid pinned normalized impedance.');
  }
  return {candidate,view:v,pin};
}
function restoreSession(data){
  const {candidate,view,pin}=validateSession(data);
  setChartFocus(false);updateInspection(null);$('copy-status').textContent='';
  Object.assign(states,candidate);
  $('preset').value=states.special==='open'?'open':'custom';
  $('order').value=String(states.N);syncPacketControls();$('packet').value=String(states.j);
  $('grid-mode').value=view.grid;
  for(const [id,key] of [['show-r','r'],['show-x','x'],['show-rays','rays'],['show-orbit','orbit'],['show-weight','weight']])$(id).checked=view[key];
  $('sample-radius').value=String(states.rho);$('sample-count').value=String(states.sampleCount);
  referencePin=pin?{...pin}:null;
  presetToInputs();$('phase').value=String(states.k);$('input-warning').textContent='';discardGammaDraft();
  syncSamplingButton();switchView(view.tab);render();clearLoadHistory();
}
function downloadLocalFile(name,data,type){
  const b=new Blob([data],{type}),url=URL.createObjectURL(b),a=document.createElement('a');
  a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('download-session').addEventListener('click',()=>{
  downloadLocalFile('smith-chart-settings.json',JSON.stringify(serializeSession(),null,2)+'\n','application/json');
  $('session-status').textContent='Settings JSON downloaded.';
});
$('import-session').addEventListener('change',async e=>{
  const file=e.target.files?.[0];if(!file)return;
  try{if(file.size>32000)throw new Error('Settings file too large');
    restoreSession(JSON.parse(await file.text()));$('session-status').textContent='Settings restored.';
  }catch(error){$('session-status').textContent='Settings not imported: '+String(error.message||error)}
  finally{e.target.value=''}
});
function shareUrl(){
  if(location.protocol==='about:')throw new Error('A URL is available when the HTML is opened as a file or hosted on a site. Use Download settings JSON here.');
  const url=new URL(location.href);url.searchParams.set('smith',btoa(encodeURIComponent(JSON.stringify(serializeSession()))));
  return url.href;
}
async function copyText(value){
  if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(value);return}
  const input=document.createElement('textarea');input.value=value;input.style.position='fixed';input.style.top='-9999px';document.body.appendChild(input);input.select();
  const ok=document.execCommand('copy');input.remove();if(!ok)throw new Error('Clipboard permission denied; download a settings file instead.');
}
$('copy-session-link').addEventListener('click',async()=>{
  try{await copyText(shareUrl());$('session-status').textContent='Settings link copied.'}
  catch(e){$('session-status').textContent=String(e.message||e)}
});
function restoreFromQuery(){
  const value=new URL(location.href).searchParams.get('smith');if(!value)return;
  if(value.length>12000){$('session-status').textContent='Invalid settings link: payload exceeds limit.';return;}
  try{const raw=JSON.parse(decodeURIComponent(atob(value)));
    restoreSession(raw);$('session-status').textContent='Settings restored from link.';
  }catch(e){$('session-status').textContent='The settings link was invalid: '+String(e.message||e)}
}
$('results-detail').open=false;
$('smith-studio').classList.add('js-ready');switchView('exact');
buildBase();syncPacketControls();syncSamplingButton();restoreFromQuery();render();syncLoadHistory();runChecks();
})();
