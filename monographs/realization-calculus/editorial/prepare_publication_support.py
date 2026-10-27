import pathlib,json,hashlib,re,shutil,datetime
from fontTools.ttLib import TTFont
R=pathlib.Path('/dev/shm/komorebi_core_monograph_fbc994080222')
E=R/'editorial'; N=R/'publication_notices';N.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
readers=json.loads((R/'reader_inventory.json').read_text())
core=json.loads((E/'core_inventory.json').read_text())
order=[p['paper'] for p in core['papers']]
source_map={re.search(r'Paper_([IVX]+)_Frozen',pathlib.Path(x['archive']).name).group(1):x for x in readers}
notice_rows=[]; inventories=[]
for roman in order:
 entry=source_map[roman]
 name=pathlib.Path(entry['archive']).stem
 base=R/'readers'/name/name
 dest=N/'per_paper'/roman
 copied=[]
 for src in sorted(base.rglob('*')):
  if not src.is_file():continue
  rel=src.relative_to(base);upper=str(rel).upper()
  if src.suffix.lower()=='.pdf':continue
  if not any(t in upper for t in ['LICENSE','NOTICE','COPYING','COPYRIGHT','THIRD_PARTY']):continue
  payload=src.read_bytes()
  try:payload.decode('utf-8')
  except UnicodeDecodeError:raise RuntimeError(f'Unexpected non-UTF8 notice: {src}')
  out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out)
  assert out.read_bytes()==payload
  row={'paper':roman,'reader_archive':pathlib.Path(entry['archive']).name,'reader_archive_sha256':entry['sha256'],'source_relative_path':rel.as_posix(),'destination':out.relative_to(R).as_posix(),'bytes':len(payload),'sha256':sha(out),'preserved_byte_for_byte':True}
  notice_rows.append(row);copied.append(row)
 inventories.append({'paper':roman,'notice_count':len(copied),'notice_bytes':sum(v['bytes'] for v in copied)})
