from pathlib import Path
import json, sys, time, unittest, platform
ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / 'engine'
sys.path.insert(0, str(ENGINE))
GROUPS = {
 'structural': ['test_streaming_skat','test_approximate_lightcone','test_budget_scheduler','test_residual_completion','test_residual_trace_cap','test_spectral_tail_bridge','test_realistic_skat'],
 'signed_noncentral': ['test_signed_engine','test_noncentral_engine'],
 'interval': ['test_interval_kcos'],
 'accuracy': ['test_accuracy_driven'],
 'verified_spectrum': ['test_verified_spectrum'],
 'directed_contract': ['test_directed_contract'],
}
name, output = sys.argv[1:]
modules=GROUPS[name]
start=time.perf_counter()
suite=unittest.defaultTestLoader.loadTestsFromNames(modules)
result=unittest.TextTestRunner(verbosity=2).run(suite)
record={'group':name,'modules':modules,'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'successful':result.wasSuccessful(),'elapsed_seconds':time.perf_counter()-start,'python':sys.version}
Path(output).write_text(json.dumps(record,indent=2)+'\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
