# Figure review for the final report, Oct 26, 3:30 AM CT

From D.E.'s side, for M.S. and his agent. Please check it and reply on this PR or by email.

## The files

- **`report_v2_60c34d4.pdf`**: the report as of commit 60c34d4 on report-v2 (PR #45), rendered with `scripts/render_report.py`. The body is 8 pages.
- **`figure_review_sheet.pdf`**: 14 figures from the review, one per page, each with the reviewers' verdict, score and reasons. It is compressed. The full-resolution figures are on the source branches.

## How the review was done

Five reviewers read all 91 candidate figures: 21 of ours, 9 of M.S.'s main figures and 61 of his supplement figures. For each figure they recorded:

- what it shows;
- which claim in the report it supports;
- whether it is legible at the 6.5-inch print width, with all text at 8 pt or more;
- what it duplicates;
- body, appendix or cut.

A sixth agent then made the allocation, and Daniel reviewed the borderline cases on the sheet.

## The body, five figures

1. **Market and threat model**: M.S.'s diag1_market, redrawn at print size.
   - The $90 label becomes "index zero".
   - The header becomes "Prompt notice, by arm".
   - "report a seller" replaces the code name.
2. **The ten arms grid.**
3. **Every arm-D seller-episode** (report and pretend).
4. **The offer**: M.S.'s fig1_offer with the GPT-4.1 rows, redrawn.
   - Panel b is now hand-coded rather than judge labels. Its columns are reported, wrote to seat 5 in support, and declined. Its rows are Gemini at $96 and at $99, GPT-4.1 at $96, under the precedent and at $99, and Haiku. The judge's echo label could not show GPT-4.1's support, because GPT-4.1 Base also scores 12 of 12 on it.
   - Panel a adds a "suspects a test (judge)" column, so the precedent result is in the body.
5. **Talk against price by arm**: M.S.'s fig2_warning. The caption now explains the open markers above 0.5.

## The appendix, and Daniel's verdicts on the sheet

| Sheet # | Figure | Daniel | Plan |
|---|---|---|---|
| 1 | Arms grid (body) | Agrees | Keep in the body |
| 2 | Figure 4 redraw (body) | Agrees | Redraw as above |
| 3 | First-report timing by arm (M.S. S41_02, panel a) | Agrees | Add to D.1 |
| 4 | Where the offer sat against each family's asks (M.S. S41_05) | Agrees | Add to D.2 |
| 5 | Two runs, talk against price (M.S. S43_02) | Agrees | Add to D.4 |
| 6 | Opening price, two panels (M.S. fig4_opening_price) | Not bad | Keep in D.5 |
| 7 | Talk against price, 110 markets (M.S. fig3_talk_vs_price) | Illegible as printed | Redraw full width at 8 pt or more, or drop |
| 8 | Suspicion by notice text (M.S. S42_09) | Uninformative | Cut; Figure 4a carries it |
| 9 | Design timeline | Not bad, but a lot | Crop to the seat-5 price panel only |
| 10 | Hour-3 noise floor | Legible, not that interesting | Keep in D.1 only because the text cites it |
| 11 | Peak hour of the mean ask (M.S. S44_05) | Legible, not that interesting | Cut |
| 12 | Plea 2x2 (M.S. S41_07) | Kind of illegible | Cut |
| 13 | Quote wall (M.S. S44_08) | Illegible | Cut |
| 14 | Opening book (M.S. S3_02) | Panel b very interesting; panel a illegible | Add panel b to the appendix: hour-1 asks by seller model, before any message is read |

Panel b of S3_02 shows that Sol and Gemini start at $95.80 or above, while many Luna, Grok and Haiku sellers are already at $91 or below in hour 1. The split between models that keep the opening and models that cut it exists before any communication.

All other figures are cut. Most repeat a body figure or table. The rest show outcomes the report does not claim (profit, dispersion, the Bertrand matrix), or single-market stories that the quotes table already carries.

## What we would like from you

1. **Check that your figures are represented correctly.** The adapted print scripts are in `scripts/figures/ms/` on report-v2, with credit in each header.
2. **Sheet items 7 and 14.** If you can quickly produce print-size versions (6.5 in wide, all text at 8 pt or more), push them to a branch:
   - item 7, talk against price, legible at full width;
   - item 14, panel b of S3_02 alone.

   We will redraw them ourselves if we have not heard from you by about 4:00 AM CT.
3. **Your wording pass** on report-v2, as agreed: wording only, numbers frozen.
