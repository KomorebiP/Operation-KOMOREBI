from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,struct
import matplotlib
W=Path('/dev/shm/komorebi_paper_xii_freeze_fbc994080222');B=W/'baseline/core';A=W/'audit_licenses';D=A/'license_additions'
OLD=Path('/dev/shm/komorebi_paper_x_freeze_fbc994080222/audit_licenses');XI=Path('/dev/shm/komorebi_paper_xi_freeze_fbc994080222/audit_licenses/license_additions')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def h(b):return hashlib.sha256(b).hexdigest()
def put(rel,data):
 p=D/rel;assert not (W/'baseline'/rel).exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes) else data.encode());return p
if D.exists():shutil.rmtree(D)
D.mkdir();grants=[];provenance=[]
# Authenticate cached complete author-grant payloads against the already saved
# Paper XI manifest, without importing that paper's scope or font claims.
zpath=Path('/workspace/scratch/fbc994080222/paper_viii_freeze/output/Paper_XI_Frozen_Release_2026-10-21.zip')
assert sha(zpath)=='e569e174acd49dd527918b49758b386c241c5aacfe5866e96757b0fb4c573b9a'
with zipfile.ZipFile(zpath) as z:
 root='Paper_XI_Frozen_Release_2026-10-21/';pins={r['path']:r for r in json.loads(z.read(root+'MANIFEST.json'))['files']}
 for rel in ['LICENSES/MIT.txt','LICENSES/CC-BY-4.0.txt']:
  data=z.read(root+rel);assert len(data)==pins[rel]['bytes'] and h(data)==pins[rel]['sha256'];put(rel,data);grants.append({'published_path':rel,'bytes':len(data),'sha256':h(data),'source_archive':zpath.name,'source_archive_sha256':sha(zpath),'source_member':root+rel,'source_manifest_pin_verified':True,'scope':'Exact full original-author license text; same author and year. Not third-party font licensing.'})
for src,rel in [('publication/source/lean_guide/fonts/DEJAVU_LICENSE.txt','LICENSES/fonts/DEJAVU-FONT-LICENSE.txt'),('publication/source/lean_guide/fonts/LM_LICENSE.txt','LICENSES/fonts/LATIN-MODERN-FONT-LICENSE.txt')]:
 data=(B/src).read_bytes();p=put(rel,data);provenance.append({'published_path':rel,'path':rel,'bytes':len(data),'sha256':h(data),'source_baseline_path':'core/'+src,'source_sha256':sha(B/src),'copy':'Exact existing full notice; original remains byte-identical.'})
M=Path(matplotlib.get_data_path())/'fonts/ttf'
for src,rel in [(Path('/usr/share/doc/fonts-urw-base35/copyright'),'LICENSES/fonts/URW-FONT-LICENSE.txt'),(M/'LICENSE_STIX','LICENSES/fonts/STIX-FONT-LICENSE.txt'),(M/'LICENSE_DEJAVU','LICENSES/fonts/DEJAVU-MATPLOTLIB-FONT-LICENSE.txt')]:
 data=src.read_bytes();put(rel,data);provenance.append({'published_path':rel,'path':rel,'bytes':len(data),'sha256':h(data),'source':str(src),'source_sha256':sha(src),'copy':'Exact installed full family notice; current embedded metadata comparison is separate.'})
selected=['OLD_URW-uplr8a-FONT-NOTICE.txt','OLD_URW-uplb8a-FONT-NOTICE.txt','OLD_URW-uplri8a-FONT-NOTICE.txt','OLD_URW-uhvr8a-FONT-NOTICE.txt','OLD_URW-uhvb8a-FONT-NOTICE.txt','OLD_URW-uhvro8a-FONT-NOTICE.txt','PAZO-fplmr-FONT-NOTICE.txt','PAZO-fplmri-FONT-NOTICE.txt','PAZO-fplmbb-FONT-NOTICE.txt','AMS-cmr10-FONT-NOTICE.txt','AMS-cmmi10-FONT-NOTICE.txt','AMS-cmsy10-FONT-NOTICE.txt','AMS-cmex10-FONT-NOTICE.txt','AMS-msbm10-FONT-NOTICE.txt','AMS-eufm10-FONT-NOTICE.txt','GPL-2.txt','SIL-OFL-1.1.txt']
cache={Path(r['path']).name:r for r in json.loads((OLD/'PREPARED_NOTICE_FILES.json').read_text())}
for name in selected:
 r=cache[name];src=Path(r['source']);p0=OLD/'notices'/name;assert sha(p0)==r['sha256'];assert sha(src)==r['source_sha256']
 rel='LICENSES/fonts/freeze_2026-10-21/'+name;put(rel,p0.read_bytes());provenance.append({**r,'published_path':rel,'path':rel,'cached_payload_sha256_reverified':sha(p0),'primary_source_sha256_reverified':sha(src),'scope':r['scope']})
