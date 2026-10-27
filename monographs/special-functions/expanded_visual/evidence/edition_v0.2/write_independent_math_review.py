"""Write the completed bounded review with current local source/evidence hashes.

This records an already performed review. It is not a theorem prover or a
replacement for the mathematical checks in the independently pinned runs.
"""
from datetime import datetime, timezone
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'evidence'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative):
    return json.loads((ROOT / relative).read_text())


def run_is_current(manifest):
    for item in manifest.get('input_artifacts', []):
        p = ROOT/item['path']
        if not p.is_file() or digest(p) != item.get('sha256_after',item['sha256']):
            return False
    return manifest['run'].get('exit_status') == 0


def main():
    chapters = {'Foundations':('foundations.tex',8),
                'I–III':('chapters_i_iii.tex',36), 'IV':('chapters_iv.tex',12),
                'V':('chapters_v.tex',12), 'VI':('chapters_vi.tex',12),
                'VII–VIII':('chapters_vii_viii.tex',24), 'Synthesis':('synthesis.tex',6)}
    for label,(file,count) in chapters.items():
        assert len(re.findall(r'\\lesson\{',(ROOT/file).read_text())) == count, label
    assert sum(count for _,count in chapters.values()) == 110
    scalar_text = (ROOT/'chapters_vii_viii.tex').read_text()
    assert r'\mu_{\alpha,\beta}(n)' in scalar_text
    assert 'indices modulo 5' in scalar_text
    assert scalar_text.count('$0<q<1$') >= 2

    arithmetic = []
    for p in E.glob('independent_arithmetic_*/manifest.json'):
        m=json.loads(p.read_text())
        if run_is_current(m):
            arithmetic.append((m['run']['started_at'],p,m))
    assert arithmetic, 'A fresh arithmetic run is required after regeneration.'
    arithmetic_path = max(arithmetic,key=lambda row:row[0])[1]
    manifests = [E/'independent_foundation_final/manifest.json',
                 E/'independent_cross_series_run/manifest.json', arithmetic_path,
                 E/'independent_scalar_run/manifest.json',E/'iv_v_independent_run/manifest.json']
    runs=[]
    for p in manifests:
        m=json.loads(p.read_text())
        assert run_is_current(m),str(p)
        for item in m['outputs']:
            assert digest(ROOT/item['path']) == item['sha256'],item['path']
        record={'manifest':str(p.relative_to(ROOT)),'sha256':digest(p),
                     'claim_id':m['claim_id'],'command':m['command'],
                     'environment':m['environment'],'runtime_seconds':m['run']['runtime_seconds'],
                     'exit_status':m['run']['exit_status'],'resource_limits':m['run']['resource_limits'],
                     'current_input_hashes_and_output_hashes_verified':True,
                     'assertion_tested':m['mathematics']['assertion_tested'],
                     'bounds':m['mathematics']['bounds']}
        if m['claim_id']=='VISUAL_ARITHMETIC_PRESENTATION_PRESERVATION_V02':
            record['record_kind']='provenance_only_refresh'
            record['retained_independent_computation']='evidence/independent_arithmetic_final_snapshot/manifest.json'
            record['mathematical_computation_rerun']=False
        else:
            record['record_kind']='independent_computation'
        runs.append(record)

    scripts = sorted(ROOT.glob('figures_*.py'))
    assert {p.name for p in scripts} == {'figures_foundations.py','figures_i_iii.py',
        'figures_iv.py','figures_v.py','figures_vi.py','figures_vii_viii.py',
        'figures_synthesis.py','figures_iv_vi.py'}
    portability=[]
    for p in scripts:
        values=[n.value for n in ast.walk(ast.parse(p.read_text()))
                if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        hardcoded=[s for s in values if '/workspace/' in s or '/scratch/' in s or 'special_function_sources' in s]
        assert not hardcoded,p.name
        portability.append({'script':p.name,'absolute_scratch_or_extraction_literals':0,
                            'local_dependency_resolution_reviewed':True})

    bounds=[
      {'lesson':'F05','bound':'e^z z^13/13!; uniform e^2 2^13/13! for real 0<=z<=2',
       'reason':'Taylor integral/Lagrange remainder; exact polynomial coefficient routing is separate.'},
      {'lesson':'I04','bound':'8^22/(66+r)! divided by 1-8/((67+r)(68+r)(69+r)), r=0,1,2',
       'reason':'Geometric majorant for omitted packet terms; unmatched finite-row term <=8^22/65!.'},
      {'lesson':'I12/II/III','bound':'Energy tail <=1/(3N^3); signed amplitude tail <=1/N',
       'reason':'Drop bounded filters and Mobius factors; use decreasing-power integral tails.'},
      {'lesson':'II06','bound':'2^m/((3+2m)N^(3+2m))',
       'reason':'1-x_n=2/n^2-1/n^4 <=2/n^2; every term is positive.'},
      {'lesson':'II08','bound':'1/(3N^3 min_{x in [0,1]}|1-zx|)',
       'reason':'Sampled unmasked slit-plane grid; denominator distance is positive. No grid proof asserted.'},
      {'lesson':'II11/III07','bound':'CDF <=T0/E_N; normalized moment <=(T_m+M_m,N*T0)/E_N',
       'reason':'T_m <=(2k)^m/((3+2m)N^(3+2m)); numerator and normalization tails both included.'},
      {'lesson':'II12','bound':'Normalized character entry <=2T0/E_N',
       'reason':'Characters share their actual modulus and each absolute kernel tail is <=T0.'},
      {'lesson':'III07','bound':'0<=U_k^m-u_k^m<=m U_k^(m+1)/(4k), k>=1,m>=1',
       'reason':'u_k=U_k-U_k^2/(4k); apply difference of nonnegative powers. Moment convergence has its own source bridge.'},
      {'lesson':'III10','bound':'Input-moment tails are recorded; no determinant error interval claimed',
       'reason':'Conditioned determinant illustration uses scaled moments; coefficientwise asymptotic is source-dependent.'},
      {'lesson':'III12','bound':'Positive cusp difference tail <=1/N',
       'reason':'w_n/(1-x_n)<=1/n^2. Abelian cusp is conditional on the source energy asymptotic and retains only o(sqrt(epsilon)).'},
      {'lesson':'IV03/IV04','bound':'Finite sinc Gram integration is exact; infinite unnormalized entry tail <=1/(3N^3)',
       'reason':'Finite-time extraction and infinite-model limits are explicitly separated.'},
      {'lesson':'IV11','bound':'Normalized EGF remainder <=zeta(2)*P(41,8) on x in [0,8]',
       'reason':'Poisson tail after degree 40; number-support tail is separately <=1/N.'},
      {'lesson':'V01/V02/V05/V08','bound':'Gamma-CDF crop masses and analytic omitted-amplitude tails',
       'reason':'Positive shape and Jacobian u=e^y retained. Finite quadrature estimates are separate from omitted integrals.'},
      {'lesson':'V10','bound':'48-node generalized Gauss-Laguerre exact polynomial range through degree 95',
       'reason':'Displayed degree-0..4 products have degree at most eight; numerical residual is floating-point.'},
      {'lesson':'V12','bound':'Direct signed cutoff <=1/N; J=80 reference is finite',
       'reason':'a>1,beta>0,r>0 for absolute exchanges; centered binomial coordinates are not assigned a universal computed tail certificate.'},
      {'lesson':'VI05','bound':'4/pi*atan(exp(-8*pi)) <1.55e-11',
       'reason':'rho_1<=1; uniform omitted convolution is bounded by omitted rho_1 mass.'},
      {'lesson':'VI06','bound':'4 exp(-10pi)/(10pi(1-exp(-20pi))) <2.90e-15',
       'reason':'Bound |cos-1|<=2 and 1/sinh(pi x) above cutoff; stable sine-squared cancellation at zero.'},
      {'lesson':'VI04/VI12','bound':'min(1,2 sec(t/2)^s exp(-tL)), t=2 atan(2L/s)',
       'reason':'Two-sided Chernoff from M(t)=sec(t/2)^s, |t|<pi; finite windows are not renormalized.'},
      {'lesson':'VI09','bound':'Rank-61 omitted norm sigma_61=sqrt(1/10920)',
       'reason':'Exact monotone singular-value sequence; retained degrees are 0..60. Compactness for t>0 and Schatten criterion pt>2.'},
      {'lesson':'VI10','bound':'Shape-two position strip |h|<=log(3) captures 11/16',
       'reason':'Exact Beta(2,2) CDF difference, with all modulation frequencies integrated.'}
    ]
    revised=[
      'Arithmetic exponent beta harmonized; continuous shapes alpha/gamma and Bernoulli translation alias distinguished.',
      'Actual-modulus coprimality uses gcd, rather than a prime-modulus shortcut.',
      'I04 explicitly uses 22-term samples and records packet/unmatched-row tails; displayed residual includes rounding.',
      'Truncation-tail bands are not advertised as certified floating-point intervals.',
      'III07 active coordinates and moment bridge are explicit; III08 finite polynomials are monic.',
      'I04 index m>=1 and III03 b0=0,p_-1=0 boundaries are explicit.',
      'Synthesis coherent intensity uses raw |A|^2 with dh d_eta/(2pi); authority dependencies are local copies.',
      'VII overlap gauge and positive-adjacent Jacobi gauge are distinct; common-space loop has a wrong-kernel negative control.',
      'VIII07 higher-level q entropy is a bounded numerical negative control; fixed-kernel entropy and N=1 monotonicity remain distinct.',
      'VIII08 N=6 matrix is labeled seven-channel; tangent skew residual is checked before antisymmetrization.',
      'VIII11 duality explicitly swaps lattice coordinates; VIII10 tree indices are modulo five.',
      'Scalar q-Racah/AW aliases, 0<q<1 finite-series domains, nonzero denominators, and shifted AW eigenvalue convention are explicit.'
    ]
    records=['evidence/foundation_checks.json','evidence/figures_i_iii_audit.json',
             'evidence/figures_iv_audit.json','evidence/figures_v_audit.json',
             'evidence/figures_vi_audit.json','evidence/vii_viii_audit.json',
             'evidence/synthesis_computations.json','evidence/synthesis_computation_manifest.json']
    author_records=[]
    for file in records:
        data=load(file)
        author_records.append({'path':file,'sha256':digest(ROOT/file),
                               'scope':'Author-generated figure/example record, reviewed but not counted as an independent rerun.'})
    q_audit=load('evidence/vii_viii_audit.json')
    assert len(q_audit['checks'])==58 and all(c['passed'] for c in q_audit['checks'])
    inputs=[file for file,_ in chapters.values()]+['main.tex','chapters_iv_vi.tex','guide_style.py','requirements.txt']
    inputs += [p.name for p in scripts]
    inputs += ['evidence/ADOPTED_MATHEMATICAL_CHANGES.md','evidence/REFERENCE_CORRECTIONS.tex',
               'evidence/SPECIAL_FUNCTIONS_CLAIM_INDEX.csv']
    inputs += [str(p.relative_to(ROOT)) for p in sorted((E/'synthesis_authority').rglob('*')) if p.is_file()]
    inputs += [str(p.relative_to(ROOT)) for p in sorted(E.glob('*INDEPENDENT_REVIEW*')) if p.is_file()]
    payload={'schema_version':1,'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
      'status':'PASS_BOUNDED_MATHEMATICAL_REVIEW','unresolved_substantive_issues':[],
      'scope':{'lesson_count':110,'components':{k:v[1] for k,v in chapters.items()},
               'reviewed':'All lesson prose/formulas, seven figure generators and a local IV–VI wrapper, declared domains, phase/gauge conventions, analytic truncation/quadrature tails and numerical-caption evidence.',
               'figure_generators':7,'local_generator_wrappers':1,
               'authority':'Corrected v0.1 cores and adopted C01–C12 interpretation; local authority copies supplied in this package.',
               'visual_layout':'Reviewed separately by root; no mathematical certificate is inferred from rendering.',
               'original_pytest_suites_rerun':False},
      'current_source_hashes':[{'path':file,'sha256':digest(ROOT/file)} for file in inputs],
      'independent_current_runs':runs,'independent_mathematical_computations_retained':5,
      'mathematics_rerun_for_final_presentation_changes':False,
      'author_generation_records_observed':author_records,
      'VII_VIII_author_checks':{'passed':58,'total':58,'role':'Bounded author checks, distinct from independent runs.'},
      'analytic_bounds_reviewed':bounds,'applied_clarifications':revised,'portable_figure_scripts':portability,
      'phase_and_gauge_checks':['Negative-sign unitary DFT; coherent routes added before squaring.',
         'Unitary Fourier exp(-i omega y) and centered ambiguity exp(+i eta y) retained; Fourier degree i^n independently checked exactly.',
         'Cross-spectrogram density |A|^2/(2pi) and raw intensity with normalized measure are distinguished.',
         'First-row/column-positive overlap gauge does not imply positive adjacent Casimir entries; SJS and SR change together.',
         'q-coproduct retains ordered factors; matched signs are required for derivatives and limits.'],
      'remaining_research_obligations':['Principal signed Mobius coherence asymptotic remains open and is not inferred from finite plots.',
         'Full shape-to-scalar q-Racah base/parameter/weight/norm/phase dictionary remains separate.',
         'Analytic asymptotic and all-Schwartz-seminorm results retain their declared source proof dependencies.',
         'No full analytic Lean build is established by the claim-status chart.'],
      'historical_attempts':{'first_foundation_run':{'manifest':'evidence/independent_foundation_run/manifest.json',
         'status':'failed','cause':'Decimal 0**0 in the independent checker at z=0.',
         'repair':'Evaluate the polynomial constant term explicitly; successful current foundation run is listed above.',
         'source_snapshot':'evidence/independent_foundation_run/source_at_run.py'},
         'first_presentation_preservation_check':{'manifest':'evidence/independent_arithmetic_presentation_refresh/manifest.json',
            'status':'failed','cause':'The checker used a shallow JSON copy, so restoring an old PDF hash also changed the nested in-memory object checked afterward.',
            'repair':'Use a deep copy; the on-disk author audit was correct. The successful current preservation record retains all arithmetic results without rerunning them.',
            'source_snapshot':'evidence/independent_arithmetic_presentation_refresh/source_at_run.py',
            'audit_snapshot':'evidence/independent_arithmetic_presentation_refresh/audit_at_run.json'},
         'earlier_successful_snapshots':'Older input epochs remain recorded. The retained arithmetic computation is linked to current presentation inputs by its explicit provenance bridge.'},
      'non_claims':['No universal proof from sampled numerical residuals or plots.',
         'No interval certification for floating-point/high-precision roots, entropy values or quadrature estimates.',
         'The reported 70-digit child comparison in the VII–VIII author record has no bundled child code and is not counted as a reproducible independent run.',
         'The original 148 pytest cases and archived built-in checks were not rerun for this guide.']}
    preservation=E/'FINAL_PRESENTATION_PRESERVATION.json'
    if preservation.exists():
        payload['final_presentation_preservation']={'path':str(preservation.relative_to(ROOT)),
            'sha256':digest(preservation),'mathematical_computations_rerun':False}
    payload['report_writer']={'path':'evidence/write_independent_math_review.py','sha256':digest(Path(__file__))}
    (E/'INDEPENDENT_MATH_REVIEW.json').write_text(json.dumps(payload,indent=2)+'\n')
    table='\n'.join('| '+r['claim_id']+' | '+r['manifest']+' | '+str(r['exit_status'])+' | '+format(r['runtime_seconds'],'.3f')+' s |' for r in runs)
    prose="""# Independent mathematical review

Result: **PASS, within the bounded scope below.** No unresolved substantive inconsistency was found in the final 110 lessons: eight foundations, twelve lessons for each of Papers I–VIII, and six synthesis lessons. The accompanying JSON pins the current text, scripts and evidence. Rendering and layout are a separate root review.

The review checked formulas, domains, numerical captions against recorded computations, phase and gauge conventions, portable dependencies, and every claimed numerical truncation or quadrature tail. Corrected v0.1 cores and the adopted C01–C12 register are the authority. This is a review of the new guide, not a new proof of every theorem in the original series. The original 148 pytest cases were not rerun.

## Independent computations and current provenance

Five independent mathematical computations are retained. Four original manifests remain current; the arithmetic computation is carried forward by a current presentation-preservation bridge. The five current record manifests have successful exits and matching input/output hashes. Commands, versions, tested bounds and resource caps are in the manifests and JSON. The IV–V computation is an independent reviewer-child run, distinct from the source author's helper and figure run. The presentation bridge repeats no arithmetic calculations.

| Claim | Manifest | Exit | Time |
|---|---|---:|---:|
"""+table+"""

The retained computations independently verify exact coefficient/DFT/moment examples and a 70-digit Decimal Taylor grid; exact Bernoulli child values and packet-tail constants; low-order energy/node/pole/residue constants; exact binary/multinomial energy, a frame strip and singular-value tail; full-space q-Casimir benchmarks and a higher-level entropy decrement; 24 exact rational-point shifted Askey–Wilson witnesses and the exact collapsed q-Racah lattice; and 80-digit Padé examples plus exact symbolic Fourier degree phases 0–4.

At N=3 and half-shapes, the independently rebuilt row-index-one entropy decreases from approximately 1.242937939 at q=0.78 to 1.228999796 at q=0.80. Its change is approximately −0.013938143 nats. This is a bounded double-precision negative control, not an interval proof certificate. The source author's distinct saved endpoints have a decrease of approximately −0.007783987. Its separate reported 70-digit child comparison is labeled as reported because that child code is not bundled.

The two independently recomputed order-four Padé models match their first eight moments with residuals at most 1.06e−81 at 80 working digits. Later four discrepancies reach 8.27236e−8 signed and 8.10056e−9 positive. Nonzero denominator leading coefficients and separated numerical roots are present. These are finite numerical findings; universal nonbreakdown, simple roots, physical signed support and stability are not inferred. The exact generic moment sequence (0,1,0,0) also demonstrates denominator degree drop despite Hankel nonbreakdown.

## Bounds and interpretation

The JSON records each reviewed bound and derivation. Arithmetic energy and signed tails use 1/(3N³) and 1/N; normalized moments/CDFs include normalization tails; difference layers use (1−x_n)≤2/n²; slit-resolvent bounds retain the sampled denominator distance; and the cusp uses a positive tail majorant. I04's 22-term exponential packets have geometric omitted-term bounds and a separate unmatched-row term. Displayed floating-point residuals and bands do not become interval arithmetic certificates.

Continuous-window crops retain their omitted mass. Gamma-CDF or analytic amplitude tails are separate from numerical quadrature estimates. The Meixner convolution bound is below 1.55e−11, the Lévy tail bound below 2.90e−15, and optimized two-sided Chernoff tails follow the stated secant moment-generating function. The rank-61 transfer tail is exactly sigma_61=√(1/10920); the shape-two frame strip is exactly 11/16 after integrating all frequencies. Gauss–Laguerre's polynomial range and Padé's contracted moment range are stated explicitly. No determinant error interval is claimed for the scaled-Hankel illustration.

Source-dependent energy/Gamma/Laguerre limits remain fixed-degree or declared analytic results. The cusp remains conditional on the source energy law and its Abelian argument, without an O(epsilon) strengthening. The all-Schwartz heat limit remains a source proof input. Finite plots do not establish those statements or the open signed arithmetic obstruction.

## Final consistency and portability

All requested revisions are applied: actual-modulus gcd masking; beta/shape/translation aliases; explicit zero atom and recurrence boundaries; monic endpoint polynomials and active coordinates; coherent intensity normalized once; and local copied synthesis authority inputs. Fourier exp(−i omega y), centered ambiguity exp(+i eta y), and the degree phase i^n are preserved.

The overlap's first-row/column-positive gauge is distinct from the positive-adjacent Jacobi gauge; SJS and the rephased overlap change together. Fixed-kernel entropy nondecrease is distinguished from the monotone N=1 q model and its nonmonotone higher-level numerical example. Common-space loop closure has a wrong-kernel negative control. Scalar q-Racah duality swaps its lattice parameters explicitly, tree indices are cyclic, and scalar finite-series domains require 0<q<1 and nonzero denominators. The Askey–Wilson eigenvalue includes the displayed operator shift.

All seven figure generators and their local IV–VI wrapper resolve package dependencies and contain no absolute scratch/extraction literals. Synthesis reads its packaged authority copies. The source author's completed VII–VIII generation has 58/58 bounded checks passed. Author generation records for all 110 figures are reviewed evidence, separate from the independent computations.

Final page inspection shortened I04's two titles and rasterized only V03/VI03 colored mesh cells, retaining vector axes and labels. Numerical audit fields are preserved exactly. The I04 bridge restores its prior source by undoing only the standalone-render extraction and title changes, then verifies byte equality with the prior pinned source. It also verifies all 36 arithmetic audit entries/checks and the original computation results. Final source/audit hashes include these presentation changes; no unrelated mathematical computations were repeated.

The complete scalar-to-matrix q-Racah dictionary and full analytic Lean build remain explicit obligations. A scalar termination condition is not advertised as positive orthogonality. No continuous-series unitary transform is inferred from the scalar Askey–Wilson plot.

## Recorded failure and refreshes

The first independent foundation attempt failed at z=0 because Decimal treats 0**0 as invalid. The checker was repaired by writing the polynomial constant term explicitly; the current foundation run passes. Its original log, manifest and exact source snapshot remain preserved. The first presentation-preservation attempt failed because the checker used a shallow JSON copy; a deep copy fixed that check, and the on-disk author audit was correct. That failed attempt and exact source/audit snapshots are also preserved. Older input epochs remain recorded. The arithmetic computation is retained through its current provenance bridge; only the current records listed above directly pin the final inputs.
"""
    (E/'INDEPENDENT_MATH_REVIEW.md').write_text(prose)
    print(json.dumps({'status':payload['status'],'lessons':110,'independent_current_runs':len(runs),
                      'current_source_hashes':len(inputs)}))


if __name__=='__main__':
    main()
