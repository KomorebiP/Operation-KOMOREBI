/* Optional end-to-end check against a built or deployed reading. Requires Playwright. */
const { chromium } = require('playwright');
const expectedEquations = require('../research/smith-chart/unified/READING_REVIEW.json').mathematics.output_expressions;

const url = process.argv[2];
if (!url) throw new Error('Provide the URL of read/smith-chart/research.html');

async function run() {
  const launch = { headless: true };
  if (process.env.SMITH_CHROME) launch.executablePath = process.env.SMITH_CHROME;
  const browser = await chromium.launch(launch);
  try {
    for (const [name, viewport] of [
      ['desktop', { width: 1440, height: 900 }],
      ['phone', { width: 390, height: 844 }],
      ['narrow', { width: 320, height: 800 }],
    ]) {
      const page = await browser.newPage({ viewport });
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      try {
        const response = await page.goto(url, { waitUntil: 'load', timeout: 120000 });
        if (!response || response.status() !== 200) throw new Error('Reading did not load');
        await page.waitForFunction(() => document.documentElement.dataset.mathReady, null, { timeout: 180000 });
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        const layout = await page.evaluate(() => ({
          width: document.documentElement.scrollWidth,
          viewport: innerWidth,
          figures: [...document.querySelectorAll('.research-figure img')].filter(img => img.complete && img.naturalWidth > 0).length,
          vectorFigures: [...document.querySelectorAll('.research-figure img')].filter(img => new URL(img.src).pathname.endsWith('.svg')).length,
          originalLinks: document.querySelectorAll('.figure-heading a').length,
          mobileFigures: [...document.querySelectorAll('.research-figure img')].filter(img => img.currentSrc.includes('.mobile.svg')).length,
          mathReady: document.documentElement.dataset.mathReady,
          mathErrors: document.querySelectorAll('mjx-merror').length,
          unrendered: [...document.querySelectorAll('.arithmatex')].filter(el => !el.querySelector('mjx-container')).length,
          equations: document.querySelectorAll('.arithmatex').length,
          headings: document.querySelectorAll('h1').length,
          articles: document.querySelectorAll('article').length,
          rawTex: (() => {
            const walker = document.createTreeWalker(document.querySelector('article'), NodeFilter.SHOW_TEXT);
            const raw = [];
            while (walker.nextNode()) {
              const node = walker.currentNode;
              if (!node.parentElement.closest('mjx-container,.arithmatex,code,pre') && /\\[([]|\\[A-Za-z]+\b/.test(node.textContent)) raw.push(node.textContent.slice(0,100));
            }
            return raw;
          })(),
          touchHeight: Math.min(...[...document.querySelectorAll('.research-actions a, .research-actions button, .figure-open')]
            .map(element => element.getBoundingClientRect().height).filter(height => height > 0)),
        }));
        if (layout.width > layout.viewport || layout.figures !== 51 || layout.vectorFigures !== 51 || layout.originalLinks !== 51 || layout.mobileFigures !== (name === 'desktop' ? 0 : 16) || layout.mathReady !== 'true' || layout.mathErrors || layout.unrendered || layout.rawTex.length || layout.equations !== expectedEquations || layout.headings !== 1 || layout.articles !== 1 || layout.touchHeight < 44) {
          throw new Error('Reading layout, images, mathematics, or touch controls failed: ' + JSON.stringify(layout));
        }
        const figure = page.locator('#figure-2 .figure-open');
        const description = await figure.getAttribute('aria-describedby');
        if (!description || await page.locator('#' + description).count() !== 1) throw new Error('Figure description is not associated');
        await figure.focus();
        await page.keyboard.press('Enter');
        await page.waitForFunction(() => !!document.querySelector('#dialog-caption mjx-container'), null, { timeout: 30000 });
        await page.locator('#figure-fit').click();
        await page.locator('#dialog-image-wrap').focus();
        const dialog = await page.evaluate(() => ({
          open: document.querySelector('#figure-dialog').open,
          pressed: document.querySelector('#figure-fit').getAttribute('aria-pressed'),
          scrollable: document.querySelector('#dialog-image-wrap').scrollWidth > document.querySelector('#dialog-image-wrap').clientWidth,
          focus: document.activeElement.id,
          mathErrors: document.querySelectorAll('#dialog-caption mjx-merror').length,
        }));
        if (!dialog.open || dialog.pressed !== 'true' || dialog.focus !== 'dialog-image-wrap' || dialog.mathErrors ||
            (name !== 'desktop' && !dialog.scrollable)) throw new Error('Expanded figure check failed: ' + JSON.stringify(dialog));
        await page.keyboard.press('Escape');
        const certificate = page.locator('figure').filter({ has: page.locator('img[data-figure-number="08"]') });
        const certificateSource = await certificate.locator('img').evaluate(img => img.currentSrc);
        await certificate.locator('.figure-open').click();
        if (await page.locator('#dialog-image').getAttribute('src') !== certificateSource) {
          throw new Error('Expanded figure did not preserve the displayed responsive diagram');
        }
        await page.keyboard.press('Escape');
        const constraints = page.locator('figure').filter({ has: page.locator('img[src$="/stable-energy.svg"]') });
        const constraintsSource = await constraints.locator('img').evaluate(img => img.currentSrc);
        if (constraintsSource.endsWith('.mobile.svg') !== (name !== 'desktop')) throw new Error('Physical-constraint figure did not choose the correct responsive source');
        await constraints.locator('.figure-open').click();
        if (await page.locator('#dialog-image').getAttribute('src') !== constraintsSource) throw new Error('Physical-constraint dialog changed the displayed source');
        await page.keyboard.press('Escape');
        const balanced = page.locator('figure').filter({ has: page.locator('img[src$="/balanced-resonance.svg"]') });
        const balancedSource = await balanced.locator('img').evaluate(img => img.currentSrc);
        if (balancedSource.endsWith('.mobile.svg') !== (name !== 'desktop')) throw new Error('Balanced figure chose the wrong responsive source');
        await balanced.locator('.figure-open').click();
        if (await page.locator('#dialog-image').getAttribute('src') !== balancedSource) throw new Error('Balanced dialog changed the displayed responsive source');
        await page.keyboard.press('Escape');
        const regular = page.locator('figure').filter({ has: page.locator('img[src$="/regular-balanced.svg"]') });
        const regularSource = await regular.locator('img').evaluate(img => img.currentSrc);
        if (regularSource.endsWith('.mobile.svg') !== (name !== 'desktop')) throw new Error('Regular-core figure chose the wrong responsive source');
        await regular.locator('.figure-open').click();
        if (await page.locator('#dialog-image').getAttribute('src') !== regularSource) throw new Error('Regular-core dialog changed the displayed responsive source');
        await page.keyboard.press('Escape');
        const transfer = page.locator('figure').filter({ has: page.locator('img[src$="/global-transfer.svg"]') });
        const transferSource = await transfer.locator('img').evaluate(img => img.currentSrc);
        if (transferSource.endsWith('.mobile.svg') !== (name !== 'desktop')) throw new Error('Transfer figure chose the wrong responsive source');
        await transfer.locator('.figure-open').click();
        if (await page.locator('#dialog-image').getAttribute('src') !== transferSource) throw new Error('Transfer dialog changed the displayed source');
        await page.keyboard.press('Escape');
        await page.locator('.research-contents-jump').focus();
        await page.keyboard.press('Enter');
        if (!await page.locator('#contents').evaluate(element => element.open)) throw new Error('Contents control did not open');
        for (const anchor of ['six-state-invariants', 'companion-guide', 'low-order-synthesis', 'formal-graph-core', 'global-transfer', 'typed-margins', 'component-tolerances']) {
          await page.locator('.research-contents-jump').focus();
          await page.keyboard.press('Enter');
          const link = page.locator('#contents a[href="#' + anchor + '"]').first();
          await link.focus();
          await page.keyboard.press('Enter');
          if (!await page.locator('#' + anchor).evaluate(el => {
            for (let parent = el.parentElement; parent; parent = parent.parentElement) {
              if (parent.tagName === 'DETAILS' && !parent.open) return false;
            }
            return true;
          })) throw new Error('Contents did not reveal retained source section: ' + anchor);
        }
        if (process.env.SMITH_QA_DIR) {
          await page.evaluate(() => scrollTo(0, 0));
          await page.screenshot({path: process.env.SMITH_QA_DIR + '/' + name + '.png'});
        }
        await page.evaluate(() => { document.documentElement.style.fontSize = '125%'; });
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        const enlarged = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, viewport: innerWidth }));
        if (enlarged.width > enlarged.viewport || errors.length) throw new Error('Enlarged layout or JavaScript failed: ' + JSON.stringify({ enlarged, errors }));
        console.log(JSON.stringify({ name, layout, dialog, enlarged }));
      } finally {
        await page.close();
      }
    }
    const noScript = await browser.newContext({ viewport: { width: 320, height: 800 }, javaScriptEnabled: false });
    try {
      const page = await noScript.newPage();
      await page.goto(url, { waitUntil: 'load', timeout: 120000 });
      const result = await page.evaluate(() => ({
        width: document.documentElement.scrollWidth, viewport: innerWidth,
        figures: [...document.querySelectorAll('.research-figure img')].filter(img => img.complete && img.naturalWidth > 0).length,
        contents: getComputedStyle(document.querySelector('.research-contents-jump')).visibility,
        figureControls: getComputedStyle(document.querySelector('.figure-actions')).display,
      }));
      if (result.width > result.viewport || result.figures !== 51 || result.contents !== 'visible' || result.figureControls !== 'none') {
        throw new Error('No-JavaScript reading failed: ' + JSON.stringify(result));
      }
      console.log(JSON.stringify({ name: 'no-javascript', ...result }));
    } finally {
      await noScript.close();
    }
    for (const [name, anchor] of [['SMITH_FIRST_ORDER_RL','one-inductor'], ['SMITH_SINGULAR_COMPLETION','singular-completion']]) {
    const supplement = await browser.newPage({ viewport: { width: 320, height: 800 } });
    try {
      const target = new URL('../../collection/demonstrations/' + name + '.html', url).href;
      const response = await supplement.goto(target, { waitUntil: 'load', timeout: 120000 });
      if (!response || response.status() !== 200) throw new Error('Circuit supplement did not load');
      await supplement.waitForURL('**/research.html#' + anchor, {timeout: 120000});
      await supplement.waitForFunction(() => window.MathJax?.startup?.promise, null, { timeout: 60000 });
      await supplement.evaluate(() => MathJax.startup.promise);
      const result = await supplement.evaluate(() => ({
        width: document.documentElement.scrollWidth, viewport: innerWidth,
        diagram: document.querySelector('article img')?.naturalWidth || 0,
        mathErrors: document.querySelectorAll('article mjx-merror').length,
        anchor: !!document.getElementById(location.hash.slice(1)),
      }));
      if (result.width > result.viewport || !result.diagram || !result.anchor || result.mathErrors) throw new Error('Circuit supplement failed: ' + JSON.stringify(result));
      console.log(JSON.stringify({ name, ...result }));
    } finally {
      await supplement.close();
    }
    }
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
