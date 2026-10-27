from pathlib import Path
import json,hashlib,datetime
W=Path('/dev/shm/komorebi_paper_xi_freeze_fbc994080222');B=W/'baseline/Paper_XI_Complete_v1.1.0';A=W/'audit_licenses';D=A/'license_additions'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
meta=load(A/'EMBEDDED_FONT_METADATA.json');notice=load(A/'PREPARED_NOTICE_FILES.json');hist=load(A/'HISTORICAL_ARCHIVE_INVENTORY.json');pdfs=load(A/'PDF_FONT_INVENTORY.json')
assert not meta['candidate_lookup_errors'] and not meta['extraction_errors'] and not meta['unmatched_fonts'] and not meta['name_only_origin_limits']
assert meta['unique_resource_font_names']==32 and meta['unique_font_program_records']==237 and meta['font_program_metadata_parsed_records']==237
assert len({e['sha256'] for e in meta['embedded_fonts']})==237
metadata_controls=[]
for e in meta['embedded_fonts']:
 good=[m for m in e['installed_name_matches'] if not m['different_fields'] and len(m['equal_fields'])+len(m['equal_after_explicit_PostScript_octal_unescaping'])>=3]
 assert good,e['resource_font_name']
 metadata_controls.append({'resource_font_name':e['resource_font_name'],'font_program_sha256':e['sha256'],'candidate_exact_listed_metadata_match':True,'matching_paths':sorted({g['path'] for g in good})})
assert len(pdfs)==44 and not [p for p in pdfs if 'error' in p]
assert len(hist)==1 and len(hist[0]['pdf_members'])==173 and not [p for p in hist[0]['pdf_members'] if 'error' in p]
assert not hist[0]['standalone_font_binary_members']
assert not [p for p in B.rglob('*') if p.is_file() and p.suffix.lower() in ['.otf','.ttf','.pfb','.pfa','.woff','.woff2']]
assert len(notice)==27
for r in notice:
 p=D/r['published_path'];assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert sum(p.is_file() for p in D.rglob('*'))==36
for p in D.rglob('*'):
 if p.is_file():assert not (B/p.relative_to(D)).exists(),p.relative_to(D)
