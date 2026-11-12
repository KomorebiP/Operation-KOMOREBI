const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname,'../website/assets/smith-book-redirect.js'),'utf8');

function destination(page, anchor, hash) {
  const prefix = page.startsWith('collection/') ? '../../read/smith-chart/' : '';
  let result;
  vm.runInNewContext(source,{URL,document:{currentScript:{dataset:{bookTarget:prefix+'research.html#'+anchor,bookPrefix:anchor}}},
    location:{href:'https://komorebip.github.io/Operation-KOMOREBI/'+page,hash,replace:value=>result=value}});
  return result;
}

test('old chapter and supplement bookmarks lead to canonical section anchors',()=>{
  for(const [page,anchor,fragment] of [
    ['read/smith-chart/exact-six.html','exact-six','result'],
    ['read/smith-chart/families.html','families','2-exact-identity-degree-and-coprimality'],
    ['collection/demonstrations/SMITH_CHART.html','companion-guide','cyclic-reachability'],
    ['collection/demonstrations/SMITH_FIRST_ORDER_RL.html','one-inductor','the-affine-reflection-function'],
    ['collection/demonstrations/SMITH_SINGULAR_COMPLETION.html','singular-completion','the-range-condition-at-a-singular-matrix']]) {
    assert.equal(destination(page,anchor,'#'+fragment),'https://komorebip.github.io/Operation-KOMOREBI/read/smith-chart/research.html#'+anchor+'--'+fragment);
  }
});
test('hub sections and malformed hashes have safe canonical destinations',()=>{
  const page='read/smith-chart/continuation.html';
  assert.ok(destination(page,'current-results','#fresh-executable-evidence').endsWith('research.html#source-ledger'));
  assert.ok(destination(page,'current-results','#two-different-targets').endsWith('research.html#exact-six'));
  assert.ok(destination(page,'current-results','#%zz').endsWith('research.html#current-results'));
});
