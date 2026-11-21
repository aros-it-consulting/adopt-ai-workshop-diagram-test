#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["python-docx>=1.2", "lxml>=5", "pillow>=11"]
# ///
"""Builds the bad Word file of the returns specification: spec.md after years of edits.

pandoc turns the Markdown into HTML, and python-docx types that HTML into a
Word document that looks finished and holds the same facts, laid out the way
a document passed from hand to hand ends up:

- a dark cover and white headings, each one text on a shape, and the body in
  two columns;
- headings without a heading style;
- every table pasted as screenshots;
- the footnotes typed by hand after the annexes, far from their numbers;
- the amendment as the scan of its signed page, on the last page;
- the version in force in the page footer only;
- the words a reader searches for split across runs of direct formatting.

    mise exec -- uv run build/degrade_docx.py

Reads sources/3_specification/spec.md and writes spec.bad.docx next to it.
"""

import subprocess
from pathlib import Path

import lxml.html
from docx import Document
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from docx_body import (
    SINGLE_COLUMN, TEXT_COLUMNS, THEME_COLOR, WHITE, open_section, paste_picture, write_blocks, write_notes,
)
from docx_runs import Look, write_text
from docx_shapes import FLOATING_SHAPE, TextShape, add_content_paragraph, add_text_shape, new_text_content
from scanned_page import scanned_page
from tools import find_tool

SPECIFICATION_FOLDER = Path(__file__).resolve().parent.parent / "sources" / "3_specification"
SOURCE = SPECIFICATION_FOLDER / "spec.md"
OUTPUT = SPECIFICATION_FOLDER / "spec.bad.docx"
PANDOC = "pandoc"
PANDOC_FLAGS = [
    # The apostrophes and quotes stay as typed, as in the other formats built from the Markdown.
    "--from=markdown-smart",
    "--to=html",
    # Each paragraph stays on one line: a line end in the HTML then only follows a line break.
    "--wrap=none",
]

PAGE_WIDTH = Cm(21)
PAGE_HEIGHT = Cm(29.7)
PAGE_MARGIN = Cm(2)
HEADING_STYLES = ("Heading", "Title")
LANGUAGE_SETTING = "w:docDefaults//w:lang"
LANGUAGE = "fr-FR"
AUTHOR = "Orvane"

COVER = TextShape(
    name="Zone de texte", template=FLOATING_SHAPE, width=PAGE_WIDTH, height=PAGE_HEIGHT,
    fill=THEME_COLOR, outline=THEME_COLOR, inset=Cm(2.5), text_anchor="ctr",
)
TITLE_LOOK = Look(bold=True, size=Pt(30), color=WHITE)
COVER_LOOK = Look(size=Pt(12), color=WHITE)
VERSION_LINE = "Version en vigueur"
FOOTER_LOOK = Look(size=Pt(8))

NOTES_SECTION = "section"
NOTE_ITEM = "li"
NOTE_BACKLINKS = ".//a[@class='footnote-back']"
OPENER_TAG = "h2"
AMENDMENT_TITLE = "Avenant"


def read_specification():
    command = [find_tool(PANDOC), *PANDOC_FLAGS, str(SOURCE)]
    converted = subprocess.run(command, capture_output=True, text=True, check=True)
    return lxml.html.fragment_fromstring(converted.stdout, create_parent=True)


def take_notes(specification):
    """Takes pandoc's footnotes out of the blocks and returns the paragraph of each note, in the order of their numbers."""
    section = specification.find(NOTES_SECTION)
    specification.remove(section)
    for backlink in section.xpath(NOTE_BACKLINKS):
        backlink.drop_tree()
    return [item[0] for item in section.iter(NOTE_ITEM)]


def remove_heading_styles(document):
    heading_styles = [style for style in document.styles if style.name.startswith(HEADING_STYLES)]
    for style in heading_styles:
        style.delete()


def set_defaults(document):
    language = document.styles.element.find(LANGUAGE_SETTING, document.styles.element.nsmap)
    language.set(qn("w:val"), LANGUAGE)
    document.core_properties.author = AUTHOR
    document.core_properties.comments = ""


def new_document():
    document = Document()
    page = document.sections[0]
    page.page_width, page.page_height = PAGE_WIDTH, PAGE_HEIGHT
    page.left_margin = page.right_margin = page.top_margin = page.bottom_margin = PAGE_MARGIN
    set_defaults(document)
    remove_heading_styles(document)
    return document


def write_cover(document, title, lines):
    content = new_text_content()
    title_paragraph = add_content_paragraph(content, document)
    write_text(title_paragraph, title.text_content(), TITLE_LOOK)
    for line in lines:
        paragraph = add_content_paragraph(content, document)
        write_text(paragraph, line, COVER_LOOK)
    anchor = document.add_paragraph()
    add_text_shape(anchor, COVER, content)


def write_front(document, title, header_lines):
    """Writes the cover from the title and the header block, whose version line goes to the page footer only."""
    cover_lines = [line for line in header_lines if not line.startswith(VERSION_LINE)]
    version_lines = [line for line in header_lines if line.startswith(VERSION_LINE)]
    footer = document.sections[0].footer.paragraphs[0]
    write_text(footer, version_lines[0], FOOTER_LOOK)
    write_cover(document, title, cover_lines)


def is_amendment_title(block):
    return block.tag == OPENER_TAG and block.text_content().startswith(AMENDMENT_TITLE)


def write_body(document, blocks, notes):
    open_section(document, WD_SECTION.NEW_PAGE, TEXT_COLUMNS)
    write_blocks(document, blocks)
    write_notes(document, notes)


def paste_amendment(document, blocks, signatory):
    open_section(document, WD_SECTION.NEW_PAGE, SINGLE_COLUMN)
    scan = scanned_page(blocks, signatory)
    paste_picture(document, scan)


def write_parts(document, blocks, notes, signatory):
    amendment_start = next(index for index, block in enumerate(blocks) if is_amendment_title(block))
    write_body(document, blocks[:amendment_start], notes)
    paste_amendment(document, blocks[amendment_start:], signatory)


def main():
    specification = read_specification()
    notes = take_notes(specification)
    title, header, *blocks = specification
    header_lines = [line.strip() for line in header.itertext()]
    document = new_document()
    write_front(document, title, header_lines)
    write_parts(document, blocks, notes, header_lines[0])
    document.save(OUTPUT)
    print(f"{OUTPUT}: {OUTPUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
