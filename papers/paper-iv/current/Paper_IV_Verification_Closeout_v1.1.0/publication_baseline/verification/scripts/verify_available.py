#!/usr/bin/env python3
"""Scoped standard-library checks for Paper IV. No Lean build or full-suite replay."""
from __future__ import annotations
import argparse, ast, collections, csv, hashlib, importlib.util, importlib.metadata, json, math, os, platform, re, subprocess, sys, zipfile
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def manifest_check(root,name):
    records=[]
    for line in (root/name).read_text().splitlines():
        if not line.strip():continue
        digest,relative=line.split(maxsplit=1);relative=relative.lstrip('*');path=(root/relative).resolve()
        assert path.is_relative_to(root.resolve()) and path.is_file(),relative
        assert sha(path)==digest,relative
        records.append(relative)
    assert len(records)==len(set(records))
    return records

def archive_check(archive,directory):
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        entries=[x for x in z.infolist() if not x.is_dir()]
        assert len({x.filename for x in entries})==len(entries)
        actual={p.relative_to(directory).as_posix():p for p in directory.rglob('*') if p.is_file()}
        direct={x.filename for x in entries}
        if direct!=set(actual):
            prefix=entries[0].filename.split('/')[0]+'/'
            assert all(x.filename.startswith(prefix) for x in entries)
        else:prefix=''
        assert {x.filename.removeprefix(prefix) for x in entries}==set(actual)
        for e in entries:
            p=actual[e.filename.removeprefix(prefix)]
            assert hashlib.sha256(z.read(e)).hexdigest()==sha(p),str(p)
        return {'file_count':len(entries),'crc_pass':True,'exact_file_set_and_bytes':True,'archive_sha256':sha(archive)}

def safe_scrub_from_original(path):
    # Reuse precisely the inherited lexical scrub function, not its CLI or archive assumptions.
    source=path.read_text();node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name=='scrub')
    fn=ast.get_source_segment(source,node);ns={};exec(compile(fn,str(path),'exec'),ns);return ns['scrub'],sha(path),hashlib.sha256(fn.encode()).hexdigest()

def static_lean(formal):
    lexical= formal.parents[1]/'independent_audit/PRSC_IV_Independent_Audit/independent_static_audit.py'
    scrub,origin_hash,fn_hash=safe_scrub_from_original(lexical)
    lean=formal/'formalization/lean';files=sorted(lean.rglob('*.lean'));clean={p:scrub(p.read_text()) for p in files}
    findings=[]
    patterns=[r'\b(?:sorry|admit|sorryAx|unsafe|opaque|native_decide|implemented_by)\b',r'^\s*axiom\s',r'debug\.skipKernelTC',r'\b(?:addAndCompile|addDecl|setEnv|modifyEnv|ofReduceBool|trustCompiler)\b']
    for p,s in clean.items():
        for pat in patterns:
            for m in re.finditer(pat,s,re.M):findings.append({'file':str(p.relative_to(formal)),'line':s.count('\n',0,m.start())+1,'token':m.group()})
    decls=collections.defaultdict(list)
    for p,s in clean.items():
        for m in re.finditer(r'\b(theorem|lemma|def|abbrev|instance|structure|inductive)\s+([A-Za-z_][A-Za-z0-9_\'.]*)',s):decls[m.group(2)].append(m.group(1))
    targets=json.loads((formal/'verification/lean_contract_v1.0.0.json').read_text())['targets'];miss=[];wrong=[]
    for t in targets:
        short=t['declaration'].removeprefix('Komorebi.PaperIV.');found=decls.get(short,[]) or decls.get(short.rsplit('.',1)[-1],[])
        if not found:miss.append(t['declaration'])
        elif not any((x in ['theorem','lemma'])==(t['kind']=='theorem') for x in found):wrong.append(t['declaration'])
    mods={'.'.join(p.relative_to(lean).with_suffix('').parts):p for p in files}
    graph={n:re.findall(r'^\s*import\s+(KomorebiPaperIV(?:\.[A-Za-z0-9_]+)*)',clean[p],re.M) for n,p in mods.items()}
    missing=sorted({x for imp in graph.values() for x in imp if x not in mods});seen=set()
    def visit(n):
        if n in seen:return
        seen.add(n)
        for m in graph.get(n,[]):visit(m)
    visit('KomorebiPaperIV')
    prints=re.findall(r'^#print axioms ([^\s]+)',(lean/'KomorebiPaperIV/KernelAudit.lean').read_text(),re.M)
    names={t['declaration'] for t in targets}
    assert not(findings or miss or wrong or missing)
    assert set(prints)==names and len(prints)==len(names)
    return {'status':'PASS','scope':'Lexical source checks only; no elaboration, name resolution, declaration-kind kernel check or proof checking. Short-name matching is an explicitly limited textual surrogate.','lean_source_files':len(files),'lean_source_lines':sum(len(p.read_text().splitlines()) for p in files),'forbidden_source_findings':findings,'mapped_name_misses':miss,'mapped_kind_mismatches':wrong,'local_imports_missing':missing,'umbrella_reached_modules':len(seen),'umbrella_unreached_modules':sorted(set(mods)-seen),'kernel_audit_print_targets':len(prints),'audit_target_set_matches_contract':True,'semantic_check_theorems':len(re.findall(r'^theorem\s+',clean[lean/'KomorebiPaperIV/SemanticChecks.lean'],re.M)),'scrub_origin_file_sha256':origin_hash,'scrub_function_sha256':fn_hash}