newfaces=[(Path('/usr/share/texlive/texmf-dist/fonts/type1/urw/palatino/uplbi8a.pfb'),'OLD_URW-uplbi8a-FONT-NOTICE.txt'),(Path('/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/euler/eufm7.pfb'),'AMS-eufm7-FONT-NOTICE.txt'),(Path('/usr/share/texmf/fonts/type1/public/lm/lmtt9.pfb'),'LATINMODERN-lmtt9-FONT-NOTICE.txt'),(Path('/usr/share/texmf/fonts/type1/public/lm/lmtt10.pfb'),'LATINMODERN-lmtt10-FONT-NOTICE.txt'),(Path('/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/symbols/msam10.pfb'),'AMS-msam10-FONT-NOTICE.txt')]
for src,name in newfaces:
 raw=src.read_bytes();assert raw[:2]==b'\x80\x01';n=struct.unpack('<I',raw[2:6])[0];clear=raw[6:6+n];end=clear.index(b'end readonly def')+len(b'end readonly def');data=clear[:end]+b'\n';rel='LICENSES/fonts/freeze_2026-10-21/'+name;put(rel,data);provenance.append({'published_path':rel,'path':rel,'bytes':len(data),'sha256':h(data),'source':str(src),'source_sha256':sha(src),'copy':'Exact first plaintext PFB prefix through FontInfo end readonly def, plus newline; no glyph or encrypted font program.','scope':'Current face-specific original copyright and license/embedding header.'})
