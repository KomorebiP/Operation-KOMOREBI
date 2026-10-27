from pathlib import Path
import sys,json,random,hashlib,copy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'python'))
from repair_certificates import *
import sympy as sp

out=root/'examples/corpus';out.mkdir(parents=True,exist_ok=True)
gen=root/'lean/KomorebiRepair/Generated';gen.mkdir(exist_ok=True)
# Previous development singleton files are preserved in attempt snapshots only.
for name in ['WorkedInput.lean','WorkedCertificate.lean']:
    p=gen/name
    if p.exists():p.unlink()
rng=random.Random(2026101903)
def rand(r,c):return Mat.of([[F(rng.randint(-4,4),rng.randint(1,5)) for _ in range(c)] for _ in range(r)],c)
def srank(A):return sp.Matrix(A.rows,A.cols,[sp.Rational(x.numerator,x.denominator) for row in A.data for x in row]).rank()
fixed=[
 ('worked',Mat.of([[1],[0],[0]]),Mat.of([[2,4],[1,2],[1,2]])),
 ('fractional',Mat.of([[F(2,3)],[F(4,3)]]),Mat.of([[F(1,2)],[F(5,6)]])),
 ('empty_target',Mat.zero(0,2),Mat.zero(0,3)),
 ('empty_original',Mat.zero(3,0),Mat.of([[1,0],[0,1],[0,0]])),
 ('empty_residuals',Mat.of([[1],[2],[3]]),Mat.zero(3,0)),
 ('zero_residual',Mat.of([[1],[2],[3]]),Mat.zero(3,2)),
 ('surjective',Mat.eye(3),Mat.of([[1,3],[2,1],[3,7]])),
 ('zero_original_matrix',Mat.zero(3,2),Mat.of([[1,0],[0,1],[1,1]])),
 ('all_empty',Mat.zero(0,0),Mat.zero(0,0)),
 ('nontrivial_rank_two',Mat.of([[1,2],[2,4],[0,0],[0,0]]),Mat.of([[1,0],[0,1],[1,2],[0,1]])),
]
cases=list(fixed)
for i in range(254):
    m=rng.randrange(0,6);n=rng.randrange(0,6);s=rng.randrange(0,5)
    # Force varied ranks instead of generating mostly surjective matrices.
    k=rng.randrange(min(m,n)+1)
    D=rand(m,k)@rand(k,n);R=rand(m,s)
    cases.append((f'random_{i:03d}',D,R))
records=[]; exports=[];trace=[]
for idx,(label,D,R) in enumerate(cases):
    p=problem(D,R);local=[];c=construct(p,local)
    ranks=(srank(D),srank(D.join(R)));expected=ranks[1]-ranks[0]
    require(c['t']==expected,'Independent SymPy rank mismatch')
    record={'id':idx,'label':label,'m':D.rows,'n':D.cols,'s':R.cols,'t':c['t'],
            'rank_D':ranks[0],'rank_DR':ranks[1],'problem_sha256':digest(p),'certificate_sha256':digest(c),
            'identities':check_certificate(p,c),'independent_rank_check':True}
    records.append(record)
    if idx<10 or (idx>=10 and len(exports)<24 and D.rows<=4 and D.cols<=4):
        caseid=len(exports);namespace=f'Case{caseid:03d}'
        exports.append({'case':caseid,'label':label,'problem':p,'certificate':c,'namespace':namespace})
        (out/f'{namespace}_input.json').write_bytes(canonical(p));(out/f'{namespace}_certificate.json').write_bytes(canonical(c))
        trace+=['\n=== '+namespace+' / '+label+' ===',*local]
