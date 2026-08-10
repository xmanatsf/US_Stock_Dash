/* Tab bootstrap: nav, the shared horizon control, loading/error states, and the
 * validation-banner branch that makes a failed universe honest instead of blank.
 *
 * Horizon is CLIENT-SIDE SLICING ONLY. Benchmarks ship as raw levels and the relative series is
 * rebased to 100 at the selected window's first index, because rebasing server-side would
 * hardcode one horizon and make the 1-month view meaningless.
 */

import { chart, clearCharts, destroyChart, fmt, regimeRibbon, scatterChart, sign, sparkline } from "./charts.js";
import { loadIndex, loadManifest, loadSummary, prefetch } from "./data-client.js";
import { createStockPanel } from "./stock-panel.js";
import * as Interp from "./interpret.js";
import { REGIME_COLORS } from "./regimes.js";

export const HORIZONS = ["1m", "3m", "6m", "1y", "2y", "3y", "5y"];
const BARS = { "1m": 21, "3m": 63, "6m": 126, "1y": 252, "2y": 504, "3y": 756, "5y": 1260 };

export function horizonWindow(n, h) {
  const b = BARS[h];
  return { i0: b ? Math.max(0, n - b) : 0, i1: n - 1 };
}

function readState() {
  const q = new URLSearchParams(location.search);
  let h = q.get("h") || localStorage.getItem("stkdash.horizon") || "1y";
  if (!HORIZONS.includes(h)) h = "1y";
  return { horizon: h, ticker: q.get("t") || null, bench: q.get("b") || null };
}

function writeState(s) {
  const q = new URLSearchParams(location.search);
  if (s.horizon) { q.set("h", s.horizon); localStorage.setItem("stkdash.horizon", s.horizon); }
  if (s.ticker) q.set("t", s.ticker);
  history.replaceState(null, "", `${location.pathname}?${q}`);
}

export async function initNav(active) {
  const host = document.querySelector("#tabNav");
  if (!host) return;
  let idx;
  try { idx = await loadIndex(); } catch { host.innerHTML = ""; return; }
  const h = readState().horizon;
  const us = Object.entries(idx.universes).sort((a, b) => a[1].order - b[1].order);
  host.innerHTML = us.map(([k, u]) =>
    `<a class="tabBtn${k === active ? " active" : ""}" href="${u.tab}.html?h=${h}"
        data-universe="${k}">${u.label}${u.status !== "ok" ? " ⚠" : ""}</a>`).join("");
}

function themeToggle() {
  const btn = document.querySelector("#themeBtn");
  if (!btn) return;
  btn.onclick = () => {
    const root = document.documentElement;
    const cur = root.getAttribute("data-theme") ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    root.setAttribute("data-theme", cur === "dark" ? "light" : "dark");
  };
}

function horizonControl(onChange, current) {
  const host = document.querySelector("#horizonCtl");
  if (!host) return;
  host.innerHTML = HORIZONS.map(h =>
    `<button class="hBtn${h === current ? " active" : ""}" data-h="${h}">${h}</button>`).join("");
  host.onclick = ev => {
    const b = ev.target.closest(".hBtn");
    if (!b) return;
    host.querySelectorAll(".hBtn").forEach(x => x.classList.toggle("active", x === b));
    onChange(b.dataset.h);
  };
}

