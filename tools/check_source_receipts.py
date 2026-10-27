#!/usr/bin/env python3
"""Verify every selected source receipt against a committed Git tree.

This reads Git objects, so it works with sparse checkouts and keeps exact path
case and modes. It checks content-addressed source identity, not a new SHA-256
read of every source blob, mathematical correctness, or Lean execution.
"""
from __future__ import annotations
import argparse
import collections
import json
import subprocess
from pathlib import Path
from import_source_collection import ImportFailure, _fingerprint, require, safe_relative, tree_digest


def git_tree(root, git, revision):
    tree={}
    for row in subprocess.check_output([git,'ls-tree','-rz',revision],cwd=root).split(b'\0'):
        if row:
            meta,path=row.split(b'\t',1); mode,kind,sha=meta.decode().split()
            if kind=='blob': tree[path.decode('utf-8')]={'mode':mode,'sha':sha}
    return tree


def read_blobs(root, git, objects):
    """Read exactly the requested objects without relying on checkout conversion."""
    raw=subprocess.check_output([git,'cat-file','--batch'],cwd=root,
        input=('\n'.join(objects)+'\n').encode('ascii'))
    offset=0; result=[]
    for sha in objects:
        end=raw.index(b'\n',offset); header=raw[offset:end].split()
        require(len(header)==3 and header[0].decode()==sha and header[1]==b'blob', 'Missing or invalid Git blob: '+sha)
        size=int(header[2]);offset=end+1
        body=raw[offset:offset+size];offset+=size
        require(len(body)==size and raw[offset:offset+1]==b'\n','Truncated Git blob: '+sha)
        offset+=1;result.append(body)
    require(offset==len(raw),'Unexpected Git batch output')
    return result


def check_records(config, state, receipts, tree):
    components=config['components'];ids=[c['id'] for c in components]
    require(len(ids)==len(set(ids)), 'Duplicate component ID')
    rows=state['components'];state_ids=[r['id'] for r in rows]
    require(len(state_ids)==len(set(state_ids)) and set(state_ids)==set(ids),'Availability/component ID mismatch')
    require(set(receipts)==set(ids),'Receipt/component ID mismatch')
    by_id={r['id']:r for r in rows};owned={};counts=collections.Counter();groups=collections.Counter()
    for c in components:
        identifier=c['id'];destination=safe_relative(c['destination']);r=receipts[identifier];s=by_id[identifier]
        require(r['component']==identifier and r['destination']==destination,'Receipt identity mismatch: '+identifier)
        require(r['component_sha256']==_fingerprint(c),'Receipt configuration binding mismatch: '+identifier)
        files=r['files'];names=[f['path'] for f in files]
        require(len(names)==len(set(names)),'Duplicate receipt path: '+identifier)
        require(len(files)==r['file_count']==c['expected']['file_count'],'File count mismatch: '+identifier)
        digest=tree_digest(files)
        require(digest==r['tree_sha256']==c['expected']['tree_sha256'],'Aggregate digest mismatch: '+identifier)
        for f in files:
            path=destination+'/'+safe_relative(f['path'])
            require(tree.get(path)=={'mode':f['mode'],'sha':f['git_blob_sha1']},'Published source mismatch: '+path)
            require(path not in owned or owned[path]==f['sha256'],'Conflicting ownership digest: '+path)
            owned[path]=f['sha256']
        require(s['destination']==destination and s['available'] is True and s['disposition']=='imported', 'Availability mismatch: '+identifier)
        require(s['file_count']==len(files) and s['tree_sha256']==digest,'Availability digest/count mismatch: '+identifier)
        require(s['role'] in ('primary','supporting'),'Unknown component role: '+identifier)
        counts[s['role']]+=1
        if s['role']=='primary':groups[destination.split('/')[0]]+=1
    expected={'selected_components':len(ids),'available_components':len(ids),
        'selected_primary_components':counts['primary'],'available_primary_components':counts['primary'],
        'selected_supporting_components':counts['supporting'],'available_supporting_components':counts['supporting'],
        'unique_source_files':len(owned),'pending_components':0,'primary_components_by_group':dict(sorted(groups.items()))}
    for key,value in expected.items():
        require(state['totals'].get(key)==value,'Availability total mismatch: '+key)
    return {'status':'PASS','components':len(ids),'primary_components':counts['primary'],
        'supporting_collections':counts['supporting'],'owned_source_files':len(owned),'repository_files':len(tree),
        'basis':'Receipt/configuration bindings, aggregate SHA-256 record digests, and exact committed paths, Git blob SHA-1 values and modes.',
        'new_sha256_read_of_all_source_blobs':False,'new_lean_execution':False,'new_mathematical_proof_audit':False}


def check(root, git='git', revision='HEAD'):
    revision=subprocess.check_output([git,'rev-parse','--verify',revision+'^{commit}'],cwd=root,text=True).strip()
    tree=git_tree(root,git,revision)
    names=['manifests/source-collection.json','manifests/source-components.json']
    config,state=[json.loads(b) for b in read_blobs(root,git,[tree[p]['sha'] for p in names])]
    ids=[c['id'] for c in config['components']]
    paths=['manifests/source-imports/'+safe_relative(i)+'.json' for i in ids]
    receipts=dict(zip(ids,[json.loads(b) for b in read_blobs(root,git,[tree[p]['sha'] for p in paths])]))
    return {'source_commit':revision,**check_records(config,state,receipts,tree)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--git',default='git');ap.add_argument('--revision',default='HEAD')
    args=ap.parse_args()
    try:result=check(args.root.resolve(),args.git,args.revision)
    except (ImportFailure,OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)}));return 1
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
