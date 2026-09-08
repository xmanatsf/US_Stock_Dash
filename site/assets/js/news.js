/* News Intelligence page.
 *
 * Like fab5, this page renders CLAIMS rather than measurements -- but it draws a second line the
 * stock tabs do not need, and that line is the whole design:
 *
 *   - AUTHORED prose carries a CITATION. Every analytical sentence that rests on an article links
 *     to that article, resolved at build time against the source audit. A `{{cite:Key}}` that
 *     matched zero or two articles failed the build, so a link here cannot be quietly wrong.
 *   - GENERATED counts carry no citation, because they are arithmetic over the audit file: the
 *     article index, the coverage map, the KPI tiles and the signal-board tallies.
 *
 * A count is never dressed up as a judgement, and a judgement always carries its source.
 */

import { loadIndex } from "./data-client.js";
import { initNav } from "./tabs.js";

const ST_CLASS = { ok: "ig-ok", bad: "ig-bad", warn: "ig-warn", new: "ig-new" };
const GRADE_LABEL = { a: "official", b: "on-record", c: "relayed", d: "single-outlet" };

const esc = s => String(s ?? "").replace(/[&<>"]/g,
  c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/* Escape FIRST, then swap the citation tokens for links. Doing it in this order means authored
 * prose can never inject markup while the citations still render as anchors. */
let CITES = {};
function rich(s) {
  return esc(s).replace(/\{\{cite:([^}]+)\}\}/g, (_, key) => citeLink(key.trim()));
}
function citeLink(key) {
  const c = CITES[key];
  if (!c) return "";
  return `<a class="cite" href="${esc(c.url)}" target="_blank" rel="noopener"
    title="${esc(c.title)}">${esc(c.publication)}&nbsp;·&nbsp;${esc(c.date.slice(5))}</a>`;
}
function citeList(keys) {
  return (keys || []).map(citeLink).join("");
}
function gradeChip(g) {
  return g ? `<span class="chip small grade-${esc(g)}" title="Evidence grade ${esc(g)} — ${
    esc(GRADE_LABEL[g] || "")}">${esc(g)}</span>` : "";
}
const paras = arr => (arr || []).map(p => `<p>${rich(p)}</p>`).join("");

/* ------------------------------------------------------------------ masthead + infographic */

function renderMasthead(doc) {
  const g = doc.generated;
  const m = doc.masthead;
  document.querySelector("#tabTitle").textContent = doc.title;
  document.querySelector("#tabMeta").textContent =
    `${m.dates} · ${g.counts.articles} article entries · ${g.counts.files} briefs · ` +
    `${g.publications.join(", ")} · ${Object.keys(doc.citeMap).length} citations resolved`;

  document.querySelector("#masthead").innerHTML = `
    <div class="card mast">
      <div class="ig-kicker">${esc(m.kicker)} · ${esc(m.dates)}</div>
      <h2 class="mastHead">${esc(m.headline)}</h2>
      <p class="mastStand">${rich(m.standfirst)}</p>
    </div>`;
}

function renderInfographic(doc) {
  const g = doc.generated;
  const host = document.querySelector("#infographic");
  const band = (kicker, title, body) =>
    `<section class="ig-band"><div class="ig-kicker">${esc(kicker)}</div>
       <h3 class="ig-title">${esc(title)}</h3>${body}</section>`;

  // 1 -- The narratives. Authored and cited, because article counts measure coverage VOLUME,
  // which is not the same thing as which narrative mattered. This is the row to stop at.
  const n = doc.narratives;
  const narratives = band("The week in one line", n.thesis, `
    ${/* The counter is the row's first grid cell, so everything else has to sit in one wrapper
          -- otherwise the title, the line and the chips land in alternating columns. */ ""}
    <ol class="ig-reads">${n.reads.map(r => `
      <li><div><b>${esc(r.title)}</b> <span>${rich(r.line)}</span>
        <span class="chipRow">${citeList(r.cites)}</span></div></li>`).join("")}</ol>`);

  // 2 -- KPI tiles. Generated from the audit's own counts.
  const kpis = band("The archive", "What this window is made of", `
    <div class="ig-kpis">${g.kpis.map(k => `
      <div class="ig-kpi"><b>${k.n === null || k.n === undefined ? "—" : k.n}</b>
        <span>${esc(k.label)}</span></div>`).join("")}</div>`);

  // 3 -- Coverage map. Generated. A missing prior window renders as "no prior window", never as
  // a zero, which a reader would correctly read as a collapse to nothing.
  const max = Math.max(...g.coverage.map(c => c.n), 1);
  const arrow = c => {
    if (c.prior === null || c.prior === undefined) {
      return `<span class="ig-mom none" title="No prior-window audit file is present, so there is
        nothing to compare against">no prior window</span>`;
    }
    const d = c.delta;
    const cls = d > 0 ? "up" : d < 0 ? "down" : "flat";
    const glyph = d > 0 ? "▲" : d < 0 ? "▼" : "▬";
    return `<span class="ig-mom ${cls}">${glyph} ${d > 0 ? "+" : ""}${d} vs prior</span>`;
  };
  const coverage = band("Coverage map", "Which theme the week actually covered", `
    <div class="ig-cov">${g.coverage.map(c => `
      <div class="ig-covRow">
        <span class="ig-covName"><b>${esc(c.theme)}</b><i>${c.n} ${
          c.n === 1 ? "entry" : "entries"}</i></span>
        <span class="ig-covBar" style="width:${(c.n / max * 100).toFixed(1)}%">${
          g.publications.map((p, i) => {
            const v = c.byPublication[p] || 0;
            if (!v) return "";
            return `<span class="ig-seg s${i + 1}" style="width:${(v / c.n * 100).toFixed(1)}%"
              title="${esc(c.theme)} — ${esc(p)}: ${v}"></span>`;
          }).join("")}</span>
        ${arrow(c)}
      </div>`).join("")}</div>
    <div class="ig-legend">${g.publications.map((p, i) =>
      `<span class="ig-legItem"><i class="s${i + 1}"></i>${esc(p)}</span>`).join("")}</div>
    <p class="note">${rich(doc.coverageNote)}</p>
    ${coverageTable(doc)}`);

  // 4 -- Cross-theme relationships: the matrix is generated, the links between themes are
  // authored and each one carries the article that establishes it.
  const relationships = band("Cross-theme relationships", "How the week's themes connect", `
    <div class="ig-two">
      <div>
        <div class="ig-subhead">Theme × publication</div>
        ${themeMatrix(doc)}
      </div>
      <div>
        <div class="ig-subhead">Theme to theme · authored, each with its source</div>
        <ul class="ig-links">${doc.themeLinks.map(t => `
          <li><span class="ig-linkPair">${esc(t.from)} <i>→</i> ${esc(t.to)}</span>
            <span>${rich(t.line)}</span>
            <span class="chipRow">${citeList(t.cites)}</span></li>`).join("")}</ul>
      </div>
    </div>`);

  // 5 -- Momentum. Generated off the signal board's own statuses.
  const momentum = band("Momentum", "How the signal board moved this week", `
    <div class="ig-counts">${Object.entries(g.signalCounts).filter(([, v]) => v).map(([k, v]) =>
      `<span class="ig-count ${ST_CLASS[k] || ""}"><b>${v}</b>${
        esc(g.signalLabels[k] || k)}</span>`).join("")}</div>
    <p class="note">${esc(doc.signalsNote)}</p>`);

  host.innerHTML = `<div class="ig-wrap">${narratives}${kpis}${coverage}${relationships}${momentum}
    <p class="note ig-foot">The narrative band and the theme-to-theme links are authored, and each
      carries the article that establishes it. The tiles, the coverage bars and the momentum chips
      are generated from <code>${esc(doc.auditFile)}</code> and carry no citation, because they are
      arithmetic over the archive rather than a reading of it.</p></div>`;
}

function coverageTable(doc) {
  const g = doc.generated;
  const total = p => g.articles.filter(a => a.publication === p).length;
  return `<details class="ig-det"><summary>Table view</summary>
    <div class="tblWrap"><table class="tbl">
      <thead><tr><th>Primary theme</th>${g.publications.map(p =>
        `<th class="num">${esc(p)}</th>`).join("")}<th class="num">Total</th></tr></thead>
      <tbody>${g.coverage.map(c => `
        <tr><td>${esc(c.theme)}</td>${g.publications.map(p =>
          `<td class="num">${c.byPublication[p] || 0}</td>`).join("")}
          <td class="num"><b>${c.n}</b></td></tr>`).join("")}
        <tr><td><b>All themes</b></td>${g.publications.map(p =>
          `<td class="num"><b>${total(p)}</b></td>`).join("")}
          <td class="num"><b>${g.counts.articles}</b></td></tr>
      </tbody>
    </table></div></details>`;
}

function themeMatrix(doc) {
  const g = doc.generated;
  return `<div class="tblWrap"><table class="tbl">
    <thead><tr><th>Theme</th>${g.publications.map(p =>
      `<th class="num">${esc(p)}</th>`).join("")}</tr></thead>
    <tbody>${g.coverage.map(c => `
      <tr><td>${esc(c.theme)}</td>${g.publications.map(p => {
        const v = c.byPublication[p] || 0;
        return `<td class="num ${v === 0 ? "zero" : ""}">${v}</td>`;
      }).join("")}</tr>`).join("")}</tbody>
  </table></div>`;
}

/* ------------------------------------------------------------------ the six sections */

function renderInsights(doc) {
  document.querySelector("#sec-insights").innerHTML = `
    <h2>The four-layer read</h2>
    <p class="note">Where the argument actually sits. Every claim that rests on an article carries
      a link to it.</p>
    <div class="ig-themes">${doc.layers.map(l => `
      <div class="ig-theme">
        <div class="ig-themeN">Layer ${l.n}</div>
        <b>${esc(l.title)}</b>
        ${paras(l.paras)}
      </div>`).join("")}</div>

    ${figureHtml(doc)}

    <h2>Eight reads — what the prior week expected, against what this week established</h2>
    <p class="note">${rich(doc.readsNote)}</p>
    <div class="readGrid">${doc.reads.map(r => `
      <div class="card read">
        <div class="readN">${esc(r.n)}</div>
        <h3>${esc(r.title)}</h3>
        <p>${rich(r.claim)}</p>
        <div class="readSplit">
          <div><span class="evLbl">The prior week predicted</span><p class="note">${
            rich(r.predicted)}</p></div>
          <div><span class="evLbl">What ${esc(r.verdict === "contradicted" ? "happened instead"
              : r.verdict === "established" ? "established it" : "proved it")}</span>
            <p class="note">${rich(r.outcome)}</p></div>
        </div>
        <div class="chipRow">${(r.houses || []).map(h =>
          `<span class="chip small src">${esc(h)}</span>`).join("")}</div>
      </div>`).join("")}</div>`;
}

function figureHtml(doc) {
  const f = doc.figure;
  if (!f) return "";
  const max = Math.max(...f.points.map(p => p.pct), 75);
  return `
    <h2>${esc(f.title)}</h2>
    <p class="note">${esc(f.kicker)}</p>
    <div class="card">
      <div class="oddsArc">${f.points.map(p => `
        <div class="oddsCol">
          <div class="oddsBarWrap"><div class="oddsBar" style="height:${
            (p.pct / max * 100).toFixed(1)}%"><span>${esc(p.label)}</span></div></div>
          <div class="oddsWhen"><b>${esc(p.when)}</b><i>${esc(p.sub)}</i></div>
        </div>`).join("")}</div>
      <p class="note">${rich(f.note)}</p>
      <details class="ig-det"><summary>Table view</summary>
        <div class="tblWrap"><table class="tbl">
          <thead><tr><th>Date</th><th>Reported odds</th><th>Driver</th><th>Source</th></tr></thead>
          <tbody>${f.points.map(p => `
            <tr><td>${esc(p.when)}</td><td class="num">${esc(p.label)}</td>
              <td>${esc(p.driver)}</td><td>${esc(p.source)}</td></tr>`).join("")}</tbody>
        </table></div>
      </details>
    </div>`;
}

