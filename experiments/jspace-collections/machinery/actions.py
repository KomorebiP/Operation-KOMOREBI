"""A data-only action interface and replayable proposal receipts. Komorebi P.

Receipts protect against accidental changes and stale state. They are not
signatures or authorization credentials. No action policy is learned here.
"""
import copy
import numpy as np
from .values import Value, Fault, digest, change, equivalent, element_kind
from .runtime import Program


def residual(outputs,targets,atol=1e-9):
    rows={}
    for name,target in targets.items():
        actual=outputs.get(name)
        if actual is None:
            rows[name]={'matched':False,'reason':'missing_output'};continue
        expected=Value.unpack(target);value=Value.unpack(actual)
        row={'matched':equivalent(value,expected,atol),'kind':expected.kind}
        if value.kind!=expected.kind:row['reason']='type_mismatch'
        elif value.kind in ('grid','mask'):
            if value.data.shape!=expected.data.shape:
                row.update(reason='shape_mismatch',actual_shape=list(value.data.shape),target_shape=list(expected.data.shape))
            else:
                wrong=np.argwhere(value.data!=expected.data)
                row.update(mismatched_cells=len(wrong),total_cells=value.data.size,
                           coordinates=wrong[:256].tolist(),coordinates_truncated=len(wrong)>256)
        elif value.kind in ('scalar','index'):
            row.update(signed_error=value.data-expected.data,absolute_error=abs(value.data-expected.data))
        elif element_kind(value.kind):
            row.update(actual_length=len(value.data),target_length=len(expected.data))
        rows[name]=row
    return {'provided':bool(targets),'all_matched':all(r['matched'] for r in rows.values()) if targets else None,'outputs':rows}


def graph_patch(program,edits):
    result=copy.deepcopy(program)
    if not isinstance(edits,list) or len(edits)>64:raise Fault('budget','At most 64 graph edits may be proposed together.')
    for edit in edits:
        if not isinstance(edit,dict):raise Fault('schema','Invalid graph edit.')
        mode=edit.get('kind');index={n['id']:i for i,n in enumerate(result['nodes'])}
        if mode=='rebind' and set(edit)=={'kind','node','argument','ref'}:
            if edit['node'] not in index:raise Fault('binding','Cannot rebind a missing node.')
            node=result['nodes'][index[edit['node']]]
            if 'args' not in node or edit['argument'] not in node['args']:raise Fault('binding','Rebind requires an existing named operation argument.')
            node['args'][edit['argument']]=edit['ref']
        elif mode=='replace_node' and set(edit)=={'kind','node','value'}:
            if edit['node'] not in index or not isinstance(edit['value'],dict) or edit['value'].get('id')!=edit['node']:
                raise Fault('binding','A replacement must retain an existing node id.')
            result['nodes'][index[edit['node']]]=copy.deepcopy(edit['value'])
        elif mode=='add_node' and set(edit)=={'kind','value'}:
            result['nodes'].append(copy.deepcopy(edit['value']))
        elif mode=='remove_node' and set(edit)=={'kind','node'}:
            if edit['node'] not in index:raise Fault('binding','Cannot remove a missing node.')
            del result['nodes'][index[edit['node']]]
        elif mode=='set_output' and set(edit)=={'kind','output','ref'}:
            result['outputs'][edit['output']]=edit['ref']
        else:raise Fault('schema','Unknown or malformed graph edit.')
    return result


def check_locks(before,after,locks,atol):
    rows={}
    for name in locks:
        a,b=before.get(name),after.get(name)
        rows[name]=a is not None and b is not None and equivalent(Value.unpack(a),Value.unpack(b),atol)
    return {'all_preserved':all(rows.values()),'outputs':rows}


