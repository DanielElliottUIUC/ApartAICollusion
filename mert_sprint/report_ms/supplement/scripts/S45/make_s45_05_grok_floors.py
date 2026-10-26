"""S4.5.5: Grok's floor ratchet. The floors the sellers named in public, hour by hour, on top of the asks they
posted. The named floor starts at 90 and steps down with the asks to 86.47.

Run: box/frontier/..._grok47_comms_haikuB-seed1 (Grok 4.7 sellers, Claude Haiku 5.5 buyers, default opening,
messaging on). Lines: each seller's posted ask by hour (unified.log). Marks: every number a seller's public
message gives as a floor ("at or above X" or "hold a X floor"), at the hour of the message.
Call-outs: quotes.py entries k1_zoe_h1, k1_zoe_h2, k1_tara_h10.
Output: supplement/figures/S45/S45_05_grok_floors.png
"""
import re

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import s45lib as L
import style
from quotes import K1, QUOTES as Q

FLOOR = re.compile(r"at or above (\d+(?:\.\d+)?)|hold a (\d+(?:\.\d+)?) floor")
SELLERS = ["Amir", "Maya", "Tara", "Zoe"]


def named_floors(rec):
    """[(hour, seller, floor)] for every floor named in a public message."""
    out = []
    for h in L.HOURS:
        for s in SELLERS:
            for m in FLOOR.finditer(rec[h]["public"].get(f"Seller {s}", "")):
                out.append((h, s, float(m.group(1) or m.group(2))))
    return out


def main():
    L.setup()
    rec = L.run(K1)
    c = style.COLOR["grok"]
    dark = "#8E3F6E"                       # Grok pink, darkened for the highlighted seller and the text
    ask = {s: L.ask_path(rec, f"Seller {s}") for s in SELLERS}
    floors = named_floors(rec)
    same = sum(1 for h, s, f in floors if abs(f - ask[s][h - 1]) < 0.005)
    print(f"named floors: {len(floors)}; equal to the seller's own ask that hour: {same}")
    late = [(h, s, f) for h, s, f in floors if h >= 5]
    late_same = sum(1 for h, s, f in late if abs(f - ask[s][h - 1]) < 0.005)
    print(f"from hour 5: {len(late)} named floors, {late_same} equal to the seller's own ask")

    fig = plt.figure(figsize=(style.SLOT_IN, 5.9))
    ax = fig.add_axes([0.115, 0.2, 0.865, 0.72])
    style.ref_lines(ax)
    for s in SELLERS:
        ax.plot(L.HOURS, ask[s], color=dark if s == "Zoe" else style.tint(c, 0.35), lw=2.6 if s == "Zoe" else 1.6,
                zorder=4 if s == "Zoe" else 3)
    ax.plot([h for h, s, f in floors], [f for h, s, f in floors], ls="none", marker="_", ms=13, mew=2.4,
            color="black", zorder=5)
    L.hour_axis(ax)
    ax.set_ylim(80.4, 93.4)
    ax.set_yticks([82, 84, 86, 88, 90, 92])
    ax.set_ylabel("Price ($)")
    ax.set_title("Grok 4.7 sellers, default opening", pad=8)

    L.callout(ax, Q["k1_zoe_h1"], (1, ask["Zoe"][0]), (1.6, 90.75), 30, dark, rel=(0.0, 0.0))
    L.callout(ax, Q["k1_zoe_h2"], (2, ask["Zoe"][1]), (3.3, 87.6), 22, dark, rel=(0.0, 0.75))
    L.callout(ax, Q["k1_tara_h10"], (10, ask["Tara"][9]), (15.4, 87.45), 21, dark, ha="right", rel=(0.05, 0.0),
              header_side="right")
    h0, p0 = L.settle_hour(rec)
    ax.text(15.4, 85.75, f"Hours {h0} to 15: all four asks ${p0:.2f}\nCriterion {L.verdict(K1)}",
            fontsize=12, ha="right", va="top")

    handles = [Line2D([], [], color=dark, lw=2.6), Line2D([], [], color=style.tint(c, 0.35), lw=1.6),
               Line2D([], [], ls="none", marker="_", ms=13, mew=2.4, color="black")]
    ax.legend(handles, ["Zoe's ask", "Amir's, Maya's, Tara's asks", "floor named in a public message"],
              loc="lower right", bbox_to_anchor=(1.0, 0.0), frameon=False, handlelength=1.8, borderaxespad=0.3)
    L.channel_key(fig, 0.035, channels=("public",), color=dark)
    L.save(fig, "S45_05_grok_floors.png")


if __name__ == "__main__":
    main()
