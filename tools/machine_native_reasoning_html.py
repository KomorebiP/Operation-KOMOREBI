"""Publish the complete source-bound MNR reading edition in shared reader chrome."""
import html,json,posixpath,re
from pathlib import Path
from reading_payload import PREFIX,decode,sha
from machine_native_reasoning_expanded import PAGE,WORK,BOOK,RECORD
MANIFEST=PREFIX+'READING.json'
SCRIPT='assets/mnr-chapter.js'
STYLE='assets/mnr-reading.css'

def load(root):
    data=json.loads((root/MANIFEST).read_bytes())
    if len(data['pages'])!=121 or [p['chapter'] for p in data['pages'] if p['chapter']]!=list(range(1,98)):raise ValueError('Incomplete MNR HTML edition')
    if data['proofs']!=527 or data['statement_count']!=803 or data['mathjax_validation']['errors']:raise ValueError('MNR conversion checks changed')
    if len(data['images'])!=141:raise ValueError('MNR figures incomplete')
    for kind in ('sources','images'):
        for item in data[kind]:
            path=PREFIX+('figures/'+item['file'] if kind=='images' else item['path'])
            if sha((root/path).read_bytes())!=item['sha256']:raise ValueError('MNR retained asset changed: '+path)
    body_started=False
    for page in data['pages']:
        if page['chapter']:body_started=True
        elif body_started:page['part']='Glossary, appendices, and references'
    return data

def configuration(data):
    groups=[];previous=None;chapters=[]
    for p in data['pages']:
        path='read/'+WORK+'/'+p['file'];title=(str(p['chapter'])+'. ' if p['chapter'] else '')+p['title']
        chapters.append(dict(url=path,title=title))
        if p['part']!=previous:groups.append(dict(start=path,title=p['part']));previous=p['part']
    return dict(work=WORK,label='Machine-Native Reasoning',title='Machine-Native Reasoning',index=PAGE,chapters=chapters,
      contents_groups=groups,menu_current_group_only=True,menu_index_only=True,footer_index_only=True,compact_chrome=True)

