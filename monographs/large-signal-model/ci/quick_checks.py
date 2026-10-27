#!/usr/bin/env python3
"""Read-only packaging, source-index and metadata checks. No Lean is run."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path
from verify_frozen_lean import verify_manifest

HERE=Path(__file__).resolve().parent
CHECKS=['scripts/build_inventory.py','scripts/check_metadata.py',
        'scripts/test_source_scan.py','scripts/test_negative_control_classifier.py']
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=Path('Lean'))
    ap.add_argument('--baseline',type=Path,default=HERE/'frozen_lean_release.json')
    args=ap.parse_args();project=args.project.resolve()
    baseline=json.loads(args.baseline.read_text())
    integrity=verify_manifest(project,baseline['manifest_sha256'])
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    for script in CHECKS:
        subprocess.run([sys.executable,str(project/script)],cwd=project,env=env,check=True)
    # Check again so helper execution cannot silently replace frozen evidence.
    verify_manifest(project,baseline['manifest_sha256'])
    print(json.dumps({'kind':'quick source and packaging checks','passed':True,
      'payload_integrity':integrity,'helper_checks':CHECKS,'fresh_lean_execution':False},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
