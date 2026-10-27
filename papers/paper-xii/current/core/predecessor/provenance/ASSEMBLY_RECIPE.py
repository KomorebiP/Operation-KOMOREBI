#!/usr/bin/env python3
"""Assemble Paper XII's reviewed companions and authenticated source evidence."""
from pathlib import Path
import hashlib, json, shutil
import fitz

W = Path(__file__).resolve().parent
R = W.parent/'output/Komorebi_Paper_XII_Final_Edition_2026-10-06'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')
def copy(p, q):
    q.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, q)

assert not R.exists(), 'Assembly requires a new release directory.'
roles = [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]
docs = []
for role, part in roles:
    origin = W/role
    stem = f'Paper_XII_{part}_Final'
    for name in [stem+'.pdf', stem+'.tex', 'build.py', 'README.md']:
        assert (origin/name).is_file(), (role,name)
    dest = R/'editable'/role
    shutil.copytree(origin, dest)
    target = R/'papers'/(stem+'.pdf')
    copy(origin/(stem+'.pdf'), target)
    with fitz.open(target) as d:
        assert len(d)>0 and not d.is_encrypted
        assert all(p.get_text().strip() for p in d)
        pages = len(d)
    docs.append({'role':role,'title':part.replace('_',' '),'path':str(target.relative_to(R)),
                 'source_entry_point':str((dest/(stem+'.tex')).relative_to(R)),
                 'pages':pages,'bytes':target.stat().st_size,'sha256':sha(target)})

for folder in ['source','provenance','audit','verification']:
    def omit_transient(directory, names):
        path = Path(directory)
        omitted = []
        for n in names:
            if n == '__pycache__': omitted.append(n)
            elif folder != 'source' and (n.startswith(('isolated_bundle','isolated_original','final_build_','build_primary')) or n in {'page_renders','private_renders','acquired','.research-cache','draft_build','layout_build','page_preflight'} or ((path/n).is_dir() and 'rebuild' in n)): omitted.append(n)
            elif folder == 'provenance' and n == '.gitignore': omitted.append(n)
            elif folder == 'audit' and path == W/'audit/final_review' and (n.endswith(('.pdf','.tex')) or '_page_' in n): omitted.append(n)
        return omitted
    shutil.copytree(W/folder, R/folder, ignore=omit_transient)

# Retain exact containers used by run contracts and selected historical sidecars.
for p in sorted((W/'downloads').rglob('*')):
    if not p.is_file(): continue
    if p.name.startswith(('ADDITIONAL_DOWNLOAD_','Komorebi_Papers_II-XII_Frozen_Working_Checkpoint')): continue
    copy(p, R/p.relative_to(W))
for p in (W/'scripts').glob('*.py'): copy(p, R/'scripts'/p.name)
for name in ['README.md','RELEASE_SCOPE.md']: copy(W/name, R/name)

