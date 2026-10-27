from pathlib import Path
import json,hashlib,zipfile,shutil,datetime,struct
import matplotlib
W=Path('/dev/shm/komorebi_paper_xi_freeze_fbc994080222');B=W/'baseline/Paper_XI_Complete_v1.1.0';A=W/'audit_licenses';D=A/'license_additions'
OLD=Path('/dev/shm/komorebi_paper_x_freeze_fbc994080222/audit_licenses')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def h(b):return hashlib.sha256(b).hexdigest()
def put(rel,data):
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes) else data.encode());return p
if D.exists():shutil.rmtree(D)
D.mkdir()
provenance=[]
# Reuse full original-author grant texts and a Latin Modern full notice from the
# authenticated, already frozen preceding paper. Bind member hashes to its strict manifest.
zpath=Path('/workspace/scratch/fbc994080222/paper_viii_freeze/output/Paper_X_Frozen_Release_2026-10-21.zip')
with zipfile.ZipFile(zpath) as z:
 root='Paper_X_Frozen_Release_2026-10-21/'
 pins={r['path']:r for r in json.loads(z.read(root+'MANIFEST_SHA256.json'))['files']}
 for src,rel in [('LICENSES/MIT.txt','LICENSES/MIT.txt'),('LICENSES/CC-BY-4.0.txt','LICENSES/CC-BY-4.0.txt'),('LICENSES/fonts/LATIN-MODERN-FONT-LICENSE.txt','LICENSES/fonts/LATIN-MODERN-FONT-LICENSE.txt')]:
  data=z.read(root+src);assert h(data)==pins[src]['sha256'] and len(data)==pins[src]['bytes']
  p=put(rel,data);provenance.append({'published_path':rel,'bytes':len(data),'sha256':h(data),'source_archive':str(zpath),'source_member':root+src,'source_manifest_pin_verified':True,'scope':'Exact full license text; original author and year same for MIT. Third-party font terms retained without relicensing.'})
