#!/usr/bin/env python3
"""Snapshot-bound proof-certificate workflow for AVOC's propositional fragment.

Untrusted candidates are JSON proof DATA, never Lean source. The trusted Lean
program executes the proved checker. This Python filesystem/parser orchestration
is tested but is not claimed formally extracted. Host, installed toolchain,
selected environment fingerprint, SHA-256 collision resistance, and exclusive
control of the store remain explicit trust boundaries.
"""
from __future__ import annotations
import argparse, base64, contextlib, copy, hashlib, json, os, re, signal
import subprocess, sys, tempfile, time
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 1048576
TASK = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")

class GateError(ValueError):
    pass

def require(ok: bool, message: str) -> None:
    if not ok:
        raise GateError(message)

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def strict_json(raw: str) -> Any:
    require(len(raw.encode('utf-8')) <= MAX_BYTES, 'byte limit exceeded')
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, 'duplicate JSON field')
            result[k] = v
        return result
    try:
        return json.loads(raw, object_pairs_hook=unique,
                          parse_constant=lambda x: (_ for _ in ()).throw(GateError('non-finite JSON number')))
    except (json.JSONDecodeError, RecursionError, UnicodeError) as e:
        raise GateError('invalid JSON') from e

def read_raw(path: Path) -> str:
    require(not path.is_symlink(), 'symlink inputs are not supported')
    data = path.read_bytes()
    require(len(data) <= MAX_BYTES, 'input byte limit exceeded')
    try:
        return data.decode('utf-8', errors='strict')
    except UnicodeError as e:
        raise GateError('input must be valid UTF-8') from e

