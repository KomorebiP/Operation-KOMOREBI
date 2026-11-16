// Exact JavaScript execution; the independent Python oracle checks the output.
import {sequenceTransfer,transferAnchor} from '../website/assets/sequence-transfer-core.mjs';
import {generate} from '../website/assets/sequence-atlas-core.mjs';
import process from 'node:process';
let input='';for await(const chunk of process.stdin)input+=chunk;
const data=JSON.parse(input),results=[];
for(const entry of data.entries){
  if(entry.collection==='atlas'){
    const actual=generate(entry,entry.terms.length).map(String);
    if(JSON.stringify(actual)!==JSON.stringify(entry.terms))throw Error('Curated generator mismatch '+entry.id);
  }
  if(entry.triangle||entry.id==='KOM084'||entry.index_symbol==='j'){results.push({id:entry.id,excluded:'coefficient table'});continue;}
  try{const anchor=transferAnchor(entry),count=Math.min(12,anchor.available,data.source.terms.length);results.push({id:entry.id,...sequenceTransfer(data.source,entry,count)});}
  catch(error){if(!/no stored nonzero anchor/.test(error.message))throw error;results.push({id:entry.id,excluded:'no stored nonzero anchor'});}
}
process.stdout.write(JSON.stringify(results));
