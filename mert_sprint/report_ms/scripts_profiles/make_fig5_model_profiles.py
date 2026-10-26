"""Figure 5: behaviour fingerprint of the six seller models.

One row per seller model, one column per measured behaviour, columns grouped by design:
  (a) M.S.'s 4+4 market (talk with messaging on; price opened at $97.50 and at $90) and the Bertrand game (P0);
  (b) D.E.'s 5+5 undercover market (the plain offer, arm D, and the warning, arm E).
Every cell shows its value and its n, and a tinted bar whose length is the value on the column's scale
(the late-ask bars grow leftward from the opening). A blank cell means the model was not run in that design.
All values come from profiles_lib (the run files and D.E.'s CSVs at b7cbccd); the cell table is also written to
report_ms/supplement/data/S5/fig5_cells.csv.

Run from anywhere:  python report_ms/scripts_profiles/make_fig5_model_profiles.py
"""
import csv
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import profiles_lib as L
from profiles_lib import style

MINUS = "−"
LABEL = {"gemini": "Gemini 3.8\nFlash", "grok": "Grok 4.7", "sol": "GPT-5.6 Sol", "luna": "GPT-6 Luna",
         "gpt41": "GPT-4.1", "haiku": "Claude\nHaiku 5.5"}


def pct(v):
    p = 100 * v
    return f"{p:.1f}%" if 0 < p < 1 else f"{p:.0f}%"


def dollars(v):
    return f"{MINUS if v < 0 else '+'}${abs(v):.1f}"


def signed(v, nd=2):
    return f"{MINUS if v < 0 else ''}{abs(v):.{nd}f}"


def rate_cell(k, n):
    return {"value": k / n, "top": pct(k / n), "sub": f"{k} of {n}", "k": k, "n": n}


# ------------------------------------------------------------------------------------------- cells
def cells_4x4(model):
    out = {}
    df = L.runs_4x4()
    t = L.talk_runs(df)
    t = t[t["seller"] == model]
    if len(t):
        msgs = t["private_msgs"].mean()
        out["msgs"] = {"value": msgs, "top": f"{msgs:.0f}" if msgs >= 10 or msgs == 0 else f"{msgs:.1f}",
                       "sub": f"n = {len(t)}", "n": len(t)}
        total = int(t["public_msgs"].sum() + t["private_msgs"].sum())
        hit = int(t["explicit_public"].sum() + t["explicit_private"].sum())
        out["explicit"] = {"value": hit / total, "top": pct(hit / total), "sub": f"of {total:,}", "k": hit, "n": total}
    for col, opening in (("pass975", 97.5), ("late975", 97.5), ("late90", 90.0)):
        p = L.price_runs(opening, df)
        p = p[p["seller"] == model]
        if not len(p):
            continue
        if col.startswith("pass"):
            out[col] = rate_cell(int(p["passed"].sum()), len(p))
        else:
            v = p["late_minus_opening"].mean()
            out[col] = {"value": v, "top": dollars(v), "sub": f"n = {len(p)}", "n": len(p)}
    b = L.bertrand_runs(model)
    if b:
        g = sum(r[2] for r in b) / len(b)
        out["gain"] = {"value": g, "top": signed(g), "sub": f"n = {len(b)}", "n": len(b)}
    return out


def cells_5x5(model):
    if model not in L.DANIEL_FAMILY:
        return {}
    out = {}
    mk = L.daniel_markets(model)
    d = mk[mk["arm"] == "D"]
    out["passD"] = rate_cell(int(d["passed"].sum()), len(d))
    v = d["late_minus_opening"].mean()
    out["lateD"] = {"value": v, "top": dollars(v), "sub": f"n = {len(d)}", "n": len(d)}
    for col, arm, lab in (("reported", "D", "reported"), ("agreed", "D", "agreed"),
                          ("rejected", "D", "rejected"), ("agreedE", "E", "agreed")):
        kn = L.daniel_label(model, arm, lab)
        if kn:
            out[col] = rate_cell(*kn)
    return out


# Column specs: (key, header, scale, anchor). Bars use value/scale; 'right' bars grow leftward from the opening.
PANEL_A = {
    "groups": [("4+4 market (M.S.)", 0, 5), ("Bertrand", 5, 6)],
    "subgroups": [("Messaging on", 0, 2), ("Opened at\n$97.50", 2, 4), ("Opened\nat $90", 4, 5), ("Prompt\nP0", 5, 6)],
    "cols": [("msgs", "Private\nmessages\nper run", 120, "left"),
             ("explicit", "Floor or\ncartel\nwording", 1, "left"),
             ("pass975", "Passes", 1, "left"),
             ("late975", "Late ask\nminus\nopening", 12, "right"),
             ("late90", "Late ask\nminus\nopening", 12, "right"),
             ("gain", "Collusion\ngain", 1, "left")],
    "cells": cells_4x4,
}
PANEL_B = {
    "groups": [("5+5 undercover market (D.E.)", 0, 6)],
    "subgroups": [("Plain offer, arm D", 0, 5), ("Warning,\narm E", 5, 6)],
    "cols": [("passD", "Passes", 1, "left"),
             ("lateD", "Late ask\nminus\nopening", 12, "right"),
             ("reported", "Reported\nseat 5", 1, "left"),
             ("agreed", "Agreed\nwith a\npeer", 1, "left"),
             ("rejected", "Rejected a\nproposal", 1, "left"),
             ("agreedE", "Agreed\nwith a\npeer", 1, "left")],
    "cells": cells_5x5,
}

