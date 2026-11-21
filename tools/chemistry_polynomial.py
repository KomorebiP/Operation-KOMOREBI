"""Publish the local polynomial extension without altering predecessor evidence."""
from fractions import Fraction as F
import hashlib,json
import markdown
from chemistry_polynomial_data import AREA,DATA,payload,replay

PROOF='read/computational-chemistry/polynomial-responses.html'
def prepare(site):
    raw=payload(site.root)
    if (site.root/DATA).read_bytes()!=raw:raise ValueError('Stale polynomial fixture')
    digest=hashlib.sha256(raw).hexdigest();site.write('assets/chemistry/polynomial-v1.json',raw.decode())
    shared=(site.root/'website/assets/chemistry-lab-core.mjs').read_bytes();site.write('assets/chemistry-lab-core.mjs',shared.decode())
    core=(site.root/'website/assets/chemistry-polynomial-core.mjs').read_text(encoding='utf-8').replace("'./chemistry-lab-core.mjs'","'./chemistry-lab-core.mjs?v="+hashlib.sha256(shared).hexdigest()[:12]+"'")
    site.write('assets/chemistry-polynomial-core.mjs',core)
    css=(site.root/'website/assets/chemistry-polynomial.css').read_bytes();site.write('assets/chemistry-polynomial.css',css.decode())
    package=replay(site.root);target=site.output/'assets/chemistry/stage18-replay.zip';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(package)
    for name in ['POLYNOMIAL_RESPONSES.md','SELF_REVIEW.json']:
        target=site.output/'assets/chemistry/stage18'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((site.root/AREA/name).read_bytes())
    proof=markdown.markdown((site.root/AREA/'POLYNOMIAL_RESPONSES.md').read_text(encoding='utf-8'),extensions=['fenced_code'])
    site.page(PROOF,'Tighter chemistry response bounds from saved values','<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../../chemistry-responses.html#cr-continuous">Response explorer</a> / Local polynomial bounds</nav>'+proof+'<p><a href="../../assets/chemistry/stage18/POLYNOMIAL_RESPONSES.md">Markdown source</a> · <a href="../../assets/chemistry/stage18/SELF_REVIEW.json">Project self-review</a></p>','https://github.com/KomorebiP/Operation-KOMOREBI/blob/'+site.revision+'/'+(AREA/'POLYNOMIAL_RESPONSES.md').as_posix())
    site.search.append(dict(title='Tighter chemistry bounds from saved response values',group='Collection',kind='Written proofs',work_ids=[],url=PROOF,text='Local quadratic cubic polynomial interpolation resolvent response disks Bernstein whole interval bounds saved energies no new Hamiltonian actions'))
    return dict(data_sha256=digest,data_source='assets/chemistry/polynomial-v1.json?v='+digest[:12],core_source='assets/chemistry-polynomial-core.mjs?v='+hashlib.sha256(core.encode()).hexdigest()[:12],css_source='assets/chemistry-polynomial.css?v='+hashlib.sha256(css).hexdigest()[:12],replay_sha256=hashlib.sha256(package).hexdigest(),replay_bytes=len(package),cells=1005,new_hamiltonian_actions=0,new_endpoint_evaluations=0)

def enhance(body,meta,root):
    d=json.loads((root/DATA).read_bytes());rows=[]
    old=json.loads((root/'website/assets/chemistry/continuous-v1.json').read_bytes())
    for eta,k in [('1/10',64),('1/10',128),('1/100',512)]:
        g=next(g for g in d['groups'] if g['eta']==eta and g['order']==k);c=next(g for g in old['groups'] if g['eta']==eta and g['order']==k)
        rows.append('<tr><th scope="row">'+str(float(F(eta)))+'</th><td>'+str(k)+'</td><td>'+str(g['nodes'])+'</td><td>≈ '+f"{float(F(c['maximum_radius'])):.6g}"+'</td><td>≈ '+f"{float(F(g['maximum_radius'])):.6g}"+'</td></tr>')
    section='''<h3 id="cr-polynomial">Tighter bounds from the same observations</h3><p>Use neighboring saved values to replace each straight-line response with a local polynomial, up to cubic. The enclosing disk accounts for interpolation error and the amplified endpoint radii. The method retains the linear candidate, so its certified cell radius is never larger than the published linear bound.</p>
<div class="cr-table" tabindex="0" role="group" aria-label="Linear and polynomial bounds; scroll horizontally if needed"><table><caption>Maximum radius over the whole interval, per Hartree; identical saved data</caption><thead><tr><th scope="col">η (Ha)</th><th scope="col">H actions</th><th scope="col">Saved energies</th><th scope="col">Linear bound</th><th scope="col">Local polynomial bound</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div>
<p>At η = 0.1, 64 actions and the existing 41 energies now certify a radius below 0.001 per Hartree across the entire interval. At η = 0.01, the 512-action cache and its 166 saved energies certify a radius below 0.05. Both improvements require zero new Hamiltonian actions and zero new endpoint evaluations. These are response bounds for the declared finite model; physical approximation accuracy remains separate.</p>
<div class="cr-actions"><a href="chemistry-responses.html?cceta=1%2F10&amp;cck=64&amp;cci=205&amp;ccmethod=polynomial#cr-continuous">Inspect the tighter bound</a><a href="'''+PROOF+'''">Read the proof and scope</a><a href="assets/chemistry/stage18-replay.zip" download>Download the polynomial replay</a><a href="assets/chemistry/polynomial-v1.json">Inspect the polynomial certificates</a></div><p class="cr-small">Polynomial replay SHA-256: <code class="cr-hash">'''+meta['replay_sha256']+'''</code>. The analytic proof, exact finite tests and project self-review are distinguished in the proof note.</p>'''
    body=body.replace('<h3>From isolated samples to complete coverage</h3>',section+'<h3>Linear bounds: from samples to complete coverage</h3>')
    return '<link rel="stylesheet" href="'+meta['css_source']+'">'+body
