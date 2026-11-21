"""Lays the blocks of the specification out in the Word document.

The blocks are the elements of pandoc's HTML. Text flows in columns; a
picture takes the full width, in a section of its own. A main heading becomes
white text on a coloured shape, a sub-heading a bold paragraph, both with
their typed number and no heading style. Every table is pasted as screen
captures, cropped to the table the way Word crops: the rest stays in the file. The notes are typed at the end, far from the numbers that refer
to them, as ordinary paragraphs opened by a superscript number.
"""

from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from docx_runs import Look, add_run, write_inlines
from docx_shapes import INLINE_SHAPE, TextShape, add_content_paragraph, add_text_shape, new_text_content
from table_images import table_captures

SINGLE_COLUMN = 1
TEXT_COLUMNS = 2
COLUMNS_TAG = "w:cols"
COLUMN_COUNT = "w:num"
EMU_PER_PIXEL = 9525
CROP_TAG = "a:srcRect"
CROP_UNITS = 100000

THEME_COLOR = "1F3864"
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
# Narrower than one of the two columns of an A4 page, so that the banner never spills into the next one.
BANNER = TextShape(
    name="Zone de texte", template=INLINE_SHAPE, width=Cm(7.8), height=Cm(1.1),
    fill=THEME_COLOR, outline=THEME_COLOR, inset=Cm(0.15), text_anchor="ctr",
)
BANNER_LOOK = Look(bold=True, size=Pt(11), color=WHITE)
TEXT_LOOK = Look()
HEADING_LOOK = Look(bold=True, size=Pt(11))
NOTE_LOOK = Look(size=Pt(8))
NOTE_NUMBER_LOOK = Look(size=Pt(8), superscript=True)
NOTE_GAP = " "
FIRST_NOTE_NUMBER = 1
BULLET_STYLE = "List Bullet"


def open_section(document, start, column_count):
    section = document.add_section(start)
    columns = section._sectPr.find(qn(COLUMNS_TAG))
    columns.set(qn(COLUMN_COUNT), str(column_count))
    return section


def use_columns(document, column_count):
    columns = document.sections[-1]._sectPr.find(qn(COLUMNS_TAG))
    current_count = int(columns.get(qn(COLUMN_COUNT), SINGLE_COLUMN))
    if current_count != column_count:
        open_section(document, WD_SECTION.CONTINUOUS, column_count)


def text_width(document):
    section = document.sections[-1]
    return section.page_width - section.left_margin - section.right_margin


def add_text_paragraph(document):
    use_columns(document, TEXT_COLUMNS)
    return document.add_paragraph()


def add_heading_paragraph(document):
    paragraph = add_text_paragraph(document)
    paragraph.paragraph_format.keep_with_next = True
    return paragraph


def write_opener(document, heading):
    paragraph = add_heading_paragraph(document)
    content = new_text_content()
    title = add_content_paragraph(content, document)
    write_inlines(title, heading, BANNER_LOOK)
    add_text_shape(paragraph, BANNER, content)


def write_heading(document, heading):
    paragraph = add_heading_paragraph(document)
    write_inlines(paragraph, heading, HEADING_LOOK)


def write_paragraph(document, element):
    paragraph = add_text_paragraph(document)
    write_inlines(paragraph, element, TEXT_LOOK)


def write_list(document, items):
    for item in items:
        paragraph = add_text_paragraph(document)
        paragraph.style = BULLET_STYLE
        write_inlines(paragraph, item, TEXT_LOOK)


def paste_picture(document, picture):
    use_columns(document, SINGLE_COLUMN)
    document.add_picture(picture, width=text_width(document))


def crop(shape, hidden_shares):
    source_rectangle = OxmlElement(CROP_TAG)
    for side, share in hidden_shares.items():
        source_rectangle.set(side, str(round(share * CROP_UNITS)))
    shape._inline.graphic.graphicData.pic.blipFill.blip.addnext(source_rectangle)


def paste_capture(document, capture):
    use_columns(document, SINGLE_COLUMN)
    width = text_width(document)
    height = round(width * capture.proportions)
    shape = document.add_picture(capture.picture, width=width, height=height)
    crop(shape, capture.hidden_shares)


def write_table(document, table):
    pixel_width = round(text_width(document) / EMU_PER_PIXEL)
    for capture in table_captures(table, pixel_width):
        paste_capture(document, capture)


def write_notes(document, notes):
    for number, note in enumerate(notes, start=FIRST_NOTE_NUMBER):
        paragraph = add_text_paragraph(document)
        add_run(paragraph, str(number), NOTE_NUMBER_LOOK)
        add_run(paragraph, NOTE_GAP, NOTE_LOOK)
        write_inlines(paragraph, note, NOTE_LOOK)


BLOCK_WRITERS = {"h2": write_opener, "h3": write_heading, "p": write_paragraph, "ul": write_list, "table": write_table}


def write_blocks(document, blocks):
    for block in blocks:
        BLOCK_WRITERS[block.tag](document, block)
