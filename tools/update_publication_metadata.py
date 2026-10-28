#!/usr/bin/env python3
"""Bind public publication metadata to a verified source-component index.

Writes a reviewable overlay only. Does not commit, push, download, or execute
research code. The input index must have validated component and receipt bindings for the
explicitly supplied source commit. This helper checks metadata consistency;
it does not independently hash the source files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

REPOSITORY='KomorebiP/Operation-KOMOREBI'
HISTORY_PATH='manifests/history/release-candidate-2026-10-09.json'
CURRENT_PATH='manifests/release-candidate.json'
INDEX_PATH='manifests/source-components.json'
LIBRARIES=[
    {'repository':'komorebi-math','repository_url':'https://github.com/KomorebiP/komorebi-math',
     'remote_commit':'a3aa04ac18a523f30c50c7f5dba709f88e904eff','remote_commit_confirmed':True,
     'remote_observation_date':'2026-10-28','observed_package_version':'1.0.0',
     'release_channel':'beta','work_in_progress':True,'license':'MIT',
     'release_url':'https://github.com/KomorebiP/komorebi-math/releases/tag/beta-2026-10-27',
     'release_commit':'5f33ded5a8238222e5beda6e5cb701b54fc3dbdb',
     'release_prerelease':True,'release_asset_count':0,
     'qualification_scope':'The CPU release workflow passed all 18 jobs, including Linux and Windows source and installation checks on Python 3.11, 3.12, and 3.13. The Windows hardware wrapper passed its unavailable-backend rejection check. This is not a positive GPU hardware qualification.',
     'checks':[{'name':'CPU release qualification','run_id':40731941631,
                'head_sha':'a3aa04ac18a523f30c50c7f5dba709f88e904eff',
                'status':'completed','conclusion':'success',
                'url':'https://github.com/KomorebiP/komorebi-math/actions/runs/40731941631'}]},
    {'repository':'polyphase-float','repository_url':'https://github.com/KomorebiP/polyphase-float',
     'remote_commit':'64117c44738038381b8838f5f72a90745bfda87f','remote_commit_confirmed':True,
     'remote_observation_date':'2026-10-28','observed_package_version':'0.20.0',
     'release_channel':'beta','work_in_progress':True,'license':'LGPL-3.0-or-later',
     'release_url':'https://github.com/KomorebiP/polyphase-float/releases/tag/beta-2026-10-27',
     'release_commit':'a7f6e8652b11a37f2c3a5d5577f1d918a768f7d6',
     'release_prerelease':True,'release_asset_count':0,
     'qualification_scope':'The CI, ABI governance, and CodeQL workflows passed for this commit. Their configured checks and platforms define the tested scope.',
     'checks':[{'name':'CI','run_id':40731951615,
                'head_sha':'64117c44738038381b8838f5f72a90745bfda87f',
                'status':'completed','conclusion':'success',
                'url':'https://github.com/KomorebiP/polyphase-float/actions/runs/40731951615'},
               {'name':'ABI governance','run_id':40731951567,
                'head_sha':'64117c44738038381b8838f5f72a90745bfda87f',
                'status':'completed','conclusion':'success',
                'url':'https://github.com/KomorebiP/polyphase-float/actions/runs/40731951567'},
               {'name':'CodeQL','run_id':40731951229,
                'head_sha':'64117c44738038381b8838f5f72a90745bfda87f',
                'status':'completed','conclusion':'success',
                'url':'https://github.com/KomorebiP/polyphase-float/actions/runs/40731951229'}]}]


def require(condition,message):
    if not condition:raise ValueError(message)


def validate_library_records(records):
    """Check recorded passing runs, without querying GitHub or executing software."""
    require(len({r['repository'] for r in records})==len(records),'Duplicate library observation')
    for row in records:
        url='https://github.com/KomorebiP/'+row['repository']
        require(row['repository_url']==url,'Library URL does not match repository')
        for key in ('remote_commit','release_commit'):
            require(bool(re.fullmatch(r'[0-9a-f]{40}',row[key])),'Full library and release commits are required')
        require(row['checks'],'A checked revision needs a workflow record')
        for run in row['checks']:
            require(run['head_sha']==row['remote_commit'],'Workflow covers a different library revision')
            require(run['status']=='completed' and run['conclusion']=='success','Passing observation requires a completed successful run')
            require(run['url']==url+'/actions/runs/'+str(run['run_id']),'Workflow URL does not match repository and run')
    return records


def build_record(index_bytes,source_commit,history_bytes):
    validate_library_records(LIBRARIES)
    require(bool(re.fullmatch(r'[0-9a-f]{40}',source_commit)), 'A full verified source commit is required')
    index=json.loads(index_bytes)
    require(index.get('schema')==1,'Unsupported source-component index schema')
    require(index.get('source_revision')==source_commit,'Source index is bound to a different revision')
    require(index.get('source_verification_is_mathematical_replay') is False,
            'Source index must explicitly distinguish file verification from mathematical replay')
    components=index['components'];totals=index['totals']
    identifiers=[r['id'] for r in components]
    require(len(identifiers)==len(set(identifiers)),'Duplicate source-component identifiers')
    available=[r for r in components if r['available']]
    primary=[r for r in available if r['role']=='primary']
    supporting=[r for r in available if r['role']=='supporting']
    derived={'selected_components':len(components),'available_components':len(available),
             'available_primary_components':len(primary),'available_supporting_components':len(supporting),
             'selected_primary_components':sum(r['role']=='primary' for r in components),
             'selected_supporting_components':sum(r['role']=='supporting' for r in components),
             'pending_components':len(components)-len(available)}
    for key,value in derived.items():require(totals.get(key)==value,'Source index has inconsistent '+key)
    require(isinstance(totals.get('unique_source_files'),int) and totals['unique_source_files']>=0,
            'Missing unique source-file count')
    for row in available:
        require(row.get('disposition')=='imported' and row.get('receipt'), 'Available component lacks an import receipt')
        require(isinstance(row.get('file_count'),int) and row['file_count']>0,
                'Available component has no source-file count')
        require(bool(re.fullmatch(r'[0-9a-f]{64}',row.get('tree_sha256',''))),
                'Available component has no source-tree digest')
    return {
        'schema_version':2,'status':'PUBLIC_SOURCE_COLLECTION','public_release':True,
        'visibility':'public','as_of':index['as_of'],'author':'Komorebi P.',
        'repository':REPOSITORY,'repository_url':'https://github.com/'+REPOSITORY,
        'verified_source_commit':source_commit,
        'source_collection':{
            'component_index':INDEX_PATH,'component_index_sha256':hashlib.sha256(index_bytes).hexdigest(),
            'source_declarations':'manifests/source-collection.json','file_receipts':'manifests/source-imports/',
            'totals':totals,
            'all_selected_components_have_verified_receipts':totals['pending_components']==0,
            'availability_basis':index['availability_basis'],
            'counting_scope':'Components and distinct files in the declared source collection. These are publication units, not theorem totals or a claim that every research goal is complete.'},
        'library_revisions':LIBRARIES,
        'software_release_policy':{'release_channel':'beta','work_in_progress':True,
            'historical_release_labels':'Preserved as dated history; they do not override the current beta policy.'},
        'reuse_terms':{'collection_notice':'LICENSE.md','original_code':'MIT, subject to existing component grants and third-party terms',
            'original_writing_and_figures':'CC BY 4.0, subject to existing component grants and third-party terms',
            'historical_notices':'See the current collection notice for its treatment of older original-author restrictions.'},
        'verification':{'source_file_identity':'Established by the bound component index and its per-component file receipts.',
            'fresh_theorem_replay':False,'fresh_full_corpus_numerical_reproduction':False,
            'qualification':'Consult revision-specific component reports and docs/GITHUB_IMPORT_STATUS.md.',
            'scope':'Publication does not promote an open conjecture, conditional premise, uncompiled source, failed experiment, or unfinished empirical obligation.'},
        'historical_candidate':{'path':HISTORY_PATH,'sha256':hashlib.sha256(history_bytes).hexdigest(),
            'meaning':'Exact earlier private-candidate bytes, preserved as history rather than current publication status.'}}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,required=True)
    parser.add_argument('--source-components',type=Path)
    parser.add_argument('--source-commit',required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    args=parser.parse_args(argv)
    root=args.repo_root.resolve();output=args.output_root.resolve()
    index_path=args.source_components or root/INDEX_PATH
    index_bytes=index_path.read_bytes()
    history_source=root/HISTORY_PATH
    if history_source.exists():
        require(not history_source.is_symlink(),'Historical candidate must be a regular file')
        history_bytes=history_source.read_bytes()
    else:
        old=root/CURRENT_PATH
        require(not old.is_symlink(),'Candidate must be a regular file')
        history_bytes=old.read_bytes()
        require(json.loads(history_bytes).get('status')=='PRIVATE_LOCAL_CANDIDATE',
                'The historical candidate is absent and the current file is no longer the original private candidate')
    record=build_record(index_bytes,args.source_commit,history_bytes)
    for relative,data in [(HISTORY_PATH,history_bytes),
                          (CURRENT_PATH,(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))]:
        destination=output/relative
        require(not destination.is_symlink(),'Output must not be a symlink')
        if relative==HISTORY_PATH and destination.exists():
            require(destination.read_bytes()==data,'Refusing to replace different historical bytes')
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    print(json.dumps({'output_files':[HISTORY_PATH,CURRENT_PATH],
        'verified_source_commit':record['verified_source_commit'],
        'totals':record['source_collection']['totals'],
        'historical_sha256':record['historical_candidate']['sha256']},indent=2))
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,TypeError,KeyError) as exc:
        raise SystemExit('Publication metadata update failed: '+str(exc))
