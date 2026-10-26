"""Sheet item 7, print size: M.S.'s Figure 3, private talk between sellers against price (110 markets).

Runs the original script report_ms/scripts/figures/make_fig3_talk_vs_price.py unchanged (same data:
report_ms/data/ms_runs.csv and report_ms/data/daniel/ copies of D.E.'s CSVs; same encoding), and only
redirects its output here as png and vector pdf at exactly 6.5 in wide, 300 dpi, after checking that no
text is below 8 pt. Output: item7_talk_vs_price_print.{png,pdf}
"""
import _common  # noqa: F401  (sets up paths)
import style
import make_fig3_talk_vs_price as fig3

style.save = lambda fig, name: _common.save(fig, "item7_talk_vs_price_print")
fig3.style.save = style.save

if __name__ == "__main__":
    fig3.main()