function renderTimeline(doc) {
  document.querySelector("#sec-timeline").innerHTML = `
    <h2>How the week actually moved</h2>
    <p class="note">${doc.timeline.length} movements · ${rich(doc.timelineNote)}</p>
    <ol class="tline">${doc.timeline.map(t => `
      <li class="${t.big ? "big" : ""}">
        <div class="tlWhen"><b>${esc(t.when)}</b>${t.sub ? `<i>${esc(t.sub)}</i>` : ""}</div>
        <div class="tlBody">
          <h3>${esc(t.title)}</h3>
          ${paras(t.paras)}
          <div class="chipRow">${citeList(t.cites)}${t.attribution
            ? `<span class="chip small src">${esc(t.attribution)}</span>` : ""}</div>
        </div>
      </li>`).join("")}</ol>`;
}

function renderConflicts(doc) {
  document.querySelector("#sec-conflicts").innerHTML = `
    <h2>Where all ${doc.generated.publications.length} houses agree</h2>
    <p class="note">${doc.agreement.length} points · no publication dissents</p>
    <div class="agreeGrid">${doc.agreement.map(a => `
      <div class="card conv">
        <div class="agreeN">${a.n}</div>
        <b>${esc(a.claim)}</b>
        <p class="note">${rich(a.detail)}</p>
      </div>`).join("")}</div>

    <h2>Conflict registry</h2>
    <p class="note">${doc.conflicts.length} disagreements · ${rich(doc.conflictsNote)}</p>
    <div class="cfGrid">${doc.conflicts.map(c => `
      <div class="card disp">
        <div class="cfHead">
          <b>${c.n}. ${esc(c.claim)}</b>
          <span class="chip small ig-status">${esc(c.statusLabel || c.status)}</span>
        </div>
        ${(c.sides || []).length ? `<div class="ig-sides">${c.sides.map(s =>
          `<span class="ig-side"><b>${esc(s.house)}</b> ${esc(s.position)}</span>`).join("")}</div>`
          : ""}
        <p>${rich(c.body)}</p>
        <p class="note"><span class="evLbl">The honest adjudication</span> ${
          rich(c.adjudication)}</p>
      </div>`).join("")}</div>
    ${doc.conflictsAlsoCarried ? `
      <div class="card"><h3>Also carried, unresolved</h3>
        <p class="note">${rich(doc.conflictsAlsoCarried)}</p></div>` : ""}`;
}

