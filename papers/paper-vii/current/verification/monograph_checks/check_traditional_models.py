#!/usr/bin/env python3
"""Independent exact finite checks of the three declared traditional models.

Seed orbit ranks are assembled explicitly from all matrix units using SymPy,
rather than inferred from the generator's row-rank formula. Block inversion is
checked by adjugate construction and both matrix products. Channel maps are
assembled from exact Kraus matrices including radical amplitudes.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
import sympy as sp

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[2]
    base=root/'editable/traditional';models=base/'monograph_figures/exact_models.json'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    data=json.loads(models.read_text());m=data['models'];checks=[];controls=[]
    def check(name,condition):
        checks.append({'assertion':name,'passed':bool(condition)})
        if not condition:raise AssertionError(name)
    def reject(name,condition):
        controls.append({'false_assertion':name,'rejected':not bool(condition)})
        if condition:raise AssertionError(name)
    s=m['seed_support'];d=s['d'];n=s['m']
    cs=[sp.Matrix(s[k]) for k in ['C1','C2','C3']]
    check('Declared coefficients have shape 2 by 3',d==2 and n==3 and all(c.shape==(d,n) for c in cs))
    for k,c in enumerate(cs[:2]):check('C%d coefficient rank equals recorded value'%(k+1),c.rank()==s['single_ranks'][k])
    def orbit(c):
        columns=[]
        for row in range(d):
            for col in range(d):
                unit=sp.zeros(d);unit[row,col]=1
                product=unit*c
                columns.append(sp.Matrix([product[i,j] for i in range(d) for j in range(n)]))
        return sp.Matrix.hstack(*columns)
    orbits=[orbit(c) for c in cs]
    for k,o in enumerate(orbits[:2]):check('C%d explicit matrix-unit orbit rank'%(k+1),o.rank()==s['single_orbit_dimensions'][k])
    joint=sp.Matrix.hstack(orbits[1],orbits[2]);joint_rank=joint.rank()
    check('C2 and C3 explicit combined orbit spans all six coordinates',joint_rank==s['combined_orbit_dimension']==d*n)
    check('C2 and C3 combined coefficient rows have rank three',cs[1].col_join(cs[2]).rank()==s['combined_row_rank']==n)
    check('Recorded ambient dimension equals the explicit orbit row count',s['ambient_dimension']==joint.rows==d*n)
    check('One coefficient matrix can cover at most four of six coordinates',d*min(d,n)<d*n)
    check('Recorded minimum seed count equals the exact capacity ceiling',s['minimum_seed_count']==(n+d-1)//d==2)
    reject('C1 alone spans the full ambient space',orbits[0].rank()==d*n)
    reject('C2 alone spans the full ambient space',orbits[1].rank()==d*n)

    b=m['block_inverse'];H=sp.Matrix(b['H']);ret=b['retained_coordinate']
    check('H is the declared real symmetric 2 by 2 operator',H==sp.Matrix([[2,1],[1,3]]) and H==H.T and ret==0)
    A,B,D=H[0,0],H[0,1],H[1,1]
    check('Hidden block is nonzero and recorded correctly',D==sp.Rational(b['eliminated_block'])==3)
    determinant=H[0,0]*H[1,1]-H[0,1]*H[1,0]
    check('Independent 2 by 2 determinant equals five',determinant==sp.Rational(b['determinant'])==5)
    inverse=sp.Matrix([[H[1,1],-H[0,1]],[-H[1,0],H[0,0]]])/determinant
    check('Independent adjugate inverse equals recorded full inverse',inverse==sp.Matrix([[sp.Rational(x) for x in row] for row in b['full_inverse']]))
    check('Both products with the proposed inverse equal identity',H*inverse==sp.eye(2) and inverse*H==sp.eye(2))
    schur=A-B/D*H[1,0]
    check('Positive H Schur complement is five thirds',schur==sp.Rational(b['schur_complement_of_H'])==sp.Rational(5,3))
    check('Inverse Schur response equals retained full inverse entry',1/schur==sp.Rational(b['effective_inverse'])==inverse[0,0])
    check('Compressed H inverse is one half',1/A==sp.Rational(b['inverse_of_compressed_H'])==sp.Rational(1,2))
    check('Recorded inverse discrepancy is exact one tenth',inverse[0,0]-1/A==sp.Rational(b['inverse_discrepancy'])==sp.Rational(1,10))
    reject('Inverse of the compressed H equals compression of full inverse',1/A==inverse[0,0])
    reject('The positive H Schur complement equals the zI-H Schur complement at z zero',schur==-schur)

    q=m['channel_scale'];P=sp.Matrix(q['P']);Z=sp.Matrix(q['Z']);I=sp.eye(2)
    check('P is a trace-one orthogonal code projector',P==P.T and P*P==P and sp.trace(P)==1)
    check('Z is an involution acting as identity on the code state',Z.T*Z==I and Z*Z==I and Z*P==P and P*Z==P)
    maps=[]
    for key,scale_key,trace_key in [('normalized_kraus_squared_weights','normalized_kraus_gram_scale','normalized_output_trace'),('unnormalized_error_squared_weights','unnormalized_error_gram_scale','unnormalized_output_trace')]:
        weights=[sp.Rational(x) for x in q[key]]
        check(key+' are nonnegative',all(x>=0 for x in weights))
        kraus=[sp.sqrt(weights[0])*I,sp.sqrt(weights[1])*Z]
        gram=sum((K.T*K for K in kraus),sp.zeros(2))
        output=sum((K*P*K.T for K in kraus),sp.zeros(2))
        check(scale_key+' equals exact Kraus completeness scalar',gram==sp.Rational(q[scale_key])*I)
        check(trace_key+' equals independently assembled output trace',sp.trace(output)==sp.Rational(q[trace_key]))
        check(key+' output is exactly the displayed scalar multiple of P',output==sum(weights)*P)
        maps.append((gram,output))
    check('Normalized map is trace preserving',maps[0][0]==I)
    reject('Unnormalized error map is trace preserving',maps[1][0]==I)
    reject('Both maps have equal output normalization on P',maps[0][1]==maps[1][1])

    replay=out/'replay'
    proc=subprocess.run([sys.executable,str(base/'generate_monograph_examples.py'),'--output-directory',str(replay)],capture_output=True,text=True,timeout=90)
    (out/'generation_stdout.txt').write_text(proc.stdout);(out/'generation_stderr.txt').write_text(proc.stderr)
    if proc.returncode:raise RuntimeError('Figure generator failed with exit '+str(proc.returncode))
    names=['exact_models.json','exact_seed_support.pdf','exact_feshbach_compression.pdf','exact_channel_scale.pdf']
    equality=[]
    for name in names:
        same=(replay/name).read_bytes()==(base/'monograph_figures'/name).read_bytes()
        if not same:raise AssertionError('Deterministic generator output differs: '+name)
        equality.append({'path':name,'input_sha256':sha(base/'monograph_figures'/name),'regenerated_sha256':sha(replay/name),'byte_identical':same})
    result={'schema':'komorebi.paper_vii.independent_exact_models.v1','status':'PASS_FOR_STATED_SCOPE','arithmetic':'Exact Q and exact algebraic radical Kraus amplitudes in SymPy; no numerical tolerance in assertions.',
        'positive_assertions':len(checks),'false_assertions_rejected':len(controls),'checks':checks,'controls':controls,
        'bounds':{'models':3,'coefficient_matrix_shape':[2,3],'ambient_seed_dimension':6,'matrix_units_per_seed':4,'block_matrix_size':2,'channel_dimension':2,'kraus_matrices_per_map':2,'code_states':1},
        'regeneration':{'records':equality,'generator_sha256':sha(base/'generate_monograph_examples.py'),'models_sha256':sha(models),'figure_outputs':3,'byte_identical_models':True,'byte_identical_figures':True},
        'conventions':'Row-major coefficient vectorization for explicit Eij C orbit columns; positive H block inverse, not zI-H at z zero; exact Kraus squared weights and the single code density P.',
        'non_claims':['Three fixed pedagogical models only; no universal theorem proof or continuum claim.','No new Lean compiler check or added formal target.','Channel output scaling is verified on this one code state; no general recovery conclusion.','Independent checks use a different exact algebra engine and explicit orbit construction; SymPy correctness is still a dependency.','PDF regeneration verifies source reproducibility, not mathematical proof.'],
        'artifact_hashes':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'positive_assertions':len(checks),'false_assertions_rejected':len(controls),'exact_regeneration_files':len(equality)},indent=2))

if __name__=='__main__':main()
