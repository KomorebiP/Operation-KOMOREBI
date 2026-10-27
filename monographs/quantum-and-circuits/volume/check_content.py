from pathlib import Path
import json,re,hashlib,collections
ROOT=Path(__file__).resolve().parent
snapshot=json.loads((ROOT/'mathematical_blocks_source.json').read_text())
def canonical(s):
 # Remove only the reference namespace introduced by consolidation.
 for cmd in ['label','ref','eqref','pageref','cref','Cref','autoref','hyperref','cite','resultrow']:
  s=re.sub(r'\\'+cmd+r'\{([^}]+)\}',lambda m:'\\'+cmd+'{'+','.join(re.sub(r'^(?:qv|ql|q|s|g|cv|cl|c):','',x.strip(),count=1) for x in m[1].split(','))+'}',s)
 s=re.sub(r'\\includegraphics(\[[^\]]*\])?\{([^}]+)\}',lambda m:'\\includegraphics'+(m[1] or '')+'{'+re.sub(r'^[qsgc]_','',Path(m[2]).name)+'}',s)
 return re.sub(r'\s+',' ',s).strip()
def digest(s):return hashlib.sha256(canonical(s).encode()).hexdigest()
def blocks(s):
 envs='theorem|lemma|proposition|corollary|definition|example|proof|principle|algorithm|question|conjecture|protocol|counterexample'
 found=[]
 for m in re.finditer(r'\\begin\{('+envs+r')\}.*?\\end\{\1\}',s,re.S):found.append({'kind':m[1],'text':m[0],'sha256':digest(m[0])})
 for m in re.finditer(r'\\textbf\{Proof\.\}.*?\\\(\\square\\\)',s,re.S):found.append({'kind':'QA-written-proof','text':m[0],'sha256':digest(m[0])})
 return found
alltex='\n'.join(p.read_text() for p in (ROOT/'generated').glob('*.tex'))
actual=blocks(alltex);need=collections.Counter((b['kind'],digest(b['text'])) for b in snapshot);got=collections.Counter((b['kind'],b['sha256']) for b in actual)
missing=need-got;added=got-need
r={'status':'PASS' if not missing else 'FAIL','source_blocks':sum(need.values()),'generated_blocks':sum(got.values()),'source_counts':dict(collections.Counter(b['kind'] for b in snapshot)),'generated_counts':dict(collections.Counter(b['kind'] for b in actual)),'missing':[{'kind':k[0],'sha256':k[1],'multiplicity':v} for k,v in missing.items()],'additional':[{'kind':k[0],'sha256':k[1],'multiplicity':v} for k,v in added.items()],'method':'Exact block text hashes after whitespace normalization, reference namespace removal, and copied scientific asset path normalization. Includes named LaTeX statement/proof environments and arithmetic written proofs ending in square. Excludes prose outside these explicit blocks; does not certify mathematical validity.'}
(ROOT/'qa/content_preservation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2)[:5000])
raise SystemExit(0 if not missing else 1)
