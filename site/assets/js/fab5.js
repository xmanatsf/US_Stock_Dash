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
  document.querySelector("#tabMeta").textContent =
    // The synthesis counts 10 source BATCHES across 7 houses (ISI ships 2, TMTB 4). Both numbers
    // are true and neither alone is; printing one as "sources" invites the wrong one being quoted.
    `10 source batches across ${doc.sources.length} houses · synthesis as of ${doc.asOf} · ` +
    `prior baseline ${doc.priorBaseline} · technicals as of ${doc.universeAsOf.join(", ")}`;

  document.querySelector("#focus").innerHTML = `
    <div class="card">
      <h3>Focus question carried in from the ${esc(doc.priorBaseline)} baseline</h3>
      <p class="note" style="margin-bottom:10px">${esc(doc.focusQuestion)}</p>
      <div class="srcRow">${doc.sources.map(s =>
        `<span class="srcPill"><b>${esc(s.house)}</b> ${esc(s.detail)}</span>`).join("")}</div>
    </div>`;
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
            <b>${esc(d.claim)}${d.isNew ? ' <span class="chip small newTag">new</span>' : ""}</b>
            <ul class="sides">${d.sides.map(s => `<li>${esc(s)}</li>`).join("")}</ul>
            <p class="note"><span class="evLbl">Tiebreaker</span> ${esc(d.tiebreaker)}</p>
            <div class="chipRow">${sourceChips(d.sources)}${gradeChip(d.grade)}</div>
          </div>`).join("")}
      </div>
    </div>`;
}

function renderChecklist(doc) {
  document.querySelector("#checklist").innerHTML = `
    <h2>Monitoring checklist — new and materially changed items</h2>
    <p class="note">The synthesis carries 29 standing indicators. These are the ones this batch
      moved, plus the two it added.</p>
    <div class="tblWrap">
      <table class="tbl ckTbl">
        <thead><tr><th>#</th><th>Indicator</th><th>Where it stands</th>
          <th>Bullish trigger</th><th>Bearish trigger</th><th>Next checkpoint</th></tr></thead>
        <tbody>${doc.checklist.map(c => `
          <tr>
            <td class="num">${c.n}${c.isNew ? ' <span class="chip small newTag">new</span>' : ""}</td>
            <td><b>${esc(c.indicator)}</b></td>
            <td class="ckBase">${esc(c.baseline)}</td>
            <td class="ckBull">${esc(c.bull)}</td>
            <td class="ckBear">${esc(c.bear)}</td>
            <td class="ckWhen">${esc(c.checkpoint)}</td>
          </tr>`).join("")}</tbody>
      </table>
    </div>`;
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
  renderCall(doc);
  renderInsights(doc, byTicker);
  renderAgreement(doc);
  renderChecklist(doc);
  renderImplications(doc, byTicker);
  renderFooter(doc);
}