export async function initTab(opts) {
  const { universe } = opts;
  const app = document.querySelector("#app");
  const st = readState();

  // Declared at the top of the function, not next to their use. drawOverview() runs before the
  // bottom of this function is reached, and `let`/`const` sit in a temporal dead zone until
  // their declaration is *executed* -- so declaring these lower down throws at first render.
  let sortK = "ret", sortAsc = false;
  const cls = v => v == null ? "" : v >= 0 ? "pos" : "neg";
  const yn = v => v == null ? "–" : v ? '<span class="yes">yes</span>' : '<span class="no">no</span>';
  themeToggle();
  initNav(universe);

  let manifest, summary;
  try {
    manifest = await loadManifest(universe);
  } catch (e) {
    app.innerHTML = `<div class="banner fatal"><b>Could not load this tab's manifest.</b>
      ${e.message}. Run <code>python scripts/build_all.py</code> and reload.</div>`;
    return;
  }

  document.title = `${manifest.label} — US Stock Dashboard`;
  const hdr = document.querySelector("#tabTitle");
  if (hdr) hdr.textContent = manifest.label;
  const sub = document.querySelector("#tabMeta");
  if (sub) {
    sub.textContent = `${manifest.source} · ${manifest.dateCount} trading days · ` +
      `${manifest.firstDate} to ${manifest.lastDate} · built ${manifest.builtAt}`;
  }

  // THE validation branch. One place, shared by every tab.
  if (manifest.status !== "ok") {
    Interp.renderValidation(document.querySelector("#validation"), manifest.validation, { open: true });
    app.innerHTML = `<div class="banner fatal">
      <b>No charts are rendered for this tab.</b> Its source workbook did not pass validation, and
      the framework's rule is to say so rather than ship a plausible-looking chart built on data
      that is wrong. The findings are listed above. Drop a corrected workbook into
      <code>data/raw/</code>, re-run <code>python scripts/build_all.py</code>, and this tab will
      render with no code change.</div>`;
    return;
  }

  try {
    summary = await loadSummary(universe);
  } catch (e) {
    app.innerHTML = `<div class="banner fatal"><b>Could not load summary data.</b> ${e.message}</div>`;
    return;
  }

  const dates = summary.dates;
  const n = dates.length;
  let win = horizonWindow(n, st.horizon);

  Interp.renderValidation(document.querySelector("#validation"), summary.validation);
  Interp.renderVerdict(document.querySelector("#verdict"), summary);
  Interp.renderPillars(document.querySelector("#pillars"), summary);
  Interp.renderEvents(document.querySelector("#events"), summary);
  Interp.renderBaskets(document.querySelector("#baskets"), summary);
  Interp.renderSplits(document.querySelector("#splits"), summary);
  Interp.renderRollups(document.querySelector("#rollups"), summary, sparkline);
  Interp.renderCompositeSplit(document.querySelector("#compositeSplit"), summary);
  Interp.renderQuartiles(document.querySelector("#quartiles"), summary);
  if (summary.scatter && summary.scatter.length) {
    const el = document.querySelector("#chScatter");
    if (el) scatterChart(el, {
      title: "Cross-section — 65-day momentum vs total return", h: 320,
      points: summary.scatter, xlabel: "65-day ROC %", ylabel: "return since first print",
      xdec: 1,
    });
  }

  const panelRoot = document.querySelector("#stockPanel");
  let panel = null;
  if (panelRoot) {
    panel = createStockPanel(panelRoot, {
      universe, manifest, dates,
      ticker: st.ticker || manifest.defaultTicker,
      bench: st.bench || manifest.defaultBenchmark,
      zwin: (manifest.zWindows || [21])[0],
    });
    await panel.setTicker(st.ticker || manifest.defaultTicker);
    panelRoot.querySelector("#stockSel").addEventListener("change", ev =>
      writeState({ ticker: ev.target.value }));
    const bells = Object.keys(manifest.tickers).filter(t => manifest.tickers[t].bell);
    prefetch(universe, bells);
  }

  drawOverview();
  horizonControl(h => {
    win = horizonWindow(n, h);
    writeState({ horizon: h });
    drawOverview();
    if (panel) panel.setWindow(win.i0, win.i1);   // the per-ticker panel follows the same window
  }, st.horizon);
  if (panel) panel.setWindow(win.i0, win.i1);

  function drawOverview() {
    const C = (id, cfg) => {
      const el = document.querySelector("#" + id);
      if (!el) return;
      // every universe chart is scoped to the selected horizon
      try { chart(el, Object.assign({ dates, i0: win.i0, i1: win.i1 }, cfg)); }
      catch (e) { el.innerHTML = `<div class="emptyNote">${e.message}</div>`; }
    };

    C("chComp", {
      title: `${manifest.label} — equal-weight composite (daily rebalanced)`, h: 300,
      trimNulls: true, events: summary.events,
      series: [
        { name: "Composite", values: summary.comp, color: "var(--s1)", w: 2, dec: 1 },
        { name: "50-dma", values: summary.comp50, color: "var(--s2)", w: 1.3, dash: "5 4", dec: 1 },
        { name: "200-dma", values: summary.comp200, color: "var(--muted)", w: 1.3, dash: "2 3", dec: 1 },
      ],
    });

    C("chBreadth", {
      title: "Breadth — % of the universe above its moving averages", h: 220,
      min: 0, max: 100, unit: "%", band: [2, 15],
      series: [
        { name: "> 20-dma", values: summary.b20, color: "var(--s1)", w: 1.8, dec: 0 },
        { name: "> 50-dma", values: summary.b50, color: "var(--s2)", w: 1.4, dec: 0 },
        { name: "> 200-dma", values: summary.b200, color: "var(--muted)", w: 1.4, dec: 0 },
      ],
    });

    C("chRoc", {
      title: "Composite 65-day rate of change", h: 190, zero: true, unit: "%",
      series: [{ name: "65d ROC", values: summary.roc65, color: "var(--s1)", w: 1.6, dec: 1 }],
    });

    C("chHml", {
      title: "65-day highs minus lows, % of the universe", h: 190, zero: true,
      series: [{ name: "Highs − lows", values: summary.hml65, color: "var(--s3)", bars: true, dec: 1 }],
      bars: { values: summary.hml65, color: "var(--s3)" },
    });

    C("chSpread", {
      title: "Momentum quintile spread — top minus bottom", h: 190, zero: true, unit: " pts",
      series: [{ name: "Spread", values: summary.spread, color: "var(--s2)", w: 1.6, dec: 1 }],
    });

    C("chScore", {
      title: "RenMac composite score", h: 220, zero: true, min: -100, max: 100,
      series: [
        { name: "Score", values: summary.scores, color: "var(--s1)", w: 1.6, dec: 1 },
        { name: "21d smoothed (chart only)", values: summary.scoresSmooth, color: "var(--s2)",
          w: 1.2, dash: "5 4", dec: 1 },
      ],
    });

    C("chUdv", {
      title: "Up/down volume ratio (20 sessions)", h: 190,
      series: [{ name: "Up/down", values: summary.upDownVol, color: "var(--s3)", w: 1.6, dec: 2 }],
    });

    C("chDist", {
      title: "Distribution and accumulation days (25 sessions)", h: 190, zero: true,
      series: [
        { name: "Distribution", values: summary.distDays, color: "var(--critical)", w: 1.5, dec: 0 },
        { name: "Accumulation", values: summary.accumDays, color: "var(--good-text)", w: 1.5, dec: 0 },
      ],
    });

    C("chObvComp", {
      title: "Composite on-balance volume (millions of shares)", h: 190, trimNulls: true,
      series: [{ name: "OBV", values: summary.obv, color: "var(--s4)", w: 1.6, dec: 0 }],
    });

    // Benchmark comparison, rebased to 100 at the SELECTED window's first index. Benchmarks
    // ship as raw levels precisely so this can be done per horizon; rebasing server-side would
    // hardcode one window and make the 1-month view meaningless.
    const benches = Object.keys(summary.bench || {});
    if (benches.length) {
      const rebase = a => {
        let b = null;
        for (let i = win.i0; i <= win.i1; i++) { if (a[i] != null) { b = a[i]; break; } }
        return b ? a.map(v => v == null ? null : v / b * 100) : a.map(() => null);
      };
      const compR = rebase(summary.comp);
      C("chBenchAbs", {
        title: `Composite vs benchmarks — rebased to 100 at the window start`, h: 230,
        series: [{ name: "Composite", values: compR, color: "var(--s1)", w: 2, dec: 1 }].concat(
          benches.filter(b => b !== "EW basket").map((b, k) => ({
            name: b, values: rebase(summary.bench[b]),
            color: ["var(--s2)", "var(--s4)", "var(--s3)"][k % 3], w: 1.5, dec: 1 }))),
      });
      const primary = manifest.defaultBenchmark;
      if (summary.bench[primary]) {
        const rel = summary.comp.map((v, i) => {
          const b = summary.bench[primary][i];
          return (v == null || b == null || !b) ? null : v / b;
        });
        C("chBenchRel", {
          title: `Composite relative to ${primary} — rebased to 100 at the window start`,
          h: 230, series: [{ name: `vs ${primary}`, values: rebase(rel), color: "var(--s3)", w: 1.8, dec: 1 }],
        });
      }
    }

    // composite-level MACD / RSI / total volume -- parity with the reference dashboard
    C("chCompMacd", {
      title: "Composite MACD (12,26,9)", h: 190, zero: true, trimNulls: true,
      series: [
        { name: "MACD", values: summary.macdLine, color: "var(--s1)", w: 1.4, dec: 2 },
        { name: "Signal", values: summary.macdSignal, color: "var(--s2)", w: 1.1, dash: "5 4", dec: 2 },
        { name: "Histogram", values: summary.macdHist, color: "var(--muted)", bars: true, dec: 2 },
      ],
      bars: { values: summary.macdHist, color: "var(--muted)" },
    });
    C("chCompRsi", {
      title: "Composite RSI (14)", h: 190, min: 0, max: 100, band: [30, 70], trimNulls: true,
      series: [{ name: "RSI", values: summary.rsi, color: "var(--s1)", w: 1.5, dec: 1 }],
    });
    C("chTotVol", {
      title: "Total universe volume (millions of shares) with 50-dma", h: 190, min: 0, trimNulls: true,
      series: [
        { name: "Total volume", values: summary.totVol, color: "var(--muted)", bars: true, dec: 0 },
        { name: "50-dma", values: summary.totVol50, color: "var(--s4)", w: 1.6, dec: 0 },
      ],
      bars: { values: summary.totVol, color: "var(--muted)" },
    });
    C("chX2065", {
      title: "% of the universe with a 20-dma above its 65-dma", h: 190, min: 0, max: 100, unit: "%",
      series: [{ name: "20 > 65", values: summary.x2065, color: "var(--s3)", w: 1.6, dec: 0 }],
    });
    C("chObos", {
      title: "Overbought minus oversold (14-day stochastic)", h: 190, zero: true, unit: " pts",
      series: [{ name: "OB − OS", values: summary.obos, color: "var(--s2)", w: 1.5, dec: 0 }],
    });

    const rib = document.querySelector("#chRegime");
    if (rib) regimeRibbon(rib, summary.runs, dates, REGIME_COLORS, "Regime history (debounced label)");

    drawTable();
  }

  function drawTable() {
    const host = document.querySelector("#stockTable");
    if (!host) return;
    const COLS = [
      ["t", "Ticker", false], ["px", "Price", true], ["ret", "Return %", true],
      ["ret1y", "1y %", true], ["offHi", "Off high %", true], ["hiDate", "High date", false],
      ["roc", "65d ROC %", true], ["a20", "> 20-dma", false], ["a50", "> 50-dma", false],
      ["avgVol", "Avg vol (M)", true], ["relVol", "Rel vol", true],
    ];
    const rows = [...summary.stocks].sort((a, b) => {
      const x = a[sortK], y = b[sortK];
      if (x == null) return 1;
      if (y == null) return -1;
      return (x > y ? 1 : x < y ? -1 : 0) * (sortAsc ? 1 : -1);
    });
    host.innerHTML = `<table class="tbl"><thead><tr>${COLS.map(([k, l, num]) =>
      `<th data-k="${k}" class="${num ? "num" : ""}${k === sortK ? " sorted" : ""}">${l}</th>`).join("")}
      </tr></thead><tbody>${rows.map(r => `<tr>
        <td><a href="#stockPanel" data-goto="${r.t}">${r.t}</a>${r.bell ? ' <span class="star">★</span>' : ""}
          ${r.part ? ' <span class="chip small not-testable">partial</span>' : ""}
          ${r.pinned ? ' <span class="chip small warn">pinned</span>' : ""}</td>
        <td class="num">${fmt(r.px, 2)}</td>
        <td class="num ${cls(r.ret)}">${sign(r.ret)}</td>
        <td class="num ${cls(r.ret1y)}">${sign(r.ret1y)}</td>
        <td class="num ${cls(r.offHi)}">${sign(r.offHi)}</td>
        <td>${r.hiDate || "–"}</td>
        <td class="num ${cls(r.roc)}">${sign(r.roc)}</td>
        <td>${yn(r.a20)}</td><td>${yn(r.a50)}</td>
        <td class="num">${fmt(r.avgVol, 2)}</td>
        <td class="num">${fmt(r.relVol, 2)}</td></tr>`).join("")}</tbody></table>`;
    host.querySelectorAll("th").forEach(th => th.onclick = () => {
      const k = th.dataset.k;
      if (k === sortK) sortAsc = !sortAsc; else { sortK = k; sortAsc = false; }
      drawTable();
    });
    host.querySelectorAll("[data-goto]").forEach(a => a.onclick = ev => {
      if (panel) panel.setTicker(ev.target.dataset.goto);
      writeState({ ticker: ev.target.dataset.goto });
    });
  }

  renderFooter(summary, manifest);
}