(root/'evidence/python_cases.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in records), encoding="utf-8")
(root/'evidence/certificate_trace.txt').write_text('\n'.join(trace)+'\n', encoding="utf-8")
(root/'evidence/python_summary.json').write_text(json.dumps({'status':'PASS','cases':len(cases),'exported_cases':len(exports),
        'seed':2026101903,'sympy_version':sp.__version__,'independent_sympy_ranks':len(cases)},indent=2), encoding="utf-8")
module_names=[];echoimports=[];echos=[]
for batch in range(4):
    group=exports[batch*6:(batch+1)*6];iname=f'Inputs{batch:02d}';cname=f'Certificates{batch:02d}'
    itext='import KomorebiRepair.Wire\n'+'\n'.join(emit_input(x['problem'],x['namespace']).split('\n',1)[1] for x in group)
    ctext=f'import KomorebiRepair.Generated.{iname}\n'+'\n'.join(emit_certificate(x['problem'],x['certificate'],x['namespace'],f'KomorebiRepair.Generated.{iname}').split('\n',1)[1] for x in group)
    (gen/(iname+'.lean')).write_text(itext, encoding="utf-8");(gen/(cname+'.lean')).write_text(ctext, encoding="utf-8")
    module_names += ['KomorebiRepair.Generated.'+iname,'KomorebiRepair.Generated.'+cname]
    echoimports.append('import KomorebiRepair.Generated.'+iname)
    for x in group:
        n=x['namespace'];echos.append(f'#eval IO.println ("{{\\"id\\":{x["case"]},\\"D\\":" ++ matrixJson {n}.D ++ ",\\"R\\":" ++ matrixJson {n}.R ++ "}}")')
(root/'lean/InputEcho.lean').write_text('\n'.join(echoimports)+'\nopen KomorebiRepair.RationalCertificates\n'+'\n'.join(echos)+'\n', encoding="utf-8")
(root/'evidence/export_index.json').write_text(json.dumps([{'case':x['case'],'label':x['label'],'namespace':x['namespace'],'t':x['certificate']['t'],'input':f'examples/corpus/{x["namespace"]}_input.json','certificate':f'examples/corpus/{x["namespace"]}_certificate.json','problem_sha256':digest(x['problem'])} for x in exports],indent=2), encoding="utf-8")
(root/'evidence/generated_modules.json').write_text(json.dumps(module_names,indent=2), encoding="utf-8")
# Mutation controls use the very same compiled original Case000 input.
neg=root/'lean/certificate_negative_controls';neg.mkdir(exist_ok=True)
x=exports[0]
for key,label in [('P','BrokenSplit'),('G','BrokenFactor'),('J','FalseDimension'),('U','FalseOutput')]:
    c=copy.deepcopy(x['certificate']);a=Mat.from_wire(c['matrices'][key]);rows=[list(r) for r in a.data];rows[0][0]+=1;c['matrices'][key]=Mat.of(rows,a.cols).to_wire()
    text=emit_certificate(x['problem'],c,'Case000','KomorebiRepair.Generated.Inputs00',check=False)
    (neg/(label+'.lean')).write_text(text, encoding="utf-8")
# Validity must reject a zero denominator even when its quotient value is zero.
(neg/'ZeroDenominator.lean').write_text('import KomorebiRepair.Wire\nopen KomorebiRepair.RationalCertificates\ntheorem false_valid : WireMatrixValid (Matrix.of ![![(0,0)]] : WireMatrix 1 1) := by decide +kernel\n', encoding="utf-8")
# A zero detector with a zero-dimensional obstruction is not complete.
(neg/'HiddenObstruction.lean').write_text('import KomorebiRepair.Wire\nopen KomorebiRepair.RationalCertificates\ntheorem concealed : checkOptimalConstruction (0 : Mat 1 0) (1 : Mat 1 1) (0 : Mat 0 1) (0 : Mat 1 0) (0 : Mat 0 1) (0 : Mat 0 0) (0 : Mat 0 1) (0 : Mat 0 0) (0 : Mat 1 0) = true := by decide +kernel\n', encoding="utf-8")
print(json.dumps({'python_cases':len(cases),'exported':len(exports),'batches':4,'modules':module_names},indent=2))
