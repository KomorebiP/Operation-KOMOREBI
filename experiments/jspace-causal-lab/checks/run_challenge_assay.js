'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),E=require('../app/engine'),C=require('../app/causal_engine'),R=require('../app/refine_engine'),T=require('../app/challenge_engine');
const root=path.resolve(__dirname,'..'),meta=JSON.parse(fs.readFileSync(root+'/app/weights.json')),frames=JSON.parse(fs.readFileSync(root+'/app/frames.json')),buf=fs.readFileSync(root+'/app/weights.bin'),store=E.load(meta,buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength));
const hash=x=>crypto.createHash('sha256').update(fs.readFileSync(root+'/'+x)).digest('hex');
const contract={schema:'komorebi.challenge-assay.contract.v1.3',stage:'bounded development, not primary cohort',seed:271313,cases_per_lineage:32,lineages:['A','B'],variant:'calibrated',methods:['J','random','complement'],strength:1,agent:'both',offsets:[0,0,0],suffix:[],families:{commuting:'LRLR'.repeat(12),conjugation:'SLSR'.repeat(12)},checkpoints:[0,12,48],reloads:4,source_hashes:Object.fromEntries(['app/engine.js','app/causal_engine.js','app/refine_engine.js','app/challenge_engine.js','app/weights.bin','app/frames.json','checks/run_challenge_assay.js'].map(x=>[x,hash(x)])),freeze_time:new Date().toISOString(),interpretation:'Report reference failures, current donor consistency and factual/private recall separately. No per-case setting selection. Same histories reused across controls.'};
const loc=root+'/checks/robustness/';if(fs.existsSync(loc+'assay_contract.json'))throw Error('Refusing to overwrite existing assay evidence');fs.writeFileSync(loc+'assay_contract.json',JSON.stringify(contract,null,2));
const results=[],fixtures=[],start=Date.now();
for(const lineage of contract.lineages){const d=new E.Dyad(store,meta,lineage,contract.variant);for(let i=0;i<contract.cases_per_lineage;i++){
 const spec=T.caseSpec(contract.seed,i),exp=T.prepareCase(d,spec,i);
 for(const [family,program]of Object.entries(contract.families))for(const method of contract.methods){
  const settings={method,strength:1,agent:'both',offsets:[0,0,0],suffix:[]},p={program,points:contract.checkpoints,reloads:4},t=T.begin(d,exp,frames.lineages[lineage],settings,spec.world,spec.roles,spec.cue,p,'Input-native seeded case; projected branch artificial');T.run(t);
  results.push({lineage,index:i,family,method,spec,settings,initialValues:{factual:exp.factualValue,target:exp.targetValue},records:t.records,summary:T.summarize(t.records)});
  if(i<2&&family==='commuting'){
   const short=T.begin(d,exp,frames.lineages[lineage],settings,spec.world,spec.roles,spec.cue,{program:'LSRILRSI',points:[0,1,4,8],reloads:4},'PyTorch fixture source');T.run(short,true);fixtures.push({...T.cleanExport(short,{}),spec});
  }
 }
 if(i%8===7)console.log(JSON.stringify({lineage,cases:i+1,traces:results.length,seconds:(Date.now()-start)/1000}));
}}
const groups={};for(const x of results){const key=[x.lineage,x.family,x.method].join('/');if(!groups[key])groups[key]={};for(const r of x.records){const k=r.phase==='work'?'work'+r.work:'reload'+r.reloads,g=groups[key][k]??={agent_cases:0,exact_desired:[0,0,0],all_facts:[0,0,0],private_correct:[0,0,0],eligible:0,transferred:0,reference_errors:0,strict:0,consumer_eligible:0,consumer_transferred:0,new_fact_errors:0};
 for(let a=0;a<2;a++){g.agent_cases++;for(let b=0;b<3;b++){g.exact_desired[b]+=Number(r.outputs[b][0][a].prediction===r.reference[b][0]);g.all_facts[b]+=Number(r.memory[b].correct[a]===8);g.private_correct[b]+=Number(r.privateCorrect[b][a]);}if(['transferred','reverted','other_error'].includes(r.status[a]))g.eligible++;if(r.status[a]==='transferred')g.transferred++;if(r.status[a]==='reference_error')g.reference_errors++;g.strict+=Number(r.status[a]==='transferred'&&r.memory[1].correct[a]===8&&r.privateCorrect[1][a]);g.new_fact_errors+=r.memoryComparedToOriginal.lost[a];}
 for(const c of r.conditional)if(c.referenceCompetent){g.consumer_eligible++;g.consumer_transferred+=Number(c.transferred);}
}}
const finish={status:'COMPLETED',elapsed_seconds:(Date.now()-start)/1000,traces:results.length,unique_histories:contract.cases_per_lineage,model_lineages:2,source_hashes_unchanged:Object.entries(contract.source_hashes).every(([x,h])=>hash(x)===h),groups,note:'Cases use matching input histories across saved models, methods, families and checkpoints. Neither traces nor agent-case entries are independent training replications.'};
fs.writeFileSync(loc+'assay_raw.json',JSON.stringify(R.plain(results)));fs.writeFileSync(loc+'assay_summary.json',JSON.stringify(finish,null,2));fs.writeFileSync(loc+'numeric_fixtures.json',JSON.stringify(fixtures));console.log(JSON.stringify({status:finish.status,seconds:finish.elapsed_seconds,traces:finish.traces,source_hashes_unchanged:finish.source_hashes_unchanged}));
