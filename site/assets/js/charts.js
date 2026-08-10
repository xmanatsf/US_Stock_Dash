/* Inline-SVG chart engine. No libraries, no network calls, works from file://.
 *
 * Ported from dashboard_template.html's render(), with two mandatory fixes:
 *
 *  1. DATES COME FROM cfg, NOT A GLOBAL. The original closed over a page-level `DATA.dates`,
 *     which makes it impossible to render two universes on one page, and silently mis-renders
 *     any series whose array starts at its own first print (every shard does).
 *
 *  2. ONE RESIZE LISTENER, in a module-level registry. The original added a listener per chart
 *     element and never removed it, leaking one closure per dropdown switch. destroyChart()
 *     now makes teardown explicit and REGISTRY.size is directly assertable in a test.
 *
 * The bipolar-bar fix (y: min(baseY,vY), height: abs(baseY-vY)) lives HERE and only here.
 * The naive form emits a negative SVG height for below-baseline bars -- a MACD histogram -- which
 * Chromium logs as an error and silently declines to paint. It does not look wrong in a
 * screenshot, so it must not be reintroduced in a per-chart code path.
 */

const NS = "http://www.w3.org/2000/svg";
const REGISTRY = new Set();
let _resizeInstalled = false;

export function fmt(v, d = 1) {
  if (v == null || Number.isNaN(v)) return "–";
  return v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
}
export function sign(v, d = 1) {
  if (v == null || Number.isNaN(v)) return "–";
  return (v > 0 ? "+" : "") + fmt(v, d);
}
export function debounce(f, ms) {
  let t;
  return (...a) => { clearTimeout(t); t = setTimeout(() => f(...a), ms); };
}

const _onResize = debounce(() => {
  for (const el of REGISTRY) { if (el.isConnected && el.__render) el.__render(); }
}, 150);

export function monthTicks(dates) {
  const out = []; let cur = "";
  dates.forEach((d, i) => { const m = d.slice(0, 7); if (m !== cur) { cur = m; out.push(i); } });
  return out.filter((_, k) => k > 0);   // drop the partial first month to avoid label crowding
}

export function niceTicks(lo, hi, n = 5) {
  const span = hi - lo;
  if (!(span > 0)) return [lo];
  const step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1, 2, 2.5, 5, 10].map(s => s * mag).find(s => span / s <= n + 1) || mag * 10;
  const t = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) t.push(v);
  return t;
}

export function chart(el, cfg) {
  if (!el) return;
  if (!cfg || !Array.isArray(cfg.dates)) throw new Error("chart(): cfg.dates is required");
  if (el.__chart) destroyChart(el);
  el.__chart = true;
  el.__cfg = cfg;
  el.__render = () => render(el, cfg);
  el.__render();
  REGISTRY.add(el);
  if (!_resizeInstalled) { addEventListener("resize", _onResize); _resizeInstalled = true; }
}

export function destroyChart(el) {
  if (!el) return;
  REGISTRY.delete(el);
  el.__chart = false;
  el.__render = null;
  el.__cfg = null;
  el.innerHTML = "";
}

export function clearCharts(root) {
  (root || document).querySelectorAll("[data-chart]").forEach(destroyChart);
}

export function liveChartCount() { return REGISTRY.size; }   // for the leak test

export function emptyCard(el, title, msg) {
  if (!el) return;
  destroyChart(el);
  el.innerHTML = `<div class="chartHead"><span class="chartTitle">${title}</span></div>
    <div class="emptyNote">${msg}</div>`;
}

