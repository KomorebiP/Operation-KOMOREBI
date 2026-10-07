#!/usr/bin/env python3
"""Rebuild Paper I sources, audit mapped declarations, and test rejection controls.

Run inside the portable kit's Lake environment. No dependency revision or
mathematical source is changed. The upstream cached dependencies are reused.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, time
from pathlib import Path

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def active_text(s: str) -> str:
    # Lean comments nest. String contents are not scanned as declarations.
    out=[]; i=0; depth=0; quoted=False
    while i<len(s):
        if depth:
            if s.startswith('/-',i): depth+=1; i+=2
            elif s.startswith('-/',i): depth-=1; i+=2
            else:
                out.append('\n' if s[i]=='\n' else ' '); i+=1
        elif quoted:
            if s[i]=='\\': out.extend('  '); i+=2
            elif s[i]=='"': quoted=False; out.append(' '); i+=1
            else: out.append('\n' if s[i]=='\n' else ' '); i+=1
        elif s.startswith('--',i):
            j=s.find('\n',i); j=len(s) if j<0 else j
            out.extend(' '*(j-i)); i=j
        elif s.startswith('/-',i): depth=1; out.extend('  '); i+=2
        elif s[i]=='"': quoted=True; out.append(' '); i+=1
        else: out.append(s[i]); i+=1
    if depth or quoted: raise RuntimeError('Unterminated comment/string')
    return ''.join(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--kit',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); project=a.project.resolve(); kit=a.kit.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    report={'status':'RUNNING','project':str(project),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'modules':[],'checks':[],'limits':['Pinned dependency cache reused; Mathlib was not independently rebuilt.','Compiler acceptance and source-to-prose correspondence are distinct checks.']}
    def save(): (out/'fresh_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        target=json.loads((project/'lake-manifest.json').read_text()); cached=json.loads((kit/'workspace/lake-manifest.json').read_text())
        cmap={p['name']:p for p in cached['packages']}; pins=[]
        def norm_url(s): return s.rstrip('/').removesuffix('.git')
        for p in target['packages']:
            q=cmap[p['name']]; cp=kit/'workspace/.lake/packages'/p['name']
            head=subprocess.check_output(['git','-C',str(cp),'rev-parse','HEAD'],text=True).strip()
            if norm_url(p['url'])!=norm_url(q['url']) or p['rev']!=q['rev'] or head!=p['rev']: raise RuntimeError('Dependency mismatch: '+p['name'])
            pins.append({'name':p['name'],'rev':head,'manifest_url':p['url'],'cache_url':q['url']})
        report['dependencies']=pins
        version=subprocess.check_output(['lean','--version'],text=True).strip(); report['lean_version']=version
        if 'version 4.34.0-rc2' not in version: raise RuntimeError('Wrong compiler')
        if (project/'lean-toolchain').read_text().strip()!=(kit/'workspace/lean-toolchain').read_text().strip(): raise RuntimeError('Toolchain pin mismatch')
        sources={'.'.join(p.relative_to(project).with_suffix('').parts):p for p in project.glob('**/*.lean') if '.lake' not in p.parts}
        report['source_hashes']={str(p.relative_to(project)):digest(p) for p in sources.values()}
        forbidden=r'\b(sorry|admit|sorryAx|axiom|unsafe|opaque|native_decide)\b|Lean\.addDecl|addAndCompile|ofReduceBool'
        findings=[]
        for p in sources.values():
            for m in re.finditer(forbidden,active_text(p.read_text())): findings.append((str(p.relative_to(project)),m.group()))
        if findings: raise RuntimeError('Source-policy failures: '+repr(findings))
        report['source_policy']='PASS'
        dep={m:[x for x in re.findall(r'^import\s+(\S+)',p.read_text(),re.M) if x in sources] for m,p in sources.items()}
        order=[]; pending=set(sources)
        while pending:
            ready=sorted(m for m in pending if all(x in order for x in dep[m]))
            if not ready: raise RuntimeError('Import cycle')
            order.extend(ready); pending.difference_update(ready)
        build=out/'objects'; build.mkdir(exist_ok=True)
        # The output folder must start clean, so no project object is reused.
        if any(build.rglob('*.olean')): raise RuntimeError('Refusing nonempty build output')
        env=os.environ.copy(); env['LEAN_PATH']=str(build)+os.pathsep+env.get('LEAN_PATH','')
        flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
        report['compiler_flags']=flags
        def run(label,cmd,expect_failure=False,pattern=None):
            start=time.monotonic(); log=out/(label+'.log')
            try:
                with log.open('w') as f: proc=subprocess.run(cmd,cwd=project,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
                code=proc.returncode
            except subprocess.TimeoutExpired:
                code=124
            text=log.read_text(errors='replace')
            passed=(code==0) if not expect_failure else (code!=0 and code!=124 and pattern is not None and re.search(pattern,text) is not None and not re.search(r'[Uu]nknown (identifier|module|constant)|error\(lean\.(unknownIdentifier|unknownModule)|object file .* does not exist|failed to locate|unknown option',text))
            row={'label':label,'command':cmd,'returncode':code,'seconds':round(time.monotonic()-start,3),'passed':bool(passed),'log':log.name,'log_sha256':digest(log)}
            report['checks'].append(row); save(); print(('PASS' if passed else 'FAIL')+' '+label+' '+str(row['seconds'])+'s',flush=True)
            if not passed: raise RuntimeError('Failed '+label+'; see '+str(log))
            return text
        for m in order:
            p=sources[m]; obj=build.joinpath(*m.split('.')).with_suffix('.olean'); obj.parent.mkdir(parents=True,exist_ok=True)
            run('compile_'+m.replace('.','_'),['lean',*flags,'-o',str(obj),str(p.relative_to(project))])
            if not obj.is_file(): raise RuntimeError('Compiler produced no object: '+m)
            report['modules'].append({'module':m,'source_sha256':digest(p),'object_sha256':digest(obj)}); save()
        maps=list(project.glob('LEAN_THEOREM_MAP_v*.md'))
        if len(maps)!=1: raise RuntimeError('Map ambiguity')
        rows={}
        for line in maps[0].read_text().splitlines():
            if re.match(r'^\|\s*\d+\s*\|',line):
                cols=[c.strip() for c in line.split('|')[1:-1]]
                if len(cols)!=6 or cols[2] not in ['Exact','Stronger']: raise RuntimeError('Map row invalid')
                idx=int(cols[0]); names=re.findall(r'`((?:Komorebi|KomorebiVerification)\.[^`]+)`',cols[3]); rows[idx]=names
        if sorted(rows)!=list(range(1,36)): raise RuntimeError('Missing map row')
        names=[n for ns in rows.values() for n in ns]
        if len(names)!=len(set(names)): raise RuntimeError('Duplicate map targets')
        direct=re.findall(r'^#print axioms\s+(\S+)\s*$',(project/'KomorebiVerification/KernelAudit.lean').read_text(),re.M)
        if sorted(direct)!=sorted(names): raise RuntimeError('Map/audit mismatch')
        # A separately elaborated file both resolves the declarations and prints every type.
        inventory=out/'MappedTypes.lean'
        inventory.write_text('import KomorebiVerification\n'+''.join('set_option pp.universes true\n#check '+n+'\nset_option pp.universes false\n#print axioms '+n+'\n' for n in names))
        text=run('mapped_declarations',['lean',*flags,str(inventory)])
        axiom_rows=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",text)
        if len(axiom_rows)!=len(names) or set(n for n,_ in axiom_rows)!=set(names): raise RuntimeError('Missing direct axiom reports')
        for n,axs in axiom_rows:
            if set(x.strip() for x in axs.split(',') if x.strip())-{'propext','Classical.choice','Quot.sound'}: raise RuntimeError('Unapproved axioms for '+n)
        report['mapped_rows']=len(rows); report['mapped_declarations']=len(names); report['direct_axiom_reports']=len(axiom_rows)
        audit=run('kernel_audit',['lean',*flags,'KomorebiVerification/KernelAudit.lean'])
        m=re.search(r'FAIL-CLOSED KERNEL AUDIT PASS: (\d+) project declarations',audit)
        if not m: raise RuntimeError('No fail-closed audit summary')
        report['namespace_declarations_audited']=int(m.group(1))
        negatives={'FalseEquality':('import Mathlib.Data.Nat.Basic\nexample : (0 : Nat) = 1 := by decide\n',r'decide.*(false|failed)|is false|tactic.*failed'), 'Placeholder':('import Mathlib.Data.Nat.Basic\nexample : (0 : Nat) = 1 := by sorry\n',r'uses .sorry.|declaration uses')}
        for name,(body,pattern) in negatives.items():
            p=out/(name+'.lean'); p.write_text(body)
            run('negative_'+name,['lean',*flags,str(p)],True,pattern)
        report['status']='PASS'; report['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()); save()
        print('FRESH PAPER I VERIFICATION PASS: '+str(len(order))+' modules, '+str(len(rows))+' rows, '+str(len(names))+' mapped declarations.',flush=True)
    except Exception as e:
        report['status']='FAIL'; report['failure']=str(e); save(); print(str(e),flush=True); raise
if __name__=='__main__': main()
