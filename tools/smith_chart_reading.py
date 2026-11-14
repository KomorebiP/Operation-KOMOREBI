"""Source-bound final prose and chapter order for the Smith research reading."""
from __future__ import annotations
from html.parser import HTMLParser
import hashlib,html,json,re

EDITION='research/smith-chart/unified/reading-edition.json'
MATH=re.compile(r'<(?P<tag>span|div)\b[^>]*class="[^"]*\b(?:arithmatex|math inline|math display)[^"]*"[^>]*>.*?</(?P=tag)>|\\\(.*?\\\)|\\\[.*?\\\]',re.S)
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
BLOCK={'h1','h2','h3','h4','h5','h6','p','li','td','th','summary','figcaption','pre'}

def digest(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
def normalized(s):return re.sub(r'(?<![\w-])(href|src|srcset|data-source-figure|data-mobile-figure)="[^"]*"',r'\1="{url}"',s)
def prose(s):
    return ' '.join(html.unescape(re.sub('<[^>]+>',' ',MATH.sub(' [math] ',s))).split())

class Source(HTMLParser):
    def __init__(self,s):
        super().__init__(convert_charrefs=False);self.source=s;self.lines=[0]+[m.end() for m in re.finditer('\n',s)];self.nodes=[];self.stack=[]
        self.feed(s)
        if self.stack:raise ValueError('Unclosed Smith source markup')
    def position(self):line,column=self.getpos();return self.lines[line-1]+column
    def handle_starttag(self,tag,attrs):
        p=self.position();n=dict(tag=tag,attrs=dict(attrs),start=p,open_end=p+len(self.get_starttag_text()),parent=self.stack[-1] if self.stack else None)
        self.nodes.append(n);i=len(self.nodes)-1
        if tag in VOID:n['end']=n['open_end']
        else:self.stack.append(i)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if self.stack and self.nodes[self.stack[-1]]['start']==self.position():self.nodes[self.stack.pop()]['end']=self.position()+len(self.get_starttag_text())
    def handle_endtag(self,tag):
        if not self.stack or self.nodes[self.stack[-1]]['tag']!=tag:raise ValueError('Unbalanced Smith source markup: '+tag)
        n=self.nodes[self.stack.pop()];n['close_start']=self.position();n['end']=self.source.index('>',self.position())+1
    def blocks(self):
        result=[];chapter='cover'
        for node in self.nodes:
            if node['tag']=='h2':chapter=node['attrs'].get('id','')
            if node['tag'] not in BLOCK:continue
            parent=node['parent'];skip=False
            while parent is not None:
                p=self.nodes[parent]
                if p['tag'] in {'p','li','td','th','figcaption','pre'}:skip=True;break
                parent=p['parent']
            if skip:continue
            fragment=self.source[node['start']:node['end']]
            if prose(fragment):result.append(dict(node,key=f'B{len(result):04}',chapter=chapter,prose=prose(fragment),html=fragment))
        return result

def splices(source,changes):
    end=len(source)
    for start,stop,value in sorted(changes,reverse=True):
        if not 0<=start<=stop<=end:raise ValueError('Overlapping editorial source ranges')
        source=source[:start]+value+source[stop:];end=start
    return source

def apply_edits(body,record):
    if digest(normalized(body))!=record['input_semantic_sha256']:raise ValueError('Smith editorial source changed; review the new source before publishing')
    blocks={n['key']:n for n in Source(body).blocks()};changes=[]
    for edit in record['edits']:
        node=blocks[edit['block']];old=node['html']
        if digest(normalized(old))!=edit['source_sha256']:raise ValueError('Smith editorial block changed: '+edit['block'])
        new=old
        if edit['action']=='drop':new=''
        elif edit['action']=='replace':
            inner=edit['text'];math=[m[0] for m in MATH.finditer(old)]
            for i,value in reversed(list(enumerate(math))):inner=inner.replace('{M'+str(i)+'}',value)
            if re.search(r'\{M\d+\}',inner):raise ValueError('Unbound editorial math placeholder')
            new=body[node['start']:node['open_end']]+inner+body[node['close_start']:node['end']]
        elif edit['action']=='sub':
            for a,b in edit['changes']:
                if new.count(a)!=1:raise ValueError('Ambiguous editorial phrase: '+a)
                new=new.replace(a,b,1)
        else:raise ValueError('Unknown Smith editorial operation')
        if not(edit.get('retire_mathematics') or edit.get('mathematical_repair')) and [m[0] for m in MATH.finditer(old)]!=[m[0] for m in MATH.finditer(new)]:raise ValueError('Editorial operation changed mathematics: '+edit['block'])
        changes.append((node['start'],node['end'],new))
    return splices(body,changes)

def arrange(body,record):
    # Remove presentation wrappers before ordering complete source chapters.
    source=Source(body);changes=[]
    for node in source.nodes:
        classes=node['attrs'].get('class','').split()
        if (node['tag']=='section' and 'book-chapter' in classes) or (node['tag']=='details' and set(classes)&{'book-history','book-reference'}):
            changes.extend([(node['start'],node['open_end'],''),(node['close_start'],node['end'],'')])
    body=splices(body,changes);source=Source(body)
    tables=[]
    for marker in record.get('retired_tables',[]):
        matches=[n for n in source.nodes if n['tag']=='table' and prose(body[n['start']:n['end']]).startswith(marker)]
        if len(matches)!=1:raise ValueError('Missing editorial review table: '+marker)
        tables.append((matches[0]['start'],matches[0]['end'],''))
    body=splices(body,tables);source=Source(body)
    recovered={}
    for name,target in record.get('recover_figures',{}).items():
        found=[body[n['start']:n['end']] for n in source.nodes if n['tag']=='figure' and '/'+name+'"' in body[n['start']:n['end']]]
        if len(found)!=1:raise ValueError('Missing retained scientific figure: '+name)
        recovered.setdefault(target,[]).append(found[0])
    retire=[]
    headings=[n for n in source.nodes if n['tag'] in {'h2','h3','h4','h5','h6'}]
    for key in record['retired_subsections']:
        match=next((n for n in headings if n['attrs'].get('id')==key),None)
        if not match:raise ValueError('Missing retired subsection: '+key)
        following=next((n for n in headings if n['start']>match['start'] and int(n['tag'][1])<=int(match['tag'][1])),None)
        stop=following['start'] if following else next(n['close_start'] for n in source.nodes if n['tag']=='article')
        retire.append((match['start'],stop,''))
    body=splices(body,retire);source=Source(body)
    article=next((n for n in source.nodes if n['tag']=='article'),None)
    if not article:raise ValueError('Missing Smith article')
    inner=body[article['open_end']:article['close_start']]
    headings=list(re.finditer(r'<h2\b[^>]*id="([^"]+)"[^>]*>.*?</h2>',inner,re.S))
    sections={m[1]:inner[m.start():headings[i+1].start() if i+1<len(headings) else len(inner)] for i,m in enumerate(headings)}
    if set(sections)!=set(record['chapter_order'])|set(record['retired_chapters']):raise ValueError('Smith chapter inventory changed')
    content=inner[:headings[0].start()]+''.join(sections[k]+''.join(recovered.get(k,[])) for k in record['chapter_order'])
    # Preserve old incoming fragments as aliases beside the matching subject.
    ids=set(re.findall(r'\bid="([^"]+)"',content))
    for target,names in record['anchor_aliases'].items():
        marker=re.search(r'<(?:h[2-6]|span)\b[^>]*id="'+re.escape(target)+r'"[^>]*>',content)
        if not marker:raise ValueError('Missing editorial alias destination: '+target)
        aliases=''.join('<span id="'+name+'" class="book-anchor" aria-hidden="true"></span>' for name in names if name not in ids)
        content=content[:marker.start()]+aliases+content[marker.start():];ids.update(names)
    body=body[:article['open_end']]+content+body[article['close_start']:]
    toc=re.search(r'<details id="contents" class="contents" open>.*?</details>',body,re.S)
    if not toc:raise ValueError('Missing Smith contents')
    links=re.findall(r'<h2\b[^>]*id="([^"]+)"[^>]*>(.*?)</h2>',content,re.S)
    value=('<details id="contents" class="contents" open><summary>Contents</summary><p class="contents-title">Smith chart and RLC synthesis</p><div class="toc-links">'+''.join('<a href="#'+key+'">'+re.sub('<[^>]+>','',title)+'</a>' for key,title in links)+'</div><div class="toc-progress">Reading progress<progress id="reading-progress" max="100" value="0" aria-label="Reading progress"></progress></div></details>')
    return body[:toc.start()]+value+body[toc.end():]

def number_figures(body,record):
    source=Source(body);figures=[n for n in source.nodes if n['tag']=='figure' and 'research-figure' in n['attrs'].get('class','').split()]
    old_numbers={}
    for index,node in enumerate(figures,1):
        fragment=body[node['start']:node['end']]
        match=re.search(r'<figcaption>(?:<(?:strong|em)>)?Figure (\d+)\.',fragment)
        if match:
            old=int(match[1])
            if old in old_numbers:raise ValueError('Repeated source figure number')
            old_numbers[old]=index
    def references(text):return re.sub(r'\bFigure (\d+)\b',lambda m:'Figure '+str(old_numbers.get(int(m[1]),int(m[1]))),text)
    result=[];start=0
    for index,node in enumerate(figures,1):
        result.append(references(body[start:node['start']]))
        fragment=body[node['start']:node['end']]
        image=re.search(r'<img\b[^>]*src="([^"]+)"',fragment)
        name=image[1].split('/')[-1]
        if name in record.get('figure_captions',{}):
            caption=html.escape(record['figure_captions'][name])
            fragment=re.sub(r'<figcaption>.*?</figcaption>','<figcaption>'+caption+'</figcaption>',fragment,flags=re.S)
            fragment=re.sub(r'(<img\b[^>]*\balt=")[^"]*"',lambda m:m[1]+caption+'"',fragment,count=1)
        fragment=re.sub(r'(<div class="figure-heading"><span>).*?(</span>)',lambda m:m[1]+'Figure '+str(index)+m[2],fragment,count=1,flags=re.S)
        # Remove the original prefix inside its existing emphasis wrapper, then
        # add exactly one final number outside that wrapper.
        fragment=re.sub(r'(<figcaption>(?:<(?:strong|em)>)?)Figure \d+\.\s*',r'\1',fragment,count=1)
        fragment=fragment.replace('<figcaption>','<figcaption><strong>Figure '+str(index)+'.</strong> ',1)
        fragment=re.sub(r'aria-label="Open figure \d+ at full size"','aria-label="Open figure '+str(index)+' at full size"',fragment)
        if not re.search(r'<figure\b[^>]*\bid=',fragment):fragment=fragment.replace('<figure ',f'<figure id="smith-figure-{index}" ',1)
        result.append(fragment);start=node['end']
    result.append(references(body[start:]));return ''.join(result)

def polish_text(body,rules):
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False);self.stack=[];self.changes=[];self.counts=[0]*len(rules);self.lines=[0]+[m.end() for m in re.finditer('\n',body)]
        def handle_starttag(self,tag,attrs):
            if tag not in VOID:self.stack.append((tag,dict(attrs)))
        def handle_startendtag(self,tag,attrs):pass
        def handle_endtag(self,tag):
            if self.stack:self.stack.pop()
        def handle_data(self,value):
            if any(t in {'pre','code','script','style','a'} or 'arithmatex' in a.get('class','') or a.get('class','').startswith('math ') for t,a in self.stack):return
            def transform(text):
                for i,rule in enumerate(rules):
                    text,n=re.subn(rule['pattern'],rule['replacement'],text,flags=re.I);self.counts[i]+=n
                return text
            result=[];start=0
            for match in MATH.finditer(value):result.extend([transform(value[start:match.start()]),match[0]]);start=match.end()
            result.append(transform(value[start:]));new=''.join(result)
            if new!=value:
                line,column=self.getpos();p=self.lines[line-1]+column;self.changes.append((p,p+len(value),new))
    parser=Text();parser.feed(body)
    for count,rule in zip(parser.counts,rules):
        if rule.get('expected_count') is not None and count!=rule['expected_count']:raise ValueError('Smith proofreading rule count changed: '+rule['pattern'])
    return splices(body,parser.changes),parser.counts

