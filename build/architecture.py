"""Draws the deployment model as the SVG an architect would hand over.

The layout comes from architecture_layout.py, the routes of the links from architecture_routes.py
and the place of their labels from architecture_labels.py. The SVG is written to be read as text
too: a boundary is a group that holds its boxes and its boundaries, each named by its path in the
model, and a link carries the paths of its two ends.
"""

import sys
from textwrap import wrap
from xml.sax.saxutils import escape, quoteattr

from architecture_labels import LINE_PIXELS as LABEL_LINE_PIXELS
from architecture_labels import CHARACTER_PIXELS as LABEL_CHARACTER_PIXELS
from architecture_labels import MARGIN_PIXELS as LABEL_MARGIN_PIXELS
from architecture_labels import place_labels
from architecture_lanes import CELL_PIXELS, Lanes
from architecture_layout import BOX, PATH_SEPARATOR, REGION_GAP, SITE, lay_out
from architecture_routes import SOURCE, TARGET, route_all

TIERS = ("public", "application", "data")
NO_TIER = "plain"
BOX_LINE_CHARACTERS = 20
BOX_LINE_PIXELS = 13
BOX_BASELINE_PIXELS = 4
BOX_RADIUS = 5
BOUNDARY_RADIUS = 8
TITLE_INSET_PIXELS = 11
TITLE_BASELINE_PIXELS = 19
LABEL_BASELINE_PIXELS = 3.5
LABEL_RADIUS = 3
JOINT_RADIUS = 2.6
ARROW_END = "marker-end"
ARROW_START = "marker-start"
LEGEND_LINE_PIXELS = 22
LEGEND_SAMPLE_PIXELS = 56
LEGEND_TEXT_INSET_PIXELS = 70
LEGEND_BASELINE_PIXELS = 4
# What the drawing adds to the model, each with the class of the link that shows it.
LEGEND = (
    ("link plain", "Traffic or data between two components"),
    ("link plain rule", "Route or rule of a whole subnet or VPC"),
    ("link application", "A link has the colour of the subnet it starts from"),
)
LEGEND_JOINT = "Links to one component, or from one, run together from the dot"

STYLE = """\
text{font-family:Arial,Helvetica,sans-serif;fill:#1f2937}
.page{fill:#fff}
.boundary>rect,.boundary>path{stroke-width:1.4}
.cloud>path{fill:#f3f6fa;stroke:#a9b6c9}
.region>rect{fill:#fff;stroke:#7b8ba3;stroke-dasharray:8 5}
.vpc>rect{fill:#f7f9fc;stroke:#5f7396}
.zone>rect{fill:#fff;stroke:#b3bfd1;stroke-dasharray:4 3}
.site>rect{fill:#f8f4ec;stroke:#a59b8a}
.subnet.public>rect{fill:#e8f6ed;stroke:#62b585}
.subnet.application>rect{fill:#e9f1fe;stroke:#74a0ee}
.subnet.data>rect{fill:#fff4dd;stroke:#e5ad45}
.title{font-size:12px;font-weight:700;fill:#475569}
.cloud>.title,.region>.title{font-size:14px}
.public>.title{fill:#2c7a4d}
.application>.title{fill:#2d5cb3}
.data>.title{fill:#946608}
.box>rect{fill:#fff;stroke:#64748b;stroke-width:1.2}
.box.public>rect{stroke:#3f9a66}
.box.application>rect{stroke:#4a7fdb}
.box.data>rect{stroke:#cf9320}
.box>text{font-size:11px;text-anchor:middle}
.link{fill:none;stroke:#5b6779;stroke-width:1.3;stroke-linejoin:round}
.link.public{stroke:#2f8a57}
.link.application{stroke:#3b6fd4}
.link.data{stroke:#c08410}
.rule{stroke-dasharray:5 3}
.arrow,.joint{fill:#5b6779}
.arrow.public,.joint.public{fill:#2f8a57}
.arrow.application,.joint.application{fill:#3b6fd4}
.arrow.data,.joint.data{fill:#c08410}
.label>rect{fill:#fff;fill-opacity:.93}
.label>text{font-size:10px;text-anchor:middle;fill:#334155}
.legend>text{font-size:11px;fill:#475569}
"""
MARKER = ('<marker id="arrow-{tier}" viewBox="0 0 8 8" refX="7.5" refY="4" markerWidth="7" markerHeight="7" '
          'orient="auto-start-reverse"><path class="arrow {tier}" d="M0 0.8L8 4L0 7.2z"/></marker>')


