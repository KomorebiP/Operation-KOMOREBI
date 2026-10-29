const assert = require('node:assert/strict');
const api = require('../website/assets/side-reader-core.js');
const base = 'https://example.test/Operation-KOMOREBI/';
const data = {
  pages: {'read/one.html':'One', 'read/two.html':'Two', 'claims.html':'Claims', 'collection/examples/a.html':'Example'},
  works: [{id:'one',left:'read/one.html',right:'claims.html#one'}, {id:'two',left:'read/two.html',right:'claims.html#two'}],
  entries: [
    {url:'read/one.html',title:'Café operator',kind:'Papers and source',works:['one'],text:'seed-rank'},
    {url:'read/two.html',title:'The proof',kind:'Written proofs',works:['two'],text:'operator reconstruction'},
    {url:'collection/examples/a.html',title:'An example',kind:'Examples',works:['one','two'],text:'reconstruction'}
  ]
};
assert.equal(api.canonical('read/one.html#L12',base,data.pages),'read/one.html#L12');
assert.equal(api.canonical(base+'read/one.html?reading-pane=left&q=x#L12',base,data.pages),'read/one.html?q=x#L12');
for (const value of ['https://evil.test/read/one.html','//evil.test/read/one.html','javascript:alert(1)','data:text/html,x',
  '../read/one.html','/Operation-KOMOREBI-other/read/one.html','read\\one.html','side-by-side.html','missing.html',
  'https://name:secret@example.test/Operation-KOMOREBI/read/one.html','read/%ZZ.html','toString','__proto__',null]) {
  assert.equal(api.canonical(value,base,data.pages),null,String(value));
}
assert.equal(api.filter(data.entries,'cafe seed rank','one','').length,1);
assert.equal(api.filter(data.entries,'reconstruction','two','Examples').length,1);
assert.equal(api.filter(data.entries,'proof','one','').length,0);
assert.equal(api.filter(data.entries,'','two','').length,2);
let state=api.parsePair(base+'side-by-side.html?left=read%2Ftwo.html%23L13',base,data,false);
assert.equal(state.right,'claims.html#two','The companion follows the originating work');
assert.equal(state.left,'read/two.html#L13');
state.width=65;state.view='right';
let restored=api.parsePair(api.pairURL(base,state),base,data,false);
assert.deepEqual(restored,state,'Share link restores both panes, anchor, layout and width');
assert.equal(api.parsePair(base+'side-by-side.html',base,data,true).view,'left');
state=api.parsePair(base+'side-by-side.html?left=https%3A%2F%2Fevil.test%2F&right=side-by-side.html&width=0&view=hidden',base,data,false);
assert.equal(state.left,'read/one.html');assert.equal(state.right,'claims.html#one');assert.equal(state.invalid,true);
assert.equal(state.width,50);assert.equal(state.view,'both');
console.log('PASS: local target restrictions, search, work association, mobile defaults and pair-link round trip');
