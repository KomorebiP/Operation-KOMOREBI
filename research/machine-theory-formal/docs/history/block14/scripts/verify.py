#!/usr/bin/env python3
"""Cold-build this proof block against an existing pinned runtime and audit actual proof terms.
No network access, dependency installation, or modification of the source book occurs.
Outputs go to a new evidence directory. The dependency cache is reused, not rebuilt.
"""
from __future__ import annotations
import argparse, collections, datetime, hashlib, json, os, re, shutil, subprocess, sys, time, signal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
LEAN_COMMIT = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
MATHLIB_COMMIT = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()

def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def masked_lean(text: str) -> str:
    # Only a source preflight. The Lean compiler and environment audit are authoritative.
    out = []; i = 0; depth = 0; string = False
    while i < len(text):
        if depth:
            if text.startswith('/-', i): depth += 1; out.extend('  '); i += 2
            elif text.startswith('-/', i): depth -= 1; out.extend('  '); i += 2
            else: out.append('\n' if text[i] == '\n' else ' '); i += 1
        elif string:
            if text[i] == '\\': out.extend('  '); i += 2
            elif text[i] == '"': string = False; out.append(' '); i += 1
            else: out.append('\n' if text[i] == '\n' else ' '); i += 1
        elif text.startswith('/-', i): depth = 1; out.extend('  '); i += 2
        elif text.startswith('--', i):
            end = text.find('\n', i); end = len(text) if end < 0 else end
            out.extend(' ' * (end-i)); i = end
        elif text[i] == '"': string = True; out.append(' '); i += 1
        else: out.append(text[i]); i += 1
    if depth or string: raise ValueError('Unterminated source comment or string')
    return ''.join(out)

def source_inventory():
    rows = []
    for path in [ROOT/'MachineTheory.lean'] + sorted((ROOT/'MachineTheory').glob('*.lean')):
        text = masked_lean(path.read_text(encoding='utf-8'))
        banned = re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe|implemented_by|extern)\b', text)
        if banned: raise ValueError(f'Forbidden production syntax in {path}: {banned}')
        stack = []
        for line_no, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            m = re.match(r'namespace\s+([\w.]+)', line)
            if m: stack.append(('namespace',m.group(1))); continue
            if re.match(r'(?:noncomputable\s+)?section\b', line): stack.append(('section','')); continue
            if re.match(r'end(?:\s|$)',line):
                if not stack: raise ValueError(f'Unbalanced namespace in {path}')
                stack.pop(); continue
            line = re.sub(r'^@\[[^]]*\]\s*','',line)
            m = re.match(r'(?:noncomputable\s+)?(theorem|lemma|def|abbrev|structure|inductive|instance)\s+([\w?.]+)',line)
            if m:
                ns='.'.join(n for kind,n in stack if kind=='namespace')
                rows.append({'name':ns+'.'+m.group(2),'kind':m.group(1),
                             'file':str(path.relative_to(ROOT)), 'line':line_no})
    if len({r['name'] for r in rows}) != len(rows): raise ValueError('Duplicate source declarations')
    return rows

def source_pins():
    paths=[ROOT/'MachineTheory.lean', ROOT/'MODULES.json', ROOT/'lean-toolchain',
           ROOT/'lakefile.toml',ROOT/'lake-manifest.json', ROOT/'THEOREM_MAP.json', ROOT/'PREDECESSOR.json']
    for directory in ['MachineTheory','scripts','checks','docs','source']:
        paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend(p for p in ROOT.glob('*.md') if p.is_file())
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(set(paths))}

