# Copied from Daniel Elliott's ApartAICollusion repository (scripts/render_report.py at origin/main b7cbccd).
# Credit: Daniel Elliott wrote this render pipeline. ROOT resolves to report_ms/, so it renders report_ms/report/REPORT.md.
# Changed by M.S. on 2026-10-25 for the print layout. The font-size patterns accept pandoc 3.1's `<w:sz w:val="24" />`,
# so body text is 11 pt. Figures embed at the full text width unless their image line sets a width. Table captions
# go above their tables, and tables and figures stay on one page with their captions.

"""Render report/REPORT.md to .docx and .pdf in the Apart template's page setup, and print the page count.

Why not the template .docx directly: Word refuses the Google-Docs-exported template as a pandoc reference
document ("file appears to be corrupted"). pandoc's own reference document, patched to Letter, 1-inch margins
and Arial 11 pt, renders identically to the template's body text. Paste the final text into the real template
at the end, or submit this output if the organisers accept it.

    python scripts/render_report.py                 # body (Abstract..Conclusion) and full report; prints pages
    python scripts/render_report.py --open          # also opens the body PDF

Needs: `pip install --user pypandoc_binary` (bundles pandoc) and Microsoft Word (page count + PDF export via COM).
HTML comments and the §2 TODO(verify) table are stripped; figure links are switched from .svg to .png.
Output: report/build/{body,full}.{md,docx,pdf} (gitignored).
"""

import argparse
import math
import pathlib
import re
import subprocess
import sys
import zipfile

import pypandoc

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "report" / "REPORT.md"
BUILD = ROOT / "report" / "build"
TEXT_WIDTH = "6.5in"  # Letter width minus the two 1-inch margins
PAGE_TEXT_HEIGHT_IN = 9.0  # Letter height minus the two 1-inch margins
CELL_CHARS_PER_IN = 11.0


def keep_lines(styles: str, style_id: str) -> str:
    """Add keepLines to one paragraph style, after keepNext as the OOXML element order requires."""
    m = re.search(rf'<w:style [^>]*w:styleId="{style_id}".*?</w:style>', styles, flags=re.S)
    style = m.group(0)
    if "<w:pPr>" in style:
        anchor = re.search(r"<w:keepNext\s*/>", style) or re.search(r"<w:pPr>", style)
        new = style[:anchor.end()] + "<w:keepLines/>" + style[anchor.end():]
    else:
        new = re.sub(r"(<w:basedOn [^>]*/>)", r"\1<w:pPr><w:keepLines/></w:pPr>", style, count=1)
    return styles[:m.start()] + new + styles[m.end():]


def table_height_in(tbl: str) -> float:
    """Estimated printed height of a table and its caption, in inches.

    Word sizes the columns to their content, so each row is taken to spread its text over the full 6.5 in, less
    0.15 in of cell margins per column, at CELL_CHARS_PER_IN characters per inch (Arial 9 pt with word wrap). The
    caption takes one line per 127 characters (Arial 11 pt across 6.5 in). Calibrated on Tables 1 to 3 of the
    2026-10-25 render: estimates 2.6, 8.0 and 9.7 in against 2.4, 8.0 and 10.5 in printed."""
    width = 6.5 - 0.15 * len(re.findall(r"<w:gridCol ", tbl))
    caption = re.search(r'<w:tblCaption w:val="([^"]*)"', tbl)
    height = math.ceil(len(caption.group(1) if caption else "") / 127) * 0.176 + 0.15
    for row in re.findall(r"<w:tr>.*?</w:tr>", tbl, flags=re.S):
        chars = len("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", row)))
        height += max(1, math.ceil(chars / (CELL_CHARS_PER_IN * width))) * 0.144 + 0.06
    return height


def keep_tables_together(docx: pathlib.Path) -> None:
    """No table row splits across pages. A table that fits on a page also keeps every row with the next, so Word
    keeps it whole with its caption; a longer table keeps only its caption, header and first row together."""
    with zipfile.ZipFile(docx) as z:
        items = {i.filename: (i, z.read(i.filename)) for i in z.infolist()}
    info, data = items["word/document.xml"]

    def table(m: re.Match) -> str:
        rows = re.findall(r"<w:tr>.*?</w:tr>", m.group(0), flags=re.S)
        kept = len(rows) - 1 if table_height_in(m.group(0)) <= PAGE_TEXT_HEIGHT_IN else 1
        out = m.group(0)
        for k, row in enumerate(rows):
            new = row.replace("<w:trPr>", "<w:trPr><w:cantSplit/>", 1) if "<w:trPr>" in row                 else row.replace("<w:tr>", "<w:tr><w:trPr><w:cantSplit/></w:trPr>", 1)
            if k < kept:
                new = re.sub(r"(<w:pPr>(?:<w:pStyle [^>]*/>)?)", r"\1<w:keepNext/>", new)
            out = out.replace(row, new, 1)
        return out

    doc = re.sub(r"<w:tbl>.*?</w:tbl>", table, data.decode("utf-8"), flags=re.S)
    items["word/document.xml"] = (info, doc.encode("utf-8"))
    tmp = docx.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for item, payload in items.values():
            out.writestr(item, payload)
    tmp.replace(docx)


