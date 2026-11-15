import test from 'node:test';
import assert from 'node:assert/strict';
import {archiveWindow,archiveLink,windowCSV} from '../website/assets/sequence-archive-core.mjs';
import {searchEntries,canonicalID} from '../website/assets/sequence-atlas-search.mjs';

// Parse source integers losslessly through Python, rather than JS JSON numbers.
import {execFileSync} from 'node:child_process';
const entries=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','-c','import sys,json;sys.path.insert(0,"tools");from sequence_archive import records;print(json.dumps(records()))'],{encoding:'utf8'}));

test('all archive values round-trip exactly through every finite integer view',()=>{
  for(const entry of entries) {
    const values=entry.terms.map(BigInt);
    for(let at=0;at<values.length;at+=128)for(const view of ['raw','difference','sum','mod','pairs']) {
      const rows=archiveWindow(entry,{start:entry.offset+at,size:Math.min(128,values.length-at),view,scale:'signed-log',mod:13}).rows;
      let sum=values.slice(0,at).reduce((a,b)=>a+b,0n);
      for(const [k,row]of rows.entries()) {
        const i=at+k;sum+=values[i];assert.equal(row.n,entry.offset+i);assert.equal(row.raw,String(values[i]));
        const v=view==='raw'?values[i]:view==='difference'?(i?values[i]-values[i-1]:null):view==='sum'?sum:((values[i]%13n)+13n)%13n;
        assert.equal(row.value,v===null?null:String(v));
        if(view==='pairs')assert.equal(row.next,i+1<values.length?String(((values[i+1]%13n)+13n)%13n):null);
      }
    }
  }
});

test('search respects KOM aliases, exact large values, family filters and actual offsets',()=>{
  assert.equal(canonicalID('kom-85'),'KOM085');
  assert.equal(searchEntries(entries,'id:kom85')[0].entry.id,'KOM085');
  const offset=entries.find(x=>x.id==='KOM067');
  const match=searchEntries([offset],offset.terms.slice(0,5).join(','))[0];assert.equal(match.reason,'Term pattern at n = 2–6');
  const big=entries.find(x=>x.id==='KOM004');assert.ok(big.terms.at(-1).length>100);
  const triangle=entries.find(x=>x.id==='KOM084');assert.match(searchEntries([triangle],triangle.terms.slice(0,5).join(','))[0].reason,/at j = 0–4/);
  assert.equal(searchEntries([big],big.terms.slice(-3).join(','))[0].termMatch.start,big.terms.length-3);
  assert.ok(searchEntries(entries,'name:Collatz -name:jump').every(x=>x.entry.id==='KOM079'));
});

test('window validation never extrapolates or fabricates a first difference',()=>{
  const entry=entries.find(x=>x.id==='KOM067');assert.throws(()=>archiveWindow(entry,{start:0}));assert.throws(()=>archiveWindow(entry,{size:128}));
  assert.throws(()=>archiveWindow(entry,{mod:0}));assert.throws(()=>archiveWindow(entry,{size:1.5}));
  assert.equal(archiveWindow(entry,{view:'difference',size:1}).rows[0].value,null);
  const rows=archiveWindow(entry,{start:3,size:2,view:'sum'}).rows;assert.equal(rows[0].value,String(BigInt(entry.terms[0])+BigInt(entry.terms[1])));
  assert.match(windowCSV(rows),/^n,a\(n\),plotted_value,following_residue\n3,/);
  assert.match(windowCSV(rows,'j'),/^j,a\(j\),/);
  assert.equal(new URL(archiveLink('https://example.test/sequence-archive.html?terms=private&junk=1',{query:'id:KOM067'})).search,'?query=id%3AKOM067');
});
