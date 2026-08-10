/* Single source of truth for regime labels and colours.
 *
 * These were previously duplicated in tabs.js, index.html and dashboard.css. Three copies of a
 * label-to-colour map is three chances for a regime to render in the wrong colour after someone
 * edits one of them. The CSS custom properties still exist for the callout accent, but they are
 * derived from the same slugs used here.
 *
 * The order matches config/parameters.json regime.order -- from most bearish to most bullish,
 * with Indeterminate last because it is an absence of signal, not a position on the scale.
 */

export const REGIME_COLORS = {
  "Capitulation / washout": "#d03b3b",
  "Capitulation inside a confirmed top": "#8c1d1d",
  "Breakdown": "#ec835a",
  "Bottoming / base": "#fab219",
  "Early recovery": "#9dc63b",
  "Confirmed uptrend": "#1baf7a",
  "Momentum expansion": "#0d8f5f",
  "Late-cycle topping": "#b5462f",
  "Indeterminate": "#898781",
};

export function regimeColor(label) {
  return REGIME_COLORS[label] || "#898781";
}

export function slug(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}
