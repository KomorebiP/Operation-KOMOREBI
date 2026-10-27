#!/usr/bin/env python3
"""Independent frozen guide comparison. Does not import or run its generator.

Exact scientific values are compared with freshly reproduced source certificates,
an independent audit, and the complete Block70 result hash. Drawing coordinates
are not mathematical field coordinates. This is not an arithmetic realization.
"""
import argparse, hashlib, json, math, platform
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
CHECKS = []

def read(path):
    return json.loads((ROOT/path).read_text())

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def check(label, condition):
    if not condition:
        raise AssertionError(label)
    CHECKS.append(label)

def pair_mul(x, y):
    a,b=x; c,d=y
    return ((a*c+5*b*d)%7, (a*d+b*c)%7)

def mv(matrix, vector):
    return [sum(x*y for x,y in zip(row,vector))%7 for row in matrix]

def main():
    args=argparse.ArgumentParser()
    args.add_argument('--output',required=True)
    opts=args.parse_args()
    data=read('visual/data.json')
    figures={int(k[:2]):v['values'] for k,v in data['figures'].items()}
    pins=read('visual/SOURCE_PINS.json')
    for path,expected in pins['files'].items():
        check('final source pin '+path,sha(path)==expected)
    check('final corrected PDF pin',pins['files']['pdf/Komorebi_Beal_Visual_Guide_v1.0.pdf']=='74ff9dc7d9b2e6cf6f1372c3ec0b7396630d9e26cb1b5f3b8150da8d58cd0c27')
    check('final corrected generator pin',pins['files']['visual/figures.py']=='3452c8bb3e02ea5f690566d1d53c1145372b5bd18d443aa8cf5363101816b494')
    check('active final bounded visual run',pins['active_manifest']=='visual/computations/atlas-final-v1.0b/manifest.json')
    primary=read('evidence/computation/portable80-run/primary80.json')
    finite=read('evidence/computation/portable80-run/finite_inputs.json')
    independent=read('evidence/computation/independent80-run/audit.json')
    check('fresh independent exact audit passed',independent['status']=='PASS_INDEPENDENT_EXACT_AUDIT')
    check('canonical visual primary is complete fresh result',read('visual/inputs/block80_primary80.json')==primary)
    check('canonical visual finite inputs are complete rebuilt inputs',read('visual/inputs/block80_finite_inputs.json')==finite)
    check('fresh supplied target evaluator complete equality',read('visual/inputs/block80_target_evaluator80.json')==read('evidence/computation/portable80-run/target_evaluator80.json'))
    check('all 24 figures present',set(figures)==set(range(1,25)))
    v=figures[1]
    check('worked nonprimitive example terms',[a**b for a,b in zip(v['bases'],v['exponents'])]==v['terms'])
    check('worked nonprimitive equality',v['terms'][0]+v['terms'][1]==v['terms'][2])
    check('worked nonprimitive gcd',math.gcd(*v['bases'])==v['common_gcd']==3)
    v=figures[2]
    check('absorbed exponents',[a*b for a,b in zip(v['reduced_signature'],v['new_base_powers'])]==v['source_signature'])
    check('reduced illustrated signature',v['reduced_signature']==[4,3,7])
    v=figures[4]
    t=sp.symbols('t');s=1-t
    a,b,c=[t**x*s**y for x,y in v['parameter_exponents']]
    check('universal rational parametrization symbolic identity',sp.expand(a**3+b**5-c**7)==0)
    check('weighted scale common degree',[x*y for x,y in zip([3,5,7],v['weighted_scale'])]==[v['homogeneous_degree']]*3)
    for sector in figures[3]['active_sectors']:
        m,n=sector['m'],sector['n']
        lam=-sp.Rational(m,3) if m>0 else -sp.Rational(4*n,5) if n>0 else -sp.Rational(8*m,7)
        valuations=[x*m+y*n+w*lam for (x,y),w in zip(v['parameter_exponents'],v['weighted_scale'])]
        check('primitive valuation sector '+str((m,n)),valuations==sector['output'])
    v=figures[5];aa,bb,cc=v['coefficients']
    check('local coefficient dyadic test',(aa+bb)%8==0 and cc%2==0 and v['dyadic_C_even'])
    check('local odd coefficient residues',str((bb*cc)%3)==str(v['odd_tests']['3']) and str((aa*cc)%5)==str(v['odd_tests']['5']))
    check('coefficient equation powers',(aa**3,bb**5,cc**7)==(27,3125,128))
    check('coefficient field irreducibility',5 not in {x*x%7 for x in range(7)})
    trace=read('visual/inputs/block47_modular_correlations.json')
    roots=set()
    # Evaluate the two coordinates of every source polynomial directly, rather
    # than calling the visual field arithmetic or trusting its stored root count.
    for source in trace['q11_regular_point_counts']:
        co=source['trace_polynomial']+[0]*(3-len(source['trace_polynomial']))
        C,B,A=co
        for x in range(49):
            a,b=x%7,x//7
            if (A*(a*a+5*b*b)+B*a+C)%7==0 and (2*A*a*b+B*b)%7==0:
                roots.add(x)
    pairs=[[x,x%7+7*(-(x//7)%7)] for x in sorted(roots)]
    v=figures[7]
    check('q11 roots reconstructed in coordinate equations',sorted(roots)==v['root_codes']==data['q11_roots'])
    check('q11 exact conjugate pairs',pairs==v['conjugate_pairs']==data['q11_conjugate_pairs'])
    check('q11 joint versus Cartesian counts',(len(pairs),len(roots)**2,len(roots)**2-len(pairs))==(v['joint_count'],v['marginal_pair_count'],v['extra_pairs']))
    plus=[];minus=[]
    for a in range(7):
        for b in range(7):
            x=(a,b);power=(1,0)
            for _ in range(7):power=pair_mul(power,x)
            check('coefficient Frobenius '+str(x),power==(a,-b%7))
            if power==x:plus.append(x)
            if power==(-a%7,-b%7):minus.append(x)
    check('plus and minus F7 lines',len(plus)==len(minus)==7 and figures[10]['plus_dimension_F7']==figures[10]['minus_dimension_F7']==1)
    check('reported Frobenius tested range',figures[10]['elements_checked']==49)
    check('depth precision window',figures[8]['precisions']==[7,49,343] and figures[8]['actual_frozen_patterns_depth']==1)
    theta,beta,cval,h=sp.symbols('theta beta c h')
    M=cval*sp.Matrix([[theta,-theta**2],[1,-theta]])
    check('local packet square-zero symbolic identity',M*M==sp.zeros(2))
    check('local toric elimination symbolic identity',sp.expand(cval*(theta*beta-h)-beta*(theta*cval)+h*cval)==0)
    refinement=read('evidence/computation/readerqa_inputs/refinement70.json')
    comparison=read('evidence/computation/portable70-run/report.json')['complete_json_comparisons']['work70/verification/refinement70.json']
    check('Block70 result freshly reproduced complete hash',comparison['complete_json_equal'] and sha('evidence/computation/readerqa_inputs/refinement70.json')==comparison['sha256_generated'])
    check('Block70 survivor total',refinement['survivor_count']==len(refinement['survivors'])==figures[12]['count']==8)
    union=primary['prime_order']
    check('complete support universe',figures[11]['prime_order']==union and union==sorted({q for p in finite['patterns'].values() for q in p['support']}))
    scales={q:primary['residue_data'][str(q)]['beta_inertia_scale'] for q in union}
    check('display inertia scales from fresh arithmetic',figures[13]['primes']==union and figures[13]['factors']==[scales[q] for q in union])
    for idx,name in enumerate('ABCD'):
        p=primary['patterns'][name];f=finite['patterns'][name];q=independent['patterns'][name]
        row=[int(x in f['support']) for x in union]
        check(name+' support grid exact',row==figures[11]['support_indicator'][idx] and sum(row)==figures[11]['cardinalities'][idx]==9)
        check(name+' complete displayed data',{key:p[key] for key in data['pattern_data'][name]}==data['pattern_data'][name])
        matching=[entry for entry in refinement['survivors'] if [x for x,v in zip(entry['columns'],entry['inertia']) if v]!=[] and [x for x,v in zip(entry['columns'],entry['inertia']) if v]==f['support']]
        expected={21,28} if name in 'AB' else {7,42}
        check(name+' coefficient tuple pair from fresh70',len(matching)==2 and {e['alpha'][0] for e in matching}==expected and all(e['alpha'][1:]==[figures[12]['ratio'],figures[12]['a5']] for e in matching))
        check(name+' exact original inertia carried from70',all([v for v in e['inertia'] if v]==f['inertia'] for e in matching))
        check(name+' independently audited rank/dimensions',p['rank']==q['ranks_and_exact_integer_minors']['A']['rank']==figures[19]['rank'][idx] and q['homogeneous_dimension']==figures[19]['kernel'][idx] and q['obstruction_dimension']==figures[19]['cokernel'][idx])
        check(name+' independent localization ranks',q['ranks_and_exact_integer_minors']['L']['rank']==figures[17]['L_rank']==14 and q['ranks_and_exact_integer_minors']['J']['rank']==figures[17]['J_rank']==10)
        check(name+' localization shapes',[len(p['localization_relations']),len(p['localization_relations'][0])]==figures[17]['L_shape'] and [len(p['localization_image_basis']),len(p['localization_image_basis'][0])]==figures[17]['J_shape'])
        check(name+' local coordinate dimensions',len(p['local_labels'])==figures[16]['total']==24 and p['local_labels'][:6]==['2:F','3:F','5:F','7:phi','7:3','7:7'] and p['global_H1_dimension_over_k']==figures[17]['H1_dimension_k'])
        for toric in p['toric_values']:
            prime=toric['q'];Q=prime**2  # all support primes are inert in K; cyclotomic residue degree is a different datum
            check(name+' exact toric row '+str(prime),toric['c']==scales[prime]*f['inertia'][f['support'].index(prime)]%7 and toric['h']==((Q-1)//7)%7 and toric['toric_rhs']==-toric['h']*toric['c']%7)
        check(name+' no arithmetic target in fresh record',p['actual_affine_target_computed'] is False and p['particular_cochain_computed'] is False)
    v=figures[14]
    check('all norm-q conductor data',v['norm_primes']==sorted(int(x) for x in finite['conductor_generators']) and v['norms']==primary['conductor_generator_norms'] and all(int(q)==n for q,n in v['norms'].items()))
    check('own conductor checks agree independent audit',{row['q'] for row in independent['self_conductor_units']}==set(v['norm_primes']))
    check('PatternC complete displayed matrix',figures[18]['matrix']==primary['patterns']['C']['global_to_constraint_matrix'] and figures[18]['shape']==[15,10] and figures[18]['fixed_rows']==6 and figures[18]['toric_rows']==9)
    old=finite['old_fixed_and_minus_constraints']['patterns']['C'];A=primary['patterns']['C']['global_to_constraint_matrix'];support=primary['patterns']['C']['support']
    vectors=[old['kernel_basis'][1],old['kernel_basis'][3]]
    minor=[[mv([A[6+support.index(prime)]],[0]+vector)[0] for vector in vectors] for prime in [197,337]]
    check('PatternC improvement minor derived from old vectors',minor==figures[20]['matrix'])
    check('PatternC exact determinant and dimensions',int(sp.Matrix(minor).det())%7==figures[20]['det_mod7']==1 and len(old['kernel_basis'])==figures[20]['old_kernel_dimension']==4 and independent['patterns']['C']['homogeneous_dimension']==figures[20]['new_kernel_dimension']==2 and independent['patterns']['C']['remaining_character_support']==figures[20]['remaining_support'])
    v=figures[22];N=primary['patterns']['C']['dual_obstruction_basis']
    translated=[(x-y)%7 for x,y in zip(v['t'],mv(A,v['z0']))]
    check('synthetic translated target exact',translated==v['translated_t'])
    check('synthetic origin invariant nonzero obstruction',mv(N,v['t'])==mv(N,translated)==v['obstruction'] and any(v['obstruction']))
    check('synthetic label and authentication boundary',v['kind']=='synthetic' and v['arithmetic_authenticated'] is False and figures[21]['actual_arithmetic_target_computed'] is False and figures[24]['full_beal_open'] is True)
    correction=read('evidence/computation/unit-domain71-run/correction.json')
    actual=sum(1 for a in range(49) for b in range(49) if (a%7,b%7)!=(0,0))
    check('correct actual Block71 unit metadata',actual==49*48==2352==correction['actual_enumerated_unit_domain'] and correction['legacy_primary_unit_domain']==2304 and correction['historical_bytes_changed'] is False)
    body=(ROOT/'visual/body.tex').read_text();generator=(ROOT/'visual/figures.py').read_text()
    check('guide avoids incorrect legacy unit metadata','2304' not in body and '2304' not in generator and '2304' not in json.dumps(data))
    check('guide corrected primewise bound caption','every beta-ramifying rational prime at most 2000' in body and 'does not bound every divisor' in body)
    check('upper support not bounded',figures[23]['global_upper_support_bounded'] is False)
    check('bare primitive numerical values absent',figures[15]['values_computed'] is False)
    chapter=(ROOT/'paper/chapters/23_evidence.tex').read_text()
    check('final reader PDF pinned',sha('pdf/Komorebi_Beal_Conjecture_Piece_v1.0.pdf')=='3b1911d594d7c68bdfccc5d4788d4a6a33df1ce968ea226ca053f020c0b03ebf')
    check('reader finite input correction explicit','49^2-7^2=2352' in chapter and '2304' in chapter and 'original record is preserved' in chapter)
    check('reader portable69 outcome and archival boundary','all seventeen result JSONs' in chapter and '840 second resource timeout' in chapter and 'That attempt is inconclusive' in chapter)
    check('reader wrapper67 interpretation disclosed','PASS\\_DECLARED\\_CHECKS' in chapter and 'failed wrapper record is retained' in chapter and 'exit zero' in chapter)
    check('reader no arithmetic target and zero exclusion','No actual affine target is authenticated' in chapter and 'Exactly zero residual patterns are excluded' in chapter)
    out=ROOT/opts.output;out.mkdir(parents=True,exist_ok=True)
    result={'status':'PASS_INDEPENDENT_READER_DATA_QA','check_count':len(CHECKS),'checks':CHECKS,'software':{'python':platform.python_version(),'sympy':sp.__version__},'guide_pdf_sha256':sha('pdf/Komorebi_Beal_Visual_Guide_v1.0.pdf'),'reader_pdf_sha256':sha('pdf/Komorebi_Beal_Conjecture_Piece_v1.0.pdf'),'reader_evidence_chapter_sha256':sha('paper/chapters/23_evidence.tex'),'generator_sha256':sha('visual/figures.py'),'data_sha256':sha('visual/data.json'),'source_pins_sha256':sha('visual/SOURCE_PINS.json'),'figures_reviewed':list(range(1,25)),'originals_mutated':False,'actual_arithmetic_target_authenticated':False,'patterns_eliminated':0,'review_limits':['Exact data/source and fresh result comparisons. Conditional written duality and integral theorems need their separate proof audits.','No new q11 curve point-count enumeration; exact roots are reconstructed from the authenticated source polynomials.','Drawing geometry and color are illustrative; separate final rendered-PDF review checks layout.','Generator is read as source, not imported or executed by this independent audit.']}
    (out/'reader_data_qa.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],len(CHECKS),'checks')

if __name__=='__main__':main()
