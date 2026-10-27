"""Finalize the complete frozen census after the scan writes it.
Author: Komorebi P.
"""
from pathlib import Path
import gc
import shutil
import subprocess
import sys
import time
import engine


def main():
    root = Path(__file__).resolve().parent
    path = root/'results/final_legacy_census.json'
    last_size = None
    stable = 0
    while True:
        if path.exists():
            size = path.stat().st_size
            stable = stable + 1 if size == last_size else 0
            last_size = size
            if stable >= 2:
                try:
                    census = engine.read(path)
                    engine.verify(census)
                    if len(census['records']) == 1000:
                        break
                except (ValueError, OSError):
                    pass
        time.sleep(5)
    del census
    gc.collect()
    shutil.copyfile(path, root/'results/legacy_census.json')
    print('Complete census verified; freezing policies.', flush=True)
    subprocess.run([sys.executable, '-u', str(root/'finish_run.py')], check=True)
    print('Scoring complete; verifying the frozen release.', flush=True)
    subprocess.run([sys.executable, str(root/'validate.py'), '--output', str(root/'results/validation.json')], check=True)
    subprocess.run([sys.executable, str(root/'create_report.py')], check=True)
    print('Validation and final report complete.', flush=True)


if __name__ == '__main__':
    main()
