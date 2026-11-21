"""Turns an HTML table into the screen captures a colleague pastes from another tool.

The table is shown in a browser window that fills a screen, and captured
whole, at screen resolution, in as many captures as its length calls for,
each compressed the way a wiki or a chat tool compresses what goes through
it. A capture comes with the place of the table on the screen: Word crops the
rest out of sight and keeps the whole capture in the file. On the way the
table loses what a pasted picture loses: the status column, of which only a
colour and a strikethrough remain on the rows it marked, and the repeated
cells, merged the way a hand-made matrix is laid out.
"""

import io
import math
import sys
from copy import deepcopy
from dataclasses import dataclass

import lxml.html
from PIL import Image, ImageChops

from screenshots import as_jpeg, capture

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_COLOR = "#eceef1"
TABLE_LEFT = 340
TABLE_TOP = 110
JPEG_QUALITY = 60
PAGE = """<!doctype html>
<meta charset="utf-8">
<style>
  html, body {{ height: 100%; }}
  body {{ margin: 0; background: {screen_color}; font: 14px/1.4 "DejaVu Sans", Arial, sans-serif; }}
  header {{ height: 56px; background: #253858; }}
  nav {{ position: absolute; top: 56px; bottom: 0; left: 0; width: 280px; background: #dfe1e6; }}
  main {{ position: absolute; left: {left}px; top: {top}px; width: {width}px; }}
  table {{ width: 100%; border-collapse: collapse; background: white; }}
  th, td {{ border: 1px solid #7f7f7f; padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: #d9e1f2; }}
  td[rowspan] {{ vertical-align: middle; }}
  a {{ color: inherit; text-decoration: none; }}
  .amended td {{ color: #c55a11; }}
  .repealed td {{ color: #c00000; text-decoration: line-through; }}
</style>
<header></header>
<nav></nav>
<main>{table}</main>
"""
# What a screen shows of a table without scrolling.
MAX_ROWS_PER_PICTURE = 8
BODY_ROWS = "./tbody/tr"
HEADER_CELLS = "./thead/tr/th"
COLUMNS = "./colgroup/col"
STATUS_COLUMN = "Statut"
ROW_CLASS_BY_STATUS = {"Modifiée": "amended", "Abrogée": "repealed"}
MERGED_COLUMNS = ("Canal", "Moyen de paiement")
ROW_SPAN = "rowspan"
SINGLE_ROW = "1"


@dataclass(frozen=True)
class ScreenCapture:
    """A JPEG of the whole screen, the share of it hidden on each side of the table, and the table's height over its width."""

    picture: io.BytesIO
    hidden_shares: dict
    proportions: float


def column_titles(table):
    return [cell.text_content() for cell in table.xpath(HEADER_CELLS)]


def remove(element):
    element.getparent().remove(element)


def mark_status(row, status_index):
    status = row[status_index].text_content()
    classes = [name for prefix, name in ROW_CLASS_BY_STATUS.items() if status.startswith(prefix)]
    row.set("class", " ".join(classes))
    remove(row[status_index])


def drop_status_column(table):
    titles = column_titles(table)
    if STATUS_COLUMN not in titles:
        return
    status_index = titles.index(STATUS_COLUMN)
    for row in table.xpath(BODY_ROWS):
        mark_status(row, status_index)
    remove(table.xpath(HEADER_CELLS)[status_index])
    remove(table.xpath(COLUMNS)[status_index])


def merge_into(merged, cell):
    if merged is None or cell.text_content() != merged.text_content():
        return cell
    row_span = int(merged.get(ROW_SPAN, SINGLE_ROW)) + 1
    merged.set(ROW_SPAN, str(row_span))
    remove(cell)
    return merged


def merge_column(table, column_index):
    merged = None
    for row in table.xpath(BODY_ROWS):
        merged = merge_into(merged, row[column_index])


def merge_repeated_cells(table):
    titles = column_titles(table)
    merged_indexes = [titles.index(title) for title in MERGED_COLUMNS if title in titles]
    # From the right: removing a cell shifts the ones that follow it in its row.
    for column_index in sorted(merged_indexes, reverse=True):
        merge_column(table, column_index)


def part_of(table, first_row, last_row):
    part = deepcopy(table)
    rows = part.xpath(BODY_ROWS)
    for row in rows[:first_row] + rows[last_row:]:
        remove(row)
    merge_repeated_cells(part)
    return part


def split(table):
    """Cuts a long table into pictures of equal length, each with the header row."""
    row_count = len(table.xpath(BODY_ROWS))
    picture_count = math.ceil(row_count / MAX_ROWS_PER_PICTURE)
    rows_per_picture = math.ceil(row_count / picture_count)
    first_rows = range(0, row_count, rows_per_picture)
    return [part_of(table, first_row, first_row + rows_per_picture) for first_row in first_rows]


def find_table(screenshot, width):
    """Returns the box of the table on the screen: its corner is known, its height depends on its text."""
    column = screenshot.crop((TABLE_LEFT, TABLE_TOP, TABLE_LEFT + width, SCREEN_HEIGHT))
    blank = Image.new(column.mode, column.size, SCREEN_COLOR)
    left, top, right, bottom = ImageChops.difference(column, blank).getbbox()
    if bottom == column.height:
        sys.exit(f"A table is taller than the {SCREEN_HEIGHT} px screen.")
    return TABLE_LEFT + left, TABLE_TOP + top, TABLE_LEFT + right, TABLE_TOP + bottom


def capture_of(table, width):
    table_html = lxml.html.tostring(table, encoding="unicode")
    page = PAGE.format(screen_color=SCREEN_COLOR, left=TABLE_LEFT, top=TABLE_TOP, width=width, table=table_html)
    screenshot = capture(page, SCREEN_WIDTH, SCREEN_HEIGHT)
    left, top, right, bottom = find_table(screenshot, width)
    hidden_shares = {"l": left / SCREEN_WIDTH, "t": top / SCREEN_HEIGHT,
                     "r": 1 - right / SCREEN_WIDTH, "b": 1 - bottom / SCREEN_HEIGHT}
    proportions = (bottom - top) / (right - left)
    picture = as_jpeg(screenshot, JPEG_QUALITY)
    return ScreenCapture(picture, hidden_shares, proportions)


def table_captures(table, width):
    """Returns the screen captures showing `table`, drawn `width` pixels wide."""
    pasted = deepcopy(table)
    drop_status_column(pasted)
    parts = split(pasted)
    return [capture_of(part, width) for part in parts]
