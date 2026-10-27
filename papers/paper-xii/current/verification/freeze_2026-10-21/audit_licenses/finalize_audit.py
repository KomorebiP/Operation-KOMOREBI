from pathlib import Path
import json,hashlib,datetime,zipfile
W=Path('/dev/shm/komorebi_paper_xii_freeze_fbc994080222');B=W/'baseline/core';A=W/'audit_licenses';D=A/'license_additions'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p,base):return {'path':p.relative_to(base).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
meta=json.loads((A/'EMBEDDED_FONT_METADATA.json').read_text());hist=json.loads((A/'HISTORICAL_FONT_INVENTORY.json').read_text());input_pins=json.loads((A/'CURRENT_INPUT_BINDINGS.json').read_text())
for r in input_pins['bound_inputs']:
 p=B/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert meta['unique_resource_font_names']==30 and meta['unique_font_program_records']==meta['font_program_metadata_parsed_records']==63
assert not meta['extraction_errors'] and not meta['candidate_lookup_errors'] and not meta['unmatched_fonts'] and not meta['name_only_origin_limits']
for e in meta['embedded_fonts']:
 assert max(len(m['equal_fields'])+len(m['equal_after_explicit_PostScript_octal_unescaping']) for m in e['installed_name_matches'])>=3
assert not hist['archive_errors'] and hist['counts']['pdf_parse_errors']==0 and not hist['standalone_font_files']
licenses=[row(p,B) for p in sorted(B.rglob('*')) if p.is_file() and ('license' in p.name.lower() or 'copyright' in p.name.lower())]
apache=[r for r in licenses if Path(r['path']).name=='MATHLIB_LICENSE'];assert len(apache)==5 and len({r['sha256'] for r in apache})==1
project_old=[r for r in licenses if Path(r['path']).name=='LICENSE'];assert len(project_old)==5 and len({r['sha256'] for r in project_old})==1
oldtext=(B/project_old[0]['path']).read_text();assert 'No new redistribution license is assigned' in oldtext
assert sha(D/'LICENSES/third_party/MATHLIB_APACHE_2.0.txt')==apache[0]['sha256']
predecessor=json.loads((B/'evidence/block01/PREDECESSOR_AUDIT.json').read_text());excluded=predecessor['font_distribution_exclusions'];assert len(excluded)==9
inventory=json.loads((A/'LICENSE_ADDITION_INVENTORY.json').read_text());paths=[r['path'] for r in inventory['files']];assert len(paths)==len(set(paths))==40
for r in inventory['files']:
 p=D/r['path'];assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];assert not (W/'baseline'/r['path']).exists()
