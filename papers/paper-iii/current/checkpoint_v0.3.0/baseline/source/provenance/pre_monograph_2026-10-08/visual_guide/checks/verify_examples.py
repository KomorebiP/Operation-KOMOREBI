#!/usr/bin/env python3
"""Run exact finite example checks, with independent path accumulation and controls.

No floating tolerance, external data, Lean invocation, or universal conjecture test.
The finite ranges are explicit in each evidence record.
"""
from __future__ import annotations
from pathlib import Path
from itertools import product
import hashlib, json, sys, time
from datetime import datetime,timezone
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import models as M

records=[]
def check(name,condition,scope):
    good=bool(condition)
    records.append({'name':name,'passed':good,'scope':scope})
    if not good: raise AssertionError(f'{name}: {scope}')

def eq(a,b):
    if isinstance(a,sp.MatrixBase) or isinstance(b,sp.MatrixBase):
        return a.shape==b.shape and all(sp.simplify(v)==0 for v in a-b)
    return sp.simplify(a-b)==0

start=time.monotonic()
e=M.Edge('e',0,1,2);f=M.Edge('f',1,2,3)
le=M.edge_matrix(3,e);lf=M.edge_matrix(3,f)
check('target_row_source_column',le[1,0]==2 and sum(v!=0 for v in le)==1,'3 packets, one edge')
check('matched_pair',eq(lf*le,M.edge_matrix(3,M.Edge('ef',0,2,6))),'over integers')
check('reverse_pair_annihilated',lf*le!=le*lf and le*lf==sp.zeros(3),'execution e then f is Lf Le')
check('single_edge_squares_vanish',le**2==lf**2==sp.zeros(3),'no self-loop')
p=M.parallel_model();edges=p['edges'];T=p['T']
check('parallel_transfer_matrix',T==sp.Matrix([[0,0,1],[1,0,0],[0,3,0]]),'distinct coefficients 2 and -1 summed only at same support')
check('parallel_square',T**2==sp.Matrix([[0,3,0],[0,0,1],[3,0,0]]),'T^2 exact')
check('parallel_cube',T**3==3*sp.eye(3),'weighted 3-cycle')
for n in range(7):
    acc=sp.zeros(3);violations=[];kept=0
    for w in product(edges,repeat=n):
        op=M.word_operator(3,w);acc+=op
        if n and M.composable(w):
            expected=M.edge_matrix(3,M.Edge('path',w[0].source,w[-1].target,M.word_coefficient(w)))
            if op!=expected: violations.append(tuple(e.name for e in w))
            kept+=1
        elif n and op!=sp.zeros(3):violations.append(tuple(e.name for e in w))
    check(f'word_products_length_{n}',not violations,f'all {4**n} words; endpoint collapse/nonwalk annihilation')
    check(f'word_sum_length_{n}',acc==T**n,f'all {4**n} words independently multiplied')
    check(f'endpoint_accumulation_length_{n}',M.enumerate_walk_matrix(3,edges,n)==T**n,'independent endpoint and coefficient accumulation')
