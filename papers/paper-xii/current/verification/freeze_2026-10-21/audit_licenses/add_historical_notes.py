from pathlib import Path
import json,hashlib,fitz
W=Path('/dev/shm/komorebi_paper_xii_freeze_fbc994080222');A=W/'audit_licenses';D=A/'license_additions'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(rel,data):
 p=D/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes) else data.encode());return p
metadata=json.loads((A/'HISTORICAL_FAMILY_METADATA.json').read_text());provenance=[]
for r in metadata:
 p=W/'baseline'/r['pdf']
 with fitz.open(p) as doc:
  raw=doc.extract_font(r['xref'])[3]
 r['pdf_sha256']=sha(p);r['font_program_sha256']=hashlib.sha256(raw).hexdigest()
 if r['font']=='SFRM1000':
  rel='LICENSES/fonts/historical/CM-SUPER-OBSERVED-HEADER.txt';put(rel,r['plaintext_header']+'\n');provenance.append({'published_path':rel,'path':rel,'bytes':(D/rel).stat().st_size,'sha256':sha(D/rel),'source_baseline_pdf':r['pdf'],'source_pdf_sha256':r['pdf_sha256'],'source_font_program_sha256':r['font_program_sha256'],'copy':'Exact observed historical embedded program plaintext prefix through FontInfo end readonly def, plus newline; no glyph program.','scope':'Historical CM-Super copyright and unversioned GPL pointer; no license version or embedding exception inferred.'})
(A/'HISTORICAL_FAMILY_METADATA.json').write_text(json.dumps(metadata,indent=2)+'\n')
rel='LICENSES/fonts/historical/LPPL-1.3c.tex';src=Path('/usr/share/texlive/texmf-dist/tex/latex/base/lppl.tex');put(rel,src.read_bytes());provenance.append({'published_path':rel,'path':rel,'bytes':src.stat().st_size,'sha256':sha(src),'source':str(src),'source_sha256':sha(src),'copy':'Complete unmodified installed LPPL 1.3c license document in its original TeX form.','scope':'Referenced full license text for Latin Modern/GUST and current Yhmath package metadata; not proof of old embedded font lineage.'})
rel='LICENSES/fonts/historical/FAMILY_SOURCE_LIMITS.txt';put(rel,'''HISTORICAL FONT FAMILY NOTES | 21 October 2026

These observations concern retained historical PDFs, not the three current
readers. They do not certify exact historical font-program source or license
lineage. Every original PDF and embedded program remains byte-identical.

CM-Super
The retained original historical paper embeds an SFRM1000 program with a 2001
Vladimir Volovich copyright and a pointer to COPYING / GNU GPL. Its observed
plaintext prefix is copied in CM-SUPER-OBSERVED-HEADER.txt; the original embedded
font program and source PDF hashes are in the full audit. The current CTAN
package record also names GPL: https://ctan.org/pkg/cm-super . Neither the
embedded header nor that generic package label specifies a GPL version here.
The already supplied generic GPL-2.txt remains reference text only. No unstated
font embedding exception or exact original source version is inferred. Attempts
to retrieve the original CM-Super README/COPYING through available mirrors failed;
that access limit remains explicit.

Yhmath
The retained historical paper also embeds Yhcmex, with a 2003 conversion header
naming Haruhiko Okumura. Its actual embedded metadata is retained in the full
audit. Current CTAN metadata identifies the Yhmath package and LPPL 1.3c:
https://ctan.org/pkg/yhmath . The package README attributes the font/support
bundle to Yannis Haralambous and describes merging its older packages. Complete
unmodified LPPL 1.3c text is included as LPPL-1.3c.tex. Current package metadata
is not a recovered license history for that exact 2003 subset program.
The package-specific LICENSE retrieval failed; no missing historical copyright
or permission text is invented.

These historical family notes supplement the complete existing and current-
reader font notices. They do not assign the original project's MIT or CC BY
license to any font. More metadata or a family-name match would not, by itself,
prove exact historical program provenance. Detailed inventory and source-access
history are in the full ZIP's dated audit_licenses directory.
''')
provenance.append({'published_path':rel,'path':rel,'bytes':(D/rel).stat().st_size,'sha256':sha(D/rel),'role':'Bounded paraphrase of primary CTAN metadata plus observed historical embedded headers; not a newly granted font license.','primary_sources':[{'url':'https://ctan.org/pkg/cm-super','web_ref':'turn88view0','claim':'Current package generic GPL label; version/embedding terms not inferred.'},{'url':'https://ctan.org/pkg/yhmath','web_ref':'turn88view1','claim':'Current package version1.6/2020 and LPPL1.3c metadata.'},{'url':'https://mirrors.ctan.org/fonts/yhmath/README','web_ref':'turn89view3','claim':'Package authorship/merge and LPPL pointer; no exact older font provenance.'}],'access_limits':['CM-Super README/COPYING inaccessible via available mirror retrievals.','Yhmath package-specific LICENSE retrieval inaccessible.','Current package metadata does not authenticate the historical 2001/2003 embedded font lineage.']})
p=D/'LICENSES/FONT_NOTICE_PROVENANCE.json';d=json.loads(p.read_text());d['historical_notes']=provenance;p.write_text(json.dumps(d,indent=2)+'\n')
p=D/'LICENSES/THIRD_PARTY_NOTICES.txt';s=p.read_text();s+='\nAdditional historical CM-Super and Yhcmex family observations and full LPPL\nreference text are under fonts/historical/. Their source-access and exact\nhistorical font-origin limits remain explicit; no missing permission or\nunstated embedding exception is invented. These fonts do not occur in the\nthree current readers.\n';p.write_text(s)
files=[{'path':p.relative_to(D).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(D.rglob('*')) if p.is_file()];(A/'LICENSE_ADDITION_INVENTORY.json').write_text(json.dumps({'scope':'All additive paths relative to frozen distribution root. Core unchanged. The three LICENSES/PDF_NOTICES files may also be copied unchanged adjacent to smaller reader PDFs.','files':files},indent=2)+'\n')
print(json.dumps({'total_additions':len(files),'current_font_notice_payloads':27,'historical_supplement_payloads':len(provenance),'source_access_limits_explicit':True}))
