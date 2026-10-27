"""Bounded exhaustive checks and independent oracles for the v0.3 continuation."""
from __future__ import annotations
import argparse
from collections import defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util
from itertools import product, combinations
import json
from pathlib import Path
from random import Random
import sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'prior_v0_2'/'src'))
from packet_information import (Matrix,accessible_repair,verify_repair,obstruction_dimension,
                                predictive_closure,packet_transfer,leakage_block,factor_rows,minimal_raw_packets)
from access_graph import build_access_graph,optimal_coloring,decode_from_coloring,restricted_success
from information import FiniteModel,partitions


def require(condition,message='check failed'):
    if not condition:
        raise AssertionError(message)


def expect_error(f,exception=ValueError):
    try:f()
    except exception:return
    raise AssertionError(f'expected {exception.__name__} was not raised')


def adequate(r,f):
    """Fiber oracle, independent of graphs and Gaussian elimination."""
    table={}
    for a,b in zip(r,f):
        if a in table and table[a]!=b:return False
        table[a]=b
    return True


@lru_cache(None)
def subspaces(p,n):
    zero=Matrix.zero(p,0,n)
    seen={zero}
    queue=[zero]
    vectors=tuple(product(range(p),repeat=n))
    for space in queue:
        for v in vectors:
            b=space.stack(Matrix(p,n,(v,))).basis()
            if b not in seen:seen.add(b);queue.append(b)
    return tuple(sorted(seen,key=lambda x:(x.nrows,x.rows)))


def graph_suite():
    cases=impossible=feasible=oracle_codes=oracle_cases=0
    by_n=[]
    for n in range(1,6):
        start=cases
        ps=partitions(n)
        for r,f,u in product(ps,repeat=3):
            g=build_access_graph(r,f,u)
            color=optimal_coloring(g)
            ok=adequate(tuple(zip(r,u)),f)
            require((color is not None)==ok,'graph feasibility differs from fiber oracle')
            cases+=1
            if ok:
                feasible+=1
                decoder=decode_from_coloring(g,color,r,f)
                require(all(decoder[r[i],color[u[i]]]==f[i] for i in range(n)),'graph decoder failed')
            else:
                impossible+=1
                i,j=g.impossible_witness
                require(r[i]==r[j] and u[i]==u[j] and f[i]!=f[j],'invalid access obstruction')
            if n<=4:
                best=None
                for code in partitions(max(u)+1):
                    oracle_codes+=1
                    obs=tuple((r[i],code[u[i]]) for i in range(n))
                    if adequate(obs,f):
                        size=max(code)+1
                        best=size if best is None else min(best,size)
                require(best==(None if color is None else max(color)+1),'chromatic optimum differs from exhaustive code search')
                oracle_cases+=1
        by_n.append({'n':n,'partition_triples':cases-start})
    # Beyond the exhaustive n<=5 graph family: classical odd-cycle boundary.
    states=tuple((i,j) for i in range(5) for j in (i,(i+1)%5))
    r=tuple(i for i,j in states);f=tuple(j for i,j in states)
    g=build_access_graph(r,f,f);c=optimal_coloring(g)
    require(max(c)+1==3,'five-cycle chromatic number')
    success,_,count=restricted_success(r,f,f,(1,)*10,2)
    require(success==Q(9,10) and count==32,'five-cycle approximate optimum')
    return {'partition_triples':cases,'feasible':feasible,'inaccessible':impossible,
            'independent_code_oracle_instances':oracle_cases,'independent_code_partitions':oracle_codes,
            'coverage':by_n,'five_cycle_target_only_two_symbol_success':str(success)}