apache='publication/source/lean_guide/formal_release/MATHLIB_LICENSE';data=(B/apache).read_bytes();put('LICENSES/third_party/MATHLIB_APACHE_2.0.txt',data)
thirdparty=[{'published_path':'LICENSES/third_party/MATHLIB_APACHE_2.0.txt','bytes':len(data),'sha256':h(data),'source_baseline_path':'core/'+apache,'source_sha256':sha(B/apache),'copy':'Exact existing Mathlib Apache 2.0 terms; original retained.'}]
put('LICENSE.md','''# Paper XII open license

Copyright (c) 2026 Komorebi P.

The author confirmed open licensing for all papers on 20 October 2026. This
21 October distribution supplies the complete grants for original Operation
Komorebi material in Paper XII, accepted reading release 1.0.0 of 10 October.

Original Lean and Python code, build and verification scripts, configurations,
machine-readable examples, datasets, correspondence maps and release evidence
use the MIT License. Full terms: LICENSES/MIT.txt. Original project code in
historical snapshots and nested project archives is included. Code listings
reproduced in the paper and guides may also be used under MIT.

Original manuscripts, traditional paper, visual guide, Lean guide, figures and
explanatory writing, including their available editable sources, use Creative
Commons Attribution 4.0 International. Full terms: LICENSES/CC-BY-4.0.txt and
https://creativecommons.org/licenses/by/4.0/.

Attribute the work to Komorebi P., retain the title and license notice, include
the license link and indicate adaptations. Suggested attribution:
Komorebi P., Patching Support and Hecke Packets, Paper XII, reading release
1.0.0 (10 October 2026), frozen distribution 21 October 2026. CC BY 4.0.

When sharing a reader PDF alone, include its adjacent .license notice or
reproduce that notice with the distribution. Notices for the three current
PDFs are also supplied under LICENSES/PDF_NOTICES/.

Third-party work retains its own copyright and license terms. The original
project grants do not relicense third-party articles, quotations, excerpts,
source materials, dependencies or fonts. Existing Mathlib Apache 2.0 terms
are retained unchanged and exposed under LICENSES/third_party/. Font notices
and primary embedding language retain their separate terms. See
LICENSES/THIRD_PARTY_NOTICES.txt. External toolchains, dependency caches and
standalone font binaries remain reproduction prerequisites under their terms.

Historical statements that no project license was selected, including the
unchanged formal_release/LICENSE files, describe the earlier release state.
For original project material included here, this grant supersedes those
restrictions. It does not supersede Mathlib or other third-party terms.
All accepted source, historical archives and PDFs retain their original bytes.
No excluded font binary is silently reintroduced. Missing or external input
is not licensed as if supplied.

The revised conditional theorem and its quantifiers remain unchanged.
A license grant does not construct residual or deformation data, patching
hypotheses, Hecke points, attached representations or compatible families.

The applicable license texts contain their warranty disclaimers. No additional
fee, institutional affiliation or project permission is required by these grants.
''')
status={'release':'Paper XII accepted reading 1.0.0; distribution freeze 2026-10-21','author_authorization_date':'2026-10-20','notice_date':'2026-10-21','original_code_machine_data_evidence':'MIT','original_writing_figures_editable_sources':'CC-BY-4.0','code_listings_also_MIT':True,'third_party_terms_retained':True,'source_notice':'LICENSE.md','third_party_notice':'LICENSES/THIRD_PARTY_NOTICES.txt','historical_original_project_restrictions_superseded':True,'baseline_core_bytes_changed':False,'pdf_bytes_changed':False,'nine_original_font_exclusions_retained':True,'current_pdf_notices':'LICENSES/PDF_NOTICES/'}
put('LICENSE_STATUS.json',json.dumps(status,indent=2)+'\n')
put('LICENSES/THIRD_PARTY_NOTICES.txt','''PAPER XII THIRD-PARTY AND FONT NOTICES | 21 October 2026

Original project grants are in ../LICENSE.md. They do not relicense third-party
work. Existing copyright/source attributions remain at their original paths,
including in core/ and the unchanged preserved delivery archives. References,
selected source reviews, quotations and excerpts retain their named authors
and source-specific scope. No blanket rights to external papers are asserted.

Mathlib Apache 2.0 terms are copied exactly to third_party/MATHLIB_APACHE_2.0.txt.
Their original MATHLIB_LICENSE copies remain unchanged in core/. The old
formal_release/LICENSE files say no new original-manuscript license was assigned;
that historical original-project status is superseded by the author's current
MIT / CC BY 4.0 grants. Apache 2.0 and other third-party terms are unaffected.
External Lean, Mathlib dependency caches, TeX packages and installed font binaries
remain reproduction prerequisites under their own terms.

Current-reader font notices are under fonts/:
- URW-FONT-LICENSE.txt: complete installed modern URW distribution notice,
  including its applicable terms and document/font exception.
- DEJAVU-FONT-LICENSE.txt: exact existing DejaVu/Bitstream distribution notice.
- DEJAVU-MATPLOTLIB-FONT-LICENSE.txt: installed DejaVu notice including the
  Tavmjong Bah/Arev permission found in matching current subset metadata.
- LATIN-MODERN-FONT-LICENSE.txt: exact existing Latin Modern full terms.
- STIX-FONT-LICENSE.txt: installed STIX copyright, reserved names and SIL OFL1.1.
- freeze_2026-10-21/: older URW/Pazo, AMS and Latin Modern primary face headers,
  exact SIL OFL1.1 text and generic GPL2 reference text.

Older URW/Pazo headers retain their own GPL and document-embedding language.
No unstated GPL version is inferred from generic GPL-2.txt. Modern URW, older
URW and original-project licenses remain separate. AMS headers expressly name
SIL OFL1.1 and reserved names. Latin Modern primary headers retain GUST terms.
DejaVu/Latin Modern notice sections about Debian packaging do not assign that
packaging license to every embedded font or original project file.

The three current readers contain 30 resource names and 63 distinct font-program
records. All programs were parsed and compared independently against installed
name/metadata candidates, with at least three exact listed metadata fields.
Subset metadata does not establish exact whole-font source/build identity.
There are no current Type3/name-only program records. Historical PDF/font
resource inventories are separate and are not blanket origin certification.
The inherited nine standalone font exclusions remain explicit; external fonts
must be obtained under their own terms for reproduction.

FONT_NOTICE_PROVENANCE.json lists published notice paths relative to the
distribution root and their exact payload and source hashes. Detailed audits
are in the full ZIP under verification/freeze_2026-10-21/audit_licenses/;
those full-evidence paths are not promised inside the smaller reader ZIP.
Complete notices accompany both ZIPs. No PDF or embedded-font bytes changed.
''')
put('LICENSES/FONT_NOTICE_PROVENANCE.json',json.dumps({'scope':'Current reader font-notice payload identities and bounded sources; published_path/path are relative to the distribution root. Metadata comparisons are not whole-font identity.','grants':grants,'notices':provenance,'third_party':thirdparty},indent=2)+'\n')
notice='''Paper XII | Komorebi P. | Original writing, figures and editable writing:
Creative Commons Attribution 4.0 International (CC BY 4.0).
https://creativecommons.org/licenses/by/4.0/
Original code listings may also be used under MIT.
Attribute Komorebi P., preserve title and license notice, link the license and
indicate adaptations. Full grants are at the distribution root: LICENSE.md and
LICENSES/. Third-party fonts, references and excerpts retain their own terms.
This notice does not relicense them. Retained original-project unassigned-license
statements are superseded by the author's current grants; third-party terms
remain unchanged. Keep this notice when distributing the PDF alone.
Reading release 1.0.0, 10 October 2026; distribution frozen 21 October 2026.
Licensing does not change the paper's conditional theorem or supply its inputs.
'''
for p in sorted((B/'publication/pdfs').glob('*.pdf')):put('LICENSES/PDF_NOTICES/'+p.name+'.license',notice)
(A/'PREPARED_NOTICE_FILES.json').write_text(json.dumps(provenance,indent=2)+'\n')
files=[{'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(D.rglob('*')) if p.is_file()]
(A/'LICENSE_ADDITION_INVENTORY.json').write_text(json.dumps({'scope':'All additive paths are relative to frozen distribution root. Core is unchanged. PDF notice copies may also be placed adjacent to readers with identical bytes.','files':files},indent=2)+'\n')
print(json.dumps({'staged_files':len(files),'font_notice_payloads':len(provenance),'grant_payloads':len(grants),'third_party_payloads':len(thirdparty),'pdf_sidecars':3,'paths_nonoverwriting_core':True}))
