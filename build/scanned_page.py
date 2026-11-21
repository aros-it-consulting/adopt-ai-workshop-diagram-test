"""Turns blocks of the specification into the picture of a page printed, signed and scanned.

The blocks are printed as they are, on an A4 page that ends with the
signatory's name under a signature and a stamp. The page then goes through
what an office scanner does to a sheet: grey levels, a sheet fed slightly
askew, soft edges, grain and a strong compression. Nothing of the text is
left but the picture.
"""

import html
import random

import lxml.html
from PIL import Image, ImageFilter

from screenshots import as_jpeg, capture

# A4 at 150 dots per inch, the resolution of a scan sent by e-mail.
SHEET_WIDTH = 1240
SHEET_HEIGHT = 1754
SHEET = """<!doctype html>
<meta charset="utf-8">
<style>
  body {{ margin: 0; background: white; color: #111; font: 22px/1.45 "DejaVu Serif", serif; }}
  main {{ padding: 130px 140px 0; }}
  h2 {{ font-size: 32px; margin: 0 0 14px; }}
  h3 {{ font-size: 23px; margin: 30px 0 10px; }}
  p {{ margin: 0 0 12px; }}
  .signature {{ position: relative; margin: 50px 0 0 430px; height: 230px; }}
  .signature svg {{ position: absolute; left: 0; top: 30px; }}
  .stamp {{ position: absolute; left: 150px; top: 70px; width: 300px; padding: 10px 14px; transform: rotate(-9deg);
            border: 4px double #2f4b9c; color: #2f4b9c; opacity: 0.75; text-align: center;
            font: bold 19px/1.3 "DejaVu Sans", sans-serif; text-transform: uppercase; }}
</style>
<main>
{content}
<div class="signature">
  {signatory}
  <svg width="330" height="150" viewBox="0 0 330 150" fill="none" stroke="#1c2a5e" stroke-width="3">
    <path d="M12 96 C40 20 66 18 60 74 C56 122 30 132 46 88 C64 40 100 30 104 80 C106 108 88 112 98 84
             C112 48 132 60 138 86 C146 60 166 56 174 84 C182 58 204 62 214 82 C240 70 276 74 318 52"/>
    <path d="M30 124 C110 112 210 108 300 116"/>
  </svg>
  <div class="stamp">{signatory}</div>
</div>
</main>
"""
GREY_LEVELS = "L"
PAPER_WHITE = 255
SKEW_DEGREES = 0.8
BLUR_RADIUS = 0.7
GRAIN_SEED = 7
GRAIN_SHARE = 0.08
JPEG_QUALITY = 40


def printed_sheet(blocks, signatory):
    printed_blocks = [lxml.html.tostring(block, encoding="unicode") for block in blocks]
    content = "".join(printed_blocks)
    signatory_text = html.escape(signatory)
    return SHEET.format(content=content, signatory=signatory_text)


def grain(size):
    width, height = size
    dots = random.Random(GRAIN_SEED).randbytes(width * height)
    return Image.frombytes(GREY_LEVELS, size, dots)


def scan(sheet):
    grey_sheet = sheet.convert(GREY_LEVELS)
    askew_sheet = grey_sheet.rotate(SKEW_DEGREES, resample=Image.Resampling.BICUBIC, fillcolor=PAPER_WHITE)
    soft_edges = ImageFilter.GaussianBlur(BLUR_RADIUS)
    soft_sheet = askew_sheet.filter(soft_edges)
    sheet_grain = grain(soft_sheet.size)
    return Image.blend(soft_sheet, sheet_grain, GRAIN_SHARE)


def scanned_page(blocks, signatory):
    """Returns the JPEG picture of the blocks printed on one page, signed by `signatory` and scanned."""
    sheet = printed_sheet(blocks, signatory)
    printed = capture(sheet, SHEET_WIDTH, SHEET_HEIGHT)
    scanned = scan(printed)
    return as_jpeg(scanned, JPEG_QUALITY)