function renderSignals(doc) {
  const host = document.querySelector("#sec-signals");
  const g = doc.generated;

  const draw = (filter) => {
    const rows = doc.signals.filter(s => filter === "all" || s.status === filter);
    host.querySelector("#sigBody").innerHTML = rows.map(s => `
      <tr>
        <td class="num">${s.n}</td>
        <td><b>${esc(s.indicator)}</b>
          <div class="ckStatus ${ST_CLASS[s.status]}">${esc(g.signalLabels[s.status])}</div></td>
        <td class="ckBase">${rich(s.reading)}</td>
        <td class="ckBull">${rich(s.bull)}</td>
        <td class="ckBear">${rich(s.bear)}</td>
        <td class="ckWhen">${rich(s.next)}</td>
      </tr>`).join("");
    host.querySelectorAll(".sigFilter").forEach(b =>
      b.classList.toggle("active", b.dataset.st === filter));
  };

  host.innerHTML = `
    <h2>Signal board</h2>
    <p class="note">${doc.signals.length} indicators · every trigger traceable to a brief.
      ${esc(doc.signalsNote)}</p>
    <div class="ctlRow">
      <label>Status</label>
      <button class="hBtn sigFilter" data-st="all">All <span class="cnt">${
        doc.signals.length}</span></button>
      ${Object.entries(g.signalCounts).filter(([, v]) => v).map(([k, v]) => `
        <button class="hBtn sigFilter" data-st="${k}">${esc(g.signalLabels[k])}
          <span class="cnt">${v}</span></button>`).join("")}
    </div>
    <div class="tblWrap">
      <table class="tbl ckTbl">
        <thead><tr><th>#</th><th>Indicator</th><th>Reading &amp; supporting data</th>
          <th>Bullish trigger</th><th>Bearish trigger</th><th>Next checkpoint</th></tr></thead>
        <tbody id="sigBody"></tbody>
      </table>
    </div>`;
  host.querySelectorAll(".sigFilter").forEach(b =>
    b.addEventListener("click", () => draw(b.dataset.st)));
  draw("all");
}

