const assert=require('node:assert/strict');
const {rank,search}=require('../website/assets/notation-search.js');
const context={work:'paper-i',excerpt:'Packet system',source_url:'read/paper-i/table.html#L67'};
const entry=(tex,names,extra={})=>({tex,names,aliases:names.join(' '),work:'paper-i',context:0,kind:'notation-table',...extra});
const alpha=entry('\\alpha',['α','alpha']);
const packet=entry('\\Pcal',['Pcal','P']);
const subscript=entry('P_\\alpha',['P_α','P_alpha'],{aliases:'P_α P_alpha alpha'});
assert.equal(rank(alpha,context,'alpha',false),1);
assert.equal(rank(alpha,context,'α',false),1);
assert.equal(rank(alpha,context,'\\alpha',true),0);
assert.equal(rank(alpha,context,'alpha',true),-1);
assert.equal(rank(entry('\\Phi',['Φ','Phi']),context,'\\phi',false),-1);
assert.equal(rank(packet,context,'a',false),-1); // No single-letter matches in prose.
assert.ok(rank(subscript,context,'alpha',false)>rank(alpha,context,'alpha',false));
const data={contexts:[context],entries:[alpha,packet,subscript]};
let result=search(data,{query:'packet'});
assert.equal(result.groups.length,1);
assert.equal(result.count,3);
assert.equal(result.groups[0].entries.length,3); // No entries discarded when grouped.
data.contexts.push({...context,work:'paper-ii'});
data.entries.push(entry('\\Pcal',['Pcal','P'],{work:'paper-ii',context:1}));
assert.equal(search(data,{query:'packet'}).groups.length,2);
assert.equal(search(data,{query:'packet',work:'paper-ii'}).count,1);
assert.equal(search(data,{query:'packet',kind:'use'}).count,0);
assert.equal(search(data,{query:'unfindable'}).count,0);
assert.equal(search(data,{query:'alpha'}).groups[0].entries[0].tex,'\\alpha');
assert.equal(search(data,{query:'\\alpha',exact:true}).count,1);
console.log('PASS: symbol ranking, case, short queries, grouping, filters and retained entries');
