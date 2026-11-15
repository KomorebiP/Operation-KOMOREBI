import test from 'node:test';import assert from 'node:assert/strict';
import {referenceQuery,referenceValues,referencePositions,referenceNameMatches} from '../website/assets/sequence-oeis-core.mjs';
import {searchEntries} from '../website/assets/sequence-atlas-search.mjs';
import {PLOT_DEFAULTS,plotColors,plotTheme,validateAppearance,contrastRatio,appearanceLink,readAppearance} from '../website/assets/sequence-plot-options.mjs';
test('bulk reference queries preserve exact large integers, signs, zero and wildcard positions',()=>{
  assert.equal(referenceQuery('a108').id,'A000108');assert.throws(()=>referenceQuery('1,2'));assert.throws(()=>referenceQuery('?,?,?,?,?,?,?,?'));
  const q=referenceQuery('0,-1,9007199254740993,?,4,5,6,7'),row=referenceValues('A123456 ,99,0,-1,9007199254740993,3,4,5,6,7,');assert.equal(row.id,'A123456');assert.deepEqual(referencePositions(row.values,q),[1]);
  assert.equal(referenceNameMatches('A000108','Catalan numbers',referenceQuery('catalan numbers')),true);assert.equal(referenceNameMatches('A000108','Catalan numbers',referenceQuery('catalan Lucas')),false);
});
test('alternate formulas and parameter fields are searchable without changing terms',()=>{
  const entry={id:'KFOR-C-03-01-02-num',title:'Coefficient numerator',formula:'a(n)=num(q(n))',recurrence:'',formulas:[{kind:'hypergeometric',expression:'0F2( ; 1/3, 2/3 ; z)'}],tags:[],kind:'congruential numerator',collection:'formulas',N:3,j:1,power:2,offset:2,status:'Published',terms:['1','2','3']};
  for(const query of ['formula:0F2','representation:hypergeometric','n:03 j:01 r:02','collection:formulas','1,?,3'])assert.equal(searchEntries([entry],query).length,1,query);
  assert.equal(searchEntries([entry],'j:2').length,0);assert.match(searchEntries([entry],'1,?,3')[0].reason,/2–4/);
});
test('theme, custom comparison, reversal and opacity survive shared links and legacy preferences',()=>{
  assert.equal(contrastRatio('#ffffff','#000000'),21);assert.equal(contrastRatio('#ffffff','#ffffff'),1);
  const state=validateAppearance({theme:'night',palette:'custom',custom:'#aabbcc',secondary:'#ffeecc',reverse:'reverse',opacity:'0.55'}),colors=plotColors(state);assert.equal(colors[0],'#aabbcc');assert.equal(colors[1],'#ffeecc');assert.equal(plotTheme(state).background,'#142130');
  assert.deepEqual(readAppearance(appearanceLink('https://example.test/',state)).state,state);
  for(const palette of ['lagoon','plum','cividis','spectrum'])assert.equal(plotColors({...PLOT_DEFAULTS,palette}).length,8);
  assert.equal(readAppearance('https://example.test/',{getItem:()=>JSON.stringify({schema:1,appearance:{palette:'ocean'}})}).state.theme,'paper');
  for(const options of [{secondary:'red'},{opacity:'0'},{theme:'arbitrary'},{reverse:'yes'}])assert.throws(()=>validateAppearance(options));
});
