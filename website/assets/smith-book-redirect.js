/* Author: Komorebi P. Preserve legacy section bookmarks in the unified reading. */
(() => {
  const script = document.currentScript;
  const destination = new URL(script.dataset.bookTarget, location.href);
  const prefix = script.dataset.bookPrefix;
  let fragment = '';
  try { fragment = decodeURIComponent(location.hash.slice(1)); } catch { fragment = ''; }
  if (fragment && prefix !== 'current-results') destination.hash = prefix + '--' + fragment;
  if (prefix === 'current-results') {
    const sections = {'fresh-executable-evidence':'source-ledger','work-still-open':'source-ledger',
      'what-the-newest-family-claim-depends-on':'effective-margin','two-different-targets':'exact-six'};
    destination.hash = sections[fragment] || 'current-results';
  }
  location.replace(destination.href);
})();
