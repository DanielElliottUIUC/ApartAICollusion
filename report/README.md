# report/

Write-up assets for the Apart AI Collusion Research Sprint submission.

| Path | What |
|---|---|
| `REPORT.md` | Report skeleton, section order of the official Apart template. `TODO(results)` marks Sunday's numbers, `TODO(verify)` marks unchecked citations or facts, `TODO(confirm)` marks choices for Daniel. |
| `figures/` | Figures and the outcome table, generated from `results/`. Expected: `fig_index_by_arm.svg`, `tab_outcomes_by_arm.csv`. |

The official template is a Google Docs copy link (`mert_sprint/report/TEMPLATE.md`), not LaTeX. Reference exports from Oct 22 are in `mert_sprint/report/template/` (`.docx` and `.pdf`). The Guidelines tab says to always use a fresh copy of the linked template, since an older one may come with an acceptance email.

## Rendering REPORT.md into the template PDF

Nothing in this repo renders the PDF for you. Pick one route. Route 1 is the safer one.

**Route 1: paste into a fresh Google Docs copy (recommended).**
1. Open the template copy link in `mert_sprint/report/TEMPLATE.md` and make a copy.
2. Replace the title, authors and affiliations, and the abstract (with the guidance text and yellow info box deleted).
3. For each section, replace the template's italic guidance with the matching section of `REPORT.md`. Sections keep the template's numbering: 1 Introduction, 2 Related Work, 3 Methods, 4 Results, 5 Discussion and Limitations (Limitations, Future Work), 6 Conclusion, then Code and Data, Author Contributions, References, Appendix, LLM Usage Statement.
4. Insert figures from `figures/` (export SVG to PNG at a legible size) and turn `tab_outcomes_by_arm.csv` into a table. Number and caption every figure and table.
5. Add Appendix A (Limitations and Dual-Use / Ethical Considerations), B (Provenance) and C (Frozen texts) after References. The template has no dual-use appendix; the Guidelines tab requires one.
6. File, Download, PDF.

**Route 2: pandoc to .docx, then merge.** Needs pandoc (not installed on Daniel's machine as of Oct 24; `winget install JohnMacFarlane.Pandoc`).
```bash
pandoc report/REPORT.md -o report/REPORT_draft.docx --from gfm
```
Then copy the body into the template `.docx` and fix styles by hand. HTML comments and `TODO(...)` text come through as visible text, so strip them first (`grep -v` or the check below).

**Route 3: edit the template `.docx` directly** (`mert_sprint/report/template/apart_report_template_export.docx`). Same content mapping as Route 1.

## Page-count check

Limit: **8 pages before References and Appendices.** The template says "4 pages"; the Guidelines tab says most strong projects are 4 to 8, cap 8.

1. Export to PDF.
2. The first page of References is the end of the body. Body pages = that page number minus 1 (if References start mid-page, count it as the body's last page, and check that nothing but References follows on it).
3. Sanity estimate before rendering: the body (Abstract through Conclusion) is about 4,100 words in this skeleton with tables, at roughly 500 words per template page. Figures and tables take about a page. Expect 7 to 8 pages. If over, cut in this order: §2 paragraphs K8/K9, Table 4, the Discussion bullets, §3.1 bullets.

Word-count checks (PowerShell from the repo root):
```powershell
# abstract: paste into a tool, or after editing run:
(Get-Content report\REPORT.md -Raw) -replace '(?s)<!--.*?-->','' | Out-String | Measure-Object -Word
```

## Pre-submission checklist

From `mert_sprint/report/TEMPLATE.md` (Guidelines tab), plus the checks for this report:

- [ ] Report PDF uses the template.
- [ ] 8 pages or fewer before references and appendices.
- [ ] Abstract is 150 to 250 words.
- [ ] Authors and affiliations listed.
- [ ] Limitations and Dual-Use / Ethical Considerations appendix included.
- [ ] All links work.
- [ ] Preexisting code (if any) marked in README and report.
- [ ] Every template guidance paragraph and the yellow info box deleted.
- [ ] No `TODO(...)` text, HTML comments or `?` citation markers left: `grep -n "TODO\|<!--\|\]\|?\]" report/REPORT.md` finds nothing unintended.
- [ ] **Every citation checked against its primary page.** All items in REPORT.md's `TODO(verify)` table resolved or the sentence cut. The Honeypots report has no identified authors; decide how to cite it.
- [ ] Every number in the text and tables traced to a run in `results/`; the exact title matches the submission form (resubmission needs the identical title).
- [ ] Frozen texts in Appendix C match `configs/texts/` byte for byte, with hashes.
- [ ] The README no longer says Haiku buyers or randomized seat order, and its arm table matches what ran.
- [ ] LLM Usage Statement filled in honestly; Author Contributions agreed with Mert.
- [ ] The repo is public if the Code and Data link points to it.