def reader_support(root,body):
    """Add source-bound explanations and semantic reading aids to the edition."""
    from smith_chart_continuation import render,load
    record=json.loads((root/'research/smith-chart/unified/reader-support.json').read_bytes())
    archive_files=None
    for edit in record['edits']:
        repair=edit.get('mathematical_repair')
        if not repair:continue
        if 'archive' in repair:
            if archive_files is None:_,archive_files=load(root)
            raw=archive_files[repair['archive']][repair['member']]
        else:raw=(root/repair['source_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=repair['source_sha256'] or repair['source_fragment'] not in raw.decode('utf-8').replace('\r\n','\n'):
            raise ValueError('Smith reader restoration source changed')
    body=apply_edits(body,record)
    guide_raw=(root/record['guide']).read_bytes()
    if hashlib.sha256(guide_raw).hexdigest()!=record['guide_sha256']:
        raise ValueError('Smith reader guide changed without review')
    guide=render(guide_raw.decode('utf-8'))
    guide=re.sub(r'(<h2\b[^>]*\bid=")[^"]+"',r'\1reading-guide"',guide,count=1)
    guide=re.sub(r'(<h[3-6]\b[^>]*\bid=")([^"]+)"',r'\1reader-guide--\2"',guide)
    article=next(n for n in Source(body).nodes if n['tag']=='article')
    body=body[:article['open_end']]+'<section class="reader-guide" aria-labelledby="reading-guide">'+guide+'</section>'+body[article['open_end']:]
    body=body.replace('<div class="toc-links">','<div class="toc-links"><a href="#reading-guide">Reading guide and engineering meaning</a>',1)
    body=re.sub(r'(<nav class="quick-nav"[^>]*>)',r'\1<a href="#reading-guide">Reading guide</a>',body,count=1)
    source=Source(body);changes=[]
    figures=[n for n in source.nodes if n['tag']=='figure']
    if len(figures)!=len(record['figures']):raise ValueError('Smith described figure inventory changed')
    for index,(node,entry) in enumerate(zip(figures,record['figures']),1):
        fragment=body[node['start']:node['end']]
        image=re.search(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>',fragment)
        if not image or image[1].split('/')[-1]!=entry['file'] or entry['number']!=index:
            raise ValueError('Smith described figure order changed')
        if entry.get('path'):raw=(root/entry['path']).read_bytes()
        else:
            if archive_files is None:_,archive_files=load(root)
            raw=archive_files[entry['archive']][entry['member']]
        if hashlib.sha256(raw).hexdigest()!=entry['source_sha256']:
            raise ValueError('Smith described figure source changed')
        image_tag=re.sub(r'\balt="[^"]*"',lambda m:'alt="'+html.escape(entry['alt'],quote=True)+'"',image[0])
        if 'aria-details=' in image_tag:raise ValueError('Unexpected pre-existing figure detail binding')
        detail_id='smith-figure-description-'+str(index)
        image_tag=image_tag[:-1]+' aria-details="'+detail_id+'">'
        fragment=fragment[:image.start()]+image_tag+fragment[image.end():]
        fragment=re.sub(r'(<button\b[^>]*\bclass="[^"]*\bfigure-open\b[^"]*"[^>]*>).*?(</button>)',r'\1Open diagram\2',fragment,flags=re.S)
        caption=re.search(r'<figcaption([^>]*)>(.*?)</figcaption>',fragment,re.S)
        if not caption:raise ValueError('Missing described Smith figure caption')
        existing_id=re.search(r'\bid="([^"]+)"',caption[1])
        caption_id=existing_id[1] if existing_id else 'smith-figure-caption-'+str(index)
        caption_attrs=caption[1] if existing_id else caption[1]+' id="'+caption_id+'"'
        caption_body=caption[2]
        if entry.get('caption'):
            if MATH.search(caption_body):raise ValueError('Descriptive caption would replace retained mathematics')
            caption_body='<strong>Figure '+str(index)+'.</strong> '+html.escape(entry['caption'])
        elif prose(caption_body)[-1] not in '.!?':caption_body+='.'
        replacement='<figcaption'+caption_attrs+'>'+caption_body+'</figcaption>'
        fragment=fragment[:caption.start()]+replacement+fragment[caption.end():]
        description=('<details class="figure-description" id="'+detail_id+'"><summary>Text description of figure '+str(index)+
            '</summary><div><p>'+html.escape(entry['description'])+'</p></div></details>')
        fragment=fragment.replace('</figure>',description+'</figure>',1)
        changes.append((node['start'],node['end'],fragment))
    body=splices(body,changes)
    source=Source(body);changes=[];wrappers=set();heading='Reading example';table_number=0;pre_number=0
    for node in source.nodes:
        tag=node['tag'];attrs=node['attrs']
        if tag in {'h2','h3'}:heading=prose(body[node['start']:node['end']]).replace('[math]','the stated parameter')
        if tag=='table':
            table_number+=1;fragment=body[node['start']:node['end']]
            if '<caption' not in fragment:
                title=html.escape('Table '+str(table_number)+'. '+heading)
                end=fragment.index('>')+1
                fragment=fragment[:end]+'<caption class="table-caption">'+title+'</caption>'+fragment[end:]
            fragment=re.sub(r'<th(\s[^>]*)?>',lambda m:'<th'+(m[1] or '')+('' if 'scope=' in (m[1] or '') else ' scope="col"')+'>',fragment)
            parent=source.nodes[node['parent']] if node['parent'] is not None else None
            if not parent or not set(parent['attrs'].get('class','').split())&{'table-wrap','table-scroll'}:
                fragment='<div class="table-scroll" tabindex="0" role="region" aria-label="'+html.escape('Scrollable table '+str(table_number)+'. '+heading,quote=True)+'">'+fragment+'</div>'
            elif parent['start'] not in wrappers:
                opening=body[parent['start']:parent['open_end']]
                for attr,value in [('tabindex','0'),('role','region'),('aria-label','Scrollable table '+str(table_number)+'. '+heading)]:
                    if attr not in parent['attrs']:opening=opening[:-1]+' '+attr+'="'+html.escape(value,quote=True)+'">'
                changes.append((parent['start'],parent['open_end'],opening));wrappers.add(parent['start'])
            changes.append((node['start'],node['end'],fragment))
        if tag=='pre' and 'tabindex' not in attrs:
            pre_number+=1;opening=body[node['start']:node['open_end']]
            label=html.escape('Preformatted example '+str(pre_number)+'. '+heading,quote=True)
            changes.append((node['start'],node['open_end'],opening[:-1]+' tabindex="0" role="region" aria-label="'+label+'">'))
    return splices(body,changes)


def finalize(root,body,site=None):
    record=json.loads((root/EDITION).read_bytes())
    for edit in record['edits']:
        repair=edit.get('mathematical_repair')
        if not repair:continue
        if 'archive' in repair:
            from smith_chart_continuation import load
            _,files=load(root);raw=files[repair['archive']][repair['member']]
        else:raw=(root/repair['source_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=repair['source_sha256'] or repair['source_fragment'] not in raw.decode('utf-8').replace('\r\n','\n'):raise ValueError('Forced mathematical correction source changed')
    result=number_figures(arrange(apply_edits(body,record),record),record)
    for figure in record.get('figure_editions',[]):
        old=(root/figure['source']).read_bytes();new=(root/figure['edition']).read_bytes()
        if hashlib.sha256(old).hexdigest()!=figure['source_sha256'] or hashlib.sha256(new).hexdigest()!=figure['edition_sha256']:raise ValueError('Smith figure edition source changed')
        expected=old.decode('utf-8')
        for before,after in figure['text_changes']:
            if expected.count(before)!=1:raise ValueError('Ambiguous Smith figure text change')
            expected=expected.replace(before,after,1)
        if expected.encode('utf-8')!=new:raise ValueError('Unrecorded Smith figure change')
        if site:
            target=site.resolve('collection','research/smith-chart/unified/README.md','read/smith-chart/research.html',figure['edition'].removeprefix('research/smith-chart/unified/'),True)
        else:target='../../assets/source/collection/'+figure['edition']
        result=re.sub(r'\b(href|src|srcset)="([^"]*)"',lambda m:m[1]+'="'+target+'"' if html.unescape(m[2]).split('?',1)[0].endswith('/'+figure['source']) else m[0],result)
    result=re.sub(r'<footer class="end-note">.*?</footer>','<footer class="end-note">'+html.escape(record['footer_text'])+'</footer>',result,flags=re.S)
    for before,after in record.get('chrome_edits',[]):
        if result.count(before)!=1:raise ValueError('Smith reading chrome changed')
        result=result.replace(before,after,1)
    result,_=polish_text(result,record.get('text_rules',[]))
    for phrase in record['forbidden_visible_phrases']:
        if re.search(phrase,prose(result),re.I):raise ValueError('Obsolete research-log language in final reading: '+phrase)
    return reader_support(root,result)
