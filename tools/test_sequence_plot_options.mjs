import test from 'node:test';
import assert from 'node:assert/strict';
import {PLOT_DEFAULTS,validateAppearance,readAppearance,appearanceLink,plotColors,plotHeight,showIndexLabel,mergePlotLabels} from '../website/assets/sequence-plot-options.mjs';
import {archiveLink,archiveWindow,moveArchiveWindow,triangleWindow,archivePreset} from '../website/assets/sequence-archive-core.mjs';
import {execFileSync} from 'node:child_process';

const entries=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','-c','import sys,json;sys.path.insert(0,"tools");from sequence_archive import records;print(json.dumps(records()))'],{encoding:'utf8'}));

test('appearance accepts only bounded presentation choices and keeps source data separate',()=>{
  assert.deepEqual(validateAppearance(),PLOT_DEFAULTS);
  for(const options of [{point:100},{width:0},{height:'huge'},{palette:'<script>'},{custom:'red'},{baseline:'arbitrary'},{labels:'unlimited'}])assert.throws(()=>validateAppearance(options));
  const custom=validateAppearance({palette:'custom',custom:'#ABCDEF',point:'8',height:'tall'});assert.equal(plotColors(custom)[0],'#abcdef');assert.equal(plotHeight(320,custom),520);
  assert.ok(plotHeight(1200,custom)>plotHeight(1200,PLOT_DEFAULTS));
  assert.equal(showIndexLabel(0,276,{...PLOT_DEFAULTS,labels:'ends'},300),true);
  assert.equal(showIndexLabel(275,276,{...PLOT_DEFAULTS,labels:'ends'},300),true);
  assert.equal(showIndexLabel(12,276,{...PLOT_DEFAULTS,labels:'ends'},300),false);
  const count=Array.from({length:276},(_,n)=>showIndexLabel(n,276,{...PLOT_DEFAULTS,labels:'sparse'},300)).filter(Boolean).length;assert.ok(count<=7);
});

test('view links fully override recipient preferences and tolerate unavailable or corrupt storage',()=>{
  const saved={getItem:()=>JSON.stringify({schema:1,appearance:{palette:'ocean',point:'8'}})};
  assert.equal(readAppearance('https://example.test/a',saved).state.palette,'ocean');
  const href=appearanceLink('https://example.test/a?start=2',PLOT_DEFAULTS);
  assert.deepEqual(readAppearance(href,saved).state,PLOT_DEFAULTS);assert.equal(new URL(href).searchParams.get('start'),'2');
  assert.deepEqual(readAppearance('https://example.test/a',{getItem:()=>{throw Error('Denied')}}).state,PLOT_DEFAULTS);
  assert.deepEqual(readAppearance('https://example.test/a',{getItem:()=>'{invalid'}).state,PLOT_DEFAULTS);
  assert.deepEqual(readAppearance('https://example.test/a?plot-palette=bad',saved).state,PLOT_DEFAULTS);
  const safe=appearanceLink(archiveLink('https://example.test/a?terms=private',{start:2,size:4},'plot'),{...PLOT_DEFAULTS,palette:'ocean'});assert.equal(new URL(safe).searchParams.has('terms'),false);
});

test('coincident plotted labels combine without changing the indexed samples',()=>{
  const input=[{x:65,y:120,text:'0'},{x:65,y:120,text:'31'},{x:65,y:120,text:'0'},{x:100,y:90,text:'7'}];
  assert.deepEqual(mergePlotLabels(input).map(row=>row.text),['0, 31','7']);assert.equal(input.length,4);
  const combined=mergePlotLabels(Array.from({length:12},(_,n)=>({x:1,y:1,text:String(n)})))[0];assert.equal(combined.text,'0 +11');assert.equal(combined.full.split(', ').length,12);
});

test('all 90 finite windows pan and zoom within original offsets without changing a term',()=>{
  for(const entry of entries){
    const fitted=moveArchiveWindow(entry,archiveWindow(entry).state,'all');assert.equal(fitted.start,entry.offset);assert.equal(fitted.size,entry.terms.length);
    assert.deepEqual(archiveWindow(entry,fitted).rows.map(row=>row.raw),entry.terms);
    for(const size of [...new Set([1,2,Math.min(32,entry.terms.length)])])for(const start of [...new Set([entry.offset,entry.offset+entry.terms.length-size])]){
      const state={...fitted,start,size};
      for(const action of ['previous','next','in','out','all']){
        const next=moveArchiveWindow(entry,state,action),rows=archiveWindow(entry,next).rows;
        assert.ok(next.start>=entry.offset&&next.start+next.size<=entry.offset+entry.terms.length);
        assert.deepEqual(rows.map(row=>row.raw),entry.terms.slice(next.start-entry.offset,next.start-entry.offset+next.size));
      }
    }
    for(const name of ['growth','residues','changes','profile'])assert.deepEqual(archiveWindow(entry,{...fitted,...archivePreset(entry,name)}).rows.map(row=>row.raw),entry.terms);
  }
});

test('each of the 23 triangle-row windows agrees with independently generated polynomial coefficients',()=>{
  const entry=entries.find(x=>x.id==='KOM084');
  const rows=JSON.parse(execFileSync(process.env.PYTHON||'python',['-B','-c','import sys,json;sys.path.insert(0,"research/sequence-archive");import generate_candidates as g;print(json.dumps([[str(x) for x in row] for row in g.ladder_poly(23)]))'],{encoding:'utf8'}));
  for(let n=0;n<23;n++){const options=triangleWindow(entry,n),actual=archiveWindow(entry,options).rows;assert.equal(options.start,n*(n+1)/2);assert.deepEqual(actual.map(row=>row.raw),rows[n]);}
  for(const n of [-1,1.5,23,''])assert.throws(()=>triangleWindow(entry,n));
  assert.throws(()=>triangleWindow(entries[0],2));
});
