"""Seven worked, exactly checked examples. Standard library only.

    python examples/worked_examples.py
Results are written to reports/worked_examples.json. See WORKED_EXAMPLES.md
for the hand derivations. All structural state spaces are enumerated in full.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from information import FiniteModel, predictive_refinement, matvec, rank_mod


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def history(x, horizon):
    outputs=[]
    for _ in range(horizon+1):
        outputs.append(x[0])
        a,b,c=x
        x=(b,c,a^b)
    return tuple(outputs)


def dynamics_example():
    xs=tuple(product(range(2),repeat=3))
    weights=tuple((3 if b==0 else 1)*(7 if c==0 else 1) for a,b,c in xs)
    numeric=tuple(4*a+2*b+c for a,b,c in xs)
    rows=[]
    models=[]
    for h in range(3):
        m=FiniteModel(tuple(history(x,h) for x in xs),xs,weights)
        row={'horizon':h,**m.profile(),'numeric_mse':str(m.mse(numeric)),
             'entropy_60_digit':str(m.entropy_certificate().decimal())}
        rows.append(row);models.append(m)
    check([m.repair_bits() for m in models]==[2,1,0],'dynamics bits')
    check([m.bayes_error() for m in models]==[Q(11,32),Q(1,8),Q(0)],'dynamics errors')
    check([m.mse(numeric) for m in models]==[Q(55,64),Q(7,64),Q(0)],'dynamics MSE')
    check([m.categorical_residual() for m in models]==[Q(131,256),Q(7,32),Q(0)],'dynamics categorical residual')
    losses=[]
    for coarse,fine in zip(models,models[1:]):
        mse_drop=coarse.mse(numeric)-fine.mse(numeric)
        v_drop=coarse.categorical_residual()-fine.categorical_residual()
        check(mse_drop==coarse.projection_distance(fine,numeric),'MSE exact energy drop')
        check(v_drop==coarse.categorical_projection_distance(fine),'categorical exact energy drop')
        losses.append({'mse_drop':str(mse_drop),'categorical_drop':str(v_drop)})
    t=tuple(xs.index((b,c,a^b)) for a,b,c in xs)
    p,parts=predictive_refinement(tuple(x[0] for x in xs),(t,))
    check([len(set(v)) for v in parts]==[2,4,8],'dynamics partition sequence')
    budget=[]
    for m in range(1,5):
        code,decoder=models[0].budget_repair(m)
        actual=Q(sum(w for i,w in enumerate(weights) if decoder[xs[i][0:1],code[i]]==xs[i]),sum(weights))
        check(actual==models[0].optimal_success(m),'budget encoder attainment')
        budget.append({'alphabet':m,'success':str(actual),'error':str(1-actual)})
    check([r['success'] for r in budget]==['21/32','7/8','31/32','1'],'budget curve')
    return {'states':xs,'weights':weights,'observation_rows':rows,'projection_drops':losses,
            'strict_partition_sizes':[len(set(v)) for v in parts],'budget_curve':budget}


def signal_example():
    p=5;xs=tuple(product(range(p),repeat=4))
    R=((1,1,0,0),(0,0,1,1));D=((1,-1,0,0),(0,0,1,-1))
    rows=[]
    for k in range(3):
        obs=tuple(matvec(R+D[:k],x,p) for x in xs)
        model=FiniteModel(obs,xs)
        rows.append({'detail_channels':k,'observation_rank':rank_mod(R+D[:k],p,4),**model.profile()})
    check([r['kappa'] for r in rows]==[25,5,1],'GF5 residual dimensions')
    reconstructed=0
    for x in xs:
        s0,s1=matvec(R,x,p);d0,d1=matvec(D,x,p)
        recovered=(3*(s0+d0)%p,3*(s0-d0)%p,3*(s1+d1)%p,3*(s1-d1)%p)
        check(recovered==x,'explicit signal inverse');reconstructed+=1
    sample=(4,1,3,2)
    return {'field':5,'rows':rows,'states_reconstructed':reconstructed,
            'sample':{'x':sample,'sums':matvec(R,sample,p),'details':matvec(D,sample,p)},
            'characteristic_two_counterexample':{'states':[(1,0,0,0),(0,1,0,0)],
                'common_combined_observation':matvec(R+D,(1,0,0,0),2),
                'combined_rank':rank_mod(R+D,2,4)}}


def arithmetic_example():
    xs=tuple(range(60));rows=[]
    for label,obs in [('mod12',tuple(x%12 for x in xs)),
                      ('mod12_and_mod6',tuple((x%12,x%6) for x in xs)),
                      ('mod12_and_mod5',tuple((x%12,x%5) for x in xs))]:
        rows.append({'observation':label,**FiniteModel(obs,xs).profile()})
    check([r['kappa'] for r in rows]==[5,5,1],'arithmetic repair')
    for x in xs:
        r,c=x%12,x%5
        check(r+12*((3*(c-r))%5)==x,'CRT inverse')
    return {'rows':rows,'explicit_reconstructions_checked':60,
            'sample':{'x':47,'mod12':11,'mod5':2,'lift_digit':3},
            'inconsistent_pair':{'x_mod4':0,'x_mod6':1,'solutions_mod12':[]}}


def parity_example():
    xs=tuple(product(range(2),repeat=2));f=tuple(a^b for a,b in xs)
    rows=[]
    for label,obs in [('none',(0,)*4),('A',tuple(a for a,b in xs)),
                      ('B',tuple(b for a,b in xs)),('A_and_B',xs)]:
        model=FiniteModel(obs,f)
        rows.append({'observation':label,**model.profile(),'task_mutual_information_bits':1-model.entropy()})
    check([r['task_mutual_information_bits'] for r in rows]==[0,0,0,1],'XOR synergy')
    return {'rows':rows}


def noisy_example():
    states=tuple(product(range(2),repeat=3))
    # (F,R,S), fair F; crossover 1/10 then 1/5. Integer denominator 100.
    weights=tuple((9 if f==r else 1)*(4 if r==s else 1) for f,r,s in states)
    f=tuple(x[0] for x in states)
    R=FiniteModel(tuple(x[1] for x in states),f,weights)
    S=FiniteModel(tuple(x[2] for x in states),f,weights)
    check(R.bayes_error()==Q(1,10) and S.bayes_error()==Q(13,50),'noisy risk')
    check(R.mse(f)==Q(9,100) and S.mse(f)==Q(481,2500),'noisy MSE')
    check(S.mse(f)-R.mse(f)==Q(64,625)==R.projection_distance(S,f),'stochastic projector identity')
    check(S.categorical_residual()-R.categorical_residual()==Q(128,625)
          ==R.categorical_projection_distance(S),'stochastic categorical identity')
    rows=[{'observation':name,'error':str(m.bayes_error()),'entropy_bits':m.entropy(),
           'numeric_mse':str(m.mse(f)),'categorical_residual':str(m.categorical_residual())}
          for name,m in [('R',R),('S',S)]]
    return {'states':states,'weights':weights,'rows':rows,'numeric_loss_increment':'64/625',
            'categorical_loss_increment':'128/625','markov_assumption':'F -> R -> S'}


def restricted_encoder_example():
    states=tuple((edge,v) for edge in range(5) for v in (edge,(edge+1)%5))
    r=tuple(x[0] for x in states);f=tuple(x[1] for x in states)
    model=FiniteModel(r,f)
    code,decoder=model.exact_repair()
    check(all(decoder[r[i],code[i]]==f[i] for i in range(10)),'state-aware exact code')
    results=[]
    for m in (1,2,3):
        best=Q(0);exact=0;example=None
        for mapping in product(range(m),repeat=5):
            joined=tuple((edge,mapping[v]) for edge,v in states)
            score=1-FiniteModel(joined,f).bayes_error()
            if score>best:
                best,example=score,mapping
            exact+=score==1
        results.append({'alphabet':m,'target_only_best_success':str(best),
                        'exact_encoders':exact,'best_mapping':example,
                        'state_aware_best_success':str(model.optimal_success(m))})
    check([x['target_only_best_success'] for x in results]==['1/2','9/10','1'],'restricted-encoder scores')
    return {'states':states,'kappa':model.kappa(),'state_aware_code':code,'rows':results,
            'minimum_target_only_alphabet':3,'minimum_state_aware_alphabet':2}


def gluing_example():
    states=tuple(product(range(2),repeat=3))
    tests=(lambda x:(x[0]^x[1])==0,lambda x:(x[1]^x[2])==0,lambda x:(x[2]^x[0])==1)
    pair_solutions={str(k):[x for x in states if all(t(x) for i,t in enumerate(tests) if i!=k)] for k in range(3)}
    solutions=[x for x in states if all(t(x) for t in tests)]
    check([len(x) for x in pair_solutions.values()]==[2,2,2] and not solutions,'gluing counterexample')
    return {'equations':['x1 XOR x2 = 0','x2 XOR x3 = 0','x3 XOR x1 = 1'],
            'solutions_when_equation_index_is_omitted':pair_solutions,'global_solutions':solutions,
            'certificate':'XOR all three equations: 0 = 1'}


def main():
    data={'version':'0.2.0','status':'PASS',
          'dynamics':dynamics_example(),'signal_GF5':signal_example(),
          'arithmetic_CRT':arithmetic_example(),'XOR_synergy':parity_example(),
          'noisy_Markov':noisy_example(),'restricted_encoder':restricted_encoder_example(),
          'global_assembly':gluing_example()}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports'/'worked_examples.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(data,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
