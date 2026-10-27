"""Local version1 computation-evidence validation, not the full Mathbox CLI.
Checks the consulted v1 required fields, substantive values, paths and output hashes.
Per-run records separately retain training input/source hashes and replay provenance.
"""
from pathlib import Path
import argparse,json,hashlib,math,re
REQ={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
def validate(x,root):
    assert REQ<=x.keys();assert x['schema_version']==1
    assert all(isinstance(x[k],str) and x[k].strip() for k in ['claim_id','result'])
    assert x['command'];assert isinstance(x['repository']['dirty'],bool)
    m=x['mathematics'];assert {'assertion_tested','coefficient_domain','conventions','inputs','bounds','non_claims'}<=m.keys()
    assert all(m[k] for k in ['assertion_tested','coefficient_domain','conventions','bounds','non_claims'])
    assert isinstance(m['inputs'],list);assert x['environment']['software']
    for v in x['environment']['software']:assert v['name'] and v['version']
    r=x['randomness'];assert isinstance(r['used'],bool)
    if r['used']:assert r['generator'] and r['seed'] is not None
    r=x['run'];assert r['started_at'] and type(r['exit_status']) is int;assert math.isfinite(r['runtime_seconds']) and r['runtime_seconds']>=0
    assert x['outputs'] and isinstance(x['checks'],list) and isinstance(x['residual_risks'],list)
    for out in x['outputs']:
        rel=Path(out['path']);assert not rel.is_absolute() and '..' not in rel.parts
        p=(root/rel).resolve();assert p.is_relative_to(root.resolve()) and p.is_file()
        assert re.fullmatch('[0-9a-f]{64}',out['sha256']);assert hashlib.sha256(p.read_bytes()).hexdigest()==out['sha256'],str(rel)
    return {'status':'PASS','validator':'local version1 structure/path/hash checker','outputs_verified':len(x['outputs']),
        'legacy_limits':['v1 itself does not require input hashes or machine-enforced per-command resource caps','full canonical plugin CLI not executed; supplementary run records retain source/input hashes']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('--root',type=Path,required=True);a=p.parse_args();print(json.dumps(validate(json.loads(a.manifest.read_text()),a.root),indent=2))