check('five_legal_pairs',sum(M.composable(w) for w in product(edges,repeat=2))==5,'all 16 ordered pairs')
check('parallel_edges_not_deduplicated',(T**2)[2,0]==6-3 and (T**2)[2,0]!=6,'both a,c and b,c paths retained')
check('empty_word_identity',M.word_operator(3,())==sp.eye(3),'empty product, not zero')
nc=M.noncommutative_model()
check('noncommuting_coefficient_order',nc['BA']==sp.Matrix([[1,1],[1,2]]) and nc['AB']==sp.Matrix([[2,1],[1,1]]),'2x2 rational coefficient ring')
check('matrix_ring_totalization',(nc['Lf']*nc['Le'])[4:6,0:2]==nc['BA'],'6x6 ordinary representation of Mat3(Mat2(Q))')
check('matrix_ring_wrong_order_rejected',nc['BA']!=nc['AB'],'negative mathematical shortcut control')
d=M.diamond_model();v=sp.eye(5)[:,0]
check('diamond_one_step',d['T']*v==sp.Matrix([0,1,1,0,0]),'one seed, five vertices')
check('diamond_cancellation',d['T']**2*v==sp.zeros(5,1),'two opposite contributions to packet 3')
check('diamond_unsigned_reachability',(d['unsigned']**2)[3,0]==2,'two combinatorially valid paths')
check('diamond_orbit_rank',sp.Matrix.hstack(v,d['T']*v,d['T']**2*v).rank()==2,'T^3=0, so full algebraic orbit hull')
check('diamond_nilpotence',d['T']**3==sp.zeros(5),'exact matrix identity, not finite search extrapolation')
check('diamond_unreachable',all(M.enumerate_walk_matrix(5,d['edges'],n)[4,0]==0 for n in range(5)),'lengths 0..4; isolated vertex also evident directly')
check('reachable_not_sufficient_control',(d['unsigned']**2)[3,0]!=0 and (d['T']**2)[3,0]==0,'reject converse of no-path implies zero')
r=M.rectangular_model()
check('rectangular_dimensions',r['A'].shape==(3,2) and r['B'].shape==(2,3) and r['C'].shape==(1,2),'typed chain Q^2 -> Q^3 -> Q^2 -> Q')
check('rectangular_two_step',r['BA']==sp.Matrix([[-1,5],[2,4]]),'all intermediate indices 0,1,2')
check('rectangular_three_step',r['CBA']==sp.Matrix([[-4,6]]),'target has one packet')
for i in range(2):
    check(f'rectangular_path_sum_source_{i}',sum(r['contributions'][i])==r['CBA'][0,i],'six terms per source; 12 terms total')
# Arbitrary-length fixed-index identity, separately from changing sizes.
b1=sp.Matrix([[1,1],[0,1]]);b2=sp.Matrix([[2,0],[1,1]]);b3=sp.Matrix([[1,0],[-1,2]])
for mats in [[],[b1],[b1,b2],[b1,b2,b3],[b3,b1,b2,b1]]:
    n=len(mats);out=sp.eye(2)
    for mat in mats:out=mat*out
    explicit=sp.zeros(2)
    if n==0:explicit=sp.eye(2)
    else:
        for i,j in product(range(2),repeat=2):
            for mid in product(range(2),repeat=n-1):
                path=(i,)+mid+(j,);val=1
                for t,mat in enumerate(mats):val=mat[path[t+1],path[t]]*val
                explicit[j,i]+=val
    check(f'common_index_path_sum_{n}',out==explicit,'one common two-packet type; length '+str(n))
fr=M.frame_model();J=fr['J']
check('frame_coordinates',fr['coordinates']==[sp.Matrix([3,2]),sp.Matrix([1,2]),sp.Matrix([sp.Rational(3,2),sp.Rational(1,2)])],'same ambient vector (3,2)')
check('frame_synthesis',all(fr['F'][a]*fr['coordinates'][a]==fr['x'] for a in range(3)),'three exact frames')
check('frame_all_cocycles',all(J[c,b]*J[b,a]==J[c,a] for a,b,c in product(range(3),repeat=3)),'all 27 chart triples')
check('frame_round_trips',all(J[a,b]*J[b,a]==sp.eye(2) for a,b in product(range(3),repeat=2)),'all nine pairs')
for path in [(0,1,2,0),(2,1,0,2),(0,2,1,2,0),(0,)]:
    out=sp.eye(2)
    for a,b in zip(path,path[1:]):out=J[b,a]*out
    check('canonical_path_'+''.join(map(str,path)),out==J[path[-1],path[0]],'actual ordered product')
