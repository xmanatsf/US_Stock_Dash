/* Renders interpretation output. Python decides; this file only formats.
 *
 * The load-bearing rule, and the whole reason this is a separate module:
 *   CHIPS AND COLOURED BADGES ARE RESERVED FOR THE OUTPUT OF A STATED, TESTABLE RULE.
 *   INTERPRETIVE PROSE GETS NO CHROME AT ALL.
 * Giving a conclusion a green chip is what makes a narrative look measured. Every conclusion
 * block therefore carries data-signals listing the signal ids it rests on, so the claim can be
 * traced back to numbers that are on the page.
 */

import { fmt, sign } from "./charts.js";
import { slug } from "./regimes.js";

const CHIP = {
  "confirmed": "✓ Confirmed",
  "weak": "◐ Weak / partial",
  "not-confirmed": "✗ Not confirmed",
  "not-testable": "◦ Not testable",
};

export function renderVerdict(host, summary) {
  if (!host) return;
  const v = summary.verdict, m = summary.meta;
  const pb = v.playbook || {};
  const color = `var(--regime-${slug(v.regime)})`;
  host.innerHTML = `
    <div class="callout" style="--accent:${color}">
      <div class="calloutHead">
        <span class="regimeChip" style="background:${color}">${v.regime}</span>
        <span class="calloutMeta">composite score ${sign(v.score)} · pillar coverage ${v.coverage}%
          · as of ${v.lastDate}</span>
      </div>
      <div class="calloutBody">
        <div class="statRow">
          <div><span class="lbl">Composite</span><b>${fmt(v.comp, 1)}</b></div>
          <div><span class="lbl">Peak</span><b>${fmt(v.peakVal, 1)}</b>
               <span class="sub">${v.peakDate}</span></div>
          <div><span class="lbl">From peak</span><b class="${v.drawdown < 0 ? "neg" : "pos"}">${sign(v.drawdown)}%</b></div>
          <div><span class="lbl">Trough</span><b>${fmt(v.troughVal, 1)}</b>
               <span class="sub">${v.troughDate}</span></div>
          <div><span class="lbl">From trough</span><b class="pos">${sign(v.upFromTrough)}%</b></div>
        </div>
      </div>
    </div>
    ${v.topConfirmed ? `<p class="warnNote">A distribution top is confirmed in the trailing window
      (peak anchor, a first crack, and a failed retest or 50-dma break). In this structure oversold
      bounces tend to fail — the framework treats a washout here as a bull trap rather than a
      buyable base.</p>` : ""}
    <div class="playbook">
      <h3>What the framework implies next</h3>
      <p class="note">Interpretation, not measurement. It follows from the regime label above.</p>
      <div class="pbGrid">
        ${row("Exposure", pb.exposure)}
        ${row("Tilt", pb.tilt)}
        ${row("Confirms if", pb.confirm)}
        ${row("Invalidated by", pb.invalidate)}
      </div>
      ${pb.note ? `<p class="pbNote">${pb.note}</p>` : ""}
    </div>`;
}

function row(k, v) {
  return v ? `<div class="pbRow"><span class="pbKey">${k}</span><span class="pbVal">${v}</span></div>` : "";
}

export function renderPillars(host, summary) {
  if (!host) return;
  const ps = summary.pillars || [];
  host.innerHTML = ps.map(p => `
    <div class="card pillar">
      <div class="pillarHead">
        <span class="pillarName">${p.name}</span>
        <span class="chip ${p.status}">${CHIP[p.status] || p.status}</span>
      </div>
      <div class="pillarScore">${p.score == null ? "not scored" : `score ${sign(p.score, 0)}`}
        <span class="dir dir-${p.direction}">${p.direction}</span></div>
      <ul class="signals">${(p.signals || []).map(s => `<li>${s}</li>`).join("")}</ul>
      <p class="conclusion" data-signals="${(p.signals || []).length}">${p.conclusion}</p>
    </div>`).join("");
}

