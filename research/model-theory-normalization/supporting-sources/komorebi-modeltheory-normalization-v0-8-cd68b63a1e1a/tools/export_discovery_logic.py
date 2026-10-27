#!/usr/bin/env python3
"""Export formulas and a full untrusted Lean instance from an expected source."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from matrix_logic import compile_artifact,emit_lean

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('certificate',type=Path)
    p.add_argument('--output',required=True,type=Path);p.add_argument('--namespace',required=True)
    a=p.parse_args();s=json.loads(a.source.read_text());c=json.loads(a.certificate.read_text())
    artifact=compile_artifact(s,c);text=emit_lean(s,c,a.namespace)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    a.output.with_suffix('.logic.json').write_text(json.dumps(artifact,indent=2)+'\n')
    print(json.dumps({'status':'EXPORTED_NOT_YET_LEAN_CHECKED','test_count':artifact['test_count'],
      'source_enumeration':False,'lean_file':str(a.output)}))
if __name__=='__main__':main()
