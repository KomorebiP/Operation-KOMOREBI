from pathlib import Path
import json, hashlib, shutil
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
B=Path('/mnt/data/core25/Machine_Native_Reasoning_Lean_Core24')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hist=R/'evidence/history17'; hist.mkdir(parents=True,exist_ok=True)
for n in ['PREDECESSOR.json','MODULES.json','MachineTheory.lean','THEOREM_MAP.json','THEOREM_MAP.md','README.md','PROGRESS_LEDGER.md','CONTINUE_HERE.md','lakefile.toml']:
 if (B/n).exists(): shutil.copy2(B/n,hist/n)
for n in ['verify.py','compare_rebuild.py']:
 shutil.copy2(B/'scripts'/n,hist/('scripts_'+n))
for n in ['REPORT.md','ADMISSION_RECORD.json','ACCEPTED_PROGRESS_LEDGER.md','NEXT_CORE25_SPEC.md']:
 p=B/'release'/n
 if p.exists(): shutil.copy2(p,hist/n)
mods=json.loads((R/'MODULES.json').read_text()); assert len(mods)==72 and mods[-1]=='MachineTheory'
newmods=['MachineTheory.PositivePackets','MachineTheory.CoordinatePackets','MachineTheory.PacketTransport','MachineTheory.PositivePacketExamples']
mods=mods[:-1]+newmods+mods[-1:]
(R/'MODULES.json').write_text(json.dumps(mods,indent=2)+'\n')
a=(R/'MachineTheory.lean').read_text()
(R/'MachineTheory.lean').write_text(a+''.join('\nimport '+m for m in newmods)+'\n')
pins={str(p.relative_to(B)):sha(p) for p in sorted((B/'MachineTheory').glob('*.lean'))}
for p in sorted((B/'source').glob('*')):
 if p.is_file(): pins[str(p.relative_to(B))]=sha(p)
assert len(pins)==76,len(pins)
assert all(sha(R/p)==h for p,h in pins.items())
prev={'source_archive':'Machine_Native_Reasoning_Lean_Core24_v0.17.1.zip',
      'archive_sha256':'406c4b0f63e129025abb313f437c96ce25295add96afec31c58fae3832d804d3',
      'archive_bytes':62071022,'manifest_sha256':'22e28f152be6559fa37848317bf359a23ea422b3e14740a2b310185d1e97975d',
      'verified_manifest_files':2176,'scope':'Intact complete Core 2.4 archive authenticated and extracted; preserve all 71 inherited substantive Lean modules and all five original source-book files. No new recovery gap. Earlier Core 8.3 historical missing files remain documented in predecessor history.',
      'required_unchanged':pins}
(R/'PREDECESSOR.json').write_text(json.dumps(prev,indent=2)+'\n')
a=json.loads((R/'THEOREM_MAP.json').read_text())
row=next(r for r in a if r['label']=='r:positive-packets'); assert not row['lean_endpoints']
row.update(status='KERNEL_CHECKED_BLOCK18',lean_modules=newmods,lean_endpoints=[
'Komorebi.MachineTheory.PositivePackets.source_core25',
'Komorebi.MachineTheory.PositivePackets.sum_positive_weights_one',
'Komorebi.MachineTheory.PositivePackets.Coordinate.source_core25_coordinate',
'Komorebi.MachineTheory.PositivePackets.Coordinate.classification_iff',
'Komorebi.MachineTheory.PositivePackets.Transport.source_coordinate_change'])
(R/'THEOREM_MAP.json').write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n')
text=['# Source-to-Lean map — proposed cumulative Block 18','',
'26 of the 27 selected source statements have explicit endpoint targets. Admission is effective only after the complete current-source and extracted-source gates pass; this file alone is not a verification receipt. The unchanged source index fixes statement identities.','']
for row in a:
 text += [f"## {row['number']} — {row['title']}",f"Source `{row['label']}`, original printed page {row['printed_page']}, lines {row['source_lines']}. Status: `{row['status']}`.",'']
 text += ['- `'+e+'`' for e in row['lean_endpoints']] or ['No formal endpoint is claimed.']
 text += ['']
(R/'THEOREM_MAP.md').write_text('\n'.join(text)+'\n')
p=R/'lakefile.toml'; p.write_text(p.read_text().replace('version = "0.16.1"','version = "0.18.0"'))
p=R/'scripts/verify.py';s=p.read_text()
s=s.replace("komorebi.core24.lean-block-verification.v1","komorebi.core25.lean-block-verification.v1")
s=s.replace("Twenty-five selected Reviewed Core 0.2 results (twenty-four retained, Core2.4 added)","Twenty-six selected Reviewed Core 0.2 results (twenty-five retained, both sectors of Core2.5 added)")
needle="        run_step('check_common_quotient_API'"
assert s.count(needle)==1
pos=s.index(needle)
s=s[:pos]+"        run_step('check_positive_packets_API',lean_argv(Path('checks/CheckPositivePacketsAPI.lean'),obj/'checks/CheckPositivePacketsAPI.olean'))\n        run_step('exact_positive_packets',[sys.executable,'scripts/check_positive_packets.py','--out',str(out/'core25_exact.json')])\n"+s[pos:]
s=s.replace("'KERNEL_CHECKED_BLOCK17'}", "'KERNEL_CHECKED_BLOCK17','KERNEL_CHECKED_BLOCK18'}")
s=s.replace("'r:ending','r:common'}", "'r:ending','r:common','r:positive-packets'}")
p.write_text(s)
p=R/'scripts/compare_rebuild.py';s=p.read_text().replace("'core24_exact.json','checker_import_preservation.json'","'core24_exact.json','core25_exact.json','checker_import_preservation.json'")
s=s.replace('komorebi.block17.fresh-rebuild.v1','komorebi.block18.fresh-rebuild.v1')
p.write_text(s)
print('Configured',len(mods),'production modules;',len(pins),'preservation pins; 26 prospective mapped statements')