nl=M.nonlinear_model();x,y,u,vv=nl['x'],nl['y'],nl['u'],nl['v'];z=sp.Matrix([x,y])
check('nonlinear_chart_left_inverse',eq(nl['S'](nl['A'](z)),z),'symbolic polynomial identity over Q')
check('nonlinear_chart_right_inverse',eq(nl['A'](nl['S'](z)),z),'symbolic polynomial identity over Q')
check('nonlinear_naturality',eq(nl['Fb'].subs({u:x,vv:y+x*x},simultaneous=True),nl['A'](nl['F'])),'full polynomial identity; no derivative assumption')
check('nonlinear_numeric_routes',nl['Fb'].subs({u:1,vv:3})==sp.Matrix([3,11]),'candidate (1,2) in the original chart')
# Composition: choose G(s,t)=(s^2-t,s+t); conjugate each map independently.
s,t=sp.symbols('s t');g=sp.Matrix([s*s-t,s+t])
gb=nl['A'](g.subs({s:u,t:vv-u*u},simultaneous=True))
composed=gb.subs({u:nl['Fb'][0],vv:nl['Fb'][1]},simultaneous=True)
direct=nl['A'](g.subs({s:nl['F'][0],t:nl['F'][1]},simultaneous=True)).subs({x:u,y:vv-u*u},simultaneous=True)
check('nonlinear_composition',eq(composed,direct),'two independently conjugated polynomial maps')
minimal=M.scalar_connection(sp.Rational(1,6));rev=M.scalar_connection()
check('minimal_loop_can_hide_reverse_failure',M.loop(minimal,0,1,2)==1 and M.defect(minimal,0,1,2)==1,'self-normalized but not reverse-normalized')
check('minimal_relative_defect_nontrivial',minimal[2,1]*minimal[1,0]/minimal[2,0]==sp.Rational(6,5),'D-times is based at the target')
check('minimal_missing_inverse',minimal[0,2]*minimal[2,0]!=1,'5/6 is not a round trip of one')
check('reversible_inverse_pairs',all(rev[a,b]*rev[b,a]==1 for a,b in product(range(3),repeat=2)),'all nine pairs')
check('scalar_triangle_holonomy',M.loop(rev,0,1,2)==sp.Rational(6,5),'u=2, v=3, w=5')
check('scalar_defect_holonomy',M.loop(rev,0,1,2)-1==rev[0,2]*M.defect(rev,0,1,2),'1/5=(1/5)*1')
check('scalar_routes_at_five',rev[2,0]*5==25 and rev[2,1]*rev[1,0]*5==30 and M.loop(rev,0,1,2)*5==6,'direct 25; routed 30; returned 6')
check('scalar_repeated_loop',[(sp.Rational(6,5))**n for n in range(5)]==[1,sp.Rational(6,5),sp.Rational(36,25),sp.Rational(216,125),sp.Rational(1296,625)],'loops 0..4, exact fractions')
sh=M.shear_model();H=sh['H'];Ob=sh['Ob'];P=sh['P'];G=sh['G'];D=sh['D']
check('shear_trace_det_not_identity',H.trace()==2 and H.det()==1 and H!=sp.eye(2),'negative shortcut: trace and determinant cannot prove flatness')
check('shear_characteristic_polynomial',H.charpoly(t).as_expr()==(t*t-2*t+1),'same characteristic polynomial as identity')
check('shear_witness',Ob*sp.Matrix([0,1])==sp.Matrix([1,0]),'input packet 1, output packet 0')
check('diagonal_gauge',sh['Hd']==sp.Matrix([[1,2],[0,1]]),'G=diag(2,1)')
check('gauge_rank_and_spectrum',Ob.rank()==(sh['Hd']-sp.eye(2)).rank()==1 and sh['Hd'].charpoly(t)==H.charpoly(t),'rank and characteristic polynomial under conjugation')
check('gauge_size_not_invariant',sum(v*v for v in Ob)==1 and sum(v*v for v in sh['Hd']-sp.eye(2))==4,'squared Frobenius norm, an example not a stability theorem')
check('diagonal_gauge_commutes',all(D*p==p*D for p in P),'fixed standard projectors')
for i,j in product(range(2),repeat=2):
    check(f'diagonal_block_gauge_{i}{j}',P[i]*(sh['Hd']-sp.eye(2))*P[j]==D*(P[i]*Ob*P[j])*D.inv(),'packet-preserving case')
