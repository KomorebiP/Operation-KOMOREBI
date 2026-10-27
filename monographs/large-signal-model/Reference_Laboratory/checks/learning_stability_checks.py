"""Exact and separately labeled numeric examples for Foundations 0.2.0.

Run from any working directory: python checks/learning_stability_checks.py
General proofs are in the theory volume. Executable checks illustrate finite
identities and reject stronger false claims; they are not Lean proofs.
"""
from __future__ import annotations
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path
import numpy as np
import sympy as sp
from observable_reference import fit_closed_span, learn_delay, delay_pairs, forecast_scalar, zero

ROOT = Path(__file__).resolve().parents[1]
Q = sp.Rational
M = sp.Matrix
RESULTS: list[dict[str, object]] = []


def check(name: str, proposition: str, condition: bool,
          arithmetic: str = "exact rational/symbolic", scope: str = "finite example") -> None:
    if not condition:
        raise AssertionError(f"{name}: {scope}")
    RESULTS.append({"name": name, "proposition": proposition, "passed": True,
                    "arithmetic": arithmetic, "scope": scope})


def rejects(name: str, thunk, text: str) -> None:
    try:
        thunk()
    except ValueError as exc:
        check(name, "15", text in str(exc), scope="expected rejection of invalid or uncertified input")
    else:
        raise AssertionError(f"Expected ValueError: {name}")


def observed_sequence(steps: int, q0: sp.Expr = sp.Integer(0)) -> list[sp.Expr]:
    # Used only by the independent generating-system checks, never by the fitter.
    l = M([[Q(1, 2), 1, 0], [Q(1, 4), Q(1, 3), 0], [0, 0, Q(5, 6)]])
    x = M([1, q0, 7])
    observations = [x[0]]
    for _ in range(steps):
        x = l * x
        observations.append(x[0])
    return observations


