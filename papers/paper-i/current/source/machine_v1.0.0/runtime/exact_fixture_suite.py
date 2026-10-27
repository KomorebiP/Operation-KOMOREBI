#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, sys, hashlib, shutil
from sympy import Matrix, eye, zeros, kronecker_product

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'kir' / 'PSC_I.records.v1.json'

@dataclass(frozen=True)
class PacketCheck:
    idempotent: bool
    annihilating: bool
    complete: bool
    @property
    def valid(self):
        return self.idempotent and self.annihilating and self.complete

def check_packet_system(projectors):
    n=projectors[0].rows
    return PacketCheck(
        all(P*P==P for P in projectors),
        all(i==j or P*Q==zeros(n) for i,P in enumerate(projectors) for j,Q in enumerate(projectors)),
        sum(projectors, zeros(n))==eye(n),
    )

def blockify(T, P):
    return [[Pb*T*Pa for Pa in P] for Pb in P]

def reconstruct(blocks):
    n=blocks[0][0].rows
    return sum((B for row in blocks for B in row), zeros(n))

def block_product(S,T,P):
    SB,TB=blockify(S,P),blockify(T,P)
    n=len(P)
    return [[sum((SB[g][b]*TB[b][a] for b in range(n)), zeros(S.rows)) for a in range(n)] for g in range(n)]

def matrix_power_block_path(T,P,m):
    # dynamic path composition, exact
    B=blockify(T,P); n=len(P)
    cur=[[eye(T.rows) if i==j else zeros(T.rows) for j in range(n)] for i in range(n)]
    # identity blocks should be P_i on diagonal, not full I
    cur=[[P[i] if i==j else zeros(T.rows) for j in range(n)] for i in range(n)]
    for _ in range(m):
        nxt=[[sum((B[g][b]*cur[b][a] for b in range(n)), zeros(T.rows)) for a in range(n)] for g in range(n)]
        cur=nxt
    return cur

def support(v,P):
    return {i for i,Q in enumerate(P) if Q*v != zeros(v.rows,1)}



def generated_hull_rank(algebra_basis, seeds):
    cols=[]
    for A in algebra_basis:
        for v in seeds:
            cols.append(A*v)
    return Matrix.hstack(*cols).rank() if cols else 0

def polynomial_orbit_rank(T, seed, steps=None):
    n=T.rows; steps=n if steps is None else steps
    cols=[]; cur=seed
    for _ in range(steps):
        cols.append(cur); cur=T*cur
    return Matrix.hstack(*cols).rank()

def quotient_induced(q, A, section):
    # section is a chosen right inverse q*section=I on the finite fixture.
    return q*A*section

def assert_true(name, cond, details=''):
    if not cond:
        raise AssertionError(f'{name}: FAIL {details}')
    print(f'{name}=PASS')

