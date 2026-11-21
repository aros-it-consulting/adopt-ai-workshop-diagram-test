"""The lanes the links of the deployment drawing run on: one per cell of the layout and per axis.

A cell is closed when a box, the ring of cells around a box or the title of a boundary stands on
it. A lane along the border of a boundary is kept clear, so that no link is mistaken for a border.
Every other lane holds one bundle of links at most, which the routes read and write here. Each cell
also knows the subnet it lies in: a link has no business in a subnet it does not serve.
"""

from math import ceil

from architecture_layout import BOX, SUBNET

EAST, SOUTH, WEST, NORTH = range(4)
DIRECTIONS = (EAST, SOUTH, WEST, NORTH)
HORIZONTAL, VERTICAL = 0, 1
AXES = (HORIZONTAL, VERTICAL)
FREE = 0
OUTSIDE = 0

CELL_PIXELS = 8
TITLE_CHARACTER_PIXELS = 7.5
TITLE_ROWS = range(1, 3)
TITLE_INSET = 1
# A box takes a link every two cells: two arrowheads side by side stay apart.
BOX_PORT_STEP = 2
BOX_PORT_INSET = 1
BOUNDARY_PORT_STEP = 1
BOUNDARY_PORT_INSET = 2


def axis_of(direction):
    return direction % len(AXES)


def opposite(direction):
    return (direction + 2) % len(DIRECTIONS)


class Lanes:
    def __init__(self, layout):
        self.width = layout.width
        self.height = layout.height
        self.steps = (1, self.width, -1, -self.width)
        cells = self.width * self.height
        self.closed = bytearray(cells)
        self.drawn = bytearray(cells)
        self.subnets = [OUTSIDE] * cells
        self.kept_clear = [bytearray(cells) for _ in AXES]
        self.users = [[FREE] * cells for _ in AXES]
        self.shared = 0
        self.close_frame()
        for number, shape in enumerate(layout.shapes.values(), start=1):
            self.take(shape, number)
        self.numbers = {path: number for number, path in enumerate(layout.shapes, start=1)}

    def cell(self, across, down):
        return down * self.width + across

    def position(self, cell):
        down, across = divmod(cell, self.width)
        return across, down

    def close_frame(self):
        last_row = self.height - 1
        last_column = self.width - 1
        self.close(0, 0, self.width, 1)
        self.close(0, last_row, self.width, 1)
        self.close(0, 0, 1, self.height)
        self.close(last_column, 0, 1, self.height)

    def close(self, left, top, width, height):
        self.mark(self.closed, left, top, width, height)

    def take(self, shape, number):
        rectangle = shape.rectangle
        if shape.level == BOX:
            self.close(rectangle.left - 1, rectangle.top - 1, rectangle.width + 2, rectangle.height + 2)
            self.mark(self.drawn, *rectangle)
            return
        title = (rectangle.left + TITLE_INSET, rectangle.top + TITLE_ROWS.start, self.title_width(shape), len(TITLE_ROWS))
        self.close(*title)
        self.mark(self.drawn, *title)
        self.keep_borders_clear(shape.corners())
        if shape.level == SUBNET:
            self.fill(self.subnets, rectangle, number)

    def title_width(self, shape):
        return ceil(len(shape.label) * TITLE_CHARACTER_PIXELS / CELL_PIXELS)

    def fill(self, cells, rectangle, value):
        for down in range(rectangle.top, rectangle.bottom):
            start = self.cell(rectangle.left, down)
            cells[start:start + rectangle.width] = [value] * rectangle.width

    def keep_borders_clear(self, corners):
        for start, end in zip(corners, corners[1:] + corners[:1]):
            self.keep_border_clear(start, end)

    def keep_border_clear(self, start, end):
        """Keeps the two lanes along a border clear: the one inside the boundary and the one outside."""
        (left, right), (top, bottom) = sorted((start[0], end[0])), sorted((start[1], end[1]))
        if top == bottom:
            self.mark(self.kept_clear[HORIZONTAL], left - 1, top - 1, right - left + 2, 2)
            return
        self.mark(self.kept_clear[VERTICAL], left - 1, top - 1, 2, bottom - top + 2)

    def mark(self, lanes, left, top, width, height):
        for down in range(top, top + height):
            start = self.cell(left, down)
            lanes[start:start + width] = b"\x01" * width

    def ports(self, shape):
        """The cells a link leaves a shape from, each with the direction that leads away from the shape."""
        rectangle = shape.rectangle
        step, inset = (BOX_PORT_STEP, BOX_PORT_INSET) if shape.level == BOX else (BOUNDARY_PORT_STEP, BOUNDARY_PORT_INSET)
        columns = range(rectangle.left + inset, rectangle.right - inset, step)
        rows = range(rectangle.top + inset, rectangle.bottom - inset, step)
        above = [(self.cell(across, rectangle.top - 1), NORTH) for across in columns]
        below = [(self.cell(across, rectangle.bottom), SOUTH) for across in columns]
        before = [(self.cell(rectangle.left - 1, down), WEST) for down in rows]
        after = [(self.cell(rectangle.right, down), EAST) for down in rows]
        return above + below + before + after

    def is_foreign(self, cell, bundle):
        """Whether another bundle already runs on the cell, along either axis."""
        return any(self.users[axis][cell] not in (FREE, bundle) for axis in AXES)

    def occupy(self, cells, bundle):
        """Gives the lanes under a route to its bundle, and counts those another bundle already held."""
        for cell, following in zip(cells, cells[1:]):
            axis = HORIZONTAL if abs(following - cell) == 1 else VERTICAL
            self.shared += sum(self.users[axis][step] not in (FREE, bundle) for step in (cell, following))
            self.users[axis][cell] = bundle
            self.users[axis][following] = bundle