def conv(a,b,n):return [sum((a[k]*b[j-k] for k in range(j+1) if k<len(a) and j-k<len(b)),Q(0)) for j in range(n+1)]
def inverse(a,n):
    assert a[0]==1
    out=[Q(1)]
    for j in range(1,n+1):out.append(-sum((a[k]*out[j-k] for k in range(1,min(j,len(a)-1)+1)),Q(0)))
    return out

def inverse_power(a,r,n):
    # Independent repeated truncated product of inverse series, for integral r>=1.
    assert r>=1
    inv=inverse(a,n);out=[Q(1)]+[Q(0)]*n
    for _ in range(r):out=conv(out,inv,n)
    return out

@lru_cache(None)
def secant(N,r,n):
    out=[1]
    for j in range(1,n+1):out.append(-sum((-1)**k*math.comb(N*j-1,N*k)*out[j-k] for k in range(1,j))-r*sum((-1)**k*math.comb(N*j-1,N*k-1)*out[j-k] for k in range(1,j+1)))
    return out

@lru_cache(None)
def tangent(N,n):
    out=[1]
    for j in range(1,n+1):out.append((-1)**j-sum((-1)**k*math.comb(N*j+N-1,N*k)*out[j-k] for k in range(1,j+1)))
    return out

def numeric_tables(data):
    specs=[('transfer_secant_coefficients.csv','secant'),('transfer_tangent_coefficients.csv','tangent'),('congruential_euler_coefficients.csv','congruential')];report=[]
    for filename,kind in specs:
        rows=list(csv.DictReader((data/filename).open()));families={}
        for row in rows:
            N=int(row['N']);n=int(row['n']);r=int(row.get('r',1));j=int(row.get('j',0));key=(N,r,j)
            if key not in families:
                maxn=max(int(x['n']) for x in rows if int(x['N'])==N and int(x.get('r',1))==r and int(x.get('j',0))==j)
                if kind=='secant':
                    vals=secant(N,r,maxn);a=[Q((-1)**k,math.factorial(N*k)) for k in range(maxn+1)];direct=inverse_power(a,r,maxn)
                    assert vals==[direct[k]*math.factorial(N*k) for k in range(maxn+1)]
                elif kind=='tangent':
                    vals=tangent(N,maxn);a=[Q((-1)**k,math.factorial(N*k)) for k in range(maxn+1)];numer=[Q((-1)**k,math.factorial(N*k+N-1)) for k in range(maxn+1)];direct=conv(inverse(a,maxn),numer,maxn)
                    assert vals==[direct[k]*math.factorial(N*k+N-1) for k in range(maxn+1)]
                else:
                    a=[Q(math.factorial(j),math.factorial(N*k+j)) for k in range(maxn+1)];direct=inverse_power(a,r,maxn);vals=[direct[k]*math.factorial(N*k) for k in range(maxn+1)]
                families[key]=vals
            assert Q(row['coefficient'])==families[key][n],row
        report.append({'filename':filename,'rows_passed':len(rows),'families':len(families),'bounds':{k:[min(int(x[k]) for x in rows),max(int(x[k]) for x in rows)] for k in ['N','r','j','n'] if k in rows[0]},'sha256':sha(data/filename)})
    assert secant(2,1,3)==[1,1,5,61]
    return {'status':'PASS','arithmetic':'Python integer and fractions.Fraction, exact','scope':'Three numeric CSV coefficient tables only; polynomial tables and original symbolic suites not replayed. Independent inverse-series comparison accompanies secant and tangent recurrence checks.','total_rows':sum(x['rows_passed'] for x in report),'tables':report}

