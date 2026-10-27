"""Package user-facing documents and reproducible source; retain baseline ZIP."""
from pathlib import Path
import hashlib
import json
import re
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT.parent / 'Certified_Bayesian_Complete_Publication_Set.zip'
BASELINE_SHA = '844ae280ea4be7e7c25906e00733f0130996b32aa110c53951df00f8c18fa488'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def preflight():
    """Reject packaging if a final artifact is inconsistent with its review."""
    review = ROOT / 'reviews'
    build = json.loads((review / 'latex_build.json').read_text())
    pdfs = json.loads((review / 'pdf_validation.json').read_text())
    if len(build) != 3 or len(pdfs) != 3:
        raise RuntimeError('Expected three completed build and PDF review records')
    for record in build:
        if any(record[key] for key in ['overfull_boxes', 'undefined_references', 'missing_glyphs']):
            raise RuntimeError('Unresolved LaTeX defect: ' + record['name'])
    visual_records = {
        'Certified_Bayesian_Traditional_Final.pdf': 'main_visual_review.md',
        'Certified_Bayesian_Visual_Guide_Final.pdf': 'guide_visual_review.md',
        'Certified_Bayesian_Lean_Companion_Final.pdf': 'lean_visual_review.md',
    }
    if {record['file'] for record in pdfs} != set(visual_records):
        raise RuntimeError('Final PDF names differ from the declared publication set')
    for record in pdfs:
        path = ROOT / 'output' / record['file']
        if sha(path) != record['sha256']:
            raise RuntimeError('Stale rendered review: ' + record['file'])
        if any(record[key] for key in ['out_of_page_text', 'broken_internal_links', 'replacement_characters']):
            raise RuntimeError('Unresolved PDF defect: ' + record['file'])
        if record['sha256'] not in (review / visual_records[record['file']]).read_text():
            raise RuntimeError('Visual review does not identify final PDF: ' + record['file'])
    for name in ['lean_inventory.json', 'exact_example_results.json', 'figure_render_checks.json']:
        if json.loads((review / name).read_text())['status'] != 'PASS':
            raise RuntimeError('Nonpassing evidence: ' + name)
    catalogue = json.loads((review / 'figure_catalogue.json').read_text())
    if catalogue['data_sha256'] != sha(review / 'exact_example_results.json'):
        raise RuntimeError('Figure data differs from its recorded catalogue')
    if catalogue['generator_sha256'] != sha(ROOT / 'scripts' / 'bayes_figures.py'):
        raise RuntimeError('Figure generator differs from its recorded catalogue')
    figures = catalogue['figures'] if isinstance(catalogue, dict) else catalogue
    if len(figures) != 20:
        raise RuntimeError('Expected twenty final figures')
    for figure in figures:
        for extension in ['pdf', 'png']:
            if sha(ROOT / figure['paths'][extension]) != figure['sha256'][extension]:
                raise RuntimeError('Stale figure catalogue: ' + figure['stem'])
    audit = (review / 'independent_publication_audit.md').read_text()
    snapshots = re.findall(r'\| `([^`]+\.tex)` \| \d+ \| `([0-9a-f]{64})` \|', audit)
    if len(snapshots) != 8:
        raise RuntimeError('Expected eight final manuscript audit snapshots')
    for name, digest in snapshots:
        if sha(ROOT / 'manuscripts' / name) != digest:
            raise RuntimeError('Stale manuscript audit: ' + name)

def main():
    preflight()
    original = ROOT / 'inputs/FD_Certified_Inference_Core_v1.0.0_Checked.zip'
    if sha(original) != BASELINE_SHA:
        raise RuntimeError('Formal baseline archive changed')
    pdfs = list((ROOT / 'output').glob('*.pdf'))
    if len(pdfs) != 3:
        raise RuntimeError('Expected exactly three final publication PDFs')
    files = [ROOT / 'README.md', ROOT / 'requirements-publication.txt', original]
    for folder in ['manuscripts', 'figures', 'scripts', 'reviews']:
        for path in (ROOT / folder).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            if path.suffix in ['.pyc', '.lock'] or path.name == 'PACKAGE_MANIFEST.json':
                continue
            if folder == 'manuscripts' and path.suffix != '.tex':
                continue
            files.append(path)
    files.extend(pdfs)
    files.extend((ROOT / 'output').glob('*.log'))
    files.extend((ROOT / 'output').glob('*.pass*.txt'))
    files = sorted(set(files), key=lambda p: str(p.relative_to(ROOT)))
    manifest = [{'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in files]
    manifest_path = ROOT / 'PACKAGE_MANIFEST.json'
    manifest_path.write_text(json.dumps({'publication':'Certified Bayesian Inference publication edition 1.0',
                                        'baseline_sha256':BASELINE_SHA,'files':manifest},indent=2)+'\n')
    with ZipFile(DESTINATION, 'w', ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files + [manifest_path]:
            archive.write(path, 'Certified_Bayesian_Publication_1.0/' + str(path.relative_to(ROOT)))
    with ZipFile(DESTINATION) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP CRC validation failed')
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise RuntimeError('Duplicate ZIP member')
        for record in manifest:
            data = archive.read('Certified_Bayesian_Publication_1.0/' + record['path'])
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise RuntimeError('ZIP payload hash mismatch: ' + record['path'])
    report = {'archive':str(DESTINATION),'bytes':DESTINATION.stat().st_size,'sha256':sha(DESTINATION),
              'payload_files':len(files)+1,'zip_integrity':'PASS','payload_hashes':'PASS',
              'original_formal_archive_sha256':BASELINE_SHA,'fresh_lean_compilation':'NOT_RUN'}
    (ROOT.parent / 'Certified_Bayesian_Publication_Package_Verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
