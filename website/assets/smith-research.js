/* Author: Komorebi P. Local reading controls. */
(() => {
  const contents = document.getElementById('contents');
  const media = matchMedia('(max-width: 820px)');
  const setContents = () => { contents.open = !media.matches; };
  setContents();
  media.addEventListener('change', setContents);
  document.getElementById('print-reading').addEventListener('click', () => window.print());
  const links = [...document.querySelectorAll('.toc-links a, .toc-current')];
  const headings = links.map(a => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach(a => a.removeAttribute('aria-current'));
        const current = links.find(a => a.hash.slice(1) === entry.target.id);
        if (current) current.setAttribute('aria-current', 'location');
      }
    }, {rootMargin:'-5% 0px -80% 0px'});
    headings.forEach(h => observer.observe(h));
  }
  links.forEach(a => a.addEventListener('click', () => {
    if (media.matches) contents.open = false;
  }));
  const progress = document.getElementById('reading-progress');
  const research = document.getElementById('smith-research');
  const contentsJump = document.querySelector('.research-contents-jump');
  contentsJump.addEventListener('click', () => {
    contents.open = true;
    if (media.matches) requestAnimationFrame(() => contents.querySelector('summary').focus({preventScroll:true}));
  });
  let scheduled = false;
  const updateProgress = () => {
    const total = document.documentElement.scrollHeight - innerHeight;
    progress.value = total > 0 ? Math.min(100, Math.max(0, 100*scrollY/total)) : 0;
    research.classList.toggle('has-scrolled', scrollY > innerHeight);
    scheduled = false;
  };
  addEventListener('scroll', () => { if (!scheduled) { scheduled=true; requestAnimationFrame(updateProgress); } }, {passive:true});
  updateProgress();
  const dialog = document.getElementById('figure-dialog');
  const figureImage = document.getElementById('dialog-image');
  const figureCaption = document.getElementById('dialog-caption');
  const imageWrap = document.getElementById('dialog-image-wrap');
  const fitButton = document.getElementById('figure-fit');
  let captionTicket = 0;
  document.querySelectorAll('.figure-open').forEach((button, index) => {
    const figure = button.closest('figure');
    const caption = figure.querySelector('figcaption');
    // Preserve untypeset caption markup so the dialog can render its mathematics too.
    const captionTemplate = caption && !caption.querySelector('mjx-container') ? caption.cloneNode(true) : null;
    if (caption) {
      caption.id ||= 'research-figure-caption-' + (index + 1);
      button.setAttribute('aria-label', 'Open figure at full size');
      button.setAttribute('aria-describedby', caption.id);
    }
    button.addEventListener('click', () => {
      const img = figure.querySelector('img');
      figureImage.src = img.src;
      figureImage.alt = img.alt;
      const ticket = ++captionTicket;
      if (window.MathJax?.typesetClear) MathJax.typesetClear([figureCaption]);
      if (captionTemplate) {
        figureCaption.replaceChildren(...[...captionTemplate.childNodes].map(node => node.cloneNode(true)));
      } else {
        figureCaption.textContent = caption?.textContent || img.alt;
      }
      imageWrap.classList.add('dialog-fit');
      fitButton.textContent = 'View at full resolution';
      fitButton.setAttribute('aria-pressed', 'false');
      dialog.showModal();
      if (captionTemplate && window.MathJax?.typesetPromise) {
        Promise.resolve(MathJax.startup?.promise).then(() => {
          if (ticket === captionTicket && dialog.open) return MathJax.typesetPromise([figureCaption]);
        }).catch(() => {
          if (ticket === captionTicket) figureCaption.textContent = caption?.textContent || img.alt;
        });
      }
    });
  });
  dialog.addEventListener('close', () => { captionTicket++; });
  document.getElementById('figure-close').addEventListener('click', () => dialog.close());
  fitButton.addEventListener('click', () => {
    const fit = imageWrap.classList.toggle('dialog-fit');
    fitButton.textContent = fit ? 'View at full resolution' : 'Fit to window';
    fitButton.setAttribute('aria-pressed', String(!fit));
  });
  research.classList.add('research-js');
  const ready = () => {
    document.documentElement.dataset.mathReady = 'true';
    updateProgress();
    if (location.hash) document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView();
  };
  if (window.MathJax?.startup?.promise) MathJax.startup.promise.then(ready).catch(() => {
    document.documentElement.dataset.mathReady = 'error';
  }); else ready();
})();
