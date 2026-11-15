import test from 'node:test';
import assert from 'node:assert/strict';
import {workspaceForURL} from '../website/assets/sequence-atlas-interface.mjs';
test('workspace restoration retains query-selected views when the URL has no fragment',()=>{
  for(const [suffix,expected]of [
    ['','find'],['?q=bell','find'],['?sequence=KSEQ-000025','explorer'],['?seq=KSEQ-000007','explorer'],
    ['?compare=KSEQ-000025','explorer'],['?view=mod','explorer'],['?discover=0,1,4,9,16,25','discover'],
    ['?discover=0,1,4,9,16,25#find','find'],['?sequence=KSEQ-000025#discover','discover'],
    ['#catalogue','catalogue'],['#sa-results-title','sa-results-title'],
    ['?index-query=bell','catalogue'],['?index-order=id','catalogue'],['?index-connected=1','catalogue'],
  ])assert.equal(workspaceForURL('https://example.test/sequences.html'+suffix),expected,suffix);
});
