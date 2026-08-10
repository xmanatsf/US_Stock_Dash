/* Fetching + caching for the sharded payload.
 *
 * Cache-busting contract: the manifest is the ONLY no-store fetch. Everything else carries
 * ?v=<version>, so summaries and shards are immutably cacheable and a refreshed deploy is
 * visible without any special client action. The in-memory cache key includes the version too,
 * so a rebuild inside one session cannot serve a stale shard.
 */

const _manifests = new Map();
const _summaries = new Map();
const _shards = new Map();          // `${uni}:${ticker}:${version}` -> record
const SHARD_LRU = 40;               // browsing 500 names must not grow without bound

function base() {
  // tabs live in site/tabs/, the shell in site/ -- resolve data/ relative to the page
  return location.pathname.includes("/tabs/") ? "../data" : "./data";
}

async function getJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} for ${url}`);
  return r.json();
}

export async function loadIndex() {
  return getJSON(`${base()}/index.json`, { cache: "no-store" });
}

export async function loadManifest(uni) {
  if (_manifests.has(uni)) return _manifests.get(uni);
  const m = await getJSON(`${base()}/${uni}/manifest.json`, { cache: "no-store" });
  _manifests.set(uni, m);
  return m;
}

export async function loadSummary(uni) {
  const m = await loadManifest(uni);
  const key = `${uni}:${m.version}`;
  if (_summaries.has(key)) return _summaries.get(key);
  const s = await getJSON(`${base()}/${uni}/${m.summaryFile}?v=${m.version}`);
  _summaries.set(key, s);
  return s;
}

export async function loadTicker(uni, ticker) {
  const m = await loadManifest(uni);
  const meta = m.tickers && m.tickers[ticker];
  if (!meta) throw new Error(`${ticker} is not in the ${uni} manifest`);
  const key = `${uni}:${ticker}:${m.version}`;
  if (_shards.has(key)) {
    const v = _shards.get(key);
    _shards.delete(key); _shards.set(key, v);      // LRU touch
    return v;
  }
  const rec = await getJSON(`${base()}/${uni}/${meta.f}?v=${m.version}`);
  _shards.set(key, rec);
  while (_shards.size > SHARD_LRU) _shards.delete(_shards.keys().next().value);
  return rec;
}

export async function loadBenchmarks() {
  return getJSON(`${base()}/benchmarks.json`, { cache: "no-store" });
}

/** Warm the bellwethers on idle so the common path feels instant. Failures are ignored. */
export function prefetch(uni, tickers, concurrency = 3) {
  const run = () => {
    const q = [...tickers];
    const worker = async () => {
      while (q.length) {
        try { await loadTicker(uni, q.shift()); } catch { /* prefetch is best-effort */ }
      }
    };
    for (let i = 0; i < concurrency; i++) worker();
  };
  if ("requestIdleCallback" in window) requestIdleCallback(run, { timeout: 3000 });
  else setTimeout(run, 1200);
}
