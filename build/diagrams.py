"""Renders the diagrams: a Mermaid text to an SVG, then an SVG to a PNG.

The PNG is a screenshot of the SVG, so both files show the same drawing: the SVG keeps its labels
as text, the PNG holds pixels only.
"""

import json
import math
from xml.etree import ElementTree

from screenshots import capture
from tools import find_tool, run_tool

ENCODING = "utf-8"
MERMAID_CLI = "mmdc"
BROWSER = "chrome-headless-shell"

MERMAID_CONFIGURATION = {
    # Mermaid draws the boxes of an entity-relationship diagram with rough.js, seeded at random:
    # a fixed seed gives the same SVG at every run.
    "handDrawnSeed": 1,
    # The default look, "neo", puts a drop shadow under each box: the drawing stays flat.
    "look": "classic",
    # Mermaid's default font is a web font it embeds in the SVG, 170 KB of base64 that an agent
    # reading the SVG pays for. Left out without this, the labels are drawn in another font than
    # the one their boxes were sized for, and overflow.
    "fontFamily": "arial, sans-serif",
    # Mermaid gives each label a box of the exact width of its text, a fraction of a pixel, and
    # Chrome clips the box at the whole pixel below: the last letter of a label loses its edge.
    # The boxes are reached through their parents: Mermaid writes this rule in lower case, and
    # "foreignobject" matches nothing in an SVG.
    "themeCSS": ".label > *, .cluster-label > * { overflow: visible; }",
}
MERMAID_CONFIGURATION_NAME = "mermaid.json"
# The headless Chrome that Mermaid's CLI starts cannot open its sandbox on the larger diagram.
PUPPETEER_CONFIGURATION = {"args": ["--no-sandbox"]}
PUPPETEER_CONFIGURATION_NAME = "puppeteer.json"

# One page the size of the drawing, so the PNG holds the drawing and nothing around it.
PAGE = """\
<!doctype html>
<style>
  body {{ margin: 0; }}
  img {{ display: block; width: {width}px; height: {height}px; }}
</style>
<img src="{image}">
"""
VIEW_BOX = "viewBox"
VIEW_BOX_SIZE = slice(2, 4)
PNG_SUFFIX = ".png"


def render_mermaid(source, svg, work_directory):
    configuration = write_json(MERMAID_CONFIGURATION, work_directory, MERMAID_CONFIGURATION_NAME)
    puppeteer = write_json(PUPPETEER_CONFIGURATION, work_directory, PUPPETEER_CONFIGURATION_NAME)
    arguments = ["--quiet", "--input", source, "--output", svg,
                 "--configFile", configuration, "--puppeteerConfigFile", puppeteer]
    browser = find_tool(BROWSER)
    run_tool(MERMAID_CLI, *arguments, PUPPETEER_EXECUTABLE_PATH=browser)


def write_json(content, directory, name):
    path = directory / name
    text = json.dumps(content)
    path.write_text(text, encoding=ENCODING)
    return path


def export_png(svg):
    """Screenshots the SVG at the size it was laid out at, one pixel of the PNG per pixel of the drawing.

    Any smaller and the labels, 14 pixels high, can no longer be read.
    """
    drawing = ElementTree.parse(svg)
    width, height = drawing.getroot().get(VIEW_BOX).split()[VIEW_BOX_SIZE]
    page = PAGE.format(width=width, height=height, image=svg.as_uri())
    window_width = math.ceil(float(width))
    window_height = math.ceil(float(height))
    picture = capture(page, window_width, window_height)
    png = svg.with_suffix(PNG_SUFFIX)
    picture.save(png)