export function renderEvents(host, summary) {
  if (!host) return;
  const ev = summary.events || [];
  if (!ev.length) { host.innerHTML = `<p class="note">No structural events detected in the window.</p>`; return; }
  host.innerHTML = `<ol class="timeline">${ev.map((e, i) => `
    <li class="ev ev-${e.kind}">
      <span class="evBadge">${i + 1}</span>
      <div><div class="evTitle">${e.title} <span class="evDate">${e.date}</span></div>
      <div class="evDetail">${e.detail}</div></div>
    </li>`).join("")}</ol>`;
}

export function renderBaskets(host, summary) {
  if (!host) return;
  const b = summary.baskets || {};
  const keys = Object.keys(b);
  if (!keys.length) { host.innerHTML = ""; return; }
  const n = summary.dates.length - 1;
  host.innerHTML = `<div class="card"><h3>Sub-basket rotation</h3>
    <p class="note">Relative to the universe composite, base 100. Absolute performance says what
    happened; relative says what is being rotated into, and rotation is what dates the cycle.</p>
    <table class="tbl"><thead><tr><th>Basket</th><th class="num">Names</th>
      <th class="num">Relative</th><th class="num">65d ROC</th><th>Scored</th></tr></thead>
    <tbody>${keys.map(k => {
      const v = b[k];
      const rel = v.rel ? v.rel[n] : null;
      const d = rel == null ? null : rel - 100;
      return `<tr><td>${k}</td><td class="num">${v.n}</td>
        <td class="num ${d == null ? "" : d >= 0 ? "pos" : "neg"}">${d == null ? "–" : sign(d, 1) + " pts"}</td>
        <td class="num">–</td>
        <td>${v.scored ? `<span class="chip confirmed">scored</span>`
                       : `<span class="chip not-testable">${v.note || "not scored"}</span>`}</td></tr>`;
    }).join("")}</tbody></table></div>`;
}

export function renderSplits(host, summary) {
  if (!host) return;
  const sp = summary.splits || {};
  const keys = Object.keys(sp);
  if (!keys.length) { host.innerHTML = ""; return; }
  const n = summary.dates.length - 1;
  host.innerHTML = keys.map(k => {
    const s = sp[k];
    const a = s.comp[n], b = s.compEx[n];
    const ratio = b ? a / b : null;
    return `<div class="card splitCard">
      <h3>Composite split — ${s.label}</h3>
      <p class="note">${s.note || ""}</p>
      <div class="statRow">
        <div><span class="lbl">${s.label} (${s.memberCount || s.members.length} names)</span><b>${fmt(a, 1)}</b></div>
        <div><span class="lbl">Rest of the universe (${s.exCount || "–"} names)</span><b>${fmt(b, 1)}</b></div>
        <div><span class="lbl">Blended</span><b>${fmt(summary.comp[n], 1)}</b></div>
        <div><span class="lbl">Spread</span><b class="${a - b >= 0 ? "pos" : "neg"}">${sign(a - b, 1)} pts</b></div>
        ${ratio ? `<div><span class="lbl">Ratio</span><b>${fmt(ratio, 1)}×</b></div>` : ""}
      </div>
      <p class="note"><b>Read the blended number with this in mind.</b> All three series start at
        100 on the same date, so the gap above is the whole argument for splitting them: the
        blended composite is not describing the ${s.exCount || "other"} names that make up most of
        the universe.</p>
      <p class="note">Composite members (full history only): ${s.members.join(", ")}.
        ${s.partialExcluded && s.partialExcluded.length
          ? `Also in this basket but excluded from the composite for partial history:
             ${s.partialExcluded.join(", ")} — composites are built from full-history names only,
             the same rule the universe composite uses.`
          : ""}</p>
    </div>`;
  }).join("");
}

