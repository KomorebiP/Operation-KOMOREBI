# Editorial self-review of the reviewed-core reader

Scope: changed title matter, review-status paragraphs, bibliography scope text, the chapter 4 transition, the new formal correspondence chapter, and typesetting configuration. This is a conservative proofreading pass, not a new whole-manuscript correctness audit.

The 27 original proof environments, 39 theorem/proposition/corollary/counterexample environments, 54 display blocks, and every inline math span are byte-identical to the source anchor. No existing mathematical token or assumption was changed. The separate formal correspondence chapter states the release scope and evidence boundaries; its final acceptance sentence was synchronized after both cold formal gates and their comparison passed. The accepted record is pinned by hash in `SOURCE_PROVENANCE.json`.

The typesetting changes use Palatino-compatible text/math, navy headings, a restrained cover, slightly adjusted margins and line spacing, and a compact source map. One short chapter-ending transition was joined to its preceding prose paragraph to avoid a page containing only that transition. No bibliography attribution was removed.

The actual diff is in `EDITORIAL_DIFF.patch`; the automated preservation receipt identifies the protected spans and hashes. Fresh PDF compilation, navigation checks, and rendered-page inspection are separate evidence from this prose review.
