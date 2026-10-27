from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'verify_ledger.py')],check=True,cwd=root)
shutil.copyfile(root/'VERIFICATION.json',root/'certified_run/verification.json')
