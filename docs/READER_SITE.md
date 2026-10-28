# Maintain the reader website

The public site is at <https://KomorebiP.github.io/Operation-KOMOREBI/>.
Its source is in this repository. The site combines maintained collection
pages with documentation from two explicitly pinned library revisions.

## Sources

| Content | Source |
|---|---|
| Work titles and source ownership | [Source index](../manifests/source-components.json) and import receipts |
| Completion, Lean coverage, confidence and limits | [Project status](../manifests/project-status.json) |
| Selected reading, proof, Lean and code files | [Browse resources](../manifests/browse-resources.json) |
| Introductory terminology and background advice | [Reader experience](../manifests/reader-experience.json) |
| Hand-worked calculations and exercises | [Example index](HAND_WORKED_EXAMPLES.md), [tutorial pages](examples/) and [exact arithmetic checker](../tools/check_hand_examples.py) |
| Paper I statement and declaration locations | [Claim navigation](../manifests/claim-navigation.json), bound to its retained source records |
| Library source revisions | [Website library revisions](../manifests/reader-site-libraries.json) |
| Page structure and browser behavior | [Website assets](../website/assets/) and [site builder](../tools/build_reader_site.py) |

Reading routes, glossary, download guides and work introductions are generated
with the collection's normal status command. Edit their source records or
templates. Keep each claim's exact recorded scope when changing navigation.

The `learning_topics` records in the reader experience manifest generate the
[topic map](LEARNING_MAP.md), the source routes at the end of each tutorial,
and return links on the related work pages. Edit tutorial explanations above
the `learning-navigation` marker. The status command replaces the section
below that marker. A subject route does not establish a theorem correspondence.

## Build locally

Use a complete collection checkout and separate checkouts of the two libraries
at the revisions in `manifests/reader-site-libraries.json`. Python 3.13 is used
by the website workflow. Choose fresh output directories for each build.

```text
python -m pip install -r website/requirements.txt
python -B tools/update_completion_status.py --check
python -B tools/fetch_reader_runtime.py --output ../reader-runtime
python -B tools/build_reader_site.py --math-root ../komorebi-math --polyphase-root ../polyphase-float --mathjax-root ../reader-runtime --revision FULL_COLLECTION_COMMIT --output ../reader-site
python -B tools/check_reader_site.py --site ../reader-site
python -m http.server 8765 --directory ../reader-site
```

Replace `FULL_COLLECTION_COMMIT` with the output of `git rev-parse HEAD`.
The runtime fetch verifies a pinned SHA-512 digest before unpacking MathJax.
The finished site serves its math files locally. Source receipt mismatches or
missing reading files fail the build. The ZIPs identify their selected files
and do not claim to be standalone build environments.

## Publication

The [reader website workflow](../.github/workflows/reader-site.yml) builds and
checks the site on pushes and pull requests. Only a successful build on `main`
can deploy it through GitHub Pages. Pull requests receive build checks without
publication. Library revisions are pinned so a rebuild cannot silently adopt
unreviewed changes from another repository.

Update library pins deliberately after reviewing their changes and checks.
Record qualifications in the existing publication metadata only after those
runs finish successfully. A website build confirms its own navigation and
packaging scope, not new mathematical or formal verification.

The workflow also runs the documented introductory Python and C examples.
It checks the 15 hand-worked examples with exact rational arithmetic.
The library workflows retain their broader platform and release checks.

[Accessibility and known limits](ACCESSIBILITY.md) · [Repository maintenance](MAINTENANCE.md)
