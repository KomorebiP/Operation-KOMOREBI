"""Lexical/source audit. This is NOT a Lean proof checker."""
from pathlib import Path
import re,json,zipfile,hashlib,collections,subprocess,argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,required=True,help='Path to the extracted PRSC_IV directory')
parser.add_argument('--archive',type=Path,required=True,help='Path to the original ZIP')
parser.add_argument('--out',type=Path,required=True,help='Output directory, outside the release source')
args=parser.parse_args()
ROOT=args.root.resolve(); BASE=args.out.resolve(); LEAN=ROOT/'formalization/lean'
if not ROOT.is_dir() or not args.archive.is_file():parser.error('Root directory or archive is missing')
if BASE.is_relative_to(ROOT):parser.error('Use an output directory outside the release tree')
(BASE/'logs').mkdir(parents=True,exist_ok=True)

def scrub(s):
    # Remove nested Lean block comments, line comments and string contents,
    # preserving newlines and offsets. Apostrophes in identifiers are retained.
    a=list(s);i=0;depth=0;string=False
    while i<len(s):
        if depth:
            if s.startswith('/-',i): depth+=1;a[i:i+2]=[' ',' '];i+=2;continue
            if s.startswith('-/',i): depth-=1;a[i:i+2]=[' ',' '];i+=2;continue
            if s[i]!='\n':a[i]=' '
            i+=1;continue
        if string:
            if s[i]=='\\' and i+1<len(s):
                a[i]=' ';a[i+1]=' ' if s[i+1]!='\n' else '\n';i+=2;continue
            if s[i]=='"':string=False
            if s[i]!='\n':a[i]=' '
            i+=1;continue
        if s.startswith('/-',i):depth=1;a[i:i+2]=[' ',' '];i+=2;continue
        if s.startswith('--',i):
            j=s.find('\n',i)
            if j<0:j=len(s)
            a[i:j]=[' ']*(j-i);i=j;continue
        if s[i]=='"':string=True;a[i]=' '
        i+=1
    if depth or string:raise ValueError('Unterminated comment/string')
    return ''.join(a)

files=sorted(LEAN.rglob('*.lean')); cleaned={p:scrub(p.read_text()) for p in files}
findings=[]
for p,s in cleaned.items():
    for pat in [r'\b(?:sorry|admit|sorryAx|unsafe|opaque|native_decide|implemented_by)\b',
                r'^\s*axiom\s',r'debug\.skipKernelTC',r'\b(?:addAndCompile|addDecl|setEnv|modifyEnv|ofReduceBool|trustCompiler)\b']:
        for m in re.finditer(pat,s,re.M):
            findings.append({'file':str(p.relative_to(ROOT)),'line':s.count('\n',0,m.start())+1,'token':m.group()})
# Match explicit mapped names and kinds textually, not in Lean's environment.
pat=re.compile(r'\b(theorem|lemma|def|abbrev|instance|structure|inductive)\s+([A-Za-z_][A-Za-z0-9_\'.]*)')
decls=collections.defaultdict(list)
for p,s in cleaned.items():
    for m in pat.finditer(s):
        decls[m.group(2)].append({'kind':m.group(1),'file':str(p.relative_to(ROOT)),'line':s.count('\n',0,m.start())+1})
contract=json.loads((ROOT/'verification/lean_contract_v1.0.0.json').read_text())
targets=contract['targets'];missing=[];wrong=[]
for t in targets:
    short=t['declaration'].removeprefix('Komorebi.PaperIV.')
    found=decls.get(short,[]) or decls.get(short.rsplit('.',1)[-1],[])
    if not found:missing.append(t['declaration'])
    elif not any((x['kind'] in ['theorem','lemma'])==(t['kind']=='theorem') for x in found):wrong.append(t['declaration'])
modules={'.'.join(p.relative_to(LEAN).with_suffix('').parts):p for p in files}
graph={name:re.findall(r'^\s*import\s+(KomorebiPaperIV(?:\.[A-Za-z0-9_]+)*)',cleaned[p],re.M) for name,p in modules.items()}
missing_imports=sorted({x for imp in graph.values() for x in imp if x not in modules})
seen=set()
def visit(n):
    if n in seen:return
    seen.add(n)
    for m in graph.get(n,[]):visit(m)
