"""Assemble the reader edition and preserve its technical record separately."""
from pathlib import Path
import hashlib,json,shutil,zipfile

WORK=Path(__file__).resolve().parents[1]
ROOT=WORK.parent
OUT=ROOT/'output'
VERSION='1.13.0'
ACCEPTED=OUT/'Komorebi_Space_Lean_Continuation_v1.12.0'
RUN=ACCEPTED/'wr15_v1.12.0/integration/runs/clean_wr15_01'
STAGE=WORK/'build/release_stage'
PUBLIC=STAGE/f'Komorebi_Space_Publication_v{VERSION}'
TECH=STAGE/f'Komorebi_Space_Technical_Record_v{VERSION}'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
def tree(a,b):
    for p in sorted(a.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.aux','.log','.toc','.out','.fls','.fdb_latexmk'):
            copy(p,b/p.relative_to(a))
def archive(stage):
    files=[p for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='SHA256SUMS']
    (stage/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(stage).as_posix()}\n' for p in files))
    dest=OUT/(stage.name+'.zip')
    with zipfile.ZipFile(dest,'w') as z:
        for p in sorted(stage.rglob('*')):
            if not p.is_file():continue
            info=zipfile.ZipInfo((Path(stage.name)/p.relative_to(stage)).as_posix(),date_time=(2026,10,12,0,0,0))
            info.external_attr=0o100644<<16
            info.compress_type=zipfile.ZIP_STORED if p.suffix=='.zip' else zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
        manifest=z.read(stage.name+'/SHA256SUMS').decode().splitlines()
        for line in manifest:
            digest,name=line.split('  ',1)
            assert hashlib.sha256(z.read(stage.name+'/'+name)).hexdigest()==digest,name
        assert len(manifest)+1==len(names)
    return {'file':dest.name,'sha256':sha(dest),'bytes':dest.stat().st_size,'payload_files':len(files),'crc':'PASS','manifest':'PASS','safe_paths':'PASS'}

def main():
    assert not STAGE.exists(),'Use a new staging path or remove only the reproducible release_stage directory before rebuilding.'
    PUBLIC.mkdir(parents=True);TECH.mkdir(parents=True)
    copy(WORK/'README.md',PUBLIC/'README.md')
    for folder in ('source','examples','tools'):tree(WORK/folder,PUBLIC/folder)
    production=sorted((WORK/'lean/KomorebiSpace').rglob('*.lean'))
    roots=[WORK/'lean'/n for n in ('KomorebiSpace.lean','KomorebiSpaceRegularization.lean','KomorebiSpaceCombined.lean')]
    identity=[]
    for p in production+roots:
        rel=p.relative_to(WORK/'lean');prior=ACCEPTED/'formal'/rel
        assert p.read_bytes()==prior.read_bytes(),rel
        copy(p,PUBLIC/'lean'/rel)
        identity.append({'file':str(Path('lean')/rel),'sha256':sha(p),'identical_to_accepted_source':True})
    assert len(production)==153 and len(roots)==3
    for name in ('lakefile.toml','lean-toolchain','lake-manifest.json'):copy(WORK/'lean'/name,PUBLIC/'lean'/name)
    copy(WORK/'records/drafts/lean_README.md',PUBLIC/'lean/README.md')
    copy(WORK/'records/drafts/LEAN_USAGE.md',PUBLIC/'lean/USAGE.md')
    copy(WORK/'records/drafts/LEAN_THEOREM_MAP.json',PUBLIC/'verification/LEAN_THEOREM_MAP.json')
    books=[]
    for key,stem in [('monograph','Komorebi_Space_Monograph'),('visual','Komorebi_Space_Visual_Guide'),('lean','Komorebi_Space_Lean_Guide')]:
        p=WORK/'build/final_02'/key/(stem+'.pdf');name=f'{stem}_v{VERSION}.pdf'
        copy(p,OUT/name);copy(p,PUBLIC/'books'/name)
        books.append({'file':'books/'+name,'sha256':sha(p)})
    scope={
      'edition':VERSION,'author':'Komorebi P.','date':'2026-10-12',
      'scope':'Editorial publication revision; production Lean source unchanged; no new full Lean compilation claimed.',
      'production_modules':153,'roots':3,'targets':156,'explicit_theorem_lemma_declarations':1693,'exported_declarations':5048,
      'accepted_controls':{'total':44,'positive':14,'negative':28,'policy':2},'accepted_exact_commands':238,
      'principal_analytic_theorem_groups':{'formalized':13,'printed_total':16},
      'printed_proofs_without_Lean_instances':['Infinite diagonal regularization family and tail bounds','Sharp diagonal budget asymptotic','Rounded noisy diagonal parameter rate'],
      'lean_version':'4.34.0-rc2','lean_revision':'6a10ac8c22beadecabdbb0919c2b50214762f91d',
      'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
      'permitted_axioms':['Classical.choice','Quot.sound','propext'],
      'trust_boundary':'Lean compiler/kernel and pinned compiled external dependencies; mathematical prose and finite Python examples are not all machine checked.',
      'accepted_receipt_sha256':sha(RUN/'receipt.json'),'accepted_postflight_sha256':sha(RUN/'postflight.json'),
      'books':books,'production_source_identity':identity
    }
    write_json(PUBLIC/'verification/EDITION_VERIFICATION.json',scope)
    (PUBLIC/'verification/README.md').write_text('# Verification scope\n\n`EDITION_VERIFICATION.json` records the source identity, environment, accepted proof coverage, and PDF hashes. `LEAN_THEOREM_MAP.json` gives 69 selected declarations discussed in the Lean guide. These counts distinguish explicit theorem/lemma declarations from the larger compiler export.\n\nThe publication source is byte-identical to the accepted production Lean source. Package metadata was updated to the publication version, and the dependency manifest root name was aligned with the package configuration; dependency revisions are unchanged.\n\nThe separate Technical Record contains the accepted full verification, original controls and command logs, editorial comparisons, compilation logs, visual-review coverage, example runs, and archive checks. The finite examples and visual reviews support only their recorded scopes.\n')
    public_report=archive(PUBLIC)
    # Keep original verification and its independent amendment evidence intact.
    for name in ('Komorebi_Space_Lean_Continuation_v1.12.0.zip','Komorebi_Space_Lean_Progress_v1.12.0.md','Komorebi_Space_Lean_Delivery_Verification_v1.12.0.json','Komorebi_Space_Lean_Independent_Archive_Review_v1.12.0.json','Komorebi_Space_Lean_Archive_Review_Evidence_v1.12.0.zip'):
        copy(OUT/name,TECH/'accepted_verification'/name)
    for folder in ('records','review','scripts'):tree(WORK/folder,TECH/'publication'/folder)
    for p in sorted((WORK/'build').rglob('*')):
        if not p.is_file() or 'release_stage' in p.parts or '__pycache__' in p.parts:continue
        # Preserve records/logs and small proof snapshots, not reproducible page images or duplicate PDFs.
        if p.suffix in ('.json','.log','.txt','.diff','.md','.lean'):
            copy(p,TECH/'publication/build'/p.relative_to(WORK/'build'))
    write_json(TECH/'publication/PUBLICATION_ARCHIVE_CHECK.json',public_report)
    (TECH/'README.md').write_text('# Komorebi Space — Technical Record\n\nThis companion preserves the accepted formal verification and the editorial evidence for publication edition 1.13.0. Reader-facing books, sources, and examples are in the separate Publication package.\n\n## Accepted verification\n\nThe original v1.12.0 archive and four companion records are retained byte for byte in `accepted_verification/`. They contain the exact Lean sources, verification scripts, command receipts, permitted axiom audit, controls, dependency pins, and earlier research history. The clean run had 156 compilation targets, 5,048 exported declarations, 44 controls, and 238 exact commands.\n\nThe original independent archive checker rejected an inherited source/text directory because its exclusion rule was overbroad. A separate recorded amendment retained global compiled-file exclusions while allowing the pinned historical directory names. The amended nine-gate review passed without changing the accepted archive. Both the failure and its reviewed amendment remain in the supplemental archive; the original checker is not represented as having passed.\n\n## Publication evidence\n\n`publication/records/` records the editorial contract and metadata changes. `publication/review/` contains preservation, proofreading, declaration-reference, and visual reviews. `publication/build/` retains actual commands, build results, example output, figure regeneration reports, and final artifact comparisons. `publication/scripts/` contains the coordinator’s reproducible checks. Failed or superseded build attempts are retained with their resolutions.\n\nProduction Lean sources were not changed. A strict read-only declaration inspection supplements, but does not replace or repeat, the accepted full verification. The publication is not a new whole-monograph proof audit.\n\nThe complete file inventory is in `SHA256SUMS`. The public archive hash and its completed checks are recorded in `publication/PUBLICATION_ARCHIVE_CHECK.json`.\n')
    tech_report=archive(TECH)
    write_json(WORK/'build/DELIVERY_FILES.json',{'publication':public_report,'technical_record':tech_report,'books':[{'file':Path(b['file']).name,'sha256':b['sha256']} for b in books]})
    print(json.dumps({'publication':public_report,'technical_record':tech_report,'books':books},indent=2))

if __name__=='__main__':main()
