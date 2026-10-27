from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.run([sys.executable,str(ROOT/'scripts/build_pdfs.py')]+sys.argv[1:]).returncode)
