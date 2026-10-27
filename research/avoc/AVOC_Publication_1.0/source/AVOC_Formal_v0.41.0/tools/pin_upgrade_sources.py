#!/usr/bin/env python3
"""Release preparation only: freeze checked upgrade source/entrypoint fingerprints.
Do not use this to bless a changed candidate. Reprove and audit changes first.
"""
import hashlib,json,os,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
lean=kit/'toolchain/bin/lean'
seen=set()
def visit(rel):
 if rel in seen:return
 seen.add(rel)
 for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',(root/rel).read_text(),re.M):
  visit(name.replace('.','/')+'.lean')
visit('tools/UpgradeMain.lean')
targets=sorted(seen)
seen.add('tools/run_upgrade_campaign.py')
data=dict(schema=1,scope='protected local source and current build; not hostile-host attestation',
 lean_version=subprocess.check_output([str(lean),'--version'],text=True).strip(),
 lean_binary_sha256=hashlib.sha256(lean.read_bytes()).hexdigest(),compiled_targets=targets,
 sources={s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in sorted(seen)})
(root/'upgrade_source_pins.json').write_text(json.dumps(data,indent=2)+'\n')
print('Frozen',len(seen),'source files,',len(targets),'compiled targets')