function renderAction(doc) {
  const a = doc.action;
  const b = doc.bearCase;
  document.querySelector("#sec-action").innerHTML = `
    <h2>The reading — one stance, three instructions</h2>
    <div class="callout" style="--accent:var(--s1)">
      <div class="calloutHead"><b style="font-size:15px">${esc(a.headline)}</b></div>
      ${paras(a.body)}
    </div>
    <div class="grid3">${a.instructions.map(i => `
      <div class="card instr">
        <div class="instrN">${i.n}</div>
        <h3>${esc(i.title)}</h3>
        <p class="note">${rich(i.body)}</p>
      </div>`).join("")}</div>
    <div class="card ig-not">
      <h3>What is not being recommended</h3>
      <p class="note">${rich(a.notRecommended)}</p>
    </div>
    <p class="note disclaimer">${esc(a.disclaimer)}</p>

    <h2>Near-term outlook — to the September meeting</h2>
    <div class="ig-scens">${doc.scenarios.map(s => `
      <div class="ig-scen">
        <div class="ig-scenHead"><b>${esc(s.name)}</b>
          <span class="ig-pct">${s.pct}%${s.editorial
            ? '<i class="edLbl">editorial</i>' : ""}</span></div>
        <div class="ig-bar"><span style="width:${s.pct}%"></span></div>
        <p class="note">${rich(s.body)}</p>
        <p class="note"><span class="evLbl">Named trigger</span> ${rich(s.trigger)}</p>
      </div>`).join("")}</div>

    <h2>The bear case — what breaks this reading</h2>
    <div class="callout ig-bear" style="--accent:var(--critical)">
      <div class="calloutHead"><b style="font-size:15px">${esc(b.headline)}</b></div>
      ${paras(b.body)}
    </div>
    <div class="card">
      <h3>What would change the reading</h3>
      <ol class="hier">${b.wouldChange.map(x => `<li>${rich(x)}</li>`).join("")}</ol>
    </div>

    <h2>The calendar that decides it</h2>
    <ol class="ig-cal">${doc.calendar.map(c => `
      <li>
        <div class="ig-calDate">${esc(c.date)}<span>${esc(c.when || "")}</span></div>
        <div><p class="note" style="margin:0">${rich(c.body)}</p></div>
      </li>`).join("")}</ol>`;
}

