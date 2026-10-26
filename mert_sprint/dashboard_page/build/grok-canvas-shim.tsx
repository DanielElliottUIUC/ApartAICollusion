// Minimal stand-in for the "grok/canvas" component library, written so the
// dashboard Page source can be bundled into one static HTML file.
// It approximates the look of the original Page; it is not the original library.
import React, { useState, useEffect, useRef, useMemo, createContext, useContext } from "react";
export { useState, useEffect, useRef, useMemo };
export type ChangeEvent<T = Element> = React.ChangeEvent<T>;

const THEME = {
  bg: { base: "#ffffff", subtle: "#f4f5f7", elevated: "#ffffff" },
  text: { primary: "#16181d", secondary: "#4b5160", tertiary: "#7d8494" },
  border: { default: "#d5d8de", strong: "#9aa0ab", subtle: "#e7e9ed" },
  dataviz: { categorical: ["#2f6fdf", "#e07b16", "#1f9d6b", "#c2398f", "#7a5cd6", "#c9a400", "#d04848", "#2a9bb5"], other: "#9aa0ab" },
  font: { family: "Inter, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif", mono: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" },
};
export const useGrokTheme = () => THEME;
const th = THEME;
const Depth = createContext(0);

function inline(s: any): any {
  if (typeof s !== "string") return s;
  const parts = s.split(/(`[^`]+`)/g);
  return parts.map((p, i) => p.startsWith("`") && p.endsWith("`") && p.length > 1
    ? <code key={i} style={{ fontFamily: th.font.mono, background: th.bg.subtle, padding: "1px 4px", borderRadius: 4, fontSize: "0.92em" }}>{p.slice(1, -1)}</code>
    : p);
}
const toneColor = (t?: string) => t === "success" ? "#1f9d6b" : t === "warning" ? "#c77700" : t === "danger" ? "#d04848" : th.text.primary;

export function Page(p: any) {
  const w = p.width === "wide" ? 1200 : 860;
  return <div style={{ fontFamily: th.font.family, color: th.text.primary, background: th.bg.base, maxWidth: w, margin: "0 auto", padding: "32px 20px 64px", lineHeight: 1.5, fontSize: 16 }}>
    <h1 style={{ fontSize: 32, margin: "0 0 8px" }}>{p.title}</h1>
    {p.summary && <p style={{ color: th.text.secondary, fontSize: 18, marginTop: 0 }}>{p.summary}</p>}
    {p.children}
    {p.sources && <div style={{ marginTop: 40, borderTop: `1px solid ${th.border.default}`, paddingTop: 12, color: th.text.secondary, fontSize: 14 }}>
      <div style={{ fontWeight: 600 }}>Sources</div>
      <ul>{p.sources.map((s: string, i: number) => <li key={i}>{s}</li>)}</ul>
    </div>}
  </div>;
}
export function Section(p: any) {
  const d = useContext(Depth);
  const H: any = d === 0 ? "h2" : d === 1 ? "h3" : "h4";
  const size = d === 0 ? 24 : d === 1 ? 19 : 17;
  return <section id={p.id} style={{ margin: d === 0 ? "36px 0 12px" : "18px 0 8px", minWidth: 0 }}>
    {(p.heading || p.actions) && <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", justifyContent: "space-between" }}>
      {p.heading && <H style={{ fontSize: size, margin: "4px 0" }}>{p.heading}</H>}
      {p.actions && <div>{p.actions}</div>}
    </div>}
    <Depth.Provider value={d + 1}><div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 8 }}>{p.children}</div></Depth.Provider>
  </section>;
}
export const Text = (p: any) => <p style={{ margin: 0 }}>{inline(p.children)}</p>;
export const Callout = (p: any) => <div style={{ borderLeft: `4px solid ${p.tone === "warning" ? "#c77700" : th.dataviz.categorical[0]}`, background: th.bg.subtle, padding: "10px 14px", borderRadius: 6 }}>
  {p.lead && <strong>{p.lead}. </strong>}{inline(p.children)}</div>;
export const Quote = (p: any) => <blockquote style={{ margin: 0, borderLeft: `3px solid ${th.border.strong}`, padding: "4px 14px", color: th.text.primary }}>
  <div style={{ fontStyle: "italic" }}>{p.children}</div>{p.cite && <div style={{ fontSize: 13, color: th.text.tertiary, marginTop: 4 }}>{p.cite}</div>}</blockquote>;
export function Table(p: any) {
  const cell = (c: any) => c && typeof c === "object" && !React.isValidElement(c) && "text" in c ? <span style={{ color: toneColor(c.tone), fontWeight: 600 }}>{c.text}</span> : inline(c);
  return <div style={{ overflowX: "auto" }}><table style={{ borderCollapse: "collapse", width: "100%", fontSize: 15 }}>
    <thead><tr>{p.columns.map((c: string, i: number) => <th key={i} style={{ textAlign: "left", borderBottom: `2px solid ${th.border.strong}`, padding: "6px 8px", verticalAlign: "bottom" }}>{c}</th>)}</tr></thead>
    <tbody>{p.rows.map((r: any[], i: number) => <tr key={i}>{r.map((c: any, j: number) => <td key={j} style={{ borderBottom: `1px solid ${th.border.subtle}`, padding: "6px 8px", verticalAlign: "top" }}>{cell(c)}</td>)}</tr>)}</tbody>
  </table></div>;
}
export const Grid = (p: any) => <div style={{ display: "grid", gridTemplateColumns: `repeat(auto-fit, minmax(${p.columns >= 3 ? 240 : 320}px, 1fr))`, gap: 16 }}>
  {React.Children.map(p.children, (ch: any) => ch == null || ch === false ? null : <div style={p.plain ? { minWidth: 0 } : { minWidth: 0, border: `1px solid ${th.border.subtle}`, borderRadius: 10, padding: 12, background: th.bg.base }}>{ch}</div>)}</div>;
export const Columns = (p: any) => {
  const max = Math.max(...p.points.map((x: any) => x.value), 1e-9);
  return <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 220, padding: "8px 0" }}>
    {p.points.map((x: any, i: number) => <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", height: "100%" }}>
      <div style={{ fontSize: 13 }}>{x.display ?? x.value}</div>
      <div style={{ width: "70%", height: `${(x.value / max) * 150}px`, background: i === p.emphasis ? th.dataviz.categorical[0] : th.dataviz.other, borderRadius: "4px 4px 0 0" }} />
      <div style={{ fontSize: 12, marginTop: 4, textAlign: "center" }}>{x.label}</div>
    </div>)}</div>;
};
export const Bars = (p: any) => {
  const max = Math.max(...p.bars.map((x: any) => x.value), 1e-9);
  return <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>{p.bars.map((b: any, i: number) => <div key={i} style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 10, alignItems: "center" }}>
    <div style={{ fontSize: 15 }}>{b.label}</div>
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}><div style={{ width: `${(b.value / max) * 70}%`, minWidth: 2, height: 18, background: th.dataviz.categorical[0], borderRadius: 3 }} /><span style={{ fontSize: 13, color: th.text.secondary }}>{b.display ?? b.value}</span></div>
  </div>)}</div>;
};
const btn = (active: boolean): React.CSSProperties => ({ border: `1px solid ${active ? th.dataviz.categorical[0] : th.border.default}`, background: active ? th.dataviz.categorical[0] : th.bg.base, color: active ? "#fff" : th.text.primary, borderRadius: 8, padding: "6px 12px", fontSize: 15, cursor: "pointer", fontFamily: th.font.family });
export const Button = (p: any) => <button style={btn(p.variant === "primary")} onClick={p.onClick}>{p.label}</button>;
export const Segmented = (p: any) => <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>{p.options.map((o: any) => {
  const v = typeof o === "object" ? o.value : o; const l = typeof o === "object" ? o.label : o;
  return <button key={String(v)} style={btn(v === p.value)} onClick={() => p.onChange(v)}>{l}</button>; })}</div>;
export const Select = (p: any) => <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 14, color: th.text.secondary }}>{p.label}
  <select value={p.value} onChange={(e) => p.onChange(e.target.value)} style={{ fontSize: 15, padding: "6px 8px", borderRadius: 8, border: `1px solid ${th.border.default}`, fontFamily: th.font.family }}>
    {p.options.map((o: any) => { const v = typeof o === "object" ? o.value : o; const l = typeof o === "object" ? o.label : o; return <option key={v} value={v}>{l}</option>; })}
  </select></label>;
export const Toggle = (p: any) => <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
  <input type="checkbox" checked={!!p.value} onChange={(e) => p.onChange(e.target.checked)} style={{ width: 18, height: 18 }} />{p.label}</label>;
export const Properties = (p: any) => <dl style={{ display: "grid", gridTemplateColumns: "max-content 1fr", gap: "4px 14px", margin: 0 }}>
  {p.items.map((it: any, i: number) => <React.Fragment key={i}><dt style={{ color: th.text.secondary }}>{it.label}</dt><dd style={{ margin: 0 }}>{inline(it.value)}</dd></React.Fragment>)}</dl>;
export const BulletList = (p: any) => <ul style={{ margin: 0, paddingLeft: 22 }}>{p.items.map((it: any, i: number) => <li key={i}>{inline(it)}</li>)}</ul>;
export const Steps = (p: any) => <ol style={{ margin: 0, paddingLeft: 22 }}>{p.steps.map((s: any, i: number) => <li key={i}><strong>{s.title}</strong>{s.detail ? `: ${s.detail}` : ""}</li>)}</ol>;
export const TableOfContents = (p: any) => <nav style={{ background: th.bg.subtle, borderRadius: 10, padding: "10px 16px", margin: "16px 0" }}>
  <div style={{ fontWeight: 600, marginBottom: 4 }}>Contents</div>
  {p.items.map((it: any, i: number) => <div key={i} style={{ paddingLeft: (it.depth ?? 0) * 18 }}><a href={`#${it.id}`} style={{ color: th.dataviz.categorical[0], textDecoration: "none" }}>{it.label}</a></div>)}</nav>;
export const Equation = (p: any) => <div style={{ fontSize: 20, textAlign: "center", display: "flex", justifyContent: "center", alignItems: "center", gap: 6 }}>{p.children}</div>;
export const Frac = (p: any) => <span style={{ display: "inline-flex", flexDirection: "column", alignItems: "center", verticalAlign: "middle" }}>
  <span style={{ borderBottom: `1px solid ${th.text.primary}`, padding: "0 4px" }}>{p.num}</span><span style={{ padding: "0 4px" }}>{p.den}</span></span>;
export const LinkCards = (p: any) => <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>{p.links.map((l: any, i: number) =>
  <a key={i} href={l.href} target="_blank" rel="noreferrer" style={{ border: `1px solid ${th.border.default}`, borderRadius: 10, padding: "10px 14px", textDecoration: "none", color: th.text.primary, flex: "1 1 260px" }}>
    <div style={{ fontWeight: 600 }}>{l.title}</div><div style={{ fontSize: 13, color: th.text.tertiary }}>{l.site}</div></a>)}</div>;
export function Diagram(p: any) {
  const byId: Record<string, any> = Object.fromEntries(p.nodes.map((n: any) => [n.id, n]));
  return <div style={{ display: "flex", flexWrap: "wrap", alignItems: "stretch", gap: 6 }}>{p.nodes.map((n: any, i: number) => {
    const e = p.edges.find((x: any) => x.from === n.id);
    return <React.Fragment key={n.id}>
      <div style={{ border: `1.5px solid ${n.kind === "terminal" ? th.dataviz.categorical[0] : th.border.strong}`, borderRadius: 10, padding: "8px 10px", flex: "1 1 150px", background: th.bg.subtle }}>
        <div style={{ fontWeight: 600 }}>{n.label}</div>{n.detail && <div style={{ fontSize: 13, color: th.text.secondary }}>{n.detail}</div>}</div>
      {e && byId[e.to] && <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", fontSize: 12, color: th.text.secondary, maxWidth: 140, textAlign: "center" }}><span style={{ fontSize: 20 }}>→</span>{e.label}</div>}
    </React.Fragment>; })}</div>;
}
