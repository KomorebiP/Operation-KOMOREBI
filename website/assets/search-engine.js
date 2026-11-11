/* Full-text matching uses compact static postings; previews load per visible result. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.KomorebiSearch = api;
})(typeof window === 'undefined' ? this : window, function () {
  'use strict';

  function decodeIds(encoded, total) {
    if (typeof encoded !== 'string' || !encoded) throw new Error('Invalid search posting');
    const result = [];
    let previous = 0;
    for (const token of encoded.split('.')) {
      if (!/^[0-9a-z]+$/.test(token)) throw new Error('Invalid search posting');
      const id = previous + parseInt(token, 36);
      if (!Number.isSafeInteger(id) || id >= total || result.length && id <= previous) throw new Error('Invalid search posting order');
      result.push(id);
      previous = id;
    }
    return result;
  }

  async function mapLimit(values, limit, action) {
    const output = new Array(values.length);
    let next = 0;
    await Promise.all(Array.from({length: Math.min(limit, values.length)}, async () => {
      while (next < values.length) {
        const at = next++;
        output[at] = await action(values[at]);
      }
    }));
    return output;
  }

  class Client {
    constructor(indexUrl, options = {}) {
      this.indexUrl = new URL(indexUrl, options.baseUrl || (typeof location === 'undefined' ? undefined : location.href));
      this.fetch = options.fetch || globalThis.KomorebiReaderData?.fetch || fetch.bind(globalThis);
      this.assets = new Map();
      this.previews = new Map();
      this.total = null;
    }
    json(path, cache = this.assets) {
      const url = new URL(path, this.indexUrl);
      if (url.origin !== this.indexUrl.origin) return Promise.reject(new Error('Invalid search asset'));
      if (cache.has(url.href)) {
        const cached = cache.get(url.href);
        cache.delete(url.href); cache.set(url.href, cached);
        return cached.promise;
      }
      const entry = {ready: false};
      entry.promise = Promise.resolve().then(() => this.fetch(url.href)).then(response => {
        if (!response.ok) throw new Error('Search data could not be loaded');
        return response.json();
      }).then(value => {
        entry.ready = true;
        // Bound retained preview memory while coalescing requests still in flight.
        if (cache === this.previews) for (const [key, item] of cache) {
          if (cache.size <= 160) break;
          if (item.ready) cache.delete(key);
        }
        return value;
      }).catch(error => {
        if (cache.get(url.href) === entry) cache.delete(url.href);
        throw error;
      });
      cache.set(url.href, entry);
      return entry.promise;
    }
    async manifest() {
      const value = await this.json(this.indexUrl.href);
      if (value.schema !== 2 || !Number.isSafeInteger(value.entries) || value.entries < 0 ||
          !Number.isSafeInteger(value.terms_per_part) || value.terms_per_part < 1) throw new Error('Unsupported search catalogue');
      this.total = value.entries;
      return value;
    }
    async load() {
      const manifest = await this.manifest();
      const data = await this.json(manifest.metadata);
      if (data.rows.length !== manifest.entries) throw new Error('Incomplete search catalogue');
      return data.rows.map((row, id) => ({id, title: row[0], url: row[1], group: data.groups[row[2]],
        kind: data.kinds[row[3]], work_ids: row[4].map(work => data.works[work]), visual_guide: Boolean(row[5])}));
    }
    async match(words) {
      if (!words.length) return null;
      const manifest = await this.manifest();
      const terms = await this.json(manifest.lexicon);
      const wanted = words.map(word => terms.map((term, index) => term.includes(word) ? index : -1).filter(index => index >= 0));
      if (wanted.some(indices => !indices.length)) return new Set();
      const parts = [...new Set(wanted.flat().map(index => Math.floor(index / manifest.terms_per_part)))];
      const loaded = await mapLimit(parts, 8, part => this.json(manifest.postings + part + '.json'));
      const byPart = new Map(parts.map((part, i) => [part, loaded[i]]));
      const matches = wanted.map(indices => {
        const ids = new Set();
        for (const index of indices) {
          const encoded = byPart.get(Math.floor(index / manifest.terms_per_part))[terms[index]];
          for (const id of decodeIds(encoded, manifest.entries)) ids.add(id);
        }
        return ids;
      }).sort((a, b) => a.size - b.size);
      return new Set([...matches[0]].filter(id => matches.every(set => set.has(id))));
    }
    async details(rows) {
      const manifest = await this.manifest();
      return mapLimit(rows, 8, async row => {
        if (!Number.isSafeInteger(row.id) || row.id < 0 || row.id >= manifest.entries) throw new Error('Invalid search result');
        const detail = await this.json(manifest.details + row.id + '.json', this.previews);
        if (Object.keys(detail).some(key => !['text', 'preview', 'preview_parts', 'math_preview'].includes(key)) ||
            typeof (detail.preview || detail.text) !== 'string') throw new Error('Invalid search preview');
        return {...row, ...detail};
      });
    }
  }
  return {Client, decodeIds};
});
