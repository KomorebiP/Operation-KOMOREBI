from pathlib import Path
import shutil,subprocess,sys
root=Path(__file__).resolve().parent
out=root/'recorded_companion/artifact'
shutil.copytree(root/'python-companion/code',out/'code',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(root/'python-companion/scripts',out/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
raise SystemExit(subprocess.run([sys.executable,str(out/'scripts/verify_python.py'),'--out',str(out/'verification')]).returncode)