export { REGIME_COLORS };

function renderFooter(summary, manifest) {
  const f = document.querySelector("#footer");
  if (!f) return;
  const m = summary.meta;
  const ex = Object.entries(m.excluded || {});
  f.innerHTML = `
    <p><b>Universe.</b> ${m.nFull} full-history names, ${m.nPartial} partial
      ${m.partial.length ? `(${m.partial.join(", ")})` : ""},
      ${m.dropped.length} dropped for insufficient coverage
      ${m.dropped.length ? `(${m.dropped.join(", ")})` : ""}.
      Benchmarks: ${m.benchmarks.join(", ")}.</p>
    ${m.pinned && m.pinned.length ? `<p><b>Price-pinned names.</b> ${m.pinned.join(", ")} trade at a
      single unchanged price through the last session — typically an announced acquisition held at
      deal terms. They are excluded from breadth, momentum and z-score measures, where an unchanged
      price would otherwise read as strength.</p>` : ""}
    ${ex.length ? `<p><b>Excluded at load time.</b> ${ex.map(([t, r]) =>
      `<span title="${r}">${t}</span>`).join(", ")} — each with a written reason in
      <code>config/universes.json</code>; hover for detail.</p>` : ""}
    <p><b>Method.</b> The composite is equal-weight and rebalanced daily. Structure is read off a
      trailing ${252}-session window. The regime label is debounced by majority vote over a
      10-session dissent window; the smoothed score on the score chart is presentational and never
      gates a regime. Pillars with insufficient data are dropped and the remaining weights
      renormalised — coverage is stated on the verdict.</p>
    <p class="src">Source: ${manifest.source} · ${manifest.dateCount} trading days ·
      built ${manifest.builtAt} · version ${manifest.version}</p>`;
}