flat=M.flat_model();fg=flat['gamma']
check('flat_scalar_all_triangles',all(M.defect(fg,a,b,c)==0 for a,b,c in product(range(3),repeat=3)),'all 27 triples')
check('flat_not_calibrated',fg[1,0]==2 and fg[1,0]!=1,'canonical J is identity in this example')
check('flat_root_gauge',all(fg[b,a]==fg[b,0]/fg[a,0] for a,b in product(range(3),repeat=2)),'root o=0, all pairs')
bl=M.block_model();blocks=bl['blocks'];ob=bl['Ob']
check('three_packet_complete',sum(bl['P'],sp.zeros(3))==sp.eye(3) and all(p*p==p for p in bl['P']),'three idempotents')
check('three_packet_reconstruction',sum((block for row in blocks for block in row),sp.zeros(3))==ob,'all nine input-output blocks')
check('three_packet_nonzero_addresses',[(i,j) for i,j in product(range(3),repeat=2) if blocks[i][j]!=sp.zeros(3)]==[(0,1),(1,2)],'exact support, not thresholded')
check('packet_witness_01',bl['P'][0]*ob*sp.eye(3)[:,1]==sp.Matrix([2,0,0]),'explicit source basis vector')
check('packet_witness_12',bl['P'][1]*ob*sp.eye(3)[:,2]==sp.Matrix([0,3,0]),'explicit source basis vector')
check('packet_output_sum',ob*sp.Matrix([4,5,6])==sp.Matrix([10,18,0]),'two packet contributions')
check('diagonal_only_failure',all(p*Ob*p==sp.zeros(2) for p in P) and Ob!=sp.zeros(2),'all diagonal residuals zero does not suffice')
check('incomplete_family_failure',P[0]*Ob*P[0]==sp.zeros(2) and P[0]!=sp.eye(2),'one supplied projector is not a complete resolution')
Q=sh['Q']
check('oblique_complete',sum(Q,sp.zeros(2))==sp.eye(2) and all(q*q==q for q in Q),'actual conjugated projectors')
check('oblique_not_orthogonal_geometry',Q[0].T!=Q[0] and Q[0]*Q[1]==sp.zeros(2),'algebraic annihilation without self-adjointness')
check('oblique_block_reconstruction',sum((a*Ob*b for a,b in product(Q,repeat=2)),sp.zeros(2))==Ob,'actual four blocks')
mob=sh['Hm']-sp.eye(2)
check('mixing_gauge_four_blocks',mob==sp.Matrix([[-1,1],[-1,1]]) and all(mob[i,j]!=0 for i,j in product(range(2),repeat=2)),'one nonzero block becomes four at fixed packet axes')
check('mixing_gauge_total_nonzero',mob.rank()==Ob.rank()==1,'nonvanishing retained')
check('mixing_gauge_not_packet_preserving',any(G*p!=p*G for p in P),'commutation hypothesis genuinely fails')
check('moving_projector_covariance',all(Q[i]*mob*Q[j]==G*(P[i]*Ob*P[j])*G.inv() for i,j in product(range(2),repeat=2)),'transporting both projectors restores labelwise covariance')
check('fixed_packet_covariance_shortcut_fails',P[0]*mob*P[0]!=G*(P[0]*Ob*P[0])*G.inv(),'explicit counterexample without commutation')
vals=[-2,-1,0,1,2]
check('candidate_table',[list(M.candidate_residual(z)) for z in vals]==[[3,-3],[0,-2],[-1,-1],[0,0],[3,1]],'five displayed rational candidates')
check('candidate_not_global_obstruction',M.candidate_residual(-1)!=sp.zeros(2,1) and M.candidate_residual(1)==sp.zeros(2,1),'rejecting -1 does not reject 1')
check('candidate_equivalence_on_displayed_set',all((M.candidate_residual(z)!=sp.zeros(2,1))==any(v!=0 for v in M.candidate_residual(z)) for z in vals),'literal witness equivalence in a finite table')
tr=M.tree_model();env={'x':2,'y':5,'unused':0}
check('tree_inputs',M.inputs(tr)==frozenset({'x','y'}),'recursive finite input set')
check('tree_evaluation',M.evaluate(tr,env)==2,'(2^2+3)-5')
check('tree_locality_finite_grid',all(M.evaluate(tr,{'x':xv,'y':yv,'unused':k})==xv*xv+3-yv for xv,yv,k in product(range(-2,3),repeat=3)),'125 input environments; unused variable never read')
constant=('binary','add',('constant',2),('constant',3))
check('constant_tree_no_inputs',M.inputs(constant)==frozenset() and M.evaluate(constant,{})==5,'closed tree')
redundant=('binary','sub',('input','x'),('input','x'))
check('syntactic_not_minimal_dependency',M.inputs(redundant)==frozenset({'x'}) and all(M.evaluate(redundant,{'x':k})==0 for k in range(-4,5)),'x-x; syntax records x although value does not vary')
check('binary_order_control',M.evaluate(('binary','sub',('input','y'),tr[2]),env)==-2,'swap ordered root inputs')
check('arbitrary_semantics',M.evaluate(('binary','join',('input','x'),('input','y')),{'x':'ab','y':'cd'},binary={'join':lambda a,b:a+b})=='abcd','no linear or analytic assumption in tree evaluation')
check('noncanonical_node_defect',sp.expand(2*x*x-(2*x)**2)==-2*x*x,'chosen input and output scalings both 2')
check('canonical_node_no_defect',sp.expand(2*x*x-((2*x)**2)/2)==0,'correctly conjugated square is v^2/2')
check('bilinear_four_terms',sp.expand((x+y)*(u+vv)-(x*u+x*vv+y*u+y*vv))==0,'symbolic polynomial identity, not general tree theorem')
check('bilinear_area_values',(2+3)*(5+7)==60 and 2*5+3*7==31 and 2*7+3*5==29,'displayed four rectangles')
check('nonlinear_diagonal_omission',sp.expand((x+y)**2-x*x-y*y)==2*x*y,'square is not linear in its single slot')
cap=M.capstone_model();cg=cap['gamma']
check('capstone_H',cap['H']==sp.Matrix([[1,1],[1,2]]),'actual A then B then C^-1')
check('capstone_additive_identity',M.loop(cg,0,1,2)-sp.eye(2)==cg[0,2]*M.defect(cg,0,1,2),'matrix defect-holonomy identity')
check('capstone_witness',cap['Ob']*sp.Matrix([1,0])==sp.Matrix([0,1]),'input packet 0 to output packet 1')
Gs=[sp.Matrix([[2,0],[0,1]]),sp.Matrix([[1,1],[0,1]]),sp.Matrix([[1,0],[1,1]])]
gauged={(b,a):Gs[b]*cg[b,a]*Gs[a].inv() for a,b in product(range(3),repeat=2)}
check('matrix_gauge_holonomy_all_triples',all(M.loop(gauged,a,b,c)==Gs[a]*M.loop(cg,a,b,c)*Gs[a].inv() for a,b,c in product(range(3),repeat=3)),'all 27 triples, independently changed edges')
check('matrix_gauge_defect_all_triples',all(M.defect(gauged,a,b,c)==Gs[c]*M.defect(cg,a,b,c)*Gs[a].inv() for a,b,c in product(range(3),repeat=3)),'all 27 triples')
repaired=dict(cg);repaired[2,0]=cap['B']*cap['A'];repaired[0,2]=repaired[2,0].inv()
check('direct_edge_repair',M.loop(repaired,0,1,2)==sp.eye(2),'connection data changed, not gauge transformed')
check('three_chart_repair_flat',all(M.defect(repaired,a,b,c)==sp.zeros(2) for a,b,c in product(range(3),repeat=3)),'all 27 triples of this specific 3-chart connection')
# Fail-closed testing controls. Each intentionally false statement must trigger AssertionError.
controls=[]
for name,wrong in [('coefficient_order',lambda:nc['AB']==nc['BA']),
                   ('reachable_implies_nonzero',lambda:(d['T']**2)[3,0]!=0),
                   ('trace_and_det_imply_identity',lambda:H==sp.eye(2)),
                   ('fixed_packet_gauge_without_commutation',lambda:P[0]*mob*P[0]==G*(P[0]*Ob*P[0])*G.inv())]:
    try:
        assert wrong(), name
    except AssertionError:
        controls.append({'name':name,'rejected':True})
    else:
        raise RuntimeError(f'Invalid control was accepted: {name}')
report={'status':'PASS','scope':'Exact worked examples only; no new Lean certification or universal theorem claim.',
        'generated_utc':datetime.now(timezone.utc).isoformat(),'seconds':time.monotonic()-start,
        'python':sys.version.split()[0],'sympy':sp.__version__,'checks_passed':len(records),
        'checks':records,'invalid_controls_rejected':controls,
        'models_sha256':hashlib.sha256((ROOT/'source/models.py').read_bytes()).hexdigest(),
        'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'checks/EXACT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(records)} exact checks; {len(controls)} deliberately false controls rejected.')
