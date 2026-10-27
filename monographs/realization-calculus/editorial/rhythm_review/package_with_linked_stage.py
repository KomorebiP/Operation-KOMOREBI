#!/usr/bin/env python3
"""Run the unchanged publication gates with space-efficient, read-only staging.

Use after the source and review records have been sealed. The ZIP stores full
ordinary file bytes; hard links are only a temporary staging optimization.
"""
from pathlib import Path
import errno,os,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import package_publication as P

def main():
    original_copy=P.shutil.copy2
    counts={'linked':0,'copied':0}
    def stage_copy(source,target,*args,**kwargs):
        # The packager writes this generated record after selection.
        if Path(target).name=='package_selection.json':
            counts['copied']+=1
            return original_copy(source,target,*args,**kwargs)
        try:
            os.link(source,target)
            counts['linked']+=1
            return str(target)
        except OSError as error:
            if error.errno not in (errno.EXDEV,errno.EPERM,errno.EOPNOTSUPP):raise
            counts['copied']+=1
            return original_copy(source,target,*args,**kwargs)
    P.shutil.copy2=stage_copy
    try:P.main()
    finally:P.shutil.copy2=original_copy
    print('Temporary staging files:',counts)

if __name__=='__main__':main()
