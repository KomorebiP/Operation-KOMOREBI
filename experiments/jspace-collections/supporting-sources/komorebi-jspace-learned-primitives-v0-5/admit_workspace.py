"""Select a learned signal from demonstrations; retain ambiguous admissions. Komorebi P.

This wrapper was added after the original experiment was scored. It does not
modify its frozen source, models, predictions or program libraries.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from workspace import features
from cli import ROOT, load_bank


def admit(bank, name, entries, xy, observations, tolerance=1e-6):
    xy, observations = np.asarray(xy,float), np.asarray(observations,float)
    if xy.ndim!=2 or xy.shape[1]!=2 or observations.shape!=(len(xy),):
        raise ValueError('Expected n two-input demonstrations and n scalar observations.')
    if not np.all(np.isfinite(xy)) or not np.all(np.isfinite(observations)):
        raise ValueError('Demonstrations must be finite.')
    accepted=[]; audit=[]; seen=set()
    for index,entry in enumerate(entries):
        if entry['kernel_identity']!=bank.primitive_identity:
            raise ValueError('Program library and workspace primitive identities differ.')
        expression=entry['expression']; key=json.dumps(expression,separators=(',',':'))
        if key in seen:continue
        seen.add(key)
        design=np.column_stack([features(xy),bank.executor.evaluate(expression,xy)])
        weights,_,rank,_=np.linalg.lstsq(design,observations,rcond=1e-10)
        error=float(np.max(abs(design@weights-observations)))
        audit.append({'entry':index,'rank':int(rank),'demonstration_error':error})
        if rank==7 and error<=tolerance:accepted.append(index)
    receipt={'checked':len(audit),'fitting_entries':accepted,'fits':audit,
             'claim':'Unique fit within this supplied library, not proof of a unique rule.'}
    if len(accepted)!=1:
        return {'status':'ambiguous' if accepted else 'no_unique_fitting_signal',**receipt}
    chosen=entries[accepted[0]]
    committed=bank.install(name,chosen['expression'],xy,observations,tolerance)
    return {**receipt,**committed,'selected_entry':accepted[0], 'source':chosen.get('source')}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bank',type=Path,required=True);p.add_argument('--name',required=True)
    p.add_argument('--demonstrations',type=Path,required=True)
    a=p.parse_args();bank=load_bank(a.bank)
    entries=json.loads((ROOT/'results/program_libraries.json').read_text())[0]['entries']
    demo=json.loads(a.demonstrations.read_text())
    result=admit(bank,a.name,entries,demo['xy'],demo['observations'])
    if result['status']=='committed':bank.save(a.bank)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
