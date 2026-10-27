#!/usr/bin/env python3
"""Current raw-tree preservation and historical index discrepancy inventory."""
from pathlib import Path
import argparse,hashlib,json,zipfile
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();b=a.baseline.resolve();r=a.root.resolve()
 mismatches=[];sources=[];archives=[]
 for q in sorted((b/'source').rglob('*')):
  if q.is_file():
   rel=q.relative_to(b).as_posix(); row={'path':rel,'bytes':q.stat().st_size,'sha256':sha(q)};sources.append(row)
   if not (r/rel).is_file() or sha(r/rel)!=row['sha256']:mismatches.append(rel)
 for z in sorted((b/'downloads').glob('*.zip')):
  rel=z.relative_to(b);assert sha(z)==sha(r/rel)
  with zipfile.ZipFile(z) as f:
   errors=[];payload=[n for n in f.namelist() if not n.endswith('/')];branch='complete' if z.name.startswith('Paper_VIII_Complete') else 'strengthened'
   for n in payload:
    q=r/'source'/branch/n
    if not q.is_file() or q.read_bytes()!=f.read(n):errors.append(n)
   archives.append({'path':rel.as_posix(),'sha256':sha(z),'payload_files':len(payload),'all_payload_members_match_source':not errors,'mismatches':errors})
 # Audit the retrieved root's own old index, not the concurrently edited edition.
 index=json.loads((b/'MANIFEST_SHA256.json').read_text());rows=index['files'];bad=[];missing=[]
 for item in rows:
  q=b/item['path']
  if not q.is_file():missing.append(item['path'])
  elif q.stat().st_size!=item['bytes'] or sha(q)!=item['sha256']:bad.append({'path':item['path'],'indexed_bytes':item['bytes'],'actual_bytes':q.stat().st_size,'indexed_sha256':item['sha256'],'actual_sha256':sha(q)})
 declared={x['path'] for x in rows};actual={q.relative_to(b).as_posix() for q in b.rglob('*') if q.is_file() and q!=b/'MANIFEST_SHA256.json'}
 report={'status':'PASS_FOR_RAW_PRESERVATION','source_files':len(sources),'source_bytes':sum(x['bytes'] for x in sources),'delivered_source_matches_retrieved':not mismatches,'source_mismatches':mismatches,'archives':archives,'historical_outer_index':{'entries':len(rows),'missing':missing,'preexisting_hash_or_size_mismatches':bad,'unindexed_retrieved_payload_paths':sorted(actual-declared),'scope':'Retrieved baseline outer index predates later formatting changes; discrepancies are historical, not created by this monograph.'},'source_inventory':sources}
 assert not mismatches and all(x['all_payload_members_match_source'] for x in archives)
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='source_inventory'},indent=2))
if __name__=='__main__':main()