export function render(el, cfg) {
  el.innerHTML = "";
  const dates = cfg.dates, n = dates.length;
  const series = (cfg.series || []).filter(s => s && Array.isArray(s.values));

  const head = document.createElement("div");
  head.className = "chartHead";
  head.innerHTML = `<span class="chartTitle">${cfg.title || ""}</span>` +
    (series.length > 1
      ? `<span class="legend">${series.map(s =>
          `<span><span class="sw" style="background:${s.color}"></span>${s.name}</span>`).join("")}</span>`
      : "");
  el.appendChild(head);

  const W = Math.max(el.clientWidth - 36, 320), H = cfg.h || 260;
  const P = { t: cfg.events && cfg.events.length ? 46 : 18, r: 14, b: 24, l: 46 };

  // Explicit window first (the horizon control), then trimNulls narrows further within it.
  let i0 = Number.isInteger(cfg.i0) ? Math.max(0, cfg.i0) : 0;
  let i1 = Number.isInteger(cfg.i1) ? Math.min(n - 1, cfg.i1) : n - 1;
  if (cfg.trimNulls) {
    let lo = null, hi = null;
    for (const s of series) {
      for (let i = i0; i <= i1 && i < s.values.length; i++) {
        if (s.values[i] != null) { if (lo == null || i < lo) lo = i; if (hi == null || i > hi) hi = i; }
      }
    }
    // narrow WITHIN the requested window, never widen past it
    if (lo != null) { i0 = Math.max(i0, lo); i1 = Math.min(i1, hi); }
  }
  if (i1 <= i0) { i0 = 0; i1 = Math.max(1, n - 1); }

  const vals = [];
  for (const s of series) {
    for (let i = i0; i <= i1; i++) { const v = s.values[i]; if (v != null) vals.push(v); }
  }
  if (!vals.length) {
    el.innerHTML += `<div class="emptyNote">no data in range</div>`;
    return;
  }
  let lo = cfg.min != null ? cfg.min : Math.min(...vals);
  let hi = cfg.max != null ? cfg.max : Math.max(...vals);
  if (cfg.zero) { if (lo > 0) lo = 0; if (hi < 0) hi = 0; }
  if (lo === hi) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * 0.06;
  if (cfg.min == null) lo -= pad;
  if (cfg.max == null) hi += pad;

  const span = Math.max(i1 - i0, 1);
  const X = i => P.l + (W - P.l - P.r) * (i - i0) / span;
  const Y = v => P.t + (H - P.t - P.b) * (1 - (v - lo) / (hi - lo));

  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", cfg.title || "chart");
  svg.style.display = "block";
  const add = (tag, at, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in at) e.setAttribute(k, at[k]);
    (parent || svg).appendChild(e);
    return e;
  };

  if (cfg.band) {
    add("rect", { x: P.l, y: Y(cfg.band[1]), width: W - P.l - P.r,
                  height: Math.abs(Y(cfg.band[0]) - Y(cfg.band[1])), fill: "var(--band)" });
  }
  niceTicks(lo, hi).forEach(v => {
    add("line", { x1: P.l, x2: W - P.r, y1: Y(v), y2: Y(v),
                  stroke: v === 0 ? "var(--axis)" : "var(--grid)", "stroke-width": 1 });
    const t = add("text", { x: P.l - 6, y: Y(v) + 3, "text-anchor": "end" });
    t.textContent = fmt(v, cfg.ydec != null ? cfg.ydec : 0) + (cfg.unit || "");
  });
  monthTicks(dates.slice(i0, i1 + 1)).forEach(k => {
    const i = i0 + k;
    const t = add("text", { x: X(i), y: H - 6, "text-anchor": "middle" });
    t.textContent = dates[i].slice(2, 7);
  });
  add("line", { x1: P.l, x2: W - P.r, y1: H - P.b, y2: H - P.b, stroke: "var(--axis)" });

  // BARS -- the bipolar fix. baseY is the zero line, or the axis floor when the range does not
  // cross zero. Using min()/abs() means a below-baseline bar never emits a negative height.
  if (cfg.bars && Array.isArray(cfg.bars.values)) {
    const bw = Math.max(1, (W - P.l - P.r) / (span + 1) - 1);
    const baseY = Y(Math.max(lo, 0));
    for (let i = i0; i <= i1; i++) {
      const v = cfg.bars.values[i];
      if (v == null || v === 0) continue;
      const vY = Y(v);
      add("rect", { x: X(i) - bw / 2, y: Math.min(baseY, vY), width: bw,
                    height: Math.abs(baseY - vY), rx: 1, fill: cfg.bars.color });
    }
  }

  series.forEach(s => {
    if (s.bars) return;                       // drawn by cfg.bars; see the double-spec note below
    let d = "", pen = false;
    for (let i = i0; i <= i1; i++) {
      const v = s.values[i];
      if (v == null) { pen = false; continue; }
      d += (pen ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1);
      pen = true;
    }
    if (d) add("path", { d, fill: "none", stroke: s.color, "stroke-width": s.w || 2,
                         "stroke-dasharray": s.dash || "", "stroke-linejoin": "round",
                         "stroke-linecap": "round" });
  });

  if (cfg.events && cfg.events.length) {
    const KIND = { critical: "var(--critical)", serious: "var(--serious)", info: "var(--s1)" };
    cfg.events.forEach((e, k) => {
      if (e.i < i0 || e.i > i1) return;
      const x = X(e.i), cy = 10 + (k % 2) * 18;
      add("line", { x1: x, x2: x, y1: cy + 8, y2: H - P.b, stroke: KIND[e.kind] || "var(--s1)",
                    "stroke-width": 1, "stroke-dasharray": "3 3", opacity: .65 });
      add("circle", { cx: x, cy, r: 8, fill: KIND[e.kind] || "var(--s1)" });
      const t = add("text", { x, y: cy + 3.5, "text-anchor": "middle", class: "evNum" });
      t.textContent = k + 1;
    });
  }

  el.appendChild(svg);

  // hover layer
  const tip = document.createElement("div");
  tip.className = "tip";
  el.appendChild(tip);
  const cross = add("line", { y1: P.t, y2: H - P.b, stroke: "var(--crosshair)",
                              "stroke-width": 1, visibility: "hidden" });
  const lineSeries = series.filter(s => !s.bars);
  const dots = lineSeries.map(s => add("circle", { r: 3.5, fill: s.color, stroke: "var(--surface)",
                                                   "stroke-width": 2, visibility: "hidden" }));
  svg.addEventListener("mousemove", ev => {
    const r = svg.getBoundingClientRect(), sx = W / r.width;
    const px = (ev.clientX - r.left) * sx;
    let i = i0 + Math.round((px - P.l) / (W - P.l - P.r) * span);
    i = Math.max(i0, Math.min(i1, i));
    cross.setAttribute("x1", X(i)); cross.setAttribute("x2", X(i));
    cross.setAttribute("visibility", "visible");
    let rows = "";
    series.forEach(s => {
      const v = s.values[i];
      if (!s.bars) {
        const dot = dots[lineSeries.indexOf(s)];
        if (dot) {
          if (v == null) dot.setAttribute("visibility", "hidden");
          else {
            dot.setAttribute("cx", X(i)); dot.setAttribute("cy", Y(v));
            dot.setAttribute("visibility", "visible");
          }
        }
      }
      rows += `<div class="row"><span>${s.name}</span><b>${v == null ? "–" :
        fmt(v, s.dec != null ? s.dec : 1) + (cfg.unit || "")}</b></div>`;
    });
    tip.innerHTML = `<div class="d">${dates[i]}</div>` + rows;
    tip.style.display = "block";
    const eb = el.getBoundingClientRect();
    let tx = (ev.clientX - eb.left) + 14;
    if (tx + tip.offsetWidth > eb.width - 8) tx = (ev.clientX - eb.left) - tip.offsetWidth - 14;
    tip.style.left = tx + "px";
    tip.style.top = Math.min((ev.clientY - eb.top) + 10, eb.height - tip.offsetHeight - 8) + "px";
  });
  svg.addEventListener("mouseleave", () => {
    tip.style.display = "none";
    cross.setAttribute("visibility", "hidden");
    dots.forEach(d => d.setAttribute("visibility", "hidden"));
  });
}

