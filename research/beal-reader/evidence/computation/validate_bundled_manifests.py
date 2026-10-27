#!/usr/bin/env python3
"""Validate portable run provenance against only the distributed input closure.

Archive mode observations are also schema checked. Their original excluded ZIP
is needed to repeat full input hash validation. A failed wrapper record is not
changed to a success record by validation.
"""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from validate_manifest import validate

root=Path('.').resolve();base=root/'evidence/computation';results=[]
for path in sorted(base.glob('*/manifest.json')):
    record=json.loads(path.read_text())
    archival=path.parent.name.startswith('block') and path.parent.name.endswith('-run')
    errors=validate(record,root=None if archival else root)
    results.append({'path':path.relative_to(root).as_posix(),'archival_original_archive_required_for_full_root_check':archival,
                    'run_status':record['run']['status'],'schema_and_available_root_validation_passed':not errors,'errors':errors})
report={'status':'PASS' if not any(item['errors'] for item in results) else 'FAIL','records':results,
        'note':'Schema validation is not mathematical verification. Original failed run statuses are retained.'}
(base/'MANIFEST_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],len(results),'records')
raise SystemExit(0 if report['status']=='PASS' else 1)
