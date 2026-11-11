'use strict';

// Extract the unchanged, pure-math prefix of the pinned browser script. The
// harness adds exports but does not execute the page's DOM or event handlers.
const fs = require('node:fs');
const crypto = require('node:crypto');
const vm = require('node:vm');
const source = fs.readFileSync('computations/inputs/smith-chart-final-lf.js', 'utf8');
const expectedHash = 'e63ed0d751da83de7b2828aa496855cd6d645d36605607b9d84be1f644e51081';
const hash = crypto.createHash('sha256').update(source, 'utf8').digest('hex');
if (hash !== expectedHash) throw new Error('The browser source does not match the pinned Git object');
const marker = 'const fmt=';
const cut = source.indexOf(marker);
if (cut < 0 || source.indexOf(marker, cut + 1) !== -1) throw new Error('Unexpected source structure');
const sandbox = {};
vm.runInNewContext(source.slice(0, cut) +
  '\nglobalThis.tested={exactImpedancePacket,exactAdmittancePacket,smithQuantile,smithCdf,gammaFromZ,zFromGamma};})();',
  sandbox, {timeout: 5000});
const tested = sandbox.tested;

// Independent small complex-arithmetic oracle for phase averaging.
const c = (re, im = 0) => ({re, im});
const add = (a,b) => c(a.re+b.re,a.im+b.im);
const sub = (a,b) => c(a.re-b.re,a.im-b.im);
const mul = (a,b) => c(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
const div = (a,b) => { const d=b.re*b.re+b.im*b.im; return c((a.re*b.re+a.im*b.im)/d,(a.im*b.re-a.re*b.im)/d); };
const abs = a => Math.hypot(a.re,a.im);
const abs2 = a => a.re*a.re+a.im*a.im;
const rot = a => c(Math.cos(a),Math.sin(a));
const z = t => div(add(c(1),t),sub(c(1),t));
const y = t => div(sub(c(1),t),add(c(1),t));
const orders = [2,3,4,5,6,7,8,9,12,16];
const samples = [c(0),c(.1),c(.31,.24),c(-.28,.39),c(.82,-.09),c(-.95,.01),c(.005,.96)];
const radii = [.70,.84,.94,.97], counts = [32,64,96,128];
let packetChecks=0, parsevalChecks=0, quantileChecks=0, intervalChecks=0, loadChecks=0;
let maxPacketRel=0, maxParsevalRel=0, maxCdfError=0, maxMassError=0, maxLoadRel=0;
function check(ok, message) { if (!ok) throw new Error(message); }

for (const t of samples) for (const n of orders) {
  let orbitEnergy=0, packetEnergy=0;
  const zs=[], ys=[];
  for (let k=0;k<n;k++) {
    const p=mul(rot(2*Math.PI*k/n),t);
    zs.push(z(p)); ys.push(y(p)); orbitEnergy += abs2(zs[k])/n;
  }
  for (let j=0;j<n;j++) {
    let expectedZ=c(0), expectedY=c(0);
    for (let k=0;k<n;k++) {
      const weight=rot(-2*Math.PI*j*k/n);
      expectedZ=add(expectedZ,mul(weight,zs[k]));
      expectedY=add(expectedY,mul(weight,ys[k]));
    }
    expectedZ=c(expectedZ.re/n,expectedZ.im/n);
    expectedY=c(expectedY.re/n,expectedY.im/n);
    const actualZ=tested.exactImpedancePacket(t,n,j);
    const actualY=tested.exactAdmittancePacket(t,n,j);
    for (const [actual,expected,label] of [[actualZ,expectedZ,'z'],[actualY,expectedY,'y']]) {
      const error=abs(sub(actual,expected))/(1+abs(expected));
      maxPacketRel=Math.max(maxPacketRel,error);
      check(Number.isFinite(error) && error < 2e-12,`packet ${label}, n=${n}, j=${j}, t=${JSON.stringify(t)}: ${error}`);
      packetChecks++;
    }
    packetEnergy+=abs2(actualZ);
  }
  const error=Math.abs(packetEnergy-orbitEnergy)/(1+orbitEnergy);
  maxParsevalRel=Math.max(maxParsevalRel,error);
  check(Number.isFinite(error) && error < 2e-12,`Parseval n=${n}, t=${JSON.stringify(t)}: ${error}`);
  parsevalChecks++;
}

for (const rho of radii) for (const count of counts) {
  let last=-1, lastCdf=0;
  for (let j=0;j<=count;j++) {
    const mass=j/count, theta=tested.smithQuantile(rho,mass), got=tested.smithCdf(rho,theta);
    const error=Math.abs(got-mass);
    check(Number.isFinite(theta) && theta>=last && error < 2e-10,`quantile rho=${rho}, n=${count}, j=${j}: ${error}`);
    maxCdfError=Math.max(maxCdfError,error); quantileChecks++;
    if (j>0) {
      const massError=Math.abs((got-lastCdf)-1/count);
      maxMassError=Math.max(maxMassError,massError);
      check(massError < 4e-10,`mass rho=${rho}, n=${count}, j=${j}: ${massError}`);
      intervalChecks++;
    }
    last=theta; lastCdf=got;
  }
}

for (const r of [0,.01,.5,1,2,20]) for (const x of [-20,-2,-.5,0,.5,2,20]) {
  const input=c(r,x), gamma=tested.gammaFromZ(input), actual=tested.zFromGamma(gamma);
  const error=abs(sub(input,actual))/(1+abs(input));
  check(abs(gamma)<=1+2e-14 && error < 2e-13,`load r=${r}, x=${x}: ${error}`);
  maxLoadRel=Math.max(maxLoadRel,error); loadChecks++;
}

console.log(JSON.stringify({status:'passed', node:process.version, source_sha256:hash,
  domain:{orders,samples,radii,counts,loads:'r in {0,.01,.5,1,2,20}; x in {-20,-2,-.5,0,.5,2,20}'},
  counts:{packetChecks,parsevalChecks,quantileChecks,intervalChecks,loadChecks},
  maxima:{maxPacketRel,maxParsevalRel,maxCdfError,maxMassError,maxLoadRel},
  limits:'Finite double-precision fixtures; the extracted pure-math prefix is tested, not DOM behavior or universal correctness.'},null,2));
