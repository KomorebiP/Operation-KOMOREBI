import test from 'node:test';import assert from 'node:assert/strict';
import {PLOT_DEFAULTS,PLOT_PALETTES,plotColors,plotTheme,contrastRatio,validateAppearance,appearanceLink,readAppearance,pagePalette} from '../website/assets/sequence-plot-options.mjs';
import {readPageTheme,effectiveDark,PAGE_THEME_KEY,readPageScheme,PAGE_SCHEME_KEY} from '../website/assets/sequence-reading-theme.mjs';
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

test('neutral schemes are the default and monochrome plots contain only gray channels',()=>{
  assert.equal(PLOT_DEFAULTS.palette,'site');assert.equal(readPageScheme({getItem:()=>null}),'green');assert.equal(readPageScheme({getItem:()=>{throw Error('denied')}}),'green');assert.equal(readPageScheme({getItem:()=>'<script>'}),'green');
  assert.equal(readPageScheme({getItem:key=>{assert.equal(key,PAGE_SCHEME_KEY);return 'mono';}}),'mono');assert.equal(pagePalette('green'),'green');assert.equal(pagePalette('mono'),'ink');
  for(const theme of ['white','night'])for(const color of plotColors({...PLOT_DEFAULTS,theme},'mono')){const c=color.slice(1).match(/../g);assert.equal(c[0],c[1]);assert.equal(c[1],c[2]);assert.ok(contrastRatio(color,plotTheme({theme}).background)>=4.5);}
  assert.deepEqual(plotColors(PLOT_DEFAULTS,'green'),plotColors({...PLOT_DEFAULTS,palette:'green'}));
});
test('shared plot links capture rendered colors rather than the recipient page preference',()=>{
  const href=appearanceLink('https://example.test/',PLOT_DEFAULTS),state=readAppearance(href).state;assert.equal(state.palette,'green');assert.deepEqual(plotColors(state,'mono'),plotColors(PLOT_DEFAULTS,'green'));
  const mono=readAppearance(appearanceLink('https://example.test/',{...PLOT_DEFAULTS,palette:'ink'})).state;assert.equal(mono.palette,'ink');
});
