import test from 'node:test';
import assert from 'node:assert/strict';
import {generateFamily,workedFamily,finiteHyperH,constantRecurrence,validateFamily,familyURL,familyCSV} from '../website/assets/sequence-family-core.mjs';
import {modularCycle} from '../website/assets/sequence-modular-core.mjs';
import {identifyLocal,identifyInput} from '../website/assets/sequence-discovery-core.mjs';
import {composeScalarTransfers,relationPath} from '../website/assets/sequence-graph-core.mjs';
import {createNotebook,validateNotebook,readNotebooks,writeNotebooks,notebookLink,readNotebookLink,NOTEBOOK_KEY} from '../website/assets/sequence-notebook-core.mjs';
import {familySource,customSource,descriptor,readWorkbenchLink,workbenchLink,WORKBENCH_DEFAULTS} from '../website/assets/sequence-workbench-core.mjs';
import {searchEntries} from '../website/assets/sequence-atlas-search.mjs';
import {formulaLatex} from '../website/assets/math-display.mjs';
test('weighted k-step powers agree with hand-expanded denominator and seeded Lucas values',()=>{
  const a=generateFamily('linear',{k:3,r:2,c:2,count:6});assert.deepEqual(a.terms,['1','4','16','60','212','728']);assert.equal(workedFamily(a).alternative,'60');
  const denominator=constantRecurrence({k:3,r:2,c:2});assert.deepEqual(denominator.coefficients,['4','0','-4','-12','-8','-4']);assert.equal(denominator.order,6);
  const lucas=generateFamily('linear',{k:2,r:8,seedMode:'custom',seeds:'2, 1',count:8});assert.equal(lucas.params.r,1);assert.deepEqual(lucas.terms,['2','1','3','4','7','11','18','29']);assert.equal(workedFamily(lucas).alternative,'4');
  const short=generateFamily('kbonacci',{k:16,count:2});assert.deepEqual(short.terms,['0','0']);assert.equal(workedFamily(short).alternative,'0');
  assert.equal(finiteHyperH(2,1,1,0).a,1n);assert.equal(finiteHyperH(2,1,1,0).b,1n);
});
test('positive and alternating block denominators retain distinct signs and rational components',()=>{
  assert.deepEqual(generateFamily('reciprocal',{N:2,r:1,count:4}).terms,['1','1','5','61']);
  assert.deepEqual(generateFamily('congruential',{N:2,j:0,r:1,count:4}).terms,['1','-1','5','-61']);
  const a=generateFamily('congruential',{N:2,j:1,r:1,count:4}),b=generateFamily('congruential',{N:2,j:1,r:1,count:4,component:'denominator'});
  assert.deepEqual(a.rationalTerms,['1','-1/3','7/15','-31/21']);assert.deepEqual(a.terms,['1','-1','7','-31']);assert.deepEqual(b.terms,['1','3','15','21']);assert.match(familyCSV(a),/1,2,-1,-1\/3/);
  const p=generateFamily('appell',{N:3,j:1,x:2,count:4});assert.deepEqual(p.rationalTerms,['1','2','4','31/4']);
});
test('polynomial columns, theta values and original multisection indices remain explicit',()=>{
  const p=generateFamily('secancy',{N:3,column:2,count:4});assert.equal(p.offset,2);assert.deepEqual(p.terms,['10','756','142362','55429920']);assert.deepEqual(p.degrees,[6,9,12,15]);
  assert.deepEqual(generateFamily('theta',{x:2,count:4}).terms,['1','-6','144','-7536']);assert.deepEqual(generateFamily('theta',{x:0,count:4}).terms,['1','0','0','0']);assert.deepEqual(generateFamily('theta',{x:1,count:4}).terms,['1','-2','16','-272']);
  assert.deepEqual(generateFamily('tangent',{N:3,count:4}).degrees,[2,5,8,11]);
  const section=generateFamily('section',{N:3,j:1,parent:'fibonacci',count:4});assert.deepEqual(section.terms,['1','3','13','55']);assert.deepEqual(section.degrees,[1,4,7,10]);assert.deepEqual(generateFamily('section',{N:1,j:0,parent:'pell',count:5}).terms,['0','1','2','5','12']);
});
test('family boundaries reject invalid seeds, indices, fractions and excessive windows',()=>{
  for(const options of [{k:1},{count:65},{seedMode:'custom',k:3,seeds:'1,2'},{r:1.5},{c:0}])assert.throws(()=>generateFamily('linear',options));
  assert.throws(()=>generateFamily('congruential',{N:3,j:3}));assert.throws(()=>generateFamily('reciprocal',{N:1}));assert.throws(()=>generateFamily('theta',{x:0.5}));assert.throws(()=>generateFamily('appell',{component:'rounded'}));
  assert.equal(validateFamily('linear',{N:1}).k,3);
  const link=new URL(familyURL('https://example.test/library?q=old','GF-LINEAR',{k:4},{view:'mod',modulus:11}));assert.equal(link.searchParams.get('family'),'GF-LINEAR');assert.equal(link.searchParams.get('family-view'),'mod');
});
test('complete-state modular certificates prove cycles and retain transient prefixes',()=>{
  const fib=modularCycle({k:2},7);assert.equal(fib.period,16);assert.equal(fib.preperiod,0);assert.deepEqual(fib.repeatedState,fib.initialState);
  const transient=modularCycle({k:2,c:2},2);assert.equal(transient.period,1);assert.equal(transient.preperiod,1);assert.deepEqual(transient.initialState,[1,0]);assert.deepEqual(transient.repeatedState,[0,0]);
  const unknown=modularCycle({k:2},7,1);assert.equal(unknown.certified,false);assert.equal(unknown.period,null);assert.equal(unknown.scanned,1);
  const zero=modularCycle({k:2,seedMode:'custom',seeds:'0, 0'},9);assert.equal(zero.period,1);assert.equal(zero.preperiod,0);
  const p={k:3,r:2,c:2,count:64},orbit=modularCycle(p,7,256),terms=generateFamily('linear',p).terms;assert.deepEqual(orbit.values.slice(0,64),terms.slice(0,orbit.values.length).map(v=>Number(BigInt(v)%7n)));
  for(const [m,n]of [[1,100],[257,100],[7,0],[7,20001]])assert.throws(()=>modularCycle({},m,n));
});
const entry=(id,terms,offset=0)=>({id,title:id,terms:terms.map(String),offset,url:id+'.html'});
test('graph paths respect direction while scalar composition preserves Q and both shifts',()=>{
  const edges=[{key:'ab',source:'A',target:'B',kind:'seed shift',reversible:true},{key:'bc',source:'B',target:'C',kind:'extraction',reversible:false}];assert.equal(relationPath(edges,'A','C').length,2);assert.equal(relationPath(edges,'B','A')[0].reversed,true);assert.equal(relationPath(edges,'C','A'),null);assert.deepEqual(relationPath(edges,'A','A'),[]);
  const a=entry('A',[0,0,-2,3,7],-4),b=entry('B',[0,3,-2,1],5),c=entry('C',[0,-5,7,9],10),map=composeScalarTransfers(a,b,c,3);assert.equal(map.verified,true);assert.equal(map.indexShift,13);assert.equal(map.positionShift,-1);assert.equal(map.rows[0].composed,'5/2');assert.equal(map.rows[0].inverse,'2/5');
  assert.throws(()=>composeScalarTransfers({...a,triangle:{}},b,c,3),/scalar column/);assert.throws(()=>composeScalarTransfers(entry('Z',[0,0,0]),b,c,2),/nonzero anchor/);
});
test('identification ranks exact forms, exposes gcd normalization and keeps odd/even positions',()=>{
  const fib=entry('F',[0,1,1,2,3,5,8,13]),double=entry('D',[0,2,2,4,6,10,16,26]),flat={...entry('TABLE',[0,1,1,2,3,5,8,13]),triangle:{}};
  const result=identifyLocal([fib,double,flat],'0,2,2,4,6,10,16,26');assert.equal(result.scanned,2);assert.equal(result.results[0].id,'D');assert.match(result.results.find(r=>r.id==='F').inputOperation,/gcd 2/);
  const split=identifyLocal([fib],'0,0,1,0,1,0,2,0,3,0,5,0,8,0,13,0').results.find(r=>r.id==='F');assert.match(split.inputOperation,/Even/);assert.deepEqual(split.inputPositions,[0,2,4,6,8,10,12,14]);
  const odd=entry('ODD',[1,3,5,7,9,11,13],10),diff=identifyLocal([odd],'0,1,4,9,16,25,36,49').results[0];assert.match(diff.inputOperation,/First differences/);assert.equal(diff.targetIndex,10);assert.equal(diff.inputPositions[0],1);
  assert.equal(identifyLocal([entry('ZERO',Array(10).fill(0))],'0,0,0,0,0,0').results[0].lowInformation,true);assert.throws(()=>identifyInput('1,2,3,4,5,?'));assert.throws(()=>identifyInput('9'.repeat(301)+',1,2,3,4,5'));
});
test('paper search respects Roman-number boundaries and family construction aliases',()=>{
  const base={title:'Source family',formula:'4phi3',kind:'generalized family',tags:[],status:'Source-defined',offset:0,terms:[],family_names:['Generalized recoupling'],generalized_family_ids:['GF-RACAH']},a={...base,id:'A',paper_refs:['SF-VI'],paper_titles:['Special Functions VI']},b={...base,id:'B',paper_refs:['SF-VIII'],paper_titles:['Special Functions VIII']};
  assert.deepEqual(searchEntries([a,b],'paper:SF-VI').map(h=>h.entry.id),['A']);assert.deepEqual(searchEntries([a,b],'paper:"special functions vi"').map(h=>h.entry.id),['A']);assert.equal(searchEntries([a,b],'family:recoupling').length,2);assert.equal(searchEntries([a,b],'paper:"("').length,0);
  assert.match(formulaLatex('A_n(z)=4phi3(q^(-n),a b c d q^(n-1),a z,a z^(-1);a b,a c,a d;q,q)'),/\\phi_\{3\}/);
});
test('notebooks round-trip Unicode without executing data or overwriting unreadable storage',()=>{
  const notebook=createNotebook('Θ研究','Compare r=2; check the shift.',{family:{family:'GF-LINEAR',params:{k:3}}},'n-test'),url=notebookLink('https://example.test/library?q=old',notebook);assert.deepEqual(readNotebookLink(url),notebook);assert.equal(new URL(url).searchParams.has('q'),false);
  const map=new Map(),storage={getItem:k=>map.get(k),setItem:(k,v)=>map.set(k,v)};assert.equal(writeNotebooks(storage,[notebook]),true);assert.deepEqual(readNotebooks(storage).items,[notebook]);assert.equal(writeNotebooks(storage,[notebook,notebook]),false);
  map.set(NOTEBOOK_KEY,'broken');const before=map.get(NOTEBOOK_KEY),bad=readNotebooks(storage);assert.equal(bad.available,false);assert.equal(map.get(NOTEBOOK_KEY),before);
  assert.throws(()=>validateNotebook({...notebook,notes:'x'.repeat(10001)}));assert.throws(()=>validateNotebook(JSON.parse('{"schema":1,"id":"n-1","title":"x","notes":"","parts":{"family":{"__proto__":{}}}}')));assert.throws(()=>readNotebookLink('https://example.test/?notebook=%%%'));
  assert.throws(()=>notebookLink('https://example.test/',createNotebook('Big','𝛼'.repeat(4000),{},'n-big')),/too large/);
});
test('family and pasted comparison descriptors restore exact values and normalization',()=>{
  const family=familySource('congruential',{N:2,j:1,count:4}),custom=customSource({title:'Pasted',offset:3,terms:['9007199254740993','-2','0']}),url=workbenchLink('https://example.test/sequence-library.html',[family,custom],WORKBENCH_DEFAULTS),restored=readWorkbenchLink(url,[],'snapshot');
  assert.deepEqual(restored.sources[0].terms,['1','-1','7','-31']);assert.match(restored.sources[0].indexKind,/numerator/);assert.equal(restored.sources[1].terms[0],'9007199254740993');assert.equal(restored.sources[1].offset,3);assert.throws(()=>customSource({title:'Bad',offset:0,terms:['1.5']}));
});

test('notebook fragments avoid host request limits, preserve legacy links and retain large JSON workspaces',()=>{
  const notebook=createNotebook('Long research notes','x'.repeat(8000),{},'n-long'),link=notebookLink('https://example.test/library?q=old',notebook),url=new URL(link);
  assert.ok(link.length>10000);assert.equal(url.search,'');assert.equal(link.split('#')[0],'https://example.test/library');assert.deepEqual(readNotebookLink(link),notebook);
  const legacy=new URL('https://example.test/library#research-notebooks');legacy.searchParams.set('notebook',new URLSearchParams(url.hash.split('?')[1]).get('notebook'));assert.deepEqual(readNotebookLink(legacy.href),notebook);
  const large=customSource({title:'Large exact integers',offset:0,terms:Array(64).fill('9'.repeat(100))});assert.throws(()=>workbenchLink('https://example.test/library',[large],WORKBENCH_DEFAULTS),/too large/);
  const data={schema:1,state:WORKBENCH_DEFAULTS,sources:[descriptor(large)]},local=new URL('https://example.test/library');local.searchParams.set('wb',JSON.stringify(data));assert.equal(readWorkbenchLink(local.href,[],'snapshot').sources[0].terms.length,64);
});
