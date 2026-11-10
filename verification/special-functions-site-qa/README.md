# Special Functions browser checks

These records describe the generated local preview checked in installed Google
Chrome with Playwright on 2026-11-10. They are browser observations, not new
mathematical proof or Lean execution.

- `atlas-browser-qa.json`: all 175 atlas routes at 390 px; 1,494 source equations
  and rendered equations; image loading, document width, JavaScript errors,
  MathJax errors, and Special Functions destinations.
- `atlas-interaction-qa.json`: representative layouts at 320, 390, 768, and
  1440 px; previous/next navigation, saved-reading persistence, and no-JavaScript
  reading.
- `atlas-followup-qa.json`: guided-reading links and the hidden MathML overflow
  correction, including unchanged visible math and Chrome accessibility output.
- `lab-browser-results.json`: phone and desktop exact-value checks, comparison,
  invalid inputs (including disabling an invalid comparison), retained-count
  and radius limits, contribution inspection, shared-state restoration, CSV,
  equations, and document width.
- `lab-equation-accessibility.json`: normal phone/desktop and doubled phone
  text; all three equations scale correctly, remain keyboard-scrollable, and
  do not widen the document. The no-JavaScript markup retains its equations,
  named scroll regions, source links, and disabled calculation controls.

The full publication workflow separately checks generated documents, source
receipts, retained downloads, asset identities, and publication size. Live
deployment verification is performed after the workflow publishes the site.
