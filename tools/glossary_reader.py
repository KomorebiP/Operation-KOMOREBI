"""A local lookup over the glossary's maintained definitions and subject groups."""
import html
import re


def glossary_return_links(content, config):
    """Add a return route after each complete entry, retaining its original HTML."""
    inserts = []
    for term in config['glossary']:
        marker = '<p><a id="'+html.escape(term['id'], quote=True)+'"></a></p>'
        if content.count(marker) != 1:
            raise ValueError('Glossary entry anchor changed: '+term['id'])
        start = content.index(marker)+len(marker)
        boundary = re.search(r'<p><a id=|<h2\b', content[start:])
        inserts.append(start+boundary.start() if boundary else len(content))
    link = '<p class="glossary-return"><a href="#glossary-lookup">Back to glossary lookup</a></p>'
    for end in sorted(inserts, reverse=True):
        content = content[:end]+link+content[end:]
    return content


def glossary_lookup(config):
    e = html.escape
    sections = {s['id']: s['title'] for s in config['glossary_sections']}
    terms = sorted(config['glossary'], key=lambda t: t['term'].casefold())
    body = ('<section id="glossary-lookup" class="glossary-lookup" aria-labelledby="glossary-lookup-title">'
            '<h2 id="glossary-lookup-title">Find a glossary term</h2>'
            '<p id="glossary-help">Search a term or words in its definition. Matches link to the full entry, '
            'with examples and related terms. You can also browse the subjects and alphabetical index below.</p>'
            '<noscript><p>Quick lookup needs JavaScript. Use the subject links and alphabetical index below, or your browser’s Find command.</p></noscript>'
            '<form id="glossary-form" role="search" aria-label="Glossary" aria-describedby="glossary-help" hidden>'
            '<label for="glossary-query">Term or words in a definition</label>'
            '<input id="glossary-query" type="search" name="q" autocomplete="off">'
            '<label for="glossary-subject">Subject</label><select id="glossary-subject" name="subject">'
            '<option value="">All subjects</option>')
    body += ''.join('<option value="'+e(key, quote=True)+'">'+e(title)+'</option>' for key, title in sections.items())
    body += ('</select><div class="glossary-actions"><button type="submit">Find terms</button>'
             '<button type="reset">Clear lookup</button></div></form>'
             '<p id="glossary-status" role="status" aria-atomic="true" hidden></p>'
             '<div id="glossary-matches" hidden><h3 id="glossary-results-title" tabindex="-1">Matching terms</h3>'
             '<ul id="glossary-results">')
    for term in terms:
        subject = sections[term['section']]
        search = term['term']+' '+term['definition']+' '+term.get('note', '')
        body += ('<li data-glossary-entry data-subject="'+e(term['section'], quote=True)+'" '
                 'data-term="'+e(term['term'], quote=True)+'" data-search="'+e(search, quote=True)+'">'
                 '<h4><a href="#'+e(term['id'], quote=True)+'">'+e(term['term'])+'</a></h4>'
                 '<p class="glossary-subject">'+e(subject)+'</p><p>'+e(term['definition'])+'</p>')
        if term.get('note'):
            body += '<p><strong>Keep in mind:</strong> '+e(term['note'])+'</p>'
        body += '</li>'
    return body+'</ul></div></section>'