/* The article index is generated in full. 108 rows are never hand-typed -- that is the point of
 * the audit file, and it is what lets the filters below be trusted. */
function renderIndex(doc) {
  const host = document.querySelector("#sec-index");
  const g = doc.generated;

  const rows = g.articles.map(a => `
    <tr data-pub="${esc(a.publication)}" data-theme="${esc(a.theme)}">
      <td class="num">${esc(a.id)}</td>
      <td>${esc(a.date.slice(5))}</td>
      <td>${esc(a.publication)}</td>
      <td>${esc(a.theme)}</td>
      <td><a href="${esc(a.url)}" target="_blank" rel="noopener">${esc(a.title)}</a></td>
    </tr>`).join("");

  const chip = (k, v, label, n) =>
    `<button class="hBtn ixFilter" data-k="${k}" data-v="${esc(v)}">${esc(label)}
      <span class="cnt">${n}</span></button>`;

  host.innerHTML = `
    <h2>Article index</h2>
    <p class="note">All ${g.counts.articles} entries · filter by publication or theme. Every
      article heading carrying a URL across the ${g.counts.files} selected briefs. Titles link to
      the original article. Filters narrow this table only — the analysis, totals and coverage map
      are fixed.</p>
    <div class="ctlRow">
      ${chip("all", "", "All entries", g.counts.articles)}
      ${g.publications.map(p => chip("pub", p,
        p, g.articles.filter(a => a.publication === p).length)).join("")}
      ${g.themes.map(t => chip("theme", t,
        t, g.articles.filter(a => a.theme === t).length)).join("")}
    </div>
    <p class="note">Showing <b id="ixcount">${g.counts.articles}</b> of
      ${g.counts.articles} entries. Each entry carries one editorial primary theme; repeated
      coverage is retained.</p>
    <div class="tblWrap">
      <table class="tbl ixTbl">
        <thead><tr><th>#</th><th>Brief date</th><th>Publication</th><th>Primary theme</th>
          <th>Article</th></tr></thead>
        <tbody id="ixBody">${rows}</tbody>
      </table>
    </div>

    <h2>Sources</h2>
    <p class="note">${g.counts.files} briefs across ${g.counts.days} dates. The brief filenames are
      the local Markdown in <code>Cowork Playground/WSJ/</code>, which owns them.</p>
    <div class="tblWrap">
      <table class="tbl">
        <thead><tr><th>Brief</th><th class="num">n</th><th>Notes</th></tr></thead>
        <tbody>${Object.entries(g.byFile).map(([f, n]) => {
          const date = (f.match(/2026-\d\d-\d\d/) || [""])[0];
          return `<tr><td><code>${esc(f)}</code></td><td class="num">${n}</td>
            <td class="note">${esc((doc.briefNotes || {})[date] || "")}</td></tr>`;
        }).join("")}
        <tr><td><b>Total</b></td><td class="num"><b>${g.counts.articles}</b></td>
          <td class="note"><b>No briefs exist for 1–3 September.</b></td></tr></tbody>
      </table>
    </div>
    ${(g.auditNotes || []).length ? `
      <div class="card"><h3>How the archive was counted</h3>
        <ul class="hier">${g.auditNotes.map(n => `<li>${esc(n)}</li>`).join("")}</ul></div>` : ""}`;

  const body = host.querySelector("#ixBody");
  const out = host.querySelector("#ixcount");
  host.querySelectorAll(".ixFilter").forEach(b => b.addEventListener("click", () => {
    const { k, v } = b.dataset;
    let n = 0;
    body.querySelectorAll("tr").forEach(tr => {
      const hit = k === "all" || tr.dataset[k === "pub" ? "pub" : "theme"] === v;
      tr.hidden = !hit;
      if (hit) n++;
    });
    out.textContent = n;
    host.querySelectorAll(".ixFilter").forEach(o => o.classList.toggle("active", o === b));
  }));
  host.querySelector(".ixFilter").classList.add("active");
}

