"""Browser-local saved places, without adding to the manuscript content."""
import html
import re


def saveable(path):
    return path.startswith(('collection/', 'read/', 'math/', 'polyphase/')) or path in {
        'interactive.html', 'signal-lab.html', 'playground.html'}


def controls(site, path, title):
    e = html.escape
    return ('<div class="reading-save" data-reading-save data-page-title="'+e(title, quote=True)+'" hidden>'
            '<button type="button" class="reading-save-button" data-save-page aria-pressed="false">'
            '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false">'
            '<path d="M5 3h10v14l-5-3-5 3z"/></svg><span>Save page</span></button>'
            '<a data-saved-reading-link href="'+e(site.rel('reading-list.html', path), quote=True)+'">Saved reading</a>'
            '<span class="reading-save-status" role="status" aria-live="polite"></span></div>')


def enhance(site, path, title, body):
    if not saveable(path):
        return body
    return re.sub(r'</h1>', lambda match: match[0]+controls(site, path, title), body, count=1)


def build(site):
    body = ('<section class="reading-list-page" aria-labelledby="saved-reading-title">'
            '<p class="eyebrow">Your reading desk</p><h1 id="saved-reading-title">Saved reading</h1>'
            '<p class="lede">Keep a paper close. Return to the passage that mattered.</p>'
            '<p>Use <strong>Save page</strong> on a reading page, or the bookmark beside a section heading. '
            'Your saved places stay in this browser.</p>'
            '<div data-reading-list hidden><label for="saved-reading-query">Find a saved place</label>'
            '<input id="saved-reading-query" type="search" placeholder="Title, paper or section" autocomplete="off">'
            '<p class="saved-reading-count" role="status" aria-live="polite"></p>'
            '<ol class="reading-list-items"></ol><div class="reading-list-empty">'
            '<h2>Your next reading session starts here.</h2><p>Save a work or a useful passage as you explore.</p>'
            '<p><a class="button" href="read/index.html">Read the papers</a> '
            '<a href="collection/READING_ROUTES.html">Find a reading route</a></p></div>'
            '<p class="reading-list-status" role="status" aria-live="polite"></p></div>'
            '<noscript><p>Saving and showing your reading list needs JavaScript. '
            'You can also use your browser’s bookmarks.</p></noscript>'
            '<p class="reading-list-footer"><a href="works.html">Explore the collection</a> · '
            '<a href="side-by-side.html">Open a paired reading session</a></p></section>')
    site.page('reading-list.html', 'Saved reading', body)