export function renderValidation(host, validation, opts = {}) {
  if (!host) return;
  const f = (validation && validation.findings) || [];
  const fatal = f.filter(x => x.severity === "fatal");
  const warn = f.filter(x => x.severity === "warn");
  const info = f.filter(x => x.severity === "info");
  if (!f.length) { host.innerHTML = ""; return; }

  const block = (items, cls, label) => items.length ? `
    <div class="vBlock ${cls}">
      <div class="vHead">${label} (${items.length})</div>
      <ul>${items.map(x => `<li><b>${x.code}</b> — ${x.message}
        ${x.tickers && x.tickers.length ? `<span class="vTick">${x.tickers.join(", ")}</span>` : ""}</li>`).join("")}</ul>
    </div>` : "";

  host.innerHTML = `
    ${fatal.length ? `<div class="banner fatal">
      <b>This tab cannot render charts.</b> The source workbook failed validation. The findings
      below are shown instead of a plausible-looking chart built on bad data.</div>` : ""}
    <details class="validation"${fatal.length || opts.open ? " open" : ""}>
      <summary>Data validation — ${fatal.length} fatal, ${warn.length} warnings, ${info.length} notes</summary>
      ${block(fatal, "fatal", "Fatal")}
      ${block(warn, "warn", "Warnings")}
      ${block(info, "info", "Notes")}
    </details>`;
}

export { slug };

// ---------------------------------------------------------------- sector / group rollups

const REGIME_CLASS = {
  "Uptrend continuation": "regime-uptrend",
  "Topping / deteriorating": "regime-topping",
  "Positive inflection / bottoming": "regime-bottoming",
  "Downtrend continuation": "regime-downtrend",
  "Mixed / no clear signal": "regime-mixed",
  "insufficient-sample": "regime-insufficient",
};
const REGIME_SHORT = {
  "Uptrend continuation": "Uptrend", "Topping / deteriorating": "Topping",
  "Positive inflection / bottoming": "Bottoming", "Downtrend continuation": "Downtrend",
  "Mixed / no clear signal": "Mixed", "insufficient-sample": "n<3",
};

let hmLevel = "sector", hmSortK = "ret", hmSortAsc = false;

export function renderRollups(host, summary, sparkline) {
  if (!host) return;
  const R = summary.rollups || {};
  const levels = Object.keys(R);
  if (!levels.length) { host.innerHTML = ""; return; }
  if (!levels.includes(hmLevel)) hmLevel = levels[0];

  const COLS = [
    ["name", "Group", false], ["n", "N", true], ["ret", "Return %", true],
    ["ret1y", "1y %", true], ["offHi", "Off high %", true],
    ["b20Last", "% > 20-dma", true], ["roc65Last", "65d ROC %", true],
    ["trend", "Trend", false], ["regime", "Regime", false],
  ];

  function draw() {
    const rows = [...(R[hmLevel] || [])].sort((a, b) => {
      const x = a[hmSortK], y = b[hmSortK];
      if (x == null) return 1;
      if (y == null) return -1;
      return (x > y ? 1 : x < y ? -1 : 0) * (hmSortAsc ? 1 : -1);
    });
    host.innerHTML = `
      <div class="card">
        <h3>Sector and industry-group rollup</h3>
        <p class="note">Each group is classified off its <b>own</b> equal-weight sub-composite,
          independently of the market-wide call, using four inputs: where the window extremum sits
          relative to now, the breadth trend, the direction of 65-day momentum, and whether new
          highs or new lows are expanding. A group with fewer than 3 full-history members gets no
          composite at all rather than a fabricated one.</p>
        <div class="tabBtns small">${levels.map(l =>
          `<button class="tabBtn ${l === hmLevel ? "active" : ""}" data-level="${l}">
             ${l === "sector" ? "Sector" : "Industry group"}</button>`).join("")}</div>
        <div class="tblWrap"><table class="tbl hmTbl"><thead><tr>${COLS.map(([k, l, num]) =>
          `<th data-k="${k}" class="${num ? "num" : ""}${k === hmSortK ? " sorted" : ""}">${l}</th>`).join("")}
        </tr></thead><tbody>${rows.map(r => `
          <tr>
            <td title="${(r.signals || []).join(" · ")}">${r.name}</td>
            <td class="num">${r.nFull}${r.n !== r.nFull ? `<span class="sub">/${r.n}</span>` : ""}</td>
            <td class="num ${cl(r.ret)}">${sg(r.ret)}</td>
            <td class="num ${cl(r.ret1y)}">${sg(r.ret1y)}</td>
            <td class="num ${cl(r.offHi)}">${sg(r.offHi)}</td>
            <td class="num">${r.b20Last == null ? "–" : fmt(r.b20Last, 0) + "%"}</td>
            <td class="num ${cl(r.roc65Last)}">${sg(r.roc65Last)}</td>
            <td title="trailing 252 sessions — the same window the regime is read off">${
              r.comp ? sparkline(r.comp.slice(-252).filter((_, i) => i % 3 === 0)) : "–"}</td>
            <td><span class="chip ${REGIME_CLASS[r.regime] || ""}"
                     title="${r.note || (r.signals || []).join(" · ")}">
                  ${REGIME_SHORT[r.regime] || r.regime}</span></td>
          </tr>`).join("")}</tbody></table></div>
      </div>`;
    host.querySelectorAll("[data-level]").forEach(b => b.onclick = () => {
      hmLevel = b.dataset.level; draw();
    });
    host.querySelectorAll("th").forEach(th => th.onclick = () => {
      const k = th.dataset.k;
      if (k === hmSortK) hmSortAsc = !hmSortAsc; else { hmSortK = k; hmSortAsc = false; }
      draw();
    });
  }
  draw();
}

