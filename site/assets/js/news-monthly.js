/* Monthly News Intelligence page (September 2026 onward).
 *
 * A sibling of the weekly News page with a different citation contract. The weekly page links each
 * claim to one article in a source audit; the monthly canvas this page is transcribed from cites by
 * OUTLET AND DATE, and build_monthly.py fails on any Reported, Analysis or market-implied item that
 * lacks either. So every claim here renders as: a kind chip, the claim, and its source line.
 *
 * The kind chip is the page's core convention and is carried over from the canvas:
 *   Reported (solid) · Analysis (outline) · Our read (tinted) · Scenario (dashed) · Market-implied.
 * Only market prices carry probabilities. Brief counts are generated from the census, never typed.
 *
 * Organisation is the canvas's; styling is dashboard.css tokens with ig-m prefixed classes.
 */

import { loadIndex } from "./data-client.js";
import { initNav } from "./tabs.js";

const esc = s => String(s ?? "").replace(/[&<>"]/g,
  c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const KIND_LABEL = { reported: "Reported", analysis: "Analysis", ours: "Our read",
  scenario: "Scenario", market: "Market-implied" };
let THEMES = {};

const kindChip = k => k ? `<span class="ig-mk ig-mk-${esc(k)}">${esc(KIND_LABEL[k] || k)}</span>` : "";
const srcLine = s => s ? `<span class="ig-msrc">${esc(s)}</span>` : "";
const tone = t => (THEMES[t] || {}).tone || "s1";
const toneCls = t => `ig-mt-${tone(t)}`;

function claim(c) {
  return `<li class="ig-mclaim">${kindChip(c.kind)} <span>${esc(c.text)}</span> ${srcLine(c.src)}</li>`;
}
const after = b => b.after ? `<ul class="ig-mclaims ig-mafter">${claim(b.after)}</ul>` : "";
const head = (b, extra = "") => `<div class="ig-mhead"><h3>${esc(b.title || "")}</h3>${
  kindChip(b.kind)}${extra}</div>${b.note ? `<p class="note">${esc(b.note)}</p>` : ""}`;

/* ------------------------------------------------------------------ block renderers */

const R = {};

R.prose = b => `<div class="card ig-mprose">${head(b)}<p>${esc(b.text)}</p>${srcLine(b.src)}</div>`;

R.tiles = b => `<div class="card">${head(b)}<div class="ig-mtiles">${b.items.map(it => `
  <div class="ig-mtile"><div class="ig-mtileLab">${esc(it.label)}</div>
    <div class="ig-mtileVal">${esc(it.value)}</div>
    ${it.note ? `<div class="ig-mtileNote">${esc(it.note)}</div>` : ""}${srcLine(it.src)}</div>`).join("")}
  </div>${srcLine(b.src)}${after(b)}</div>`;

R.cards = b => `<div class="ig-mblock">${head(b)}<div class="ig-mcards">${b.cards.map(cd => `
  <div class="card ig-mcard ${cd.theme ? toneCls(cd.theme) : ""}">
    ${cd.kicker ? `<div class="ig-kicker">${esc(cd.kicker)}</div>` : ""}
    <div class="ig-mcardHead"><b>${esc(cd.title)}</b>${
      cd.status ? `<span class="chip small ig-status">${esc(cd.status)}</span>` : ""}</div>
    <ul class="ig-mclaims">${cd.claims.map(claim).join("")}</ul></div>`).join("")}</div>${after(b)}</div>`;

R.steps = b => `<div class="card">${head(b)}<ol class="ig-msteps">${b.items.map((it, i) => `
  <li><span class="ig-mstepN">${i + 1}</span><b>${esc(it.title)}</b>
    <span class="ig-mstepVal">${esc(it.value)}</span><span>${esc(it.text)}</span>${srcLine(it.src)}</li>`
  ).join("")}</ol>${after(b)}</div>`;

R.events = b => `<div class="card">${head(b)}<ul class="ig-mevents">${b.items.map(it => `
  <li><span class="ig-mwhen">${esc(it.when)}</span><span>${esc(it.text)} ${srcLine(it.src)}</span></li>`
  ).join("")}</ul>${srcLine(b.src)}${after(b)}</div>`;

R.calendar = b => `<div class="card">${head(b)}<ul class="ig-mevents">${b.items.map(it => `
  <li><span class="ig-mwhen">${esc(it.date)}</span><span>${esc(it.text)} ${srcLine(it.src)}</span></li>`
  ).join("")}</ul>${srcLine(b.src)}</div>`;

R.ranking = b => `<div class="card">${head(b)}<ol class="ig-mrank">${b.items.map(it => `
  <li><b>${esc(it.title)}</b> <span>${esc(it.text)}</span>
    <div class="ig-mwatch"><i>Watch:</i> ${esc(it.watch)}</div></li>`).join("")}</ol></div>`;

R.scenarios = b => `<div class="ig-mblock">${head(b)}<div class="ig-mcards">${b.items.map(it => `
  <div class="card ig-mscen"><b>${esc(it.name)}</b><p>${esc(it.body)}</p>
    <p class="ig-mwatch"><i>Signposts:</i> ${esc(it.signposts)}</p>${srcLine(it.src)}</div>`).join("")}
  </div></div>`;

R.odds = b => `<div class="card">${head({ ...b, kind: "market" })}<div class="ig-modds">${b.items.map(it => `
  <div class="ig-modd"><span>${esc(it.label)}</span><b>${esc(it.value)}</b></div>`).join("")}</div>
  ${srcLine(b.src)}${after(b)}</div>`;

R.table = b => {
  const sc = b.srcCol;
  return `<div class="card">${head(b)}<div class="tblWrap ig-mtbl"><table><thead><tr>${
    b.cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${b.rows.map(r => `<tr>${
    r.map((v, i) => `<td${i === sc ? ' class="ig-msrcCell"' : ""}>${esc(v)}</td>`).join("")}</tr>`).join("")
  }</tbody></table></div>${srcLine(b.src)}${after(b)}</div>`;
};

R.conflicts = b => `<div class="card">${head(b)}<div class="tblWrap ig-mtbl"><table><thead><tr>
  <th>Item</th><th>Source A</th><th>Source B</th><th>How this page treats it</th></tr></thead><tbody>${
  b.rows.map(r => `<tr><td><b>${esc(r.item)}</b></td><td>${esc(r.a)}</td><td>${esc(r.b)}</td>
    <td>${esc(r.treatment)}</td></tr>`).join("")}</tbody></table></div></div>`;

R.bars = b => {
  const cap = b.cap || Math.max(...b.items.map(i => i.v));
  return `<div class="card">${head(b)}<div class="ig-mbars">${b.items.map(it => {
    const w = Math.min(100, it.v / cap * 100);
    return `<div class="ig-mbar"><span class="ig-mbarLab">${esc(it.label)}</span>
      <span class="ig-mbarTrack"><span style="width:${w.toFixed(1)}%"${
        it.v > cap ? ' class="off"' : ""}></span></span><b>${esc(it.display)}</b></div>`;
  }).join("")}</div>${srcLine(b.src)}${after(b)}</div>`;
};

R.flow = b => `<div class="card">${head(b)}<div class="ig-mflow">${b.columns.map((col, ci) => `
  ${ci ? '<div class="ig-marrow" aria-hidden="true">→</div>' : ""}
  <div class="ig-mflowCol"><div class="ig-kicker">${esc(col.title || "")}</div>${col.nodes.map(n => `
    <div class="ig-mnode ${toneCls(n.theme)}"><b>${esc(n.title)}</b>${
      n.lines.length ? `<ul>${n.lines.map(l => `<li>${esc(l)}</li>`).join("")}</ul>` : ""}${srcLine(n.src)}</div>`
  ).join("")}</div>`).join("")}</div>${after(b)}</div>`;

/* A static dated series as an inline SVG line. Points are levels the briefs state, nothing is
 * interpolated between them beyond the drawn segment, and each point keeps its outlet in a
 * tooltip and in the table view underneath. */
R.series = b => {
  const W = 640, H = 230, L = 46, Rp = 14, T = 16, B = 28;
  const day = d => Number(d.slice(8, 10));
  const xs = d => L + (day(d) - 1) / 25 * (W - L - Rp);
  const vals = b.points.map(p => p.v);
  let lo = b.yMin ?? Math.min(...vals), hi = b.yMax ?? Math.max(...vals);
  if (b.ref) { lo = Math.min(lo, b.ref.v); hi = Math.max(hi, b.ref.v); }
  const pad = (hi - lo) * 0.08 || 1;
  if (b.yMin === undefined) lo -= pad;
  if (b.yMax === undefined) hi += pad;
  const ys = v => T + (hi - v) / (hi - lo) * (H - T - B);
  const dec = b.dec ?? 2;
  const fmt = v => b.unit === "$" ? `$${v.toFixed(dec)}` : `${v.toFixed(dec)}${b.unit || ""}`;
  const ticks = Array.from({ length: 5 }, (_, i) => lo + (hi - lo) * i / 4);
  const segs = {};
  b.points.forEach(p => (segs[p.seg || "_"] = segs[p.seg || "_"] || []).push(p));
  const segNames = Object.keys(segs);
  const lines = segNames.map((k, si) => `<polyline class="ig-mline${si ? " alt" : ""}" points="${
    segs[k].map(p => `${xs(p.d).toFixed(1)},${ys(p.v).toFixed(1)}`).join(" ")}"/>`).join("");
  const dots = b.points.map(p => `<circle class="ig-mdot" cx="${xs(p.d).toFixed(1)}" cy="${
    ys(p.v).toFixed(1)}" r="3.6"><title>Sep ${day(p.d)} · ${esc(fmt(p.v))}${
    p.label ? " · " + esc(p.label) : ""} (${esc(p.src)})</title></circle>`).join("");
  const last = b.points[b.points.length - 1];
  const svg = `<svg class="ig-mchart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(b.title)}">
    ${ticks.map(t => `<line class="ig-mgrid" x1="${L}" x2="${W - Rp}" y1="${ys(t)}" y2="${ys(t)}"/>
      <text class="ig-maxis" x="${L - 6}" y="${ys(t) + 3.5}" text-anchor="end">${esc(fmt(t))}</text>`).join("")}
    ${[1, 5, 10, 15, 20, 25].map(d => `<text class="ig-maxis" x="${xs("2026-09-" + String(d).padStart(2, "0"))}"
      y="${H - 8}" text-anchor="middle">Sep ${d}</text>`).join("")}
    ${b.ref ? `<line class="ig-mref" x1="${L}" x2="${W - Rp}" y1="${ys(b.ref.v)}" y2="${ys(b.ref.v)}"/>` : ""}
    ${b.marker ? `<line class="ig-mmark" x1="${xs(b.marker.d)}" x2="${xs(b.marker.d)}" y1="${T}" y2="${H - B}"/>
      <text class="ig-maxis ig-mmarkLab" x="${xs(b.marker.d) + 4}" y="${T + 9}">${esc(b.marker.label)}</text>` : ""}
    ${lines}${dots}
    <text class="ig-mlast" x="${Math.min(xs(last.d), W - Rp - 2)}" y="${ys(last.v) - 8}" text-anchor="end">${
      esc(fmt(last.v))}</text></svg>`;
  const legend = segNames.length > 1 ? `<div class="ig-legend">${segNames.map((k, i) =>
    `<span class="ig-legItem"><i class="ig-mleg${i ? " alt" : ""}"></i>${esc(k)}</span>`).join("")}</div>` : "";
  return `<div class="card">${head(b)}${svg}${legend}
    <details class="ig-det"><summary>Table view · ${b.points.length} dated levels</summary>
      <div class="tblWrap ig-mtbl"><table><thead><tr><th>Date</th><th>Level</th><th>Note</th><th>Source</th></tr></thead>
      <tbody>${b.points.map(p => `<tr><td>Sep ${day(p.d)}</td><td>${esc(fmt(p.v))}</td>
        <td>${esc(p.label || p.seg || "")}</td><td class="ig-msrcCell">${esc(p.src)}</td></tr>`).join("")}</tbody></table></div>
    </details>${srcLine(b.src)}${after(b)}</div>`;
};

R.heatmap = (b, doc) => {
  const n = b.dates.map(d => doc.generated.byDate[d]);
  const maxN = Math.max(...n);
  return `<div class="card">${head(b, ` <span class="note">${esc(b.subtitle || "")}</span>`)}
    <div class="tblWrap ig-mheatWrap"><table class="ig-mheat"><thead>
      <tr><th class="ig-mheatLab">Briefs per file date</th>${n.map(v =>
        `<th><span class="ig-mnbar" style="height:${Math.round(v / maxN * 34)}px"></span>${v}</th>`).join("")}</tr>
      <tr><th></th>${b.dates.map(d => `<th class="ig-mdate">Sep ${Number(d.slice(8))}</th>`).join("")}</tr></thead>
      <tbody>${b.rows.map(r => `<tr class="${toneCls(r.theme)}"><th class="ig-mheatLab"><i class="ig-msw"></i>${
        esc(r.name)}</th>${r.v.map((v, i) => `<td style="--pct:${v}%" class="${v >= 50 ? "hi" : ""}"
          title="${esc(r.name)}, Sep ${Number(b.dates[i].slice(8))}: ${v}% of ${n[i]} briefs">${v}%</td>`).join("")}</tr>`).join("")}
      </tbody></table></div></div>`;
};

R.sourcebase = (b, doc) => {
  const g = doc.generated;
  const max = Math.max(...g.byPublication.map(p => p.n));
  return `<div class="card">${head(b, ' <span class="chip small scope">generated</span>')}
    <div class="ig-mbars">${g.byPublication.map(p => `<div class="ig-mbar"><span class="ig-mbarLab">${
      esc(p.label)}</span><span class="ig-mbarTrack"><span style="width:${(p.n / max * 100).toFixed(1)}%"></span></span>
      <b>${p.n}</b></div>`).join("")}</div>
    <p class="note">${g.counts.briefs} briefs across ${g.counts.files} files and ${g.counts.dates} file dates
      (${esc(doc.window.from)} to ${esc(doc.window.to)}), counted from the brief files by
      <code>census_briefs.py</code>. Articles published ${esc(doc.window.published)}.</p></div>`;
};

R.timeline = b => {
  const keys = ["all", ...new Set(b.stories.map(s => s.theme))];
  return `<div class="card ig-mtl" data-sel="all">
    <div class="ig-mtlFilters">${keys.map(k => `<button class="hBtn ig-mtlF${k === "all" ? " active" : ""}"
      data-k="${esc(k)}" aria-pressed="${k === "all"}">${k === "all" ? "All stories" :
      `<i class="ig-msw ${toneCls(k)}"></i>${esc(THEMES[k].label)}`}</button>`).join("")}</div>
    <div class="tblWrap ig-mtlWrap"><table class="ig-mtlGrid"><thead><tr><th></th>${b.weeks.map(w => `
      <th><div class="ig-kicker">${esc(w.label)}</div><div class="ig-mwk">${esc(w.title)} ${kindChip("ours")}</div>
        <div class="ig-mgauges">${w.gauges.map(g => `<span>${esc(g)}</span>`).join("")}</div></th>`).join("")}</tr></thead>
    <tbody>${b.stories.map(s => `<tr class="ig-mtlRow ${toneCls(s.theme)}" data-k="${esc(s.theme)}">
      <th><i class="ig-msw"></i><b>${esc(s.name)}</b><div class="note">${esc(s.arc)}</div></th>${
      s.cells.map(c => `<td><b>${esc(c.t)}</b><p>${esc(c.x)}</p>${srcLine(c.s)}</td>`).join("")}</tr>`).join("")}
    </tbody></table></div></div>`;
};

function wireTimeline(host) {
  host.querySelectorAll(".ig-mtl").forEach(tl => {
    tl.querySelectorAll(".ig-mtlF").forEach(btn => btn.addEventListener("click", () => {
      const k = btn.dataset.k;
      tl.querySelectorAll(".ig-mtlF").forEach(o => {
        o.classList.toggle("active", o === btn);
        o.setAttribute("aria-pressed", String(o === btn));
      });
      tl.querySelectorAll(".ig-mtlRow").forEach(r =>
        r.classList.toggle("dim", k !== "all" && r.dataset.k !== k));
      tl.dataset.sel = k;
    }));
  });
}

/* ------------------------------------------------------------------ page */

function renderMasthead(doc) {
  const g = doc.generated.counts;
  const ov = doc.sections[0];
  document.querySelector("#tabTitle").textContent = doc.title;
  document.querySelector("#tabMeta").textContent =
    `Briefs dated ${doc.window.from} to ${doc.window.to} · ${g.briefs} briefs · ${g.files} files · ` +
    `${doc.generated.byPublication.map(p => p.label).join(", ")}`;
  document.querySelector("#masthead").innerHTML = `
    <div class="card mast">
      <div class="ig-kicker">${esc(ov.kicker)}</div>
      <h2 class="mastHead">${esc(ov.title)}</h2>
      <p class="mastStand">${esc(ov.dek)}</p>
    </div>`;
  document.querySelector("#legend").innerHTML = `<div class="ig-mlegend">
    <span class="ig-kicker">How to read every claim</span>${doc.legend.map(l =>
      `<span class="ig-mlegItem">${kindChip(l.kind)} ${esc(l.text)}</span>`).join("")}</div>`;
}

function renderSections(doc) {
  const host = document.querySelector("#sections");
  host.innerHTML = doc.sections.map((s, i) => `
    <section id="sec-${esc(s.id)}" class="newsSection ig-msec ${s.theme ? toneCls(s.theme) : ""}"${i ? " hidden" : ""}>
      ${i ? `<div class="ig-msecHead"><div class="ig-kicker">${esc(s.kicker)}</div>
        <h2>${esc(s.title)}</h2><p class="mastStand">${esc(s.dek)}</p></div>` : ""}
      ${s.blocks.map(b => (R[b.type] || (() => ""))(b, doc)).join("")}
    </section>`).join("");
  wireTimeline(host);
}

function initSectionNav(doc) {
  const nav = document.querySelector("#sectionNav");
  nav.innerHTML = doc.sections.map(s =>
    `<button class="tabBtn secBtn" data-sec="${esc(s.id)}">${esc(s.nav)}</button>`).join("");
  const show = key => {
    doc.sections.forEach(s => { document.querySelector(`#sec-${s.id}`).hidden = s.id !== key; });
    nav.querySelectorAll(".secBtn").forEach(b => b.classList.toggle("active", b.dataset.sec === key));
  };
  nav.querySelectorAll(".secBtn").forEach(b => b.addEventListener("click", () => {
    show(b.dataset.sec);
    nav.scrollIntoView({ block: "nearest" });
  }));
  const want = new URLSearchParams(location.search).get("s");
  show(doc.sections.some(s => s.id === want) ? want : doc.sections[0].id);
}

function renderFooter(doc) {
  const g = doc.generated;
  const k = g.claimKinds;
  document.querySelector("#footer").innerHTML = `
    <div class="card">
      <h3>Scope, grounding and limits</h3>
      <div class="pbGrid">${["scope", "grounding", "limits"].map(x =>
        `<div class="pbRow"><span class="pbKey">${x[0].toUpperCase() + x.slice(1)}</span>
           <span>${esc(doc.method[x])}</span></div>`).join("")}</div>
      <p class="note" style="margin-top:10px">On this page: ${k.reported} reported, ${k.analysis}
        analysis, ${k.ours} our-read, ${k.scenario} scenario and ${k.market} market-implied items. Every
        reported, analysis and market-implied item names its outlet and date; the build fails on one
        that does not.</p>
    </div>
    <p>${esc(doc.authoringNote)}</p>
    <p>${esc(doc.upstreamNote)}</p>
    <p class="src">Window ${esc(doc.window.from)} to ${esc(doc.window.to)} ·
      content <code>${esc(doc.contentFile)}</code> · counts from <code>${esc(g.censusFile)}</code>
      (generated ${esc(g.censusGeneratedAt || "—")}) · build ${esc(doc.version)}.</p>`;
}

export async function initMonthly() {
  await initNav("monthly");
  const idx = await loadIndex();
  const page = (idx.pages || {}).monthly;
  if (!page) {
    throw new Error("monthly is not registered in index.json — run python scripts/build_all.py");
  }
  const r = await fetch(`../data/${page.dir}/${page.file}?v=${page.version}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} loading the monthly payload`);
  const doc = await r.json();
  THEMES = doc.themes || {};

  renderMasthead(doc);
  renderSections(doc);
  initSectionNav(doc);
  renderFooter(doc);
}