def linear_suite():
    cases=feasible=inaccessible=state_decodings=oracle_codes=0
    coverage=[]
    for p,n in ((2,0),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3),(5,2)):
        spaces=subspaces(p,n)
        xs=tuple(product(range(p),repeat=n))
        values={s:tuple(s.apply(x) for x in xs) for s in spaces}
        local=0
        for r,f,u in product(spaces,repeat=3):
            rv,fv,uv=values[r],values[f],values[u]
            c=accessible_repair(r,f,u)
            require(verify_repair(c,r,f,u),'algebraic repair certificate invalid')
            ok=adequate(tuple(zip(rv,uv)),fv)
            require(c.feasible==ok,'linear feasibility differs from direct fibers')
            profile=FiniteModel(rv,fv)
            require(profile.kappa()==p**c.deficit_dimension,'linear alphabet differs from counted fiber targets')
            if ok:
                feasible+=1
                for x,a,b,y in zip(xs,rv,uv,fv):
                    message=c.encoder.apply(b)
                    require(c.decoder.apply(a+message)==y,'linear repair decoder failed on state')
                    state_decodings+=1
                # Nonlinear code oracle when the helper has at most four values.
                if n<=2 and len(set(uv))<=4:
                    labels=tuple(dict.fromkeys(uv));ix={v:i for i,v in enumerate(labels)}
                    minimum=len(labels)
                    for code in partitions(len(labels)):
                        oracle_codes+=1
                        if adequate(tuple((a,code[ix[b]]) for a,b in zip(rv,uv)),fv):
                            minimum=min(minimum,max(code)+1)
                    require(minimum==p**c.deficit_dimension,'nonlinear encoder beats claimed minimum')
            else:
                inaccessible+=1
                v=c.witness
                require(not any(r.apply(v)) and not any(u.apply(v)) and any(f.apply(v)),'inaccessible witness invalid')
            local+=1;cases+=1
        coverage.append({'field':p,'dimension':n,'row_spaces':len(spaces),'triples':local})
    # Arbitrary redundant rows, mixed dimensions, and several coefficient fields.
    rng=Random(20261015)
    seeded=1200;random_feasible=0;sampled_state_checks=0
    for _ in range(seeded):
        p=rng.choice((2,3,5,7));n=rng.randrange(0,8)
        def mat():
            return Matrix(p,n,tuple(tuple(rng.randrange(p) for _ in range(n)) for _ in range(rng.randrange(n+3))))
        r,f,u=mat(),mat(),mat()
        c=accessible_repair(r,f,u)
        require(verify_repair(c,r,f,u),'redundant-row certificate failed')
        if c.feasible:
            random_feasible+=1
            for j in range(20):
                x=tuple(rng.randrange(p) for _ in range(n))
                require(c.decoder.apply(r.apply(x)+c.encoder.apply(u.apply(x)))==f.apply(x),'random decoded task wrong')
                sampled_state_checks+=1
    return {'exhaustive_row_space_triples':cases,'feasible':feasible,'inaccessible':inaccessible,
            'exhaustive_repaired_state_checks':state_decodings,'nonlinear_code_partitions':oracle_codes,
            'seeded_redundant_row_cases':seeded,'seeded_feasible':random_feasible,
            'seeded_decoded_state_checks':sampled_state_checks,'coverage':coverage}


