"""Post-score follow-up: choose from the library without a target-family index. Komorebi P."""
import copy
import json
import numpy as np
from cli import ROOT,load_bank
from admit_workspace import admit


def main():
    folder=ROOT/'results'
    tasks=json.loads((folder/'workspace_tasks.json').read_text())
    # The admission function receives only these reduced records, not query
    # inputs, target coefficients, family labels or query outputs.
    demos=[{'xy':t['xy'],'observations':t['observations']} for t in tasks]
    libraries=json.loads((folder/'program_libraries.json').read_text())
    receipts=[];matched=0;checks=[]
    for seed in range(3):
        original=load_bank(folder/f'workspaces_{seed}.json',seed)
        bank=load_bank(folder/f'workspaces_{seed}.json',seed)
        bank.slots={name:slot for name,slot in bank.slots.items() if name in ['A','B','C']}
        for i,demo in enumerate(demos):
            result=admit(bank,'inferred_'+str(i),libraries[seed]['entries'],demo['xy'],demo['observations'])
            assert result['status']=='committed', (seed,i,result)
            # Compare resulting states only after admission finishes. A matching
            # state reuses the already replayed query-prediction evidence.
            assert bank.state('inferred_'+str(i))==original.state('rule_'+str(i))
            matched+=1
            receipts.append({'seed':seed,'case':i,'selected_entry':result['selected_entry'],
                             'fitting_count':len(result['fitting_entries']),
                             'checked':result['checked'],'demonstration_error':result['demonstration_error'],
                             'same_state_as_original_given_signal':True})
        old=copy.deepcopy(bank.to_dict())
        assert admit(bank,'insufficient',libraries[seed]['entries'],demos[0]['xy'][:5],demos[0]['observations'][:5])['status']=='no_unique_fitting_signal'
        assert bank.to_dict()==old;checks.append('insufficient_support_keeps_bank_'+str(seed))
        xy=np.array(demos[0]['xy']);y=np.sin(xy[:,0]+2*xy[:,1])
        assert admit(bank,'unsupported',libraries[seed]['entries'],xy,y)['status']=='no_unique_fitting_signal'
        assert bank.to_dict()==old;checks.append('unsupported_signal_keeps_bank_'+str(seed))
        # Two distinct representations can span the same behavior together
        # with the legacy linear features. Conservatively retain that ambiguity.
        entry=copy.deepcopy(libraries[seed]['entries'][0])
        alternate=copy.deepcopy(entry)
        alternate['expression']=['call','channel_91',entry['expression'],'x']
        assert admit(bank,'ambiguous',[entry,alternate],demos[0]['xy'],demos[0]['observations'])['status']=='ambiguous'
        assert bank.to_dict()==old;checks.append('ambiguous_signal_keeps_bank_'+str(seed))
    (ROOT/'examples/admission_demonstrations.json').write_text(json.dumps(demos[0],indent=2))
    report={'author':'Komorebi P.','status':'passed','phase':'post_score_followup',
            'separate_fresh_benchmark':False,'tasks':len(demos),'kernel_seeds':3,
            'automatically_admitted':matched,'exact_state_matches_to_original_given_signal':matched,
            'query_information_passed_to_admission':False,
            'supplied_candidate_library_size':9,'negative_checks':checks,'receipts':receipts}
    (folder/'automatic_admission_audit.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='receipts'},indent=2))


if __name__=='__main__':main()
