import test from 'node:test';
import assert from 'node:assert/strict';
import {formulaLatex,readMathDisplay} from '../website/assets/math-display.mjs';
import {atlasDestination,archiveDestination} from '../website/assets/sequence-navigation.mjs';

test('formula transcription preserves denominator function arguments and sum scope',()=>{
  const quotient=formulaLatex("a(n)=-D_2'(z)/D_2(z)");
  assert.match(quotient,/\\frac\{[^}]*D_\{2\}'/);
  assert.ok(quotient.endsWith('{D_{2}\\!\\left(z\\right)}'));
  assert.match(formulaLatex('a(n)=sum_(k=1)^n 1/k'),/\\sum_\{k=1\}\^\{n\}\{\\frac\{1\}\{k\}\}/);
  assert.ok(formulaLatex('a(n)=n!!').endsWith('n!!'));
  assert.ok(formulaLatex('a(n)=+n').endsWith('+n'));
});
test('hypergeometric parameters, polynomial columns, and substitutions retain their roles',()=>{
  const hyper=formulaLatex('0F1(;1/2;z^2/4)');
  assert.match(hyper,/\{\}_\{0\}F_\{1\}/);assert.match(hyper,/\\frac\{1\}\{2\}/);assert.match(hyper,/\\frac\{z\^\{2\}\}\{4\}/);
  assert.match(formulaLatex('a(n)=[r^2 z^(3n)] D_3(z)^(-r)'),/\\left\[r\^\{2\}/);
  assert.match(formulaLatex('a(n)=4^n (1/2)_n/(2)_n'),/\\frac/);
  assert.match(formulaLatex('F(n)=2^n; replace every source index n by (3n+1)'),/Replace source index/);
});
test('unsupported or ambiguous notation retains its literal source instead of guessing',()=>{
  for(const input of ['x^2^3','x_n_n','2^v_2(n)','f(a;b)','x^)',String.raw`\href{https://example.test}{x}`,'a(n)=the number of words','('.repeat(60)+'1'+')'.repeat(60)])assert.equal(formulaLatex(input),null,input);
  assert.equal(formulaLatex('x'.repeat(12001)),null);
});
test('one math preference has robust defaults without requiring browser storage',()=>{
  assert.equal(readMathDisplay({getItem:()=>null}),'typeset');assert.equal(readMathDisplay({getItem:()=> 'plain'}),'plain');assert.equal(readMathDisplay({getItem:()=> 'invalid'}),'typeset');assert.equal(readMathDisplay({getItem:()=>{throw Error('Denied');}}),'typeset');
});
test('old atlas search links open the complete library while plot links keep their state',()=>{
  const search=new URL(atlasDestination('https://example.test/site/sequences.html?q=id%3AKOM085#find'));assert.equal(search.pathname,'/site/sequence-library.html');assert.equal(search.searchParams.get('q'),'id:KOM085');assert.equal(search.hash,'#library-search');
  const plot=new URL(atlasDestination('https://example.test/site/sequences.html?seq=KSEQ-000025&view=mod&modulus=11#explorer'));assert.equal(plot.pathname,'/site/sequence-explorer.html');assert.equal(plot.searchParams.get('modulus'),'11');assert.equal(plot.searchParams.get('seq'),'KSEQ-000025');
  const archive=new URL(archiveDestination('https://example.test/site/sequence-archive.html',{query:'1, ?, 251',family:'Euler/block',review:'Known family',sort:'name',match:'start'}));assert.equal(archive.pathname,'/site/sequence-library.html');assert.equal(archive.searchParams.get('collection'),'recovered');assert.equal(archive.searchParams.get('q'),'1, ?, 251');assert.equal(archive.searchParams.get('status'),'Known family');assert.equal(archive.searchParams.get('match'),'start');
});

test('factorials keep their order relative to powers; definitions and constraints have separate rows',()=>{
  assert.equal(formulaLatex('n!^2'),String.raw`\left(n!\right)^{2}`);
  assert.equal(formulaLatex('n^2!'),null);
  assert.ok(formulaLatex('a(n)=n!\nb(n)=n+1').includes(String.raw`\\[.55em]`));
  assert.ok(formulaLatex('sum_(q_1+q_2=n; q_i>=1) 1/q_i!').includes(String.raw`\substack`));
  const hyper=formulaLatex('0F1(;1/2;z)');assert.ok(!hyper.includes(';'));assert.ok(hyper.includes(String.raw`\vphantom{1}`));assert.ok(hyper.includes(String.raw`\middle|`));
});

test('triangle row windows and polynomials retain sparse zeros, signs and variable row lengths',async()=>{
 const {triangleLayout,triangleWindow,trianglePolynomial}=await import('../website/assets/sequence-archive-core.mjs');
 const entry={id:'KFOR-TRI-H',offset:0,terms:['1','0','-1','-1','0','2','3','6','5'],triangle:{row_lengths:[1,3,5],variable:'x'}};
 assert.deepEqual(triangleLayout(entry).map(row=>[row.start,row.size]),[[0,1],[1,3],[4,5]]);
 assert.equal(trianglePolynomial(entry,1),'p(x)=-x - x^2');assert.equal(trianglePolynomial(entry,2),'p(x)=2x + 3x^2 + 6x^3 + 5x^4');
 assert.deepEqual(triangleWindow(entry,2),{start:4,size:5,view:'raw',scale:'linear',marks:'line',color:'single'});assert.throws(()=>triangleWindow(entry,3));
});
