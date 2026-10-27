from pathlib import Path
import hashlib,json,re

base=Path('/workspace/scratch/ea498747acd5')
root=base/'work/Komorebi_LSM_Lean_0.18.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
claims={
 '58': {
  'modules':['CellDistance','PositiveCellApproximation','PositiveCellResolution','PositiveCellUniform','PositiveCellP58'],
  'endpoints':['Komorebi.LSM.PositiveCellApproximation.positive_cell_average_certificate','Komorebi.LSM.PositiveCellApproximation.positive_equal_interval_certificate'],
  'scope':'Actual normalized Bochner cell averages on a finite measurable positive-mass partition preserve the original cone, exact integrated mass and every cell operator. The genuine induced probability-cone base norm gives the Lh resolution bound. Actual uniform equal-interval distance integrals give Lh/3. Null/empty conventions and required finite masses, metric and Lipschitz hypotheses remain explicit; a point sample is not substituted for an integral.'},
 '59': {
  'modules':['BaseNormIntegration','TimeRecords','ContinuousTVDensity','ContinuousTV','ConditionalEventTV'],
  'endpoints':['Komorebi.LSM.ContinuousTV.integrated_contraction','Komorebi.LSM.ContinuousTV.record_lawTV_le'],
  'scope':'Actual time-dependent Bochner DensityInstrument families on a common finite-dimensional probability cone and probability reference, with finite actions and one common measurable randomized full-history policy, have actual finite record-law TV at most min(1,(e0+sum epsilon)/2). Integrated contraction is derived from positive decompositions, and TV from the signed-measure half-density identity; no branch-density lower margin is required. The optional conditional-event helper proves an eventwise 2TV/min-masses bound with both masses positive, not the stronger adjacent full conditional-law statement.'},
 '60': {
  'modules':['CertifiedTemplate'],
  'endpoints':['Komorebi.LSM.CertifiedTemplate.matches_iff_scalar_system','Komorebi.LSM.CertifiedTemplate.observable_match_unique','Komorebi.LSM.CertifiedTemplate.fixed_template_recognition','Komorebi.LSM.CertifiedTemplate.record_law_transport','Komorebi.LSM.CertifiedTemplate.fitted_initial_check'],
  'scope':'Literal fixed-template coefficient/mass matching is a finite real linear system. Fitted coefficient-word observability derives uniqueness among all linear matches, including singular competitors. An invertible match transports the actual matrix-domain polynomial Gram certificate with unchanged Gram data, exact mass and actual finite record laws. Fitted initial PSD and mass normalization remain a separate check. Observability neither supplies invertibility nor guarantees existence.'},
 '61': {
  'modules':['ContinuousPopulationBridge','ContinuousRealizationP61'],
  'endpoints':[],
  'scope':'P61 integration is pending final source review; this preparation script refuses acceptance until reviewed endpoints are supplied.'},
 '62': {
  'modules':['EllipsoidGeometry','EllipsoidDualCS','OrientedEllipsoid','EllipsoidPolynomial'],
  'endpoints':['Komorebi.LSM.OrientedEllipsoid.PolynomialCertificate.preserves','Komorebi.LSM.OrientedEllipsoid.PolynomialCertificate.record_law_probability','Komorebi.LSM.OrientedEllipsoid.PolynomialCertificate.record_law_prefix'],
  'scope':'Actual positive-definite metric and centered mass coordinates derive a genuine curved ProbabilityCone, including empty spatial dimension. Literal Q, PSD remainder and nonnegative multiplier plus both inverse-metric orientation inequalities imply cone preservation. Finite interval SOS/Gram/degree/coefficient and exact moment checks construct the actual uniform-reference polynomial DensityInstrument and arbitrary-policy probability laws, word densities and prefixes at every horizon. This is a sufficient replayable certificate, not a completeness result for search.'},
 '63': {
  'modules':['EllipsoidDiscovery','EllipsoidDiscoveryP63'],
  'endpoints':['Komorebi.LSM.EllipsoidDiscoveryP63.conditional_operator_only_ellipsoid_discovery','Komorebi.LSM.EllipsoidDiscoveryP63.finite_certificate_all_horizons'],
  'scope':'The literal fitted polynomial ratio, its invertibility and mass row derive the affine block form and unique fixed center. An actual one-dimensional symmetric invariant-form subspace with a positive-definite member, and an actual rank-one fitted anchor with nonzero normalized displacement, derive the unique normalized positive metric. Complete P62 witnesses, exact mass and initial coverage for the same fitted family then yield actual all-horizon laws. Boundary placement remains a conditional proposal; failed discovery does not prove invalidity.'},
 '64': {
  'modules':['BernsteinKernel','PositivePolynomialApproximation'],
  'endpoints':['Komorebi.LSM.BernsteinKernel.kernel_squared_distance','Komorebi.LSM.PositivePolynomialApproximation.approximation_power_expansion','Komorebi.LSM.PositivePolynomialApproximation.approximatingInstrument','Komorebi.LSM.PositivePolynomialApproximation.induced_lipschitz_approximation_error','Komorebi.LSM.PositivePolynomialApproximation.common_policy_law_error'],
  'scope':'Literal Bernstein-Durrmeyer integral coefficients define cone-positive degree-at-most-n polynomial operators with exactly unchanged integrated mass. The actual doubly stochastic kernel has squared displacement 1/(3(n+2)); its actual joint-law variance inequality gives integrated genuine base-norm error L/sqrt(3(n+2)) under the stated induced-norm Lipschitz premise. Actual common-policy record laws obey min(1,TL/(2sqrt(3(n+2)))). No finite true-degree assumption is imposed; adjacent scalar examples are separate.'},
 '65': {
  'modules':['BernsteinCoefficientError'],
  'endpoints':['Komorebi.LSM.BernsteinCoefficientError.fitted_record_probability','Komorebi.LSM.BernsteinCoefficientError.uniform_bias_plus_coefficient_error','Komorebi.LSM.BernsteinCoefficientError.separate_correction_budget'],
  'scope':'Actual fitted positive Bernstein coefficients with exact average mass define a genuine DensityInstrument and finite policy probability laws. Normalized-input genuine base-norm coefficient budgets integrate to their average; the finite-action maximum is added to the actual P64 L/sqrt(3(n+2)) approximation bias. A separately supplied actual correction discrepancy is added by a proved integral triangle inequality. Positivity and mass alone do not erase coefficient error.'},
}
reviews=[
 'verification/development_p58/RAW_P58_REVIEW.json',
 'verification/development_p59/RAW_REVIEW_BY_DENSITY.json',
 'verification/development_p59/RAW_DENSITY_HELPER_REVIEW.json',
 'verification/development_certified_template/RAW_P60_REVIEW.json',
 'verification/development_p61/RAW_COORDINATOR_REVIEW.json',
 'verification/development_p62/RAW_COORDINATOR_REVIEW.json',
 'verification/development_p63/RAW_REVIEW_APPROXIMATION.json',
 'verification/p64_positive_polynomial/RAW_COORDINATOR_REVIEW.json',
 'verification/development_p65/RAW_REVIEW_APPROXIMATION.json',
]
# P61 is supplied only after the coordinator has read the frozen final sources.
p61=json.loads((root/'verification/development_p61/ACCEPTED_MAPPING.json').read_text())
assert p61['status']=='complete' and p61['modules']==claims['61']['modules']
claims['61']=p61
new={m for c in claims.values() for m in c['modules']}
ordered=[]
def visit(m):
 if m in ordered:return
 for dep in re.findall(r'^import KomorebiLSM\.(\w+)$',(root/'KomorebiLSM'/f'{m}.lean').read_text(),re.M):
  if dep in new:visit(dep)
 ordered.append(m)
for m in sorted(new):visit(m)
assert len(ordered)==len(new)==22
def hashes(x):
 if isinstance(x,str):return {x} if re.fullmatch('[0-9a-f]{64}',x) else set()
 if isinstance(x,dict):return set().union(*(hashes(v) for v in x.values()))
 if isinstance(x,list):return set().union(*(hashes(v) for v in x))
 return set()
review_hashes=set().union(*(hashes(json.loads((root/rel).read_text())) for rel in reviews))
accepted={m:sha(root/'KomorebiLSM'/f'{m}.lean') for m in ordered}
for m,h in accepted.items():assert h in review_hashes,('Current source is not bound by an accepted raw review',m,h)
cfg={'modules':ordered,'claims':claims,'accepted_source_sha256':accepted,'review_records':{rel:sha(root/rel) for rel in reviews}}
dest=base/'maintenance/accepted_claims_v018.json'
dest.write_text(json.dumps(cfg,indent=2)+'\n')
print(dest)