def parse_axioms(text: str):
    rows = {}
    for match in re.finditer(r"['‘]([^'’]+)['’] depends on axioms:\s*\[([^]]*)\]", text):
        if match.group(1) in rows: raise ValueError('Duplicate axiom report')
        rows[match.group(1)] = [a.strip() for a in match.group(2).split(',') if a.strip()]
    for match in re.finditer(r"['‘]([^'’]+)['’] does not depend on any axioms", text):
        if match.group(1) in rows: raise ValueError('Duplicate axiom report')
        rows[match.group(1)] = []
    return rows

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',default=os.environ.get('KOMOREBI_LEAN_RUNTIME'))
    ap.add_argument('--out',default='evidence/local_replay')
    ap.add_argument('--timeout',type=int,default=45)
    args=ap.parse_args()
    if not args.runtime: ap.error('--runtime or KOMOREBI_LEAN_RUNTIME is required')
    rt=Path(args.runtime).resolve(); out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out=out.resolve()
    if out.exists() and any(out.iterdir()):
        ap.error(f'Output is not empty: {out}. Choose a fresh evidence directory.')
    out.mkdir(parents=True,exist_ok=True); logs=out/'logs';logs.mkdir()
    obj=out/'objects'; obj.mkdir()
    lean=rt/'toolchain/bin/lean'; checker=rt/'toolchain/bin/leanchecker'
    packages=rt/'workspace/.lake/packages'
    libs=sorted(packages.glob('*/.lake/build/lib/lean'))
    env=os.environ.copy(); env['PATH']=str(lean.parent)+os.pathsep+env.get('PATH','')
    env['LEAN_PATH']=os.pathsep.join(str(p) for p in [obj]+libs)
    env['LEAN_NUM_THREADS']='1'
    report={'schema':'komorebi.block14.lean-block-verification.v1','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scope':'Twenty-two selected Reviewed Core 0.2 results (twenty-one retained, Core8.1 added); local source cold build, actual axiom audit, API checks, same-kernel local-module replay and negative controls.',
            'runtime':str(rt),'root':str(ROOT),'python':sys.version,'platform':sys.platform,
            'per_command_timeout_seconds':args.timeout,'lean_internal_memory_limit_MiB':4096,
            'separate_OS_memory_cap':False,'external_dependency_rebuild':False,'runtime_adapter':env.get('LD_PRELOAD'),'steps':[],'status':'RUNNING'}
    before=source_pins(); report['input_sha256_before']=before
    def run_step(name, argv, success=True, expected_diagnostics=()):
        t=time.monotonic(); timedout=False
        try:
            p=subprocess.Popen(argv,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
            text,_=p.communicate(timeout=args.timeout)
            code=p.returncode
        except subprocess.TimeoutExpired as exc:
            code=None; timedout=True
            os.killpg(p.pid,signal.SIGKILL)
            text,_=p.communicate()
            text+='\nTIMEOUT: this execution is not proof evidence.\n'
        log=logs/(name+'.log');log.write_text(text,encoding='utf-8')
        expected=(code==0) if success else (code is not None and code!=0)
        diagnostic_ok=all(d.lower() in text.lower() for d in expected_diagnostics)
        bad_import=any(d in text.lower() for d in ['unknown module','unknown constant','invalid import','failed to load','expected token'])
        ok=expected and not timedout and diagnostic_ok and (success or not bad_import)
        report['steps'].append({'name':name,'argv':argv,'cwd':str(ROOT),'exit_code':code,'timed_out':timedout,
                                'expected_success':success,'seconds':time.monotonic()-t,'passed':ok,
                                'log':str(log.relative_to(out)), 'log_sha256':digest(log)})
        write_json(out/'report.json',report)
        print(f'{name}: {"PASS" if ok else "FAIL"} ({code}, {time.monotonic()-t:.2f}s)',flush=True)
        if not ok: raise RuntimeError(f'{name} did not satisfy its execution contract. Read {log}')
        return text
    def lean_argv(src, output=None):
        a=[str(lean),'-j1','-M4096','-DwarningAsError=true']
        if output is not None:
            output.parent.mkdir(parents=True,exist_ok=True);a+=['-o',str(output)]
        return a+[str(src)]
    try:
        version=run_step('lean_version',[str(lean),'--version'])
        if '4.34.0-rc2' not in version or LEAN_COMMIT not in version: raise ValueError('Wrong Lean compiler')
        report['lean_version']=version.strip()
        pin_manifest=json.loads((ROOT/'lake-manifest.json').read_text())
        gitpins={}
        for pkg in pin_manifest['packages']:
            p=subprocess.run(['git','-C',str(packages/pkg['name']),'rev-parse','HEAD'],capture_output=True,text=True,timeout=10)
            if p.returncode or p.stdout.strip()!=pkg['rev']: raise ValueError(f'Wrong dependency pin: {pkg["name"]}')
            gitpins[pkg['name']]=p.stdout.strip()
        if gitpins.get('mathlib')!=MATHLIB_COMMIT: raise ValueError('Wrong mathlib')
        report['dependency_revisions']=gitpins
        run_step('verifier_selftests',[sys.executable,'scripts/test_verifier.py'])
        predecessor=json.loads((ROOT/'PREDECESSOR.json').read_text())
        preserved={p: digest(ROOT/p)==h for p,h in predecessor['required_unchanged'].items()}
        if not all(preserved.values()): raise ValueError('Predecessor preservation failed')
        write_json(out/'preservation.json',{'predecessor':predecessor,'checks':preserved,'status':'PASS'})
        report['preserved_predecessor_files']=len(preserved)
        inv=source_inventory();write_json(out/'source_inventory.json',inv)
        report['authored_declaration_count']=len(inv)
        report['authored_theorem_count']=sum(r['kind'] in ('theorem','lemma') for r in inv)
        mods=json.loads((ROOT/'MODULES.json').read_text())
        for mod in mods:
            src=Path(mod.replace('.','/')+'.lean');target=obj/src.with_suffix('.olean')
            run_step('build_'+mod,lean_argv(src,target))
        api=run_step('check_API',lean_argv(Path('checks/CheckAPI.lean'),obj/'checks/CheckAPI.olean'))
        run_step('check_approximation_API',lean_argv(Path('checks/CheckApproximationAPI.lean'),obj/'checks/CheckApproximationAPI.olean'))
        run_step('check_response_API',lean_argv(Path('checks/CheckResponseAPI.lean'),obj/'checks/CheckResponseAPI.olean'))
        run_step('check_recipient_API',lean_argv(Path('checks/CheckRecipientAPI.lean'),obj/'checks/CheckRecipientAPI.olean'))
        run_step('check_hard_inquiry_API',lean_argv(Path('checks/CheckHardInquiryAPI.lean'),obj/'checks/CheckHardInquiryAPI.olean'))
        run_step('check_binary_API',lean_argv(Path('checks/CheckBinaryAPI.lean'),obj/'checks/CheckBinaryAPI.olean'))
        run_step('check_synthesis_API',lean_argv(Path('checks/CheckSynthesisAPI.lean'),obj/'checks/CheckSynthesisAPI.olean'))
        run_step('check_prefix_API',lean_argv(Path('checks/CheckPrefixAPI.lean'),obj/'checks/CheckPrefixAPI.olean'))
        run_step('check_revision_API',lean_argv(Path('checks/CheckRevisionAPI.lean'),obj/'checks/CheckRevisionAPI.olean'))
        run_step('check_prices_API',lean_argv(Path('checks/CheckPricesAPI.lean'),obj/'checks/CheckPricesAPI.olean'))
        run_step('check_lineage_API',lean_argv(Path('checks/CheckLineageAPI.lean'),obj/'checks/CheckLineageAPI.olean'))
        run_step('check_joint_reconstruction_API',lean_argv(Path('checks/CheckJointReconstructionAPI.lean'),obj/'checks/CheckJointReconstructionAPI.olean'))
        run_step('positive_control',lean_argv(Path('checks/PositiveControl.lean'),obj/'checks/PositiveControl.olean'))
        closure=run_step('environment_inventory',lean_argv(Path('checks/ImportClosure.lean'),obj/'checks/ImportClosure.olean'))
        imports=re.findall(r'^IMPORTED_MODULE (\S+)$',closure,re.M)
        constants=[{'kind':k,'name':n} for k,n in re.findall(r'^PROJECT_CONSTANT (\w+) (\S+)$',closure,re.M)]
        envnames={c['name'] for c in constants}
        if not {r['name'] for r in inv}<=envnames: raise ValueError('Source inventory not present in compiled environment')
        if any(c['kind']=='axiom' for c in constants): raise ValueError('Custom axiom in project namespace')
        write_json(out/'environment_constants.json',sorted(constants,key=lambda x:x['name']))
        # Admission is checked against both the exact source index and actual elaborated endpoints.
        source_index=json.loads((ROOT/'source/RESULT_INDEX_v0.2.json').read_text())
        admission=json.loads((ROOT/'THEOREM_MAP.json').read_text())
        if len(admission)!=27 or len(source_index)!=27: raise ValueError('Unexpected source-result count')
        source_rows={row['label']:row for row in source_index}
        selected=[]
        for row in admission:
            original=source_rows[row['label']]
            for key in ['number','title','source_lines','printed_page']:
                if row[key]!=original[key]: raise ValueError('Theorem-map/source mismatch')
            if row['lean_endpoints']:
                if row['status'] not in {'KERNEL_CHECKED_BLOCK01','KERNEL_CHECKED_BLOCK02','KERNEL_CHECKED_BLOCK03','KERNEL_CHECKED_BLOCK04','KERNEL_CHECKED_BLOCK05','KERNEL_CHECKED_BLOCK06','KERNEL_CHECKED_BLOCK07','KERNEL_CHECKED_BLOCK08','KERNEL_CHECKED_BLOCK09','KERNEL_CHECKED_BLOCK10','KERNEL_CHECKED_BLOCK11','KERNEL_CHECKED_BLOCK12','KERNEL_CHECKED_BLOCK13','KERNEL_CHECKED_BLOCK14'}: raise ValueError('Unrecognized admission status')
                for endpoint in row['lean_endpoints']:
                    if not any(c['name']==endpoint and c['kind']=='theorem' for c in constants):
                        raise ValueError(f'Missing formal endpoint: {endpoint}')
                selected.append(row['label'])
            elif row['status']!='NOT_FORMALIZED_IN_THIS_BLOCK': raise ValueError('Unsupported promotion')
        if set(selected)!={'r:factor','r:behavior','r:packet','r:transport','r:memory','r:instrument','r:bayes','r:joint-refinement','r:belief-planning','r:history-bound','r:policy-error','r:risk','r:recipient','r:inquiry','r:lowerbound','r:cegis','r:ordered','r:prefix','r:dependencies','r:prices','r:lineage','r:reconstruction'}:
            raise ValueError('Selected scope changed')
        binding=json.loads((ROOT/'source/SOURCE_BINDING.json').read_text())
        if digest(ROOT/'source/core_v0.2.tex')!=binding['source_tex_sha256'] or digest(ROOT/'source/Reviewed_Core_v0.2.pdf')!=binding['original_pdf_sha256']:
            raise ValueError('Source-book identity changed')
        report['source_results_formalized']=len(selected)
        report['source_results_not_formalized']=27-len(selected)
        # Audit every theorem constant, including generated auxiliaries, plus every authored declaration.
        audited=sorted({c['name'] for c in constants if c['kind']=='theorem'}|{r['name'] for r in inv})
        audit=out/'Audit.lean'
        audit.write_text('import MachineTheory\nset_option format.width 200000\nset_option linter.auxLemma false\n'+''.join(f'#print axioms {n}\n' for n in audited))
        axtext=run_step('axiom_audit',lean_argv(audit,obj/'Audit.olean'))
        ax=parse_axioms(axtext)
        if set(ax)!=set(audited): raise ValueError(f'Incomplete axiom report: expected {len(audited)}, parsed {len(ax)}')
        violations={n:a for n,aa in ax.items() for a in aa if a not in ALLOWED}
        if violations: raise ValueError(f'Unapproved axioms: {violations}')
        write_json(out/'axioms.json',{'allowed':sorted(ALLOWED),'declarations':ax,'violations':violations})
        report['axiom_audited_declarations']=len(ax)
        report['compiled_theorem_constants_including_generated']=sum(c['kind']=='theorem' for c in constants)
        report['actual_axiom_union']=sorted({a for aa in ax.values() for a in aa})
        for mod in mods:
            if mod=='MachineTheory': continue # aggregate has imports only; replayed definitions reside in the substantive files.
            run_step('kernel_replay_'+mod,[str(checker),'--verbose',mod])
        controls=json.loads((ROOT/'checks/NEGATIVE_CONTROLS.json').read_text())
        for c in controls:
            accepted=c['expected_compile']=='accepted_then_axiom_audit_rejects'
            text=run_step('negative_'+c['name'],lean_argv(Path(c['file'])),success=accepted,
                          expected_diagnostics=c.get('expected_diagnostics',()))
            if accepted:
                ca=parse_axioms(text)
                leaked={a for aa in ca.values() for a in aa}-ALLOWED
                if c['unexpected_axiom'] not in leaked: raise ValueError('Custom-axiom control was not detected')
                report['steps'][-1]['axiom_policy_rejected']=True
                report['steps'][-1]['unapproved_axioms']=sorted(leaked)
        report['negative_controls']=len(controls)
        # Match the exact loaded upstream proof/cache parts and compiler artifacts to the recovered inventory.
        manifest_path=rt/'verification/file-manifest.json'
        manifest=json.loads(manifest_path.read_text())
        entries={r['path']:r for r in manifest['files']}
        externals={}
        search=[obj]+libs+[rt/'toolchain/lib/lean']
        for mod in imports:
            rel=Path(mod.replace('.','/')+'.olean')
            found=next((base/rel for base in search if (base/rel).is_file()),None)
            if found is None: raise FileNotFoundError(f'Imported object unavailable: {mod}')
            if found.is_relative_to(obj): continue
            for f in [found,Path(str(found)+'.server'),Path(str(found)+'.private')]:
                if f.is_file(): externals[str(f.relative_to(rt))]=f
        for rel in ['toolchain/bin/lean','toolchain/bin/leanchecker','toolchain/lib/lean/libleanshared.so',
                    'toolchain/lib/lean/libleanshared_1.so','toolchain/lib/lean/libleanshared_2.so','compat/app_path.so']:
            f=rt/rel
            if f.exists(): externals[rel]=f
        hashed=[]
        for rel,f in sorted(externals.items()):
            if rel not in entries: raise ValueError(f'Upstream object not in saved inventory: {rel}')
            actual=digest(f)
            if actual!=entries[rel]['sha256']: raise ValueError(f'Upstream object mismatch: {rel}')
            hashed.append({'path':rel,'sha256':actual,'bytes':f.stat().st_size})
        write_json(out/'dependency_artifacts.json',{'archived_manifest_sha256':digest(manifest_path),
            'scope':'Actually imported upstream olean parts and selected compiler binaries/shared libraries; hashes match saved runtime inventory, not an independent origin attestation.',
            'files':hashed})
        report['matched_upstream_artifacts']=len(hashed)
        report['imported_module_count_including_audit_tools']=len(imports)
        report['local_object_sha256']={str(p.relative_to(obj)):digest(p) for p in sorted(obj.rglob('*.olean'))}
        after=source_pins();report['input_sha256_after']=after
        if before!=after: raise ValueError('Inputs changed during verification')
        report['all_inputs_unchanged']=True
        report['status']='PASS'
    except Exception as exc:
        report['status']='FAIL';report['failure']=f'{type(exc).__name__}: {exc}'
        report['input_sha256_after']=source_pins()
        print(report['failure'],file=sys.stderr,flush=True)
    report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    report['total_seconds']=time.monotonic()-START
    report['interpretation']='Actual Lean compilation and local same-kernel replay. Pinned dependencies reused. This does not certify the entire source book, host runtime semantics, model truth, or independent mathematical review.'
    write_json(out/'report.json',report)
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':
    START=time.monotonic()
    raise SystemExit(main())
