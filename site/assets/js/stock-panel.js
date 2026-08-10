/* The shared per-ticker panel. ONE component, used identically by all four tabs.
 *
 * Takes explicit arguments -- setTicker({ticker, bench, zwin, horizon}) -- rather than reading
 * sibling <select> values the way the reference dashboard's renderStock did. That made the render
 * a non-pure function of its inputs and impossible to drive from a test.
 *
 * Moving averages are derived HERE. Shards ship raw series (price, relative, volume) and the
 * panel computes the 20/50-dma from them, which halved the payload. The arithmetic is the same
 * strict-window SMA the build uses, so two tabs sharing a ticker derive identical values.
 */

import { chart, destroyChart, emptyCard, fmt } from "./charts.js";
import { loadManifest, loadTicker } from "./data-client.js";

/** Strict SMA: one gap in the window kills the value. Mirrors scripts/indicators.py:sma. */
export function sma(col, n) {
  const out = new Array(col.length).fill(null);
  for (let i = n - 1; i < col.length; i++) {
    let s = 0, ok = true;
    for (let j = i - n + 1; j <= i; j++) {
      const v = col[j];
      if (v == null) { ok = false; break; }
      s += v;
    }
    if (ok) out[i] = s / n;
  }
  return out;
}

const PANEL = [
  { id: "chStockAbs",  h: 230, trimNulls: true },
  { id: "chStockRel",  h: 230, trimNulls: true },
  { id: "chStockMacd", h: 190, zero: true, trimNulls: true },
  { id: "chStockRsi",  h: 190, min: 0, max: 100, band: [30, 70], trimNulls: true },
  { id: "chStockObv",  h: 190, trimNulls: true },
  { id: "chStockVol",  h: 190, min: 0, trimNulls: true },
  { id: "chStockZAbs", h: 190, zero: true, band: [-1, 1], trimNulls: true },
  { id: "chStockZRel", h: 190, zero: true, band: [-1, 1], trimNulls: true },
];