# ------------------------------------------------------------------------------------------- layout (inches)
X_LABEL = 0.26            # left edge of the model names (the swatch sits left of it)
X0 = 1.30                 # left edge of the first column
CW = 0.83                 # column width
GAP = 0.10                # gap before the last column of each panel (a new design or arm)
RH = 0.44                 # row height
H_GROUP, H_SUB, H_HEAD = 0.30, 0.44, 0.64


def col_x(j):
    return X0 + j * CW + (GAP if j == 5 else 0.0)


def draw_panel(ax, spec, letter, top):
    y = top
    ax.text(0.02, y, letter, fontsize=16, fontweight="bold", va="top", ha="left")
    for text, a, b in spec["groups"]:
        x0, x1 = col_x(a), col_x(b - 1) + CW
        ax.text((x0 + x1) / 2, y + 0.02, text, fontsize=14, fontweight="bold", ha="center", va="top")
        ax.plot([x0 + 0.03, x1 - 0.03], [y + H_GROUP - 0.02] * 2, color=style.GRAY, lw=0.8)
    y += H_GROUP
    for text, a, b in spec["subgroups"]:
        x0, x1 = col_x(a), col_x(b - 1) + CW
        ax.text((x0 + x1) / 2, y + H_SUB / 2, text, fontsize=12, ha="center", va="center", linespacing=1.0,
                color="#333333", style="italic")
    y += H_SUB
    for j, (_, head, _, _) in enumerate(spec["cols"]):
        ax.text(col_x(j) + CW / 2, y + H_HEAD - 0.04, head, fontsize=12, ha="center", va="bottom", linespacing=1.0)
    y += H_HEAD
    rows = []
    for i, model in enumerate(L.MODELS):
        cells = spec["cells"](model)
        yr = y + i * RH
        ax.add_patch(Rectangle((X_LABEL - 0.20, yr + RH / 2 - 0.06), 0.12, 0.12, facecolor=style.COLOR[model],
                               edgecolor="none"))
        ax.text(X_LABEL, yr + RH / 2, LABEL[model], fontsize=12, ha="left", va="center", linespacing=1.0)
        if not cells:                                     # the model was not run in this design at all
            x0, x1 = col_x(0) + 0.03, col_x(5) + CW - 0.03
            ax.add_patch(Rectangle((x0, yr + 0.03), x1 - x0, RH - 0.06, facecolor="white", edgecolor="#DDDDDD",
                                   lw=0.6))
            ax.text((x0 + x1) / 2, yr + RH / 2, "not run in this design", fontsize=12, ha="center", va="center",
                    color="#888888", style="italic")
            continue
        for j, (key, head, scale, anchor) in enumerate(spec["cols"]):
            x = col_x(j)
            c = cells.get(key)
            inner = (x + 0.03, yr + 0.03, CW - 0.06, RH - 0.06)
            if c is None:
                ax.add_patch(Rectangle(inner[:2], inner[2], inner[3], facecolor="white", edgecolor="#DDDDDD", lw=0.6))
                continue
            ax.add_patch(Rectangle(inner[:2], inner[2], inner[3], facecolor=style.tint(style.COLOR[model], 0.93),
                                   edgecolor=style.LIGHT, lw=0.6))
            frac = max(0.0, min(1.0, abs(c["value"]) / scale)) if anchor == "right" else \
                max(0.0, min(1.0, c["value"] / scale))
            bw = frac * inner[2]
            bx = inner[0] + inner[2] - bw if anchor == "right" else inner[0]
            ax.add_patch(Rectangle((bx, inner[1]), bw, inner[3], facecolor=style.tint(style.COLOR[model], 0.55),
                                   edgecolor="none"))
            ax.text(x + CW / 2, yr + RH / 2 - 0.012, c["top"], fontsize=12, fontweight="bold", ha="center",
                    va="bottom")
            ax.text(x + CW / 2, yr + RH / 2 + 0.012, c["sub"], fontsize=12, ha="center", va="top", color="#444444")
            rows.append({"panel": letter, "model": model, "column": key,
                         "header": " ".join(head.split()), **{k: c.get(k) for k in ("value", "top", "sub", "k", "n")}})
    return y + len(L.MODELS) * RH, rows


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    style.setup()
    top_a = 0.06
    height = top_a + 2 * (H_GROUP + H_SUB + H_HEAD + len(L.MODELS) * RH) + 0.30 + 0.08
    fig = plt.figure(figsize=(style.SLOT_IN, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, style.SLOT_IN)
    ax.set_ylim(height, 0)
    ax.axis("off")
    end_a, rows_a = draw_panel(ax, PANEL_A, "a", top_a)
    _, rows_b = draw_panel(ax, PANEL_B, "b", end_a + 0.30)
    L.save(fig, L.MS / "report" / "figures" / "fig5_model_profiles.png")
    L.S5DATA.mkdir(parents=True, exist_ok=True)
    rows = rows_a + rows_b
    with open(L.S5DATA / "fig5_cells.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['panel']} {r['model']:7s} {r['column']:9s} {r['top']:>7s}  {r['sub']}")


if __name__ == "__main__":
    main()
