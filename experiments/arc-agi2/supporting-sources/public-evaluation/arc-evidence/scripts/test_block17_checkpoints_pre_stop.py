#!/usr/bin/env python3
"""Tiny fake-input controls; no live checkpoint data or frozen runtime imports."""
import argparse
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


def load(path,name):
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def save(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path);a=p.parse_args();root=a.workspace.resolve()
    checker_path=root/'arc-evidence/scripts/authenticate_block17_checkpoints_pre_stop.py'
    check=load(checker_path,'fake_pre_stop_checker');asm=check.load_primitives(root)
    adapter,_=asm.load_helper(root/'arc-evidence/later-source-audit/stream_fresh_block17_dispatch.py',
                              'fake_pre_stop_adapter',asm.PINS['adapter_sha256'])
    fixture_module=load(root/'arc-evidence/scripts/test_block17_streaming_assembly.py','fake_existing_fixture')
    entrants={'legacy_block6':6,'modern':13};legacy={'legacy_block6'};receipts={'core_blocks2_4','legacy_block6','modern'}
    cases=[]
    with tempfile.TemporaryDirectory(prefix='block17-pre-stop-synthetic-') as temp:
        base=Path(temp)

        def fixture(folder):
            clean,header,records,paths,ids,metadata,_,_=fixture_module.fixture(folder,asm)
            for key,task in clean.items():
                outputs=[[[i+1]] for i in range(len(task['test']))]
                program={'op':'synthetic-no-call'};program_hash=asm.digest(program)
                replay={'status':'verified','hook':'replay_program(program, grid)',
                        'program_hash':program_hash,'train':[],'test':[]}
                for split in ('train','test'):
                    for index,example in enumerate(task[split]):
                        output=example['output'] if split=='train' else outputs[index]
                        stage={'index':0,'name':'program','program_hash':program_hash,
                            'source_hash':asm.digest(example['input']),'successor_hash':asm.digest(output)}
                        stage['receipt_hash']=asm.digest(stage)
                        bundle={'trace_mode':'single_stage','program_hash':program_hash,
                            'input_hash':asm.digest(example['input']),'output_hash':asm.digest(output),
                            'stage_count':1,'stages':[stage],'example_index':index}
                        bundle['receipt_hash']=asm.digest(bundle);replay[split].append(bundle)
                replay=asm.seal(replay)
                modern={'entrant':'modern','family':'synthetic','program':program,'complexity':1,'evidence':{},
                        'train_outputs':[x['output'] for x in task['train']], 'test_outputs':outputs,
                        'execution_replay':replay,'behavior_hash':asm.digest(outputs)}
                modern['origin_candidate_hash']=asm.digest(modern);modern['source_block']=13
                modern['candidate_hash']=asm.digest(modern)
                native={'entrant':'legacy_block6','source_block':6,'program':{'op':'synthetic-native-no-call'},
                    'test_outputs':outputs,'task_semantic_hash':asm.digest(task),'behavior_hash':asm.digest(outputs),
                    'verification':{'status':'synthetic native metadata, no program call'}}
                native['candidate_hash']=asm.digest(native)
                records[key]=asm.seal({'task_semantic_hash':asm.digest(task),
                    'base':[{'attempt_1':[[1]],'attempt_2':[[2]]} for x in task['test']],
                    'candidates':[modern,native], 'receipts':{name:{'status':'ok'} for name in receipts}})
            metadata.pop('completed_utc',None)
            metadata['events'].pop() # Second started task remains active; this is provisional.
            return [clean,header,records,paths,ids,metadata]

        def materialize(data,fix_origin=True,fix_replay=True):
            clean,header,records,paths,ids,metadata=data
            for key,record in records.items():
                for candidate in record['candidates']:
                    if candidate['entrant']=='modern':
                        replay=candidate['execution_replay']
                        if fix_replay and replay['status']=='verified':
                            for split in ('train','test'):
                                for bundle in replay[split]:
                                    bundle['receipt_hash']=asm.digest({k:v for k,v in bundle.items() if k!='receipt_hash'})
                            candidate['execution_replay']=asm.seal(replay)
                        if fix_origin:
                            candidate['origin_candidate_hash']=asm.digest({k:v for k,v in candidate.items()
                                if k not in {'source_block','origin_candidate_hash','candidate_hash'}})
                    candidate['candidate_hash']=asm.digest({k:v for k,v in candidate.items() if k!='candidate_hash'})
                records[key]=asm.seal(record)
                save(paths[key],asm.seal({'run_hash':header['run_hash'],'record':records[key]}))
            ids.update({key:asm.identity(path) for key,path in paths.items()})
            for event in metadata['events']:
                if event['event'] in {'checkpoint_written','duplicate_identical_not_overwritten'}:
                    if event.get('record_hash')!='bad': event['record_hash']=records[event['task_id']]['content_hash']
            data[5]=asm.seal(metadata)

        def run(data,stable=lambda:None):
            c,h,r,paths,ids,m=data
            return check.authenticate_records(asm,adapter,c,paths,ids,h,m,'synthetic-scheduler',
                                              entrants,legacy,receipts,stable,planned_scope=2)
        valid=fixture(base/'valid');materialize(valid);actual=run(valid)
        assert actual['active_tasks_at_snapshot']==['z-\u96ea'] and actual['terminal_metadata_observed'] is False
        assert actual['diagnostic_counts']['legacy_candidates']==2
        assert actual['diagnostic_counts']['modern_verified_candidates']==2
        assert actual['diagnostic_counts']['replay_bundles']==5
        cases.append({'name':'verified_and_legacy_with_live_started_task','passed':True})
        absent=fixture(base/'absent')
        for r in absent[2].values():
            c=r['candidates'][0];c['execution_replay']={'status':'not_supplied','hook':None,
                'program_hash':asm.digest(c['program']),'train':[],'test':[]}
        materialize(absent);result=run(absent)
        assert result['diagnostic_counts']['modern_not_supplied_candidates']==2
        cases.append({'name':'not_supplied_counted_without_invented_seal','passed':True})
        duplicate=fixture(base/'duplicate');duplicate[5]['events'][-2]['event']='duplicate_identical_not_overwritten'
        materialize(duplicate);assert run(duplicate)['duplicate_completion_events_checked']==1
        cases.append({'name':'available_duplicate_event_hash_checked','passed':True})

        def negative(name,change,expected,**opts):
            d=fixture(base/name)
            if name=='missing_task_path':
                materialize(d,**opts);change(d)
            else:
                change(d);materialize(d,**opts)
            try:run(d)
            except (ValueError,KeyError,TypeError) as exc:
                assert expected in str(exc),(name,str(exc));cases.append({'name':name,'passed':True,'rejection':str(exc)})
            else:raise AssertionError('negative accepted: '+name)
        def modern(d):return d[2]['a-task']['candidates'][0]
        negative('modern_origin',lambda d:modern(d).update(origin_candidate_hash='bad'),
                 'origin candidate hash differs',fix_origin=False)
        negative('entrant_block',lambda d:modern(d).update(source_block=17),'entrant/block binding differs')
        negative('receipt_inventory',lambda d:d[2]['a-task']['receipts'].pop('modern'),'receipt inventory differs')
        negative('bundle_input',lambda d:modern(d)['execution_replay']['test'][0].update(input_hash='bad'),
                 'replay input/output binding differs')
        negative('stage_chain',lambda d:modern(d)['execution_replay']['test'][0]['stages'][0].update(source_hash='bad'),
                 'replay stage chain differs')
        negative('stage_receipt',lambda d:modern(d)['execution_replay']['test'][0]['stages'][0].update(receipt_hash='bad'),
                 'replay stage receipt hash differs')
        negative('replay_outer_seal',lambda d:modern(d)['execution_replay'].update(content_hash='bad'),
                 'content hash mismatch',fix_replay=False)
        negative('modern_demo',lambda d:modern(d).update(train_outputs=[[[9]]]),'demonstration output differs')
        def absent_wrong_demo(d):
            c=modern(d);c['execution_replay']={'status':'not_supplied','hook':None,
                'program_hash':asm.digest(c['program']),'train':[],'test':[]};c['train_outputs']=[[[9]]]
        negative('not_supplied_demo',absent_wrong_demo,'demonstration output differs')
        negative('available_completion_hash',lambda d:d[5]['events'][1].update(record_hash='bad'),
                 'available supplemental completion hash differs')
        negative('terminal_with_active',lambda d:d[5].update(completed_utc='2026-10-09T00:00:00+00:00'),
                 'terminal supplemental event scope incomplete')
        negative('started_after_skip',lambda d:d[5]['events'].insert(0,{'task_id':'a-task','event':'skip_existing'}),
                 'supplemental start order differs')
        negative('missing_task_path',lambda d:d[3].pop('a-task'),'checkpoint task membership differs')
        try:run(valid,lambda:(_ for _ in ()).throw(ValueError('synthetic input changed')))
        except ValueError as exc:
            assert str(exc)=='synthetic input changed';cases.append({'name':'post_authentication_instability','passed':True,'rejection':str(exc)})
        else:raise AssertionError('instability accepted')
    report=asm.seal({'schema':'komorebi.block17.checkpoint-pre-stop-synthetic-controls.v1',
        'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'checker':asm.identity(checker_path),
        'test':asm.identity(Path(__file__)),'controls':cases,'all_controls_pass':True,
        'positive_controls':3,'negative_controls':len(cases)-3,'targets_opened':False,
        'live_records_read':False,'frozen_runtime_imported':False,'compiler_dispatcher_program_calls':0,
        'production_checker_executed':False,'scope':'Two fake tasks,3 outputs; diagnostic nested replay seals/chains only, no program calls.',
        'limitations':['Synthetic checks are bounded; production source/checkpoint stability must be authenticated later.',
            'Base/status dictionaries are protected by enclosing record/wrapper seals, not independently sealed.']})
    save(a.report,report);print(json.dumps({'report':str(a.report),'controls':len(cases),'all_controls_pass':True}))


if __name__=='__main__':main()
