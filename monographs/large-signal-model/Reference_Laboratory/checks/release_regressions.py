"""Release engineering checks, separate from the 756 mathematical records."""
from pathlib import Path
import ast,copy,importlib.util,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('document_gate',ROOT/'checks/audit_documents.py')
doc=importlib.util.module_from_spec(spec);spec.loader.exec_module(doc)
def main():
    rows=[]
    def check(name,truth,kind='release'):
        if not truth:raise AssertionError(name)
        rows.append({'name':name,'passed':True,'kind':kind})
    good={'pages':1,'overfull_boxes':0,'underfull_boxes':0,'undefined_reference_messages':0,
          'duplicate_destination_messages':0,'text_outside_page':[],
          'replacement_glyph_pages':[],'font_embedding_all_yes':True}
    doc.validate_quality('test',good);check('Complete document gate accepts clean record',True)
    for key,bad in [('pages',0),('overfull_boxes',1),('underfull_boxes',1),
                    ('undefined_reference_messages',1),('duplicate_destination_messages',1),
                    ('text_outside_page',[{'page':1}]),('replacement_glyph_pages',[1]),
                    ('font_embedding_all_yes',False)]:
        record=copy.deepcopy(good);record[key]=bad
        try:doc.validate_quality('test',record)
        except ValueError:check('Document gate rejects '+key,True,'expected_rejection')
        else:raise AssertionError('Accepted '+key)
    code="""import importlib.util,sys
spec=importlib.util.spec_from_file_location('g',sys.argv[1]);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
try:g.validate_quality('bad',{'pages':0})
except ValueError:print('rejected under optimization')
else:raise SystemExit(1)
"""
    proc=subprocess.run([sys.executable,'-O','-c',code,str(ROOT/'checks/audit_documents.py')],text=True,capture_output=True)
    check('Document quality failure remains rejected under python -O',proc.returncode==0 and 'rejected' in proc.stdout)
    # Reproduce the old assert-only behavior locally; this does not imply a bad PDF was shipped.
    proc=subprocess.run([sys.executable,'-O','-c','assert False; print("assert omitted")'],text=True,capture_output=True)
    check('Legacy assertion gate is omitted under optimization',proc.returncode==0 and 'omitted' in proc.stdout,'legacy_behavior')
    reference=(ROOT/'requirements-reference.txt').read_text()
    rebuild=(ROOT/'requirements-rebuild.txt').read_text()
    check('Reference dependency file names NumPy and SymPy',all(x+'==' in reference for x in ['numpy','sympy']))
    check('Rebuild dependency file includes SciPy for existing figure source','scipy==' in rebuild)
    check('Rebuild dependency file includes PyMuPDF for optional PDF audit','PyMuPDF==' in rebuild)
    figures=json.loads((ROOT/'VISUAL_ATLAS_SOURCES.json').read_text())
    import hashlib
    for entry in figures['entries']:
        p=ROOT/entry['path']
        check('Preserved figure '+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'],'asset_identity')
    # Compile every active Python module without importing or executing it.
    paths=[p for p in ROOT.rglob('*.py') if 'provenance' not in p.parts]
    for p in paths:compile(p.read_text(),str(p),'exec')
    check('All active Python sources compile',True,'source_structure')
    report={'version':'1.0.0','passed':True,'count':len(rows),'records':rows,
            'scope':'Document gates, dependency declarations, preserved figure identity and Python syntax. Not theorem verification.'}
    (ROOT/'verification/release_regression_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(rows)} release-engineering checks, separate from mathematical suites.')
if __name__=='__main__':main()