def draw(model):
    layout = lay_out(model)
    lanes = Lanes(layout)
    routes = route_all(model, layout, lanes)
    if lanes.shared:
        sys.exit(f"{lanes.shared} lanes of the deployment drawing hold two links: give the layout more room.")
    labels = place_labels(routes, lanes)
    width, height = pixels(layout.width), pixels(layout.height)
    markers = "".join(MARKER.format(tier=tier) for tier in (*TIERS, NO_TIER))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
             f"<style>{STYLE}</style>", f"<defs>{markers}</defs>",
             f'<rect class="page" width="{width}" height="{height}"/>',
             *container_elements(model, (), layout),
             *[link_element(route, layout, lanes) for route in routes],
             *[label_element(label, lanes) for label in labels], legend_element(layout), "</svg>"]
    return "\n".join(parts) + "\n"


def pixels(cells):
    return cells * CELL_PIXELS


def tier_of(path):
    segments = path.split(PATH_SEPARATOR)
    return next((segment for segment in reversed(segments) if segment in TIERS), NO_TIER)


def container_elements(container, path, layout):
    boxes = [box_element(layout.shapes[joined(path, box)]) for box in container.get("boxes", [])]
    boundaries = [element for boundary in container.get("boundaries", [])
                  for element in boundary_elements(boundary, (*path, boundary["id"]), layout)]
    return boxes + boundaries


def joined(path, node):
    return PATH_SEPARATOR.join((*path, node["id"]))


def boundary_elements(boundary, path, layout):
    shape = layout.shapes[PATH_SEPARATOR.join(path)]
    left, top = pixels(shape.rectangle.left), pixels(shape.rectangle.top)
    opening = f'<g id={quoteattr(shape.path)} class="boundary {shape.level} {tier_of(shape.path)}">'
    title = (f'<text class="title" x="{left + TITLE_INSET_PIXELS}" y="{top + TITLE_BASELINE_PIXELS}">'
             f"{escape(shape.label)}</text>")
    return [opening, outline_element(shape), title, *container_elements(boundary, path, layout), "</g>"]


def outline_element(shape):
    if shape.cut:
        points = " ".join(f"{pixels(across)},{pixels(down)}" for across, down in shape.corners())
        return f'<path d="M{points}z"/>'
    return f"<rect {geometry(shape.rectangle)} rx=\"{BOUNDARY_RADIUS}\"/>"


def geometry(rectangle):
    left, top, width, height = (pixels(cells) for cells in rectangle)
    return f'x="{left}" y="{top}" width="{width}" height="{height}"'


def box_element(shape):
    lines = wrap(shape.label, BOX_LINE_CHARACTERS)
    rectangle = shape.rectangle
    centre = pixels(rectangle.left) + pixels(rectangle.width) / 2
    middle = pixels(rectangle.top) + pixels(rectangle.height) / 2
    text = text_element(lines, centre, middle + BOX_BASELINE_PIXELS, BOX_LINE_PIXELS)
    return (f'<g id={quoteattr(shape.path)} class="box {tier_of(shape.path)}"><title>{escape(shape.label)}</title>'
            f'<rect {geometry(rectangle)} rx="{BOX_RADIUS}"/>{text}</g>')


def text_element(lines, centre, baseline, line_pixels):
    """A text of one or several lines, centred on a point: `baseline` is the baseline of a single line."""
    first = baseline - (len(lines) - 1) * line_pixels / 2
    spans = "".join(f'<tspan x="{centre:g}" y="{first + index * line_pixels:g}">{escape(line)}</tspan>'
                    for index, line in enumerate(lines))
    return f"<text>{spans}</text>"


