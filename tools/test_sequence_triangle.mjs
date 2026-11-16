import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {tableState,tableCells,tableSlice,tableCSV,tableLink,tableSearch,shortInteger} from '../website/assets/sequence-triangle-core.mjs';

const fixture={id:'TEST',offset:5,terms:['1','0','1','0','9','10'],triangle:{row_lengths:[1,2,3],row_offsets:[0,1,3],degree_multiplier:3}};
test('reader-facing source uses UTF-8 punctuation without encoding artifacts',()=>{
  for(const path of ['website/assets/sequence-triangle.mjs','tools/sequence_library.py'])assert.doesNotMatch(readFileSync(path,'utf8'),/\uFFFD|\u00C3|\u00C2|\u00E2[\u20AC\u02C6]/);
  assert.match(readFileSync('website/assets/sequence-triangle.mjs','utf8'),/row’s last coefficient/);
});
test('slices retain flat positions, polynomial coordinates, source degrees, zeros and signs',()=>{
  assert.deepEqual(tableSlice(fixture,{kind:'row',index:2}).cells.map(c=>[c.j,c.n,c.k,c.degree,c.raw]),[[8,2,0,6,'0'],[9,2,1,6,'9'],[10,2,2,6,'10']]);
  assert.deepEqual(tableSlice(fixture,{kind:'column',index:1}).cells.map(c=>[c.n,c.k,c.j,c.raw]),[[1,1,7,'1'],[2,1,9,'9']]);
  assert.deepEqual(tableSlice(fixture,{kind:'diagonal',index:1}).cells.map(c=>[c.n,c.k,c.j,c.raw]),[[1,0,6,'0'],[2,1,9,'9']]);
});
test('right-edge diagonals use each row length, including theta widths',()=>{
  const theta={id:'THETA',offset:0,terms:['1','0','-1','-1','0','2','3','6','5'],triangle:{row_lengths:[1,3,5],degree_multiplier:2}};
  assert.deepEqual(tableSlice(theta,{kind:'diagonal',index:1}).cells.map(c=>[c.n,c.k,c.raw,c.degree]),[[1,1,'-1',2],[2,3,'6',4]]);
  assert.deepEqual(tableSlice(theta,{kind:'column',index:3}).cells.map(c=>c.raw),['6']);
  assert.equal(tableSlice(theta,{kind:'row',index:1,view:'mod',mod:7}).cells[1].residue,'6');
});
test('every stored cell in all 55 coefficient tables is covered once by each slice partition',()=>{
  const code="import json; from sequence_research_tables import research_additions; print(json.dumps([{k:e[k] for k in ('id','offset','terms','triangle')} for e in research_additions() if 'triangle' in e]))";
  const entries=JSON.parse(execFileSync(process.env.PYTHON||'python',['-c',code],{encoding:'utf8',env:{...process.env,PYTHONPATH:'tools'},maxBuffer:16*1024*1024}));
  assert.equal(entries.length,55);let visited=0;
  for(const entry of entries){
    const expected=[];entry.triangle.row_lengths.forEach((length,n)=>{for(let k=0;k<length;k++){const j=entry.triangle.row_offsets[n]+k;expected.push({j,n,k,degree:n*entry.triangle.degree_multiplier,raw:entry.terms[j]});}});
    assert.deepEqual(tableCells(entry).map(({edge,...cell})=>cell),expected);
    for(const kind of ['row','column','diagonal']){
      const selected=[];const max=kind==='row'?entry.triangle.row_lengths.length:Math.max(...entry.triangle.row_lengths);
      for(let index=0;index<max;index++){
        const slice=tableSlice(entry,{kind,index,view:'mod',mod:11});
        const oracle=expected.filter(c=>kind==='row'?c.n===index:kind==='column'?c.k===index:entry.triangle.row_lengths[c.n]-1-c.k===index);
        assert.deepEqual(slice.cells.map(c=>c.j),oracle.map(c=>c.j),entry.id+' '+kind+' '+index);
        for(const c of slice.cells){const a=BigInt(c.raw),expectedResidue=a<0n?(11n-((-a)%11n))%11n:a%11n;assert.equal(c.residue,String(expectedResidue));selected.push(c.j);}
      }
      assert.deepEqual(selected.sort((a,b)=>a-b),expected.map(c=>c.j));visited+=selected.length;
    }
  }
  assert.equal(visited,5083*3);
});
test('exact coefficients survive CSV, copied terms and search links beyond Number precision',()=>{
  const raw='-100000000000000000000000000000000000007',entry={...fixture,terms:['1','0','1','0',raw,'10']};
  const slice=tableSlice(entry,{kind:'row',index:2,view:'mod',mod:7});
  assert.ok(tableCSV(slice).includes('9,2,1,6,'+raw+','));assert.match(tableCSV(slice),/^flat_j,row_n,column_k,source_degree,coefficient,residue_mod_7\n/);
  const link=new URL(tableLink('https://example.test/sequence-families/T.html?view=mod&mod=13#plot',slice.state));assert.equal(link.searchParams.get('mod'),'13');assert.equal(link.searchParams.get('table-mod'),'7');assert.equal(link.hash,'#triangle');
  const search=new URL(tableSearch(link.href,slice));assert.equal(search.pathname,'/sequence-library.html');assert.equal(search.searchParams.get('q'),'terms:0,'+raw+',10');assert.equal(slice.cells[1].raw,raw);
});
test('invalid links, indices and moduli fail explicitly; spoken huge integers stay bounded',()=>{
  for(const options of [{kind:'unknown'},{kind:'column',index:3},{index:1.1},{index:''},{mod:1},{mod:'2e100'},{view:'color'},{scale:'log'},{zero:'maybe'}])assert.throws(()=>tableState(fixture,options));
  assert.equal(tableState(fixture).index,2);assert.equal(tableState(fixture,{kind:'column'}).index,1);
  assert.ok(shortInteger('-'+'9'.repeat(1000)).length<100);assert.match(shortInteger('-'+'9'.repeat(1000)),/negative 1000 digits/);assert.equal(shortInteger('-12'),'-12');
});
