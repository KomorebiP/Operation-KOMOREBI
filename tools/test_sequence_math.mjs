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
