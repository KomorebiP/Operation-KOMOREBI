"""Execute JSON actions through the common workspace interface. Komorebi P."""
import argparse
import json
from pathlib import Path
from machinery import Store,Fault
from machinery.operations import base_registry
from machinery.actions import Actions
from machinery.values import digest


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bank',type=Path,required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--request',type=Path);group.add_argument('--commit',type=Path,help='Saved proposal response or receipt.')
    parser.add_argument('--response',type=Path)
    args=parser.parse_args();committed_to_disk=False
    try:
        if args.response and args.response.exists():raise Fault('conflict','Response destination already exists.')
        if args.request:request=json.loads(args.request.read_text())
        else:
            obj=json.loads(args.commit.read_text())
            request={'action':'commit','receipt':obj.get('receipt',obj)}
        bank=Store.load(args.bank,base_registry());before=digest(bank.pack())
        result=Actions(bank).apply(request)
        if digest(bank.pack())!=before:
            bank.save(args.bank);committed_to_disk=True
        result['bank_updated']=committed_to_disk
        if args.response:
            args.response.parent.mkdir(parents=True,exist_ok=True)
            with args.response.open('x') as handle:json.dump(result,handle,indent=2,allow_nan=False)
            brief={k:result[k] for k in ['status','workspace','revision','proposal_id','reason','error','residual_before','residual_after','residual','bank_updated'] if k in result}
            brief['response']=str(args.response);print(json.dumps(brief,indent=2))
        else:print(json.dumps(result,indent=2,allow_nan=False))
        return 2 if result['status'] in ['rejected','failed'] else 0
    except (Fault,ValueError,KeyError,OSError,TypeError) as exc:
        print(json.dumps({'status':'failed','error':{'code':getattr(exc,'code','input'),'message':str(exc)},'bank_updated':committed_to_disk}))
        return 2


if __name__=='__main__':raise SystemExit(main())