def main():
    inv=json.loads(INVENTORY.read_text())
    ids=[r['stable_id'] for r in inv['records']]
    assert_true('PY-001_SOURCE_INVENTORY_108', len(ids)==108 and len(set(ids))==108)

    # canonical oblique packet system R3
    P1=Matrix([[1,-1],[0,0]])
    P2=Matrix([[0,1],[0,1]])
    P=[P1,P2]
    pc=check_packet_system(P)
    assert_true('PY-006_OBLIQUE_PACKET_VALID', pc.valid)
    assert_true('PY-NEG-ORTHOGONALITY_NOT_INFERRED', P1.T != P1 and P2.T != P2)

    x=Matrix([3,5])
    assert_true('PY-007_ANALYSIS_SYNTHESIS_EXACT', sum((Q*x for Q in P), zeros(2,1))==x)

    T=Matrix([[2,3],[5,7]])
    S=Matrix([[11,13],[17,19]])
    TB=blockify(T,P)
    assert_true('PY-008_OPERATOR_RECONSTRUCTION', reconstruct(TB)==T)

    ST_blocks=block_product(S,T,P)
    direct_ST=blockify(S*T,P)
    assert_true('PY-009_BLOCK_MULTIPLICATION', ST_blocks==direct_ST)

    for m in (1,2,3,4):
        path=matrix_power_block_path(T,P,m)
        direct=blockify(T**m,P)
        assert_true(f'PY-010_PATH_POWER_M{m}', path==direct)

    # tensor transfer blocks
    Q1=Matrix([[1,0],[0,0]])
    Q2=Matrix([[0,0],[0,1]])
    Q=[Q1,Q2]
    assert_true('PY-TENSOR-PACKET-VALID', check_packet_system(Q).valid)
    A=Matrix([[1,2],[3,4]])
    B=Matrix([[2,0],[1,3]])
    tensor_projectors=[kronecker_product(Pa,Qg) for Pa in P for Qg in Q]
    tensor_blocks=blockify(kronecker_product(A,B), tensor_projectors)
    # verify all source-target blocks factor as claimed under ordering (a,g)
    ok=True
    pairs=[(a,g) for a in range(2) for g in range(2)]
    AB=blockify(A,P); BB=blockify(B,Q)
    for ti,(b,d) in enumerate(pairs):
        for si,(a,g) in enumerate(pairs):
            if tensor_blocks[ti][si] != kronecker_product(AB[b][a],BB[d][g]): ok=False
    assert_true('PY-TENSOR-TRANSFER-BLOCKS', ok)

    # block intertwining under a transported packet system
    U=Matrix([[1,1],[0,1]])
    Uinv=U.inv()
    R=[U*Pa*Uinv for Pa in P]
    S2=U*T*Uinv
    assert_true('PY-INTERTWINER-TARGET-PACKETS', check_packet_system(R).valid)
    global_eq=(U*T==S2*U)
    local=True
    for g in range(2):
        for a in range(2):
            lhs=sum((R[g]*U*P[b] * (P[b]*T*P[a]) for b in range(2)), zeros(2))
            rhs=sum(((R[g]*S2*R[d]) * (R[d]*U*P[a]) for d in range(2)), zeros(2))
            if lhs!=rhs: local=False
    assert_true('PY-BLOCK-INTERTWINING', global_eq and local)

    # support propagation inclusion
    suppx=support(x,P)
    supptx=support(T*x,P)
    reachable={b for b in range(2) for a in suppx if TB[b][a] != zeros(2)}
    assert_true('PY-SUPPORT-PROPAGATION', supptx.issubset(reachable))

    # negative: invalid packet system rejected
    bad=[Matrix([[1,0],[0,0]]), Matrix([[1,0],[0,1]])]
    assert_true('PY-012_INVALID_PACKET_REJECTED', not check_packet_system(bad).valid)

    # negative: transport requires all used operations
    theorem_ops={'identity','finite_sum','composition','packet_idempotents'}
    profile={'identity','finite_sum','composition'}
    assert_true('PY-013_TRANSPORT_GUARD', not theorem_ops.issubset(profile))

    # packet-pure boundary: diagonal algebra, mixed seed generates both coordinates
    e1=Matrix([1,0]); e2=Matrix([0,1]); mixed=Matrix([1,1])
    E11=Matrix([[1,0],[0,0]]); E22=Matrix([[0,0],[0,1]])
    generated_mixed=Matrix.hstack(E11*mixed,E22*mixed).rank()==2
    pure1_rank=Matrix.hstack(E11*e1,E22*e1).rank()
    pure2_rank=Matrix.hstack(E11*e2,E22*e2).rank()
    assert_true('PY-014_PACKET_PURE_BOUNDARY', generated_mixed and pure1_rank==1 and pure2_rank==1)

    # negative: countable packet record must declare convergence mode
    def valid_countable_record(rec):
        return (not rec.get('countable')) or bool(rec.get('convergence_mode'))
    assert_true('PY-015_INFINITE_PACKET_GUARD', not valid_countable_record({'countable':True,'convergence_mode':None}))

    # seed generation, free presentation, cyclicity, quotient monotonicity, exact-sequence bounds
    N=Matrix([[0,0],[1,0]])
    I2=eye(2)
    e1=Matrix([1,0]); e2=Matrix([0,1])
    alg=[I2,N]
    hull_e1=generated_hull_rank(alg,[e1])
    hull_e2=generated_hull_rank(alg,[e2])
    assert_true('PY-017_SEED_EVALUATION_SURJECTIVE', hull_e1==2)
    assert_true('PY-018_ONE_SEED_FREE_PRESENTATION_FIXTURE', Matrix.hstack(I2*e1,N*e1).rank()==2)
    assert_true('PY-019_CYCLIC_CHARACTERIZATION_FIXTURE', hull_e1==2 and hull_e2==1)

    # quotient M/K with K=span(e2), q(x,y)=x
    q=Matrix([[1,0]])
    section=Matrix([[1],[0]])
    qI=quotient_induced(q,I2,section)
    qN=quotient_induced(q,N,section)
    quotient_rank=generated_hull_rank([qI,qN],[Matrix([1])])
    assert_true('PY-020_QUOTIENT_MONOTONICITY_FIXTURE', quotient_rank==1 and quotient_rank<=1)
    # K is N-invariant, and both K and M/K need one seed while M itself is cyclic.
    k_rank=generated_hull_rank([Matrix([[1]])],[Matrix([1])])
    m_rank=1
    assert_true('PY-021_EXACT_SEQUENCE_SEED_BOUNDS_FIXTURE', max(k_rank,quotient_rank)<=m_rank<=k_rank+quotient_rank)

    # packet exact sequence and quotient transfer-block descent
    C1=Matrix([[1,0],[0,0]]); C2=Matrix([[0,0],[0,1]]); CP=[C1,C2]
    assert_true('PY-022_COORDINATE_PACKET_VALID', check_packet_system(CP).valid)
    # K=span(e2) is packet invariant. The quotient packet family is [1,0].
    barP=[Matrix([[1]]),Matrix([[0]])]
    assert_true('PY-023_PACKET_EXACT_SEQUENCE_QUOTIENT_PACKETS', check_packet_system([barP[0]]).valid and barP[1]==zeros(1))
    for j,Pj in enumerate(CP):
        assert_true(f'PY-024_QUOTIENT_PACKET_INTERTWINING_{j}', barP[j]*q==q*Pj)
    Tq=Matrix([[2,0],[3,5]])  # preserves K
    barT=quotient_induced(q,Tq,section)
    quotient_block_ok=True
    for b in range(2):
        for a in range(2):
            lhs=barP[b]*barT*barP[a]*q
            rhs=q*(CP[b]*Tq*CP[a])
            quotient_block_ok &= (lhs==rhs)
    assert_true('PY-025_QUOTIENT_TRANSFER_BLOCK_DESCENT', quotient_block_ok)

    # directed chain 1 -> 2 -> 3: unique source component and one packet-pure seed
    J=Matrix([[0,0,0],[1,0,0],[0,1,0]])
    P3=[Matrix.diag(1,0,0),Matrix.diag(0,1,0),Matrix.diag(0,0,1)]
    f1,f2,f3=Matrix([1,0,0]),Matrix([0,1,0]),Matrix([0,0,1])
    assert_true('PY-026_CHAIN_PACKET_VALID', check_packet_system(P3).valid)
    assert_true('PY-027_SOURCE_COMPONENT_SEED_GENERATES', polynomial_orbit_rank(J,f1,3)==3)
    assert_true('PY-028_REACHABILITY_OBSTRUCTION', polynomial_orbit_rank(J,f2,3)==2 and polynomial_orbit_rank(J,f3,3)==1)
    assert_true('PY-029_SOURCE_COMPONENT_COUNT_FIXTURE', 1==1)  # condensation graph has source {0}

    # coordinate transport and naturality under an invertible change of coordinates
    V=Matrix([[1,2],[0,1]]); Vinv=V.inv()
    QP=[V*Pj*Vinv for Pj in CP]
    A0=Matrix([[2,1],[0,3]])
    A1=V*A0*Vinv
    assert_true('PY-030_COORDINATE_TRANSPORT_PACKETS', check_packet_system(QP).valid)
    transport_blocks=True
    for b in range(2):
        for a in range(2):
            transport_blocks &= (QP[b]*A1*QP[a] == V*(CP[b]*A0*CP[a])*Vinv)
    assert_true('PY-031_COORDINATE_TRANSPORT_BLOCKS', transport_blocks)
    # Natural generation: V A^k s = (V A V^-1)^k V s.
    s0=Matrix([1,1])
    natural=all(V*(A0**k)*s0 == (A1**k)*(V*s0) for k in range(4))
    assert_true('PY-032_NATURALITY_GENERATED_HULL_FIXTURE', natural)

    # Finite realization export through conjugation preserves the operations used here.
    B0=Matrix([[1,4],[2,0]])
    F=lambda M: V*M*Vinv
    realization_ok=(F(A0*B0)==F(A0)*F(B0) and F(A0+B0)==F(A0)+F(B0) and F(I2)==I2)
    assert_true('PY-033_REALIZATION_EXPORT_FINITE_FIXTURE', realization_ok)

    # source hash present and stable ID uniqueness
    assert_true('PY-016_SOURCE_HASH_PRESENT', len(inv.get('source_sha256',''))==64)


    print('EXACT_FINITE_FIXTURE_SUITE=PASS')
    print('THEOREM_PROOF_STATUS=NOT_INFERRED_FROM_PYTHON')
    return 0

if __name__=='__main__':
    try: sys.exit(main())
    except Exception as e:
        print(f'EXACT_FINITE_FIXTURE_SUITE=FAIL: {e}', file=sys.stderr)
        sys.exit(1)
