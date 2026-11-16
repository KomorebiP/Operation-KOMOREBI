import {generateFamily,workedFamily,familyRepresentations} from './sequence-family-core.mjs';
import {identifyLocal} from './sequence-discovery-core.mjs';
import {modularCycle} from './sequence-modular-core.mjs';
self.onmessage=event=>{try{const d=event.data;let result;if(d.type==='family'){const sample=generateFamily(d.engine,d.params);result={...sample,worked:workedFamily(sample,d.position??3),formulas:familyRepresentations(sample)};}else if(d.type==='identify')result=identifyLocal(d.entries,d.text,{both:Boolean(d.both)});else if(d.type==='modular')result=modularCycle(d.params,d.modulus,d.maximum);else throw Error('Choose a supported research calculation.');self.postMessage({type:'result',result});}catch(error){self.postMessage({type:'error',message:error.message});}};
