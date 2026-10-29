"""Compare each runnable demonstration with its documented expected output."""
from pathlib import Path
import re
import subprocess
import sys


def main():
    root=Path(__file__).resolve().parents[1]
    for name, page in [('packets','PACKETS'),('refinement','REFINEMENT'),('recovery','RECOVERY')]:
        text=(root/('docs/demonstrations/'+page+'.md')).read_text(encoding='utf-8')
        expected=re.search(r'<!-- expected-output -->\s*```text\n(.*?)\n```',text,re.S)
        if not expected: raise ValueError('Missing expected output in '+page)
        run=subprocess.run([sys.executable,'-B',str(root/'examples/komorebi_demonstrations.py'),name],
                           check=True,capture_output=True,text=True)
        if run.stdout != expected[1]+'\n':
            raise AssertionError('Documented output differs for '+name+'\n'+run.stdout)
    print('PASS: 3 demonstrations and their documented output')


if __name__ == '__main__':
    main()
