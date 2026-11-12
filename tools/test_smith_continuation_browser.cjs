/* Optional browser QA. node tools/test_smith_continuation_browser.cjs <site-base-url> */
const { chromium } = require('playwright');
const base = process.argv[2];
if (!base) throw new Error('Provide the site base URL');

async function settled(page) {
  await page.waitForFunction(() => window.MathJax && MathJax.startup && MathJax.startup.promise, null, {timeout: 60000});
  await page.evaluate(() => MathJax.startup.promise);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

async function main() {
  const browser = await chromium.launch({headless: true, executablePath: process.env.SMITH_CHROME});
  try {
    for (const width of [1440, 390, 320]) {
      const page = await browser.newPage({viewport: {width, height: 900}});
      const errors = [];
      page.on('pageerror', e => errors.push(String(e)));
      for (const slug of ['continuation', 'exact-six', 'composition', 'families', 'obstruction', 'quantitative-transfer', 'effective-margin']) {
        const response = await page.goto(new URL('read/smith-chart/' + slug + '.html', base).href, {waitUntil: 'load', timeout: 90000});
        if (!response || response.status() !== 200) throw new Error('Page failed: ' + slug);
        await settled(page);
        const state = await page.evaluate(() => {
          const walker = document.createTreeWalker(document.querySelector('article'), NodeFilter.SHOW_TEXT);
          const raw = [];
          while (walker.nextNode()) {
            const node = walker.currentNode;
            if (!node.parentElement.closest('mjx-container, .arithmatex, code, pre') && /\\[([]|\\(?:frac|boxed|mathbb)\b/.test(node.textContent)) raw.push(node.textContent.slice(0,100));
          }
          return {width: document.documentElement.scrollWidth, viewport: innerWidth,
            equations: document.querySelectorAll('.arithmatex').length,
            unrendered: [...document.querySelectorAll('.arithmatex')].filter(el => !el.querySelector('mjx-container')).length,
            mathErrors: document.querySelectorAll('mjx-merror, [data-mjx-error]').length,
            failedImages: [...document.querySelectorAll('article img')].filter(el => !el.complete || !el.naturalWidth).length,
            raw};
        });
        if (state.width > width || state.unrendered || state.mathErrors || state.failedImages || state.raw.length || errors.length) {
          throw new Error(JSON.stringify({slug, width, state, errors}));
        }
        await page.evaluate(() => document.documentElement.style.fontSize = '125%');
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Enlarged text overflow: ' + slug);
        console.log(JSON.stringify({slug, width, ...state}));
      }
      await page.goto(new URL('read/smith-chart/continuation.html', base).href, {waitUntil: 'load'});
      await settled(page);
      const link = page.locator('article a[href="exact-six.html"]').first();
      await link.focus();
      await page.keyboard.press('Enter');
      await page.waitForURL('**/exact-six.html');
      await page.close();
    }
    const context = await browser.newContext({viewport: {width: 320, height: 800}, javaScriptEnabled: false});
    for (const slug of ['continuation', 'exact-six', 'effective-margin']) {
      const page = await context.newPage();
      await page.goto(new URL('read/smith-chart/' + slug + '.html', base).href, {waitUntil: 'load'});
      const result = await page.evaluate(() => ({width: document.documentElement.scrollWidth, viewport: innerWidth, text: document.querySelector('article').textContent.length}));
      if (result.width > result.viewport || result.text < 1000) throw new Error('Reading without scripts failed: ' + JSON.stringify({slug, result}));
      await page.close();
    }
    await context.close();
    console.log('PASS: all seven chapters; desktop, phone, narrow, enlarged text, keyboard and no-JavaScript reading');
  } finally { await browser.close(); }
}
main().catch(error => {console.error(error); process.exitCode = 1;});
