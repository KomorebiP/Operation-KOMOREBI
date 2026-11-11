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
  let scheduled = false;
  const updateProgress = () => {
    const total = document.documentElement.scrollHeight - innerHeight;
    progress.value = total > 0 ? Math.min(100, Math.max(0, 100*scrollY/total)) : 0;
    scheduled = false;
  };
  addEventListener('scroll', () => { if (!scheduled) { scheduled=true; requestAnimationFrame(updateProgress); } }, {passive:true});
  updateProgress();
  const dialog = document.getElementById('figure-dialog');
  const figureImage = document.getElementById('dialog-image');
  const figureCaption = document.getElementById('dialog-caption');
  const imageWrap = document.getElementById('dialog-image-wrap');
  const fitButton = document.getElementById('figure-fit');
  document.querySelectorAll('.figure-open').forEach(button => button.addEventListener('click', () => {
    const figure = button.closest('figure');
    const img = figure.querySelector('img');
    figureImage.src = img.src;
    figureImage.alt = img.alt;
    figureCaption.textContent = figure.querySelector('figcaption')?.textContent || img.alt;
    imageWrap.classList.add('dialog-fit');
    fitButton.textContent = 'View at full resolution';
    fitButton.setAttribute('aria-pressed', 'false');
    dialog.showModal();
  }));
  document.getElementById('figure-close').addEventListener('click', () => dialog.close());
  fitButton.addEventListener('click', () => {
    const fit = imageWrap.classList.toggle('dialog-fit');
    fitButton.textContent = fit ? 'View at full resolution' : 'Fit to window';
    fitButton.setAttribute('aria-pressed', String(!fit));
  });
  document.getElementById('smith-research').classList.add('research-js');
  const ready = () => {
    document.documentElement.dataset.mathReady = 'true';
    updateProgress();
    if (location.hash) document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView();
  };
  if (window.MathJax?.startup?.promise) MathJax.startup.promise.then(ready).catch(() => {
    document.documentElement.dataset.mathReady = 'error';
  }); else ready();
})();
