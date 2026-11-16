// Replay generated record links through the actual exact browser family engine.
// Decimal coefficients remain strings across the JSON boundary.
import fs from 'node:fs';
import {generateFamily} from '../website/assets/sequence-family-core.mjs';

const payload=JSON.parse(fs.readFileSync(0,'utf8'));
if(!Array.isArray(payload.cases)||payload.cases.length>10000)throw Error('Invalid bounded link population.');
const results=[];
for(const example of payload.cases){
  try{
    const value=generateFamily(example.engine,example.parameters);
    if(value.terms.some(term=>typeof term!=='string'))throw Error('A coefficient crossed JSON without exact string encoding.');
    results.push({case_id:example.case_id,status:'generated',offset:value.offset,terms:value.terms,degrees:value.degrees,rational_terms:value.rationalTerms,parameters:value.params});
  }catch(error){
    results.push({case_id:example.case_id,status:'rejected',error:String(error.message).slice(0,500)});
  }
}
process.stdout.write(JSON.stringify({schema:1,cases:results.length,results})+'\n');
