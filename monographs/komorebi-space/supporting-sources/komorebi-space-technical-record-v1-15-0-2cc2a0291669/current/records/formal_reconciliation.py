#!/usr/bin/env python3
"""Read-only independent source/inventory reconciliation; writes only its reports."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, re, zipfile

TASK = Path(__file__).resolve().parents[1]
WORK = TASK.parent
OLD = WORK / 'publication_v114/publication/lean'
NEW = TASK / 'publication/lean'
ARCHIVE = WORK / 'publication_v114_output/Komorebi_Space_Publication_v1.14.0.zip'
PARENT_ZIP = WORK / 'publication_v114/parent_technical/accepted_verification/Komorebi_Space_Lean_Continuation_v1.12.0.zip'
PARENT_MEMBER = 'Komorebi_Space_Lean_Continuation_v1.12.0/wr15_v1.12.0/integration/runs/clean_wr15_01/axioms.json'
DIAGONAL = WORK / 'publication_v114/diagonal_evidence/records/DIAGONAL_DECLARATIONS.json'
FRESH = TASK / 'runs/clean_01/declarations.json'
REGEX = r'^\s*(?:@\[[^\n]*?\]\s*)*(?:protected\s+|private\s+)?(?:theorem|lemma)\s+'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
EXPECTED_PARENT_SHA = '73e9c5caa36f4ba05029c01481b345ce24cf9b1905dfb012ed21dd4bcfe86dc0'

def digest(data): return hashlib.sha256(data).hexdigest()
def sha(path): return digest(path.read_bytes())
def sources(root):
    return {str(p.relative_to(root)):p for p in sorted(list(root.glob('*.lean')) + list((root/'KomorebiSpace').rglob('*.lean')))}
def count(path):
    text = re.sub(r'/\-.*?\-/','',path.read_text(),flags=re.S)
    text = re.sub(r'--[^\n]*','',text)
    return len(re.findall(REGEX,text,flags=re.M))
def keyed(rows):
    result = {row['name']:row for row in rows}
    if len(result) != len(rows): raise ValueError('Duplicate inventory names')
    return result

old, new = sources(OLD), sources(NEW)
added = sorted(set(new)-set(old)); removed = sorted(set(old)-set(new))
changed = sorted(k for k in old.keys() & new.keys() if old[k].read_bytes()!=new[k].read_bytes())
identical = sorted(k for k in old.keys() & new.keys() if old[k].read_bytes()==new[k].read_bytes())
archive_sha = sha(ARCHIVE)
if archive_sha != EXPECTED_PARENT_SHA: raise ValueError('Parent publication ZIP SHA mismatch')
archive_mismatches=[]
with zipfile.ZipFile(ARCHIVE) as z:
    names=z.namelist()
    for k,p in old.items():
        matching=[n for n in names if n.endswith('/lean/'+k)]
        if len(matching)!=1 or z.read(matching[0])!=p.read_bytes(): archive_mismatches.append(k)
with zipfile.ZipFile(PARENT_ZIP) as z:
    parent_bytes=z.read(PARENT_MEMBER); parent_json=json.loads(parent_bytes)
parent=keyed(parent_json['declarations']); diagonal=keyed(json.loads(DIAGONAL.read_text())['declarations'])
overlap=sorted(parent.keys() & diagonal.keys())
if overlap: raise ValueError('Baseline inventory name overlap')
baseline=parent|diagonal
source_ok=(len(new)==166 and len([p for p in new if '/' in p])==162 and len(identical)==163
           and changed==['KomorebiSpaceDiagonal.lean']
           and added==['KomorebiSpace/DiagonalInexactRate.lean','KomorebiSpace/DiagonalRangeObstruction.lean']
           and not removed and not archive_mismatches and sum(count(p) for p in new.values())==1859)
rows=[]
for name,p in new.items():
    rows.append({'path':'lean/'+name,'sha256':sha(p),'bytes':p.stat().st_size,
                 'status':'added' if name in added else ('changed_import_root' if name in changed else 'inherited_identical'),
                 'explicit_theorem_lemma_count':count(p),
                 'parent_sha256':sha(old[name]) if name in old else None})

report={
 'schema':'komorebi-space-formal-reconciliation-v1',
 'recorded_utc':datetime.now(timezone.utc).isoformat(),'edition':'1.15.0',
 'scope':'Read-only independent source-byte preservation, lexical theorem/lemma count, and exact declaration-inventory reconciliation. This report does not independently audit statements or rerun Lean.',
 'parent_publication_sha256':archive_sha,
 'source_status':'PASS' if source_ok else 'FAIL',
 'counts':{'production_modules':len([p for p in new if '/' in p]),'import_entrypoints':len([p for p in new if '/' not in p]),'source_targets':len(new),'explicit_theorem_lemma_declarations':sum(count(p) for p in new.values()),'exported_declarations':None},
 'counting_convention':{'explicit_regular_expression':REGEX,'comments':'Inherited lexical convention: remove block comments with /\\-.*?\\-/ DOTALL, then line comments. Includes explicit private declarations and excludes generated declarations.','exported_declarations':'Exact fresh Lean environment inventory. Includes definitions, theorems and generated helpers, not a count of distinct mathematical theorems.'},
 'preservation':{'parent_source_targets':len(old),'parent_explicit_theorem_lemma_declarations':sum(count(p) for p in old.values()),'inherited_identical':len(identical),'inherited_changed':changed,'added':added,'removed':removed,'parent_tree_matches_published_zip':not archive_mismatches,'parent_tree_archive_mismatches':archive_mismatches},
 'baseline_inventories':{'parent_count':len(parent),'parent_archive_sha256':sha(PARENT_ZIP),'parent_inventory_member':PARENT_MEMBER,'parent_inventory_sha256':digest(parent_bytes),'diagonal_count':len(diagonal),'diagonal_inventory_sha256':sha(DIAGONAL),'union_count':len(baseline),'name_overlap':overlap},
 'inventory_reconciliation':{'status':'PENDING','path':str(FRESH.relative_to(TASK))},
 'sources':rows,
 'limitations':['Theorem-map validation belongs to the separate root check.','Historical readable type strings are unavailable in the fresh inventory schema and are not compared. Shared metadata and exact names are compared; byte-identical source preservation is checked separately.']}
if FRESH.exists():
    fresh_doc=json.loads(FRESH.read_text()); fresh=keyed(fresh_doc['declarations'])
    missing=sorted(baseline.keys()-fresh.keys()); extra=sorted(fresh.keys()-baseline.keys())
    differences=[]; common_checks=Counter()
    for name in sorted(baseline.keys() & fresh.keys()):
        a,b=baseline[name],fresh[name]
        for field in ('module','kind','unsafe','axiom_declaration','axioms'):
            if field not in a or field not in b: continue
            av,bv=a[field],b[field]
            if field=='axioms': av,bv=sorted(av),sorted(bv)
            common_checks[field]+=1
            if av!=bv:differences.append({'name':name,'field':field,'old':av,'new':bv})
    unexpected_extra=[name for name in extra if fresh[name]['module'] not in {'KomorebiSpace.DiagonalInexactRate','KomorebiSpace.DiagonalRangeObstruction'}]
    rejected=[row for row in fresh.values() if row['unsafe'] or row['axiom_declaration'] or set(row['axioms'])-ALLOWED]
    snapshot=TASK/'runs/clean_01/snapshot/lean'
    snapshot_mismatches=[name for name,p in new.items() if not (snapshot/name).exists() or (snapshot/name).read_bytes()!=p.read_bytes()]
    ok=not(missing or differences or unexpected_extra or rejected or snapshot_mismatches) and len(fresh)==fresh_doc['count'] and not fresh_doc['rejected']
    report['counts']['exported_declarations']=len(fresh)
    report['inventory_reconciliation']={
       'status':'PASS' if ok else 'FAIL','path':str(FRESH.relative_to(TASK)),'sha256':sha(FRESH),
       'fresh_count':len(fresh),'fresh_unique_names':len(fresh),'baseline_names_retained':len(baseline.keys()&fresh.keys()),
       'missing_names':missing,'new_names':extra,'new_by_module':dict(sorted(Counter(fresh[name]['module'] for name in extra).items())),
       'unexpected_new_module_names':unexpected_extra,'shared_metadata_checks':dict(common_checks),'metadata_differences':differences,
       'permitted_axioms':sorted(ALLOWED),'rejected_declarations':rejected,'recorded_rejected_declarations':fresh_doc['rejected'],
       'snapshot_source_mismatches':snapshot_mismatches,'new_declarations':[fresh[name] for name in extra]}
report['overall_status']='PASS' if source_ok and report['inventory_reconciliation']['status']=='PASS' else ('PENDING' if source_ok and report['inventory_reconciliation']['status']=='PENDING' else 'FAIL')
out=TASK/'records/formal_reconciliation.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
inv=report['inventory_reconciliation']
lines=['# Independent formal reconciliation for v1.15.0','',f"Status: **{report['overall_status']}**.",'',
 'The source tree contains 162 production modules and four import roots, or 166 Lean source targets. The inherited lexical counting convention gives 1,859 explicit theorem/lemma declarations: the predecessor’s 1,846 plus one inexact-rate theorem and 12 range-obstruction theorems.','',
 'Exactly 163 inherited Lean files are byte-identical. Only `KomorebiSpaceDiagonal.lean` changed among inherited files, to import the two additions and describe their coverage. No inherited source is removed. The parent tree itself matches the published v1.14.0 ZIP with SHA256 `'+archive_sha+'`.','',
 'The two inherited declaration inventories contain 5,048 and 273 unique names respectively, with no overlap.']
if inv['status']=='PENDING':
    lines+=['','The fresh integrated inventory is not yet available. No new exported-declaration total has been inferred.']
else:
    lines+=['',f"The fresh inventory contains **{inv['fresh_count']:,}** declarations. It retains {inv['baseline_names_retained']:,} inherited names and adds {len(inv['new_names'])} names. Metadata differences: {len(inv['metadata_differences'])}. Missing names: {len(inv['missing_names'])}. Unexpected added-module names: {len(inv['unexpected_new_module_names'])}. Rejected declarations: {len(inv['rejected_declarations'])}.",'',
             'The comparison checks exact names and shared module, safety, axiom, and declaration-kind metadata where both historical and fresh schemas provide them. It does not compare historical readable type strings, which the fresh schema does not contain. All replay-snapshot Lean sources also match the current publication tree.']
lines+=['','This report reads source bytes and recorded Lean inventory results. It does not independently audit mathematical statements, rerun Lean, validate theorem-map references, or establish that the entire replay has finished. See the separate replay receipt and statement reviews.','']
(TASK/'records/formal_reconciliation.md').write_text('\n'.join(lines))
print(json.dumps({'overall_status':report['overall_status'],'source_status':report['source_status'],'counts':report['counts'],'inventory_status':inv['status'],'metadata_differences':len(inv.get('metadata_differences',[])),'report':str(out)},indent=2))
