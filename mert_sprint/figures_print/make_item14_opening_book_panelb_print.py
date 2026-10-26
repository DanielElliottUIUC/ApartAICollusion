"""Sheet item 14, print size: panel b of M.S.'s Figure S3.2 alone, the opening book.

Each LLM seller's hour-1 ask, by seller model and opening price. Messages sent in hour 1 are read only from
hour 2, so these asks precede any seller-to-seller communication. Grey bands: the uniform support the harness
draws the seeded asks from (opening +/- $1.25).
Reuses load() and panel_b() of report_ms/supplement/scripts/S3/make_S3_02_opening_book.py unchanged
(data: report_ms/supplement/data/S3/sellers_h1.csv, runs.csv, books.csv), on a standalone 6.5 in canvas.
Prints the per-group statistics used to check the text's description. Output: item14_opening_book_panelb_print.{png,pdf}
"""
import _common
import matplotlib.pyplot as plt
import pandas as pd

import s3lib
import make_S3_02_opening_book as s302


def main():
    s3lib.setup()
    _, _, _, h1 = s302.load()
    W, H = _common.WIDTH_IN, 3.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.80 / W, 0.42 / H, (W - 0.80 - 0.10) / W, (H - 0.42 - 0.40) / H])
    st = s302.panel_b(ax, h1)
    pd.set_option("display.width", 200)
    print(st.round(2).to_string(index=False))
    _common.save(fig, "item14_opening_book_panelb_print")


if __name__ == "__main__":
    main()
