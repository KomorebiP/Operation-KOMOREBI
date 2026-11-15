import test from 'node:test';import assert from 'node:assert/strict';
import {PLOT_DEFAULTS,PLOT_PALETTES,plotColors,plotTheme,contrastRatio,validateAppearance} from '../website/assets/sequence-plot-options.mjs';
import {readPageTheme,effectiveDark,PAGE_THEME_KEY} from '../website/assets/sequence-reading-theme.mjs';
import {searchEntries} from '../website/assets/sequence-atlas-search.mjs';
test('all built-in plot colors contrast with every supported background',()=>{
  assert.equal(PLOT_DEFAULTS.theme,'white');assert.equal(PLOT_DEFAULTS.opacity,'1');
  for(const palette of Object.keys(PLOT_PALETTES))for(const theme of ['paper','white','night'])for(const reverse of ['normal','reverse']){
    const state=validateAppearance({palette,theme,reverse});for(const color of plotColors(state))assert.ok(contrastRatio(color,plotTheme(state).background)>=4.5,{palette,theme,color});
    assert.ok(contrastRatio(plotTheme(state).foreground,plotTheme(state).background)>=12);
  }
  for(const theme of ['paper','white','night']){const state=validateAppearance({palette:'custom',theme,custom:'#d9dfd4',secondary:'#87988b'});assert.deepEqual(plotColors(state).slice(0,2),['#d9dfd4','#87988b']);}
});
test('page reading preferences are explicit, robust and independent of the OS default',()=>{
  assert.equal(readPageTheme({getItem:()=>null}),'light');assert.equal(readPageTheme({getItem:()=>{throw Error('denied')}}),'light');assert.equal(readPageTheme({getItem:()=>'<script>'}),'light');
  for(const choice of ['light','dark','system'])assert.equal(readPageTheme({getItem:key=>{assert.equal(key,PAGE_THEME_KEY);return choice;}}),choice);
  assert.equal(effectiveDark('light',true),false);assert.equal(effectiveDark('dark',false),true);assert.equal(effectiveDark('system',true),true);assert.equal(effectiveDark('system',false),false);
});
test('polynomial columns have an exact, normalized search field',()=>{
  const entry={id:'KFOR-P-03-02',title:'Secancy parameter column',formula:'[r^2] P_(3,n)(r)',recurrence:'',tags:['research-derived'],kind:'secancy parameter column',status:'Research-derived',N:3,k:2,offset:2,terms:['10','756']};
  assert.equal(searchEntries([entry],'tag:research-derived n:3 k:02').length,1);assert.equal(searchEntries([entry],'k:3').length,0);assert.match(searchEntries([entry],'10,756')[0].reason,/2–3/);
});