# The edition follows the already authorized original-material split. Copy full
# grant texts from the frozen Paper I reader; do not rewrite third-party texts.
for name in ['MIT.txt','CC-BY-4.0.txt','LPPL-1.3c.txt']:
 candidates=list((N/'per_paper').rglob(name)); assert candidates,name
 src=candidates[0];out=N/'LICENSES'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out)
 notice_rows.append({'category':'shared_full_terms','source':src.relative_to(R).as_posix(),'destination':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':sha(out),'preserved_byte_for_byte':True})
rights='''Copyright 2026 Komorebi P.\n\nOriginal writing, figures and editable writing sources in this collected edition are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). Original software and machine-readable material are licensed under the MIT License. These are the original-material grants already authorized for the core series. Full license texts accompany the publication package.\n\nThird-party work remains under its own terms. The package preserves the selected frozen reader sets' license texts, font notices, PDF sidecars and attribution records byte for byte. Older original-project unassigned-license wording is historical and is superseded by the authorized grants for original material only.\n\nThe new book's display typography uses explicitly selected URW P052 and Nimbus Sans fonts. Rebuilt source pages also use their declared Latin Modern fonts. These fonts retain their separate terms, including the URW PDF embedding exception and the GUST Font License notices. The installed font files and the notice sources are identified by hashes in the accompanying inventory. Font binaries remain external build dependencies.\n\nInherited font-provenance qualifications remain in force. Current-family notice coverage does not establish the exact origin of every historical embedded font program, including name-only or Type 3 records. Missing historical source access and exact-lineage limits are retained rather than presented as newly resolved. This edition does not constitute a fresh legal or historical-font-origin audit.\n'''
(E/'rights.txt').write_text(rights);(N/'RIGHTS.txt').write_text(rights)
notice_rows.append({'category':'editorial_rights','destination':'publication_notices/RIGHTS.txt','bytes':(N/'RIGHTS.txt').stat().st_size,'sha256':sha(N/'RIGHTS.txt'),'new_original_notice':True})
fontnotice_inputs=[
 ('URW-base35-copyright.txt','/usr/share/doc/fonts-urw-base35/copyright'),
 ('Latin-Modern-GUST-FONT-LICENSE.txt','/usr/share/texmf/doc/fonts/lm/GUST-FONT-LICENSE.TXT'),
 ('Latin-Modern-README.txt','/usr/share/texmf/doc/fonts/lm/README-Latin-Modern.TXT'),
 ('Latin-Modern-Math-GUST-FONT-LICENSE.txt','/usr/share/texmf/doc/fonts/lm-math/GUST-FONT-LICENSE.txt'),
 ('Latin-Modern-Math-README.txt','/usr/share/texmf/doc/fonts/lm-math/README-Latin-Modern-Math.txt'),
 ('Latin-Modern-Math-MANIFEST.txt','/usr/share/texmf/doc/fonts/lm-math/MANIFEST-Latin-Modern-Math.txt'),
 ('Debian-fonts-lmodern-copyright.txt','/usr/share/doc/fonts-lmodern/copyright')]
for filename,origin in fontnotice_inputs:
 src=pathlib.Path(origin);assert src.is_file();out=N/'fonts_current'/filename;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,out)
 notice_rows.append({'category':'installed_font_notice','source_absolute_path':origin,'destination':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':sha(out),'preserved_byte_for_byte':True})
fontfiles=[]
for n in ['P052-Roman','P052-Bold','P052-Italic','P052-BoldItalic','NimbusSans-Regular','NimbusSans-Bold']:
 for p in [pathlib.Path('/usr/share/fonts/type1/urw-base35')/(n+'.afm'),pathlib.Path('/usr/share/fonts/X11/Type1')/(n+'.pfb')]:
  assert p.is_file();fontfiles.append({'role':'explicit outer-book font','path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'notice':'publication_notices/fonts_current/URW-base35-copyright.txt','copied_into_package':False})
for n in ['P052-Roman','P052-Bold','P052-Italic','P052-BoldItalic','NimbusSans-Regular','NimbusSans-Bold','NimbusSans-Italic','NimbusSans-BoldItalic']:
 p=pathlib.Path('/usr/share/fonts/opentype/urw-base35')/(n+'.otf');assert p.is_file()
 f=TTFont(p);names={str(k):sorted({v.toUnicode() for v in f['name'].names if v.nameID==k}) for k in [0,1,2,3,4,5,6,13,14]};f.close()
 fontfiles.append({'role':'declared rebuilt-source font','path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'name_metadata':names,'notice':'publication_notices/fonts_current/URW-base35-copyright.txt','copied_into_package':False})
for relative in ['lm/lmmono10-regular.otf','lm/lmmono10-italic.otf','lm-math/latinmodern-math.otf']:
 p=pathlib.Path('/usr/share/texmf/fonts/opentype/public')/relative;assert p.is_file()
 f=TTFont(p);names={str(k):sorted({v.toUnicode() for v in f['name'].names if v.nameID==k}) for k in [0,1,2,3,4,5,6,13,14]};f.close()
 fontfiles.append({'role':'declared rebuilt-source font','path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'name_metadata':names,'notice':'publication_notices/fonts_current/Latin-Modern-Math-GUST-FONT-LICENSE.txt' if 'lm-math' in relative else 'publication_notices/fonts_current/Latin-Modern-GUST-FONT-LICENSE.txt','copied_into_package':False})
font_provenance={'schema':'komorebi.core-monograph.current-font-notices/1','scope':'Local installed font identity and notice preservation; not a new audit of every inherited embedded program.','selection_history':{'requested_template_fonts':'TeX Gyre Pagella / TeX Gyre Heros','unavailable_checks':['kpsewhich texgyrepagella-regular.otf','kpsewhich qplr.afm','kpsewhich qplr.pfb','kpsewhich qhvr.pfb'],'resolution':'Explicit P052/Nimbus Sans selection using the paths listed below; no automatic font fallback.'},'font_files':fontfiles,'notice_records':[r for r in notice_rows if r.get('category')=='installed_font_notice']}
(N/'FONT_PROVENANCE.json').write_text(json.dumps(font_provenance,ensure_ascii=False,indent=2)+'\n')
notice_rows.append({'category':'current_font_provenance','destination':'publication_notices/FONT_PROVENANCE.json','bytes':(N/'FONT_PROVENANCE.json').stat().st_size,'sha256':sha(N/'FONT_PROVENANCE.json'),'new_inventory':True})
fullinv={'schema':'komorebi.core-monograph.source-notice-inventory/1','source':'The twelve selected frozen reader ZIPs and explicitly identified installed font notices.','policy':'Original terms and notices copied byte for byte at preserved per-reader relative paths. No PDF, scientific payload or large verification files are included in this notice tree.','original_material_grants':{'writing_figures_editable_writing':'CC-BY-4.0','software_machine_readable':'MIT','authority':'Author-confirmed open licensing and the frozen distributions, recorded in closeout register v1.16.0 / Library version 17.'},'limits':['This is notice preservation and installed-font identity checking, not new legal research.','Per-paper historical font-source access and exact-lineage limits remain in force.','Some sidecar references lead to evidence in the corresponding full frozen distribution rather than this notice-only tree.','The omitted duplicate Paper III complete reader retains its notice as part of the preserved original reader-set notices.'],'per_paper':inventories,'files':notice_rows,'all_copied_source_bytes_verified':True}
(E/'source_notice_inventory.json').write_text(json.dumps(fullinv,ensure_ascii=False,indent=2)+'\n')
# Titles and subtitles are normalized only for cover line breaks. Component
# labels are editorial navigation labels; source cover text is retained.
subtitles={
'I':'Typed operator systems, seed rank, and exact packet coordinates',
'II':'Refinement towers, weighted transfer, and integral separation of operator packets',
'III':'Typed transfer, nonlinear packets, and obstruction theory',
'IV':'Cyclic analytic functions, reciprocal families, and spectral zero data',
'V':'Exact coordinates, singular packets, and stable reconstruction',
'VI':'Probabilistic refinement, fractional operators, and exact hidden-state elimination',
'VII':'Symmetry, geometric transport, quantum channels, and bounded refinement towers',
'VIII':'Exact compilation and GPU realization',
'IX':'Completion, factorial strengthening, and sharp dyadic geometry',
'X':'Deformation forests, transport categories, and conditional system completion',
'XI':'For local Langlands',
'XII':'Conditional automorphic completion'}
role_order={'traditional':0,'machine_native':1,'analytic_supplement':1,'visual':2,'lean':3,'release_record':4,'verification_closeout':4,'research_progress':4,'research_atlas':5}
labels={'traditional':'Mathematical monograph','machine_native':'Machine-native paper','analytic_supplement':'Analytic packet jets and exact composition','visual':'Visual guide','lean':'Lean and evidence guide','release_record':'Release record','verification_closeout':'Verification closeout','research_progress':'Toward Arithmetic Packet Realization','research_atlas':'Arithmetic Packet Realization: visual atlas'}
def role(name):
 if 'Complete_Reading' in name:return 'duplicate_complete_reader'
 if 'Machine_Native' in name:return 'machine_native'
 if 'Analytic_Supplement' in name:return 'analytic_supplement'
 if 'Release_Record' in name:return 'release_record'
 if 'Verification_Closeout' in name:return 'verification_closeout'
 if 'Conjecture66_Progress' in name:return 'research_progress'
 if 'Conjecture66_Visual_Atlas' in name:return 'research_atlas'
 if 'Lean_Guide' in name:return 'lean'
 if 'Visual_Guide' in name:return 'visual'
 return 'traditional'
bookparts=[]
for roman in order:
 entry=source_map[roman];components=[];excluded=[]
 for p in entry['pdfs']:
  path=pathlib.Path(p['path']);rr=role(path.name)
  row={'filename':path.name,'source_path':str(path),'source_relative_path':path.relative_to(R/'readers').as_posix(),'source_pdf_sha256':sha(path),'source_pdf_bytes':path.stat().st_size,'source_page_count':p['pages'],'role':rr,'navigation_title':labels.get(rr,'Duplicate complete reading edition'),'source_cover_text':p['cover']}
  if rr=='duplicate_complete_reader':excluded.append(row)
  else:components.append(row)
 components.sort(key=lambda x:role_order[x['role']])
 main=next(x for x in components if x['role']=='traditional')
 corep=next(x for x in core['papers'] if x['paper']==roman)
 norm=' '.join(main['source_cover_text'].split())
 assert subtitles[roman] in norm,(roman,'subtitle mismatch')
 bookparts.append({'paper':roman,'title':corep['title'],'subtitle':subtitles[roman],'subtitle_source_pdf':main['filename'],'reader_archive':pathlib.Path(entry['archive']).name,'reader_archive_sha256':entry['sha256'],'source_component_page_total':sum(x['source_page_count'] for x in components),'components':components,'excluded_duplicate_components':excluded})
metadata={'schema':'komorebi.core-monograph.book-parts-metadata/1','source':'reader_inventory.json, bound to actual extracted frozen PDFs by current SHA-256 checks','reader_inventory_sha256':sha(R/'reader_inventory.json'),'page_count_note':'Every page count is from the selected frozen source reader, not from the new layout or current rebuild.','selection_note':'All selected components retained except Paper III duplicate complete reader. Paper I uses traditional, machine-native and Lean readers, with no separate visual reader. Paper III release record, Paper IV verification closeout and all five Paper XI components are retained. Paper X intentional atlas overlap remains intact here.','parts':bookparts}
(E/'book_parts_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
assert len(bookparts)==12
assert sum(p['source_component_page_total'] for p in bookparts)==3047
assert len([c for p in bookparts for c in p['components']])==41
print(json.dumps({'notice_files':len(notice_rows),'per_paper_notice_files':sum(x['notice_count'] for x in inventories),'notice_bytes':sum(x['notice_bytes'] for x in inventories),'parts':len(bookparts),'components':sum(len(x['components']) for x in bookparts),'source_pages':3047,'font_files_identified':len(fontfiles)}))