raw = []
for p in sorted((W/'source').rglob('*')):
    if p.is_file():
        q = R/p.relative_to(W)
        assert q.is_file() and q.stat().st_size == p.stat().st_size and sha(q) == sha(p), str(p)
        raw.append({'path':str(q.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
write(R/'provenance/RAW_SOURCE_PRESERVATION.json', {'status':'PASS','files':len(raw),
      'scope':'Every selected recovered source payload is byte-identical. Byte preservation is not proof verification.', 'payloads':raw})
write(R/'provenance/SOURCE_CONTAINER_POLICY.json', {
    'included_containers':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((R/'downloads').rglob('*.zip'))],
    'policy':'Exact outer containers required by saved-run contracts and selected XII supporting archives are retained. Nested source archives are unchanged.',
    'omitted_checkpoint':'The October 5 frozen checkpoint contained no XII payload; unrelated paper files and the retrieval container were not included.',
    'scope':'Selected current XII source branches and their supporting files, not all account history.'})

author_payloads=[]
for role,part in roles:
    for p in sorted((W/role).rglob('*')):
        if p.is_file():
            q=R/'editable'/role/p.relative_to(W/role)
            assert q.is_file() and sha(q)==sha(p),str(p)
            author_payloads.append({'path':str(q.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
write(R/'provenance/COMPANION_SOURCE_PRESERVATION.json',{'status':'PASS','files':len(author_payloads),'payloads':author_payloads,'scope':'Every file of all three frozen author packages retained byte for byte, including their own PDFs, sources, logs and manifests.'})

census = json.loads((W/'lean_guide/data/census.json').read_text())
assert (census['production_modules'],census['public_named_declarations'],census['own_public_theorems'],census['reused_public_theorems'],census['distinct_claim_targets']) == (96,1229,748,81,291)
preservation = json.loads((W/'audit/traditional/PROOF_PRESERVATION.json').read_text())
assert preservation['original_proof_environments']==preservation['final_proof_environments']==52
metadata = {
    'paper':'XII','title':'Patching Support, Hecke Packets, and Conditional Automorphic Completion','author':'Komorebi P.',
    'edition_date':'2026-10-06','edition':'Final traditional, visual and Lean companions',
    'publication_endpoint':'Proved revised structural statements and explicitly conditional automorphic completion',
    'inherited_revised_claims':{'complete':49,'partial':0,'unchecked':0},
    'inherited_original_wording_claims':{'complete':41,'partial':7,'unchecked':1},
    'original_unchecked_claim':'6.12','original_partial_claims':['9.4','9.5','9.6','10.5','12.2','12.4','12.6'],
    'inherited_amendments':census['amended_claims'],
    'final_clarifications':'editable/traditional/EDITORIAL_CHANGES.md',
    'fresh_lean_replay':False,'formal_evidence':'Authenticated inherited v0.17.1 cumulative replays and separate supplemental consumers; no fresh compilation',
    'production_modules':96,'public_named_declarations':1229,'own_public_theorems':748,'reused_paper_x_theorems':81,'distinct_claim_targets':291,
    'supplementary_consumers':{'FinalClaimsConsumer':3,'ManuscriptContractReplay':3,'included_in_production_census':False},
    'fresh_checks':{'original_finite_assertions':92892,'inherited_visual_exact_assertions':31,'independent_primitive_assertions':3216,'expanded_visual_exact_assertions':46,'visual_assertion_sets_overlap':True,'universal_proof':False},
    'original_proof_environments':52,'retained_proof_environments':52,'byte_unchanged_proof_bodies':preservation['unchanged_proof_bodies'],
    'raw_source_files':len(raw),'documents':docs,'total_pages':sum(d['pages'] for d in docs),'page_limit':None,
    'supporting_markdown_included':True,'all_figures_exact_vector':True,'ai_generated_figures':False,
    'series_scope':'Only XII finalized; completed I–XI records and content unchanged; no paper queued'}
write(R/'EDITION.json',metadata)
write(R/'COMPANION_MAP.json',{'paper':'XII','documents':docs,'current_scope':'RELEASE_SCOPE.md','markdown_index':'SUPPLEMENTARY_INDEX.md',
      'lean_catalog':'editable/lean_guide/data/source_catalog.json','declarations':'editable/lean_guide/data/declarations.json','claim_crosswalk':'editable/lean_guide/data/claim_crosswalk.json'})

previous = json.loads((W/'provenance/PREVIOUS_SERIES_STATUS.json').read_text())
status = json.loads(json.dumps(previous))
entry = next(x for x in status['papers'] if x['paper']=='XII')
entry.update(title=metadata['title'],traditional='finalized',visual_guide='finalized',lean_guide='finalized',machine_native='not_requested',
             source_refresh_before_editing=False,documents=docs,total_pages=metadata['total_pages'],
             source_branches='Authoritative revised v0.17.0 manuscript and v0.17.1 core/native formal records; original manuscript and worked visual sources',
             source_scope='49 revised internal claims complete in inherited records; original41complete/7partial/1unchecked; eight inherited amendments retained; final explicit contract clarifications separate',
             notes='Traditional, visual and Lean companions finalized with all supporting Markdown. Arithmetic completion remains conditional. Fresh finite evidence and inherited formal compilation distinguished.')
status.update(edition_date='2026-10-06',finalized_papers=12,finalized_companion_documents=36,
              run_state='closed_after_Paper_XII',active_authoring_papers=[],future_finalization_uncommitted=False,planned_companion_documents=36,
              freeze_instruction='Papers I–XI retain completed content. Paper XII finalized under revised statements and explicit arithmetic hypotheses. No next paper queued.')
assert all(a==b for a,b in zip(previous['papers'],status['papers']) if a['paper']!='XII')
write(R/'SERIES_STATUS.json',status)
copy(W/'assemble_release.py',R/'provenance/ASSEMBLY_RECIPE.py')

markdown = sorted(str(p.relative_to(R)) for p in R.rglob('*.md')) + ['SUPPLEMENTARY_INDEX.md']
(R/'SUPPLEMENTARY_INDEX.md').write_text('# Supporting Markdown files\n\nAll '+str(len(markdown))+' supporting `.md` files are included. Historical files under `source/` and `downloads/` retain their original wording and status; final scope and editorial notes identify the current contracts.\n\n'+'\n'.join('- ['+p+']('+p+')' for p in sorted(markdown))+'\n')
metadata['included_markdown_files']=len(markdown)
write(R/'EDITION.json',metadata)
print(json.dumps({'root':str(R),'documents':docs,'total_pages':metadata['total_pages'],'raw_source_files':len(raw),'markdown_files':len(markdown)},indent=2))
