"""Routes the links of the deployment drawing on the lanes, the shortest first.

A link runs straight, turns at right angles and keeps its lane to itself. It may cross another link,
never where either of the two turns, and it would rather go round a boundary than through it. The
links that share an end and a label are drawn as one bundle: each joins the route of those drawn
before it, as lines join a bus, and they reach the shared end together.
"""

from collections import Counter
from heapq import heappop, heappush
from typing import NamedTuple

from architecture_lanes import FREE, OUTSIDE, axis_of, opposite
from architecture_layout import PATH_SEPARATOR

SOURCE, TARGET = "from", "to"
STEP_COST = 1
BEND_COST = 8
CROSSING_COST = 3
# Paid twice for each border crossed, once on each side of it.
BORDER_COST = 3
# Paid on each cell of a subnet that holds neither end of the link.
FOREIGN_SUBNET_COST = 4
# A lane shared with another bundle is the last resort: the build counts them, and expects none.
OVERLAP_COST = 400
# Paid on each cell a link follows its bundle on: it joins the bundle near the shared end, not at the first chance.
FOLLOWING_COST = 0.5
TURNS = (0, 1, 3)
# Stands for the direction of a link that has joined its bundle.
JOINED = -1


class Route(NamedTuple):
    """The cells of a link from its source to its target, and the cell where it joins its bundle."""

    link: dict
    cells: list[int]
    bundle: int
    joint: int | None


def route_all(model, layout, lanes):
    links = model["links"]
    bundles = bundles_of(links)
    router = Router(layout, lanes)
    order = sorted(range(len(links)), key=lambda index: (length_of(links[index], layout), index))
    routes = {index: router.route(links[index], *bundles[index]) for index in order}
    return [routes[index] for index in range(len(links))]


def length_of(link, layout):
    source = layout.shapes[link[SOURCE]].rectangle
    target = layout.shapes[link[TARGET]].rectangle
    across = abs(source.left + source.right - target.left - target.right)
    down = abs(source.top + source.bottom - target.top - target.bottom)
    return across + down


def bundles_of(links):
    """For each link, the number of its bundle and the end it shares with it, if any."""
    targets = Counter((link.get("label"), link[TARGET]) for link in links)
    sources = Counter((link.get("label"), link[SOURCE]) for link in links)
    numbers = {}
    bundles = []
    for index, link in enumerate(links):
        shared = shared_end(link, targets, sources)
        key = (shared, link.get("label"), link[shared]) if shared else index
        bundles.append((numbers.setdefault(key, len(numbers) + 1), shared))
    return bundles


def shared_end(link, targets, sources):
    label = link.get("label")
    if link.get("both_ways"):
        return None
    if targets[(label, link[TARGET])] > 1:
        return TARGET
    if sources[(label, link[SOURCE])] > 1:
        return SOURCE
    return None


class Router:
    def __init__(self, layout, lanes):
        self.layout = layout
        self.lanes = lanes
        # For each bundle, the cell that follows each of its cells on the way to the shared end.
        self.trees = {}

    def route(self, link, bundle, shared):
        """Searches from the end the link has to itself to the end it shares, then reads the link forward."""
        far, near = (TARGET, SOURCE) if shared == SOURCE else (SOURCE, TARGET)
        tree = self.trees.setdefault(bundle, {})
        goal = self.layout.shapes[link[near]]
        arrivals = {cell: opposite(direction) for cell, direction in self.free_ports(goal)}
        search = Search(self.lanes, bundle, arrivals, tree, goal.rectangle, self.subnets_of(link))
        cells = search.run(self.free_ports(self.layout.shapes[link[far]]), link)
        joint = cells[-1] if cells[-1] in tree else None
        whole = cells + rest_of(tree, cells[-1])
        self.lanes.occupy(whole, bundle)
        tree.update(zip(whole, whole[1:] + [None]))
        return Route(link, whole[::-1] if shared == SOURCE else whole, bundle, joint)

    def subnets_of(self, link):
        """The numbers of the subnets the link serves: its two ends and every boundary that holds one of them."""
        served = {OUTSIDE}
        for end in (link[SOURCE], link[TARGET]):
            segments = end.split(PATH_SEPARATOR)
            paths = [PATH_SEPARATOR.join(segments[:length]) for length in range(1, len(segments) + 1)]
            served.update(self.lanes.numbers[path] for path in paths)
        return served

    def free_ports(self, shape):
        users = self.lanes.users
        return [(cell, direction) for cell, direction in self.lanes.ports(shape)
                if users[axis_of(direction)][cell] == FREE]