existing=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(B.rglob('*')) if p.is_file() and any(t in p.name.lower() for t in ['license','copyright','notice'])]
assert len(existing)==2
original_baseline=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(B.rglob('*')) if p.is_file()]
assert len(original_baseline)==2425
status={'audit':'Paper XI freeze original-grant and bounded font-notice audit','status':'PASS','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline':str(B),'baseline_modified':False,'baseline_project_grant_status':'No original project root license/grant or PDF sidecars existed. The author-confirmed October 20 open-license decision is expressed additively in this freeze.','grant_scope':'MIT original software/machine-readable examples/data/evidence and code listings; CC BY4.0 original writing/figures/available editable writing. Original-project historical restrictions superseded. Third-party material retains its own terms.','existing_grant_and_font_notice_files':existing,'current_readers':meta['input_readers'],'current_font_resource_name_count':32,'font_program_records':237,'font_program_records_parsed':237,'at_least_three_matching_metadata_fields_per_program':True,'installed_candidate_count':len(meta['installed_candidates']),'current_Type3_or_name_only_origin_limits':[],'font_origin_claim_boundary':'Every current program independently parsed; installed candidate name and listed metadata compared. Subsets are not asserted to be exact original whole-font/source-build byte identities.','font_families_and_terms':[{'family':'Modern URW P052 / NimbusSans','terms':'Supplied full URW notice with AGPL3 and its stated document/font exception; exact existing notice retained.'},{'family':'Older URWPalladioL / NimbusSanL and Pazo','terms':'Primary face headers preserve original copyrights, GPL wording and stated document-embedding permission. No unstated GPL version inferred; generic GPL2 file is labeled reference.'},{'family':'AMS Type1 CM/AMS/Euler','terms':'Primary headers explicitly declare SIL OFL1.1, original copyrights and reserved names; full OFL1.1 supplied.'},{'family':'Latin Modern Mono10','terms':'Current embedded header and installed primary PFB identify GUST terms; full Latin Modern terms and primary header supplied.'},{'family':'DejaVu / Arev','terms':'Existing distribution notice retained; exact Matplotlib DejaVu notice additionally supplies Tavmjong Bah/Arev permissions for the current matching metadata.'},{'family':'STIX','terms':'Exact installed STIX copyright/reserved-name/OFL1.1 notice included.'},{'family':'BaKoMa Cmsy10 TrueType','terms':'Full exact BaKoMa section from installed Matplotlib license supplied, including explicit free document embedding. Distinct from AMS CMSY10 Type1.'}],'standalone_font_binary_files':0,'historical_archive_font_binary_members':0,'all_loose_PDF_paths_parsed':44,'historical_archive_PDF_members_parsed':173,'historical_scope':'All historical PDF members and loose figure PDFs parsed for a bounded family-name inventory; no additional resource family found. Exact historical font-program/source/build origins are not certified. The Block02 source archive remains unrecovered.','prepared_addition_tree':'license_additions/','prepared_addition_files':36,'font_notice_payloads_included':25,'font_notice_payloads_already_supplied_at_baseline_paths':2,'additional_font_notice_payloads':23,'new_project_grant_texts':2,'new_current_PDF_sidecars':5,'all_addition_paths_new_and_nonoverwriting':True,'notice_provenance':'license_additions/LICENSES/FONT_NOTICE_PROVENANCE.json','published_path_resolution':'Each notice published_path/path is relative to the release root. Full-evidence audit paths explicitly refer to the full ZIP only. Smaller reader ZIP carries entire LICENSES tree, LICENSE.md/status and all five PDF sidecars.','third_party_material_boundary':'No blanket grant over external articles/books, quotations, source excerpts, references, compiler/dependency caches or fonts. Existing attributions and historical license bytes retained. No external cache or standalone font binary bundled.','required_freeze_actions':['Copy the complete contents of audit_licenses/license_additions into the full release root; every path is new.','For reader ZIP, copy LICENSE.md, LICENSE_STATUS.json and the entire LICENSES tree; keep each current PDF .license sidecar beside its PDF.','Keep existing publication/source/traditional/fonts/LICENSE_URW.txt and LICENSE_DejaVu.txt unchanged at their original paths.','Copy audit metadata and scripts under the full freeze audit location. license_additions itself need not be nested there; it is a staging tree.','Retain the recorded grant scope, no whole-font byte-provenance claim, and bounded historical source/font limitations.'],'history':[{'event':'first font metadata scan','finding':'P052-Italic installed candidate was not in the inherited candidate list; compact PostScript field syntax without whitespace was incompletely parsed.','resolution':'Enumerated current installed URW/DejaVu candidates and corrected the bounded metadata parser to accept both standard whitespace forms; all 237 programs then have at least three exact listed metadata matches. This was a harness coverage issue, not a baseline defect.'},{'event':'first additive license staging','status':'FAILED','reason':'An incorrect parent directory was used for the installed Matplotlib distribution license. It raised FileNotFoundError before touching baseline files.','resolution':'Corrected the source path and rebuilt the disposable additive staging tree; all complete grant/notice payload hashes and final paths pass.'}],'unresolved_findings':[],'evidence_files':['EMBEDDED_FONT_METADATA.json','PDF_FONT_INVENTORY.json','HISTORICAL_ARCHIVE_INVENTORY.json','PREPARED_NOTICE_FILES.json','LICENSE_ADDITION_INVENTORY.json','check_fonts.py','stage_licenses.py','finalize_audit.py']}
(A/'LICENSE_AUDIT.json').write_text(json.dumps(status,indent=2)+'\n')
inv=[{'published_path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(D.rglob('*')) if p.is_file()]
(A/'LICENSE_ADDITION_INVENTORY.json').write_text(json.dumps(inv,indent=2)+'\n')
(A/'LICENSE_AUDIT.txt').write_text('''PAPER XI FREEZE LICENSE AND FONT AUDIT | PASS | 21 October 2026

The accepted baseline has no original-project root grant or current PDF license
sidecars. Under the author's October 20 authorization, the additive staging tree
supplies MIT for original software/machine-readable material/code listings and
CC BY4.0 for original writing/figures/available editable writing. Earlier
original-project unassigned/restricted statements are superseded. Third-party
terms and source attributions remain separate and unchanged.

Copy license_additions/ contents into the release root: 36 new paths, no
baseline overwrites. This includes two full project grant texts, LICENSE.md,
LICENSE_STATUS.json, five PDF sidecars, 25 font notice payloads and their
provenance. Two font notices copy already supplied baseline notices exactly;
23 are additional current-family notice texts. The five full/current reader
PDFs and all baseline source, evidence and existing license bytes are unchanged.

All 32 current resource names / 237 distinct font-program records were parsed.
Each has an installed-name candidate with at least three matching listed
metadata fields. No current Type3/name-only record remains. This does not assert
exact whole-font/source-build byte identity for subset programs. Current faces
include modern and older URW, Pazo, AMS/Euler, Latin Modern Mono10, DejaVu/Arev,
STIX and BaKoMa Cmsy10. Existing URW/DejaVu notices are retained; the additional
Matplotlib DejaVu notice preserves Tavmjong Bah/Arev permissions. Generic GPL2
text is reference only; no unstated GPL version is assigned to old URW/Pazo.

All 44 loose PDFs and 173 historical PDF members parse. Their bounded family
inventory has no additional resource name. No standalone font binary is bundled,
including the preserved historical archive. Exact historical font origins and
missing Block02 editable source remain explicitly outside this audit.

Reader ZIP: include the whole staged LICENSES tree, LICENSE.md/status and all
five PDF sidecars. Notice inventory paths are relative to the package root and
resolve. Detailed audit-evidence references explicitly point to the full ZIP.
No external dependency cache or original third-party source is relabeled under
the original-project grants.

The first metadata pass needed wider current installed-font candidate coverage
and compact PostScript syntax handling. The first license staging failed with
FileNotFoundError from an incorrect Matplotlib license parent path; corrected,
then regenerated and verified every additive path/hash. No baseline file changed.
Unresolved findings: none within this bounded notice/inventory scope.
''')
print(json.dumps({'status':'PASS','new_files':36,'font_notices':25,'additional_font_notices':23,'current_names':32,'parsed_programs':237,'loose_pdf_paths':44,'historical_pdf_members':173,'unresolved_findings':[]}))
