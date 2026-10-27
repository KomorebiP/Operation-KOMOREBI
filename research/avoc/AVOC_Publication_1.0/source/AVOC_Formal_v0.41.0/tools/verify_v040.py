#!/usr/bin/env python3
"""Prepare a clean v0.40 build, index its graph, or audit every inventoried theorem."""
import argparse, json, re, shutil, subprocess, sys
from release_common_v040 import ROOT, RD, build_graph, kit_path, release_lock, sha, write_json, build_record_errors

def audit_summary(text, expected):
    dependencies = set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]', text, re.S):
        dependencies.update(s.strip() for s in block.split(',') if s.strip())
    names = re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)", text, re.M)
    expected_names = {record['qualified_name'] for record in expected}; allowed={'propext','Classical.choice','Quot.sound'}
    return dict(passed=not(dependencies-allowed) and set(names)==expected_names and len(names)==len(set(names)),
                reports=len(names), unique_reports=len(set(names)), expected=len(expected),
                missing=sorted(expected_names-set(names)), extra=sorted(set(names)-expected_names),
                duplicates=len(names)-len(set(names)), axiom_union=sorted(dependencies),
                unexpected=sorted(dependencies-allowed), allowed_only=not bool(dependencies-allowed))

def main():
    parser=argparse.ArgumentParser(description=__doc__); actions=parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--prepare', action='store_true'); actions.add_argument('--index', action='store_true'); actions.add_argument('--audit', action='store_true')
    parser.add_argument('--seconds', type=int, default=600); args=parser.parse_args()
    with release_lock():
        if args.prepare or args.index:
            kit=kit_path(); pins=json.loads((ROOT/'lake-manifest.json').read_text())['packages']
            if len(pins)!=9 or len({p['name'] for p in pins})!=9: raise RuntimeError('Expected exactly nine distinct package pins')
            checks=[]
            for pin in pins:
                directory=kit/'workspace/.lake/packages'/pin['name']
                actual=subprocess.check_output(['git','-c',f'safe.directory={directory}','-C',str(directory),'rev-parse','HEAD'],text=True).strip()
                checks.append(dict(name=pin['name'],expected=pin['rev'],actual=actual,passed=actual==pin['rev']))
            lean_version=subprocess.check_output([str(kit/'toolchain/bin/lean'),'--version'],text=True).strip()
            version=(ROOT/'lean-toolchain').read_text().strip().split(':')[-1].removeprefix('v')
            report=dict(passed=all(c['passed'] for c in checks) and ('version '+version+',') in lean_version,
                        pins=checks, lean_version=lean_version, lean_executable_sha256=sha(kit/'toolchain/bin/lean'),
                        manifest_sha256=sha(ROOT/'lake-manifest.json'),toolchain_sha256=sha(ROOT/'lean-toolchain'))
            write_json(RD/'dependency_pins.json',report)
            if not report['passed']: raise RuntimeError('Dependency/toolchain pin mismatch')
            order,_=build_graph(); write_json(RD/'build_order.json',order)
            if args.prepare: shutil.rmtree(ROOT/'.lake/build',ignore_errors=True)
            (ROOT/'.lake/build/lib/lean').mkdir(parents=True,exist_ok=True)
            print(('Prepared clean local rebuild:' if args.prepare else 'Indexed local targets:'),len(order))
            return 0
        log='results/v0.40.0/full_axiom_audit.log'
        result=subprocess.run([sys.executable,str(ROOT/'tools/lean_one_v040.py'),'AVOC/FullAudit.lean','--no-output','--seconds',str(args.seconds),'--log',log],stdout=subprocess.DEVNULL)
        if result.returncode:
            print((ROOT/log).read_text(errors='replace')[-6000:]); return result.returncode
        expected=json.loads((RD/'declaration_inventory.json').read_text()); report=audit_summary((ROOT/log).read_text(),expected)
        record=json.loads((ROOT/log).with_suffix('.json').read_text()); errors=build_record_errors('AVOC/FullAudit.lean',record,output=False)
        report.update(passed=report['passed'] and not errors,record_errors=errors,
                      inventory_sha256=sha(RD/'declaration_inventory.json'),audit_source_sha256=sha(ROOT/'AVOC/FullAudit.lean'),
                      audit_record_sha256=sha((ROOT/log).with_suffix('.json')))
        write_json(RD/'axiom_audit_summary.json',report); print(json.dumps(report,indent=2))
        return 0 if report['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
