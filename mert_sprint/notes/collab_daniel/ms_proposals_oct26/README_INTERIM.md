# M.S.'s proposed changes to Report v2 (1f951ac)

Status at 04:16 CT (rebased on Daniel's 1f951ac of 04:05), Mon Oct 26. Every change is a proposal, and Daniel decides.

## Start here

- `MS_all_changes_tracked.pdf` shows every proposed change in one document, against report-v2 at 1f951ac. Removed words are
  red and struck, and added words are blue.
- `MS_final_all_sets_applied.pdf` is the report with every change applied, with no tracking (40 pages in total).
- `MS_ALL_changes.md` lists every change with its reason.
- `MS_ALL.diff` takes `report/REPORT.md` at 1f951ac to the final text in one `git apply`.

## Length: one change to drop if you need 8 pages

With all changes applied, the body is **9 pages**. The Conclusion and the short Code and Data section fall on page 9.

The longer Discussion and Conclusion cause this: **C124** (Discussion) and **C125** (Conclusion). If you drop those
two and keep the shorter Discussion and Conclusion of C114 and C115, the body is **8 pages**. Every other change fits within
8 pages.

## What the sets contain

1. **Set 1 (72 changes).**
   - Reader fixes: "we" throughout, and no author initials outside the title block.
   - The any-report plea test everywhere (39 of 40 against 19 of 40, p = 0.002).
   - Consistency fixes and small phrasing.
   - Mert's rulings: Table 1, Tables D2a and D2b, and Author Contributions removed; Appendix B, Code and Data and section 3.3
     shortened (the preexisting-code marking and the prereg commit are kept); Related Work as one paragraph.
2. **Set 2 (C92 to C100; 11 of the 20 earlier rewrites no longer matched your 1f951ac text and are left out).**
   - Results paragraphs and captions rewritten as coherent paragraphs, giving purpose, finding and meaning with the same
     numbers, wherever your text still matched.
   - Your figure pass in f763a31 and 1f951ac is kept. Our earlier redraws of the five body figures are in `S2_figures/` as optional suggestions only.
3. **Set 3 (C113 to C115).** The title with "collusion", and the rewritten Discussion and Conclusion.
4. **Set 4 (C116 to C125).**
   - Headings that state each section's finding, and the first paragraph of each section.
   - The longer Discussion and Conclusion (C124 and C125).
   - The quotes appendix is left as you redesigned it in 1f951ac.

`MS_S1_tracked.pdf` to `MS_S4_tracked.pdf` show each set in place, on the text with the earlier sets applied.
`MS_S1.diff` to `MS_S4.diff` apply in that order.

## What changed from the earlier bundle (desk v4, on 60c34d4) to this one (desk v5, on 1f951ac)

- The base moved to Daniel's 1f951ac, which includes his figure allocation (f763a31), print-size appendix figures, captions
  kept with figures, and his own redesigned quotes table.
- The bundle now marks every change from all sets in one document (`MS_all_changes_tracked.pdf`). The earlier v4 marked only
  Set 3 part 1.
- New in this bundle: Set 4, which adds headings that state each section's finding, the first paragraph of each section, and
  the longer Discussion and Conclusion (C124 and C125).
- Left out because Daniel rewrote that text after 60c34d4: 11 Set 2 rewrites, 5 small Set 1 fixes, our redrawn body figures
  (his are kept, and ours stay in `S2_figures/`), and our quotes-table redesign (his is kept).
- Length: the body is 9 pages with C124 and C125, and 8 pages without them.
