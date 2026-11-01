// Machine-readable interface for independent numerical checking; no saved results are trusted.
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
(async()=>{
  const {experiment,BASES}=await import(pathToFileURL(path.join(__dirname,'../website/assets/signal-lab-core.mjs')));
  const input=fs.readFileSync(0,'utf8');
  if(input.length>1048576)throw new RangeError('Audit request too large');
  const configurations=JSON.parse(input);
  if(!Array.isArray(configurations)||configurations.length>512)throw new RangeError('Audit case limit exceeded');
  process.stdout.write(JSON.stringify(configurations.map(config=>{
    const e=experiment(config);
    return {config:e.config,reference:e.reference,observed:e.observed,noiseEnergy:e.noiseEnergy,
      analyses:Object.fromEntries(BASES.map(b=>{const a=e.analyses[b];return [b,{values:a.values,weights:a.weights,order:a.order,curve:a.curve,reconstruction:a.reconstruction,bestBudget:a.bestBudget}];}))};
  })));
})().catch(error=>{console.error(error);process.exitCode=1;});
