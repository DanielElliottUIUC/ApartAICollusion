"""Figure S3.5: when sellers use the two channels, hour by hour, in every messaging run of ours.

One row per run with messaging on (every messaging-on run in data/S3/runs.csv). Each cell is the number of messages
sellers sent in that hour, from unified.log, or auction_results.md for the GGGG seed 0 run (data/S3/hours.csv): (a) private messages (seller_dms; the cap is 4 sellers x 2 = 8 per hour), (b) public messages
(non-empty seller_messages; the cap is 4 per hour). Cell color is the seller model's color, darker for more
messages; light gray cells have none. A message sent in hour h is delivered at the start of hour h + 1, so hour-15 messages are never read.
The rule-notice rows carry D.E.'s prohibition notice ("Coordinating prices with other sellers is prohibited").
Output: supplement/figures/S3/S3_05_message_timing.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import s3lib  # noqa: E402

C = s3lib.COLOR
CAP = {"private": 8, "public": 4}
ZERO = (0.945, 0.945, 0.945)          # a cell with no messages: light gray, so silent runs stay visible


def groups(r):
    on = r[(r["messaging"] == "on") & (r["hours_logged"] == 15)]
    sel = [
        ("Grok, frontier", on[(on.block == "frontier") & (on.seller == "grok")], 6),
        ("Gemini, $97.50", on[on.block == "A_agycontrol"], 3),
        ("Gemini, $90", on[on.block == "A_lowanchor"], 3),
        ("Gemini, Haiku buyers", on[(on.block == "step_AB") & (on.seller == "gemini") & ~on.notice], 6),
        ("Gemini, rule notice", on[(on.block == "step_AB") & (on.seller == "gemini") & on.notice], 3),
        ("Sol, frontier", on[(on.block == "frontier") & (on.seller == "sol")], 6),
        ("Sol, 4.1-mini buyers", on[on.block == "frontier_b41"], 3),
        ("Sol, $90", on[(on.block == "frontier_lowanchor") & (on.seller == "sol")], 3),
        ("Luna, frontier", on[(on.block == "frontier") & (on.seller == "luna")], 6),
        ("Haiku sellers", on[(on.block == "step_AB") & (on.seller == "haiku")], 6),
    ]
    used = set()
    for name, g, n in sel:
        if len(g) != n:
            raise ValueError(f"{name}: {len(g)} runs, expected {n}")
        used.update(g.folder)
    if used != set(on.folder):
        raise ValueError(f"messaging runs not placed: {sorted(set(on.folder) - used)}")
    return [(name, g.sort_values(["tag", "buyer", "seed"])) for name, g, _ in sel]


def image(rows, hours, channel):
    img = np.ones((len(rows), 15, 3))
    for i, (folder, seller) in enumerate(rows):
        if folder is None:
            continue
        v = hours.loc[folder].sort_values("hour")[channel].to_numpy()
        if len(v) != 15:
            raise ValueError(f"{folder}: {len(v)} hours")
        for j, c in enumerate(v):
            t = min(c / CAP[channel], 1.0)
            img[i, j] = s3lib.tint(C[seller], 1 - 0.9 * t) if c > 0 else ZERO
    return img


def main():
    s3lib.setup()
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    hours = pd.read_csv(s3lib.S3DATA / "hours.csv").set_index("folder")
    gs = groups(r)
    rows, spans = [], []
    for name, g in gs:
        if rows:
            rows.append((None, None))             # one blank row between groups
        start = len(rows)
        rows.extend((f, s) for f, s in zip(g.folder, g.seller))
        spans.append((name, start, len(rows) - 1, g.seller.iloc[0]))
    row_in = 0.112
    fig_h = len(rows) * row_in + 1.72
    fig = plt.figure(figsize=(s3lib.SLOT_IN, fig_h))
    bot = 1.12 / fig_h
    hh = len(rows) * row_in / fig_h
    axa = fig.add_axes([2.12 / s3lib.SLOT_IN, bot, 1.95 / s3lib.SLOT_IN, hh])
    axb = fig.add_axes([4.38 / s3lib.SLOT_IN, bot, 1.95 / s3lib.SLOT_IN, hh])
    for ax, ch, title, letter in ((axa, "private", "Private", "a"), (axb, "public", "Public", "b")):
        ax.imshow(image(rows, hours, ch), aspect="auto", interpolation="nearest",
                  extent=(0.5, 15.5, len(rows) - 0.5, -0.5))
        for i, (f, _) in enumerate(rows):
            if f is None:
                ax.axhspan(i - 0.5, i + 0.5, color="white", zorder=2)
            elif i + 1 < len(rows) and rows[i + 1][0] is not None:
                ax.axhline(i + 0.5, color="white", lw=0.7, zorder=2)
        ax.set_xticks([1, 5, 10, 15])
        ax.set_yticks([])
        ax.set_xlabel("Hour")
        for sp in ("left", "top", "right"):
            ax.spines[sp].set_visible(False)
        ax.set_title(title, fontsize=16, loc="left", pad=6)
        s3lib.panel_letter(ax, letter, x=-0.03, y=1.0 + (6 / 72) / (len(rows) * row_in))  # level with the title
        ax.set_ylim(len(rows) - 0.5, -0.5)
    for name, a, b, seller in spans:
        axa.text(-0.6, (a + b) / 2, name, ha="right", va="center", fontsize=12, color=C[seller], clip_on=False)
    # Intensity keys under each panel: gray steps from 1 message to the cap.
    for ax, ch in ((axa, "private"), (axb, "public")):
        cap = CAP[ch]
        pos = ax.get_position()
        k = fig.add_axes([pos.x0, 0.3 / fig_h, pos.width * 0.62, 0.13 / fig_h])
        steps = np.arange(0, cap + 1)
        k.imshow([[s3lib.tint(s3lib.GRAY, 1 - 0.9 * min(s / cap, 1)) if s > 0 else ZERO for s in steps]],
                 aspect="auto", extent=(-0.5, cap + 0.5, 0, 1))
        k.set_yticks([])
        k.set_xticks([0, cap // 2, cap])
        k.tick_params(axis="x", length=2, pad=1)
        for sp in ("left", "top", "right"):
            k.spines[sp].set_visible(False)
        k.add_patch(plt.Rectangle((-0.5, 0), cap + 1, 1, fill=False, edgecolor=s3lib.LIGHT, lw=0.6))
        k.text(cap + 0.9, 0.5, "per hour", ha="left", va="center", fontsize=12)

    # Caption numbers
    on = r[(r["messaging"] == "on") & (r["hours_logged"] == 15)]
    h = hours.reset_index().merge(on[["folder", "seller", "block", "notice"]], on="folder")
    print(f"messaging runs shown: {on.folder.nunique()}")
    for name, g in gs:
        sub = h[h.folder.isin(g.folder)]
        mid = sub[(sub.hour >= 2) & (sub.hour <= 14)]
        print(f"{name:22s} runs {g.folder.nunique()}  runs with private msgs {int((g.private_messages > 0).sum())}  "
              f"private total {int(g.private_messages.sum())}  private/hour h2-14 {mid.private.mean():.2f}  "
              f"at cap h2-14 {(mid.private == 8).mean():.2f}  hour-15 private {sub[sub.hour == 15].private.mean():.2f}  "
              f"public/hour {sub.public.mean():.2f}  hour-15 public {sub[sub.hour == 15].public.mean():.2f}  "
              f"runs without public msgs {int((g.public_messages == 0).sum())}")
    print("Grok hour-15 private per run:", h[(h.seller == "grok") & (h.hour == 15)].private.tolist())
    s3lib.save(fig, "S3_05_message_timing.png")


if __name__ == "__main__":
    main()
