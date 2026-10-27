from pathlib import Path
import json,sys,re,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from certified_backend import certified_discover
from new_checks.check_trace import check_trace
from v05_checks.export_checked_data import export

def main():
    out=ROOT/'certified_data';out.mkdir(exist_ok=True)
    rows=[];sources=sorted((ROOT/'certificates').glob('*.source.json'))
    # Explicit stress fixture: many accepted torsion refinements in dimension one.
    stress={'schema':'finite-linear-profile-v1','p':2,'r':24,'dimension':1,
        'actions':[[[1]]],'observations':[[2**s] for s in reversed(range(24))],
        'initial_interface':'all_states','word_order':'left_to_right'}
    (out/'descending_torsion.source.json').write_text(json.dumps(stress,indent=2)+'\n')
    sources.append(out/'descending_torsion.source.json')
    batch_codes={}
    for idx,path in enumerate(sources):
        source=json.loads(path.read_text());trace,stats=certified_discover(source)
        checked=check_trace(source,trace)
        if idx<202:
            old=json.loads((ROOT/'certificates'/path.name.replace('.source.json','.certificate.json')).read_text())
            # The raw observation list is held in witnesses in the legacy certificate.
            old_trace=json.loads((ROOT/'queue_traces'/path.name.replace('.source.json','.trace.json')).read_text())
            assert trace['result']==old_trace['result']
        key=path.name.removesuffix('.source.json')
        (out/(key+'.trace.json')).write_text(json.dumps(trace,indent=2)+'\n')
        code=export(source,trace,'Temporary')
        lines=code.splitlines()
        start=next(i for i,l in enumerate(lines) if l.startswith('abbrev R'))
        body='\n'.join(lines[start:next(i for i,l in enumerate(lines) if l.startswith('end '))])
        names='R A O evidence result checked_data reference_result all_words standard_definition'.split()
        prefix=f'c{idx:03}_'
        body=re.sub(r'\b('+ '|'.join(names)+r')\b',lambda m:prefix+m.group(),body)
        batch=idx//12;batch_codes.setdefault(batch,[]).append(body)
        rows.append({'index':idx,'source':str(path.relative_to(ROOT)),
          'trace':str((out/(key+'.trace.json')).relative_to(ROOT)),
          'module':f'CheckedBatch{batch:02}','prefix':prefix,'stats':stats,'checked':checked})
    for b,parts in batch_codes.items():
        name=f'CheckedBatch{b:02}'
        text='\n'.join(['module','public import CertifiedOracle','', '@[expose] public section',
        'namespace Komorebi.Discovery.CheckedData.'+name,
        'open Komorebi.Discovery Komorebi.Discovery.Certified',
        'open Komorebi.Representation Komorebi.Representation.Matrix',
        'open Komorebi.ModelTheory Komorebi.ModelTheory.Standard',
        'set_option maxRecDepth 100000','set_option maxHeartbeats 12000000',*parts,
        'end Komorebi.Discovery.CheckedData.'+name,''])
        (ROOT/'formalization'/(name+'.lean')).write_text(text)
    (ROOT/'v05_evidence/EXPORTED_DATA.json').write_text(json.dumps(rows,indent=2)+'\n')
    print({'cases':len(rows),'batches':len(batch_codes),'decisions':sum(x['checked']['candidates'] for x in rows),'stress':rows[-1]})
if __name__=='__main__':main()
