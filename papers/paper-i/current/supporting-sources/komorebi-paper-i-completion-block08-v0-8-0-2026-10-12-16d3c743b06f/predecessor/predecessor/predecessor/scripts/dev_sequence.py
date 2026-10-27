from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parents[1]
for source,flag in [('source/extension/PaperICompletion5/CyclicGeometricCriterion.lean','--build'),('source/extension/PaperICompletion5.lean','--build'),('tests/GeometricBoundaryConsumers.lean','--test-build')]:
 subprocess.run([sys.executable,str(r/'scripts/dev_check.py'),str(r/source),flag],check=True)
print('DEV_SEQUENCE_PASS',flush=True)
