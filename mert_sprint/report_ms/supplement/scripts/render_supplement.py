# Copied from Daniel Elliott's ApartAICollusion repository (scripts/render_report.py at origin/main b7cbccd), by way of
# report_ms/scripts/render_report.py, and adapted to render the supplementary figure book.
# Credit: Daniel Elliott wrote this render pipeline. ROOT resolves to report_ms/supplement/, so it renders
# report_ms/supplement/SUPPLEMENT.md to report_ms/supplement/build/supplement.pdf.

"""Render SUPPLEMENT.md to .docx and .pdf in the report's page setup, and print the page count.

Page setup as in the report: pandoc's own reference document, patched to Letter, 1-inch margins and Arial 11 pt.
Changes for the figure book:
  - the font-size patch also matches pandoc 3's `<w:sz w:val="24" />` (a space before "/>");
  - the page setup is written as section properties, because pandoc's reference document.xml has empty ones (SECTION);
  - every figure prints at the full text width (6.5 in), the width its script draws it at, so its type keeps the
    owner's minimum sizes; a figure too tall to fit on a page under its heading at that width stops the render;
  - every figure starts a new page, except the first figure of a section, which follows the section's heading and
    introduction when its whole block (heading, image, caption, explanation, source) fits there; every numbered
    section after the first starts a new page;
  - where a block does not fit on one page, its text continues on the next page (sizes estimated from Arial
    advance widths);
  - figure text is set at 10 pt and the source line at 9 pt;
  - Word adds centred page numbers and exports PDF bookmarks from the headings.

    python report_ms/supplement/scripts/render_supplement.py           # prints pages and the overflowing blocks
    python report_ms/supplement/scripts/render_supplement.py --open    # also opens the PDF

Needs: `pip install --user pypandoc_binary` (bundles pandoc), Pillow, and Microsoft Word (page count and PDF export
via COM). HTML comments are stripped. Output: supplement/build/supplement.{md,docx,pdf} (gitignored).
"""

import argparse
import pathlib
import re
import subprocess
import sys
import zipfile

import pypandoc
from PIL import Image, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "SUPPLEMENT.md"
BUILD = ROOT / "build"

# Page geometry and type sizes in points (Letter, 1-inch margins). SIZES and SPACE mirror FIGURE_STYLES and the
# heading styles of pandoc's reference document.
TEXT_W, TEXT_H = 468.0, 648.0
LINE = 1.15                     # Word's single line height for Arial, as a multiple of the font size
SIZES = {"h2": 14, "h3": 12, "intro": 11, "text": 10, "source": 9}
SPACE = {"h2": 10, "h3": 10, "intro": 6 + 6, "text": 4, "source": 12, "image": 6 + 4}
SLACK = 6.0                     # points kept free on each page; the text estimate itself runs a few percent high

FIGURE_STYLES = """
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="FigureImage">
    <w:name w:val="Figure Image"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="120" w:after="80"/><w:jc w:val="center"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="FigureText">
    <w:name w:val="Figure Text"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="0" w:after="80"/></w:pPr>
    <w:rPr><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="FigureSource">
    <w:name w:val="Figure Source"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepLines/><w:spacing w:before="0" w:after="240"/></w:pPr>
    <w:rPr><w:color w:val="555555"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="SectionIntro">
    <w:name w:val="Section Intro"/><w:basedOn w:val="Normal"/><w:qFormat/>
    <w:pPr><w:spacing w:before="120" w:after="120"/></w:pPr>
  </w:style>
"""

# pandoc's reference document.xml has an empty section properties element. With it Word falls back to its own page and
# pandoc to a print width of 420 pt, which caps every image at 5.83 in. With these, pandoc allows the 6.5 in width.
SECTION = ('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" '
           'w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')


def letter_reference() -> pathlib.Path:
    """pandoc's default reference.docx patched to Letter / 1in margins / Arial 11pt, plus the figure styles."""
    BUILD.mkdir(parents=True, exist_ok=True)
    default, ref = BUILD / "ref_default.docx", BUILD / "ref_letter.docx"
    subprocess.run([pypandoc.get_pandoc_path(), "-o", str(default), "--print-default-data-file", "reference.docx"], check=True)
    with zipfile.ZipFile(default) as src, zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/styles.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<w:rFonts [^/]*/>", '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial"/>', s)
                s = re.sub(r'(<w:docDefaults>.*?)<w:sz w:val="\d+"\s*/>', r'\1<w:sz w:val="22"/>', s, flags=re.S)
                s = re.sub(r'(<w:docDefaults>.*?)<w:szCs w:val="\d+"\s*/>', r'\1<w:szCs w:val="22"/>', s, flags=re.S)
                s = s.replace("</w:styles>", FIGURE_STYLES + "</w:styles>")
                data = s.encode("utf-8")
            elif item.filename == "word/document.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<w:sectPr\s*/>|<w:sectPr\b.*?</w:sectPr>", "", s, flags=re.S)
                s = s.replace("</w:body>", SECTION + "</w:body>")
                data = s.encode("utf-8")
            out.writestr(item, data)
    return ref


_FONTS = {}


def text_height(text: str, kind: str) -> float:
    """Estimated height in points of one paragraph of `kind`, from Arial advance widths and greedy word wrap."""
    size = SIZES[kind]
    if kind not in _FONTS:
        _FONTS[kind] = ImageFont.truetype("arialbd.ttf" if kind in ("h2", "h3") else "arial.ttf", 100)
    width = lambda w: _FONTS[kind].getlength(w) * size / 100
    space, limit, lines, used = width(" "), TEXT_W * 0.98, 1, 0.0
    for word in re.sub(r"[*`]", "", text).split():
        w = width(word)
        if used and used + space + w > limit:
            lines, used = lines + 1, w
        else:
            used += (space if used else 0) + w
    return lines * size * LINE + SPACE[kind]


