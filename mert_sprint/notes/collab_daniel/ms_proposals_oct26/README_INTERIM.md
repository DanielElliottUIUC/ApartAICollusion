# M.S.'s proposed changes to Report v2 (60c34d4)

Status at 04:02 CT, Mon Oct 26. Every change is a proposal, and Daniel decides.

## Start here

- `MS_all_changes_tracked.pdf` shows every proposed change in one document, against report-v2 at 60c34d4. Removed words are
  red and struck, and added words are blue.
- `MS_final_all_sets_applied.pdf` is the report with every change applied, with no tracking (32 pages in total).
- `MS_ALL_changes.md` lists every change with its reason.
- `MS_ALL.diff` takes `report/REPORT.md` at 60c34d4 to the final text in one `git apply`.

## Length: one change to drop if you need 8 pages

With all changes applied, the body is **9 pages**. The Conclusion and the short Code and Data section fall on page 9.

The longer Discussion and Conclusion cause this: **C125** (Discussion, 427 words) and **C126** (Conclusion). If you drop those
two and keep the shorter Discussion and Conclusion of C114 and C115, the body is **8 pages**. Every other change fits within
8 pages.

## What the sets contain

1. **Set 1 (C1 to C112, 77 changes).**
   - Reader fixes: "we" throughout, and no author initials outside the title block.
   - The any-report plea test everywhere (39 of 40 against 19 of 40, p = 0.002).
   - Consistency fixes and small phrasing.
   - Mert's rulings: Table 1, Tables D2a and D2b, and Author Contributions removed; Appendix B, Code and Data and section 3.3
     shortened (the preexisting-code marking and the prereg commit are kept); Related Work as one paragraph.
2. **Set 2 (C92 to C111).**
   - The results paragraphs as coherent paragraphs, giving purpose, finding and meaning with the same numbers.
   - Eight tighter captions.
   - The five body figures redrawn for clarity. The images and script diffs are in `S2_figures/`.
3. **Set 3 (C113 to C115).** The title with "collusion", and the rewritten Discussion and Conclusion.
4. **Set 4 (C116 to C127).**
   - Headings that state each section's finding, and the first paragraph of each section.
   - The longer Discussion and Conclusion (C125 and C126).
   - The quotes appendix: each quote verbatim, the run named in plain words, and what prices did in that run.

`MS_S1_tracked.pdf` to `MS_S4_tracked.pdf` show each set in place, on the text with the earlier sets applied.
`MS_S1.diff` to `MS_S4.diff` apply in that order.
