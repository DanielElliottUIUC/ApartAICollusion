"""S4.5.7: Sol, silent and high. GPT-5.6 Sol sellers with no messaging channel hold $97.50 with private
game-theory reasoning; Sol sellers with a channel write "independently" in public and sit about $2 lower.

Runs (both GPT-5.6 Sol sellers, Claude Haiku 5.5 buyers, default opening):
  shard2/frontier/..._gpt56sol_nocomms_haikuB-seed0   messaging off
  box/frontier/..._gpt56sol_comms_haikuB-seed2        messaging on
Lines: mean of the four posted asks by hour (unified.log). Call-outs: quotes.py entries s0_kai_h11 (on the
messaging-off line), sc2_mia_h1 and sc2_amir_h8 (on the messaging-on line).
Output: supplement/figures/S45/S45_07_sol_silent.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import S0, SC2, QUOTES as Q


def identical_hours(rec):
    return sum(1 for h in L.HOURS if len(rec[h]["asks"]) == 4 and len(set(rec[h]["asks"].values())) == 1)


def main():
    L.setup()
    c = style.COLOR["sol"]
    off, on = L.run(S0), L.run(SC2)
    m_off, m_on = L.mean_ask_path(off), L.mean_ask_path(on)
    n_msgs = sum(len(off[h]["public"]) + len(off[h]["dms"]) for h in L.HOURS)
    n_dms_on = sum(len(on[h]["dms"]) for h in L.HOURS)
    print(f"messaging off: {n_msgs} messages; identical asks in {identical_hours(off)} of 15 hours")
    print(f"messaging on: {n_dms_on} private messages; identical asks in {identical_hours(on)} of 15 hours")
    pub = [t for h in L.HOURS for t in on[h]["public"].values()]
    print(f"messaging on: {sum('independently' in t for t in pub)} of {len(pub)} public messages say 'independently'")

    fig = plt.figure(figsize=(style.SLOT_IN, 5.5))
    ax = fig.add_axes([0.115, 0.19, 0.865, 0.725])
    style.ref_lines(ax)
    ax.plot(L.HOURS, m_off, color=c, lw=2.8, zorder=4)
    ax.plot(L.HOURS, m_on, color=c, lw=2.2, ls=style.MSG_LS["off"], zorder=3)
    L.hour_axis(ax)
    ax.set_ylim(92.5, 101.0)
    ax.set_yticks([94, 96, 98, 100])
    ax.set_ylabel("Mean ask ($)")
    ax.set_title("GPT-5.6 Sol sellers, default opening", pad=8)

    ax.text(1.0, 97.85, f"messaging off, {n_msgs} messages\n{L.verdict(S0)}", color=c, fontsize=12,
            ha="left", va="bottom", fontweight="bold")
    ax.text(15.4, 96.05, f"messaging on\n{L.verdict(SC2)}", color=c, fontsize=12, ha="right", va="bottom")

    L.callout(ax, Q["s0_kai_h11"], (11, m_off[10]), (15.4, 98.65), 30, c, ha="right", rel=(0.45, 0.0),
              header_side="right")
    L.callout(ax, Q["sc2_mia_h1"], (1, m_on[0]), (1.6, 94.6), 26, c, va="top", rel=(0.0, 1.0),
              header_below=True)
    L.callout(ax, Q["sc2_amir_h8"], (8, m_on[7]), (9.0, 94.6), 24, c, va="top", rel=(0.0, 1.0),
              header_below=True)
    L.channel_key(fig, 0.035, channels=("public", "note"), color=c)
    L.save(fig, "S45_07_sol_silent.png")


if __name__ == "__main__":
    main()
