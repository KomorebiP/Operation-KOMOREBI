/* Legacy entry point: continuation QA now exercises the one canonical reading. */
const base = process.argv[2];
if (!base) throw new Error('Provide the site base URL');
process.argv[2] = new URL('read/smith-chart/research.html', base).href;
require('./test_smith_research_browser.cjs');