def rest_of(tree, cell):
    """The cells that follow a cell of a bundle on the way to the shared end."""
    rest = []
    while tree.get(cell) is not None:
        cell = tree[cell]
        rest.append(cell)
    return rest


class Search:
    """One search of the cheapest way from the ports of an end to the ports of the other, or to the bundle."""

    def __init__(self, lanes, bundle, arrivals, tree, goal, served_subnets):
        self.lanes = lanes
        self.bundle = bundle
        self.arrivals = arrivals
        self.tree = tree
        self.served_subnets = served_subnets
        self.goals = [goal, *self.tree_bounds()]
        self.costs = {}
        self.origins = {}
        self.queue = []

    def tree_bounds(self):
        if not self.tree:
            return []
        positions = [self.lanes.position(cell) for cell in self.tree]
        columns = [across for across, _ in positions]
        rows = [down for _, down in positions]
        return [(min(columns), min(rows), max(columns) - min(columns) + 1, max(rows) - min(rows) + 1)]

    def run(self, starts, link):
        for start in starts:
            self.push(0, start, None)
        while self.queue:
            _, cost, state = heappop(self.queue)
            if self.is_end(state):
                return self.cells_to(state)
            if cost == self.costs[state]:
                self.join(cost, state)
                self.advance(cost, state)
        raise SystemExit(f"No way found for the link from {link[SOURCE]} to {link[TARGET]}.")

    def push(self, cost, state, origin):
        if cost >= self.costs.get(state, cost + 1):
            return
        self.costs[state] = cost
        self.origins[state] = origin
        heappush(self.queue, (cost + self.distance_left(state[0]), cost, state))

    def distance_left(self, cell):
        across, down = self.lanes.position(cell)
        return min(distance_to(goal, across, down) for goal in self.goals)

    def is_end(self, state):
        cell, direction = state
        return direction == JOINED or self.arrivals.get(cell) == direction

    def join(self, cost, state):
        """Offers the link, arrived on a cell of its bundle, to follow the bundle to the shared end."""
        cell, direction = state
        if self.origins[state] is not None and self.joins(cell, direction):
            following = FOLLOWING_COST * len(rest_of(self.tree, cell))
            self.push(cost + following, (cell, JOINED), state)

    def joins(self, cell, direction):
        """Whether the link can follow its bundle from a cell: the cell is on it, and the link does not face it."""
        if cell not in self.tree:
            return False
        following = self.tree[cell]
        return following is None or self.lanes.steps[opposite(direction)] != following - cell

    def advance(self, cost, state):
        cell, direction = state
        may_turn = not self.lanes.is_foreign(cell, self.bundle)
        for turn in TURNS if may_turn else TURNS[:1]:
            heading = (direction + turn) % len(self.lanes.steps)
            following = cell + self.lanes.steps[heading]
            price = self.price(following, heading)
            if price is not None:
                self.push(cost + price + BEND_COST * bool(turn), (following, heading), state)

    def price(self, cell, heading):
        """The cost of one step onto a cell, or None when the cell cannot be stepped on."""
        axis = axis_of(heading)
        if self.arrivals.get(cell) == heading or cell in self.tree:
            return STEP_COST
        if self.lanes.closed[cell] or self.lanes.kept_clear[axis][cell]:
            return None
        along = self.lanes.users[axis][cell] not in (FREE, self.bundle)
        across = self.lanes.users[1 - axis][cell] not in (FREE, self.bundle)
        border = self.lanes.kept_clear[1 - axis][cell]
        foreign = self.lanes.subnets[cell] not in self.served_subnets
        return (STEP_COST + OVERLAP_COST * along + CROSSING_COST * across + BORDER_COST * border
                + FOREIGN_SUBNET_COST * foreign)

    def cells_to(self, state):
        cells = []
        while state is not None:
            cells.append(state[0])
            state = self.origins[state]
        return list(dict.fromkeys(cells[::-1]))


def distance_to(rectangle, across, down):
    left, top, width, height = rectangle
    beside = max(left - across, 0, across - (left + width - 1))
    beyond = max(top - down, 0, down - (top + height - 1))
    return beside + beyond
