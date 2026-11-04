#!/usr/bin/env python3
"""Compare with the pinned CompQuadForm Davies C++ core, outside the R runtime.

Use --prepare to download the upstream source and build a local shared library.
The source bytes are checked before compilation. The numerical code is unchanged.
Two local compatibility headers supply only <cmath>/<cstdlib>, not R algorithms.
Upstream code and compiled binaries are not redistributed in the audit package.
"""
import argparse, ctypes as C, hashlib, json, os, subprocess, sys, time, urllib.request
from collections import Counter
from decimal import Decimal, localcontext
from pathlib import Path
from independent_reference import exact_law_tail, imhof_quad, imhof_weighted
ROOT=Path(__file__).resolve().parent
VENDOR=ROOT/'vendor_work'
PIN='f1e110ac54aa0e64dda8cf6254823e801878e036'
BLOB='ee7e6c1f81ffcb8a1496d5d1d43839bdf6d03867'
URL=f'https://raw.githubusercontent.com/cran/CompQuadForm/{PIN}/src/qfc.cpp'

def prepare(download=False):
    VENDOR.mkdir(exist_ok=True)
    source=VENDOR/'qfc.cpp'
    if download and not source.exists():
        with urllib.request.urlopen(URL,timeout=45) as response:source.write_bytes(response.read())
    raw=source.read_bytes()
    sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if sha!=BLOB:raise RuntimeError('Davies upstream source identity mismatch')
    (VENDOR/'R.h').write_text('#include <cmath>\n#include <cstdlib>\n')
    (VENDOR/'Rmath.h').write_text('#include <cmath>\n')
    compiler=os.environ.get('CXX','g++')
    command=[compiler,'-O2','-std=c++17','-fPIC','-shared','-I',str(VENDOR),str(source),'-o',str(VENDOR/'libqfc.so')]
    subprocess.run(command,check=True,timeout=45)
    return {'repository':'cran/CompQuadForm','revision':PIN,'path':'src/qfc.cpp','git_blob_sha1':sha,
            'sha256':hashlib.sha256(raw).hexdigest(),'compiler':subprocess.check_output([compiler,'--version'],text=True).splitlines()[0],
            'flags':['-O2','-std=c++17','-fPIC','-shared'],'source_modifications':[],
            'headers':'R.h: cmath and cstdlib; Rmath.h: cmath',
            'execution_scope':'Unmodified Davies C++ core via ctypes, not the installed R package'}

def davies(q,eig,acc=1e-10,lim=200000):
    # A process-local library, called serially because qfc uses global state.
    lib=C.CDLL(str(VENDOR/'libqfc.so'))
    pd,pi=C.POINTER(C.c_double),C.POINTER(C.c_int)
    lib.qfc.argtypes=[pd,pd,pi,pi,pd,pd,pi,pd,pd,pi,pd];lib.qfc.restype=None
    grouped=Counter(map(float,eig));n=len(grouped)
    lam=(C.c_double*n)(*grouped.keys());nc=(C.c_double*n)(*[0.0]*n)
    df=(C.c_int*n)(*grouped.values());rank=C.c_int(n);sigma=C.c_double(0)
    threshold=C.c_double(float(q));limit=C.c_int(lim);accuracy=C.c_double(acc)
    trace=(C.c_double*7)();ifault=C.c_int(0);cdf=C.c_double(0)
    start=time.perf_counter()
    lib.qfc(lam,nc,df,C.byref(rank),C.byref(sigma),C.byref(threshold),C.byref(limit),C.byref(accuracy),trace,C.byref(ifault),C.byref(cdf))
    seconds=time.perf_counter()-start
    return {'raw_sf':1-cdf.value,'ifault':ifault.value,'trace':list(trace),'seconds':seconds,
            'requested_absolute_accuracy':acc,'integration_limit':lim,
            'success_flag_and_probability_range':ifault.value==0 and 0<=1-cdf.value<=1}

def run(provenance):
    records=[]
    cases=['running-16384','equal-8','clustered-8','mixed-12','wide-8','scale-small','scale-large']
    for case in cases:
        row=json.loads((ROOT/'results'/f'{case}.json').read_text());q=row['input']['q'];eig=row['input']['eigenvalues']
        # Reference the EXACT binary64 input supplied to Davies, not ideal decimals.
        q_binary=str(Decimal.from_float(float(q)))
        eig_binary=[str(Decimal.from_float(float(x))) for x in eig]
        ref=exact_law_tail(q_binary,eig_binary,digits=220)
        d=davies(q,eig)
        with localcontext() as c:
            c.prec=240
            estimate=Decimal.from_float(d['raw_sf']);lo,hi=map(Decimal,ref['probability'])
            error_lo=max(Decimal(0),lo-estimate,estimate-hi)
            error_hi=max(abs(estimate-lo),abs(estimate-hi))
        d.update({'absolute_error_lower':str(error_lo),'absolute_error_upper':str(error_hi),
                  'observed_error_within_requested_absolute_accuracy':bool(error_hi<=Decimal(str(d['requested_absolute_accuracy'])))})
        imhof=row.get('imhof_quad') or imhof_quad(q,eig)
        records.append({'case':case,'davies':d,'imhof_quad':imhof,
                        'davies_input_semantics':'exact binary64 casts of the stored decimal input; repeated coefficients grouped',
                        'davies_independent_reference':ref,
                        'imhof_weighted':imhof_weighted(q,eig)})
        ideal=row['independent_reference']['probability']
        for method in ('imhof_quad','imhof_weighted'):
            value=records[-1][method]
            with localcontext() as ctx:
                ctx.prec=260
                estimate=Decimal.from_float(value['probability']);lo,hi=map(Decimal,ideal)
                value['observed_absolute_error_upper']=str(max(abs(estimate-lo),abs(estimate-hi)))
            value['observed_error_within_requested_absolute_accuracy']=(Decimal(value['observed_absolute_error_upper'])<=Decimal(str(value['requested_absolute_accuracy'])))
        print(case,'Davies flag',d['ifault'],'absolute error',f'{float(error_hi):.3e}',flush=True)
    output={'provenance':provenance,'comparisons':records,
            'not_claimed':['Directed enclosure for Davies or Imhof','R package execution','Equal-accuracy timing benchmark',
                           'Deep-tail superiority based on absolute-error outputs']}
    (ROOT/'results'/'comparisons.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    run(prepare(download=args.prepare))