def main() -> None:
    l = M([[Q(1, 2), 1, 0], [Q(1, 4), Q(1, 3), 0], [0, 0, Q(5, 6)]])
    c = M([[1, 0, 0]])
    o2 = M.vstack(c, c*l)
    o3 = M.vstack(o2, c*l*l)
    expected = M([[0, 1], [Q(1, 12), Q(5, 6)]])
    check("delay rank stabilization", "14", c.rank() == 1 and o2.rank() == o3.rank() == 2)
    check("delay intertwining", "14", zero(o2*l - expected*o2))
    check("hidden independent coordinate stays invisible", "14", zero(o2*M([0,0,1])))
    check("one sample is not closed", "14", not zero(c*l*M([0,1,0])))
    # These are the only samples passed to learning.
    train = [sp.Integer(1), Q(1,2), Q(1,2), Q(11,24)]
    model = learn_delay(train, 2)
    x, y = delay_pairs(train, 2)
    check("observed training determinant", "15", x.det() == Q(1,4))
    check("learned ambient delay recurrence", "25", model.ambient_transition == expected)
    check("certificate does not claim global coverage", "15",
          model.certificate()["true_state_space_coverage"] == "NOT_CERTIFIED_BY_THESE_SAMPLES")
    future = forecast_scalar(model, train[-2:], 30)
    true = observed_sequence(33)
    check("output-only exact prediction on 30 subsequent steps", "25", future == true[4:34])
    check("first unseen output", "25", future[0] == Q(61,144))
    # Nontrivial rank-deficient ambient history: three entries, rank two.
    model3 = learn_delay(true[:7], 3)
    check("three-entry histories compress to rank two", "15", model3.input_rank == 2)
    check("compressed three-history recurrence", "25",
          forecast_scalar(model3, true[4:7], 12) == true[7:19])
    zero_model = learn_delay([0,0,0,0], 2)
    check("zero-span case remains conditional", "15", zero_model.input_rank == 0
          and forecast_scalar(zero_model,[0,0],3) == [0,0,0])
    rejects("reject inconsistent successors", lambda: fit_closed_span([[1,1],[0,0]], [[1,2],[0,0]]), "Inconsistent")
    rejects("reject successors outside observed span", lambda: fit_closed_span([[1],[0]], [[0],[1]]), "leave")
    rejects("reject floating-point exact input", lambda: learn_delay([1.0,0.5,0.5],1), "exact rational")
    rejects("reject short output record", lambda: learn_delay([1,2],2), "At least")
    rejects("reject nonpositive delay", lambda: learn_delay([1,2,3],0), "positive integer")
    rejects("reject boolean delay", lambda: learn_delay([1,2,3],True), "positive integer")
    rejects("reject unobserved initialization", lambda: forecast_scalar(zero_model,[1,0],2), "outside")
    rejects("reject negative forecast horizon", lambda: forecast_scalar(model,[1,0],-1), "nonnegative")
    # Exact nonidentification off the sampled span.
    xx = M([[1,2],[0,0]])
    b1, b2 = sp.diag(Q(1,2),0), sp.diag(Q(1,2),7)
    check("same fit different unobserved dynamics", "15", b1*xx == b2*xx and b1*M([0,1]) != b2*M([0,1]))
    # Deterministic errors-in-variables identity in a fixed full-rank space.
    xx = M([[1,0,1],[0,1,1]])
    bb = M([[Q(1,2),Q(1,4)],[0,Q(1,3)]])
    ee = M([[Q(1,100),0,0],[0,Q(-1,200),0]])
    ff = M([[0,Q(1,500),0],[Q(1,300),0,0]])
    rr = M([[0,0,Q(1,700)],[0,0,Q(-1,800)]])
    xt = xx+ee
    pinv = xt.T*(xt*xt.T).inv()
    bhat = (bb*xx+rr+ff)*pinv
    check("exact fixed-space perturbation identity", "16", zero(bhat-bb-(rr+ff-bb*ee)*pinv))
    eps = Q(1,100000)
    for s in [Q(1,1),Q(1,10),Q(1,100),Q(1,1000)]:
        xx = sp.diag(1,s)
        bb = sp.diag(Q(1,2),Q(1,3))
        ff = sp.diag(0,eps)
        err = (bb*xx+ff)*xx.inv()-bb
        check(f"inverse singular-value amplification s={s}","16",err == sp.diag(0,eps/s))
    check("input-noise boundary can destroy rank", "16", (sp.diag(1,Q(1,10))+sp.diag(0,Q(-1,10))).rank()==1,
          scope="negative control at excluded boundary norm(E)=sigma_min")
    for horizon in [0,1,3,8,15]:
        d = horizon+2
        shift = sp.zeros(d)
        for j in range(1,d): shift[j-1,j]=1
        v = sp.eye(d)[:,-1]
        output=[]
        for _ in range(horizon+2):
            output.append(v[0]);v=shift*v
        check(f"finite-prefix delayed mode T={horizon}","17",output == [0]*(horizon+1)+[1] and zero(shift**d),
              scope="constructive negative control to unrestricted finite-prefix certification")
    # Variable-Lipschitz recursion: exact sharp scalar equality.
    lambdas=[Q(1,2),Q(3,4),Q(1,3),Q(4,5)]
    defects=[Q(1,100),Q(1,50),Q(3,100),Q(1,25)]
    initial=Q(1,5)
    error=initial
    for t in range(len(lambdas)):
        error=lambdas[t]*error+defects[t]
        formula=sp.prod(lambdas[:t+1])*initial+sum(sp.prod(lambdas[k+1:t+1])*defects[k] for k in range(t+1))
        check(f"sharp propagated defect step {t+1}","18",error==formula)
    a=M([[0,2],[0,0]]); b=M([[0,0],[2,0]])
    check("stable factors can be unstable under switching","18",zero(a*a) and zero(b*b) and b*a==sp.diag(0,4),
          scope="negative control to individual spectral stability sufficing")
    metric=sp.diag(1,4)
    family=[sp.diag(Q(1,2),Q(1,3)),M([[0,1],[Q(1,4),0]])]
    for i,op in enumerate(family):
        defect=Q(1,4)*metric-op.T*metric*op
        check(f"common metric certificate operator {i}","18",defect.is_positive_semidefinite is True)
    # Uniform finite-memory bound, exact arithmetic and distinct numerical horizon.
    z=[sp.Integer(1)]
    for t in range(80):
        z.append(Q(1,2)*z[t]+sum(Q(1,4)*Q(1,3)**k*z[t-1-k] for k in range(t)))
    memory=[]
    for h in range(9):
        pred=[sp.Integer(1)]
        for t in range(80):
            pred.append(Q(1,2)*pred[t]+sum(Q(1,4)*Q(1,3)**k*pred[t-1-k] for k in range(min(h,t))))
        measured=max(abs(left-right) for left,right in zip(z,pred,strict=True))
        aa=Q(7,8)-Q(3,8)*Q(1,3)**h
        tail=Q(3,8)*Q(1,3)**h
        bound=3*Q(1,3)**h/(1+3*Q(1,3)**h)
        check(f"stable memory recursive bound H={h}","19",measured<=bound and tail/(1-aa)==bound)
        memory.append({"H":h,"steps_checked":80,"max_error":str(measured),"uniform_bound":str(bound),
                       "a":str(aa),"tail_bound":str(tail)})
    check("exact example true output bound","19",all(0<=v<=1 for v in z))
    # Polynomial interactions are ordered and need cross terms.
    u,v=sp.symbols('u v',real=True)
    omission=sp.expand((u+v)**2-u**2-v**2)
    check("quadratic omitted interaction identity","20",omission==2*u*v)
    for uu,vv in [(Q(1,2),Q(1,1000)),(Q(-2,3),Q(2,5)),(0,1)]:
        check(f"quadratic majorant attained {uu},{vv}","20",abs(omission.subs({u:uu,v:vv}))==2*abs(uu)*abs(vv))
    # Atlas consensus on a common semantic state, one redundant representation.
    atlas=[sp.eye(2),M([[1,0],[0,1],[1,1]]),M([[2,0],[0,Q(1,3)]])]
    synth=[(aa.T*aa).inv()*aa.T for aa in atlas]
    target=M([[Q(1,2),Q(1,4)],[0,Q(1,3)]])
    locals_=[target+sp.diag(Q(1,10),0), target-sp.diag(Q(1,5),0), target]
    weights=[Q(1,4),Q(1,4),Q(1,2)]
    avg=sum((w*op for w,op in zip(weights,locals_,strict=True)),sp.zeros(2))
    charts=[aa*avg*ss for aa,ss in zip(atlas,synth,strict=True)]
    for i,j in itertools.product(range(3),repeat=2):
        t=atlas[j]*synth[i]
        check(f"reconciled chart pair {i}->{j}","21",zero(charts[j]*t*atlas[i]-t*charts[i]*atlas[i]))
    zz=M([Q(2,7),Q(-1,3)])
    for i,j in itertools.product(range(3),repeat=2):
        t=atlas[j]*synth[i]
        check(f"pullback norm transport {i}->{j}","21",synth[j]*t*atlas[i]*zz==zz)
    trial=M([[1,2],[3,4]])
    fro2=lambda q:sum(v*v for v in q)
    lhs=sum(w*fro2(trial-op) for w,op in zip(weights,locals_,strict=True))
    rhs=fro2(trial-avg)+sum(w*fro2(avg-op) for w,op in zip(weights,locals_,strict=True))
    check("atlas least squares variance identity","21",sp.simplify(lhs-rhs)==0)
    # Conditioning of an arbitrary left inverse away from consistency.
    ar=M([[1],[0]]); sr=M([[1,1000]])
    check("left inverse off-space amplification","21",sr*ar==sp.eye(1) and (sr*M([0,1]))[0]==1000,
          scope="negative control to bounding arbitrary synthesis by analysis singular value")
    coarse=M([[1,0]]);fine=sp.eye(2)
    xp,xm=M([0,1]),M([0,-1])
    check("strict refinement has no deterministic upward lift","22",coarse*xp==coarse*xm and fine*xp!=fine*xm)
    check("upward-lift half-diameter lower bound","22",(xp-xm).dot(xp-xm)==4 and xp.dot(xp)==xm.dot(xm)==1)
    # Enumerated posterior exact identities, no arbitrary zero probability for omitted programs.
    prior=[Q(1,2),Q(1,4),Q(1,8),Q(1,8)]
    likelihood=[Q(1,10),Q(1,2),Q(3,4),Q(1,5)]
    w=[p*l for p,l in zip(prior,likelihood,strict=True)];total=sum(w)
    post=[v/total for v in w]
    mixture_q=[Q(1,10),Q(3,5),Q(9,10),Q(1,3)]
    grammar=[]
    for n in range(1,5):
        zn=sum(w[:n]);pn=[w[i]/zn if i<n else 0 for i in range(4)]
        tau=1-zn/total
        tv=sum(abs(p-q) for p,q in zip(post,pn,strict=True))/2
        prior_tail=sum(prior[n:]);tail_bound=prior_tail/(zn+prior_tail)
        pred=abs(sum((p-q)*r for p,q,r in zip(post,pn,mixture_q,strict=True)))
        check(f"posterior grammar accounting n={n}","23",tv==tau and pred<=tau and tau<=tail_bound)
        grammar.append({"n":n,"posterior_omitted_mass":str(tau),"prior_tail_bound":str(tail_bound),"predictive_tv":str(pred)})
    # Parent mixture over whole records, exact evidence preservation.
    parent_prior=Q(2,5);alpha=[Q(1,3),Q(2,3)];child_l=[Q(1,4),Q(3,4)]
    parent_l=sum(a*l for a,l in zip(alpha,child_l,strict=True))
    other=Q(3,5)*Q(1,2)
    before=parent_prior*parent_l+other
    after=sum(parent_prior*a*l for a,l in zip(alpha,child_l,strict=True))+other
    check("prior-preserving split keeps evidence","24",before==after)
    check("prior-preserving split keeps aggregated posterior","24",
          sum(parent_prior*a*l/after for a,l in zip(alpha,child_l,strict=True))==parent_prior*parent_l/before)
    dup_before=Q(1,2)*Q(3,4)/(Q(1,2)*Q(3,4)+Q(1,2)*Q(1,4))
    dup_after=2*Q(1,3)*Q(3,4)/(2*Q(1,3)*Q(3,4)+Q(1,3)*Q(1,4))
    check("fresh mass for syntax duplicates changes posterior","24",dup_before==Q(3,4) and dup_after==Q(6,7),
          scope="negative control to unweighted syntactic duplication")
    # Mixing per time versus mixing a whole record differs.
    check("whole-record mixture is not per-step switching mixture","24",
          Q(1,2)*Q(1,4)**2+Q(1,2)*Q(3,4)**2 != (Q(1,2)*Q(1,4)+Q(1,2)*Q(3,4))**2)
    # Separate floating-point illustration, no empirical SOTA or discovery claim.
    numeric=[]
    bb=np.array([[0.5,0.25],[0,1/3]],float)
    xx=np.array([[1.,0.,1.],[0.,1.,1.]])
    for scale in [1e-6,1e-4,1e-2]:
        ee=scale*np.array([[1,0,-1],[0,1,0]],float)
        ff=scale*np.array([[0,1,0],[1,0,-1]],float)
        xt=xx+ee;yt=bb@xx+ff
        bhat=yt@np.linalg.pinv(xt)
        s=np.linalg.svd(xx,compute_uv=False)[-1]
        bound=(np.linalg.norm(ff,2)+np.linalg.norm(bb,2)*np.linalg.norm(ee,2))/(s-np.linalg.norm(ee,2))
        actual=np.linalg.norm(bhat-bb,2)
        check(f"floating-point perturbation bound scale={scale}","16",actual<=bound+1e-12,
              arithmetic="NumPy float64, tolerance 1e-12",scope="deterministic numerical sensitivity illustration")
        numeric.append({"scale":scale,"error":actual,"bound":bound})
    verification=ROOT/'verification';verification.mkdir(exist_ok=True)
    report={"version":"0.2.0","status":"PASS","python":platform.python_version(),
            "sympy":sp.__version__,"numpy":np.__version__,"checks_passed":len(RESULTS),
            "exact_checks_passed":sum(c['arithmetic']=='exact rational/symbolic' for c in RESULTS),
            "floating_point_checks_passed":sum(c['arithmetic']!='exact rational/symbolic' for c in RESULTS),
            "lean_kernel_verification":False,"production_runtime_modified":False,"checks":RESULTS}
    (verification/'learning_stability_checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (verification/'output_only_certificate.json').write_text(json.dumps(model.certificate(),indent=2)+'\n',encoding='utf-8')
    data={"scope":"Deterministic mathematical examples, not empirical benchmark scores.",
          "delay":{"training_observations":[str(v) for v in train],"outputs":[str(v) for v in true[:21]],
                   "naive_compression":[str(Q(1,2)**t) for t in range(21)],
                   "learned_predictions":[str(v) for v in future[:17]],"first_unseen_index":4},
          "memory":memory,"grammar":grammar,"numeric_sensitivity":numeric}
    (verification/'figure_data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(f"PASS: {len(RESULTS)} new finite checks ({report['exact_checks_passed']} exact, {report['floating_point_checks_passed']} float64).")
    print('General proof-kernel verification: NOT RUN. Production runtime: UNCHANGED.')
    print(verification/'learning_stability_checks.json')


if __name__=='__main__':
    main()
