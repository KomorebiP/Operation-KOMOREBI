"""Package the reviewed ABC readers, preserved inputs, and execution evidence."""
from pathlib import Path
import hashlib, json, shutil, zipfile

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT.parent/'output'
PDF_OUTPUT=OUTPUT/'pdf'
PDF_OUTPUT.mkdir(parents=True,exist_ok=True)
required=['README.md','AUTHORING_REPORT.md','paper/PROOFREADING.md','visual/PROOFREADING.md','evidence/LITERATURE_CHECK.md','evidence/PROOF_AUDIT.md','evidence/COMPUTATION_AUDIT.md','evidence/FORMAL_STATUS.md','evidence/REVIEW_PINS.json','evidence/SOURCE_VALIDATION.json','evidence/LAYOUT_VALIDATION.json','pdf/Komorebi_ABC_Conjecture_Piece_v1.0.pdf','pdf/Komorebi_ABC_Visual_Guide_v1.0.pdf']
for name in required:assert (ROOT/name).is_file(),name
for name in ['SOURCE_VALIDATION.json','LAYOUT_VALIDATION.json']:
 assert json.loads((ROOT/'evidence'/name).read_text())['status']=='passed',name

def include(path):
 rel=path.relative_to(ROOT)
 if rel.parts[:2]==('evidence','literature'):return False
 if '__pycache__' in rel.parts or rel==Path('MANIFEST.json'):return False
 if '.openai-download-' in path.name:return False
 if path.suffix in {'.pyc','.aux','.toc','.out'}:return False
 if path.suffix in {'.tar','.zst','.so'}:return False
 if path.suffix=='.pdf' and any(rel.parts[i:i+2]==('sources','iut') for i in range(len(rel.parts)-1)):return False
 if len(rel.parts)==2 and rel.parts[0] in {'paper','visual'} and path.name in {'main.pdf','main.log','build_stdout.log'}:return False
 return True

files=sorted(p for p in ROOT.rglob('*') if p.is_file() and include(p))
assert all(p.stat().st_size<40*1024*1024 for p in files),'A runtime or unexpected large cache entered the release.'
entries=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest=ROOT/'MANIFEST.json'
manifest.write_text(json.dumps({'edition':'1.0','date':'2026-10-08','author':'Komorebi P.','self_excluded':'MANIFEST.json','scope':'ABC readers, exact figure generator/data, preserved user-authored archives, selected historical formal payloads, and fresh mathematical/computational/formal/layout evidence. External full papers and compiler runtimes excluded.','files':entries},indent=2)+'\n')
archive=OUTPUT/'Komorebi_ABC_Source_and_Evidence_v1.0.zip'
prefix='Komorebi_ABC_v1.0/'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[manifest]:z.write(p,prefix+str(p.relative_to(ROOT)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for e in entries:assert hashlib.sha256(z.read(prefix+e['path'])).hexdigest()==e['sha256'],e['path']
for p in sorted((ROOT/'pdf').glob('*.pdf')):
 target=PDF_OUTPUT/p.name;shutil.copyfile(p,target);print(target)
print(archive)
print(f'Verified {len(entries)} payload files plus manifest, SHA-256 and ZIP CRC.')
