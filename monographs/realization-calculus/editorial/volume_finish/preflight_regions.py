"""Verify all exact native prose regions against the preceding publication."""
from pathlib import Path
import argparse,collections,hashlib,json,sys,zipfile
import fitz
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from volume_finish_adapter import prepare_edit

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--baseline-package',type=Path,required=True)
 args=parser.parse_args();review=ROOT/'editorial/volume_finish'
 plan=json.loads((review/'display_edits.json').read_text())
 spec=json.loads((review/'baseline_build_spec.json').read_text())
 components={c['id']:c for p in spec['parts'] for c in p['components']}
 groups=collections.defaultdict(list)
 for e in plan['edits']:groups[e['component_id'],e['page_1based']].append(e)
 archive=zipfile.ZipFile(args.baseline_package);documents={};errors=[];regions_count=0
 for (cid,pn),edits in groups.items():
  if cid not in documents:
   data=archive.read('Realization_Calculus_Publication_Package/'+components[cid]['path'])
   if hashlib.sha256(data).hexdigest()!=components[cid]['sha256']:raise ValueError('Preceding component hash mismatch')
   documents[cid]=fitz.open(stream=data,filetype='pdf')
  page=documents[cid][pn-1];regions=[]
  try:
   for e in edits:
    for region in prepare_edit(page,e):
     if any((region['rect']&p['rect']).get_area()>.1 for p in regions):raise ValueError('Prepared edit regions overlap')
     regions.append(region)
   regions_count+=len(regions)
  except Exception as ex:errors.append({'component_id':cid,'source_page':pn,'error':str(ex)})
 result={'status':'FAIL' if errors else 'PASS','pages':len(groups),'regions':regions_count,'errors':errors}
 (review/'native_region_preflight.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
