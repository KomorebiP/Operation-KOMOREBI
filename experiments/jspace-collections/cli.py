"""Command-line workspace editing and inspection. Author: Komorebi P."""
import argparse
import json
from pathlib import Path
from machinery import Value, Fault, Store, Program
from machinery.operations import base_registry
from collection_scenarios import make_bank


def read(path): return json.loads(Path(path).read_text())
def values(obj): return {k:Value.unpack(v) for k,v in obj.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank',type=Path,default=Path('my_workspaces.json'))
    sub = parser.add_subparsers(dest='command',required=True)
    sub.add_parser('init',help='Create grid, scalar and object-collection workspaces.')
    sub.add_parser('empty',help='Create an empty bank with native operations and frozen learned kernels.')
    sub.add_parser('list'); sub.add_parser('registry')
    p = sub.add_parser('create'); p.add_argument('name'); p.add_argument('--program',type=Path,required=True); p.add_argument('--inputs',type=Path,required=True)
    p = sub.add_parser('run'); p.add_argument('name')
    p = sub.add_parser('graph'); p.add_argument('name')
    p = sub.add_parser('inspect'); p.add_argument('name'); p.add_argument('value',help='Qualified value name, for example root/copy/patch')
    p = sub.add_parser('trace'); p.add_argument('name'); p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('fork'); p.add_argument('source'); p.add_argument('name')
    for command in ['edit','preview']:
        p = sub.add_parser(command); p.add_argument('name'); p.add_argument('--patch',type=Path,required=True); p.add_argument('--expect')
    p = sub.add_parser('program'); p.add_argument('name'); p.add_argument('--file',type=Path,required=True); p.add_argument('--expect')
    p = sub.add_parser('define'); p.add_argument('--file',type=Path,required=True)
    p = sub.add_parser('undo'); p.add_argument('name')
    p = sub.add_parser('checkout'); p.add_argument('name'); p.add_argument('revision')
    p = sub.add_parser('compare'); p.add_argument('a'); p.add_argument('b')
    p = sub.add_parser('history'); p.add_argument('name')
    args = parser.parse_args()
    try:
        mutate = False
        if args.command in ['init','empty']:
            bank = make_bank() if args.command=='init' else Store(base_registry())
            result = {'status':'created','workspaces':list(bank.branches)}; mutate = True
        else:
            bank = Store.load(args.bank,base_registry())
            if args.command=='list': result = bank.branches
            elif args.command=='registry': result = bank.registry.manifest()
            elif args.command=='create':
                result = bank.create(args.name,read(args.program),values(read(args.inputs))); mutate = result['status']=='committed'
            elif args.command=='run':
                run = bank.run(args.name); result = {k:run[k] for k in ['status','outputs','steps','native_executions','cache_hits']}
                if 'error' in run: result['error'] = run['error']
            elif args.command=='inspect':
                run = bank.run(args.name)
                if args.value not in run['values']: raise Fault('binding','This value was not produced by the executed branch.')
                result = {'name':args.value,'value':run['values'][args.value]}
            elif args.command=='graph':
                snapshot = bank.snapshot(args.name)
                graph = Program(snapshot['program'],{k:v['kind'] for k,v in snapshot['inputs'].items()},bank.registry)
                result = {'types':graph.types,'potential_dependencies':graph.dependencies,'outputs':graph.outputs}
            elif args.command=='trace':
                result = bank.run(args.name); args.output.parent.mkdir(parents=True,exist_ok=True)
                # Trace exports intentionally require a new destination.
                with args.output.open('x') as handle: json.dump(result,handle,indent=2,allow_nan=False)
                result = {'status':'exported','output':str(args.output),'events':len(result['trace'])}
            elif args.command=='fork': result = bank.fork(args.source,args.name); mutate = True
            elif args.command in ['edit','preview']:
                method = bank.edit if args.command=='edit' else bank.preview
                result = method(args.name,values(read(args.patch)),expected_revision=args.expect)
                mutate = args.command=='edit' and result['status']=='committed'
            elif args.command=='program':
                result = bank.edit(args.name,program=read(args.file),expected_revision=args.expect,label='edit_program'); mutate = result['status']=='committed'
            elif args.command=='define': result = bank.define_function(**read(args.file)); mutate = True
            elif args.command=='undo': result = bank.undo(args.name); mutate = result['status']=='restored'
            elif args.command=='checkout': result = bank.checkout(args.name,args.revision); mutate = True
            elif args.command=='compare': result = bank.compare(args.a,args.b)
            else:
                revision = bank.branches[args.name]; result = []
                while revision is not None:
                    row = bank.revisions[revision]; result.append({'id':row['id'],'parent':row['parent'],'label':row['label']}); revision = row['parent']
        if mutate: bank.save(args.bank)
        if isinstance(result,dict) and 'run' in result:
            full = result; result = {k:full[k] for k in ['status','workspace','revision','base_revision'] if k in full}
            if 'error' in full['run']: result['error'] = full['run']['error']
            result['execution'] = {k:full['run'][k] for k in ['steps','native_executions','cache_hits']}
            if full.get('changes'):
                result['changed_values'] = list(full['changes']['values'])
                result['changed_outputs'] = {k:{f:v for f,v in detail.items() if f not in ['before','after']}
                                             for k,detail in full['changes']['outputs'].items()}
        print(json.dumps(result,indent=2,allow_nan=False))
        if isinstance(result,dict) and result.get('status') in ['failed','rejected']: return 2
        return 0
    except (Fault,ValueError,KeyError,OSError) as exc:
        print(json.dumps({'status':'failed','error':{'code':getattr(exc,'code','input'),'message':str(exc)}}))
        return 2


if __name__=='__main__': raise SystemExit(main())
