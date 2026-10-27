"""Train, freeze, compose, and score learned primitive kernels. Komorebi P."""
import argparse,copy,hashlib,json,time
from pathlib import Path
import numpy as np
from primitive_environment import CHANNELS,dataset,primitive_cases,outcomes,higher_targets,higher_names,world_values
from primitive_model import Kernels,Catalog
from executor import Executor
from primitive_workspace import PrimitiveWorkspace
from workspace import Workspace
from geometry import BehaviorGeometry

CONFIG={'author':'Komorebi P.','seeds':[0,1,2],'training_seed':81101,'validation_seed':91802,
        'training_examples_per_channel':2048,'validation_examples_per_channel':1024,
        'steps':6000,'batch':256,'width':12,'parameters_per_channel':51,
        'primitive_tolerance':1e-6,'program_max_calls':3,'workspace_cases':144,
        'test_seed':93011,'old_core_weights_updated':False}

def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False))
def hashfile(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def train(folder):
    folder.mkdir(parents=True,exist_ok=True);(folder/'models').mkdir(exist_ok=True)
    write(folder/'training_freeze.json',{'config':CONFIG,'sources':{p.name:hashfile(p) for p in sorted(Path('.').glob('*.py'))}})
    x,y=dataset(CONFIG['training_seed'],CONFIG['training_examples_per_channel'])
    v,t=dataset(CONFIG['validation_seed'],CONFIG['validation_examples_per_channel'])
    np.savez_compressed(folder/'operation_observations.npz',train_x=x,train_y=y,validation_x=v,validation_y=t)
    receipts=[]
    for seed in CONFIG['seeds']:
        start=time.perf_counter()
        for activation in ['tanh','square']:
            m=Kernels(CHANNELS,seed=seed,width=CONFIG['width'],activation=activation)
            m.save(folder/f'models/untrained_{activation}_{seed}.npz')
            random=copy.deepcopy(m);ranks=random.refit_readout(x,y)
            random.save(folder/f'models/random_readout_{activation}_{seed}.npz')
            trace=m.train(x,y,CONFIG['steps'],CONFIG['batch'],seed=22000+seed)
            m.save(folder/f'models/before_refit_{activation}_{seed}.npz')
            before=np.max(abs(m.predict(v)-t),axis=1).tolist();m.refit_readout(x,y)
            m.save(folder/f'models/trained_{activation}_{seed}.npz')
            catalog=Catalog.validate(m,v,t,CONFIG['primitive_tolerance'])
            receipts.append({'seed':seed,'activation':activation,'trace':trace,'before_refit_validation_max':before,
                             'catalog':catalog.to_dict(),'random_feature_readout_rank':ranks})
            write(folder/f'catalog_{activation}_{seed}.json',catalog.to_dict())
            print(f'seed {seed}, {activation}: accepted {catalog.accepted}',flush=True)
        shuffled=Kernels(CHANNELS,seed=seed,width=CONFIG['width'],activation='square')
        rng=np.random.default_rng(55000+seed);wrong=np.stack([row[rng.permutation(len(x))] for row in y])
        shuffled.train(x,wrong,CONFIG['steps'],CONFIG['batch'],seed=22000+seed);shuffled.refit_readout(x,wrong)
        shuffled.save(folder/f'models/shuffled_square_{seed}.npz')
        write(folder/f'catalog_shuffled_{seed}.json',Catalog.validate(shuffled,v,t).to_dict())
        print(f'seed {seed}: training complete in {time.perf_counter()-start:.1f}s',flush=True)
    write(folder/'training_receipts.json',receipts)
    write(folder/'model_freeze.json',{p.name:hashfile(p) for p in sorted((folder/'models').glob('*.npz'))})

def make_catalog(folder,seed=0):
    m=Kernels.load(folder/f'models/trained_square_{seed}.npz')
    c=json.loads((folder/f'catalog_square_{seed}.json').read_text())
    return Catalog(m,c['accepted'],c['receipt'])

def predict(folder):
    model_hashes=json.loads((folder/'model_freeze.json').read_text())
    for name,h in model_hashes.items():assert hashfile(folder/'models'/name)==h
    cases=primitive_cases(CONFIG['test_seed']);np.savez_compressed(folder/'primitive_test_inputs.npz',**cases)
    primitive=[];compositions=[];libraries=[];deep=[];workspace_predictions=[];tasks=[];audits=[]
    for seed in CONFIG['seeds']:
        models={p.stem.rsplit('_',1)[0]:Kernels.load(p) for p in sorted((folder/'models').glob(f'*_{seed}.npz'))}
        for name,m in models.items():
            for cohort,x in cases.items():
                primitive.append({'seed':seed,'model':name,'cohort':cohort,'predictions':m.predict(x).tolist()})
        catalog=make_catalog(folder,seed);executor=Executor(catalog)
        demo_xy=np.random.default_rng(70100+seed).uniform(-1.5,1.5,(24,2));target=higher_targets(demo_xy)
        programs=executor.enumerate(demo_xy,max_calls=CONFIG['program_max_calls'])
        all_values=np.stack([p['values'] for p in programs]);learned=[]
        for i in range(9):
            errors=np.max(abs(all_values-target[i]),axis=1);matches=np.flatnonzero(errors<=1e-6)
            if not len(matches):raise RuntimeError('No neural-call composition fits development behavior.')
            selected=programs[int(matches[0])];expr=selected['expression']
            validation_xy=np.random.default_rng(70900+seed*10+i).uniform(-1.8,1.8,(16,2))
            validation_target=higher_targets(validation_xy)[i]
            validation_error=float(np.max(abs(executor.evaluate(expr,validation_xy)-validation_target)))
            if validation_error>1e-6:raise RuntimeError('Program promotion failed.')
            learned.append({'expression':expr,'calls':selected['calls'],'source':f'composition_development_{seed}_{i}',
                            'demo_xy':demo_xy.tolist(),'demo_outputs':target[i].tolist(),
                            'validation_xy':validation_xy.tolist(),'validation_outputs':validation_target.tolist(),
                            'validation_error':validation_error,'kernel_identity':catalog.kernels.identity()})
        libraries.append({'seed':seed,'enumerated_programs':len(programs),'entries':learned})
        # Same saved ASTs, alternative learned or control kernels. These are
        # explicitly evaluation-only substitutions, not validated deployments.
        for name,m in models.items():
            alternative=Executor(Catalog(m,catalog.accepted,{'status':'evaluation_only_substitution'}))
            for cohort,x in cases.items():
                predictions=np.stack([alternative.evaluate(r['expression'],x) for r in learned])
                compositions.append({'seed':seed,'model':name,'cohort':cohort,'predictions':predictions.tolist()})
        # Find the learned channel behaving like the already fitted two-input
        # signal from demonstrations, without assigning a product opcode.
        target_pair=outcomes(demo_xy)[1]
        pair_program=executor.discover(demo_xy,target_pair,max_calls=1)['expression']
        op=pair_program[1];start=np.random.default_rng(78700).uniform(.75,1.25,128)
        for name in ['trained_square','random_readout_square','trained_tanh','untrained_square']:
            m=models[name];state=start.copy()
            for depth in range(1,7):
                state=m.call(op,state,state)
                deep.append({'seed':seed,'model':name,'depth':depth,'predictions':state.tolist(),'inputs':start.tolist()})
        core=Workspace.load('baseline/model_0.npz');geometry=BehaviorGeometry.from_dict(json.loads(Path('baseline/geometry_0.json').read_text()))
        rng=np.random.default_rng(87011);adapter_x=rng.uniform(-4,4,(64,2))
        adapter_y=np.stack([adapter_x[:,0],adapter_x[:,0]-adapter_x[:,1],adapter_x[:,0]+adapter_x[:,1]],axis=1)
        adapter=np.linalg.lstsq(adapter_x,adapter_y,rcond=None)[0].T
        bank=PrimitiveWorkspace(core,geometry,executor,adapter)
        old=json.loads(Path('baseline/behavior_workspaces.json').read_text())
        for name,slot in old['slots'].items():bank.add(name,slot['versions'][slot['current']]['state'])
        originals=copy.deepcopy(bank.slots);old_values={name:bank.read(name,cases['in_range'][:32]).copy() for name in bank.slots}
        for i in range(CONFIG['workspace_cases']):
            rng=np.random.default_rng(88100+i);base=rng.integers(-2,3,6);higher=i%9;amp=float(rng.choice([-2,-1,1,2]))
            xy=rng.uniform(-1.8,1.8,(24,2));y=world_values(base,higher,amp,xy)
            q1=rng.uniform(-2,2,(32,2));q2=rng.uniform(-2,2,(32,2));wide1=rng.uniform(-6,6,(32,2));wide2=rng.uniform(-6,6,(32,2))
            receipt=bank.install('rule_'+str(i),learned[higher]['expression'],xy,y)
            if receipt['status']!='committed':raise RuntimeError(receipt)
            workspace_predictions.append({'seed':seed,'case':i,'in_range':bank.read('rule_'+str(i),q1,q2).tolist(),
                                          'larger_inputs':bank.read('rule_'+str(i),wide1,wide2).tolist()})
            if seed==0:tasks.append({'case':i,'base':base.tolist(),'higher':higher,'amplitude':amp,
                                    'xy':xy.tolist(),'observations':y.tolist(),'q1':q1.tolist(),'q2':q2.tolist(),'wide1':wide1.tolist(),'wide2':wide2.tolist()})
        for name in originals:
            assert bank.slots[name]==originals[name];np.testing.assert_array_equal(bank.read(name,cases['in_range'][:32]),old_values[name])
        bank.fork('rule_0','editable_cubic');before=bank.read('editable_cubic',cases['in_range'][:32]);bank.edit_amplitude('editable_cubic',.5)
        after=bank.read('editable_cubic',cases['in_range'][:32]);signal=executor.evaluate(learned[0]['expression'],cases['in_range'][:32])
        edit_error=float(np.max(abs(after-before-.5*signal[None,:])))
        audits.append({'seed':seed,'adopted':CONFIG['workspace_cases'],'old_snapshots_preserved':len(originals),'amplitude_edit_coherence_error':edit_error})
        bank.save(folder/f'workspaces_{seed}.json')
        print(f'seed {seed}: learned programs and workspace predictions frozen',flush=True)
    for name,obj in [('primitive_predictions',primitive),('composition_predictions',compositions),('program_libraries',libraries),
                     ('depth_predictions',deep),('workspace_predictions',workspace_predictions),('workspace_tasks',tasks),('workspace_audit',audits)]:write(folder/(name+'.json'),obj)
    write(folder/'prediction_freeze.json',{p.name:hashfile(p) for p in sorted(folder.glob('*predictions.json'))})

def metrics(pred,target):
    pred=np.asarray(pred);target=np.asarray(target);error=pred-target
    return {'count':int(error.size),'mae':float(np.mean(abs(error))),'rmse':float(np.sqrt(np.mean(error**2))),
            'max_abs_error':float(np.max(abs(error))),'within_1e6':float(np.mean(abs(error)<=1e-6)),
            'rounded_accuracy':float(np.mean(np.rint(pred)==np.rint(target)))}

def score(folder):
    for name,h in json.loads((folder/'prediction_freeze.json').read_text()).items():assert hashfile(folder/name)==h
    inputs=primitive_cases(CONFIG['test_seed']);results={'primitive':{},'composition':{},'depth':{},'workspace':{}}
    records=json.loads((folder/'primitive_predictions.json').read_text())
    for name in sorted({r['model'] for r in records}):
        for cohort,x in inputs.items():
            rows=[r for r in records if r['model']==name and r['cohort']==cohort]
            pred=np.array([r['predictions'] for r in rows]);truth=np.broadcast_to(outcomes(x),pred.shape)
            results['primitive'][name+'/'+cohort]={channel:metrics(pred[:,i],truth[:,i]) for i,channel in enumerate(CHANNELS)}
    records=json.loads((folder/'composition_predictions.json').read_text())
    for name in sorted({r['model'] for r in records}):
        for cohort,x in inputs.items():
            pred=np.array([r['predictions'] for r in records if r['model']==name and r['cohort']==cohort])
            truth=np.broadcast_to(higher_targets(x),pred.shape);result=metrics(pred,truth)
            result['whole_functions_within_1e6']=int(np.all(abs(pred-truth)<=1e-6,axis=-1).sum())
            result['function_seed_pairs']=pred.shape[0]*pred.shape[1]
            results['composition'][name+'/'+cohort]=result
    records=json.loads((folder/'depth_predictions.json').read_text())
    for name in sorted({r['model'] for r in records}):
        for depth in range(1,7):
            rows=[r for r in records if r['model']==name and r['depth']==depth]
            pred=np.array([r['predictions'] for r in rows]);truth=np.array([np.asarray(r['inputs'])**(2**depth) for r in rows])
            result=metrics(pred,truth);result['max_relative_error']=float(np.max(abs(pred-truth)/np.maximum(abs(truth),1e-12)))
            results['depth'][name+'/'+str(depth)]=result
    tasks=json.loads((folder/'workspace_tasks.json').read_text());rows=json.loads((folder/'workspace_predictions.json').read_text())
    for cohort,a,b in [('in_range','q1','q2'),('larger_inputs','wide1','wide2')]:
        targets=[];predictions=[]
        for r in rows:
            t=tasks[r['case']];v1=world_values(t['base'],t['higher'],t['amplitude'],t[a]);v2=world_values(t['base'],t['higher'],t['amplitude'],t[b])
            targets.append(np.stack([v1,v1-v2,v1+v2]));predictions.append(r[cohort])
        pred=np.array(predictions);truth=np.array(targets);result=metrics(pred,truth)
        result['exact_task_seed_pairs']=int(np.all(abs(pred-truth)<=1e-6,axis=(1,2)).sum());result['task_seed_pairs']=len(rows)
        results['workspace'][cohort]=result
    write(folder/'scores.json',results)
    compact={'workspace':results['workspace'],'product':{k:v[CHANNELS[1]] for k,v in results['primitive'].items() if k.startswith(('trained_','random_readout_square'))},
             'composition':{k:v for k,v in results['composition'].items() if k.startswith(('trained_','random_readout_square'))}}
    print(json.dumps(compact,indent=2));return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['train','predict','score','all'],default='all',nargs='?');p.add_argument('--output',default='results')
    a=p.parse_args();folder=Path(a.output)
    if a.stage in ['train','all']:train(folder)
    if a.stage in ['predict','all']:predict(folder)
    if a.stage in ['score','all']:score(folder)