def F(rec):return Q(int(rec['numerator']),int(rec['denominator']))
def rec(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator)}
def rounded(pair,digits=70):
    scale=10**digits;lo,hi=pair
    return Q(lo.numerator*scale//lo.denominator,scale),Q(-((-hi.numerator*scale)//hi.denominator),scale)

def endpoint(a,terms=90):
    assert a>0
    total=sum((Q((-1)**j)*a**(3*j)/math.factorial(3*j) for j in range(terms+1)),Q(0));n=terms+1
    tail=Q((-1)**n)*a**(3*n)/math.factorial(3*n);ratio=a**3/Q((3*n+1)*(3*n+2)*(3*n+3));assert ratio<1
    return min(total,total+tail),max(total,total+tail)

def derivative(a,b,terms=90):
    assert 0<a<b
    lo=hi=Q(0)
    for j in range(1,terms+1):
        p=3*j-1;aa=a**p/math.factorial(p);bb=b**p/math.factorial(p)
        if j%2:lo-=bb;hi-=aa
        else:lo+=aa;hi+=bb
    n=terms+1;tail=b**(3*n-1)/math.factorial(3*n-1);ratio=b**3/Q(3*n*(3*n+1)*(3*n+2));assert ratio<1
    return lo-tail,hi+tail

def brackets(report_path):
    old=json.loads(report_path.read_text());res=[]
    for c in old['cubic_brackets']:
        a,b=F(c['lower']),F(c['upper']);assert b-a==Q(1,10**20)
        low=rounded(endpoint(a));high=rounded(endpoint(b));der=rounded(derivative(a,b))
        assert (low[1]<0<high[0]) or (high[1]<0<low[0])
        assert der[1]<0 or der[0]>0
        for pair,key in [(low,'D3_lower_endpoint_interval'),(high,'D3_upper_endpoint_interval'),(der,'D3_derivative_interval')]:assert pair==tuple(map(F,c[key])),key
        res.append({'model_index':c['model_index'],'lower':rec(a),'upper':rec(b),'opposite_endpoint_signs':True,'derivative_excludes_zero':True,'saved_enclosure_endpoints_reproduced_exactly':True,'terms':90})
    assert len(res)==4
    return {'status':'PASS','scope':'Four pre-existing rational brackets for D3(x)=sum((-1)^j*x^(3j)/(3j)!) on the positive real axis. Endpoint signs and derivative exclusion establish one root per bracket using continuity and monotonicity. No root search, plotting, complex-zero census, global enumeration or asymptotic theorem is claimed.','arithmetic':'fractions.Fraction, exact; alternating-series Taylor remainder','rounding':'outward to denominator10^70','brackets':res,'historical_exact_checks_sha256':sha(report_path)}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--downloads',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    source=args.source.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True);complete=source/'complete';strength=source/'strengthened';formal=complete/'original_snapshot/lean_release/PRSC_IV'
    before={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*') if p.is_file()}
    environment={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'deps':{}}
    for name in ['sympy','mpmath','numpy','pandas','matplotlib']:
        try:environment['deps'][name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:environment['deps'][name]='NOT_INSTALLED'
    import shutil
    environment['lean']=shutil.which('lean');environment['lake']=shutil.which('lake')
    counts={}
    for root,name,label in [(complete,'SHA256SUMS.txt','complete'),(strength,'MANIFEST.sha256','strengthened'),(formal,'SHA256SUMS.txt','formal'),(complete/'original_snapshot/proofread_review/PRSC_IV_Review','REVIEW_SHA256SUMS.txt','proofread_review')]:counts[label]=len(manifest_check(root,name))
    fm=json.loads((complete/'FILE_MANIFEST.json').read_text());assert all(sha(complete/x['path'])==x['sha256'] for x in fm['files']);counts['complete_json_payload']=len(fm['files'])
    archives={}
    for filename,directory in [('Paper_IV_Complete_v1.0.0_With_Visual_Appendix.zip',complete),('PSC_Paper_IV_Strengthened_Annals_Edition_Package.zip',strength)]:archives[filename]=archive_check(args.downloads/filename,directory)
    proc=subprocess.run([sys.executable,'-B',str(complete/'tools/audit_original.py'),'--output-dir',str(out/'original_static')],text=True,capture_output=True,timeout=90,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    (out/'original_static_stdout.txt').write_text(proc.stdout);(out/'original_static_stderr.txt').write_text(proc.stderr);assert proc.returncode==0,proc.stderr
    gate=load_module('paper_iv_release_gate',formal/'verification/check_release.py');reporter=gate.Reporter('release');files=gate.release_files(formal)
    gate.check_manifest(formal,files,reporter);gate.check_evidence_claims(formal,files,reporter);register=gate.check_generated_register(formal,files,reporter)
    targets,nd,nt=gate.load_lean_contract(formal,reporter);rows=gate.parse_theorem_map(formal/gate.AUTHORITATIVE_THEOREM_MAP);mapped,records=gate.crosscheck_map_contract(rows,register,targets)
    static={'status':'PASS','map_rows':len(rows),'mapped_targets':len(mapped),'associated_records':len(set(records)),'register_records':len(register),'saved_namespace_counts_not_regenerated':[nd,nt]}
    lexical=static_lean(formal);tables=numeric_tables(strength/'verification/original_data');cubic=brackets(complete/'visual_appendix/checks/EXACT_CHECKS.json')
    after={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*') if p.is_file()};assert before==after
    report={'status':'PASS_FOR_STATED_SCOPE','environment':environment,'source_files':len(before),'source_files_unchanged':True,'manifest_entries':counts,'archives':archives,'formal_static':static,'lexical':lexical,'numeric_csv_checks':tables,'cubic_rational_brackets':cubic,'not_run':[{'item':'fresh Lean kernel compilation and namespace census','reason':'lean and lake unavailable; no Lean invocation authorized for this check scope'},{'item':'original visual147 exact/symbolic/enclosure tests and5 invalid controls','reason':'SymPy and mpmath unavailable'},{'item':'original24 TikZ plate regeneration','reason':'SymPy and mpmath unavailable'},{'item':'all three original strengthened regression scripts, including1246 historical strengthened checks','reason':'SymPy and mpmath unavailable; original table verifier also uses pandas'}],'dependency_install_attempted':False,'note':'No automatic approval rejection occurred in this Paper IV verification run. A prior Paper III installation rejection was respected; no install, download or retry was made. Current finite checks do not replace unrun suites or fresh Lean proofs.'}
    (out/'CURRENT_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');(out/'SOURCE_HASHES.json').write_text(json.dumps(before,indent=2)+'\n')
    print(f'PASS: {len(before)} unchanged source files; manifest counts {counts}; {len(rows)} map rows, {len(mapped)} saved targets; {tables["total_rows"]} exact numeric CSV rows;4 rational cubic brackets. Full visual/strengthened suites and Lean build NOT RUN.')
if __name__=='__main__':main()