export function createStockPanel(root, opts) {
  const { universe, manifest, dates } = opts;
  const state = {
    ticker: opts.ticker || manifest.defaultTicker,
    bench: opts.bench || manifest.defaultBenchmark,
    zwin: String(opts.zwin || (manifest.zWindows && manifest.zWindows[0]) || 21),
    i0: 0, i1: dates.length - 1,
  };
  let rec = null;

  const $ = id => root.querySelector("#" + id);
  const selT = $("stockSel"), selB = $("benchSel"), selZ = $("zWinSel");
  const tickers = Object.keys(manifest.tickers).sort();

  selT.innerHTML = tickers.map(t =>
    `<option value="${t}"${manifest.tickers[t].bell ? "" : ""}>${t}${manifest.tickers[t].bell ? " ★" : ""}${manifest.tickers[t].pinned ? " ⚑" : ""}</option>`).join("");
  selT.value = tickers.includes(state.ticker) ? state.ticker : tickers[0];
  state.ticker = selT.value;

  selB.innerHTML = (manifest.benchmarks || []).map(b => `<option value="${b}">${b}</option>`).join("");
  selB.value = (manifest.benchmarks || []).includes(state.bench) ? state.bench : (manifest.benchmarks || [])[0];
  state.bench = selB.value;

  const zw = (manifest.zWindows || [21]).filter(w =>
    !manifest.shardZWindows || manifest.shardZWindows.includes(w));
  selZ.innerHTML = zw.map(w => `<option value="${w}">${w}d</option>`).join("");
  selZ.value = zw.includes(Number(state.zwin)) ? state.zwin : String(zw[0]);
  state.zwin = selZ.value;

  selT.onchange = () => setTicker(selT.value);
  selB.onchange = () => { state.bench = selB.value; draw(); };
  selZ.onchange = () => { state.zwin = selZ.value; draw(); };

  async function setTicker(t) {
    state.ticker = t;
    if (selT.value !== t) selT.value = t;
    root.querySelectorAll("[data-chart]").forEach(el => {
      destroyChart(el);
      el.innerHTML = `<div class="skeleton"></div>`;
    });
    try {
      rec = await loadTicker(universe, t);
    } catch (e) {
      root.querySelectorAll("[data-chart]").forEach(el =>
        emptyCard(el, t, `Could not load data for ${t}: ${e.message}`));
      return;
    }
    draw();
  }

  function setWindow(i0, i1) {
    state.i0 = i0;
    state.i1 = i1;
    if (rec) draw();
  }

  function draw() {
    if (!rec) return;
    const t = rec.t, off = rec.i0 || 0;
    // shards are stored from the ticker's own first print; pad back onto the universe grid
    const pad = a => (a == null ? null : new Array(off).fill(null).concat(a));
    const px = pad(rec.px);
    const bench = state.bench;
    const rel = rec.rel && rec.rel[bench] ? pad(rec.rel[bench]) : null;
    const vol = pad(rec.vol);
    const obv = pad(rec.obv);
    const macd = { line: pad(rec.macd.line), signal: pad(rec.macd.signal), hist: pad(rec.macd.hist) };
    const rsi = pad(rec.rsi);
    const zA = rec.zAbs && rec.zAbs[state.zwin] ? pad(rec.zAbs[state.zwin]) : null;
    const zR = rec.zRel && rec.zRel[state.zwin] ? pad(rec.zRel[state.zwin]) : null;

    const d20 = sma(px, 20), d50 = sma(px, 50);
    const rd20 = rel ? sma(rel, 20) : null, rd50 = rel ? sma(rel, 50) : null;
    const vAvg = vol ? sma(vol, 20) : null;

    const common = { dates, i0: state.i0, i1: state.i1 };
    const put = (id, cfg) => {
      const el = $(id);
      if (!el) return;
      try { chart(el, Object.assign({}, common, cfg)); }
      catch (e) { emptyCard(el, cfg.title || id, e.message); }
    };

    put("chStockAbs", {
      title: `${t} — absolute price`, h: 230, trimNulls: true, ydec: 0,
      series: [
        { name: t, values: px, color: "var(--s1)", w: 2, dec: 2 },
        { name: "20-dma", values: d20, color: "var(--s2)", w: 1.3, dash: "5 4", dec: 2 },
        { name: "50-dma", values: d50, color: "var(--muted)", w: 1.3, dash: "2 3", dec: 2 },
      ],
    });

    if (rel) {
      put("chStockRel", {
        title: `${t} — relative to ${bench} (base 100)`, h: 230, trimNulls: true,
        series: [
          { name: "Relative", values: rel, color: "var(--s3)", w: 2, dec: 1 },
          { name: "20-dma", values: rd20, color: "var(--s2)", w: 1.3, dash: "5 4", dec: 1 },
          { name: "50-dma", values: rd50, color: "var(--muted)", w: 1.3, dash: "2 3", dec: 1 },
        ],
      });
    } else {
      emptyCard($("chStockRel"), `${t} — relative`, `No series for benchmark ${bench}.`);
    }

    put("chStockMacd", {
      title: `${t} — MACD (12,26,9)`, h: 190, zero: true, trimNulls: true, ydec: 1,
      series: [
        { name: "MACD", values: macd.line, color: "var(--s1)", w: 1.4, dec: 2 },
        { name: "Signal", values: macd.signal, color: "var(--s2)", w: 1.1, dash: "5 4", dec: 2 },
        { name: "Histogram", values: macd.hist, color: "var(--muted)", bars: true, dec: 2 },
      ],
      bars: { values: macd.hist, color: "var(--muted)" },
    });

    put("chStockRsi", {
      title: `${t} — RSI (14)`, h: 190, min: 0, max: 100, band: [30, 70], trimNulls: true,
      series: [{ name: "RSI", values: rsi, color: "var(--s1)", w: 1.5, dec: 1 }],
    });

    if (obv) {
      put("chStockObv", {
        title: `${t} — on-balance volume (millions of shares)`, h: 190, trimNulls: true,
        series: [{ name: "OBV", values: obv, color: "var(--s4)", w: 1.8, dec: 1 }],
      });
    } else {
      emptyCard($("chStockObv"), `${t} — OBV`, "Volume not available for this ticker.");
    }

    if (vol) {
      put("chStockVol", {
        title: `${t} — volume (shares) with 20-dma`, h: 190, min: 0, trimNulls: true,
        series: [
          { name: "Volume", values: vol, color: "var(--muted)", bars: true, dec: 0 },
          { name: "20-dma", values: vAvg, color: "var(--s4)", w: 1.6, dec: 0 },
        ],
        bars: { values: vol, color: "var(--muted)" },
      });
    } else {
      emptyCard($("chStockVol"), `${t} — volume`, "Volume not available for this ticker.");
    }

    if (zA) {
      put("chStockZAbs", {
        title: `${t} — ${state.zwin}d rolling z-score, daily return`, h: 190,
        zero: true, band: [-1, 1], trimNulls: true, ydec: 1,
        series: [{ name: "z", values: zA, color: "var(--s1)", w: 1.5, dec: 2 }],
      });
    }
    if (zR) {
      put("chStockZRel", {
        title: `${t} — ${state.zwin}d rolling z-score vs ${manifest.defaultBenchmark}`, h: 190,
        zero: true, band: [-1, 1], trimNulls: true, ydec: 1,
        series: [{ name: "z (rel)", values: zR, color: "var(--s3)", w: 1.5, dec: 2 }],
      });
    }

    renderSignals(root.querySelector("#stockSignals"), rec, t);
  }

  function renderSignals(host, rec, t) {
    if (!host) return;
    const sig = rec.signals || [];
    if (!sig.length) { host.innerHTML = ""; return; }
    host.innerHTML =
      `<div class="card"><h3>Technical signals — ${t}</h3>
        <p class="note">Each row is a stated test against the latest session. These are measurements,
        not recommendations.</p>
        <div class="sigGrid">${sig.map(s => `
          <div class="sigRow">
            <span class="sigTest">${s.test}</span>
            <span class="sigVal">${s.value}</span>
            <span class="chip state-${s.state.replace(/[^a-z]/gi, "")}">${s.state}</span>
          </div>`).join("")}</div></div>`;
  }

  return {
    setTicker, setWindow,
    setBenchmark: b => { state.bench = b; selB.value = b; draw(); },
    setZWindow: z => { state.zwin = String(z); selZ.value = String(z); draw(); },
    getState: () => ({ ...state }),
    destroy: () => root.querySelectorAll("[data-chart]").forEach(destroyChart),
  };
}

export const PANEL_IDS = PANEL.map(p => p.id);
