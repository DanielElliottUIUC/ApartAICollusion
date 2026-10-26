"""Writes the derived tables of this section into report_ms/supplement/data/s44/ from experiments/runs/.

  runs.csv         one row per market (81): folder, phase, seller, buyer, messaging, prohibition notice, opening,
                   seed, joint criterion, private-message total, mean ask by hour (avg_seller_asks_by_round),
                   late ask (hours 11 to 15) and the first hour that holds the market's highest mean ask
  seller_asks.csv  every seller's posted ask by hour for the 18 low-anchor and control markets
  dms.csv          every private seller-to-seller message of those 18 markets, with a cartel-word flag
Run from anywhere: python report_ms/supplement/scripts/S44/build_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import s44lib as L  # noqa: E402

LOW_PHASES = {"frontier_lowanchor", "A_lowanchor", "A_agycontrol"}


def main():
    L.DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = L.catalog()
    asks = df[L.ASK_COLS].to_numpy()
    df["max_hour"] = asks.argmax(axis=1) + 1
    df.to_csv(L.DATA_DIR / "runs.csv", index=False)

    sa, dm = [], []
    for folder in df[df["phase"].isin(LOW_PHASES)]["folder"]:
        rec = L.run(folder)
        for h in L.HOURS:
            for s, a in sorted(rec[h]["asks"].items()):
                sa.append({"folder": folder, "hour": h, "seller": s, "ask": a})
            for d in rec[h]["dms"]:
                dm.append({"folder": folder, "hour": h, "sender": d["sender"], "recipient": d["recipient"],
                           "cartel_word": bool(L.CARTEL_RE.search(d["text"])), "text": d["text"]})
    pd.DataFrame(sa).to_csv(L.DATA_DIR / "seller_asks.csv", index=False)
    dms = pd.DataFrame(dm)
    dms.to_csv(L.DATA_DIR / "dms.csv", index=False)
    # the per-run private-message totals of collusion_metrics.json must equal the DMs read from unified.log
    n = dms.groupby("folder").size()
    low = df[df["phase"].isin(LOW_PHASES)].set_index("folder")["dms"]
    if not (n.reindex(low.index, fill_value=0) == low).all():
        raise ValueError("dm_summary totals and unified.log DMs disagree")
    print(f"runs.csv {len(df)} markets; seller_asks.csv {len(sa)} rows; dms.csv {len(dm)} messages")


if __name__ == "__main__":
    main()
