"""Authenticate packed chapter HTML before validating the complete reading DOM."""
from functools import lru_cache
import gzip,hashlib,json,re
from pathlib import Path
PREFIX='publication/mnr-html-reading/2026-11-04/'
ROOT=Path(__file__).resolve().parents[1]
PATTERN=re.compile(r'<script type="application/json" id="mnr-payload">(.*?)</script>',re.S)

def sha(raw):return hashlib.sha256(raw).hexdigest()

@lru_cache(maxsize=8)
def part(root,name,expected):
    if not re.fullmatch(re.escape(PREFIX)+r'parts/\d{3}\.bin',name):raise ValueError('Unexpected reading part path')
    target=Path(root)/name
    if target.is_symlink() or not target.resolve().is_relative_to(Path(root).resolve()):raise ValueError('Unsafe reading part')
    raw=target.read_bytes()
    if not 0<len(raw)<=512*1024 or sha(raw)!=expected:raise ValueError('Reading part changed')
    return raw

def decode(record,root=ROOT):
    raw=part(str(root),record['path'],record['part_sha256']);start=record['offset'];size=record['bytes']
    if type(start)!=int or type(size)!=int or start<0 or size<1 or start+size>len(raw):raise ValueError('Reading slice is outside its part')
    if not 0<record['html_bytes']<=1024*1024:raise ValueError('Invalid chapter size')
    body=gzip.decompress(raw[start:start+size])
    if len(body)!=record['html_bytes'] or sha(body)!=record['html_sha256']:raise ValueError('Reading HTML changed')
    body=body.decode('utf-8')
    if re.search(r'<(?:script|iframe|object|embed)\b|\son\w+\s*=|javascript:',body,re.I):raise ValueError('Active content in reading payload')
    return body.replace('mnr-figure/',record['figure_root'])

def expand(text,root=ROOT):
    match=PATTERN.search(text)
    if not match:return text
    body=decode(json.loads(match[1]),root)
    pattern=r'(<article id="chapter-text"[^>]*>).*?(</article>)'
    text,count=re.subn(pattern,lambda m:m[1]+body+m[2],text,count=1,flags=re.S)
    if count!=1:raise ValueError('Missing packed chapter article')
    return text
