"""A browsable index and explicit evidence for the existing finite connections."""
import csv
import hashlib
import io
import json
from html import escape as e

OPERATIONS = {'alternating signs':'alternating', 'absolute values':'absolute', 'first differences':'difference', 'partial sums':'sum'}


def connection_graph(entries):
    lookup = {entry['id']:entry for entry in entries}
    edges = []
    for source in entries:
        values = list(map(int, source['terms']))
        for link in source['connections']:
            target = lookup[link['id']]
            operation = OPERATIONS[link['transform']]
            if link['matched_terms'] != 12 or link['source_start'] < (1 if operation == 'difference' else 0) or link['target_start'] < 0 or link['source_start']+12 > len(values) or link['target_start']+12 > len(target['terms']):
                raise ValueError('Connection indices must describe twelve defined stored terms')
            rows = []
            for k in range(link['matched_terms']):
                n, m = link['source_start']+k, link['target_start']+k
                value = {'alternating':lambda:(-1)**n*values[n], 'absolute':lambda:abs(values[n]),
                    'difference':lambda:values[n]-values[n-1], 'sum':lambda:sum(values[:n+1])}[operation]()
                if str(value) != target['terms'][m]:
                    raise ValueError('Connection evidence differs from the stored terms')
                rows.append(dict(source_n=n, source_value=source['terms'][n], transformed_value=str(value), target_n=m, target_value=target['terms'][m]))
            key=source['id']+'-'+operation+'-'+target['id']+'-'+str(link['source_start'])+'-'+str(link['target_start'])
            edges.append(dict(key=key,source_id=source['id'],source_title=source['title'],target_id=target['id'],target_title=target['title'],operation=operation,label=link['transform'],source_start=link['source_start'],target_start=link['target_start'],matched_terms=link['matched_terms'],rows=rows))
    signature=json.dumps([(entry['id'],entry['terms']) for entry in entries],separators=(',',':')).encode()
    return dict(schema=1,catalogue_term_sha256=hashlib.sha256(signature).hexdigest(),
        scope='Existing exact twelve-term comparisons. Edges are directed from a transformed source to an untransformed target; indices retain the local stored conventions. These finite checks do not prove infinite sequence identities.',edges=edges)


def connection_counts(graph, identifier):
    return (sum(edge['source_id']==identifier for edge in graph['edges']), sum(edge['target_id']==identifier for edge in graph['edges']))


def connection_block(entry, graph):
    identifier=entry['id']
    blocks=[]
    for direction,key in [('From this entry','source_id'),('Into this entry','target_id')]:
        edges=[edge for edge in graph['edges'] if edge[key]==identifier]
        if not edges:
            continue
        cards=[]
        for edge in edges:
            source,target=edge['source_id'],edge['target_id']
            rows=''.join('<tr><th scope="row">'+str(row['source_n'])+'</th><td>'+row['source_value']+'</td><td>'+row['transformed_value']+'</td><td>'+str(row['target_n'])+'</td><td>'+row['target_value']+'</td></tr>' for row in edge['rows'])
            cards.append('<details class="sa-connection" id="connection-'+edge['key']+'" data-connection-key="'+edge['key']+'"><summary>'+e(edge['source_title'])+' → '+e(edge['label'])+' → '+e(edge['target_title'])+'</summary>'
                '<p><a href="'+source+'.html">'+source+'</a> supplies the source. Its '+e(edge['label'])+' at n='+str(edge['source_start'])+'–'+str(edge['source_start']+11)+' match the original terms of <a href="'+target+'.html">'+target+'</a> at n='+str(edge['target_start'])+'–'+str(edge['target_start']+11)+'. No indices are re-based in this table.</p>'
                '<div class="sa-connection-actions"><a href="'+source+'.html?study='+edge['operation']+'&amp;from='+str(edge['source_start'])+'&amp;size=12#analysis">Study the source transform</a><a href="'+target+'.html?study=raw&amp;from='+str(edge['target_start'])+'&amp;size=12#analysis">Study the matching target</a></div>'
                '<div class="table-scroll" tabindex="0" role="region" aria-label="Connection evidence '+e(source+' '+edge['label']+' '+target)+'"><table><caption>Twelve checked terms; source transform compared with original target values</caption><thead><tr><th scope="col">Source n</th><th scope="col">Source a(n)</th><th scope="col">Transformed source</th><th scope="col">Target n</th><th scope="col">Target a(n)</th></tr></thead><tbody>'+rows+'</tbody></table></div></details>')
        blocks.append('<h3>'+direction+' <span class="sa-count">'+str(len(edges))+'</span></h3>'+''.join(cards))
    return ('<section id="connections"><h2>Computed connections</h2><p>Follow a transformation in either direction through the catalogue. Expand a connection to inspect its exact values and both index ranges.</p>'
        +(''.join(blocks) if blocks else '<p>No incoming or outgoing connections from the four tested transforms were found in this catalogue.</p>')
        +'<p class="sa-note">These are the existing twelve-term checks of alternating signs, absolute values, first differences, and partial sums. A reverse listing preserves the direction of the original check; it does not infer an inverse transformation or an infinite identity.</p><p><a download href="../assets/sequence-atlas-connections.json">Download all connection evidence (JSON)</a></p></section>')