def letter_reference() -> pathlib.Path:
    """pandoc's default reference.docx patched to Letter / 1in margins / Arial 11pt."""
    BUILD.mkdir(parents=True, exist_ok=True)
    default, ref = BUILD / "ref_default.docx", BUILD / "ref_letter.docx"
    subprocess.run([pypandoc.get_pandoc_path(), "-o", str(default), "--print-default-data-file", "reference.docx"], check=True)
    with zipfile.ZipFile(default) as src, zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/styles.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<w:rFonts [^/]*/>", '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial"/>', s)
                s = re.sub(r'(<w:docDefaults>.*?)<w:sz w:val="\d+"\s*/>', r'\1<w:sz w:val="22"/>', s, count=1, flags=re.S)
                s = re.sub(r'(<w:docDefaults>.*?)<w:szCs w:val="\d+"\s*/>', r'\1<w:szCs w:val="22"/>', s, count=1, flags=re.S)
                # A caption never splits across pages. Pandoc's styles already keep a figure with its caption
                # (Captioned Figure) and a table caption with its table (Table Caption).
                s = keep_lines(s, "ImageCaption")
                s = keep_lines(s, "TableCaption")
                # A figure narrower than the text width (one too tall for its page at full width) sits centred.
                s = re.sub(r'(<w:style [^>]*w:styleId="Figure".*?<w:basedOn [^>]*/>)', r'\1<w:pPr><w:jc w:val="center"/></w:pPr>',
                           s, count=1, flags=re.S)
                # Table text is 9 pt, so the wide tables fit on a page; body text stays 11 pt.
                s = re.sub(r'(<w:style [^>]*w:styleId="Table".*?)(<w:tblPr>)',
                           r'\1<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>\2', s, count=1, flags=re.S)
                data = s.encode("utf-8")
            elif item.filename == "word/document.xml":
                s = data.decode("utf-8")
                # pandoc 3.1's reference has an empty <w:sectPr />. Without a page size pandoc caps figures at 5.83 in.
                s = re.sub(r"<w:sectPr\s*/>|<w:sectPr>.*?</w:sectPr>", '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
                           '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
                           "</w:sectPr>", s, flags=re.S)
                data = s.encode("utf-8")
            out.writestr(item, data)
    return ref


def prepare_markdown() -> dict[str, pathlib.Path]:
    s = REPORT.read_text(encoding="utf-8")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"### TODO\(verify\): citations not yet checked.*?(?=\n---\n)", "", s, flags=re.S)
    s = s.replace("<sup>1</sup>", "").replace(".svg)", ".png)")
    # Figures print at the full text width, where their fonts meet the owner minimums. An image line that sets its
    # own width keeps it (a figure too tall to fit on one page with its caption at full width).
    s = re.sub(r"(!\[[^\]]*\]\([^)\s]+\))(?!\{)", rf"\1{{width={TEXT_WIDTH}}}", s)
    # The italic "*Table N. ...*" line under a table becomes a pandoc table caption, which Word puts above the table.
    s = re.sub(r"(\n\|[^\n]*\|\n)\n\*(Table [A-Z]?\d+\..*?)\*\n", r"\1\nTable: \2\n", s)
    cut = s.find("## Code and Data")
    body = s[:cut] if cut > 0 else s
    paths = {"body": BUILD / "body.md", "full": BUILD / "full.md"}
    paths["body"].write_text(body, encoding="utf-8")
    paths["full"].write_text(s, encoding="utf-8")
    return paths


def word_pages(docx: pathlib.Path, pdf: pathlib.Path) -> str:
    ps = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
        f"$d = $w.Documents.Open('{docx}', $false, $true); $d.Repaginate(); "
        f"$pg = $d.ComputeStatistics(2); $wd = $d.ComputeStatistics(0); $d.ExportAsFixedFormat('{pdf}', 17); "
        "Write-Output \"$pg pages, $wd words\"; $d.Close($false); $w.Quit()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())[:200]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--open", action="store_true", help="open the body PDF when done")
    args = ap.parse_args()
    ref = letter_reference()
    for name, md in prepare_markdown().items():
        docx, pdf = BUILD / f"{name}.docx", BUILD / f"{name}.pdf"
        pypandoc.convert_file(str(md), "docx", outputfile=str(docx),
                              extra_args=[f"--reference-doc={ref}", f"--resource-path={ROOT / 'report'}", "--dpi=150"])
        keep_tables_together(docx)
        print(f"{name:5}: {word_pages(docx, pdf)}  ({pdf.relative_to(ROOT)})")
    print("cap: body (Abstract through Conclusion, incl. figures and tables) must be 8 pages or fewer; appendices and references are excluded.")
    if args.open:
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{BUILD / 'body.pdf'}'"])


if __name__ == "__main__":
    sys.exit(main())