prov=json.loads((D/'LICENSES/FONT_NOTICE_PROVENANCE.json').read_text())
for r in prov['grants']+prov['notices']+prov['third_party']+prov['historical_notes']:
 p=D/r['published_path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
for p in (D/'LICENSES/PDF_NOTICES').iterdir():assert 'distribution root' in p.read_text()
limits=[{'area':'Subset program provenance','limit':'Installed name/metadata matches do not establish exact whole-font source/build identity.'},{'area':'Historical font origins','limit':'426 loose PDF paths and 668 ZIP PDF occurrences parse; historical resources are inventoried without exact font-origin certification.'},{'area':'Historical CM-Super','limit':'Observed 2001 SFRM1000 header and current primary CTAN metadata name generic GPL. Specific version and embedding exception are not inferred; original README/COPYING access failed.'},{'area':'Historical Yhcmex','limit':'Observed 2003 conversion header retained. Current primary CTAN metadata names LPPL1.3c, but that does not recover exact 2003 font license lineage; package-specific LICENSE access failed.'}]
source_access=[{'source':'https://ctan.org/pkg/cm-super','status':'retrieved','bounded_fact':'Current package metadata identifies GNU GPL without a specific version.'},{'source':'https://ctan.org/pkg/yhmath','status':'retrieved','bounded_fact':'Current package metadata identifies version1.6 dated2020-03-17 and LPPL1.3c.'},{'source':'https://mirrors.ctan.org/fonts/yhmath/README','status':'retrieved via CTAN link','bounded_fact':'Package README identifies Haralambous fonts/support and merged source bundles; refers to LPPL.'},{'source':'https://mirrors.ctan.org/fonts/ps-type1/cm-super/README','status':'failed','error':'Mirror redirect target inaccessible via available retrieval route.'},{'source':'https://mirrors.ctan.org/fonts/ps-type1/cm-super/COPYING','status':'failed','error':'Not accessible via available retrieval route.'},{'source':'https://raw.githubusercontent.com/TeX-Live/yhmath/master/README','status':'failed','error':'DisabledError from retrieval service.'},{'source':'https://raw.githubusercontent.com/TeX-Live/yhmath/master/README.md','status':'failed','error':'DisabledError from retrieval service.'},{'source':'https://us.mirrors.cicku.me/ctan/fonts/yhmath/LICENSE','status':'failed','error':'Not accessible via available retrieval route.'}]
(A/'SOURCE_ACCESS_HISTORY.json').write_text(json.dumps(source_access,indent=2)+'\n')
r={'audit':'Paper XII original-material license additions and bounded font/third-party preservation','status':'PASS','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_core':str(B),'baseline_modified':False,'original_root_project_grant_present':False,'existing_project_license_status':'Five exact inherited formal-release notices state no new original-manuscript license assigned; preserved unchanged and superseded only for original project material by current author grants.','existing_license_files':licenses,'grant_scope':{'original_code_machine_readable':'MIT','original_writing_figures_editable_sources':'CC-BY-4.0','code_listings_also_MIT':True,'author_authorization':'2026-10-20','original_historical_restrictions_superseded':True,'third_party_excluded_from_project_grants':True},'existing_apache_preservation':{'exact_copies':len(apache),'sha256':apache[0]['sha256'],'root_copy':'LICENSES/third_party/MATHLIB_APACHE_2.0.txt'},'current_readers':meta['input_readers'],'current_resource_font_names':30,'current_font_program_records':63,'current_programs_parsed':63,'installed_candidates':len(meta['installed_candidates']),'minimum_exact_listed_metadata_matches_per_program':3,'current_name_only_origin_limits':[],'whole_font_identity_asserted':False,'historical_inventory_counts':hist['counts'],'nine_inherited_font_exclusions':excluded,'prepared_additions':{'total_files':40,'full_original_author_license_texts':2,'current_font_notice_payloads':27,'of_which_exact_existing_full_notice_copies':2,'additional_current_font_notice_payloads':25,'historical_supplement_payloads':3,'apache_license_payloads':1,'pdf_notices':3,'staged_directory':'license_additions','path_scope':'All inventory paths are relative to frozen distribution root; core stays unchanged. Three notices under LICENSES/PDF_NOTICES may also be copied unchanged adjacent to reader PDFs.'},'historical_and_provenance_limits':limits,'source_access_history':'SOURCE_ACCESS_HISTORY.json','history':json.loads((A/'FONT_HARNESS_HISTORY.json').read_text()),'unresolved_findings':[],'not_claimed':['Exact whole-font source/build identity','Blanket historical font-origin or license-lineage certification','New ownership of third-party work','Reintroduction of nine excluded standalone fonts','PDF or scientific source edits'],'required_freeze_actions':['Copy complete license_additions contents to frozen root without changing core/.','Copy all root LICENSES and LICENSE.md/status to smaller reader ZIP.','Copy each LICENSES/PDF_NOTICES/<PDF>.license unchanged adjacent to its reader PDF.','Retain existing core and preserved delivery bytes; identify current original-project grants as superseding inherited unassigned status only for project-owned material.']}
(A/'LICENSE_AUDIT.json').write_text(json.dumps(r,indent=2)+'\n')
(A/'LICENSE_AUDIT.txt').write_text('''PAPER XII LICENSE AND FONT AUDIT | PASS | 21 October 2026

Forty additive wrapper files are staged. They include full original-author MIT
and CC BY 4.0 texts, three PDF notices, twenty-seven current font notice payloads
(two exact copies of already present full notices), three bounded historical
supplements and an exact copy of existing Mathlib Apache 2.0 terms.

Five inherited project LICENSE notices explicitly assign no new manuscript
license. Their bytes remain unchanged. The author's current grant supersedes
that original-project status only. Five Mathlib Apache license copies and all
DejaVu/Latin Modern notices retain their original hashes. Project grants do not
relicense fonts, dependencies, quotations or third-party articles.

All thirty current font names / sixty-three distinct program records parsed.
Every program has an installed name candidate and at least three exact listed
metadata matches, with explicit octal unescaping where noted. There are no
current Type3/name-only records. Metadata matches are not exact whole-font
source/build identity. The current face set needed three additional installed
candidates (URW bold italic, EUFM7 and LMMono9); the first coverage gap and its
resolution are retained as harness history, not a baseline defect.

The wider selected baseline has 426 loose PDF paths and 668 recursively retained
ZIP PDF occurrences, all parsed. Twenty-three ZIP occurrences contain no
standalone font binaries. Repeated extracted/container copies remain distinct
occurrences. The nine inherited font exclusions are preserved exactly.

Historical CM-Super and Yhcmex are not current-reader faces. Their observed
headers and primary CTAN family metadata are supplied with full LPPL reference
text and explicit lineage/access limits. Original CM-Super README/COPYING and
Yhmath package-specific LICENSE retrievals failed; no missing permission text,
GPL version, font embedding exception or old font license lineage is invented.
Current package metadata does not certify those historical embedded programs.

Copy the whole license_additions tree to the frozen wrapper root. Its forty
paths do not overwrite core/. Copy LICENSE.md/status and the complete LICENSES
tree into the smaller reader package. Copy the three LICENSES/PDF_NOTICES files
unchanged adjacent to their PDFs. Their references say distribution root and
work for both layouts. Detailed audit paths are explicitly full-ZIP-only.
No baseline, PDF, embedded-font or scientific bytes were changed. No current
extraction/candidate-match issue remains unresolved; historical limits are
listed separately in LICENSE_AUDIT.json and the family source-limit notice.
''')
print(json.dumps({'status':r['status'],'additions':40,'current_names':30,'current_programs':63,'historical_counts':hist['counts'],'unresolved_findings':[]}))