export function renderCompositeSplit(host, summary) {
  if (!host) return;
  const cs = summary.compositeSplit || [];
  if (!cs.length) { host.innerHTML = ""; return; }
  host.innerHTML = cs.slice(0, 3).map(s => `
    <div class="card splitCard">
      <h3>Composite-distorting spread — ${s.parent}</h3>
      <p class="note">Before trusting any single blended number for this sector, note that its
        industry groups disagree by ${fmt(s.spread, 0)} percentage points.</p>
      <div class="statRow">
        <div><span class="lbl">${s.hiGroup}</span><b class="${cl(s.hiRet)}">${sg(s.hiRet)}%</b>
          <span class="sub">${REGIME_SHORT[s.hiRegime] || s.hiRegime}</span></div>
        <div><span class="lbl">${s.loGroup}</span><b class="${cl(s.loRet)}">${sg(s.loRet)}%</b>
          <span class="sub">${REGIME_SHORT[s.loRegime] || s.loRegime}</span></div>
        <div><span class="lbl">Spread</span><b>${fmt(s.spread, 0)} pts</b></div>
      </div>
    </div>`).join("");
}

export function renderQuartiles(host, summary) {
  if (!host) return;
  const q = summary.quartiles || [];
  if (!q.length) { host.innerHTML = ""; return; }
  const maxAbs = Math.max(...q.map(b => Math.abs(b.avgRet)), 1);
  host.innerHTML = `
    <div class="card">
      <h3>Return by ${q[0].metric} quartile</h3>
      <p class="note">Quartile edges and averages are computed in the build; the bar below is a
        diverging scale anchored at zero.</p>
      ${q.map(b => {
        const pct = Math.min(100, Math.abs(b.avgRet) / maxAbs * 50);
        const pos = b.avgRet >= 0;
        return `<div class="bucketRow">
          <span title="${b.tickers.join(', ')}">${b.bucket}
            <span class="sub">${fmt(b.lo, 1)} to ${fmt(b.hi, 1)} · n=${b.n}</span></span>
          <span class="bar"><i style="${pos ? "left:50%" : `right:50%`};width:${pct}%;
            background:${pos ? "var(--good-text)" : "var(--critical)"}"></i></span>
          <span class="num ${cl(b.avgRet)}">${sg(b.avgRet)}%</span>
        </div>`;
      }).join("")}
    </div>`;
}

const cl = v => v == null ? "" : v >= 0 ? "pos" : "neg";
const sg = (v, d = 1) => v == null ? "–" : (v > 0 ? "+" : "") + fmt(v, d);