def encode(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

def exact_keys(obj: Any, keys: set[str]) -> None:
    require(isinstance(obj, dict) and set(obj) == keys, 'unexpected or missing fields')

def validate_formula(f: Any, depth: int = 0) -> None:
    require(depth < 64 and isinstance(f, list) and bool(f), 'invalid formula or depth')
    tag = f[0]
    if tag == 'atom':
        require(len(f) == 2 and type(f[1]) is int and 0 <= f[1] <= 1000000, 'invalid atom')
    elif tag in ('true', 'false'):
        require(len(f) == 1, 'invalid nullary formula')
    elif tag in ('and', 'or', 'imp'):
        require(len(f) == 3, 'invalid binary formula')
        validate_formula(f[1], depth+1); validate_formula(f[2], depth+1)
    else:
        raise GateError('unknown formula constructor')

def validate_proof(p: Any, depth: int = 0, count: list[int] | None = None) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    require(count[0] <= 10000 and depth < 128 and isinstance(p, list) and p, 'invalid proof or resource limit')
    tag = p[0]
    arities = {'hyp':2,'true':1,'pair':3,'fst':2,'snd':2,'intro':3,
               'mp':3,'left':3,'right':3,'cases':4,'absurd':3}
    require(isinstance(tag, str) and tag in arities and len(p) == arities[tag], 'invalid proof tag/arity')
    if tag == 'hyp':
        validate_formula(p[1]); return
    if tag == 'true':
        return
    start = 1
    if tag in ('intro','left','right','absurd'):
        validate_formula(p[1]); start = 2
    for child in p[start:]:
        validate_proof(child, depth+1, count)

def parse_target(raw: str) -> dict[str, Any]:
    obj = strict_json(raw)
    exact_keys(obj, {'schema','task','statement','dependencies'})
    require(obj['schema'] == 'avoc-proposition-1', 'wrong target schema')
    require(isinstance(obj['task'], str) and TASK.fullmatch(obj['task']) is not None, 'invalid task name')
    validate_formula(obj['statement'])
    deps = obj['dependencies']
    require(isinstance(deps,list) and all(isinstance(x,str) and TASK.fullmatch(x) for x in deps), 'invalid dependencies')
    require(len(set(deps)) == len(deps) and obj['task'] not in deps, 'duplicate/self dependency')
    require(len(deps) <= 64, 'dependency limit')
    return obj

def wire_identity(ticket: dict[str,Any]) -> list[Any]:
    spec=parse_target(ticket['target_bytes'])
    deps=[]
    for d in ticket['dependencies']:
        target=parse_target(d['record']['ticket']['target_bytes'])
        deps.append([d['task'],target['statement'],encode(d['record'])])
    return [spec['task'],spec['statement'],ticket['target_bytes'],deps,
            [[k,encode(v)] for k,v in sorted(ticket['environment'].items())]]

def wire_ticket(ticket: dict[str,Any]) -> list[Any]:
    return [ticket['generation'],[wire_identity(ticket),ticket['candidate_bytes']]]

class LeanChecker:
    """Runs only the trusted data checker, with bounded process-group execution."""
    def __init__(self, root: Path = ROOT, kit: Path | None = None, seconds: int = 20):
        self.root = root.resolve()
        self.kit = (kit or Path(os.environ.get('AVOC_LEAN_KIT', '/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))).resolve()
        self.lean = self.kit / 'toolchain/bin/lean'
        self.seconds = seconds
        self.records: list[dict[str,Any]] = []
        self.version = subprocess.check_output([str(self.lean),'--version'], text=True, timeout=10).strip()
        require('4.34.0-rc2' in self.version, 'wrong Lean pin')

    def environment(self) -> dict[str,Any]:
        sources = ['AVOC/CertificateLogic.lean','AVOC/CertificateCodec.lean','tools/CertificateMain.lean']
        if (self.root/'AVOC/BindingCodec.lean').exists():
            sources += ['AVOC/ArtifactBinding.lean','AVOC/BindingCodec.lean']
        modules = [s for s in sources if s.startswith('AVOC/')]
        return {'schema':'avoc-checker-env-1', 'lean_version':self.version,
                'lean_executable_sha256':digest(self.lean),
                'libleanshared_sha256':digest(self.kit/'toolchain/lib/lean/libleanshared.so'),
                'checker_source_bytes':{s:read_raw(self.root/s) for s in sources},
                'checker_olean_sha256':{s:digest(self.root/'.lake/build/lib/lean'/Path(s).with_suffix('.olean')) for s in modules},
                'trusted_runtime_boundary':'Pinned Lean/Std/Lean.Json binary cache and host remain trusted; not a hash-injectivity proof.'}

    def request(self, payload: Any) -> bool:
        raw = encode(payload)
        require(len(raw.encode()) <= MAX_BYTES, 'checker request limit')
        env = os.environ.copy()
        env['LEAN_PATH'] = str(self.root/'.lake/build/lib/lean')
        env['PATH'] = str(self.kit/'toolchain/bin') + ':' + env.get('PATH','')
        with tempfile.TemporaryDirectory(prefix='avoc_check_') as d:
            path = Path(d)/'request.json'; path.write_text(raw, encoding='utf-8')
            cmd = [str(self.lean),'-j1','-DwarningAsError=true','--run',
                   str(self.root/'tools/CertificateMain.lean'),str(path)]
            start = time.monotonic()
            proc = subprocess.Popen(cmd,cwd=self.root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                    text=True,start_new_session=True)
            timed_out = False
            try:
                out, err = proc.communicate(timeout=self.seconds)
            except subprocess.TimeoutExpired:
                timed_out = True; os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate()
            self.records.append({'request_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                                 'returncode':proc.returncode,'timed_out':timed_out,
                                 'stdout':out,'stderr':err,'seconds':round(time.monotonic()-start,4)})
            require(not timed_out, 'checker timed out')
            require(not err.strip(), 'checker diagnostic: ' + err[:200])
            require(proc.returncode in (0,1), 'checker setup/parser failed: '+out[:200])
            require(out.strip() in ('{"accepted":true}','{"accepted":false}'), 'unexpected checker output')
            accepted = out.strip() == '{"accepted":true}'
            require(accepted == (proc.returncode == 0), 'checker result/exit mismatch')
            return accepted

    def check(self, target: Any, context: list[Any], proof: Any) -> bool:
        validate_formula(target)
        for f in context: validate_formula(f)
        validate_proof(proof)
        return self.request([target,context,proof])

class ArtifactGate:
    """Single-writer local store. Persisted receipts are claims, not authorities.
    Target meaning, dependency proof chains, exact pending bytes, and current
    environment are rechecked at admission. The protected store/host is trusted.
    """
    def __init__(self, store: Path, checker: LeanChecker):
        self.store=store.resolve();self.checker=checker
        self.store.mkdir(parents=True,exist_ok=True)
        self.state_path=self.store/'state.json'

    @contextlib.contextmanager
    def lock(self) -> Iterator[None]:
        path=self.store/'LOCK'
        try: fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError as e: raise GateError('store locked; no concurrent mutation allowed') from e
        try:
            os.write(fd,str(os.getpid()).encode());os.close(fd)
            yield
        finally:
            path.unlink(missing_ok=True)

    def load(self) -> dict[str,Any]:
        if not self.state_path.exists():
            return {'schema':'avoc-store-1','next':0,'pending':None,'admitted':{},'events':[]}
        obj=strict_json(read_raw(self.state_path))
        exact_keys(obj,{'schema','next','pending','admitted','events'})
        require(obj['schema']=='avoc-store-1' and type(obj['next']) is int and obj['next']>=0,'invalid store')
        require(isinstance(obj['admitted'],dict) and isinstance(obj['events'],list),'invalid store collections')
        return obj

    def save(self, obj: dict[str,Any]) -> None:
        raw=encode(obj)
        # The state may exceed the single-artifact bound, but remains deliberately bounded.
        require(len(raw.encode()) <= MAX_BYTES, 'store byte budget exceeded')
        path=self.store/'state.tmp'
        with path.open('w',encoding='utf-8') as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(path,self.state_path)

    def capture(self, target_path: Path, candidate_path: Path, state: dict[str,Any], generation: int) -> dict[str,Any]:
        target_raw=read_raw(target_path);spec=parse_target(target_raw)
        proof_raw=read_raw(candidate_path);validate_proof(strict_json(proof_raw))
        dependencies=[]
        for name in spec['dependencies']:
            require(name in state['admitted'],'dependency has not been admitted: '+name)
            dependencies.append({'task':name,'record':copy.deepcopy(state['admitted'][name])})
        return {'schema':'avoc-ticket-1','generation':generation,
                'target_path':str(target_path.resolve()),'candidate_path':str(candidate_path.resolve()),
                'target_bytes':target_raw,'candidate_bytes':proof_raw,
                'dependencies':dependencies,'environment':self.checker.environment()}

    def register(self,target_path: Path,candidate_path: Path) -> dict[str,Any]:
        with self.lock():
            s=self.load();ticket=self.capture(target_path,candidate_path,s,s['next'])
            s['next']+=1;s['pending']=ticket
            s['events'].append({'op':'register','generation':ticket['generation'],'task':parse_target(ticket['target_bytes'])['task']})
            self.save(s);return copy.deepcopy(ticket)

    def verify_ticket(self,ticket: Any, environment: dict[str,Any], stack: tuple[str,...]=(), depth:int=0) -> Any:
        exact_keys(ticket,{'schema','generation','target_path','candidate_path','target_bytes','candidate_bytes','dependencies','environment'})
        require(ticket['schema']=='avoc-ticket-1' and type(ticket['generation']) is int and ticket['generation']>=0,'invalid ticket')
        require(depth<=16,'dependency depth limit')
        require(ticket['environment']==environment,'stale checker environment')
        spec=parse_target(ticket['target_bytes']);task=spec['task']
        require(task not in stack,'dependency cycle')
        proof=strict_json(ticket['candidate_bytes']);validate_proof(proof)
        deps=ticket['dependencies']
        require(isinstance(deps,list) and len(deps)==len(spec['dependencies']),'dependency shape mismatch')
        context=[]
        for name,item in zip(spec['dependencies'],deps):
            exact_keys(item,{'task','record'})
            require(item['task']==name,'dependency identity mismatch')
            record=item['record'];exact_keys(record,{'schema','ticket'})
            require(record['schema']=='avoc-admission-1','invalid admission record')
            require(parse_target(record['ticket']['target_bytes'])['task']==name,'substituted dependency task')
            context.append(self.verify_ticket(record['ticket'],environment,stack+(task,),depth+1))
        require(self.checker.check(spec['statement'],context,proof),'proof rejected')
        return spec['statement']

    def verify(self) -> dict[str,Any]:
        with self.lock():
            s=self.load();t=s['pending'];require(t is not None,'no pending candidate')
            env=self.checker.environment()
            self.verify_ticket(t,env)
            require(self.checker.environment()==env,'environment changed during verification')
            return {'schema':'avoc-receipt-1','subject':copy.deepcopy(t),'approved':True}

    def admit(self,receipt: Any) -> dict[str,Any]:
        with self.lock():
            s=self.load();t=s['pending'];require(t is not None,'no pending candidate (already consumed or never registered)')
            exact_keys(receipt,{'schema','subject','approved'})
            require(receipt['schema']=='avoc-receipt-1' and receipt['approved'] is True,'invalid or rejected receipt')
            # Exact structured equality includes exact raw target/candidate strings.
            # Hash equality is never substituted for candidate/statement byte equality.
            require(receipt['subject']==t,'receipt does not identify the pending ticket')
            current=self.capture(Path(t['target_path']),Path(t['candidate_path']),s,t['generation'])
            require(current==t,'candidate, target, dependency, or environment changed after registration')
            self.verify_ticket(t,t['environment'])  # Receipt verdict is deliberately not trusted.
            require(self.checker.environment()==t['environment'],'environment changed during admission')
            # Execute the very binding function whose soundness and identity
            # properties were proved in Lean. Its artifact parser reads the
            # exact stored candidate bytes, not a separately supplied proof AST.
            payload=['bound',wire_identity(current),[s['next'],wire_ticket(t)],
                     [wire_ticket(receipt['subject']),receipt['approved']]]
            require(self.checker.request(payload),'formal binding gate rejected')
            require(self.checker.environment()==t['environment'],'environment changed in binding gate')
            final_snapshot=self.capture(Path(t['target_path']),Path(t['candidate_path']),s,t['generation'])
            require(final_snapshot==t,'live inputs changed during admission verification')
            task=parse_target(t['target_bytes'])['task']
            record={'schema':'avoc-admission-1','ticket':copy.deepcopy(t)}
            s['admitted'][task]=record;s['pending']=None
            s['events'].append({'op':'admit','generation':t['generation'],'task':task})
            self.save(s);return record

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--store',type=Path,required=True)
    sub=ap.add_subparsers(dest='command',required=True)
    reg=sub.add_parser('register');reg.add_argument('target',type=Path);reg.add_argument('candidate',type=Path)
    ver=sub.add_parser('verify');ver.add_argument('--receipt',type=Path,required=True)
    adm=sub.add_parser('admit');adm.add_argument('receipt',type=Path)
    args=ap.parse_args();gate=ArtifactGate(args.store,LeanChecker())
    try:
        if args.command=='register':
            out=gate.register(args.target,args.candidate)
            print(encode({'registered':parse_target(out['target_bytes'])['task'],'generation':out['generation']}))
        elif args.command=='verify':
            out=gate.verify();args.receipt.write_text(encode(out),encoding='utf-8')
            print('verified; receipt written; nothing admitted')
        else:
            out=gate.admit(strict_json(read_raw(args.receipt)))
            print(encode({'admitted':parse_target(out['ticket']['target_bytes'])['task'],'generation':out['ticket']['generation']}))
    except (GateError,OSError,subprocess.SubprocessError) as e:
        print('REJECTED: '+str(e),file=sys.stderr);raise SystemExit(1)

if __name__=='__main__': main()