def transfer_suite():
    pair_cases=0;cancel_cases=0
    for p in (2,3):
        matrices=[Matrix(p,2,(flat[:2],flat[2:])) for flat in product(range(p),repeat=4)]
        for b1,b2 in product(matrices,repeat=2):
            total=b2@b1
            direct=leakage_block(total,(0,))
            rhs=b2.take_rows((0,)).take_cols((0,)) @ leakage_block(b1,(0,)) + leakage_block(b2,(0,)) @ b1.take_rows((1,)).take_cols((1,))
            require(direct==rhs,'block transport product identity')
            require(direct.rank()<=leakage_block(b1,(0,)).rank()+leakage_block(b2,(0,)).rank(),'rank composition upper bound')
            if leakage_block(b1,(0,)).rank() and leakage_block(b2,(0,)).rank() and not direct.rank():cancel_cases+=1
            pair_cases+=1
    # Independent minimality among all row subspaces for small linear systems.
    closure_cases=minimality_comparisons=state_steps=0
    for p,n in ((2,2),(2,3),(3,2)):
        spaces=subspaces(p,n)
        actions=[Matrix(p,n,tuple(tuple(flat[i*n:(i+1)*n]) for i in range(n))) for flat in product(range(p),repeat=n*n)]
        for t,r in product(actions,spaces):
            c=predictive_closure(r,(t,))
            require(c.decode_initial@c.state==r and c.transitions[0]@c.state==c.state@t,'closure matrix identities')
            require(len(c.rank_history)-1<=n-r.rank(),'closure termination bound')
            for candidate in spaces:
                if factor_rows(r,candidate) is not None and factor_rows(candidate@t,candidate) is not None:
                    require(factor_rows(c.state,candidate) is not None,'closure not smallest adequate invariant row space')
                minimality_comparisons+=1
            for x in product(range(p),repeat=n):
                require(c.transitions[0].apply(c.state.apply(x))==c.state.apply(t.apply(x)),'closure transition state oracle')
                state_steps+=1
            closure_cases+=1
    rng=Random(87234);multi=400
    for _ in range(multi):
        p=rng.choice((2,3,5));n=rng.randrange(1,7)
        actions=tuple(Matrix(p,n,tuple(tuple(rng.randrange(p) for _ in range(n)) for _ in range(n))) for _ in range(2))
        r=Matrix(p,n,tuple(tuple(rng.randrange(p) for _ in range(n)) for _ in range(rng.randrange(n+1))))
        c=predictive_closure(r,actions)
        for t,m in zip(actions,c.transitions):
            require(m@c.state==c.state@t,'multi-action closure identity')
        for _ in range(10):
            x=tuple(rng.randrange(p) for _ in range(n));sx=c.state.apply(x)
            for step in range(10):
                a=rng.randrange(2);x=actions[a].apply(x);sx=c.transitions[a].apply(sx)
                require(sx==c.state.apply(x) and c.decode_initial.apply(sx)==r.apply(x),'multi-action trajectory mismatch')
    return {'exhaustive_two_stage_transfer_pairs':pair_cases,'nonzero_stage_leakages_with_zero_composed_leakage':cancel_cases,
            'exhaustive_single_action_closures':closure_cases,'candidate_subspace_minimality_checks':minimality_comparisons,
            'exhaustive_closed_state_transition_checks':state_steps,'seeded_two_action_systems':multi,
            'seeded_two_action_trajectory_steps':multi*100}


