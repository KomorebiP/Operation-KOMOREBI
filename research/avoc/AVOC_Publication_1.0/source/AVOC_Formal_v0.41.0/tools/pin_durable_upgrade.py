#!/usr/bin/env python3
"""Release preparation only. Freeze protected sources AFTER successful checking.
Does not bless arbitrary candidate code or repair a drifting existing campaign.
"""
from pathlib import Path
import hashlib, json, os, re, subprocess
R=Path(__file__).resolve().parents[1]
kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
visited=set()
def visit(rel):
 if rel in visited:return
 visited.add(rel)
 text=(R/rel).read_text()
 for mod in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',text,re.M):visit(mod.replace('.','/')+'.lean')
visit('tools/DurableUpgradeMain.lean')
sources=sorted(visited | {'tools/durable_upgrade_campaign.py','tools/run_upgrade_campaign.py'})
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lean=kit/'toolchain/bin/lean'
out={'sources':{s:h(R/s) for s in sources},'compiled_targets':sorted(visited),
 'lean_version':subprocess.check_output([str(lean),'--version'],text=True).strip(),'lean_binary_sha256':h(lean)}
(R/'durable_upgrade_source_pins.json').write_text(json.dumps(out,indent=2)+'\n')
print('Pinned',len(sources),'sources and',len(visited),'local compiled targets')
