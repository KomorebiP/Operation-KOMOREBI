#!/usr/bin/env python3
"""Freeze the flat Paper I production tree and topologically order its imports."""
import argparse, hashlib, json, re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();root=a.root.resolve()
files={'.'.join(p.relative_to(root).with_suffix('').parts):p for p in root.rglob('*.lean')
       if p.relative_to(root).parts[0].split('.')[0].startswith(('KomorebiVerification','PaperICompletion','PaperIRelease'))}
imports={m:[x for x in re.findall(r'^\s*(?:public\s+)?import\s+([\w.]+)',p.read_text(),re.M) if x in files] for m,p in files.items()}
order=[];visiting=set();seen=set()
def visit(m):
    if m in seen:return
    if m in visiting:raise ValueError('Import cycle: '+m)
    visiting.add(m)
    for dep in imports[m]:visit(dep)
    visiting.remove(m);seen.add(m);order.append(m)
for m in sorted(files):visit(m)
rows=[{'module':m,'source_sha256':hashlib.sha256(files[m].read_bytes()).hexdigest()} for m in order]
a.out.write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),'production sources frozen')
