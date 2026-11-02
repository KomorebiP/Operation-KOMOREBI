"""Check complete statement indexes against the rendered source passages."""
from html.parser import HTMLParser
import json
import re

VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


class StatementIndex(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.stack=[];self.entries=[];self.body_proofs={};self.anchor=None
        self.feed(text)

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='li' and 'data-statement-entry' in attrs:
            self.entries.append(dict(attrs=attrs,targets=[],proofs=[]))
        if tag=='a':
            if any('statement-navigation' in a.get('class','').split() for _,a in self.stack) and self.entries:
                if 'data-statement-target' in attrs:self.entries[-1]['targets'].append(attrs.get('href'))
                if 'statement-proof-link' in attrs.get('class','').split():self.entries[-1]['proofs'].append(attrs.get('href'))
            elif any(a.get('id')=='chapter-text' for _,a in self.stack):
                passage=next((a['id'] for _,a in reversed(self.stack) if re.fullmatch(r'L\d+',a.get('id',''))),None)
                self.anchor=dict(passage=passage,href=attrs.get('href'),text=[])
        if tag not in VOID:self.stack.append((tag,attrs))

    def handle_data(self,text):
        if self.anchor:self.anchor['text'].append(text)

    def handle_endtag(self,tag):
        if tag=='a' and self.anchor:
            if ''.join(self.anchor['text']).strip()=='Read proof' and self.anchor['passage']:
                self.body_proofs.setdefault(self.anchor['passage'],[]).append(self.anchor['href'])
            self.anchor=None
        index=next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i][0]==tag),None)
        if index is not None:del self.stack[index:]


def check(markup,report):
    from readable_chapters import KIND_NAMES,NUMBERED
    expected=[node for node in report['nodes'] if node['kind'] in NUMBERED]
    parsed=StatementIndex(markup)
    assert len(parsed.entries)==len(expected),('Incomplete statement index',report['url'])
    proof_links=0
    for entry,node in zip(parsed.entries,expected):
        attrs=entry['attrs'];identifier=node['id']
        assert attrs['data-statement-entry']==identifier,('Wrong statement order',report['url'])
        assert attrs['data-statement-kind']==node['kind'],('Wrong statement type',identifier)
        assert attrs['data-statement-name']==KIND_NAMES.get(node['kind'],node['kind'].capitalize()),('Wrong displayed type',identifier)
        assert attrs['data-statement-number']==node['number'],('Wrong printed number',identifier)
        assert attrs['data-statement-labels']==' '.join(node.get('labels',[])),('Wrong source labels',identifier)
        assert entry['targets']==['#'+identifier],('Wrong statement target',identifier)
        assert entry['proofs']==parsed.body_proofs.get(identifier,[]),('Statement and passage proof routes differ',identifier)
        proof_links+=len(entry['proofs'])
    return dict(statements=len(expected),proof_links=proof_links)


def verify(root):
    reports=json.loads((root/'documents/readable-chapters.json').read_bytes())
    statements=proofs=chapters=0;papers=set()
    for report in reports:
        match=re.match(r'read/(paper-[ivx]+)/',report['url'])
        if not match:continue
        result=check((root/report['url']).read_text(encoding='utf-8'),report)
        papers.add(match[1]);statements+=result['statements'];proofs+=result['proof_links']
        chapters+=bool(result['statements'])
    return dict(papers=len(papers),chapters_with_statements=chapters,statements=statements,proof_links=proofs)
