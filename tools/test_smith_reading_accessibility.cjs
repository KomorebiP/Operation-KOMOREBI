/* Focused reading-accessibility checks; this is not a WCAG certification. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const url = process.argv[2];
if (!url) throw new Error('Provide the canonical reading URL');
const output = process.env.SMITH_QA_DIR;
const expected = require('../research/smith-chart/unified/READING_REVIEW.json').mathematics.output_expressions;

(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.SMITH_CHROME});
  const records=[];
  try {
    for (const [name,width,js] of [['desktop',1440,true],['phone',390,true],['narrow-no-js',320,false]]) {
      const page=await browser.newPage({viewport:{width,height:900},javaScriptEnabled:js});
      const errors=[];page.on('pageerror',error=>errors.push(String(error)));
      await page.goto(url,{waitUntil:'load',timeout:120000});
      if(js)await page.waitForFunction(()=>document.documentElement.dataset.mathReady,null,{timeout:180000});
      await page.evaluate(()=>document.fonts.ready);
      if(js)await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      const data=await page.evaluate(()=>{
        const tables=[...document.querySelectorAll('article table')];
        const images=[...document.querySelectorAll('.research-figure img')];
        const headings=[...document.querySelectorAll('article :is(h2,h3,h4,h5,h6)')];
        let previous=1;const jumps=[];
        for(const h of headings){const level=Number(h.tagName[1]);if(level>previous+1)jumps.push(h.id);previous=level;}
        return {
          tables:tables.length,unnamedTables:tables.filter(t=>!t.caption?.textContent.trim()).length,
          unfocusableTables:tables.filter(t=>t.parentElement.tabIndex!==0||t.parentElement.getAttribute('role')!=='region'||!t.parentElement.getAttribute('aria-label')).length,
          missingHeaderScopes:document.querySelectorAll('article th:not([scope])').length,
          inaccessiblePre:[...document.querySelectorAll('article pre')].filter(p=>p.tabIndex!==0||!p.getAttribute('aria-label')).length,
          figures:images.length,descriptions:document.querySelectorAll('.figure-description').length,
          brokenFigureDetails:images.filter(img=>!img.alt||!document.getElementById(img.getAttribute('aria-details'))).length,
          headingJumps:jumps,guide:!!document.getElementById('reading-guide'),
          overflow:document.documentElement.scrollWidth>innerWidth,
          math:document.querySelectorAll('article .arithmatex').length,
          mathErrors:document.querySelectorAll('mjx-merror').length,
          assistiveMath:document.querySelectorAll('mjx-assistive-mml').length,
          renderedMath:document.querySelectorAll('article mjx-container').length,
          mathMenu:typeof window.MathJax?.startup?.document?.menu==='object',
          lang:document.documentElement.lang
        };
      });
      if(data.tables!==35||data.figures!==51||data.descriptions!==51||data.unnamedTables||data.unfocusableTables||data.missingHeaderScopes||data.inaccessiblePre||data.brokenFigureDetails||data.headingJumps.length||!data.guide||data.overflow||data.math!==expected||data.mathErrors||data.lang!=='en')throw new Error(name+': '+JSON.stringify(data));
      if(js&&(data.renderedMath<expected||data.assistiveMath<expected||!data.mathMenu))throw new Error('Mathematical rendering or assistive markup is unavailable: '+name);
      const disclosure=page.locator('#smith-figure-description-20');
      await disclosure.locator('summary').focus();await page.keyboard.press('Enter');
      if(!await disclosure.evaluate(el=>el.open))throw new Error('Figure description cannot be opened with keyboard');
      if(!await disclosure.locator('p').isVisible())throw new Error('Figure description is hidden after expansion');
      await page.keyboard.press('Enter');
      if(await disclosure.evaluate(el=>el.open))throw new Error('Figure description cannot be closed with keyboard');
      if(js){
        const button=page.locator('figure').nth(19).locator('.figure-open');
        if(await button.getAttribute('aria-label')!=='Open figure 20 at full size')throw new Error('Figure control has a generic accessible name');
        await button.focus();await page.keyboard.press('Enter');
        if(!await page.locator('#figure-dialog').evaluate(el=>el.open))throw new Error('Figure dialog did not open');
        await page.keyboard.press('Escape');
        if(!await button.evaluate(el=>el===document.activeElement))throw new Error('Figure dialog did not restore keyboard focus');
        const printState=await page.evaluate(()=>{
          const details=[...document.querySelectorAll('.figure-description')];
          details[0].open=true;
          dispatchEvent(new Event('beforeprint'));dispatchEvent(new Event('beforeprint'));
          const expanded=details.filter(el=>el.open).length;
          dispatchEvent(new Event('afterprint'));dispatchEvent(new Event('afterprint'));
          const restored=details.filter(el=>el.open).length;
          details[0].open=false;
          return {expanded,restored};
        });
        if(printState.expanded!==51||printState.restored!==1)throw new Error('Printing changed the saved disclosure state');
        await page.addStyleTag({content:'#smith-research .manuscript{font-size:200%}'});
        await page.evaluate(()=>document.fonts.ready);
        await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
        if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Enlarged text overflows: '+name);
        await page.addStyleTag({content:'#smith-research .manuscript{font-size:inherit}'});
      }
      await page.emulateMedia({media:'print'});
      const print=await page.evaluate(()=>({
        descriptions:[...document.querySelectorAll('.figure-description p')].filter(el=>el.getBoundingClientRect().height>0&&getComputedStyle(el).visibility!=='hidden').length,
        figures:[...document.querySelectorAll('.research-figure img')].filter(el=>el.getBoundingClientRect().height>0).length
      }));
      if(print.descriptions!==51||print.figures!==51)throw new Error('Print hides reading content: '+JSON.stringify(print));
      await page.emulateMedia({media:'screen'});
      if(output){fs.mkdirSync(output,{recursive:true});await page.locator('#reading-guide').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(output,'support-'+name+'.png')});fs.writeFileSync(path.join(output,'support-'+name+'.json'),JSON.stringify({name,...data,print,errors},null,2));}
      records.push({name,...data,print,errors});
      if(errors.length)throw new Error('Browser errors: '+JSON.stringify(errors));
      await page.close();
    }
    console.log(JSON.stringify({status:'passed',scope:'Semantic structure, keyboard controls, reflow and print; no screen-reader user testing or WCAG certification',records},null,2));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
