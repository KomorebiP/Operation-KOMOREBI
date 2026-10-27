"""Write editable machinery examples and action requests. Komorebi P."""
import json
from pathlib import Path
from collection_scenarios import make_bank,collection_case,proposal
from scenarios import grid_case,scalar_case
from machinery import Value

ROOT=Path(__file__).resolve().parent


def main():
    folder=ROOT/'examples';folder.mkdir(exist_ok=True)
    def write(name,obj):(folder/name).write_text(json.dumps(obj,indent=2))
    for name,case in [('grid',grid_case()),('scalar',scalar_case()),('collection',collection_case())]:
        program,inputs=case[:2];write(name+'_program.json',program);write(name+'_inputs.json',{k:v.pack() for k,v in inputs.items()})
    bank=make_bank();write('functions.json',bank.registry.definitions())
    write('observe_objects.json',{'action':'observe','workspace':'objects'})
    write('move_proposal.json',proposal(bank))
    write('collision_proposal.json',proposal(bank,(0,4),False))
    write('wrong_target_proposal.json',proposal(bank,(0,1),True))
    write('offset_2.json',{'offset':Value('point',[0,2]).pack()})
    write('turns_2.json',{'turns':Value('index',2).pack()})
    write('disable.json',{'enabled':Value('flag',False).pack()})
    write('scalar_graph_proposal.json',{'action':'propose','workspace':'scalar','expected_revision':bank.branches['scalar'],
          'graph_edits':[{'kind':'rebind','node':'product','argument':'b','ref':'a'}],
          'targets':{'product':Value('scalar',9).pack()},'require_target_match':True})


if __name__=='__main__':main()
