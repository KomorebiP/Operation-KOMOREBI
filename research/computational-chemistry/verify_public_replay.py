"""Verify the unpacked validated replay with Python's standard library."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path,PurePosixPath
import re

ROOT=Path(__file__).resolve().parent


def safe(name):
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:raise ValueError('Unsafe path: '+name)
    target=(ROOT/name).resolve()
    if not target.is_relative_to(ROOT) or not target.is_file():raise ValueError('Missing or escaped file: '+name)
    return target


def sha(name):return hashlib.sha256(safe(name).read_bytes()).hexdigest()


def main():
    contents=json.loads(safe('BUNDLE_CONTENTS.json').read_text());expected=set(contents['files'])-{'VALIDATION_SHA256SUMS'}
    indexed={}
    for line in safe('VALIDATION_SHA256SUMS').read_text().splitlines():
        match=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
        if not match or match[2] in indexed:raise ValueError('Invalid checksum index')
        indexed[match[2]]=match[1]
    assert set(indexed)==expected,'Delivered-file coverage mismatch'
    for name,value in indexed.items():assert sha(name)==value,name
    records=[]
    for folder in ['validation/exact-001','validation/molecular-001','validation/extensions-001']:
        manifest=json.loads(safe(folder+'/manifest.json').read_text())
        assert manifest['schema_version']==2 and manifest['run']['status']=='completed'
        assert manifest['command'][0]=='python','Unexpected executable locator'
        inputs=manifest['input_artifacts'];assert set(manifest['execution_artifacts'])=={x['path'] for x in inputs}
        for item in inputs:assert item['sha256']==item['sha256_after']==sha(item['path']),item['path']
        for item in manifest['outputs']:assert item['sha256']==sha(item['path']),item['path']
        assert set(manifest['declared_results'])=={x['path'] for x in manifest['outputs'] if x['kind']=='result'}
        records.append(folder)
    exact=json.loads(safe('validation/exact-001/checks.json').read_text());extensions=json.loads(safe('validation/extensions-001/checks.json').read_text())
    qual=json.loads(safe('validation/molecular-001/qualification.json').read_text())
    molecular=json.loads(safe('validation/molecular-001/molecular_certificate.json').read_text());toy=json.loads(safe('validation/exact-001/example_certificate.json').read_text())
    assert exact['status']=='passed' and exact['check_count']==82 and extensions['status']=='passed'
    assert qual['status']=='passed' and qual['projection_equal_exactly'] and molecular['all_compatible_positive_integral']
    assert qual['fixture_sha256']==sha('chemistry_checkpoint/molecular_fixtures/h10_1.4.npz')
    assert molecular['input_sha256']==sha('validation/molecular-001/molecular_cache.json')
    assert toy['input_sha256']==sha('chemistry_stage14/example_cache.json')
    assert Fraction(toy['response_radius_rational_upper'])<Fraction(exact['pi_scaled_ldos_gap'])
    radius=Fraction(molecular['response_radius_rational_upper'])
    assert Fraction(qual['response_error_squared_exact'])<=radius**2
    assert Fraction(qual['action_error_squared_exact'])<=Fraction(qual['action_error_radius_rational_upper'])**2
    assert Fraction(qual['operator_error_squared_exact'])<=Fraction(molecular['operator_radius_squared_upper'])
    joint=extensions['combined_example'];assert Fraction(joint['response_error_squared_exact'])<=Fraction(joint['radius_rational_upper'])**2
    print(json.dumps({'status':'passed','delivered_files_checked':len(indexed),'manifests_checked':len(records),'original_exact_checks':exact['check_count'],
        'extension_checks':extensions['check_count'],'extension_aggregated_cases':extensions['aggregated_cases'],
        'scope':'Hashes, completed-run/input/output provenance and saved exact inequalities; not a new execution or an independent mathematical proof'},indent=2))


if __name__=='__main__':main()