# Preserve supplied URW and DejaVu notices exactly, also expose them beside readers.
for src,rel in [('publication/source/traditional/fonts/LICENSE_URW.txt','LICENSES/fonts/URW-FONT-LICENSE.txt'),('publication/source/traditional/fonts/LICENSE_DejaVu.txt','LICENSES/fonts/DEJAVU-FONT-LICENSE.txt')]:
 p=put(rel,(B/src).read_bytes());provenance.append({'published_path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'source_baseline_path':src,'source_sha256':sha(B/src),'copy':'exact baseline full notice'})
M=Path(matplotlib.get_data_path())/'fonts/ttf'
for src,rel in [(M/'LICENSE_STIX','LICENSES/fonts/STIX-FONT-LICENSE.txt'),(M/'LICENSE_DEJAVU','LICENSES/fonts/DEJAVU-MATPLOTLIB-FONT-LICENSE.txt')]:
 p=put(rel,src.read_bytes());provenance.append({'published_path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'source':str(src),'source_sha256':sha(src),'copy':'exact installed Matplotlib family license notice; STIX includes full SIL OFL1.1 and DejaVu includes Bitstream/Arev permissions'})
# Vendor-maintained full BaKoMa license section as distributed with the actual
# installed Matplotlib family. The exact slice boundaries remain explicit.
dist=M.parents[3]/'matplotlib-3.10.8.dist-info/LICENSE'
raw=dist.read_bytes();start=raw.index(b'Name: BaKoMa Fonts\n');end=raw.index(b'Name: ColorBrewer Color Schemes\n',start);section=raw[start:end]
p=put('LICENSES/fonts/BAKOMA-FONT-LICENSE.txt',section);provenance.append({'published_path':p.relative_to(D).as_posix(),'bytes':len(section),'sha256':h(section),'source':str(dist),'source_sha256':sha(dist),'copy':'exact complete BaKoMa section from installed Matplotlib license, from its Name heading to before ColorBrewer heading','scope':'Current Cmsy10.ttf, distinct from AMS CMSY10 Type1'})
selected=['OLD_URW-uplr8a-FONT-NOTICE.txt','OLD_URW-uplb8a-FONT-NOTICE.txt','OLD_URW-uplri8a-FONT-NOTICE.txt','OLD_URW-uhvr8a-FONT-NOTICE.txt','OLD_URW-uhvb8a-FONT-NOTICE.txt','OLD_URW-uhvro8a-FONT-NOTICE.txt','PAZO-fplmr-FONT-NOTICE.txt','PAZO-fplmri-FONT-NOTICE.txt','PAZO-fplmbb-FONT-NOTICE.txt','AMS-cmr10-FONT-NOTICE.txt','AMS-cmmi10-FONT-NOTICE.txt','AMS-cmsy10-FONT-NOTICE.txt','AMS-cmex10-FONT-NOTICE.txt','AMS-msbm10-FONT-NOTICE.txt','AMS-eufm10-FONT-NOTICE.txt','GPL-2.txt','SIL-OFL-1.1.txt']
cache={Path(r['path']).name:r for r in json.loads((OLD/'PREPARED_NOTICE_FILES.json').read_text())}
for name in selected:
 r=cache[name];src=Path(r['source']);p0=OLD/'notices'/name
 assert sha(p0)==r['sha256']
 if src.is_file():assert sha(src)==r['source_sha256']
 rel='LICENSES/fonts/freeze_2026-10-21/'+name;p=put(rel,p0.read_bytes());provenance.append({**r,'published_path':rel,'path':rel,'cache_path':str(p0),'cache_sha256_reverified':sha(p0),'source_sha256_reverified':sha(src) if src.is_file() else None,'scope':r['scope']})
for src,name in [(Path('/usr/share/texmf/fonts/type1/public/lm/lmtt10.pfb'),'LATINMODERN-lmtt10-FONT-NOTICE.txt'),(Path('/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/symbols/msam10.pfb'),'AMS-msam10-FONT-NOTICE.txt')]:
 raw=src.read_bytes();assert raw[:2]==b'\x80\x01';n=struct.unpack('<I',raw[2:6])[0];clear=raw[6:6+n];end=clear.index(b'end readonly def')+len(b'end readonly def');data=clear[:end]+b'\n'
 rel='LICENSES/fonts/freeze_2026-10-21/'+name;p=put(rel,data);provenance.append({'published_path':rel,'bytes':len(data),'sha256':h(data),'source':str(src),'source_sha256':sha(src),'copy':'exact first plaintext PFB segment prefix through FontInfo end readonly def, plus newline; no glyph programs or standalone font binaries','scope':'Current face-specific original copyright/license header'})
put('LICENSE.md','''# Paper XI open license

Copyright (c) 2026 Komorebi P.

The author confirmed open licensing for all papers on 20 October 2026. This
21 October distribution supplies the complete grants for original Operation
Komorebi material in Paper XI, accepted publication release 1.1.0 of 18 October.

Original Lean and Python code, build and verification scripts, configuration,
machine-readable examples, datasets, correspondence maps and release evidence
use the MIT License. Full terms: LICENSES/MIT.txt. Original project code in
historical snapshots and nested project archives is included. Code listings
reproduced in the papers and guides may also be used under MIT.

Original manuscripts, traditional paper, core visual guide, Lean guide,
Conjecture 66 research paper and atlas, figures and explanatory writing,
including their available editable sources, use Creative Commons Attribution
4.0 International. Full terms: LICENSES/CC-BY-4.0.txt and
https://creativecommons.org/licenses/by/4.0/.

Attribute the work to Komorebi P., retain the title and license notice, include
the license link and indicate adaptations. Suggested attribution:
Komorebi P., Tame and Wild Packet Geometry for Local Langlands, Paper XI,
publication release 1.1.0 (18 October 2026), frozen distribution 21 October 2026.
CC BY 4.0.

When sharing a reader PDF alone, include its adjacent .license notice or
reproduce that notice with the distribution.

Third-party work retains its own copyright and license terms. The original
project grants do not relicense third-party articles, quotations, excerpts,
source materials, dependencies or fonts. Embedded fonts retain applicable
notices and embedding terms. See LICENSES/THIRD_PARTY_NOTICES.txt. External
compiler/dependency caches and standalone font binaries are not supplied.

Historical statements that no project license was selected, and earlier
original-project all-rights-reserved notices, describe the earlier release
state. For original project material included here, this grant supersedes those
restrictions. Third-party terms and unmodified license texts remain unaffected.
No missing editable source or unavailable historical record is invented or
licensed as if recovered. Conjecture 66 and the stated open obligations remain
open; a license grant is not a mathematical completion claim.

The applicable license texts contain the warranty disclaimers. No additional
fee, institutional affiliation or project permission is required by these grants.
''')
status={'release':'Paper XI accepted 1.1.0; distribution freeze 2026-10-21','author_authorization_date':'2026-10-20','notice_date':'2026-10-21','original_code_machine_data_evidence':'MIT','original_writing_figures_editable_sources':'CC-BY-4.0','code_listings_also_MIT':True,'third_party_terms_retained':True,'source_notice':'LICENSE.md','third_party_notice':'LICENSES/THIRD_PARTY_NOTICES.txt','historical_original_project_restrictions_superseded':True,'unrecovered_sources_not_reconstructed':True}
put('LICENSE_STATUS.json',json.dumps(status,indent=2)+'\n')
put('LICENSES/THIRD_PARTY_NOTICES.txt','''PAPER XI THIRD-PARTY AND FONT NOTICES | 21 October 2026

Original project grants are in ../LICENSE.md. They do not relicense third-party
work. Existing copyright/source attributions remain at their original paths,
including inside the preserved historical archive. References, selected source
reviews and quotations retain their named authors and source-specific scope.
The project grants do not assert blanket rights to external articles or books.

External Lean, Mathlib, dependencies, TeX engines/packages and installed font
binaries remain reproduction prerequisites under their own terms. No external
compiler/dependency cache or standalone font binary is included in this package.

Current-reader font notices are provided under fonts/:
- URW-FONT-LICENSE.txt: supplied full modern URW notice, AGPL3 and its stated
  document/font exception. Original baseline notice remains unchanged.
- DEJAVU-FONT-LICENSE.txt: supplied Bitstream/DejaVu distribution notice.
- DEJAVU-MATPLOTLIB-FONT-LICENSE.txt: Matplotlib-distributed DejaVu notice,
  including Tavmjong Bah/Arev permission for current matching subset metadata.
- LATIN-MODERN-FONT-LICENSE.txt: GUST/LPPL-based Latin Modern full terms.
- STIX-FONT-LICENSE.txt: installed STIX copyright/reserved names and SIL OFL1.1.
- BAKOMA-FONT-LICENSE.txt: installed Matplotlib BaKoMa-CM/AMS permission notice;
  the current Cmsy10 TrueType face is distinct from AMS CMSY10 Type1.
- freeze_2026-10-21/: primary older URW/Pazo/AMS/Latin Modern face headers,
  exact SIL OFL1.1 text and generic GPL2 text as historical reference.

Older URW/Pazo headers state their own GPL and document-embedding language.
A specific unstated GPL version is not inferred from the supplied generic
GPL-2.txt reference. Modern URW, older URW and original project licensing are
separate. AMS headers expressly declare SIL OFL1.1, including their reserved
font names. Latin Modern primary headers declare GUST terms.

The current five-reader inventory contains 32 resource names and 237 distinct
font-program records. Every program was parsed and compared independently with
installed name/metadata candidates. No exact whole-font source/build identity
is asserted for subset programs. The current readers have no Type3/name-only
program record. Historical figure/font origins retain a separately bounded
inventory; this is not a blanket historical font-origin certification.

FONT_NOTICE_PROVENANCE.json resolves each notice path relative to the release
root, with exact payload hashes and recorded primary/cached source identities.
Detailed current embedded metadata and historical inventory are in the full
ZIP under verification/freeze_2026-10-21/audit_licenses/. Those full-evidence paths
are not promised inside the smaller reader ZIP. This notice and the complete
font notices accompany both distributions. No PDF or embedded-font byte changed.
''')
put('LICENSES/FONT_NOTICE_PROVENANCE.json',json.dumps({'scope':'Current-reader notice identities and sources; published_path/path fields are relative to the distribution root, not this JSON directory.','notices':provenance},indent=2)+'\n')
notice='''Paper XI | Komorebi P. | Original writing, figures and editable writing:
Creative Commons Attribution 4.0 International (CC BY 4.0).
https://creativecommons.org/licenses/by/4.0/
Original code listings may also be used under MIT.
Attribute Komorebi P., preserve title and license notice, link the license and
indicate adaptations. Full grants at the distribution root: LICENSE.md and LICENSES/.
Third-party fonts, references and excerpts retain their own terms. This notice
does not relicense them. Keep this notice when distributing the PDF alone.
Accepted publication 1.1.0, 18 October 2026; distribution frozen 21 October 2026.
Conjecture 66 and the stated arithmetic and source-recovery obligations remain
open. Licensing does not change the paper's mathematical scope.
'''
for p in sorted((B/'publication/pdfs').glob('*.pdf')):put(p.relative_to(B).as_posix()+'.license',notice)
(A/'PREPARED_NOTICE_FILES.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(json.dumps({'license_additions':str(D),'added_files':sum(p.is_file() for p in D.rglob('*')),'font_notice_payloads':len(provenance)-2,'full_font_notices':6,'face_or_reference_supplement_files':19,'five_sidecars_staged':True},indent=2))
