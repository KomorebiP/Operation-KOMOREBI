"""Finite exact controls for the separate written regular classification.
Author: Komorebi P. Counts below do not constitute whole-topology margins.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations,product,permutations
from pathlib import Path
import json,subprocess,sys,tempfile
from exact_phasor import C,response as reference
from phasor_unit_voltage import response
from natural_graph_polynomials import pair,value
from real_root_constraints import derivative
from coefficient_fiber import multiply
from pure_type_margins import P as PH,Q as QH,SAMPLES,gamma
from balanced_obstructions import controls
from resonant_mode_face import find_modes
import regular_balanced as rb
from regular_support_inventory import inventory

def ordered_support_crosscheck(report):
    """Ordered-edge/BFS/adjacency-word check of the multiset/union-find iterator."""
    labeled=set();words=set();sequences=0
    def word(es,n):
        A=[[0]*n for _ in range(n)]
        for u,v in es:A[u][v]+=1;A[v][u]+=1
        return min(tuple(A[p[u]][p[v]] for u,v in combinations(range(n),2))
          for tail in permutations(range(2,n)) for p in ((0,1)+tail,))
    for m in range(1,5):
        for n in range(2,m+2):
            for es in product(tuple(combinations(range(n),2)),repeat=m):
                sequences+=1
                if (0,1) in es:continue
                degree=[sum(v in e for e in es) for v in range(n)]
                if not degree[0] or not degree[1] or any(d<2 for d in degree[2:]):continue
                reach={0}
                while True:
                    more=reach|{v for u,v in es if u in reach}|{u for u,v in es if v in reach}
                    if more==reach:break
                    reach=more
                if 1 not in reach:continue
                labeled.add((m,n,tuple(sorted(es))));words.add((m,n,word(es,n)))
    expected={(r['active_edges'],r['active_vertices'],word(r['edges'],r['active_vertices'])) for r in report['types']}
    assert words==expected and len(words)==18
    assert len(labeled)==sum(report['labeled_retained_by_edge_count'].values())==34
    return {'ordered_edge_sequences_visited':sequences,'port_fixed_labeled_multisets':len(labeled),
      'port_fixed_isomorphism_types':len(words),'exact_cover_agreement':True}

def solve4(A,b):
    rows=[[F(x) for x in row]+[F(v)] for row,v in zip(A,b)];pivots=[];r=0
    for col in range(4):
        pivot=next((k for k in range(r,4) if rows[k][col]),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r];z=rows[r][col];rows[r]=[x/z for x in rows[r]]
        for k in range(4):
            if k!=r:
                z=rows[k][col];rows[k]=[a-z*v for a,v in zip(rows[k],rows[r])]
        pivots.append(col);r+=1
    if any(not any(row[:4]) and row[4] for row in rows):return None,'inconsistent'
    if r<4:return None,'underdetermined'
    x=[F(0)]*4
    for row,col in zip(rows,pivots):x[col]=row[4]
    assert all(sum(a*v for a,v in zip(row,x))==t for row,t in zip(A,b))
    return x,'unique'

def forest_systems():
    tested=positive=0;solutions=[]
    matchings=(((0,2),(1,4)),((0,3),(1,4)),((0,3),(2,4)))
    for positions in combinations(range(4),2):
        order=['L' if j in positions else 'C' for j in range(4)];sign=[1 if k=='L' else -1 for k in order]
        for chords in matchings:
            A=[[int(k=='L') for k in order],[int(k=='C') for k in order]]
            A += [[sign[j]*int(u<=j<v) for j in range(4)] for u,v in chords]
            x,status=solve4(A,[3,2,0,0]);tested+=1;assert status!='underdetermined'
            if x is None or min(x)<=0:continue
            positive+=1;assert chords!=matchings[1]
            R=(F(5,9),F(4,9)) if chords==matchings[0] else (F(4,9),F(5,9))
            labels=(1,2,3,4,0)
            graph=[(k,labels[j],labels[j+1],x[j] if k=='L' else 1/x[j]) for j,k in enumerate(order)]
            graph += [('R',labels[u],labels[v],r) for (u,v),r in zip(chords,R)]
            assert rb.analyze_nominal(graph)['kind']=='forest';solutions.append(graph)
    assert tested==18 and positive==4
    return {'linear_systems':tested,'positive_endpoint_and_first_jet_circuits':positive,'response_types':1},solutions

def cyclic_systems():
    tested=positive=0;graphs=[]
    for doubled in range(3):
        groups=[b for b in range(3) for _ in range(2 if b==doubled else 1)]
        for Lpos in combinations(range(4),2):
            order=['L' if j in Lpos else 'C' for j in range(4)]
            A=[[int(g==b)*(1 if k=='L' else -1) for g,k in zip(groups,order)] for b in range(3)]
            A.append([1]*4);y,status=solve4(A,[1,-1,1,5]);tested+=1
            assert status!='underdetermined'
            if y is None or min(y)<=0:continue
            positive+=1;assert doubled in (0,2);labels=(1,2,3,0)
            graph=[(k,labels[g],labels[g+1],1/v if k=='L' else v) for g,k,v in zip(groups,order,y)]
            a,b=(F(4,5),F(1)) if doubled==0 else (F(1),F(4,5))
            graph += [('R',1,3,a),('R',2,0,b)]
            assert rb.analyze_nominal(graph)['kind']=='cyclic';graphs.append(graph)
    assert tested==18 and positive==4
    return {'block_colour_systems':tested,'positive_labelled_circuits':positive,'port_fixed_supports':2,'response_types':1},graphs

def cloud(graph,variant):
    if not variant:return list(graph)
    out=[e for e in graph if e[0]!='R'];next_node=max(v for k,u,v,x in graph for v in (u,v))+1
    for count,(k,u,v,target) in enumerate(e for e in graph if e[0]=='R'):
        n=4 if variant<5 else 5
        raw=[('R',a,b,F(2+(a*7+b*5+variant+count)%11,2+(a+b+variant)%5)) for a,b in combinations(range(n),2)]
        z=reference(raw,C(1))['gamma'];assert not z.im
        equivalent=(1+z.re)/(1-z.re);scale=target/equivalent
        mapping={0:v,1:u}
        for node in range(2,n):mapping[node]=next_node;next_node+=1
        out += [('R',mapping[a],mapping[b],r*scale) for kind,a,b,r in raw]
        out.append(('R',u,next_node,F(2+variant)));next_node+=1
    if variant%2:out=[(k,v,u,x) for k,u,v,x in reversed(out)]
    if variant==7:
        nodes=sorted({v for k,u,v,x in out for v in (u,v)}-{0,1},reverse=True)
        mapping={0:0,1:1,**{v:100+7*j for j,v in enumerate(nodes)}}
        out=[(k,mapping[u],mapping[v],x) for k,u,v,x in out]
    return out

def physical_controls(forest,cyclic):
    fixtures=compares=0;max_nodes=max_R=0
    bases=[('forest',g) for g in forest]+[('cyclic',list(rb.CORES['cyclic'])),
        ('cyclic',[(k,1-v if v in (0,1) else v,1-u if u in (0,1) else u,x) for k,u,v,x in rb.CORES['cyclic']])]
    for expected,base in bases:
        for variant in range(8):
            graph=cloud(base,variant);report=rb.analyze_nominal(graph);assert report['kind']==expected and report['effective_R_edges']==2
            original=pair(graph);P,Q=original['P'],original['Q'];reduced=rb.kron_resistors(graph);r=pair(reduced)
            assert rb.same_response(P,Q,r['P'],r['Q']) and value(Q,C(0,1))
            phasor=response(graph,C(0,1));assert 1/phasor['Y']==C(0,1)
            assert all(not cur for (k,u,v,x),cur in zip(graph,phasor['current']) if k=='R')
            assert sum(k!='R' and bool(cur) for (k,u,v,x),cur in zip(graph,phasor['current']))==4
            assert not find_modes(graph)
            for s in SAMPLES+(C(0,1),):
                expected_gamma=(value(P,s)-value(Q,s))/(value(P,s)+value(Q,s))
                actual=reference(graph,C.make(s))['gamma'];assert actual==C.make(expected_gamma);compares+=1
            fixtures+=1;max_nodes=max(max_nodes,len({v for k,u,v,x in graph for v in (u,v)}));max_R=max(max_R,sum(k=='R' for k,u,v,x in graph))
    return {'physical_graphs':fixtures,'independent_phasor_comparisons':compares,'max_nodes':max_nodes,'max_R_edges':max_R,
      'units':'Finite rational physical graphs with arbitrarily structured finite R clouds; not whole placement exclusions.'}

def scope_guards():
    disconnected=0
    for t,(a,b) in product((F(1,2),F(1),F(3,2)),((F(1),F(1)),(F(1,3),F(7,4)),(F(4,9),F(5,9)))):
        ell=1/(2-t)
        graph=[('L',1,2,t+1),('C',2,0,1/t),('L',3,4,ell),('C',3,4,1/ell),('R',1,3,a),('R',0,4,b)]
        p=pair(graph);P,Q=p['P'],p['Q'];ti=C(0,1);qi=value(Q,ti);pi=value(P,ti)
        assert qi and pi/qi==ti
        jet=(value(derivative(P),ti)*qi-pi*value(derivative(Q),ti))/(qi*qi);assert jet==C(5)
        assert rb.endpoint(P,Q)==rb.endpoint(P,Q,True)==a+b
        state=response(graph,ti);assert all(not cur for (k,u,v,x),cur in zip(graph,state['current']) if k=='R')
        assert sum(k!='R' and bool(cur) for (k,u,v,x),cur in zip(graph,state['current']))==4 and not find_modes(graph)
        try:rb.analyze_nominal(graph)
        except ValueError:pass
        else:raise AssertionError('Unequal-endpoint hypothesis was lost')
        disconnected+=1
    old=controls()['controls'][1];graph=[(k,u,v,F(x)) for k,u,v,x in old['edges']];state=response(graph,C(0,1))
    inactive=[j for j,((k,u,v,x),cur) in enumerate(zip(graph,state['current'])) if k!='R' and not cur]
    assert len(inactive)==1 and old['Zprime_i']==['3','0']
    removed=pair([e for j,e in enumerate(graph) if j not in inactive]);assert rb.endpoint(removed['P'],removed['Q'],True)==F(9,5)
    assert old['Zinf']=='1'
    try:rb.analyze_nominal(graph)
    except ValueError:pass
    else:raise AssertionError('First-jet hypothesis was lost')
    singular=[('L',1,2,F(1)),('C',2,0,F(1)),('L',2,3,F(1)),('C',2,3,F(1)),('R',1,0,F(1))]
    assert not value(pair(singular)['Q'],C(0,1)) and find_modes(singular)
    try:rb.analyze_nominal(singular)
    except ValueError as exc:assert 'Q(i)' in str(exc)
    else:raise AssertionError('Singular state accepted as regular')
    try:rb.analyze_nominal(list(rb.CORES['forest'])+[('L',9,9,F(1))])
    except ValueError:pass
    else:raise AssertionError('Extra reactive budget accepted')
    return {'disconnected_cycle_graphs':disconnected,'inactive_LC_endpoint_guard':1,'natural_Q_singular_guard':1,'extra_reactive_budget_guard':1}

def surgery_controls():
    checks=0
    for kind in rb.CORES:
        base=list(rb.CORES[kind])
        for edge in (4,5):
            for amount in (F(1,1000),F(1),F(1000)):
                graph=list(base);k,u,v,x=graph[edge];graph[edge]=(k,u,v,amount)
                for opened,shorted,bound in (([edge],[],2/amount),([],[edge],2*amount)):
                    changed,mapping=rb.surgery_graph(graph,opened,shorted)
                    for s in SAMPLES:
                        assert abs((reference(graph,C(s))['gamma']-reference(changed,C(s))['gamma']).re)<=bound;checks+=1
    for r in (F(1,1000),F(1),F(1000)):
        g=[('R',1,0,r)]
        for s in SAMPLES:
            v=reference(g,C(s));i=v['currents'][0];assert not i.im
            assert 2*i.re*i.re==2/(1+r)**2
            assert abs(v['gamma'].re+1)<=2*r and abs(v['gamma'].re-1)<=2/r;checks+=2
    return {'positive_real_open_short_comparisons':checks,'reference_resistor_derivative_controls':21}

def perturbation_controls():
    cases=checks=0;eps=F(1,100)
    for kind,base in rb.CORES.items():
        for signs in product((-1,1),repeat=6):
            actual=[(k,u,v,x*(1+sign*eps)) for (k,u,v,x),sign in zip(base,signs)]
            spec={'nominal':rb.serialized(base),'actual':rb.serialized(actual),'relative_error':str(eps),'requested_margin':'1/300'}
            cert=rb.certificate(spec);assert cert['status']=='PASS' and F(cert['strict_slack'])>0
            error=F(0)
            for s in SAMPLES:
                g=reference(actual,C(s))['gamma'];assert not g.im
                error=max(error,abs(g.re-gamma(s)));checks+=1
            assert error>=F(cert['remaining_error_floor'])>F(1,300);cases+=1
    uniform=F(25,2769)-F(1,198)-F(1,5000)-F(1,300);assert uniform>0
    example=json.loads((Path(__file__).parent/'regular_core_example.json').read_bytes())
    report=rb.certificate(example);assert report['status']=='PASS' and rb.verify(example,report)['status']=='PASS'
    actual=[(k,u,v,F(x)) for k,u,v,x in example['actual']]
    error=max(abs(reference(actual,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
    assert error>=F(report['remaining_error_floor'])>F(1,300)
    cycle=deepcopy(example);cycle['actual'][7][3]='1/120000'
    cycle['actual'] += [['R',1,5,'1/120000'],['R',5,4,'1/120000']];cycle['shorted_R_indices']=[7,8,9]
    cycle_report=rb.certificate(cycle);assert cycle_report['status']=='PASS'
    cycle_graph=[(k,u,v,F(x)) for k,u,v,x in cycle['actual']]
    cycle_error=max(abs(reference(cycle_graph,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
    assert cycle_error>=F(cycle_report['remaining_error_floor'])>F(1,300)
    for kind,base in rb.CORES.items():
        nominal=cloud(base,3);actual=[(k,u,v,x*(1+eps*(-1 if j%2 else 1))) for j,(k,u,v,x) in enumerate(nominal)]
        spec={'nominal':rb.serialized(nominal),'actual':rb.serialized(actual),'relative_error':str(eps),'requested_margin':'1/300'}
        rec=rb.certificate(spec);assert rec['status']=='PASS'
        measured=max(abs(reference(actual,C(s))['gamma'].re-gamma(s)) for s in SAMPLES)
        assert measured>=F(rec['remaining_error_floor'])>F(1,300)
    return {'all_component_corner_graphs':cases,'independent_positive_real_comparisons':checks+28,
      'redundant_R_short_cycle_graphs':1,'detuned_R_cloud_graphs':2,
      'unified_strict_margin':'1/300','epsilon_max':'1/100','combined_R_surgery_budget_max':'1/10000',
      'uniform_strict_slack':str(uniform),'worked_example_error':str(error)},example,report

def consumer_controls(example,report):
    corruptions=0
    for field,val in (('input_sha256','0'*64),('strict_margin','1/2'),('surgery_response_bound','0'),('strict_slack','1'),('status','INCONCLUSIVE')):
        wrong=deepcopy(report);wrong[field]=val
        try:rb.verify(example,wrong)
        except ValueError:corruptions+=1
        else:raise AssertionError('Altered certificate accepted')
    wrong=deepcopy(example);wrong['requested_margin']='1/400'
    try:rb.verify(wrong,report)
    except ValueError:corruptions+=1
    else:raise AssertionError('Requested margin not bound')
    invalid=[]
    for field,val in (('opened_R_indices',[0]),('shorted_R_indices',[0]),('opened_R_indices',[6,6]),('shorted_R_indices',[6]),('relative_error','1'),('relative_error',True),('requested_margin','0')):
        spec=deepcopy(example);spec[field]=val;invalid.append(spec)
    spec=deepcopy(example);spec['actual'][0][3]='2';invalid.append(spec)
    spec=deepcopy(example);spec['nominal'][0][1]=9;invalid.append(spec)
    spec=deepcopy(example);spec['opened_R_indices']=[];spec['shorted_R_indices']=[6];invalid.append(spec)
    spec=deepcopy(example);spec['target']='different';invalid.append(spec)
    spec=deepcopy(example);spec['actual'][0][3]=0.5;invalid.append(spec)
    spec=deepcopy(example);spec['relative_error']='-1';invalid.append(spec)
    invalid_count=0
    for spec in invalid:
        try:rb.certificate(spec)
        except (ValueError,RuntimeError):invalid_count+=1
        else:raise AssertionError('Invalid physical data accepted')
    for bad in ([['R',True,0,'1']],[['R',1,0,True]],[['R',1,0,'0']],[['R',1,0,'1']]*257,[['R',j+2,0,'1'] for j in range(63)],[['R',1,0,1<<257]]):
        try:rb.checked_edges(bad)
        except ValueError:invalid_count+=1
        else:raise AssertionError('Invalid/capped graph accepted')
    spec=deepcopy(example);spec['requested_margin']='1'
    inc=rb.certificate(spec);assert inc['status']=='INCONCLUSIVE' and inc['strict_margin'] is None
    assert rb.verify(spec,inc)['status']=='INCONCLUSIVE'
    spec=deepcopy(example);spec['relative_error']='99/100'
    inc=rb.certificate(spec);assert F(inc['remaining_error_floor'])<0 and inc['status']=='INCONCLUSIVE' and inc['strict_margin'] is None
    with tempfile.TemporaryDirectory(prefix='smith-regular-cli-') as directory:
        root=Path(directory);source=root/'input.json';output=root/'certificate.json';source.write_text(json.dumps(example),encoding='utf-8')
        module=Path(__file__).parent/'regular_balanced.py'
        subprocess.run([sys.executable,'-B','-S',str(module),str(source),'--output',str(output)],capture_output=True,text=True,check=True,timeout=30)
        run=subprocess.run([sys.executable,'-B','-S',str(module),str(output),'--verify'],capture_output=True,text=True,check=True,timeout=30)
        assert json.loads(run.stdout)['status']=='PASS'
        obj=json.loads(output.read_bytes());obj['input']['requested_margin']='1/400';output.write_text(json.dumps(obj),encoding='utf-8')
        bad=subprocess.run([sys.executable,'-B','-S',str(module),str(output),'--verify'],capture_output=True,text=True,timeout=30);assert bad.returncode
        source.write_text('{"nominal":[],"nominal":[]}',encoding='utf-8')
        bad=subprocess.run([sys.executable,'-B','-S',str(module),str(source)],capture_output=True,text=True,timeout=30);assert bad.returncode and 'Duplicate JSON field' in bad.stderr
        source.write_bytes(b' '*(rb.MAX_BYTES+1))
        bad=subprocess.run([sys.executable,'-B','-S',str(module),str(source)],capture_output=True,text=True,timeout=30);assert bad.returncode and 'byte cap' in bad.stderr
    return {'bound_or_input_corruptions_rejected':corruptions,'invalid_domain_or_resource_cases_rejected':invalid_count,
      'nonpositive_slack_remains_inconclusive':True,'negative_floor_remains_inconclusive':True,
      'CLI_roundtrip':1,'CLI_changed_margin_rejected':1,'CLI_duplicate_field_rejected':1,'CLI_byte_cap_rejected':1}

def run():
    supports=inventory();assert supports['unlabelled_port_fixed_types']==18
    independent_support=ordered_support_crosscheck(supports)
    forest,fg=forest_systems();cyclic,cg=cyclic_systems()
    for P,Q,constant in ((rb.FOREST_P,rb.FOREST_Q,F(414)),(rb.CYCLIC_P,rb.CYCLIC_Q,F(-4))):
        assert [a-b for a,b in zip(multiply(P,QH),multiply(PH,Q))]==[constant*a for a in (0,1,0,2,0,1,0)]
    assert rb.BASE_ERRORS['forest']>rb.BASE_ERRORS['cyclic']>0
    physical=physical_controls(fg,cg);guards=scope_guards();surgery=surgery_controls()
    perturbation,example,record=perturbation_controls();consumer=consumer_controls(example,record)
    return {'status':'PASS','support_inventory':supports,'orthogonal_support_enumerator':independent_support,'forest_systems':forest,'cyclic_systems':cyclic,
      'physical_R_clouds':physical,'scope_guards':guards,'R_surgery':surgery,'near_core_region':perturbation,'portable_consumer':consumer,
      'coverage_unchanged':{'covered':1334,'remaining':796},'selected_Lean_statements_unchanged':41,
      'interpretation':'Exact finite controls support the separate written two-response classification and supplied positive-real neighborhood; no useful uniform all-balanced margin follows.'}

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(run(),indent=2))
