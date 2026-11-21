"""Draws the Word shapes that carry text: a banner in the text, a cover over its page.

Each shape is written the way Word writes its own: a DrawingML shape holding
the paragraphs, and the same paragraphs again in a VML fallback for readers
that predate DrawingML. A tool that reads the file meets both copies, as it
does in a document saved by Word.
"""

from copy import deepcopy
from dataclasses import dataclass

from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Length
from docx.text.paragraph import Paragraph

TEXT_CONTENT_TAG = "w:txbxContent"
PARAGRAPH_TAG = "w:p"

NAMESPACES = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:v="urn:schemas-microsoft-com:vml"'
)
EXTENT = '<wp:extent cx="{width}" cy="{height}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
GRAPHIC = (
    '<wp:docPr id="{identifier}" name="{name}"/><wp:cNvGraphicFramePr/>'
    '<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">'
    '<wps:wsp><wps:cNvSpPr txBox="1"/><wps:spPr>'
    '<a:xfrm><a:off x="0" y="0"/><a:ext cx="{width}" cy="{height}"/></a:xfrm>'
    '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
    '<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    '<a:ln w="6350"><a:solidFill><a:srgbClr val="{outline}"/></a:solidFill></a:ln>'
    "</wps:spPr><wps:txbx><w:txbxContent/></wps:txbx>"
    '<wps:bodyPr rot="0" vert="horz" wrap="square" lIns="{inset}" tIns="{inset}" rIns="{inset}" bIns="{inset}"'
    ' anchor="{text_anchor}" anchorCtr="0"><a:noAutofit/></wps:bodyPr>'
    "</wps:wsp></a:graphicData></a:graphic>"
)
INLINE_DRAWING = '<wp:inline distT="0" distB="0" distL="0" distR="0">' + EXTENT + GRAPHIC + "</wp:inline>"
FLOATING_DRAWING = (
    '<wp:anchor distT="0" distB="0" distL="114300" distR="114300" simplePos="0" relativeHeight="251659264"'
    ' behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1"><wp:simplePos x="0" y="0"/>'
    '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
    '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
    + EXTENT + "<wp:wrapNone/>" + GRAPHIC + "</wp:anchor>"
)
SHAPE = (
    "<mc:AlternateContent " + NAMESPACES + '><mc:Choice Requires="wps"><w:drawing>{drawing}</w:drawing></mc:Choice>'
    '<mc:Fallback><w:pict><v:rect style="width:{width_points}pt;height:{height_points}pt"'
    ' fillcolor="#{fill}" strokecolor="#{outline}"><v:textbox><w:txbxContent/></v:textbox></v:rect></w:pict>'
    "</mc:Fallback></mc:AlternateContent>"
)
INLINE_SHAPE = SHAPE.replace("{drawing}", INLINE_DRAWING)
FLOATING_SHAPE = SHAPE.replace("{drawing}", FLOATING_DRAWING)


@dataclass(frozen=True)
class TextShape:
    """A rectangle holding text: in the line of its paragraph, or floating from the top left corner of its page."""

    name: str
    template: str
    width: Length
    height: Length
    fill: str
    outline: str
    inset: Length
    text_anchor: str


def new_text_content():
    return OxmlElement(TEXT_CONTENT_TAG)


def add_content_paragraph(content, parent):
    element = OxmlElement(PARAGRAPH_TAG)
    content.append(element)
    return Paragraph(element, parent)


def add_text_shape(paragraph, shape, content):
    """Anchors the shape in the paragraph, holding the paragraphs typed in `content`."""
    xml = shape.template.format(
        **vars(shape), identifier=paragraph.part.next_id, width_points=shape.width.pt, height_points=shape.height.pt
    )
    drawn = parse_xml(xml)
    placeholders = list(drawn.iter(qn(TEXT_CONTENT_TAG)))
    for placeholder in placeholders:
        placeholder.getparent().replace(placeholder, deepcopy(content))
    paragraph.add_run()._r.append(drawn)
