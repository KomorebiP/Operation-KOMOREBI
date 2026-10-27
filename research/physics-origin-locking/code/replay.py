"""Replay named recorded configurations without overwriting reference evidence."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from expansion import Config,Model,ROOT

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name',action='append',required=True,help='Configuration stem from results; may be repeated.')
    parser.add_argument('--output',type=Path,required=True,help='New output directory. Existing result names are rejected.')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    for name in args.name:
        if Path(name).name!=name or name in ('.','..'):parser.error('name must be a simple recorded configuration stem')
        source=ROOT/'results'/f'{name}.json'
        if not source.is_file():parser.error(f'No recorded configuration: {name}')
        dst=args.output/f'{name}.json';arrdst=dst.with_suffix('.npz')
        if dst.exists() or arrdst.exists():parser.error(f'Refusing to overwrite {dst}')
        old=json.loads(source.read_text())
        if 'config' not in old or 'parameters' not in old:parser.error(f'Not a finite configuration: {name}')
        result,arrays=Model(Config(**old['config'])).solve()
        dst.write_text(json.dumps(result,indent=2));np.savez_compressed(arrdst,**arrays)
        print(json.dumps({'name':name,'final_q_difference':result['final_q']-old['final_q'],
                          'energy_work_residual':result['energy_work_max_relative_residual'],
                          'absolute_mode_invariant_residual':result['invariant_max_residual']}),flush=True)
if __name__=='__main__':main()
