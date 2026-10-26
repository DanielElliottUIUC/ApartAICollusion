# Print-size figures for the figure review (PR #51, sheet items 7 and 14)

Both figures are exactly 6.5 in wide (no tight cropping), 300 dpi, as png and vector pdf. Every text item is
12 pt or more as printed at that width: tick labels, legend, annotations and column names 12 pt, axis labels
14 pt. The scripts check the width and refuse any text below 8 pt or outside the page. Run from this folder:
`python3 make_item7_talk_vs_price_print.py` and `python3 make_item14_opening_book_panelb_print.py`.
They import M.S.'s original scripts in `../report_ms/` read-only and change no data or encoding.

## Item 7: `item7_talk_vs_price_print.{png,pdf}`, 6.5 x 4.86 in

M.S.'s Figure 3, private talk between sellers against price, 110 markets. Same data and encoding as
`report_ms/scripts/figures/make_fig3_talk_vs_price.py` (data: `report_ms/data/ms_runs.csv` and the copies of
D.E.'s CSVs in `report_ms/data/daniel/`). x: private messages between sellers per market, with the 68
zero-message markets in a strip on the left. y: last-third ask index. Marker by seller model, filled when the
market meets the joint criterion, black ring when it opened at $90.
Script: `make_item7_talk_vs_price_print.py`. The original was already laid out at 6.5 in with 12 pt text;
the sheet's compressed copy is likely what read as illegible, so the pdf here is vector.

## Item 14: `item14_opening_book_panelb_print.{png,pdf}`, 6.5 x 3.6 in

Panel b of M.S.'s Figure S3.2 alone: each LLM seller's hour-1 ask by seller model and opening, before any
message is read (hour-1 messages are read only from hour 2). Grey bands: the uniform support of the seeded asks
(opening +/- $1.25). Same `load()` and `panel_b()` as
`report_ms/supplement/scripts/S3/make_S3_02_opening_book.py` (data: `report_ms/supplement/data/S3/sellers_h1.csv`,
`runs.csv`, `books.csv`). Script: `make_item14_opening_book_panelb_print.py`, which prints the counts below.

Hour-1 asks in markets opened at $97.50:

| Seller | Sellers | Runs | Median | At or above $95.80 | At or below $91 |
|---|---|---|---|---|---|
| Sol | 96 | 24 | $96.34 | 96 | 0 |
| Gemini | 60 | 15 | $96.22 | 60 | 0 |
| Luna | 48 | 12 | $90.00 | 23 | 25 |
| Grok | 48 | 12 | $89.90 | 8 | 34 |
| Haiku | 36 | 9 | $90.00 | 4 | 21 |

In markets opened at $90, every Sol (48), Gemini (24) and Luna (12) hour-1 ask is at or below $91, as the
opening sets.
