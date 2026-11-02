/* Select an exact retained file. Compiler results belong to the native runner. */
(() => {
  'use strict';
  const root = document.querySelector('[data-lean-execution]');
  if (!root) return;
  const search = root.querySelector('#lean-run-search');
  const select = root.querySelector('#lean-run-file');
  const status = root.querySelector('[data-lean-run-count]');
  const selection = root.querySelector('[data-lean-run-selection]');
  const field = name => root.querySelector(`[data-run-${name}]`);
  const command = root.querySelector('#lean-run-command');
  let files = [];
  let activeId = null;
  const shellQuote = value => "'" + value.replaceAll("'", "'\\''") + "'";
  function show(id, updateAddress = true) {
    const source = files.find(item => item.id === id);
    if (!source) {
      activeId = null;
      select.value = '';
      selection.hidden = true;
      status.textContent = 'That source is not in this catalogue. Choose a file from the list.';
      return;
    }
    select.value = id;
    activeId = id;
    field('work').textContent = source.label || source.work;
    field('name').textContent = source.path.split('/').pop();
    field('path').textContent = source.path;
    field('mode').textContent = source.mode === 'retained-project'
      ? `Retained Lake project · ${source.input_files} source/configuration inputs`
      : `Reconstructed workspace · ${source.input_files} local source inputs`;
    field('pin').textContent = source.toolchain ? `Lean pin: ${source.toolchain}` : 'Environment needs setup.';
    field('issues').hidden = source.issues.length === 0;
    field('issues').textContent = source.issues.length
      ? 'Preparation needs attention: ' + source.issues.join(' ') : '';
    field('inspect').href = '../' + source.url;
    command.value = 'python run_lean.py --source ' + shellQuote(source.path)
      + ' --output ../lean-run-' + source.id;
    selection.hidden = false;
    if (updateAddress) {
      const url = new URL(location.href);
      url.searchParams.set('file', id);
      history.replaceState(null, '', url);
    }
  }
  function filter() {
    const query = search.value.toLocaleLowerCase().trim();
    const selected = activeId;
    const found = files.filter(s => (s.work + ' ' + (s.label || '') + ' ' + s.path).toLocaleLowerCase().includes(query));
    const options = found.map(source => {
      const option = document.createElement('option');
      option.value = source.id;
      option.textContent = (source.label || source.work) + ' · ' + source.path;
      return option;
    });
    if (selected && !found.some(s => s.id === selected)) {
      const current = files.find(s => s.id === selected);
      const option = document.createElement('option');
      option.value = selected;
      option.textContent = 'Current selection: ' + (current.label || current.work) + ' · ' + current.path;
      options.unshift(option);
    } else if (!selected) {
      const option = document.createElement('option');
      option.value = '';
      option.textContent = 'Choose a source file';
      options.unshift(option);
    }
    select.replaceChildren(...options);
    select.value = selected || '';
    status.textContent = `${found.length} of ${files.length} source files`;
    // Filtering does not silently switch the displayed run command to a different file.
  }
  fetch(root.dataset.catalog).then(response => {
    if (!response.ok) throw new Error('Catalogue unavailable');
    return response.json();
  }).then(data => {
    files = data.files;
    filter();
    const requested = new URL(location.href).searchParams.get('file');
    show(requested || files[0]?.id, false);
    select.addEventListener('change', () => show(select.value));
    search.addEventListener('input', filter);
    window.addEventListener('popstate', () => show(new URL(location.href).searchParams.get('file'), false));
  }).catch(() => {
    status.textContent = 'The catalogue could not load. Download the bundle and run python run_lean.py --list.';
  });
})();