def library_suite():
    import numpy as np
    from komorebi_adapter import backend,export_haar,integer_nodes,complete_prunings,source_receipt,native_integer_packets
    lib=backend();exports=0;basis_vectors=0;pruning_syntheses=0
    rng=Random(419)
    for n in (1,2,4,8,16):
        maxdepth=n.bit_length()-1
        for depth in range(maxdepth+1):
            choices=complete_prunings(depth) if n<=8 else (tuple(format(i,f'0{depth}b') for i in range(2**depth)) if depth else ('',),)
            for leaves in choices:
                a,receipt=export_haar(n,depth,leaves=leaves,p=5)
                require(a.inverse()@a==Matrix.identity(5,n),'library export inverse')
                basis_vectors+=n;exports+=1
                for trial in range(5):
                    x=tuple(rng.randrange(-20,21) for _ in range(n))
                    tree=lib.haar_packet_analyze(np.array(x,dtype=float),depth,normalized=False)
                    out=lib.haar_packet_synthesize(tree,leaves)
                    require(np.array_equal(out,np.array(x)),'native complete-pruning synthesis mismatch')
                    oracle=integer_nodes(x,depth)
                    for path in leaves:
                        require(tuple(tree.coefficient(path))==oracle[path],'native packet differs from integer recurrence')
                    pruning_syntheses+=1
    # The main integrated finite-field experiment: actual library analysis of every
    # small source state, all retained-coordinate masks, and all cyclic shifts.
    n=4;depth=1;observed_cases=library_calls=0;field_counts=[]
    for p in (3,5):
        a,_=export_haar(n,depth,p=p)
        xs=tuple(product(range(p),repeat=n))
        native={}
        for x in xs:
            tree=lib.haar_packet_analyze(np.array(x,dtype=float),depth,normalized=False)
            values=native_integer_packets(x,depth,p=p)
            require(values==a.apply(x),'native analysis/modular export mismatch')
            require(np.array_equal(lib.haar_packet_synthesize(tree),np.array(x)),'native full synthesis mismatch')
            native[x]=values;library_calls+=2
        local=0
        for shift in range(4):
            t=Matrix(p,4,tuple(tuple(int(j==(i+shift)%4) for j in range(4)) for i in range(4)))
            b=packet_transfer(a,t)
            native_future=[]
            for x in xs:
                tx=t.apply(x)
                tree=lib.haar_packet_analyze(np.array(tx,dtype=float),depth,normalized=False)
                vals=native_integer_packets(tx,depth,p=p)
                require(vals==b.apply(native[x]),'actual transformed signal does not commute with packet transfer')
                native_future.append(vals);library_calls+=2
            for mask in product((False,True),repeat=4):
                kept=tuple(i for i,yes in enumerate(mask) if yes)
                r=a.take_rows(kept);f=r@t
                obs=tuple(tuple(native[x][i] for i in kept) for x in xs)
                target=tuple(tuple(v[i] for i in kept) for v in native_future)
                m=FiniteModel(obs,target)
                d=leakage_block(b,kept).rank()
                require(m.kappa()==p**d,'leakage rank differs from native-library fiber cardinality')
                require(m.bayes_error()==Q(p**d-1,p**d),'uniform task error differs from rank prediction')
                require(m.categorical_residual()==m.bayes_error(),'uniform residual differs from rank prediction')
                c=accessible_repair(r,f,a.take_rows(tuple(i for i in range(4) if i not in kept)))
                helper=a.take_rows(tuple(i for i in range(4) if i not in kept))
                require(c.feasible and c.deficit_dimension==d and verify_repair(c,r,f,helper),'packet repair certificate')
                for x,rv,fv in zip(xs,obs,target):
                    require(c.decoder.apply(rv+c.message.apply(x))==fv,'integrated repaired task mismatch')
                observed_cases+=len(xs);local+=1
        field_counts.append({'field':p,'source_states':len(xs),'mask_shift_models':local})
    expect_error(lambda:export_haar(4,1,p=2))
    expect_error(lambda:native_integer_packets((2**53,1),1,p=5))
    expect_error(lambda:native_integer_packets((1.0,2.0),1,p=5))
    # Complete pruning is not packet deletion. The upstream object retains the
    # full tree and original signal, so no erasure test is allowed to pass it.
    tree=lib.haar_packet_analyze(np.array([1.,2.,3.,4.]),1,normalized=False)
    expect_error(lambda:lib.haar_packet_synthesize(tree,('0',)))
    return {'source_receipt':source_receipt(),'exported_complete_pruning_matrices':exports,
            'native_impulse_columns_checked':basis_vectors,'native_pruned_syntheses':pruning_syntheses,
            'native_analysis_calls_in_modular_experiments':library_calls,'modular_observation_task_state_cases':observed_cases,
            'field_coverage':field_counts,'bad_prime_rejected':True,'incomplete_pruning_rejected':True,'native_integer_guard_checked':True,
            'scope':'Actual pinned Haar code with floating execution on exactly representable inputs; separate exact modular adapter. No finite-field arithmetic is attributed to the upstream library.'}


