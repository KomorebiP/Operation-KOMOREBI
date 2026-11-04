"""Construct an explicitly separate, hash-bound resource-cap repair candidate.

Never edits the retained publication master. The generated patch adds integer
validation and clamps the final support-scale refinement to its declared cap.
"""
import difflib, hashlib, importlib.util, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ENGINE=ROOT/'engine' if (ROOT/'engine').is_dir() else ROOT.parents[1]/'monographs/cos-method/engine'
sys.path.insert(0,str(ENGINE))
EXPECTED='b113179002cda9f5e6a66d88ff998a7241147535'

def candidate_text():
    raw=(ENGINE/'accuracy_driven.py').read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if actual!=EXPECTED:raise RuntimeError('Repair candidate requires the audited source revision')
    original=raw.decode()
    source=original.replace('import math\n','import math\nfrom decimal import Decimal, InvalidOperation\n',1)
    helper='''def _positive_integer_parameter(value, name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"{name} must be a finite positive integer") from error
    if not number.is_finite() or number <= 0 or number != number.to_integral_value():
        raise ValueError(f"{name} must be a finite positive integer")
    return int(number)


'''
    source=source.replace('def certified_positive_logsf(',helper+'def certified_positive_logsf(',1)
    before='''    K = int(initial_K)
    L = int(mp.mpf(initial_L))
    dps = int(initial_interval_dps)
'''
    after='''    K = _positive_integer_parameter(initial_K, "initial_K")
    L = _positive_integer_parameter(initial_L, "initial_L")
    dps = _positive_integer_parameter(initial_interval_dps, "initial_interval_dps")
    max_K = _positive_integer_parameter(max_K, "max_K")
    max_L = _positive_integer_parameter(max_L, "max_L")
    max_interval_dps = _positive_integer_parameter(max_interval_dps, "max_interval_dps")
    if K > max_K or L > max_L or dps > max_interval_dps:
        raise ValueError("initial resources must not exceed their corresponding caps")
'''
    assert source.count(before)==1 and source.count('            L += 2\n')==1
    source=source.replace(before,after,1).replace('            L += 2\n','            L = min(max_L, L + 2)\n',1)
    return original,source

def load_candidate():
    original,source=candidate_text()
    target=ROOT/'candidate';target.mkdir(exist_ok=True)
    path=target/'accuracy_driven.py';path.write_text(source)
    patch=''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),
        fromfile='a/monographs/cos-method/engine/accuracy_driven.py',tofile='b/monographs/cos-method/engine/accuracy_driven.py'))
    (ROOT/'controller_caps.patch').write_text(patch)
    spec=importlib.util.spec_from_file_location('kcos_resource_cap_candidate',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module

if __name__=='__main__':
    load_candidate();print('Created candidate/accuracy_driven.py and controller_caps.patch; original source unchanged.')