class Actions:
    SCHEMA='komorebi_workspace_proposal_v0.7'
    def __init__(self,store):self.store=store

    def apply(self,request):
        try:
            result=self._apply(copy.deepcopy(request))
            return result
        except Fault as exc:
            return {'status':'rejected','error':{'code':exc.code,'message':str(exc)}}
        except (KeyError,TypeError,ValueError) as exc:
            return {'status':'rejected','error':{'code':'schema','message':str(exc)}}

    def _apply(self,request):
        if not isinstance(request,dict) or 'action' not in request:raise Fault('schema','A request needs an action.')
        action=request['action'];self.store._meaning()
        if action=='observe':
            if set(request)!={'action','workspace'}:raise Fault('schema','Observe expects only a workspace.')
            name=request['workspace'];snapshot=self.store.snapshot(name);run=self.store.run(name)
            program=Program(snapshot['program'],{k:v['kind'] for k,v in snapshot['inputs'].items()},self.store.registry)
            return {'status':'observed','workspace':name,'revision':self.store.branches[name],
                    'registry_identity':self.store.registry_identity,'snapshot':snapshot,'outputs':run['outputs'],
                    'types':program.types,'potential_dependencies':program.dependencies,'trace':run['trace']}
        if action=='propose':return self.propose(request)
        if action=='commit':
            if set(request)!={'action','receipt'}:raise Fault('schema','Commit expects a receipt.')
            return self.commit(request['receipt'])
        if action=='fork' and set(request)=={'action','workspace','name','expected_revision'}:
            if self.store.branches.get(request['workspace'])!=request['expected_revision']:raise Fault('conflict','Workspace revision changed.')
            return self.store.fork(request['workspace'],request['name'])
        if action=='undo' and set(request)=={'action','workspace','expected_revision'}:
            if self.store.branches.get(request['workspace'])!=request['expected_revision']:raise Fault('conflict','Workspace revision changed.')
            return self.store.undo(request['workspace'])
        if action=='compare' and set(request)=={'action','a','b'}:
            return {'status':'compared','changes':self.store.compare(request['a'],request['b'])}
        raise Fault('schema','Unknown or malformed action.')

    def propose(self,request):
        allowed={'action','workspace','expected_revision','updates','graph_edits','targets','locked_outputs','require_target_match','atol'}
        if set(request)-allowed or not {'workspace','expected_revision'}<=set(request):raise Fault('schema','Invalid proposal fields.')
        name=request['workspace'];head=request['expected_revision']
        if not isinstance(head,str) or self.store.branches.get(name)!=head:raise Fault('conflict','Proposal is based on a stale or missing revision.')
        atol=request.get('atol',1e-9)
        if isinstance(atol,bool) or not isinstance(atol,(float,int)) or not np.isfinite(atol) or atol<0:raise Fault('type','Tolerance must be finite and nonnegative.')
        targets=request.get('targets',{});locks=request.get('locked_outputs',[]);required=request.get('require_target_match',False)
        if not isinstance(targets,dict) or not isinstance(locks,list) or not all(isinstance(k,str) for k in locks) or type(required) is not bool:
            raise Fault('schema','Invalid targets or constraints.')
        targets={k:Value.unpack(v).pack() for k,v in targets.items()}
        if required and not targets:raise Fault('constraint','Required target matching needs at least one target.')
        snapshot=self.store.snapshot(name)
        updates={k:Value.unpack(v) for k,v in request.get('updates',{}).items()}
        program=graph_patch(snapshot['program'],request.get('graph_edits',[]))
        before=self.store.run(name)
        preview=self.store.preview(name,updates,program,expected_revision=head)
        constraints={'targets':targets,'locked_outputs':locks,'require_target_match':required,'atol':atol}
        if preview['status']!='ready':
            return {'status':'rejected','error':preview['run']['error'],'trace':preview['run']['trace'],
                    'base_revision':head,'residual_before':residual(before['outputs'],targets,atol)}
        after=preview['run'];lock_result=check_locks(before['outputs'],after['outputs'],locks,atol)
        feedback=residual(after['outputs'],targets,atol)
        allowed=lock_result['all_preserved'] and (not required or feedback['all_matched'])
        payload={'schema':self.SCHEMA,'author':'Komorebi P.','workspace':name,'base_revision':head,
                 'base_snapshot_identity':digest(snapshot),'registry_identity':self.store.registry_identity,
                 'candidate':preview['snapshot'],'predicted_outputs':after['outputs'],'constraints':constraints,
                 'eligible':bool(allowed)}
        receipt={'proposal_id':digest(payload),'payload':payload}
        return {'status':'ready' if allowed else 'rejected','receipt':receipt,'locks':lock_result,
                'residual_before':residual(before['outputs'],targets,atol),'residual_after':feedback,
                'changes':preview['changes'],'trace':after['trace'],
                'reason':None if allowed else 'locked_output_changed' if not lock_result['all_preserved'] else 'target_mismatch'}

    def commit(self,receipt):
        if not isinstance(receipt,dict) or set(receipt)!={'proposal_id','payload'}:raise Fault('schema','Malformed proposal receipt.')
        payload=receipt['payload']
        if digest(payload)!=receipt['proposal_id']:raise Fault('integrity','Proposal receipt changed after preview.')
        fields={'schema','author','workspace','base_revision','base_snapshot_identity','registry_identity','candidate','predicted_outputs','constraints','eligible'}
        if not isinstance(payload,dict) or set(payload)!=fields or payload['schema']!=self.SCHEMA:
            raise Fault('schema','Unknown receipt payload.')
        if payload['eligible'] is not True:raise Fault('constraint','The preview did not meet its constraints.')
        if payload['registry_identity']!=self.store.registry_identity:raise Fault('identity','Operation library changed after preview.')
        name=payload['workspace'];head=payload['base_revision']
        if self.store.branches.get(name)!=head or digest(self.store.snapshot(name))!=payload['base_snapshot_identity']:
            raise Fault('conflict','Workspace changed after preview.')
        current=self.store.run(name);candidate=payload['candidate'];constraints=payload['constraints']
        updates={k:Value.unpack(v) for k,v in candidate['inputs'].items()}
        preview=self.store.preview(name,updates,candidate['program'],expected_revision=head)
        if preview['status']!='ready':raise Fault('replay','Candidate no longer executes successfully.')
        if digest(preview['snapshot'])!=digest(candidate):raise Fault('integrity','Candidate input set changed.')
        run=preview['run'];atol=constraints['atol']
        predicted=payload['predicted_outputs']
        if set(predicted)!=set(run['outputs']) or not residual(run['outputs'],predicted,atol)['all_matched']:
            raise Fault('replay','Candidate outputs differ from the preview.')
        locked=check_locks(current['outputs'],run['outputs'],constraints['locked_outputs'],atol)
        feedback=residual(run['outputs'],constraints['targets'],atol)
        if not locked['all_preserved'] or (constraints['require_target_match'] and not feedback['all_matched']):
            raise Fault('constraint','Candidate no longer meets its constraints.')
        # The standard edit path revalidates the same candidate before its atomic commit.
        result=self.store.edit(name,updates,candidate['program'],expected_revision=head,label='commit_proposal')
        if result['status']!='committed':return result
        return {'status':'committed','workspace':name,'revision':result['revision'],'proposal_id':receipt['proposal_id'],
                'outputs':result['run']['outputs'],'changes':result['changes'],'residual':feedback,
                'registry_identity':self.store.registry_identity}