def index_csv(entries, graph):
    stream=io.StringIO(newline='')
    writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['id','title','kind','offset','N','r','oeis','public_url','connections_out','connections_in'])
    for entry in entries:
        writer.writerow([entry['id'],entry['title'],entry['kind'],entry['offset'],entry.get('N',''),entry.get('power',''),entry.get('oeis') or '',
            'https://komorebip.github.io/Operation-KOMOREBI/sequences/'+entry['id']+'.html',*connection_counts(graph,entry['id'])])
    return stream.getvalue()


def directory_block(entries, graph, cards):
    topics=sorted({tag for entry in entries for tag in entry['tags'] if not tag.startswith(('N=','r='))},key=str.casefold)
    options=''.join('<option value="'+e(tag,quote=True)+'">'+e(tag)+' ('+str(sum(tag in entry['tags'] for entry in entries))+')</option>' for tag in topics)
    bodies=[]
    letters=sorted({entry['title'][0].upper() for entry in entries})
    for letter in letters:
        rows=[]
        for entry in sorted((entry for entry in entries if entry['title'][0].upper()==letter),key=lambda entry:(entry['title'].casefold(),entry['id'])):
            identifier=entry['id'];outgoing,incoming=connection_counts(graph,identifier)
            meta=('N='+str(entry['N'])+' · r='+str(entry['power']) if entry['kind']=='reciprocal' else 'Reference sequence')
            if entry.get('oeis'): meta+=' · '+entry['oeis']
            rows.append('<tr data-index-entry="'+identifier+'"><th scope="row"><a href="sequences/'+identifier+'.html">'+identifier+'</a></th><td><a class="sa-directory-name" href="sequences/'+identifier+'.html">'+e(entry['title'])+'</a><span class="sa-directory-meta">'+e(meta)+'</span><p class="sa-directory-terms">n=0: '+e(', '.join(entry['terms'][:4]))+'…</p><div class="sa-directory-actions"><a href="sequences/'+identifier+'.html#analysis">Study terms</a>'+('<a href="sequences/'+identifier+'.html#connections">Connections: '+str(outgoing)+' out · '+str(incoming)+' in</a>' if outgoing+incoming else '')+'</div></td></tr>')
        bodies.append('<tbody data-index-group="'+letter+'"><tr class="sa-directory-letter"><th id="index-'+letter+'" tabindex="-1" colspan="2" scope="rowgroup">'+letter+'</th></tr>'+''.join(rows)+'</tbody>')
    families={(entry['N'],entry['power']):entry for entry in entries if entry['kind']=='reciprocal'}
    matrix=''.join('<tr><th scope="row">'+str(N)+'</th>'+''.join('<td><a href="sequences/'+families[N,r]['id']+'.html" aria-label="'+e(families[N,r]['title']+' '+families[N,r]['id'],quote=True)+'">'+families[N,r]['id']+'</a></td>' for r in range(1,4))+'</tr>' for N in range(2,9))
    return ('<section id="catalogue" aria-labelledby="catalogue-title"><h2 id="catalogue-title">The sequence directory</h2><p>Browse by name, topic, or stable identifier. Each entry links to its definition, exact terms, study tools, and available connections.</p>'
        '<form id="sa-directory-form" class="sa-directory-controls" hidden><label for="sa-directory-query">Filter the directory<input id="sa-directory-query" type="search" maxlength="20000" placeholder="Name, KSEQ7, oeis:A000364, or terms" aria-describedby="sa-directory-help"></label><label for="sa-directory-topic">Topic<select id="sa-directory-topic"><option value="">All topics</option>'+options+'</select></label><label for="sa-directory-order">Order<select id="sa-directory-order"><option value="name">Alphabetical</option><option value="id">Identifier</option></select></label><label class="sa-check" for="sa-directory-connected"><input id="sa-directory-connected" type="checkbox"> Has computed connections</label><div class="sa-toolbar"><button type="submit">Apply filters</button><button type="button" id="sa-directory-clear">Reset directory</button><button type="button" id="sa-directory-share">Copy directory link</button></div></form>'
        '<p id="sa-directory-help" class="sa-note">Filter with the same words, fields, and exact integer patterns as Browse. Directory filters are separate from the Browse search.</p><p id="sa-directory-error" class="sa-error" role="alert" hidden></p><p id="sa-directory-status" role="status" aria-live="polite" aria-atomic="true">'+str(len(entries))+' entries, alphabetically indexed.</p>'
        '<label id="sa-directory-copy-fallback" for="sa-directory-copy-text" hidden>Directory link<textarea id="sa-directory-copy-text" readonly></textarea></label>'
        '<nav class="sa-directory-alphabet" aria-label="Alphabetical sequence index">'+''.join('<a href="#index-'+letter+'" data-index-jump="'+letter+'">'+letter+'</a>' for letter in letters)+'</nav>'
        '<div class="table-scroll sa-directory-region" role="region" aria-label="Sequence directory" tabindex="0"><table id="sa-directory-table" class="sa-directory-table"><caption>All entries, arranged by name</caption><thead><tr><th scope="col">Identifier</th><th scope="col">Sequence and tools</th></tr></thead>'+''.join(bodies)+'</table></div><p id="sa-directory-empty" hidden>No entries match these filters. Reset the directory or try fewer search terms.</p>'
        '<details class="sa-family-index"><summary>Reciprocal family index: N × r</summary><p>N is the ordinary-degree spacing; r is the fixed reciprocal power. The compressed index n corresponds to degree Nn. Each cell opens the definition for that pair.</p><div class="table-scroll" tabindex="0" role="region" aria-label="Reciprocal family index"><table><caption>All 21 reciprocal entries</caption><thead><tr><th scope="col">N</th><th scope="col">r=1</th><th scope="col">r=2</th><th scope="col">r=3</th></tr></thead><tbody>'+matrix+'</tbody></table></div></details>'
        '<p class="sa-directory-downloads"><a download href="assets/sequence-atlas-index.csv">Download the full index (CSV)</a> · <a download href="assets/sequence-atlas-connections.json">Download connection evidence (JSON)</a></p>'
        '<details class="sa-expanded-catalogue"><summary>Expanded catalogue cards: formulas and sources</summary><div class="sa-catalogue">'+cards+'</div></details><p class="sa-note">Topic and alphabetical browsing takes inspiration from the <a href="https://oeis.org/wiki/Index_to_OEIS">OEIS index</a>. This directory covers the Komorebi catalogue.</p></section>')
