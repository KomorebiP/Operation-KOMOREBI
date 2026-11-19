// Exact numeric and serialization regressions for Closed Forms calculator.
// Author: Komorebi P.
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {binomial,falling,sparseCoefficients,centralWeightedMoment,weightedJet,
  bareissDeterminant,weightedHankel,fourFthreeHankel,meixnerCoefficients,
  computeExactWindow,exactWindowCSV,exactViewURL,readExactView
} from '../website/assets/sequence-closed-forms-core.mjs';

function factorial(n){let x=1n;for(let i=2;i<=n;i++)x*=BigInt(i);return x;}
function rising(r,n){let p=1n;for(let k=0;k<n;k++)p*=BigInt(r+k);return p;}
function directSparse(n,p,q,r,u,v){
  let sum=0n;
  for(let i=0;i<=Math.floor(n/p);i++)for(let j=0;j<=Math.floor(n/q);j++){
    if(p*i+q*j!==n)continue;
    const num=rising(r,i+j)*BigInt(u)**BigInt(i)*BigInt(v)**BigInt(j);
    const den=factorial(i)*factorial(j);
    assert.equal(num%den,0n);
    sum+=num/den;
  }
  return sum;
}
function directJet(n,d,lambda,c){
  function J(t){
    if(t<0)return 0n;
    let sum=0n;
    for(let m=d;2*m<=t;m++){
      sum+=binomial(t,2*m)*falling(m,d)*binomial(2*m,m)*BigInt(lambda)**BigInt(t-2*m);
    }
    return sum;
  }
  return J(n)+BigInt(c)*BigInt(n)*J(n-1);
}
test('exact two-delay recurrence matches independent finite compositions',()=>{
  for(const [p,q,r,u,v] of [
    [2,3,1,1,1],[2,5,1,1,1],[3,3,3,2,-2],
    [4,6,2,1,1],[2,5,-3,1,1],[1,2,4,0,2],
    [2,3,5,-1,0],[1,1,1,2,3],[3,5,-2,3,-4]
  ]){
    const values=sparseCoefficients(p,q,r,u,v,30);
    for(let n=0;n<=30;n++)assert.equal(values[n],directSparse(n,p,q,r,u,v),
      'sparse mismatch: '+[p,q,r,u,v,n].join(','));
  }
  assert.deepEqual(sparseCoefficients(2,5,1,1,1,11).map(String),
    ['1','0','1','0','1','1','1','2','1','3','2','4']);
  assert.deepEqual(sparseCoefficients(2,3,-2,1,1,9).map(String),
    ['1','0','-2','-2','1','2','1','0','0','0']);
});
test('weighted jets agree with an independently constructed finite J formula',()=>{
  for(let d=0;d<=4;d++)for(const lambda of [-2,0,1,3])
    for(const c of [-2,0,1,2])for(let n=0;n<=22;n++){
      assert.equal(weightedJet(n,d,lambda,c),directJet(n,d,lambda,c),
        'weighted mismatch '+[d,lambda,c,n].join(','));
    }
  assert.deepEqual(Array.from({length:7},(_,n)=>String(weightedJet(n,0,1,1))),
    ['1','2','5','16','47','146','447']);
  assert.deepEqual(Array.from({length:9},(_,n)=>String(weightedJet(n,1,1,1))),
    ['0','0','2','12','48','200','750','2772','9912']);
  assert.equal(centralWeightedMoment(1,0,1),1n);
  assert.equal(centralWeightedMoment(3,1,1),6n);
});
test('fraction-free Hankel determinant agrees with terminating 4F3 and known weighted blocks',()=>{
  assert.equal(bareissDeterminant([]),1n);
  assert.equal(bareissDeterminant([[0n,1n],[1n,0n]]),-1n);
  assert.equal(bareissDeterminant([[0n,0n],[0n,0n]]),0n);
  for(const c of [-2,-1,0,1,2])for(let n=0;n<=10;n++){
    assert.equal(weightedHankel(n,0,c),fourFthreeHankel(n,c),
      'Hankel mismatch c='+c+', n='+n);
  }
  assert.deepEqual(Array.from({length:9},(_,n)=>String(weightedHankel(n,0,1))),
    ['1','1','1','-14','-100','56','6112','58304','320448']);
  assert.deepEqual(Array.from({length:8},(_,n)=>String(weightedHankel(n,1,1))),
    ['1','0','0','-8','1680','-271488','-2874880','1840174080']);
  assert.deepEqual(Array.from({length:8},(_,n)=>String(weightedHankel(n,2,1))),
    ['1','0','0','0','0','248832','-57644421120','-289931282841600']);
});
test('integer Meixner polynomial recurrence retains exact signs and initial values',()=>{
  assert.deepEqual(meixnerCoefficients(1,2,8).map(String),
    ['1','2','3','-2','-31','-30','715','2510','-30015']);
  for(const s of [-2,0,1,5])for(let n=0;n<=28;n++){
    const positive=meixnerCoefficients(s,3,n)[n];
    const negative=meixnerCoefficients(s,-3,n)[n];
    assert.equal(negative,(n%2?-1n:1n)*positive);
  }
});
test('window has correct original indices, exact large numbers and CSV columns',()=>{
  const sparse=computeExactWindow({mode:'sparse',start:'72',count:'2',
    p:'1',q:'1',r:'1',u:'12',v:'12'});
  assert.equal(sparse.rows[0].index,72);
  assert.equal(sparse.rows[0].value,String(24n**72n));
  assert.equal(sparse.rows[1].value,String(24n**73n));
  assert.match(exactWindowCSV(sparse),/family,index,exact_integer,parameters/);
  assert.ok(exactWindowCSV(sparse).includes(String(24n**72n)));
  const negative=computeExactWindow({mode:'sparse',start:'0',count:'4',
    p:'2',q:'3',r:'-2',u:'1',v:'1'});
  assert.deepEqual(negative.rows.map(x=>x.value),['1','0','-2','-2']);
  const h=computeExactWindow({mode:'hankel',start:'0',count:'4',d:'0',c:'1'});
  assert.deepEqual(h.rows.map(x=>x.value),['1','1','1','-14']);
  assert.match(h.verification,/independent terminating 4F3/);
});
test('shared calculator views restore exact parameters without sending coefficients',()=>{
  const raw={mode:'jet',start:'4',count:'11',d:'2',lambda:'-1',c:'3'};
  const link=exactViewURL('https://example.test/sequence-closed-forms.html?q=Hankel#closed-theorems',raw);
  const url=new URL(link);
  assert.equal(url.searchParams.get('q'),'Hankel');
  assert.equal(url.hash,'#closed-calculator-panel');
  assert.ok(!link.includes('exact_integer'));
  assert.deepEqual(readExactView(link),raw);
  assert.equal(readExactView('https://example.test/sequence-closed-forms.html'),null);
  const duplicate=new URL(link);duplicate.searchParams.append('cf-d','5');
  assert.throws(()=>readExactView(duplicate.href),/repeated setting/);
  const unknown=new URL(link);unknown.searchParams.append('cf-out','999');
  assert.throws(()=>readExactView(unknown.href),/unexpected setting/);
  assert.throws(()=>readExactView(link.replace('cf-v=1','cf-v=999')),/Unsupported/);
  assert.equal(exactViewURL(link,raw),link);
});
test('calculator rejects bounds and malformed integers without numerical rounding',()=>{
  const base={mode:'sparse',p:'2',q:'3',r:'1',u:'1',v:'1',start:'0',count:'12'};
  assert.throws(()=>computeExactWindow({...base,p:'0'}),/between 1 and 16/);
  assert.throws(()=>computeExactWindow({...base,r:'0.5'}),/integer/);
  assert.throws(()=>computeExactWindow({...base,count:'99'}),/between 1 and 32/);
  assert.throws(()=>computeExactWindow({...base,start:'90',count:'12'}),/last index/);
  assert.throws(()=>computeExactWindow({...base,r:'9007199254740993'}),/between/);
  assert.throws(()=>computeExactWindow({mode:'hankel',start:'10',count:'8',d:'1',c:'1'}),/last index/);
  assert.throws(()=>computeExactWindow({mode:'unknown',start:0,count:2}),/supported/);
});
