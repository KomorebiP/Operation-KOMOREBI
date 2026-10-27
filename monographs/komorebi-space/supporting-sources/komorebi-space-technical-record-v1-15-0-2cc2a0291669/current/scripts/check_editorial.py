"""Check final source links, fixed edition totals, and visual section pointers."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/'publication'
BUILD=sys.argv[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
aux=ROOT/f'build/{BUILD}/monograph/Komorebi_Space_Monograph.aux'
labels={m.group(1):{'section':m.group(2),'page':m.group(3)} for m in re.finditer(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',aux.read_text())}
refpath=PUB/'source/visual_companion/monograph_references.json'
refs=json.loads(refpath.read_text())
differences={k:{'old':v,'current':labels.get(k)} for k,v in refs.items() if labels.get(k)!=v}
assert not differences, differences
(ROOT/'records/VISUAL_REFERENCES.json').write_text(json.dumps({'status':'PASS','source_aux_sha256':sha(aux),'references':len(refs),'section_or_page_changes':differences,'reference_file_sha256':sha(refpath)},indent=2)+'\n')
links=[]
for rel in ['README.md','lean/README.md','lean/USAGE.md','examples/README.md','examples/WORKED_EXAMPLE.md','verification/runner/README.md']:
    p=PUB/rel
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith('#'):continue
        dest=(p.parent/target.split('#')[0]).resolve()
        assert dest.exists(),(rel,target)
        links.append({'file':rel,'target':target,'exists':True})
source_files=list((PUB/'source').rglob('*.tex'))
stale=[]
for p in source_files:
    for i,line in enumerate(p.read_text().splitlines(),1):
        if re.search(r'v1\.14\.0|5,321|1,846|controls were not rerun|audit remains the union|records are retained separately',line):
            stale.append({'file':str(p.relative_to(PUB)),'line':i,'text':line})
assert not stale,stale
old=ROOT.parent/'publication_v114/publication/source'
preserved={}
for directory in ['figures','visual_companion']:
    for p in (old/directory).rglob('*'):
        if p.is_file():
            rel=p.relative_to(old)
            assert (PUB/'source'/rel).read_bytes()==p.read_bytes(),rel
            preserved[str(rel)]=sha(p)
record={'status':'PASS','scope':'Final source/prose/links and unchanged figure inputs; mathematical statement audits and PDF visual inspection are separate records.',
        'build':BUILD,'links':links,'stale_edition_scope_claims':stale,'unchanged_figure_and_scene_files':preserved,
        'source_hashes':{str(p.relative_to(PUB)):sha(p) for p in source_files},
        'editorial_changes':['Updated current audit scope and counts from completed replay','Named both exact formal connections','Retained printed mathematical environments and all figure/scene inputs','Added an existing-example crosswalk and citation','Retained explicit pending reuse-license choice without a new grant']}
(ROOT/'records/final_editorial_review.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':'PASS','links':len(links),'visual_references':len(refs),'unchanged_figure_scene_files':len(preserved)}))
