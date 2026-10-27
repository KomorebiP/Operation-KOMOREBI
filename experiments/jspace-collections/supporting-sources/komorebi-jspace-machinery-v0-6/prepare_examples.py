"""Write editable program and input examples. Author: Komorebi P."""
import json
from pathlib import Path
from scenarios import grid_case,scalar_case,registry,node

ROOT = Path(__file__).resolve().parent


def main():
    folder = ROOT/'examples'; folder.mkdir(exist_ok=True)
    def save(name,obj): (folder/name).write_text(json.dumps(obj,indent=2))
    grid,inputs,_ = grid_case()
    save('grid_program.json',grid); save('grid_inputs.json',{k:v.pack() for k,v in inputs.items()})
    scalar,inputs = scalar_case()
    save('scalar_program.json',scalar); save('scalar_inputs.json',{k:v.pack() for k,v in inputs.items()})
    save('functions.json',registry().definitions())
    save('turns_2.json',{'turns':{'kind':'index','data':2}})
    save('disable.json',{'enabled':{'kind':'flag','data':False}})
    save('invalid_type.json',{'turns':{'kind':'scalar','data':2.}})
    save('double_function.json',{'name':'double','parameters':{'state':'scalar'},
         'body':{'nodes':[node('twice','number.add',a='state',b='state')],'outputs':{'result':'twice'}}})


if __name__=='__main__':main()
