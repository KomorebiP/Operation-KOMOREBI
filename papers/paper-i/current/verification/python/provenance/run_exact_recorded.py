from pathlib import Path
import shutil,subprocess,sys
root=Path(__file__).resolve().parent
out=root/'recorded_96/artifact'
(out/'visual_checks').mkdir(parents=True)
(out/'visual_model_sources').mkdir()
shutil.copy2(root/'python-examples/visual_checks/verify_examples.py',out/'visual_checks/verify_examples.py')
shutil.copy2(root/'python-examples/visual_model_sources/models.py',out/'visual_model_sources/models.py')
raise SystemExit(subprocess.run([sys.executable,str(out/'visual_checks/verify_examples.py')]).returncode)