def image_height(image: pathlib.Path) -> float:
    """Height in points of an image printed at the full text width."""
    w, h = Image.open(image).size
    return TEXT_W * h / w


def layout(md: str) -> tuple[str, list[str], list[str]]:
    """Wrap figure blocks and section intros in the custom styles, and decide where pages break.

    Returns the Markdown, the headings that must start a new page, and one note per figure block whose text
    continues on the next page."""
    chunks = re.split(r"\n(?=#{1,3} )", md)
    out, breaks, notes = [], [], []
    shared, sections = 0.0, 0   # points used on the page by a section heading and intro that the next figure follows
    room = TEXT_H - SLACK
    for chunk in chunks:
        head, _, body = chunk.partition("\n")
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        if head.startswith("## "):
            sections += 1
            if sections > 1:
                breaks.append(head[3:])
            shared = 0.0
            if re.match(r"## \d", head):
                body = "\n\n".join(f'::: {{custom-style="Section Intro"}}\n{p}\n:::' for p in paras)
                if sections > 1:  # the first section shares the title page, so its first figure starts overleaf
                    # Word drops the space before a heading at the top of a page.
                    shared = text_height(head[3:], "h2") - SPACE["h2"] + sum(text_height(p, "intro") for p in paras)
            out.append(f"{head}\n\n{body}\n")
            continue
        if not head.startswith("### Figure"):
            out.append(chunk + "\n")
            continue
        fid = re.match(r"### Figure (S[\d.]+?)\. ", head).group(1)
        img = next(p for p in paras if p.startswith("!["))
        src = [p for p in paras if p.startswith("Source:")]
        txt = [p for p in paras if p is not img and p not in src]
        path = re.search(r"\]\((.*?)\)", img).group(1)
        # A heading at the top of a page loses its space before, and the block's last space after falls at the page
        # foot, so neither takes room.
        title = text_height(head[4:], "h3") - SPACE["h3"]
        image = image_height(ROOT / path) + SPACE["image"]
        text = sum(text_height(p, "text") for p in txt) + sum(text_height(p, "source") for p in src) - SPACE["source"]
        if title + image > room:
            sys.exit(f"Figure {fid}: {path} is {(image - SPACE['image']) / 72:.2f} in tall at full width, and a page "
                     f"holds {(room - title - SPACE['image']) / 72:.2f} in under its heading. Redraw it shorter.")
        if shared and shared + SPACE["h3"] + title + image + text > room:
            shared = 0.0   # the block does not fit under the section's introduction, so it starts a new page
        if not shared:
            breaks.append(f"Figure {fid}.")
        if shared + (SPACE["h3"] if shared else 0.0) + title + image + text > room:
            notes.append(f"{fid:8} text continues on the next page")
        shared = 0.0
        parts = [head, "", '::: {custom-style="Figure Image"}', f"![]({path}){{width={TEXT_W / 72:g}in}}", ":::", ""]
        parts += ['::: {custom-style="Figure Text"}', "\n\n".join(txt), ":::", ""]
        parts += ['::: {custom-style="Figure Source"}', "\n\n".join(src), ":::", ""]
        out.append("\n".join(parts))
    return "\n".join(out), breaks, notes


def page_breaks(docx: pathlib.Path, starts: list[str]) -> None:
    """Give the heading paragraphs that begin with one of `starts` a page break before them."""
    tmp = docx.with_suffix(".tmp.docx")
    with zipfile.ZipFile(docx) as src, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/document.xml":
                s = data.decode("utf-8")

                def mark(m):
                    p = m.group(0)
                    text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
                    if re.search(r'w:pStyle w:val="Heading[23]"', p) and any(text.startswith(t) for t in starts):
                        p = re.sub(r'(<w:pStyle w:val="Heading[23]"\s*/>)', r"\1<w:pageBreakBefore/>", p, count=1)
                    return p

                data = re.sub(r"<w:p>.*?</w:p>|<w:p .*?</w:p>", mark, s, flags=re.S).encode("utf-8")
            out.writestr(item, data)
    tmp.replace(docx)


def word_pages(docx: pathlib.Path, pdf: pathlib.Path) -> str:
    ps = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
        f"$d = $w.Documents.Open('{docx}', $false, $true); "
        "$d.Sections.Item(1).Footers.Item(1).PageNumbers.Add(1, $true) | Out-Null; $d.Repaginate(); "
        "$pg = $d.ComputeStatistics(2); $wd = $d.ComputeStatistics(0); "
        f"$d.ExportAsFixedFormat('{pdf}', 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false); "
        "Write-Output \"$pg pages, $wd words\"; $d.Close($false); $w.Quit()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    return (r.stdout.strip() or r.stderr.strip())[:300]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--open", action="store_true", help="open the PDF when done")
    args = ap.parse_args()
    ref = letter_reference()
    s = re.sub(r"<!--.*?-->", "", SOURCE.read_text(encoding="utf-8"), flags=re.S)
    s, breaks, notes = layout(s)
    md, docx, pdf = BUILD / "supplement.md", BUILD / "supplement.docx", BUILD / "supplement.pdf"
    md.write_text(s, encoding="utf-8")
    pypandoc.convert_file(str(md), "docx", outputfile=str(docx),
                          extra_args=[f"--reference-doc={ref}", f"--resource-path={ROOT}", "--dpi=300"])
    page_breaks(docx, breaks)
    print(f"supplement: {word_pages(docx, pdf)}  ({pdf.relative_to(ROOT)})")
    for n in notes:
        print("  " + n)
    if args.open:
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{pdf}'"])


if __name__ == "__main__":
    sys.exit(main())
