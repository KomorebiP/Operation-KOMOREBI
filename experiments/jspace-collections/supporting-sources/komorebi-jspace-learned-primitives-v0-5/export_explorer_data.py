"""Export actual learned weights and reference probes for inspection. Komorebi P."""
import json
import numpy as np
from pathlib import Path
from primitive_model import Kernels, Catalog
from executor import Executor

ROOT = Path(__file__).resolve().parent


def main():
    folder = ROOT/'results'
    names = ['trained_square','random_readout_square','trained_tanh']
    models = {n:Kernels.load(folder/'models'/f'{n}_0.npz') for n in names}
    entries = json.loads((folder/'program_libraries.json').read_text())[0]['entries']
    expressions = {'product':['call','channel_42','x','z'],
                   'cubic':entries[1]['expression'], 'quartic':entries[6]['expression']}
    data = {'author':'Komorebi P.', 'seed':0,
            'models':{n:{'activation':m.activation,'identity':m.identity(),'channels':m.channels,
                         'weights':{k:v.tolist() for k,v in m.p.items()}} for n,m in models.items()},
            'expressions':expressions,
            'claim':'Actual learned-kernel evaluation. Alternative kernels are evaluation-only substitutions. Reference formulas are comparison data, not used by kernel inference.'}
    (ROOT/'examples/primitive_explorer_data.json').write_text(json.dumps(data,indent=2))
    rng = np.random.default_rng(98233)
    xy = rng.uniform([-6,-3],[6,3],(80,2)); amplitudes = rng.uniform(-2,2,len(xy))
    rows = []
    for name,model in models.items():
        executor = Executor(Catalog(model,model.channels,{'status':'evaluation_only_substitution'}))
        for signal,expression in expressions.items():
            values = amplitudes*executor.evaluate(expression,xy)
            rows.extend({'model':name,'signal':signal,'x':float(x),'z':float(z),'amplitude':float(a),'value':float(v)}
                        for (x,z),a,v in zip(xy,amplitudes,values))
    (ROOT/'examples/explorer_probe_reference.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps({'exported_models':len(models),'numeric_reference_probes':len(rows)}))


if __name__ == '__main__': main()
