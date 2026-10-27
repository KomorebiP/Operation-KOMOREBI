#!/usr/bin/env python3
"""Replay the owning-module audit from relocated delivered Paper X artifacts.

No production source compilation occurs here. The preserved build receipt is
authenticated, its source-manifest path is rebound in an external working copy,
and every delivered source/object/private artifact is checked against its pins.
The default then performs a fresh 122-owner audit and exact target-type capture.
--preflight-only performs binding/runtime checks, with zero production census.
"""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'tooling'))
from audit_engine import AuditError, parse_json, safe_relative, save_json, sha256, utc, execute, require_success
from runtime_adapter import runtime_env

def inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents

def load_runner():
    spec = importlib.util.spec_from_file_location('paper_x_production_runner', HERE/'run_production_audit.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def prepare(args) -> tuple[dict,list[str]]:
    replay, runtime, work = args.production_replay.resolve(), args.runtime.resolve(), args.work.resolve()
    if inside(work,replay) or inside(work,HERE):
        raise AuditError('Use an external work directory; delivered files stay immutable')
    if work.exists():
        raise AuditError('Choose a new external work directory')
    work.mkdir(parents=True)
    report = {'schema':'paper_x.portable_owned_audit_preflight.v1','status':'RUNNING',
        'started_utc':utc(),'production_replay':str(replay),'runtime':str(runtime),
        'wrapper_sha256':sha256(Path(__file__)), 'fresh_production_census_performed':False,
        'source_compilation_performed':False}
    save = lambda:save_json(work/'PREFLIGHT.json',report)
    save()
    try:
        pins = parse_json((HERE/'REPLAY_INPUT_PINS.json').read_text())
        for rel,digest in pins['production_replay_files'].items():
            path=replay/safe_relative(rel)
            if path.is_symlink() or not path.is_file() or sha256(path)!=digest:
                raise AuditError('Delivered replay input changed: '+rel)
        target_file=HERE/'contract_review/AUDIT_TARGETS.json'
        if sha256(target_file)!=pins['target_contract_sha256']:
            raise AuditError('Explicit target contract changed')
        manifest_path=replay/'PUBLICATION_SOURCE_MANIFEST.json'
        manifest=parse_json(manifest_path.read_text())
        if manifest.get('count')!=pins['module_count'] or manifest.get('missing')!=[]:
            raise AuditError('Incomplete delivered production source selection')
        modules=[]
        for row in manifest['modules']:
            relative=safe_relative(row['source_relative'])
            if relative.parts[0]!='publication_sources':
                raise AuditError('Source reference outside delivered publication_sources')
            source=replay/relative
            if not inside(source.resolve(),(replay/'publication_sources').resolve()):
                raise AuditError('Source escapes delivered source root')
            modules.append({'module':row['module'],'source':str(source),
                            'source_sha256':row['source_sha256']})
        targets=parse_json(target_file.read_text())
        if len(targets)!=pins['target_count']:
            raise AuditError('Explicit target count changed')
        inputs=work/'inputs';inputs.mkdir()
        selection={'schema':'paper_x.production_selection.v1',
            'scope':pins['scope'],'production_manifest':str(manifest_path),
            'production_manifest_sha256':sha256(manifest_path),
            'modules':modules,'targets':targets}
        selection_path=inputs/'PRODUCTION_SELECTION.json';save_json(selection_path,selection)
        original_receipt_path=replay/'build_A1/BUILD_REPORT.json'
        raw=original_receipt_path.read_bytes()
        (inputs/'ORIGINAL_BUILD_REPORT.json').write_bytes(raw)
        receipt=parse_json(raw.decode('utf-8'))
        adapted=copy.deepcopy(receipt)
        adapted['source_manifest']=str(manifest_path)
        adapted['relocation_adapter']={
            'schema':'paper_x.compilation_receipt_path_rebinding.v1',
            'original_as_executed_report_sha256':sha256(original_receipt_path),
            'original_as_executed_report':str(original_receipt_path),
            'only_rebound_original_field':'source_manifest',
            'note':'This is a location adapter for the preserved successful compile, not a new compilation receipt.'}
        receipt_path=inputs/'RELOCATED_BUILD_REPORT.json';save_json(receipt_path,adapted)
        module=load_runner()
        validated=module.selection(selection_path)
        object_root=replay/'build_A1/objects'
        observed=module.pins(validated,object_root)
        module.verify_compilation_receipt(adapted,receipt_path,validated,observed,replay/'build_A1')
        artifacts=module.verify_artifact_inventory(object_root,replay/'build_A1/ALL_ARTIFACTS.json')
        if len(observed)!=pins['module_count'] or len(artifacts)!=pins['artifact_count']:
            raise AuditError('Delivered source/artifact count mismatch')
        dependencies=[]; package_paths=[]
        for name,expected in pins['dependency_revisions'].items():
            package=runtime/'workspace/.lake/packages'/name
            p=subprocess.run(['git','-C',str(package),'rev-parse','HEAD'],
                             capture_output=True,text=True,check=False)
            if p.returncode!=0 or p.stdout.strip()!=expected:
                raise AuditError('Pinned runtime dependency mismatch: '+name)
            lib=package/'.lake/build/lib/lean'
            dependencies.append({'name':name,'revision':expected,'compiled_root':str(lib) if lib.is_dir() else None})
            if lib.is_dir():package_paths.append(lib)
            elif name!='Cli':raise AuditError('Missing compiled dependency root: '+name)
        if sha256(runtime/'workspace/lake-manifest.json')!=pins['runtime_lake_manifest_sha256']:
            raise AuditError('Portable runtime dependency manifest mismatch')
        lean,env=runtime_env(runtime,[object_root],packages=package_paths)
        result=execute([str(lean),'--version'],work,env,60,work/'compiler_version.log')
        require_success(result)
        version=(work/'compiler_version.log').read_text().strip()
        if version!=pins['lean_version']:raise AuditError('Pinned Lean version string mismatch')
        argv=[sys.executable,'-B',str(HERE/'run_production_audit.py'),
            '--selection',str(selection_path),'--compile-receipt',str(receipt_path),
            '--compile-output-root',str(replay/'build_A1'),
            '--artifact-inventory',str(replay/'build_A1/ALL_ARTIFACTS.json'),
            '--objects',str(object_root),'--runtime',str(runtime),
            '--batch-size','122','--work',str(work/'audit')]
        for path in package_paths:argv.extend(['--package-path',str(path)])
        report.update(status='PASS',finished_utc=utc(),sources_bound=len(observed),
            generated_artifacts_bound=len(artifacts),explicit_targets=len(targets),
            runtime_command=result,dependencies=dependencies,
            selected_source_root=str(replay/'publication_sources'),selected_object_root=str(object_root),
            old_absolute_source_paths_required=False,
            location_adapter_receipt=str(receipt_path),selection=str(selection_path),
            replay_argv=argv,compiler_memory_limit_mb=6144,
            limitations=['The dependency cache is authenticated to the external portable-kit pins; it is not cold rebuilt.',
                        'Source/object binding preflight is not a fresh declaration census or a source compilation.'])
        save();return report,argv
    except BaseException as error:
        report.update(status='FAILED',finished_utc=utc(),error=f'{type(error).__name__}: {error}')
        save();raise

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--production-replay',type=Path,required=True,
                        help='Delivered production_replay directory; relative paths work.')
    parser.add_argument('--runtime',type=Path,required=True,help='Extracted pinned external portable Lean kit.')
    parser.add_argument('--work',type=Path,required=True,help='New directory outside the delivered package.')
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args()
    try:
        preflight,argv=prepare(args)
        if args.preflight_only:
            print(json.dumps({'status':'PASS','scope':'portable binding/runtime preflight only',
                              'production_modules_audited':0,'sources_bound':preflight['sources_bound'],
                              'artifacts_bound':preflight['generated_artifacts_bound']}));sys.exit(0)
        code=subprocess.call(argv)
        print(json.dumps({'preflight':'PASS','audit_exit':code,'audit_report':str(args.work.resolve()/'audit/REPORT.json')}))
        sys.exit(code)
    except Exception as error:
        print('FAILED:',error,file=sys.stderr);sys.exit(1)
