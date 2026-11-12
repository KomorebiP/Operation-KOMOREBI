"""Author: Komorebi P. Bounded graph discovery with exact interval acceptance.

Searches declared canonical four-node 3-reactive, 4/5-resistor catalogs.
Numerical ranks and fits are untrusted search filters. Every successful return
contains an independently checked exact interval circuit certificate.
"""
from fractions import Fraction as F
import time
from interval_certificate import reduce_target
from interval_synthesis import certify_candidate


def find_topology_interval(P,Q,*,starts=2,max_nfev=600,max_candidates=2,seed=2026111223):
    from topology_search import fit_target
    started=time.perf_counter()
    try:P,Q=reduce_target(P,Q)
    except (ValueError,ZeroDivisionError) as exc:
        return {'status':'INVALID_INPUT','reason':str(exc)}
    if len(P)!=4 or len(Q)!=4 or P[-1]<=0:
        return {'status':'UNKNOWN','reason':'Current graph search supports positive-leading reduced (3,3) targets'}
    searches=[];rejections=[]
    for resistors in (4,5):
        try:
            search=fit_target(P,Q,resistors=resistors,starts=starts,max_nfev=max_nfev,
                              max_candidates=max_candidates,seed=seed)
        except (ValueError,ZeroDivisionError,OverflowError,FloatingPointError) as exc:
            searches.append({'resistors':resistors,'status':'SEARCH_ERROR','reason':str(exc)})
            continue
        searches.append({'resistors':resistors,**{k:v for k,v in search.items() if k!='proposals'}})
        for proposal in search.get('proposals',[]):
            branches=[{'type':{'R':'g','L':'h','C':'c'}[t],'nodes':[a,b]} for t,a,b in proposal['spec']]
            answer=certify_candidate(P,Q,branches,proposal['parameters'],
                                     fixed_parameters=proposal.get('fixed_parameters'))
            if answer['status']=='CERTIFIED_MINIMUM':
                answer['route']='canonical sparse graph proposal + independent exact rational interval certificate'
                answer['graph_discovery']={'catalog_index':proposal['catalog_index'],
                    'resistors':resistors,'seed':seed,'starts':starts,'max_nfev':max_nfev,
                    'proposal_scaled_residual':proposal['scaled_residual'],
                    'searched_catalogs':searches,
                    'scope':'four-node mixed q3 catalogs with four or five resistor branches'}
                answer['elapsed_seconds_total']=time.perf_counter()-started
                return answer
            rejections.append({'resistors':resistors,'catalog_index':proposal['catalog_index'],
                               'status':answer['status'],'reason':answer.get('reason')})
    return {'status':'UNKNOWN','reason':'No accepted interval certificate within declared graph and numerical search limits',
            'searched_catalogs':searches,'certificate_rejections':rejections,
            'elapsed_seconds':time.perf_counter()-started,
            'scope':'bounded topology search; no impossibility conclusion'}
