"""Run the declared finite atlas checks and emit a machine-readable result."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import unittest

from sequence_atlas import ROOT, catalogue
from sequence_atlas_index import connection_graph

if __name__ == '__main__':
    # Node's test reporter emits Unicode even when launched from legacy Windows pipes.
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tools'),pattern='test_sequence_atlas.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    import os
    env=dict(os.environ,PYTHON=sys.executable)
    browser_core=subprocess.run([args.node,'--test','tools/test_sequence_atlas.mjs','tools/test_sequence_atlas_search.mjs','tools/test_sequence_atlas_discovery.mjs','tools/test_sequence_atlas_interface.mjs','tools/test_sequence_atlas_study.mjs','tools/test_sequence_atlas_directory.mjs'],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
    print(browser_core.stdout)
    print(browser_core.stderr,file=sys.stderr)
    graph=connection_graph(catalogue())
    report=dict(status='passed' if result.wasSuccessful() and browser_core.returncode==0 else 'failed',
        python_tests=result.testsRun,python_errors=len(result.errors),python_failures=len(result.failures),
        browser_core_exit=browser_core.returncode,entries=len(catalogue()),
        assertion_tested='Exact catalogue terms, bounded transforms, index and normalization maps, 1482 study windows, and all seven existing directed connections with 84 exact comparisons agree with independent implementations over the declared ranges. The index preserves all 38 identifiers and 21 N/r cells.',
        bounds=dict(reciprocal_N=[2,8],reciprocal_powers=[1,3],rational_oracle_terms=16,python_browser_terms=64,partition_recurrence_terms=32,second_difference_terms=64,successive_modular_fixture_terms=3,entries=len(catalogue()),entry_program_terms=16,retained_original_terms=1664,binomial_round_trip_terms=64,partition_cross_implementation_terms=100,computed_connection_terms=12,new_oeis_prefix_terms=12,reading_map_rows=228,normalized_reciprocal_rows=126),
        study_bounds=dict(windows=1482,entries=38,transforms=11,moduli=[2,7,128],windows_start_count=[[0,12],[9,16],[52,12]],backward_difference_orders=[0,4],constant_difference_minimum_defined=4),
        directory_bounds=dict(entries=len(catalogue()),family_cells=21,directed_edges=len(graph['edges']),distinct_comparisons=sum(len(edge['rows']) for edge in graph['edges']),rendered_evidence_rows=2*sum(len(edge['rows']) for edge in graph['edges'])),
        non_claims=['No new sequence or formula novelty','No global period or asymptotic result','No new formal or independent mathematical review','Constant finite differences do not prove infinite polynomial identities'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if report['status']=='passed' else 1)