def publish(site):
    from reading_navigation import navigation,outline,resources
    from build_reader_site import github,REPOSITORY
    from reader_display import EXTRA_EDITIONS
    data=load(site.root);config=configuration(data);EXTRA_EDITIONS[WORK]=config;e=html.escape
    base='https://raw.githubusercontent.com/'+REPOSITORY+'/'+site.revision+'/'+PREFIX
    for asset in (SCRIPT,STYLE):
        target=site.output/asset;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((site.root/'website'/asset).read_bytes())
    added=0
    for p in data['pages']:
        path='read/'+WORK+'/'+p['file'];payload=dict(p['payload']);payload['path']=PREFIX+payload.pop('part');payload['url']=base+payload['path'][len(PREFIX):];payload['figure_root']=base+'figures/'
        full=decode(payload,site.root)
        title=(str(p['chapter'])+'. ' if p['chapter'] else '')+p['title']
        contents='<ol>'+''.join('<li><a href="#'+e(h['id'],quote=True)+'">'+e(h['title'])+'</a></li>' for h in p['headings'] if h['level']==2)+'</ol>'
        source=github(REPOSITORY,site.revision,PREFIX+p['source'],p['line'])
        resource='<a href="book.html">PDF and editable source</a> · <a href="'+e(source,quote=True)+'">Chapter source</a> · <a href="reconstructed-edition.html#edition">About this edition</a>'
        body='<h1 id="'+e(p['id'],quote=True)+'">'+e(title)+'</h1>'+navigation(config,path)
        if p['headings']:body+=outline(contents)
        body+='<div class="mnr-loading" id="mnr-loading" role="status" aria-live="polite"><span>Loading chapter…</span> <button type="button" id="mnr-retry" hidden>Retry</button></div>'
        body+=resources(resource)
        body+='<article id="chapter-text" class="readable-chapter mnr-chapter" data-reading-no-notation="true" aria-busy="true">'+p['preview']+'</article>'
        body+='<noscript><p>Full chapters require JavaScript. <a href="book.html">Read or download the complete PDF</a>.</p></noscript>'+navigation(config,path,'bottom')
        body+='<script type="application/json" id="mnr-payload">'+json.dumps(payload,separators=(',',':'))+'</script>'
        site.page(path,title+' · Machine-Native Reasoning',body,source)
        doc=(site.output/path).read_text(encoding='utf-8')
        # Initialize passage tools only after the full article has arrived.
        doc=re.sub(r'<script defer src="([^"]*/(?:reader|reading-tools)\.js[^\"]*)"></script>',r'<script type="application/x-mnr-deferred" data-src="\1"></script>',doc)
        extras='<link rel="stylesheet" href="'+site.rel(STYLE,path)+'?v='+sha((site.root/'website'/STYLE).read_bytes())[:12]+'"><script defer src="'+site.rel(SCRIPT,path)+'?v='+sha((site.root/'website'/SCRIPT).read_bytes())[:12]+'"></script>'
        doc=doc.replace('</head>',extras+'</head>');site.write(path,doc);added+=len(doc.encode())
        preview=re.sub('<[^>]+>',' ',p['preview'])
        site.search.append(dict(title='Machine-Native Reasoning / '+title,group='Collection',kind='Papers and source',work_ids=[WORK],url=path,text=html.unescape(preview)+' '+p['part']))
    body='<h1>Machine-Native Reasoning</h1><p class="lead">A complete reading edition in 97 chapters, with figures, proofs, references, and chapter navigation.</p>'
    body+='<p><a class="button" href="preface.html">Start reading</a> <a class="button" href="chapter-01.html">Chapter 1</a> <a href="book.html">PDF and editable source</a></p>'
    previous=None
    for p in data['pages']:
        if p['part']!=previous:
            if previous is not None:body+='</ol></details>'
            body+='<details'+(' open' if previous is None else '')+'><summary>'+e(p['part'])+'</summary><ol>';previous=p['part']
        title=(str(p['chapter'])+'. ' if p['chapter'] else '')+p['title']
        body+='<li'+(' id="chapter-'+str(p['chapter'])+'"' if p['chapter'] else '')+'><a href="'+e(p['file'],quote=True)+'">'+e(title)+'</a></li>'
    body+='</ol></details><h2 id="edition">About this edition</h2><p>This separately identified reconstruction brings together the expanded book in 13 parts. It preserves the source mathematics and adds a browser reading layout. The accepted 27-result core retains its separate scope. Production and rendering checks are not an independent proof audit.</p>'
    body+='<p><a href="book.html">Complete 977-page PDF and editable TeX</a> · <a href="../../'+RECORD+'">Publication record</a> · <a href="../../collection/works/'+WORK+'.html">Work overview</a></p>'
    site.page(PAGE,'Machine-Native Reasoning: complete reading edition',body,github(REPOSITORY,site.revision,MANIFEST))
    # Replace the older PDF-only chapter search entries, keeping one index entry.
    site.search[:]=[r for r in site.search if not (r['url'].startswith(PAGE+'#chapter-'))]
    record=json.loads((site.output/RECORD).read_bytes());record['html_reading']=dict(index=PAGE,pages=len(data['pages']),chapters=97,manifest=MANIFEST,math_expressions=16476,new_proof_audit=False)
    site.write(RECORD,json.dumps(record))
    site.write('documents/mnr-html-reading.json',json.dumps(dict(schema=1,pages=[dict(url='read/'+WORK+'/'+p['file'],payload=p['payload']) for p in data['pages']],manifest=MANIFEST,chapter_shell_bytes=added,proofs=527,statements=803)))
    if added>1800000:raise ValueError('MNR chapter shells exceed their Pages budget')
    return dict(pages=121,chapters=97,shell_bytes=added)

def verify(root):
    from check_reader_site import Page as Parsed
    root=Path(root);record=json.loads((root/'documents/mnr-html-reading.json').read_bytes());proofs=statements=0
    for i,p in enumerate(record['pages']):
        text=(root/p['url']).read_text(encoding='utf-8');parsed=Parsed(text)
        if len(parsed.ids)!=len(set(parsed.ids)):raise ValueError('Duplicate MNR chapter anchor: '+p['url'])
        from reading_payload import expand
        full=expand(text);proofs+=len(re.findall(r'class="proof"',full));statements+=len(re.findall(r'data-statement-number=',full))
        for direction,j in [('prev',i-1),('next',i+1)]:
            if 0<=j<len(record['pages']):
                target=posixpath.basename(record['pages'][j]['url'])
                if not re.search(r'rel="'+direction+'" href="'+re.escape(target)+'"',text):raise ValueError('MNR chapter sequence changed')
    if (proofs,statements)!=(527,803):raise ValueError('MNR article inventory changed')
    return dict(pages=len(record['pages']),proofs=proofs,statements=statements)
