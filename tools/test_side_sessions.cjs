const assert = require('node:assert/strict');
const api = require('../website/assets/side-reader-sessions.js');
const base = 'https://example.test/Operation-KOMOREBI/';
const data = {pages:{'read/one.html':'One','read/two.html':'Two'}};
const original = {schema:1,left:'read/one.html#L37',right:'read/two.html',view:'right',width:60,focus:true,
  send:{left:true,right:false},updatedAt:12345,
  positions:{left:{url:'read/one.html#L37',html:{anchor:'L37',offset:48,x:0,y:2071,ratio:.25,progress:.2,width:600}},
    right:{url:'read/two.html',html:{anchor:'',offset:0,x:0,y:600,ratio:.5,progress:0,width:600},pdf:'#page=6&zoom=125,0,327',rotation:90}}};
const session = api.snapshot(original,base,data);
assert.equal(session.left,'read/one.html#L37');
assert.equal(session.positions.left.html.y,2071);
assert.equal(session.positions.left.html.anchor,'L37');
assert.equal(session.positions.right.pdf,'page=6&zoom=125,0,327');
assert.equal(session.positions.right.rotation,90);
assert.deepEqual(session.send,{left:true,right:false});
assert.equal(session.width,60);assert.equal(session.view,'right');assert.equal(session.focus,true);
assert.equal(original.positions.right.pdf,'#page=6&zoom=125,0,327','Normalization leaves the input untouched');
for (const target of ['https://evil.test/read/one.html','side-by-side.html','missing.html','../read/one.html']) {
  assert.equal(api.snapshot({...original,left:target},base,data),null,target);
}
const unbound=api.snapshot({...original,positions:{left:{...original.positions.left,url:'read/two.html'}}},base,data);
assert.equal(unbound.positions.left,null,'A position cannot be transferred to another document');
const badNumbers=api.snapshot({...original,positions:{left:{url:original.left,html:{anchor:'L37',y:Infinity,ratio:10,width:-3}}}},base,data);
assert.equal(badNumbers.positions.left.html.y,0);assert.equal(badNumbers.positions.left.html.ratio,0);
for (const hash of ['page=0','page=-1','page=1&page=2','page=1&zoom=Infinity','page=1&zoom=0',
  'page=1&zoom=150,garbage,2','page=1&zoom=150,1','page=1&search=private','javascript:alert(1)',
  'page=1&zoom=auto&zoom=200','page=9999999']) assert.equal(api.pdfHash(hash),null,hash);
assert.equal(api.pdfHash('#page=18&zoom=page-width,0,-4'),'page=18&zoom=page-width,0,-4');
assert.equal(api.pdfHash('page=2'),'page=2');
let current=api.library(null);
current=api.withBookmark(current,'  Papers I and II  ',session);
assert.equal(current.bookmarks.length,1);assert.equal(current.bookmarks[0].name,'Papers I and II');
const revised={...session,width:35};
current=api.withBookmark(current,'Papers I and II',revised);
assert.equal(current.bookmarks.length,1);assert.equal(current.bookmarks[0].session.width,35,'An existing name updates its bookmark');
for (const name of ['', ' '.repeat(3), 'x'.repeat(81), 'two\nlines']) assert.throws(()=>api.withBookmark(current,name,session));
const full={...current,bookmarks:Array.from({length:50},(_,n)=>({name:'Session '+n,session}))};
assert.throws(()=>api.withBookmark(full,'Another',session));
assert.equal(api.withBookmark(full,'Session 3',revised).bookmarks.length,50);
for (const raw of ['{broken','x'.repeat(512001),'null','{"schema":9}']) assert.deepEqual(api.library(raw),{schema:1,remember:true,last:null,bookmarks:[]});
const unavailable=api.library(JSON.stringify({schema:1,remember:false,last:session,bookmarks:[{name:'Old edition',session:{...session,left:'read/old-edition.html'}}]}));
assert.equal(unavailable.bookmarks.length,1,'Unavailable editions remain listed until explicitly deleted');
assert.equal(api.snapshot(unavailable.bookmarks[0].session,base,data),null);
assert.equal(unavailable.remember,false);
const values=new Map(),storage={setItem:(key,value)=>values.set(key,value)};
assert.equal(api.writeLibrary(storage,'reader-key',{...current,last:session}),true);
const recovered=api.library(values.get('reader-key'));
assert.deepEqual(api.snapshot(recovered.last,base,data),session,'Saved session round trip retains passages, positions, PDF zoom and layout');
assert.equal(api.writeLibrary({setItem(){throw Error('Quota exceeded');}},'reader-key',current),false);
assert.equal(api.writeLibrary(undefined,'reader-key',current),false);
assert.deepEqual(api.initialSession(recovered,base+'side-by-side.html',base,data),session);
for (const query of ['?left=read/one.html','?work=paper-i','?right=read/two.html','?width=35']) {
  assert.equal(api.initialSession(recovered,base+'side-by-side.html'+query,base,data),null,'An explicit link keeps its requested documents');
}
assert.equal(api.initialSession({...recovered,remember:false},base+'side-by-side.html',base,data),null);
const samePair=new URL(base+'side-by-side.html');
samePair.searchParams.set('left',session.left);samePair.searchParams.set('right',session.right);
samePair.searchParams.set('view',session.view);samePair.searchParams.set('width',session.width);
assert.deepEqual(api.initialSession(recovered,samePair.href,base,data,'reload'),session,'Refreshing the same pair restores its reading positions');
assert.equal(api.initialSession(recovered,samePair.href,base,data,'navigate'),null,'A newly followed link opens its stated passages');
samePair.searchParams.set('right','read/one.html');
assert.equal(api.initialSession(recovered,samePair.href,base,data,'reload'),null,'Reloading a different requested pair cannot restore the old one');
console.log('PASS: saved reading positions, PDF state, safe targets, bookmark updates, storage failure and explicit-link priority');
