from pathlib import Path
import re, json, hashlib
ROOT=Path('/mnt/data/Komorebi_Space_Monograph_v1.7.0')
CH=ROOT/'source/chapters'
changes=[]

def proof(file,label,new,reason):
 p=CH/file;s=p.read_text();pos=s.index('\\label{'+label+'}')
 start=s.index('\\begin{proof}',pos);end=s.index('\\end{proof}',start)+len('\\end{proof}')
 old=s[start:end];new='\\begin{proof}\n'+new.strip()+'\n\\end{proof}'
 assert '\\begin{theorem}' not in s[pos:start] and '\\source{' not in s[pos:start],label
 s=s[:start]+new+s[end:];p.write_text(s)
 changes.append({'id':label,'file':str(p.relative_to(ROOT)),'change':'expanded proof','focus':reason,'old_words':len(old.split()),'new_words':len(new.split()),'old_proof_sha256':hashlib.sha256(old.encode()).hexdigest(),'new_proof_sha256':hashlib.sha256(new.encode()).hexdigest()})

def replace(file,old,new,reason,label):
 p=CH/file;s=p.read_text();assert old in s,(file,old[:60]);assert s.count(old)==1,(file,'ambiguous')
 p.write_text(s.replace(old,new));changes.append({'id':label,'file':str(p.relative_to(ROOT)),'change':reason,'old_words':len(old.split()),'new_words':len(new.split())})

