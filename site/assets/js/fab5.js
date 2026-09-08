/* Fab5 cross-source page.
 *
 * Every other tab renders measurements. This one renders CLAIMS, and the whole design follows
 * from that one difference:
 *
 *   - A claim wears a chip carrying its SOURCE and its EVIDENCE GRADE. That is what the chip
 *     means here -- not "this passed a test", but "this is who said it and how well it is
 *     evidenced". The claim text itself stays plain prose.
 *   - The only measured content on the page is the live technical strip on each ticker, and it is
 *     read verbatim out of the same pipeline payload the four dashboard tabs render. Nothing is
 *     computed client-side, so this page cannot disagree with them.
 *
 * The existing "How to read this" contract is extended, not replaced.
 */

import { loadIndex } from "./data-client.js";
import { initNav } from "./tabs.js";
import { REGIME_COLORS } from "./regimes.js";

const GRADE_LABEL = { a: "primary", b: "modeled", c: "channel", d: "social" };
const DIR_LABEL = { bull: "constructive", bear: "cautionary", neutral: "two-sided" };

/* Signal-board buckets. The label under each is the page's own grouping of the source's verbatim
 * status word, which is rendered beside it -- so the filter is usable without the bucket ever
 * being mistaken for something the research house said. */
const CK_STATUS = {
  ok:   { label: "confirmed",   cls: "ig-ok" },
  warn: { label: "in motion",   cls: "ig-warn" },
  bad:  { label: "moved against", cls: "ig-bad" },
  new:  { label: "new this run", cls: "ig-new" },
};
const VERDICT = {
  confirmed:    { label: "confirmed",  cls: "ig-ok" },
  contradicted: { label: "contradicted", cls: "ig-bad" },
  unresolved:   { label: "unresolved", cls: "ig-warn" },
  new:          { label: "new",        cls: "ig-new" },
};

