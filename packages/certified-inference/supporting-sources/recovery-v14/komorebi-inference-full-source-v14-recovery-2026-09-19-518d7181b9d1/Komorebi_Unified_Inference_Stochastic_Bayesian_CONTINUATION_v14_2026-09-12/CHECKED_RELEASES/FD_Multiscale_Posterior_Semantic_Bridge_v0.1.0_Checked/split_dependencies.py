#!/usr/bin/env python3
"""Reproduce the exact inherited proof-body slices needed by the semantic bridge.

The continuous-time propagation proofs are retained in the predecessor, not
imported by the one-step bridge. No theorem conclusion or proof body is changed.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
source=ROOT/'PREDECESSOR/BayesianMultiscaleKalmanPosteriorPerturbation.lean'
EXPECTED='a7be2533e7ee75920b0298785e0cbbf7831c3e650af24687c718b412300a196b'
def digest(s):return hashlib.sha256(s).hexdigest()
def main():
    b=source.read_bytes()
    if digest(b)!=EXPECTED:raise RuntimeError('Inherited source hash mismatch')
    lines=b.decode().splitlines(keepends=True)
    def sl(a,b):return ''.join(lines[a-1:b])
    header=sl(1,11)
    tail=sl(12,15)
    specs=[
      ('PosteriorRefinementCore',None,[(17,193)],'\nend Komorebi.AbstractProjectorRefinement\n'),
      ('PosteriorRefinementNorms','PosteriorRefinementCore',[(17,24),(194,382),(595,612)],'\nend FiniteTimeMultiscale\nend Komorebi.AbstractProjectorRefinement\n'),
      ('PosteriorAlgebra','PosteriorRefinementNorms',[(1324,1396)],''),
      ('PosteriorGain','PosteriorAlgebra',[(1398,1521)],''),
      ('PosteriorNorms','PosteriorGain',[(1523,1607)],''),
      ('PosteriorInverse','PosteriorNorms',[(1609,1646)],''),
      ('PosteriorBudgets','PosteriorInverse',[(1648,1779)],''),
      ('PosteriorMean','PosteriorBudgets',[(1781,1869)],''),
      ('PosteriorRefinement','PosteriorMean',[(1871,1997)],'')]
    report={'source_sha256':digest(b),'source_lines':len(lines),'excluded':
      'Unchanged continuous-time stochastic propagation blocks are retained in predecessor but not required for this one-step bridge.', 'modules':[]}
    for name,dep,ranges,end in specs:
        txt=header+(f'public import Komorebi.{dep}\n' if dep else '')+tail+'\n'
        txt+='\n'.join(sl(a,b) for a,b in ranges)+end
        p=ROOT/'Komorebi'/f'{name}.lean';p.write_text(txt)
        report['modules'].append({'module':name,'source_ranges':ranges,'range_sha256':[digest(sl(a,b).encode()) for a,b in ranges], 'output_sha256':digest(txt.encode())})
    (ROOT/'DEPENDENCY_SPLIT.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