/* NOTE on histograms, which trip up every refactor of this file:
 * a histogram is specified TWICE on purpose -- once inside `series` with bars:true so it appears
 * in the legend and the hover tooltip, and again as the top-level `cfg.bars` which actually draws
 * the rects. The line loop skips it (`if (s.bars) return`) and the hover dots exclude it.
 * Unifying the two silently drops either the legend entry or the bars themselves. */

// ---------------------------------------------------------------- scatter (no time axis)

export function scatterChart(el, cfg) {
  if (!el) return;
  destroyChart(el);
  el.__chart = true;
  el.__render = () => _scatter(el, cfg);
  el.__render();
  REGISTRY.add(el);
  if (!_resizeInstalled) { addEventListener("resize", _onResize); _resizeInstalled = true; }
}

function _scatter(el, cfg) {
  el.innerHTML = "";
  const head = document.createElement("div");
  head.className = "chartHead";
  head.innerHTML = `<span class="chartTitle">${cfg.title || ""}</span>
    <span class="legend">
      <span><span class="sw dot" style="background:var(--good-text)"></span>positive</span>
      <span><span class="sw dot" style="background:var(--critical)"></span>negative</span></span>`;
  el.appendChild(head);

  const pts = (cfg.points || []).filter(p => p.x != null && p.y != null);
  if (!pts.length) { el.innerHTML += `<div class="emptyNote">no data</div>`; return; }
  const W = Math.max(el.clientWidth - 36, 320), H = cfg.h || 300;
  const P = { t: 18, r: 16, b: 34, l: 46 };
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  let xlo = Math.min(...xs), xhi = Math.max(...xs), ylo = Math.min(...ys), yhi = Math.max(...ys);
  const xp = (xhi - xlo) * 0.08 || 1, yp = (yhi - ylo) * 0.08 || 1;
  xlo -= xp; xhi += xp; ylo -= yp; yhi += yp;
  const X = v => P.l + (W - P.l - P.r) * (v - xlo) / (xhi - xlo);
  const Y = v => P.t + (H - P.t - P.b) * (1 - (v - ylo) / (yhi - ylo));

  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.style.display = "block";
  const add = (tag, at) => { const e = document.createElementNS(NS, tag);
    for (const k in at) e.setAttribute(k, at[k]); svg.appendChild(e); return e; };

  niceTicks(ylo, yhi).forEach(v => {
    add("line", { x1: P.l, x2: W - P.r, y1: Y(v), y2: Y(v),
                  stroke: v === 0 ? "var(--axis)" : "var(--grid)", "stroke-width": 1 });
    const t = add("text", { x: P.l - 6, y: Y(v) + 3, "text-anchor": "end" });
    t.textContent = fmt(v, 0) + (cfg.yunit || "%");
  });
  niceTicks(xlo, xhi).forEach(v => {
    add("line", { x1: X(v), x2: X(v), y1: P.t, y2: H - P.b, stroke: "var(--grid)", "stroke-width": 1 });
    const t = add("text", { x: X(v), y: H - P.b + 16, "text-anchor": "middle" });
    t.textContent = fmt(v, cfg.xdec != null ? cfg.xdec : 1);
  });
  add("line", { x1: P.l, x2: W - P.r, y1: H - P.b, y2: H - P.b, stroke: "var(--axis)" });
  add("line", { x1: P.l, x2: P.l, y1: P.t, y2: H - P.b, stroke: "var(--axis)" });

  const tip = document.createElement("div");
  tip.className = "tip";
  el.appendChild(tip);

  pts.forEach(p => {
    add("circle", { cx: X(p.x), cy: Y(p.y), r: p.bell ? 5.5 : 3.5,
                    fill: p.y >= 0 ? "var(--good-text)" : "var(--critical)",
                    opacity: p.bell ? .95 : .55,
                    stroke: p.bell ? "var(--ink)" : "none", "stroke-width": p.bell ? 1 : 0,
                    "data-t": p.t });
  });
  // ONE delegated handler, not one per point (the original bound a listener per circle)
  svg.addEventListener("mousemove", ev => {
    const el2 = ev.target;
    if (el2.tagName !== "circle") { tip.style.display = "none"; return; }
    const p = pts.find(q => q.t === el2.getAttribute("data-t"));
    if (!p) return;
    tip.innerHTML = `<div class="d">${p.t}${p.bell ? " ★" : ""}</div>
      <div class="row"><span>${cfg.xlabel || "x"}</span><b>${fmt(p.x, cfg.xdec != null ? cfg.xdec : 2)}</b></div>
      <div class="row"><span>${cfg.ylabel || "return"}</span><b>${sign(p.y)}%</b></div>
      ${p.group ? `<div class="row"><span>Group</span><b>${p.group}</b></div>` : ""}`;
    tip.style.display = "block";
    const eb = el.getBoundingClientRect();
    let tx = (ev.clientX - eb.left) + 14;
    if (tx + 170 > eb.width - 8) tx = (ev.clientX - eb.left) - 184;
    tip.style.left = tx + "px";
    tip.style.top = Math.max(0, (ev.clientY - eb.top) - 40) + "px";
  });
  svg.addEventListener("mouseleave", () => { tip.style.display = "none"; });
  el.appendChild(svg);
}

