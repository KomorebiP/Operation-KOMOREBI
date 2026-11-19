// Exact numeric and serialization regressions for Closed Forms calculator.
// Author: Komorebi P.
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {binomial,falling,sparseCoefficients,padovanCoefficients,
  fourBlockCoefficients,betaMomentCoefficients,betaHankelCoefficients,
  polynomialDifferentialMoment,differentialHankel,differentialMomentGeneratingFunction,
  differentialMomentsFromAlgebraicRecurrence,
  centralWeightedMoment,weightedJet,
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
test('Padovan powers reproduce the original and exact convolution squares',()=>{
  const a=padovanCoefficients(1,24);
  assert.deepEqual(a.slice(0,12).map(String),['1','0','0','1','0','1','1','1','2','2','3','4']);
  const squared=padovanCoefficients(2,24);
  for(let n=0;n<=24;n++){
    const convolution=Array.from({length:n+1},(_,k)=>a[k]*a[n-k])
      .reduce((s,v)=>s+v,0n);
    assert.equal(squared[n],convolution,'Padovan power mismatch n='+n);
  }
});
test('four-block polynomials preserve the offset and known integer coefficients',()=>{
  assert.deepEqual(fourBlockCoefficients(0,4).slice(1).map(String),
    ['1','34','11056','14873104']);
  assert.equal(fourBlockCoefficients(1,2)[1],3n);
  assert.equal(fourBlockCoefficients(1,2)[2],294n);
  const row=computeExactWindow({mode:'fourblock',start:'1',count:'4',a:'0'});
  assert.deepEqual(row.rows.map(x=>x.value),['1','34','11056','14873104']);
});
test('unnormalized beta-binomial moments and determinant rank stay exact',()=>{
  const values=betaMomentCoefficients(4,1,1,8);
  assert.deepEqual(values.slice(0,4).map(String),['120','240','720','2400']);
  const h=betaHankelCoefficients(4,1,1,8);
  assert.equal(h[0],1n);
  assert.equal(h[1],120n);
  assert.equal(h[2],28800n);
  assert.deepEqual(h.slice(6).map(String),['0','0','0']);
  for(const [L,a,b] of [[0,1,1],[4,1,1],[5,1,2],[6,2,1]]){
    const moments=betaMomentCoefficients(L,a,b,2*(L+1));
    const dets=betaHankelCoefficients(L,a,b,L+3);
    for(let n=0;n<=L+1;n++){
      const direct=bareissDeterminant(Array.from({length:n},(_,i)=>
        Array.from({length:n},(_,j)=>moments[i+j])));
      assert.equal(dets[n],direct,'beta determinant mismatch '+[L,a,b,n]);
    }
    assert.equal(dets[L+2],0n);
  }
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
test('finite differential Hankel mode matches independent source values and parity',()=>{
  const a=[1,1,0,0],c=[1,2,1,0];
  assert.deepEqual(Array.from({length:6},(_,n)=>String(differentialHankel(n,a,c))),
    ['1','1','2','-84','-456','52197296']);
  assert.deepEqual(Array.from({length:10},(_,n)=>String(polynomialDifferentialMoment(n,a,c))),
    ['1','2','6','24','66','180','620','1120','4830','6300']);
  const sparse=[0,1,0,0],second=[0,0,2,0];
  assert.equal(polynomialDifferentialMoment(3,sparse,second),0n);
  assert.equal(polynomialDifferentialMoment(4,sparse,second),48n);
  assert.deepEqual(Array.from({length:6},(_,n)=>String(differentialHankel(n,sparse,second))),
    ['1','0','0','0','0','254803968']);
  const flipped=[c[0],-c[1],c[2],-c[3]];
  for(let n=0;n<=8;n++)
    assert.equal(differentialHankel(n,a,c),differentialHankel(n,a,flipped));
  const report=computeExactWindow({mode:'differential_hankel',start:'0',count:'5',
    a0:'1',a1:'1',a2:'0',a3:'0',c0:'1',c1:'2',c2:'1',c3:'0'});
  assert.deepEqual(report.rows.map(row=>row.value),['1','1','2','-84','-456']);
  assert.match(report.verification,/separated-block rank/);
  const shared=exactViewURL('https://example.test/sequence-library.html',{
    mode:'differential_hankel',start:'0',count:'5',a0:'1',a1:'1',a2:'0',a3:'0',
    c0:'1',c1:'2',c2:'1',c3:'0'});
  assert.equal(new URL(shared).searchParams.get('cf-a1'),'1');
  assert.equal(new URL(shared).searchParams.get('cf-c2'),'1');
  assert.equal(readExactView(shared).mode,'differential_hankel');
});
test('every finite differential moment OGF matches independent BigInt moment sums',()=>{
  const sample=differentialMomentGeneratingFunction([1,1],[1,2,1]);
  assert.deepEqual(sample.numerator,['1','2','-8','-4','52','-16','-24']);
  assert.equal(sample.twiceExponent,7);
  assert.equal(sample.degreeBound,6);
  assert.equal(sample.weightDegree,1);
  assert.equal(sample.operatorOrder,2);
  for(const a of [[1],[0,1],[1,1],[2,-3,1],[0,0,1],[1,0,2,-1],[0]]){
    for(const c of [[1],[0,1],[1,2,1],[0,0,1],[1,0,-2,3],[0]]){
      const g=differentialMomentGeneratingFunction(a,c);
      const numerator=g.numerator.map(BigInt),den=[1n],t=BigInt(g.twiceExponent);
      assert.ok(numerator.length<=g.degreeBound+1);
      for(let m=1;m<=20;m++){
        const exact=den[m-1]*2n*(t+2n*BigInt(m)-2n);
        assert.equal(exact%BigInt(m),0n,'Denominator binomial coefficient failed to be integral');
        den.push(exact/BigInt(m));
      }
      for(let n=0;n<35;n++){
        let predicted=0n;
        for(let m=0;m<=Math.floor(n/2);m++){
          const k=n-2*m;
          if(k<numerator.length)predicted+=numerator[k]*den[m];
        }
        assert.equal(predicted,polynomialDifferentialMoment(n,a,c),
          'Moment generating function mismatch for '+JSON.stringify([a,c,n]));
      }
    }
  }
  const moments=computeExactWindow({mode:'differential_moments',start:'0',count:'10',
    a0:'1',a1:'1',a2:'0',a3:'0',c0:'1',c1:'2',c2:'1',c3:'0'});
  assert.deepEqual(moments.rows.map(row=>row.value),
    ['1','2','6','24','66','180','620','1120','4830','6300']);
  assert.deepEqual(moments.generatingFunction.numerator,sample.numerator);
  const large=computeExactWindow({mode:'differential_moments',start:'144',count:'17',
    a0:'1',a1:'1',a2:'0',a3:'0',c0:'1',c1:'2',c2:'1',c3:'0'});
  assert.equal(large.rows[0].index,144);
  assert.equal(large.rows.at(-1).index,160);
  assert.equal(large.rows.length,17);
  assert.equal(large.rows.at(-1).value,
    String(polynomialDifferentialMoment(160,[1,1,0,0],[1,2,1,0])));
  const shared=exactViewURL('https://example.test/sequence-library.html',{
    mode:'differential_moments',start:'144',count:'17',
    a0:'1',a1:'1',a2:'0',a3:'0',c0:'1',c1:'2',c2:'1',c3:'0'});
  assert.equal(readExactView(shared).mode,'differential_moments');
  assert.equal(new URL(shared).searchParams.get('cf-count'),'17');
});
test('regularized algebraic recurrence reconstructs exact moments after singular starts',()=>{
  for(const a of [[1],[0,1],[1,1],[2,-3,1],[0,0,1],[1,0,2,-1],[0]]){
    for(const c of [[1],[0,1],[1,2,1],[0,0,1],[1,0,-2,3],[0]]){
      const g=differentialMomentGeneratingFunction(a,c);
      const reconstructed=differentialMomentsFromAlgebraicRecurrence(a,c,65,g);
      assert.equal(reconstructed.length,66);
      const ell=g.initialZeroMoments;
      if(ell!==null){
        assert.ok(g.regularizedRecurrenceOrderBound>=0);
        for(let n=0;n<ell;n++)assert.equal(reconstructed[n],0n);
        assert.notEqual(reconstructed[ell],0n);
      }else{
        assert.ok(reconstructed.every(x=>x===0n));
      }
      for(let n=0;n<=65;n++)
        assert.equal(reconstructed[n],polynomialDifferentialMoment(n,a,c),
          'Regularized algebraic recurrence mismatch '+JSON.stringify([a,c,n]));
    }
  }
  const singular=differentialMomentGeneratingFunction([0,1],[0,0,1]);
  assert.equal(singular.initialZeroMoments,4);
  assert.equal(singular.regularizedRecurrenceOrderBound,4);
  const vanishes=differentialMomentGeneratingFunction([0],[1,2,3]);
  assert.equal(vanishes.initialZeroMoments,null);
  assert.equal(vanishes.regularizedRecurrenceOrderBound,0);
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
  assert.deepEqual(computeExactWindow({mode:'padovan',start:'0',count:'4',h:'1'})
    .rows.map(x=>x.value),['1','0','0','1']);
  assert.deepEqual(computeExactWindow({mode:'beta_moments',start:'0',count:'3',L:'4',a:'1',b:'1'})
    .rows.map(x=>x.value),['120','240','720']);
  assert.deepEqual(computeExactWindow({mode:'beta_hankel',start:'0',count:'3',L:'4',a:'1',b:'1'})
    .rows.map(x=>x.value),['1','120','28800']);
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
  assert.throws(()=>readExactView(link.replace('cf-version=1','cf-version=999')),/Unsupported/);
  assert.equal(exactViewURL(link,raw),link);
  const four={mode:'fourblock',start:'1',count:'4',a:'-2'};
  assert.deepEqual(readExactView(exactViewURL('https://example.test/sequence-library.html',four)),four);
  const sparseView={mode:'sparse',start:'3',count:'4',p:'2',q:'5',r:'1',u:'1',v:'12'};
  const sparseLink=exactViewURL('https://example.test/sequence-closed-forms.html',sparseView);
  assert.equal(new URL(sparseLink).searchParams.get('cf-version'),'1');
  assert.equal(new URL(sparseLink).searchParams.get('cf-v'),'12');
  assert.deepEqual(readExactView(sparseLink),sparseView);
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
  assert.throws(()=>computeExactWindow({mode:'fourblock',start:'0',count:'4',a:'0'}),/between 1 and 32/);
  assert.throws(()=>computeExactWindow({mode:'beta_moments',start:'0',count:'3',L:'4',a:'0',b:'1'}),/Beta shape a/);
  assert.throws(()=>computeExactWindow({mode:'beta_hankel',start:'0',count:'3',L:'13',a:'1',b:'1'}),/between 0 and 12/);
  assert.throws(()=>computeExactWindow({mode:'differential_hankel',start:'11',count:'5',
    a0:'1',a1:'0',a2:'0',a3:'0',c0:'1',c1:'0',c2:'0',c3:'0'}),/last index/);
});
