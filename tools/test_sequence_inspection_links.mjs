import test from 'node:test';
import assert from 'node:assert/strict';
import {INSPECTION_WINDOW_SIZE,createInspectionLink,readInspectionLink} from '../website/assets/sequence-inspection-links.mjs';

const base='https://komorebip.github.io/Operation-KOMOREBI/sequence-workspace.html?old=1#notebook';
const entry={
  id:'KFOR-P-03-02',offset:2,terms:Array.from({length:24},(_,i)=>String(i*i)),
  formulas:Array.from({length:4},(_,i)=>({expression:'formula '+i}))
};

test('an exact view link is canonical, independently shareable and offset aware',()=>{
  assert.equal(INSPECTION_WINDOW_SIZE,8);
  const raw=createInspectionLink(base,entry,2,18);
  const url=new URL(raw);
  assert.equal(url.origin,'https://komorebip.github.io');
  assert.equal(url.pathname,'/Operation-KOMOREBI/sequence-library.html');
  assert.equal(url.hash,'#sl-results');
  assert.deepEqual([...url.searchParams.entries()],[
    ['q','id:KFOR-P-03-02'],['sl-record','KFOR-P-03-02'],
    ['sl-formula','2'],['sl-start','18']
  ]);
  assert.deepEqual(readInspectionLink(raw,entry,4),{variantIndex:2,startPosition:16});
  assert.equal(createInspectionLink(raw,entry,2,18),raw,'Repeated sharing has a stable URL');
});

test('partial last windows and flat triangle indices are preserved as stored indices',()=>{
  const triangle={id:'KFOR-TRI-P-03',offset:0,terms:Array(91).fill('123'),formulas:[{},{}]};
  assert.deepEqual(readInspectionLink(createInspectionLink(base,triangle,1,88),triangle,2),
    {variantIndex:1,startPosition:88});
  assert.throws(()=>createInspectionLink(base,triangle,0,91),RangeError);
  assert.throws(()=>createInspectionLink(base,triangle,0,89),RangeError);
});

test('wrong record, query, scope, duplicates and arbitrary formula indices are rejected',()=>{
  const valid=createInspectionLink(base,entry,1,10);
  const variants=[
    u=>u.searchParams.set('q','id:KFOR-H-02'),
    u=>u.searchParams.set('sl-record','KFOR-H-02'),
    u=>u.searchParams.set('scope','families'),
    u=>u.searchParams.set('sl-formula','99'),
    u=>u.searchParams.set('sl-formula','-1'),
    u=>u.searchParams.set('sl-formula','1.5'),
    u=>u.searchParams.set('sl-formula','01'),
    u=>u.searchParams.set('sl-start','3'),
    u=>u.searchParams.set('sl-start','1'),
    u=>u.searchParams.set('sl-start','26'),
    u=>u.searchParams.set('sl-start','9999999999999999999999'),
    u=>u.searchParams.append('q','id:KFOR-P-03-02'),
    u=>u.searchParams.append('sl-record','KFOR-P-03-02'),
    u=>u.searchParams.append('sl-formula','1'),
    u=>u.searchParams.append('sl-start','10')
  ];
  for(const mutate of variants){
    const url=new URL(valid);mutate(url);
    assert.equal(readInspectionLink(url.href,entry,4),null,url.href);
  }
  assert.equal(readInspectionLink(valid,entry,1),null,'Unavailable variants must not be selected');
  assert.equal(readInspectionLink('not a URL',entry,4),null);
  const missing=new URL(valid);missing.searchParams.delete('sl-start');
  assert.equal(readInspectionLink(missing.href,entry,4),null);
});

test('building an invalid or unaligned inspection link fails before copying',()=>{
  for(const [selected,start] of [[-1,2],[4,2],[1,-1],[1,3],[1,26],[0,1000],[0,2.5]]){
    assert.throws(()=>createInspectionLink(base,entry,selected,start),RangeError);
  }
  assert.throws(()=>createInspectionLink(base,{...entry,offset:1.5},0,2),RangeError);
  assert.throws(()=>createInspectionLink(base,{...entry,terms:[]},0,2),RangeError);
});