def boundary_suite():
    p=5;r=Matrix(p,4,((1,1,0,0),(0,0,1,1)))
    u=Matrix(p,4,((1,-1,0,0),(0,0,1,-1)))
    t=Matrix(p,4,((0,1,0,0),(0,0,1,0),(0,0,0,1),(1,0,0,0)))
    f=r@t;c=accessible_repair(r,f,u)
    require(c.feasible and c.deficit_dimension==1,'Haar constrained repair dimension')
    raw=minimal_raw_packets(r,f,(u.take_rows((0,)),u.take_rows((1,))))
    require(raw==(0,1),'one raw detail coordinate unexpectedly suffices')
    require(minimal_raw_packets(r,f,(u,))==(0,),'one native detail leaf should contain both needed coordinates')
    failed=accessible_repair(r,f,u.take_rows((0,)))
    require(not failed.feasible and verify_repair(failed,r,f,u.take_rows((0,))),'inaccessible helper did not produce witness')
    # Nonuniform full-support linear example: exact optimum agrees, intermediate
    # budget optimum differs between state-aware and helper-only encoders.
    xs=tuple(product(range(3),repeat=2));obs=tuple(a for a,b in xs);target=tuple(b for a,b in xs)
    weights=(2,2,1,2,1,2,1,2,2)
    model=FiniteModel(obs,target,weights)
    success,_,count=restricted_success(obs,target,target,weights,2)
    require(model.optimal_success(2)==Q(4,5) and success==Q(11,15),'nonuniform intermediate-budget boundary')
    gf3=accessible_repair(Matrix(3,2,((1,0),)),Matrix(3,2,((0,1),)),Matrix(3,2,((0,1),)))
    require(gf3.feasible and gf3.deficit_dimension==1,'linear exact optimum should remain three symbols')
    # A corrupted encoder certificate must not be trusted because construction returned PASS.
    from dataclasses import replace
    broken=replace(c,encoder=Matrix.zero(p,1,2))
    require(not verify_repair(broken,r,f,u),'mutated encoder certificate was accepted')
    # Invalid algebraic domains and API shapes.
    invalid=[lambda:Matrix(4,1,((1,),)),lambda:Matrix(5,1,((True,),)),lambda:Matrix(5,1,((1.0,),)),
             lambda:Matrix(5,2,((1,),)),lambda:Matrix(5,-1,()),lambda:Matrix(5,1,((1,),)).apply((True,)),
             lambda:Matrix.identity(5,2)@Matrix.identity(3,2),lambda:Matrix.identity(5,2)@Matrix.identity(5,3),
             lambda:Matrix.zero(5,2,2).inverse(),lambda:leakage_block(Matrix.identity(5,2),(0,0)),
             lambda:predictive_closure(r,(Matrix.identity(3,4),)),lambda:minimal_raw_packets(r,f,(u,)*21),
             lambda:build_access_graph((),(),()),lambda:restricted_success((0,),(0,),(0,),(0,),1)]
    for v in invalid:expect_error(v)
    # Energy is not task information. Dyadic scaling makes the runtime signal
    # values exactly representable while discarded energy tends to zero.
    import numpy as np
    from komorebi_adapter import backend
    lib=backend();energy_rows=[]
    for k in (0,4,12,24):
        eps=2.0**(-k);rs=[];fs=[];energies=[]
        for a,b in product((-1,1),repeat=2):
            x=np.array([eps*a,-eps*a,eps*b,-eps*b])
            tree=lib.haar_packet_analyze(x,1,normalized=False)
            rs.append(tuple(tree.coefficient('0')));fs.append((a,b))
            energies.append(float(np.vdot(tree.coefficient('1'),tree.coefficient('1'))))
        m=FiniteModel(tuple(rs),tuple(fs))
        require(m.kappa()==4 and m.bayes_error()==Q(3,4),'small-energy information witness')
        require(all(e==8*eps*eps for e in energies),'discarded detail energy formula')
        energy_rows.append({'epsilon':eps,'detail_energy':energies[0],'missing_bits':2,'bayes_error':'3/4'})
    require(lib.entropy_cost(np.array([1.]))==0 and lib.entropy_cost(np.array([999.]))==0,'single-coordinate energy entropy semantics')
    return {'raw_detail_coordinates_needed':len(raw),'native_detail_leaf_packets_needed':1,'linear_message_coordinates_needed':1,
            'inaccessible_helper_witness':failed.witness,'nonuniform_state_aware_success':'4/5',
            'nonuniform_helper_only_success':str(success),'nonuniform_encoders_enumerated':count,
            'mutated_encoder_rejected':True,'invalid_inputs_rejected':len(invalid),'energy_counterexamples':energy_rows}


SUITES={'graph':graph_suite,'linear_access':linear_suite,'transfer_closure':transfer_suite,'library':library_suite,'boundaries':boundary_suite}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite',choices=tuple(SUITES)+('all',),default='all')
    args=parser.parse_args();names=tuple(SUITES) if args.suite=='all' else (args.suite,)
    (ROOT/'reports').mkdir(exist_ok=True)
    for name in names:
        start=time.perf_counter();print('RUN',name,flush=True)
        suffix='_optimized' if sys.flags.optimize else ''
        try:
            result=SUITES[name]()
            report={'suite':name,'status':'PASS','python':sys.version,'optimization_level':sys.flags.optimize,
                    'elapsed_seconds':round(time.perf_counter()-start,3),**result}
        except Exception:
            report={'suite':name,'status':'FAIL','optimization_level':sys.flags.optimize,
                    'elapsed_seconds':round(time.perf_counter()-start,3),'traceback':traceback.format_exc()}
        (ROOT/'reports'/f'v03_{name}{suffix}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2),flush=True)
        if report['status']!='PASS':return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
