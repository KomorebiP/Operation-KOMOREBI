"""Use the existing verified component builder for explicit editorial subsets."""
from pathlib import Path
import json,concurrent.futures,sys
p=Path(__file__).resolve().parent/'build_all.py'
targets=sys.argv[1:] or [f'{r}_{role}' for r in ['V','VI','VII','VIII'] for role in ['traditional','visual_guide']]
sys.argv=[sys.argv[0]]
d={'__file__':str(p),'__name__':'book_component_rebuild'}
exec(compile(p.read_text().split('with concurrent.futures.ThreadPoolExecutor')[0],str(p),'exec'),d)
tasks=[x for x in d['TASKS'] if f'{x[0]}_{x[1]}' in targets]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: results=list(ex.map(d['build'],tasks))
out=p.parent/'REBUILD_RESULT.json';rs=json.loads(out.read_text());lookup={(r['paper'],r['role']):r for r in results};rs=[lookup.get((r['paper'],r['role']),r) for r in rs];out.write_text(json.dumps(rs,indent=2))
raise SystemExit(0 if all(r['success'] for r in results) else 1)