def link_element(route, layout, lanes):
    link = route.link
    tier = tier_of(link[SOURCE])
    ends = [layout.shapes[link[SOURCE]], layout.shapes[link[TARGET]]]
    rule = " rule" if any(end.level != BOX for end in ends) else ""
    arrows = [ARROW_END, ARROW_START] if link.get("both_ways") else [ARROW_END]
    markers = "".join(f' {arrow}="url(#arrow-{tier})"' for arrow in arrows)
    arrow_text = "↔" if link.get("both_ways") else "→"
    title = escape(f"{ends[0].label} {arrow_text} {ends[1].label}" + (f": {link['label']}" if "label" in link else ""))
    path = (f'<path class="link {tier}{rule}" data-from={quoteattr(link[SOURCE])} data-to={quoteattr(link[TARGET])} '
            f'd="{path_data(route.cells, lanes)}"{markers}><title>{title}</title></path>')
    return path + joint_element(route, tier, lanes)


def joint_element(route, tier, lanes):
    if route.joint is None:
        return ""
    across, down = centre_of(route.joint, lanes)
    return f'<circle class="joint {tier}" cx="{across:g}" cy="{down:g}" r="{JOINT_RADIUS}"/>'


def centre_of(cell, lanes):
    across, down = lanes.position(cell)
    return pixels(across) + CELL_PIXELS / 2, pixels(down) + CELL_PIXELS / 2


def path_data(cells, lanes):
    """The line through the centres of the cells, drawn from the edge of one end to the edge of the other."""
    points = [centre_of(cell, lanes) for cell in cells]
    start = stretched(points[0], points[1])
    end = stretched(points[-1], points[-2])
    commands = [f"M{start[0]:g} {start[1]:g}"]
    for previous, point in zip([start, *points[1:-1]], [*points[1:-1], end]):
        commands.append(f"H{point[0]:g}" if point[1] == previous[1] else f"V{point[1]:g}")
    return "".join(merged(commands))


def stretched(point, neighbour):
    """The point half a cell further from its neighbour: on the edge of the shape the link ends on."""
    across = point[0] + (point[0] - neighbour[0]) / 2
    down = point[1] + (point[1] - neighbour[1]) / 2
    return across, down


def merged(commands):
    """Keeps the last of each run of steps along one axis: one command per straight line."""
    kept = [commands[0]]
    for command, following in zip(commands[1:], [*commands[2:], ""]):
        if command[0] != following[:1]:
            kept.append(command)
    return kept


def legend_element(layout):
    """The legend, under the site that stands outside the cloud."""
    site = next(shape.rectangle for shape in layout.shapes.values() if shape.level == SITE)
    left, top = pixels(site.left), pixels(site.bottom + REGION_GAP)
    rows = [legend_row(left, top + index * LEGEND_LINE_PIXELS, link_class, text)
            for index, (link_class, text) in enumerate(LEGEND)]
    joint_row = top + len(LEGEND) * LEGEND_LINE_PIXELS
    joint = f'<circle class="joint" cx="{left + LEGEND_SAMPLE_PIXELS / 2:g}" cy="{joint_row}" r="{JOINT_RADIUS}"/>'
    return f'<g class="legend">{"".join(rows)}{joint}{legend_text(left, joint_row, LEGEND_JOINT)}</g>'


def legend_row(left, row, link_class, text):
    tier = link_class.split()[1]
    sample = (f'<path class="{link_class}" d="M{left} {row}H{left + LEGEND_SAMPLE_PIXELS}" '
              f'{ARROW_END}="url(#arrow-{tier})"/>')
    return sample + legend_text(left, row, text)


def legend_text(left, row, text):
    return f'<text x="{left + LEGEND_TEXT_INSET_PIXELS}" y="{row + LEGEND_BASELINE_PIXELS}">{escape(text)}</text>'


def label_element(label, lanes):
    across, down = centre_of(label.cell, lanes)
    width = max(map(len, label.lines)) * LABEL_CHARACTER_PIXELS + LABEL_MARGIN_PIXELS
    height = len(label.lines) * LABEL_LINE_PIXELS + LABEL_MARGIN_PIXELS
    ground = (f'<rect x="{across - width / 2:g}" y="{down - height / 2:g}" width="{width:g}" height="{height:g}" '
              f'rx="{LABEL_RADIUS}"/>')
    text = text_element(label.lines, across, down + LABEL_BASELINE_PIXELS, LABEL_LINE_PIXELS)
    return f'<g class="label {tier_of(label.link[SOURCE])}">{ground}{text}</g>'
