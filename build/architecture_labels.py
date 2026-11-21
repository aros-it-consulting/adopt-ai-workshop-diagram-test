"""Places the label of each bundle of links on its route, where it hides the least.

A bundle is labelled once: its links run together and read as one. The label sits on the route or
right next to it, away from the boxes, the titles, the borders, the other links and the labels
placed before.
"""

from math import ceil
from textwrap import wrap
from typing import NamedTuple

from architecture_lanes import AXES, CELL_PIXELS, FREE, VERTICAL

LINE_CHARACTERS = 26
CHARACTER_PIXELS = 5.8
LINE_PIXELS = 12
MARGIN_PIXELS = 4
# The cells next to the ends of a route are left to the arrowhead.
END_CELLS = 3
HIDDEN_SHAPE = 60
HIDDEN_LINK = 8
HIDDEN_BORDER = 5
ACROSS_ITS_LINK = 2
OFF_ITS_LINK = 2
OFF_CENTRE = 0.01
# How far from its route a label may sit, above or below, in cells.
ROWS_OFF = range(-6, 7)
BESIDE = 2


class Label(NamedTuple):
    """The lines of a label, the cell it is centred on and the link whose colour it takes."""

    lines: list[str]
    cell: int
    link: dict


class Place(NamedTuple):
    """A place a label may take: `cell`, on a cell of a route or `off` it by some rows or columns."""

    route: object
    index: int
    cell: int
    off: int


def place_labels(routes, lanes):
    taken = bytearray(len(lanes.closed))
    bundles = {}
    for route in routes:
        bundles.setdefault(route.bundle, []).append(route)
    labelled = [members for members in bundles.values() if members[0].link.get("label")]
    return [place_label(members, lanes, taken) for members in labelled]


def place_label(members, lanes, taken):
    link = members[0].link
    lines = wrap(link["label"], LINE_CHARACTERS)
    width = cells_around(max(map(len, lines)) * CHARACTER_PIXELS + MARGIN_PIXELS)
    height = cells_around(len(lines) * LINE_PIXELS + MARGIN_PIXELS)
    places = [place for route in members for index in labelled_cells(route)
              for place in places_around(route, index, lanes, width)]
    best = min(places, key=lambda place: hidden(place, lanes, taken, width, height))
    for covered in covered_cells(lanes, best.cell, width, height):
        taken[covered] = True
    return Label(lines, best.cell, link)


def places_around(route, index, lanes, width):
    """A cell of the route, the cells above and below it, and those a label would sit beside the link from."""
    across, down = lanes.position(route.cells[index])
    beside = width // 2 + 1
    cells = [(across, down + rows, abs(rows)) for rows in ROWS_OFF]
    cells += [(across - beside, down, BESIDE), (across + beside, down, BESIDE)]
    return [Place(route, index, lanes.cell(column, row), off) for column, row, off in cells
            if 0 <= column < lanes.width and 0 <= row < lanes.height]


def cells_around(size_pixels):
    """The odd number of cells that a label of this size, centred on a cell, reaches into."""
    return 2 * ceil((size_pixels / CELL_PIXELS - 1) / 2) + 1


def labelled_cells(route):
    """The cells of a route a label may sit on: all but its ends, or its middle when it is that short."""
    cells = range(END_CELLS, len(route.cells) - END_CELLS)
    return cells or [len(route.cells) // 2]


def covered_cells(lanes, cell, width, height):
    across, down = lanes.position(cell)
    left = max(0, across - width // 2)
    top = max(0, down - height // 2)
    columns = range(left, min(lanes.width, left + width))
    rows = range(top, min(lanes.height, top + height))
    return [lanes.cell(column, row) for row in rows for column in columns]


def hidden(place, lanes, taken, width, height):
    """How much a label would hide at a place, and how far it would sit from its link and from its middle."""
    route, index, cell, off = place
    covered = covered_cells(lanes, cell, width, height)
    shapes = sum(lanes.drawn[covered_cell] or taken[covered_cell] for covered_cell in covered)
    links = sum(lanes.is_foreign(covered_cell, route.bundle) for covered_cell in covered)
    borders = sum(any(lanes.kept_clear[axis][covered_cell] for axis in AXES) for covered_cell in covered)
    across_its_link = lanes.users[VERTICAL][route.cells[index]] != FREE
    off_centre = abs(index - len(route.cells) / 2)
    return (HIDDEN_SHAPE * shapes + HIDDEN_LINK * links + HIDDEN_BORDER * borders
            + ACROSS_ITS_LINK * across_its_link + OFF_ITS_LINK * off + OFF_CENTRE * off_centre)