function renderFooter(doc) {
  const e = doc.evidence;
  document.querySelector("#footer").innerHTML = `
    <div class="card">
      <h3>How to read this page</h3>
      <p class="note">Authored prose carries a <b>citation</b> — a link to the article it rests
        on, resolved at build time against the source audit. Generated content carries none,
        because it is arithmetic over the archive: the article index, the coverage map, the tiles
        and the signal-board tallies. A citation key that matched zero articles, or more than one,
        failed the build rather than rendering.</p>
      <div class="pbGrid">
        ${["a", "b", "c", "d"].map(k =>
          `<div class="pbRow"><span class="pbKey">${gradeChip(k)} ${esc(GRADE_LABEL[k])}</span>
             <span>${esc(e[k])}</span></div>`).join("")}
      </div>
      <p class="note" style="margin-top:10px">${esc(e.note)}</p>
    </div>
    ${(doc.perimeters || []).length ? `
      <details class="card ig-det"><summary><b>Figures quoted at multiple perimeters</b> — scope
        and timing, not disagreement</summary>
        <div class="pbGrid">${doc.perimeters.map(p =>
          `<div class="pbRow"><span class="pbKey">${esc(p.figure)}</span>
             <span>${esc(p.range)}</span></div>`).join("")}</div>
      </details>` : ""}
    ${(doc.gaps || []).length ? `
      <details class="card ig-det"><summary><b>Known gaps and flags</b> — ${doc.gaps.length} open,
        carried rather than resolved</summary>
        <ul class="hier">${doc.gaps.map(g => `<li>${esc(g)}</li>`).join("")}</ul>
      </details>` : ""}
    <p>${esc(doc.authoringNote)}</p>
    <p>${esc(doc.upstreamNote)}</p>
    <p class="src">Window ${esc(doc.windowFrom)} to ${esc(doc.windowTo)} ·
      content <code>${esc(doc.contentFile)}</code> ·
      counts and links from <code>${esc(doc.auditFile)}</code>
      (generated ${esc(doc.generated.auditGeneratedAt || "—")}) ·
      build ${esc(doc.version)}.</p>`;
}