const esc = s => String(s ?? "").replace(/[&<>"]/g,
  c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const num = (v, d = 1, suf = "") =>
  v === null || v === undefined ? "—" : `${v.toFixed(d)}${suf}`;
const signed = (v, d = 1, suf = "%") =>
  v === null || v === undefined ? "—" : `${v > 0 ? "+" : ""}${v.toFixed(d)}${suf}`;

function gradeChip(g) {
  return `<span class="chip small grade-${esc(g)}" title="Evidence grade ${esc(g)} — ${
    esc(GRADE_LABEL[g] || "")}">${esc(g)}</span>`;
}
function sourceChips(sources) {
  return (sources || []).map(s => `<span class="chip small src">${esc(s)}</span>`).join("");
}
function dirTag(d) {
  return `<span class="dirTag dir-${esc(d)}">${esc(DIR_LABEL[d] || d)}</span>`;
}

/* A ticker reference only becomes a link when the build actually joined it to a universe. An
 * unjoined name renders as plain text -- a dead link would imply data we do not have. */
function tickerRefs(tickers, byTicker) {
  if (!tickers || !tickers.length) return "";
  return `<div class="tkRefs">${tickers.map(t => {
    const imp = byTicker[t];
    if (imp && imp.live) {
      return `<a class="tkRef" href="#imp-${esc(t)}">${esc(t)}</a>`;
    }
    return `<span class="tkRef ext" title="${
      esc((imp && imp.externalReason) || "no price data in this build")}">${esc(t)}</span>`;
  }).join("")}</div>`;
}

function renderHeader(doc) {
  document.querySelector("#tabTitle").textContent = doc.title;
  // The run counts reports, not batches, and the two are different numbers for the same window
  // (Run 6: 51 reports across 7 houses). Printing one as "sources" invites the wrong one being
  // quoted, so both the count and its unit come from the content file rather than from here.
  const scale = doc.reportCount
    ? `${doc.reportCount} reports across ${doc.sources.length} houses`
    : `${doc.sources.length} houses`;
  document.querySelector("#tabMeta").textContent =
    `${doc.runLabel ? doc.runLabel + " · " : ""}${scale}` +
    `${doc.windowLabel ? " · " + doc.windowLabel : ""} · ` +
    `prior baseline ${doc.priorBaseline} · technicals as of ${doc.universeAsOf.join(", ")}`;

  document.querySelector("#focus").innerHTML = `
    <div class="card">
      <h3>Focus question carried in from the ${esc(doc.priorBaseline)} baseline</h3>
      <p class="note" style="margin-bottom:10px">${esc(doc.focusQuestion)}</p>
      <div class="srcRow">${doc.sources.map(s =>
        `<span class="srcPill"><b>${esc(s.house)}</b> ${esc(s.detail)}</span>`).join("")}</div>
    </div>`;
}

/* The top-of-page infographic.
 *
 * Six bands, one per category the page has to summarise, and every one of them reads an array
 * that already exists in the payload -- the infographic adds no facts of its own. Two kinds of
 * figure appear here and they are kept visually distinct on purpose:
 *
 *   - GENERATED counts (the signal-board buckets, the prior-run verdicts, the direction split)
 *     come from `doc.infographic`, which build_fab5.py computes. They carry no source chip
 *     because they are arithmetic over this page's own content.
 *   - AUTHORED figures (the stat tiles, the scenarios, the calendar) carry their source chips and
 *     evidence grade, exactly as every other claim on the page does. The build fails on one that
 *     carries neither.
 */
function renderInfographic(doc) {
  const host = document.querySelector("#infographic");
  if (!host || doc.schemaVersion < 2) return;
  const ig = doc.infographic || {};
  const wc = doc.whatChanged || {};

  const band = (kicker, title, body) =>
    `<section class="ig-band"><div class="ig-kicker">${esc(kicker)}</div>
       <h3 class="ig-title">${esc(title)}</h3>${body}</section>`;

  // 1 -- Key themes. The four-layer summaries are already authored but are click-gated behind
  // #layerNote further down the page, so this is the one place they are visible on arrival.
  const themes = band("The four-layer read", "Where the argument actually sits", `
    <div class="ig-themes">${doc.layers.map(l => `
      <div class="ig-theme">
        <div class="ig-themeN">Layer ${l.n}</div>
        <b>${esc(l.title)}</b>
        <p class="note">${esc(l.summary)}</p>
      </div>`).join("")}</div>`);

  // 2 -- KPI tiles. Authored, so every one carries its sources and grade.
  const kpis = band("The numbers that moved", "What this run put on the table", `
    <div class="ig-stats">${doc.stats.map(s => `
      <div class="ig-stat">
        <div class="ig-statKicker">${esc(s.kicker)}</div>
        <div class="ig-statNum">${esc(s.num)}</div>
        <p class="note">${esc(s.lab)}</p>
        <div class="chipRow">${sourceChips(s.sources)}${gradeChip(s.grade)}</div>
      </div>`).join("")}</div>`);

  // 3 -- Major company developments: the named-scope implications, with the dated catalysts
  // beside them. Both are authored; the count in the kicker is generated.
  const named = doc.implications.filter(i => i.scope === "name");
  const devs = band(
    `${named.length} named developments · ${doc.calendar.length} dated catalysts`,
    "Major company developments and what decides them", `
    <div class="ig-two">
      <div>
        <div class="ig-subhead">Names carrying a development this run</div>
        <div class="ig-tkGrid">${named.map(i => `
          <a class="ig-tk dir-edge-${esc(i.direction)}" href="#imp-${esc(i.ticker)}"
             title="${esc(i.line.slice(0, 180))}">
            <b>${esc(i.ticker)}</b>${gradeChip(i.grade)}
          </a>`).join("")}</div>
        <p class="note">Direction is the edge colour; the grade chip is the evidence behind the
          claim, not a rating. Follow a ticker for the full line and its live technical strip.</p>
      </div>
      <div>
        <div class="ig-subhead">The calendar that decides it</div>
        <ol class="ig-cal">${doc.calendar.map(c => `
          <li>
            <div class="ig-calDate">${esc(c.date)}<span>${esc(c.when || "")}</span></div>
            <div><p class="note" style="margin:0 0 4px">${esc(c.body)}</p>
              <div class="chipRow">${sourceChips(c.sources)}${gradeChip(c.grade)}</div></div>
          </li>`).join("")}</ol>
      </div>
    </div>`);

  // 4 -- Competitive dynamics: who is on which side, which is what schemaVersion 2's
  // house-attributed dispute sides exist to make renderable.
  const dyn = band(
    `${doc.disputes.length} live disagreements · ${doc.agreement.length} points of agreement`,
    "Who is on which side", `
    <div class="ig-two">
      <div>
        <div class="ig-subhead">Disagreement, by house</div>
        ${doc.disputes.map(d => `
          <div class="ig-disp">
            <b>${d.n ? d.n + ". " : ""}${esc(d.claim)}</b>
            <span class="chip small ig-status">${esc(d.statusLabel || d.status || "")}</span>
            <div class="ig-sides">${d.sides.map(s => `
              <span class="ig-side"><b>${esc(s.house)}</b> ${esc(s.position)}</span>`).join("")}</div>
          </div>`).join("")}
      </div>
      <div>
        <div class="ig-subhead">Where all ${doc.sources.length} houses agree</div>
        <ol class="ig-agree">${doc.agreement.map(a =>
          `<li><b>${esc(a.claim)}</b><div class="chipRow">${sourceChips(a.sources)}${
            gradeChip(a.grade)}</div></li>`).join("")}</ol>
      </div>
    </div>`);

  // 5 -- Market implications: the scenario set, probabilities as authored.
  const near = doc.scenarios.filter(s => s.horizon === "near");
  const med = doc.scenarios.filter(s => s.horizon === "medium");
  const scen = (s) => `
    <div class="ig-scen">
      <div class="ig-scenHead">
        <b>${esc(s.name)}</b>
        ${typeof s.pct === "number" ? `<span class="ig-pct">${s.pct}%</span>` : ""}
      </div>
      ${typeof s.pct === "number"
        ? `<div class="ig-bar"><span style="width:${s.pct}%"></span></div>` : ""}
      <p class="note">${esc(s.body)}</p>
      ${(s.triggers || []).length
        ? `<ul class="ig-trig">${s.triggers.map(t => `<li>${esc(t)}</li>`).join("")}</ul>` : ""}
      <div class="chipRow">${sourceChips(s.sources)}${gradeChip(s.grade)}</div>
    </div>`;
  const implications = band("Scenarios", "Market implications", `
    <div class="ig-subhead">Near term · weeks, with named triggers</div>
    <div class="ig-scens">${near.map(scen).join("")}</div>
    <div class="ig-subhead" style="margin-top:14px">Medium term · quarters</div>
    <div class="ig-scens">${med.map(scen).join("")}</div>`);

  // 6 -- Momentum. The delta banner is authored; the two count rows are generated.
  const countRow = (obj, dict) => `<div class="ig-counts">${
    Object.entries(obj || {}).filter(([, v]) => v > 0).map(([k, v]) =>
      `<span class="ig-count ${(dict[k] || {}).cls || ""}"><b>${v}</b>${
        esc((dict[k] || {}).label || k)}</span>`).join("")}</div>`;
  const momentum = band(`What changed since ${esc(wc.priorBaseline || doc.priorBaseline)}`,
    esc(wc.headline || "What changed"), `
    <p>${esc(wc.body || "")}</p>
    <div class="ig-subhead">Signal board · ${ig.checklistTotal || doc.checklist.length} indicators
      <span class="note" style="display:inline">(${ig.addendumCount || 0} revisited in the
      addendum)</span></div>
    ${countRow(ig.checklistCounts, CK_STATUS)}
    <div class="ig-subhead">The nine reads, against what the prior run predicted</div>
    ${countRow(ig.verdictCounts, VERDICT)}
    <details class="ig-det"><summary>The ${wc.bullets ? wc.bullets.length : 0} movements
      in date order</summary>
      <ol class="ig-moves">${(wc.bullets || []).map(b => `
        <li>
          <div class="ig-calDate">${esc(b.when)}${
            b.addendum ? "<span>addendum</span>" : ""}</div>
          <div><b>${esc(b.title)}</b><p class="note" style="margin:2px 0 4px">${esc(b.body)}</p>
            <div class="chipRow">${sourceChips(b.sources)}${gradeChip(b.grade)}</div></div>
        </li>`).join("")}</ol>
    </details>
    ${wc.stanceRefinement
      ? `<p class="ig-refine"><span class="evLbl">Refinement</span> ${esc(wc.stanceRefinement)}</p>`
      : ""}`);

  host.innerHTML = `<div class="ig-wrap">${themes}${kpis}${momentum}${dyn}${devs}${implications}
    <p class="note ig-foot">Counts on this panel — the signal-board buckets, the prior-run
      verdicts, the named-development and catalyst totals — are generated from the arrays below
      and carry no source chip, because they are arithmetic over this page's own content. Every
      other figure here is hand-authored and carries the house that said it and the grade of the
      evidence. The build fails on a figure that has neither.</p></div>`;
}

function renderCall(doc) {
  const c = doc.call;
  document.querySelector("#call").innerHTML = `
    <h2>The call</h2>
    <div class="callout" style="--accent:var(--s1)">
      <div class="calloutHead"><b style="font-size:15px">${esc(c.headline)}</b></div>
      <p style="margin:10px 0 0">${esc(c.body)}</p>
    </div>
    <div class="grid3">${c.instructions.map(i => `
      <div class="card instr">
        <div class="instrN">${i.n}</div>
        <h3>${esc(i.title)}</h3>
        <p class="note">${esc(i.body)}</p>
      </div>`).join("")}</div>
    ${c.notRecommended ? `
      <div class="card ig-not">
        <h3>What is not being recommended</h3>
        <p class="note">${esc(c.notRecommended)}</p>
      </div>` : ""}
    ${bearCaseHtml(doc)}`;
}

/* The bear case is rendered next to the call rather than in a section of its own, because a
 * recommendation shown without the thing that would break it is half an argument. */
function bearCaseHtml(doc) {
  const b = doc.bearCase;
  if (!b) return "";
  return `
    <div class="callout ig-bear" style="--accent:var(--critical)">
      <div class="calloutHead"><b style="font-size:15px">${esc(b.headline)}</b></div>
      <p style="margin:10px 0 0">${esc(b.body)}</p>
    </div>
    <div class="grid3">${(b.variants || []).map(v => `
      <div class="card">
        <h3>${esc(v.title)}</h3>
        <p class="note">${esc(v.body)}</p>
        <div class="chipRow">${sourceChips(v.sources)}${gradeChip(v.grade)}</div>
      </div>`).join("")}</div>`;
}

function renderInsights(doc, byTicker) {
  const host = document.querySelector("#insights");
  const layers = doc.layers;

  const draw = (filter) => {
    const rows = doc.insights.filter(i => filter === "all" || i.layer === filter);
    host.querySelector("#insightList").innerHTML = rows.map(i => `
      <div class="card insight dir-edge-${esc(i.direction)}">
        <div class="insHead">
          <h3>${esc(i.headline)}</h3>
          <div class="chipRow">${sourceChips(i.sources)}${gradeChip(i.grade)}${dirTag(i.direction)}</div>
        </div>
        <p class="insClaim">${esc(i.claim)}</p>
        <p class="insEvidence"><span class="evLbl">Evidence</span> ${esc(i.evidence)}</p>
        ${tickerRefs(i.tickers, byTicker)}
      </div>`).join("");
    host.querySelectorAll(".hBtn").forEach(b =>
      b.classList.toggle("active", b.dataset.layer === filter));
  };

  host.innerHTML = `
    <h2>Key insights</h2>
    <p class="note">Grouped by the synthesis's own four-layer read. Each claim carries who said it
      and how well it is evidenced; the claim itself is prose because it is a reading, not a
      measurement.</p>
    <div class="ctlRow">
      <label>Layer</label>
      <button class="hBtn" data-layer="all">all <span class="cnt">${doc.insights.length}</span></button>
      ${layers.map(l => `<button class="hBtn" data-layer="${esc(l.id)}">${esc(l.title)}
        <span class="cnt">${doc.insights.filter(i => i.layer === l.id).length}</span></button>`).join("")}
    </div>
    <div id="layerNote" class="playbook" hidden></div>
    <div id="insightList"></div>`;

  host.querySelectorAll(".hBtn").forEach(b => b.addEventListener("click", () => {
    const l = b.dataset.layer;
    const note = host.querySelector("#layerNote");
    const meta = layers.find(x => x.id === l);
    note.hidden = !meta;
    if (meta) note.innerHTML =
      `<div class="pbRow"><span class="pbKey">Layer ${meta.n}</span><span>${esc(meta.summary)}</span></div>`;
    draw(l);
  }));
  draw("all");
}

function renderAgreement(doc) {
  document.querySelector("#agreement").innerHTML = `
    <h2>Where the sources agree — and where they do not</h2>
    <p class="note">Independent corroboration is the whole point of a cross-source read, so the two
      are shown side by side rather than blended into one narrative. Every dispute names the thing
      that would settle it.</p>
    <div class="grid2">
      <div>
        <h3 class="colHead agree">Agreement · high conviction</h3>
        ${doc.agreement.map(a => `
          <div class="card conv">
            <b>${esc(a.claim)}</b>
            <p class="note">${esc(a.detail)}</p>
            <div class="chipRow">${sourceChips(a.sources)}${gradeChip(a.grade)}</div>
          </div>`).join("")}
      </div>
      <div>
        <h3 class="colHead dispute">Disagreement · unresolved</h3>
        ${doc.disputes.map(d => `
          <div class="card disp">
            <b>${d.n ? d.n + ". " : ""}${esc(d.claim)}${
              d.isNew ? ' <span class="chip small newTag">new</span>' : ""}${
              d.statusLabel ? ` <span class="chip small ig-status">${esc(d.statusLabel)}</span>` : ""}</b>
            ${/* schemaVersion 2 attributes each side to a house; v1 sides were bare strings. */ ""}
            <ul class="sides">${d.sides.map(s => typeof s === "string"
              ? `<li>${esc(s)}</li>`
              : `<li><b>${esc(s.house)}</b> — ${esc(s.position)}</li>`).join("")}</ul>
            <p class="note"><span class="evLbl">Tiebreaker</span> ${esc(d.tiebreaker)}</p>
            <div class="chipRow">${sourceChips(d.sources)}${gradeChip(d.grade)}</div>
          </div>`).join("")}
        ${doc.disputesAlsoClosed
          ? `<div class="card"><h3>Also closed this run</h3>
               <p class="note">${esc(doc.disputesAlsoClosed)}</p></div>` : ""}
      </div>
    </div>`;
}

function renderChecklist(doc) {
  const host = document.querySelector("#checklist");
  const ig = doc.infographic || {};
  const counts = ig.checklistCounts || {};
  const n = s => doc.checklist.filter(c => c.status === s).length;

  const draw = (filter) => {
    const rows = doc.checklist.filter(c => filter === "all" || c.status === filter);
    host.querySelector("#ckBody").innerHTML = rows.map(c => `
      <tr>
        <td class="num">${c.n}${c.addendum ? ' <span class="chip small newTag">add.</span>' : ""}</td>
        <td><b>${esc(c.indicator)}</b>
          ${c.statusLabel ? `<div class="ckStatus ${
            (CK_STATUS[c.status] || {}).cls || ""}">${esc(c.statusLabel)}</div>` : ""}</td>
        <td class="ckBase">${esc(c.baseline)}</td>
        <td class="ckBull">${esc(c.bull)}</td>
        <td class="ckBear">${esc(c.bear)}</td>
        <td class="ckWhen">${esc(c.checkpoint)}</td>
      </tr>`).join("");
    host.querySelectorAll(".ckFilter").forEach(b =>
      b.classList.toggle("active", b.dataset.st === filter));
  };

  host.innerHTML = `
    <h2>Signal board — every standing indicator, with both triggers</h2>
    <p class="note">${doc.checklist.length} live indicators${
      doc.indicatorNote ? ` — ${esc(doc.indicatorNote)}` : ""} The status word in each row is the
      source's own; the filter groups those words into four buckets, which is this page's grouping
      and not a research house's.</p>
    <div class="ctlRow">
      <label>Status</label>
      <button class="hBtn ckFilter" data-st="all">all <span class="cnt">${
        doc.checklist.length}</span></button>
      ${Object.entries(CK_STATUS).map(([k, v]) => `
        <button class="hBtn ckFilter" data-st="${k}">${esc(v.label)}
          <span class="cnt">${counts[k] !== undefined ? counts[k] : n(k)}</span></button>`).join("")}
    </div>
    <div class="tblWrap">
      <table class="tbl ckTbl">
        <thead><tr><th>#</th><th>Indicator</th><th>Where it stands</th>
          <th>Bullish trigger</th><th>Bearish trigger</th><th>Next checkpoint</th></tr></thead>
        <tbody id="ckBody"></tbody>
      </table>
    </div>`;
  host.querySelectorAll(".ckFilter").forEach(b =>
    b.addEventListener("click", () => draw(b.dataset.st)));
  draw("all");
}

function strip(live) {
  if (!live) return "";
  const color = REGIME_COLORS[live.regime] || "#898781";
  const cell = (lbl, val, cls = "") =>
    `<div><span class="lbl">${lbl}</span><b class="${cls}">${val}</b></div>`;
  const ma = (ok, n) => `<span class="chip small ${ok ? "state-above" : "state-below"}">${
    ok ? "&gt;" : "&lt;"} ${n}dma</span>`;
  return `
    <div class="liveStrip">
      <div class="statRow tight">
        ${cell("Last", live.px === null ? "—" : `$${live.px.toFixed(2)}`)}
        ${cell("1y", signed(live.ret1y, 0), live.ret1y >= 0 ? "pos" : "neg")}
        ${/* offHi already arrives signed: 0 at the high, negative below it. Do not negate. */ ""}
        ${cell("From high", live.offHi === 0 ? "at high" : signed(live.offHi, 1),
               live.offHi === 0 ? "pos" : "neg")}
        ${cell("RSI", num(live.rsi, 0))}
        ${cell("65d ROC", signed(live.roc, 0), live.roc >= 0 ? "pos" : "neg")}
        ${cell("Rel vol", num(live.relVol, 2, "x"))}
      </div>
      <div class="chipRow">
        ${ma(live.a20, 20)}${ma(live.a50, 50)}
        ${live.partial ? '<span class="chip small warn">partial history</span>' : ""}
        ${live.pinned ? '<span class="chip small warn">price-pinned</span>' : ""}
        <span class="chip small univ">${esc(live.universeLabel)}</span>
        <span class="regimeChip tiny" style="background:${color}">${esc(live.regime)}</span>
      </div>
    </div>`;
}

function renderImplications(doc, byTicker) {
  const host = document.querySelector("#implications");
  const h = new URLSearchParams(location.search).get("h") || "1y";

  const draw = (filter) => {
    const rows = doc.implications.filter(i => filter === "all" || i.direction === filter);
    host.querySelector("#impList").innerHTML = rows.map(i => {
      const link = i.live
        ? `<a class="impGo" href="./${i.live.tab}.html?t=${encodeURIComponent(i.ticker)}&h=${h}"
             >open in ${esc(i.live.universeLabel)} →</a>`
        : `<span class="impGo none" title="${esc(i.externalReason || "")}">no price data in this build</span>`;
      return `
        <div class="card imp dir-edge-${esc(i.direction)}" id="imp-${esc(i.ticker)}">
          <div class="impHead">
            <div>
              <span class="impTk">${esc(i.ticker)}</span>
              ${dirTag(i.direction)}
              ${i.scope !== "name" ? `<span class="chip small scope">${esc(i.scope)}</span>` : ""}
            </div>
            <div class="chipRow">${sourceChips(i.sources)}${gradeChip(i.grade)}</div>
          </div>
          ${strip(i.live)}
          <p class="impLine">${esc(i.line)}</p>
          <div class="impFoot">${link}</div>
        </div>`;
    }).join("");
    host.querySelectorAll(".impFilter").forEach(b =>
      b.classList.toggle("active", b.dataset.dir === filter));
  };

  const n = d => doc.implications.filter(i => i.direction === d).length;
  host.innerHTML = `
    <h2>Stock-specific implications</h2>
    <p class="note">One line per name, with the live technical read joined in from the same
      pipeline the other four tabs render — so the narrative and the tape sit on one card and can
      be compared directly. <b>Scope</b> matters: <code>name</code> is a call on that ticker,
      <code>cohort</code> is a group-level number applied to a member, <code>read-through</code> is
      implied from evidence about something else.</p>
    <div class="ctlRow">
      <label>Direction</label>
      <button class="hBtn impFilter" data-dir="all">all <span class="cnt">${doc.implications.length}</span></button>
      <button class="hBtn impFilter" data-dir="bull">constructive <span class="cnt">${n("bull")}</span></button>
      <button class="hBtn impFilter" data-dir="bear">cautionary <span class="cnt">${n("bear")}</span></button>
      <button class="hBtn impFilter" data-dir="neutral">two-sided <span class="cnt">${n("neutral")}</span></button>
    </div>
    <div id="impList" class="impGrid"></div>`;
  host.querySelectorAll(".impFilter").forEach(b =>
    b.addEventListener("click", () => draw(b.dataset.dir)));
  draw("all");
}

function renderFooter(doc) {
  const g = doc.gradeScale;
  document.querySelector("#footer").innerHTML = `
    <div class="card">
      <h3>How to read this tab</h3>
      <p class="note">Every other tab in this dashboard renders <b>measurements</b> — the output of
      a stated rule against a stated threshold. This tab renders <b>claims</b> made by research
      houses, so the chip means something different here: it names the source and grades the
      evidence, rather than reporting a test result. The claim text stays plain prose.</p>
      <div class="pbGrid">
        ${["a", "b", "c", "d"].map(k =>
          `<div class="pbRow"><span class="pbKey">${gradeChip(k)} ${esc(GRADE_LABEL[k])}</span>
             <span>${esc(g[k])}</span></div>`).join("")}
      </div>
      <p class="note" style="margin-top:10px">${esc(g.note)}</p>
    </div>
    <div class="card">
      <h3>${esc(doc.evidenceHierarchy.title)}</h3>
      <ol class="hier">${doc.evidenceHierarchy.rungs.map(r => `<li>${esc(r)}</li>`).join("")}</ol>
      <p class="note">${esc(doc.evidenceHierarchy.note)}</p>
    </div>
    ${(doc.perimeters || []).length ? `
      <details class="card ig-det"><summary><b>Figures quoted at multiple perimeters</b> — scope,
        not disagreement</summary>
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
    <p class="src">Source: <code>${esc(doc.sourceDoc)}</code> · synthesis ${esc(doc.asOf)} ·
      build ${esc(doc.version)} · technicals joined from
      ${doc.joinStats.joined} of ${doc.implications.length} named tickers
      (${doc.joinStats.external} not present in any workbook in this build).</p>`;
}

export async function initFab5() {
  await initNav("fab5");
  const idx = await loadIndex();
  const page = (idx.pages || {}).fab5;
  if (!page) {
    throw new Error("fab5 is not registered in index.json — run python scripts/build_all.py");
  }
  const r = await fetch(`../data/${page.dir}/${page.file}?v=${page.version}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} loading the fab5 payload`);
  const doc = await r.json();

  const byTicker = Object.fromEntries(doc.implications.map(i => [i.ticker, i]));

  renderHeader(doc);
  renderInfographic(doc);
  renderCall(doc);
  renderInsights(doc, byTicker);
  renderAgreement(doc);
  renderChecklist(doc);
  renderImplications(doc, byTicker);
  renderFooter(doc);
}
