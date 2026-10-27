#!/usr/bin/env python3
"""Bounded editorial checks. Does not evolve a collapse or compile Lean."""
from __future__ import annotations
import hashlib
import json
import platform
import sys
import time
import types
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
import sympy as sp


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / 'evidence/gravity/strong_fields_identity_checks'
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    started = datetime.now(timezone.utc).isoformat()
    archive = root / 'recovered_sources/legacy/Projector_Refinement_Physics_Volume_I_Source_and_Reproducibility.zip'
    prefix = 'Projector_Refinement_Physics_Volume_I_Source/'
    sources = []
    checks = []
    def add(name, passed, detail):
        checks.append({'name': name, 'status': 'passed' if passed else 'failed', 'detail': detail})
    with ZipFile(archive) as z:
        for short, function in [('Finite_Range_Spherical_Electrovac_Verification.py', 'symbolic_checks'), ('Finite_Range_Spherical_Scalar_Collapse_Verification.py', 'symbolic_audit')]:
            member = prefix + 'verification/' + short
            raw = z.read(member)
            sources.append({'member': member, 'sha256': hashlib.sha256(raw).hexdigest()})
            mod = types.ModuleType('_strong_field_check_' + short.replace('.', '_'))
            mod.__file__ = str(archive) + '::' + member
            sys.modules[mod.__name__] = mod
            exec(compile(raw, mod.__file__, 'exec'), mod.__dict__)
            result = getattr(mod, function)()
            algebraic = {k:v for k,v in result.items() if k != 'horizon_identity'}
            add(short + ':' + function, all(v == '0' for v in algebraic.values()), result)
        scalar_member = prefix + 'data/Finite_Range_Spherical_Scalar_Collapse_Verification.json'
        scalar_raw = z.read(scalar_member)
        scalar = json.loads(scalar_raw)
        sources.append({'member': scalar_member, 'sha256': hashlib.sha256(scalar_raw).hexdigest()})
        em_member = prefix + 'data/finite_range_strong_field_results.json'
        em_raw = z.read(em_member)
        em = json.loads(em_raw)
        sources.append({'member': em_member, 'sha256': hashlib.sha256(em_raw).hexdigest()})
    P, F, v, s = sp.symbols('P F v s', real=True)
    wp, wm = sp.symbols('wp wm', real=True)
    substitution = {P:(wp+wm)/2, F:(wp-wm)/2}
    energy = (P**2+F**2)/2 + v*P*F
    flux = s*(P+v*F)*(F+v*P)
    e_diff = sp.expand(energy.subs(substitution) - ((1+v)*wp**2+(1-v)*wm**2)/4)
    j_diff = sp.expand(flux.subs(substitution) - s*((1+v)**2*wp**2-(1-v)**2*wm**2)/4)
    add('independent null-channel energy', e_diff == 0, str(e_diff))
    add('independent null-channel flux', j_diff == 0, str(j_diff))
    M, Q, R = sp.symbols('M Q R', positive=True)
    p = sp.sqrt(2*M*R-Q**2)
    derivative = sp.diff(-p/R, R)
    target = (M*R-Q**2)/(R**2*p)
    add('independent electrovac source Lipschitz derivative', sp.simplify(derivative-target)==0, str(sp.simplify(derivative-target)))
    table = scalar['convergence']
    finest = table[-1]
    event_gap = finest['final_time'] - finest['horizon_time']
    nonmonotone = table[1]['horizon_time'] > table[0]['horizon_time']
    mass_half = max(abs(x['horizon_mass']-x['horizon_radius']/2) for x in table)
    add('archived scalar table7rows and mass-half identity', len(table)==7 and mass_half<1e-14, {'rows':len(table), 'max_error':mass_half})
    add('archived event fields later than interpolated time', event_gap>0, {'finest_event_time':finest['horizon_time'], 'finest_fields_time':finest['final_time'], 'gap':event_gap})
    add('archived scalar coarse-event nonmonotonicity recorded', nonmonotone, {'N600_time':table[0]['horizon_time'], 'N800_time':table[1]['horizon_time']})
    add('archived check counts agree with arrays', em['check_counts']['PASS']==sum(x['status']=='PASS' for x in em['checks'])==19 and scalar['check_counts']['PASS']==sum(x['status']=='PASS' for x in scalar['checks'])==12, {'electrovac':19,'scalar':12,'rerun':False})
    result = {'contract':'source symbolic identities and independent low-dimensional algebra; archived JSON consistency only', 'source_members':sources, 'checks':checks, 'full_collapse_rerun':False, 'fresh_lean_compile':False}
    result_path = out / 'results.json'
    result_path.write_text(json.dumps(result, indent=2)+'\n')
    script_path = Path(__file__).resolve()
    manifest = {
      'schema_version':1, 'claim_id':'C_STRONG_FIELD_EDITORIAL_IDENTITIES',
      'repository':{'commit':'source archive SHA256 '+hashlib.sha256(archive.read_bytes()).hexdigest(), 'dirty':True},
      'command':'python tools/verify_strong_field_identities.py',
      'environment':{'software':[f'Python {platform.python_version()}',f'SymPy {sp.__version__}'], 'hardware':platform.machine()},
      'mathematics':{'assertion_tested':result['contract'], 'coefficient_domain':'exact symbolic rational functions with algebraic square roots; archived IEEE double results read without evolution', 'conventions':'G=c=1; mass coordinate and lapse conventions of Chapters48/49; radial derivative prime', 'inputs':['tools/verify_strong_field_identities.py','recovered_sources/legacy/Projector_Refinement_Physics_Volume_I_Source_and_Reproducibility.zip'], 'bounds':{'symbolic_code_paths':['electrovac symbolic_checks','scalar symbolic_audit'],'independent_identities':3,'archived_event_rows':7,'full_pde_evolution_steps':0}, 'non_claims':['No new collapse or electrovac numerical evolution','No universal convergence theorem','No Lean compilation','No unrestricted3+1 Einstein solver']},
      'randomness':{'used':False,'generator':'','seed':None},
      'run':{'started_at':started,'runtime_seconds':time.perf_counter()-start,'exit_status':0 if all(x['status']=='passed' for x in checks) else 1},
      'outputs':[{'path':str(result_path.relative_to(root)), 'sha256':hashlib.sha256(result_path.read_bytes()).hexdigest()}],
      'checks':checks, 'result':'implementation and finite assertion verified in the stated range' if all(x['status']=='passed' for x in checks) else 'finite assertion failed',
      'residual_risks':['Source symbolic code reviewed and independently checked only in the three displayed auxiliary identities','Archived numerical receipts lack authenticated execution provenance and are not freshly reproduced','Version1 manifest lacks machine-checked resource limits or runner-owned input freshness']
    }
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'failed':sum(x['status']=='failed' for x in checks),'seconds':manifest['run']['runtime_seconds']}))
    raise SystemExit(manifest['run']['exit_status'])


if __name__ == '__main__':
    main()
