"""Render report/REPORT.md to .docx and .pdf in the Apart template's page setup, and print the page count.

Why not the template .docx directly: Word refuses the Google-Docs-exported template as a pandoc reference
document ("file appears to be corrupted"). pandoc's own reference document, patched to Letter, 1-inch margins
and Arial 11 pt, only approximates the template's page count: the template's body font is Old Standard TT, not
Arial, so the local render is a page-count estimate, not the template's layout. Paste the final text into the real
template at the end, or submit this output if the organisers accept it.

    python scripts/render_report.py                 # body (Abstract..Conclusion) and full report; prints pages
    python scripts/render_report.py --open          # also opens the body PDF

Needs: `pip install --user pypandoc_binary` (bundles pandoc) and Microsoft Word (page count + PDF export via COM).
HTML comments and any "### TODO(verify): ..." block (up to the next "---" line) are stripped; figure links are
switched from .svg to .png.
Output: report/build/{body,full}.{md,docx,pdf} (gitignored).
"""

import argparse
import pathlib
import re
import subprocess
import sys
import zipfile

import pypandoc

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "report" / "REPORT.md"
BUILD = ROOT / "report" / "build"


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
                s = re.sub(r'(<w:docDefaults>.*?)<w:sz w:val="\d+"/>', r'\1<w:sz w:val="22"/>', s, flags=re.S)
                s = re.sub(r'(<w:docDefaults>.*?)<w:szCs w:val="\d+"/>', r'\1<w:szCs w:val="22"/>', s, flags=re.S)
                # Keep each figure caption on one page. The figure paragraph (Captioned Figure) already has
                # keepNext, so with keepLines on the caption Word moves a figure and its whole caption to the
                # next page together instead of breaking the caption across a page break.
                s, n = re.subn(r'(<w:style [^>]*w:styleId="ImageCaption">.*?<w:basedOn w:val="Caption"\s*/>)',
                               r'\1<w:pPr><w:keepLines/></w:pPr>', s, count=1, flags=re.S)
                if n != 1:
                    raise RuntimeError("Image Caption style not found in pandoc's reference.docx")
                data = s.encode("utf-8")
            elif item.filename == "word/document.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<w:pgSz [^/]*/>", '<w:pgSz w:w="12240" w:h="15840"/>', s)
                s = re.sub(r"<w:pgMar [^/]*/>", '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>', s)
                if "<w:pgSz " not in s:
                    # pandoc's default reference.docx has no page size, so pandoc assumes a 420 pt (5.83 in) text
                    # width and shrinks any wider figure to it; give the section Letter / 1 in so 6.5 in figures fit.
                    s = s.replace("</w:sectPr>", '<w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>', 1)
                data = s.encode("utf-8")
            out.writestr(item, data)
    return ref


def prepare_markdown() -> dict[str, pathlib.Path]:
    s = REPORT.read_text(encoding="utf-8")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"### TODO\(verify\):.*?(?=\n---\n)", "", s, flags=re.S)
    s = s.replace("<sup>1</sup>", "").replace(".svg)", ".png)")
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
        print(f"{name:5}: {word_pages(docx, pdf)}  ({pdf.relative_to(ROOT)})")
    print("cap: body (Abstract through Conclusion, incl. figures and tables) must be 8 pages or fewer; appendices and references are excluded.")
    if args.open:
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{BUILD / 'body.pdf'}'"])


if __name__ == "__main__":
    sys.exit(main())
