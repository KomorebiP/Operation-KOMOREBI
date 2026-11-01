"""Editorial paper introductions and links into existing source-bound results."""
import html
import json

INTRODUCTIONS='manifests/paper-introductions.json'


def load_introductions(reader):
    from claim_navigation import PAPERS
    data=json.loads((reader.site.root/INTRODUCTIONS).read_bytes())
    if data.get('schema')!=1 or set(data.get('papers',{}))!=set(PAPERS):
        raise ValueError('Paper introductions must cover the twelve core papers exactly')
    claims={row['id']:row for row in reader.site.claims['records']}
    topics={row['id']:row for row in reader.learning['learning_topics']}
    for work,guide in data['papers'].items():
        for field in ('question','contribution','limits'):
            if not isinstance(guide.get(field),str) or not guide[field].strip():
                raise ValueError('Missing paper introduction '+field+': '+work)
        topic=topics.get(guide.get('example'),{})
        if work not in topic.get('works',[]):raise ValueError('Example does not belong to '+work)
        claim=claims.get(guide.get('claim'),{})
        if claim.get('work_id')!=work or not claim.get('proof_line'):
            raise ValueError('Reading path needs a recorded statement and proof for '+work)
        setup=guide['setup'];source=reader.owned.get(setup['path'],{})
        if source.get('work')!=work or type(setup['line']) is not int or setup['line']<1 or not setup.get('expected'):
            raise ValueError('Invalid setup source for '+work)
        if setup.get('kind') not in {'setup','definition'}:raise ValueError('Unknown setup kind for '+work)
        reader.add(setup['path'])
    return data['papers']


def prepare_introductions(reader):
    guides=reader.paper_introductions
    for work,guide in guides.items():
        setup=guide['setup']
        lines=reader.site.read_source(reader.records[setup['path']]).decode('utf-8-sig').splitlines()
        if setup['line']>len(lines) or lines[setup['line']-1]!=setup['expected']:
            raise ValueError('Review the reading-path setup for '+work)


def reading_passage_url(reader,path,line):
    """Map an interior source line to its containing rendered passage, if any."""
    for book in getattr(reader,'readable_books',{}).values():
        for spec,raw,chapter in book.get('chapters',[]):
            if spec['source']!=path:continue
            node=next((node for node in reversed(chapter.nodes) if node['line']<=line<=node['end_line']),None)
            if node:return spec['url']+'#'+node['id']
    return None


def paper_introduction(reader,work,page):
    guide=getattr(reader,'paper_introductions',{}).get(work)
    if not guide:return ''
    from build_reader_site import document_url
    e=html.escape
    claim=next(row for row in reader.site.claims['records'] if row['id']==guide['claim'])
    topic=next(row for row in reader.learning['learning_topics'] if row['id']==guide['example'])
    setup=guide['setup']
    def passage(path,line):
        target=reading_passage_url(reader,path,line)
        return reader.site.rel(target,page) if target else reader.resolve(path,page,'L'+str(line))
    links=[('Example',topic['title'],reader.site.rel(document_url('collection',topic['example']),page)),
           ('Definition' if setup['kind']=='definition' else 'Setup',setup['label'],passage(setup['path'],setup['line'])),
           ('Result',claim['title'],passage(claim['statement_path'],claim['statement_line'])),
           ('Proof','Read the argument',passage(claim['statement_path'],claim['proof_line']))]
    if any(not target for _,_,target in links):raise ValueError('Unpublished reading-path target for '+work)
    body='<section class="paper-introduction" aria-labelledby="paper-question"><h2 id="paper-question">'+e(guide['question'])+'</h2>'
    body+='<p class="paper-contribution">'+e(guide['contribution'])+'</p>'
    body+='<p class="paper-limits"><strong>Assumptions and limits.</strong> '+e(guide['limits'])+'</p>'
    body+='<nav class="paper-reading-path" aria-label="Suggested first reading path"><h3 id="reading-path">A first reading path</h3><ol>'
    for label,title,target in links:
        body+='<li><a href="'+e(target,quote=True)+'"><span>'+e(label)+'</span>'+e(title)+'</a></li>'
    return body+'</ol></nav></section>'


def notation_help(site,page,work):
    """Progressive chapter lookup; its data is loaded only when help is opened."""
    from urllib.parse import quote
    from readable_chapters import BOOKS
    e=html.escape;label=BOOKS.get(work,{}).get('label',work)
    index=site.rel('notation/'+work+'.html',page)
    source=site.rel('notation/reader/'+work+'.json',page)+'?v='+quote(site.revision,safe='')
    controls=('<span class="chapter-notation-controls"><button type="button" class="chapter-notation-open" aria-haspopup="dialog" '
              'aria-controls="chapter-notation" hidden>Notation help</button><a class="chapter-notation-fallback" href="'+e(index,quote=True)+'">Notation index</a></span>')
    dialog=('<dialog id="chapter-notation" class="chapter-notation" aria-labelledby="chapter-notation-title" data-work="'+e(work,quote=True)+'" data-source="'+e(source,quote=True)+'">'
            '<div class="chapter-notation-heading"><h2 id="chapter-notation-title">Notation in '+e(label)+'</h2><button type="button" class="chapter-notation-close">Close</button></div>'
            '<p>Look up a symbol without leaving this chapter. Select text before opening help to search for it.</p>'
            '<form class="chapter-notation-search"><label for="chapter-notation-query">Symbol or name</label><div><input id="chapter-notation-query" type="search" autocomplete="off" placeholder="α, alpha, packet…"><button type="submit">Search</button></div></form>'
            '<p class="chapter-notation-status" role="status" aria-live="polite">Search this work’s notation.</p>'
            '<ol class="chapter-notation-results"></ol><p class="chapter-notation-note">Symbols can have different meanings in different passages. Read each result in its own context.</p>'
            '<p><a href="'+e(index,quote=True)+'">Open the full notation index</a></p></dialog>')
    return controls,dialog