/* ------------------------------------------------------------------ section nav */

const SECTIONS = [
  ["insights", "Key insights", d => d.reads.length],
  ["timeline", "Timeline", d => d.timeline.length],
  ["conflicts", "Conflicts", d => d.conflicts.length],
  ["signals", "Signals", d => d.signals.length],
  ["action", "Action", () => null],
  ["index", "Index", d => d.generated.counts.articles],
];

function initSectionNav(doc) {
  const nav = document.querySelector("#sectionNav");
  nav.innerHTML = SECTIONS.map(([k, label, count]) => {
    const n = count(doc);
    return `<button class="tabBtn secBtn" data-sec="${k}">${esc(label)}${
      n === null ? "" : ` <span class="cnt">${n}</span>`}</button>`;
  }).join("");

  const show = (key) => {
    SECTIONS.forEach(([k]) => {
      document.querySelector(`#sec-${k}`).hidden = k !== key;
    });
    nav.querySelectorAll(".secBtn").forEach(b =>
      b.classList.toggle("active", b.dataset.sec === key));
    // The infographic stays put; only the section below it changes.
    document.querySelector("#sectionNav").scrollIntoView({ block: "nearest" });
  };

  nav.querySelectorAll(".secBtn").forEach(b =>
    b.addEventListener("click", () => show(b.dataset.sec)));
  show(new URLSearchParams(location.search).get("s") || "insights");
}

export async function initNews() {
  await initNav("news");
  const idx = await loadIndex();
  const page = (idx.pages || {}).news;
  if (!page) {
    throw new Error("news is not registered in index.json — run python scripts/build_all.py");
  }
  const r = await fetch(`../data/${page.dir}/${page.file}?v=${page.version}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} loading the news payload`);
  const doc = await r.json();

  CITES = doc.citeMap || {};

  renderMasthead(doc);
  renderInfographic(doc);
  renderInsights(doc);
  renderTimeline(doc);
  renderConflicts(doc);
  renderSignals(doc);
  renderAction(doc);
  renderIndex(doc);
  renderFooter(doc);
  initSectionNav(doc);
}