// ---------------------------------------------------------------- sparkline & ribbon

export function sparkline(values, w = 90, h = 22) {
  const vals = (values || []).filter(v => v != null);
  if (!vals.length) return "";
  const lo = Math.min(...vals), hi = Math.max(...vals), span = (hi - lo) || 1;
  const step = w / Math.max(1, values.length - 1);
  let d = "", pen = false;
  values.forEach((v, i) => {
    if (v == null) { pen = false; return; }
    const x = i * step, y = h - 2 - (v - lo) / span * (h - 4);
    d += (pen ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
    pen = true;
  });
  const up = vals[vals.length - 1] >= vals[0];
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><path d="${d}"
    fill="none" stroke="${up ? "var(--good-text)" : "var(--critical)"}" stroke-width="1.5"/></svg>`;
}

/** Regime strip chart: compressed runs, not a line. */
export function regimeRibbon(el, runs, dates, colors, title) {
  if (!el) return;
  destroyChart(el);
  const n = dates.length;
  const W = Math.max(el.clientWidth - 36, 320), H = 46;
  el.innerHTML = `<div class="chartHead"><span class="chartTitle">${title || "Regime history"}</span></div>`;
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.style.display = "block";
  const tip = document.createElement("div");
  tip.className = "tip";
  (runs || []).forEach(r => {
    const x0 = W * r.startIdx / n, x1 = W * (r.endIdx + 1) / n;
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("x", x0); rect.setAttribute("y", 6);
    rect.setAttribute("width", Math.max(1, x1 - x0)); rect.setAttribute("height", 22);
    rect.setAttribute("fill", (colors || {})[r.label] || "var(--muted)");
    rect.setAttribute("data-label", r.label);
    rect.setAttribute("data-range", `${r.start} → ${r.end}`);
    svg.appendChild(rect);
  });
  const ticks = monthTicks(dates).filter((_, k) => k % 6 === 0);
  ticks.forEach(i => {
    const t = document.createElementNS(NS, "text");
    t.setAttribute("x", W * i / n); t.setAttribute("y", H - 4);
    t.setAttribute("text-anchor", "middle");
    t.textContent = dates[i].slice(0, 7);
    svg.appendChild(t);
  });
  svg.addEventListener("mousemove", ev => {
    if (ev.target.tagName !== "rect") { tip.style.display = "none"; return; }
    tip.innerHTML = `<div class="d">${ev.target.getAttribute("data-label")}</div>
      <div class="row"><span>${ev.target.getAttribute("data-range")}</span></div>`;
    tip.style.display = "block";
    const eb = el.getBoundingClientRect();
    tip.style.left = Math.min((ev.clientX - eb.left) + 12, eb.width - 200) + "px";
    tip.style.top = "26px";
  });
  svg.addEventListener("mouseleave", () => { tip.style.display = "none"; });
  el.appendChild(svg);
  el.appendChild(tip);
}
