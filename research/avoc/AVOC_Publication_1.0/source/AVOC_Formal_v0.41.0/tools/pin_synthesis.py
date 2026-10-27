#!/usr/bin/env python3
"""Release preparation ONLY: freeze reviewed synthesis runtime source closure.
Do not use this to bless arbitrary changes in an existing campaign.
"""
from pathlib import Path
import hashlib,json,os,re,subprocess
root=Path(__file__).resolve().parents[1]
kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
seen=set()
def visit(rel):
 if rel in seen:return
 seen.add(rel)
 for m in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',(root/rel).read_text(),re.M):
  visit(m.replace('.','/')+'.lean')
visit('tools/SynthesisMain.lean')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=set(seen)|{'tools/synthesize_upgrade.py'}
obj={'sources':{r:sha(root/r) for r in sorted(source)},'targets':sorted(seen),
     'lean_version':subprocess.check_output([str(kit/'toolchain/bin/lean'),'--version'],text=True).strip(),
     'lean_sha256':sha(kit/'toolchain/bin/lean')}
(root/'synthesis_source_pins.json').write_text(json.dumps(obj,indent=2)+'\n')
print('Pinned',len(source),'sources and',len(seen),'compiled targets')
