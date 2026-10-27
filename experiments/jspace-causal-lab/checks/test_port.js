const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),E=require(path.join(root,'app/engine.js'));
const meta=JSON.parse(fs.readFileSync(path.join(root,'app/weights.json'))),b=fs.readFileSync(path.join(root,'app/weights.bin'));
const store=E.load(meta,b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength));
const ref=JSON.parse(fs.readFileSync(path.join(__dirname,'pytorch_reference.json')));
let maxState=0,maxLogit=0,decisions=0,mismatch=[],scalarChecks=0;
const start=Date.now();
for(const r of ref.results){const d=new E.Dyad(store,meta,r.lineage,r.variant),s=ref.specs[r.specId],actual=E.runCase(d,s);
 for(let p=0;p<actual.length;p++){
  for(let a=0;a<2;a++)for(let j=0;j<64;j++){maxState=Math.max(maxState,Math.abs(actual[p].state[a][j]-r.phases[p].state[a][j]));scalarChecks++;}
  for(let q=0;q<4;q++)for(let a=0;a<2;a++){
   const x=actual[p].outputs[q][a],y=r.phases[p].outputs[q][a];
   for(const key of ['logits','privateLogits'])for(let k=0;k<4;k++){maxLogit=Math.max(maxLogit,Math.abs(x[key][k]-y[key][k]));scalarChecks++;}
   for(const key of ['prediction','privatePrediction']){decisions++;if(x[key]!==y[key])mismatch.push({lineage:r.lineage,variant:r.variant,spec:s.id,phase:p,query:q,agent:a,key,actual:x[key],reference:y[key]});}
  }
 }
}
const result={status:mismatch.length===0&&maxState<.001&&maxLogit<.002?'PASS':'FAIL',runs:ref.results.length,decisions,decision_mismatches:mismatch,max_state_abs_error:maxState,max_logit_abs_error:maxLogit,scalar_checks:scalarChecks,seconds:(Date.now()-start)/1000,environment:{node:process.version,torch:ref.torch},weight_sha256:crypto.createHash('sha256').update(b).digest('hex'),scope:'Float32 tensor outputs with JavaScript double-precision dot accumulation. Tested these sampled paths, not every input or device.'};
fs.writeFileSync(path.join(__dirname,'port_validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));if(result.status!=='PASS')process.exitCode=1;