visit('KomorebiPaperIV')
unimported=sorted(set(modules)-seen)
audit_src=(LEAN/'KomorebiPaperIV/KernelAudit.lean').read_text()
prints=re.findall(r'^#print axioms ([^\s]+)',audit_src,re.M)
log=(LEAN/'kernel_audit_output.txt').read_text()
log_decls=re.findall(r"^'([^']+)' (?:depends on axioms:|does not depend on any axioms)",log,re.M)
axioms=set()
for block in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',log,re.S):
    axioms.update(x.strip() for x in block.split(',') if x.strip())
records=re.findall(r'^\|\s*([0-9]+\.[0-9]+)\s*\|.*?\|\s*Full scoped statement\s*\|', (ROOT/'provenance/COMPLETION_STATUS.md').read_text(),re.M)
tex=(ROOT/'paper/paper4.tex').read_text()
result_counts=collections.Counter(re.findall(r'\\begin\{(theorem|proposition|lemma|corollary|proof|standardfact)\}',tex))
zip_path=args.archive.resolve()
manifest=(ROOT/'SHA256SUMS.txt').read_text().splitlines();hash_ok=0
for line in manifest:
    h,n=line.split('  ',1)
    if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise AssertionError(n)
    hash_ok+=1
with zipfile.ZipFile(zip_path) as z:
    crc_error=z.testzip();entries=len(z.infolist())
report={
 'audit_type':'STATIC ONLY. Recorded logs are not a fresh Lean build.',
 'zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),
 'zip_entries':entries,'zip_crc_error':crc_error,'independently_matched_sha256_entries':hash_ok,
 'lean_source_files':len(files),'lean_source_lines':sum(len(p.read_text().splitlines()) for p in files),
 'forbidden_source_findings_after_comment_string_removal':findings,
 'mapped_targets':len(targets),'mapped_target_kinds':dict(collections.Counter(t['kind'] for t in targets)),
 'mapped_target_lexical_name_misses':missing,'mapped_target_lexical_kind_mismatches':wrong,
 'local_imports_missing':missing_imports,'local_modules_reached_from_umbrella':len(seen),
 'local_modules_not_reached_from_umbrella':unimported,
 'kernel_audit_explicit_print_targets':len(prints),'kernel_audit_matches_contract':set(prints)=={t['declaration'] for t in targets},
 'recorded_log_axiom_lines':len(log_decls),'recorded_log_unique_declarations':len(set(log_decls)),
 'recorded_log_matches_audit_prints':set(log_decls)==set(prints),
 'recorded_log_axioms':sorted(axioms),'recorded_log_has_sorryAx':'sorryAx' in log,
 'recorded_log_namespace_counts':re.findall(r'PASS: (\d+) declarations \((\d+) theoremInfo\)',log),
 'source_semantic_check_theorems':len(re.findall(r'^theorem\s+',cleaned[LEAN/'KomorebiPaperIV/SemanticChecks.lean'],re.M)),
 'completion_ledger_full_results':len(records),'manuscript_environment_counts':dict(result_counts),
 'lean_runtime_present':bool(__import__('shutil').which('lean')),'lake_runtime_present':bool(__import__('shutil').which('lake')),
 'fresh_lean_verification':'NOT_RUN: this script performs lexical/source checks only',
 'fresh_pdf_rebuild':'NOT_RUN: this script does not compile LaTeX',
}
(BASE/'logs/static_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
# Citable source excerpts for a human reviewer, without claiming compiled status.
selected=['README.md','provenance/EVIDENCE_BOUNDARY.md','provenance/RUN_ENVIRONMENT.md',
'formalization/lean/KomorebiPaperIV/AnalyticReciprocalLaws.lean',
'formalization/lean/KomorebiPaperIV/NewtonDeterminant.lean',
'formalization/lean/KomorebiPaperIV/HypergeometricAnalytic.lean',
'formalization/lean/KomorebiPaperIV/HadamardIdentification.lean',
'formalization/lean/KomorebiPaperIV/DiagonalFredholm.lean']
with (BASE/'source_excerpts.txt').open('w') as f:
    for n in selected:
        f.write('\n===== '+n+' =====\n')
        for i,line in enumerate((ROOT/n).read_text().splitlines(),1):f.write(f'{i:5d} {line}\n')
