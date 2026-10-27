"""Comment-aware source inventory and strict axiom parser, adapted from the audited baseline."""
from pathlib import Path
import re
import hashlib
ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = re.compile(r'\b(?:sorry|admit|axiom|unsafe|native_decide|implemented_by)\b|'
                       r'debug\.skipKernelTC|ofReduceBool|ofReduceNat|Lean\.addDecl|'
                       r'set_option\s+(?:maxRecDepth|maxHeartbeats)\s+0|'
                       r'set_option\s+linter\.[\w.]+\s+false')

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stripped_source(text: str) -> str:
    """Remove nested block comments, line comments and strings; preserve newlines."""
    out = []; i=0; depth=0; string=False
    while i < len(text):
        ch=text[i]; pair=text[i:i+2]
        if depth:
            if pair=='/-': depth+=1; out.extend('  '); i+=2; continue
            if pair=='-/': depth-=1; out.extend('  '); i+=2; continue
            out.append('\n' if ch=='\n' else ' '); i+=1; continue
        if string:
            if ch=='\\' and i+1 < len(text): out.extend('  '); i+=2; continue
            if ch=='"': string=False
            out.append('\n' if ch=='\n' else ' '); i+=1; continue
        if pair=='/-': depth=1; out.extend('  '); i+=2; continue
        if pair=='--':
            j=text.find('\n',i)
            if j<0: out.extend(' '*(len(text)-i)); break
            out.extend(' '*(j-i)); i=j; continue
        if ch=='"': string=True; out.append(' '); i+=1; continue
        out.append(ch); i+=1
    if depth or string: raise ValueError('Unclosed source comment or string')
    return ''.join(out)

def inspect_source(path: Path) -> dict:
    text = stripped_source(path.read_text())
    forbidden = FORBIDDEN.findall(text)
    if forbidden: raise ValueError(f'{path.name}: forbidden source construct {forbidden}')
    namespaces=re.findall(r'^namespace\s+([\w.]+)',text,re.M)
    if len(namespaces)>1 or (namespaces and not namespaces[0].startswith('Komorebi.')):
        raise ValueError(f'{path.name}: expected one explicit project namespace')
    raw_declarations = re.findall(r'\b(theorem|lemma|def|abbrev)\s+([^\s(:{]+)', text)
    for kind, name in raw_declarations:
        if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9']*", name) is None:
            raise ValueError(f'{path.name}: unsupported declaration identifier {name!r}')
    declarations=[{'kind':k, 'name':namespaces[0]+'.'+n}
                  for k,n in raw_declarations] if namespaces else []
    if len({x['name'] for x in declarations})!=len(declarations):
        raise ValueError('Duplicate explicit declaration')
    return {'module':path.stem,'source':str(path.relative_to(ROOT)), 'sha256':sha(path),
            'imports':re.findall(r'^public import ([\w.]+)',text,re.M),
            'declarations':declarations}

def parse_audits(text: str, expected: set[str]) -> dict[str,list[str]]:
    if re.search(r'PANIC|error:|unknown constant|unknown module',text,re.I):
        raise ValueError('Compiler error in audit output')
    audits={}
    # Lean may wrap an axiom list across lines.
    # Anchor the full quoted name. Apostrophes inside Lean identifiers are legal.
    pattern=r"^'([^\r\n]+)'[ \t]+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
    for m in re.finditer(pattern,text,re.M):
        name=m[1]
        if name in audits: raise ValueError('Duplicate axiom report')
        axioms=sorted(x.strip() for x in (m[2] or '').split(',') if x.strip())
        if not set(axioms)<=ALLOWED: raise ValueError(f'Unexpected axioms for {name}: {axioms}')
        audits[name]=axioms
    if set(audits)!=expected:
        raise ValueError(f'Audit inventory mismatch: missing={sorted(expected-set(audits))}, extra={sorted(set(audits)-expected)}')
    return audits
