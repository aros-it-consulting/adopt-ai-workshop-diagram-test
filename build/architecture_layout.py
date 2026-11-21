"""Places the deployment model on a grid of cells, the way an architect lays a deployment out.

The regions sit side by side. In a region the VPCs are stacked, the services of the region under
the first one. In a VPC the zones are columns and the subnets are rows, so that a tier reads across
the zones. A component keeps the same place in every zone: a zone that lacks one shows a gap. The
gateways and the services of a region stand on the side of its neighbour, the internet between the
two. The cloud wraps its regions, and leaves the corner under the shorter one to the datacenter.

Every size is a number of cells, and a cell is one lane of the links (see architecture_lanes.py).
"""

from dataclasses import dataclass, field
from itertools import count
from typing import NamedTuple

PATH_SEPARATOR = "."
BOX = "box"
SUBNET = "subnet"
ZONE = "zone"
VPC = "vpc"
REGION = "region"
CLOUD = "cloud"
SITE = "site"

# An odd width puts a lane on the axis of a box: two boxes one above the other are joined straight.
BOX_WIDTH = 19
BOX_HEIGHT = 5
BOX_GAP = 5
TITLE_HEIGHT = 4
PADDING = 4
TIER_GAP = 8
ZONE_GAP = 9
VPC_GAP = 9
REGION_GAP = 12
MARGIN = 4
SITE_COLUMNS = 2


class Rectangle(NamedTuple):
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    def moved(self, across, down):
        return Rectangle(self.left + across, self.top + down, self.width, self.height)


class Shape(NamedTuple):
    """A box or a boundary of the model, placed. `cut` is the bottom right corner a boundary leaves out."""

    path: str
    label: str
    rectangle: Rectangle
    level: str
    cut: Rectangle | None = None

    def moved(self, across, down):
        cut = self.cut.moved(across, down) if self.cut else None
        return self._replace(rectangle=self.rectangle.moved(across, down), cut=cut)

    def corners(self):
        """The corners of the outline, clockwise from the top left."""
        left, top, right, bottom = self.rectangle.left, self.rectangle.top, self.rectangle.right, self.rectangle.bottom
        if self.cut is None:
            return [(left, top), (right, top), (right, bottom), (left, bottom)]
        notch = [(right, self.cut.top), (self.cut.left, self.cut.top), (self.cut.left, bottom)]
        return [(left, top), (right, top), *notch, (left, bottom)]


@dataclass
class Fragment:
    """A part of the drawing, placed from its own top left corner."""

    width: int
    height: int
    shapes: list[Shape] = field(default_factory=list)

    def moved(self, across, down):
        shapes = [shape.moved(across, down) for shape in self.shapes]
        return Fragment(self.width, self.height, shapes)


class Layout(NamedTuple):
    width: int
    height: int
    shapes: dict[str, Shape]


def lay_out(model):
    """Places the internet above the cloud, and the datacenter in the corner the cloud leaves out."""
    site_model, cloud_model = sorted(model["boundaries"], key=lambda boundary: "boundaries" in boundary)
    cloud_fragment = cloud(cloud_model).moved(MARGIN, MARGIN + BOX_HEIGHT + REGION_GAP)
    corner = corner_left_out(cloud_fragment)
    notched_cloud = cloud_fragment.shapes[0]._replace(cut=corner)
    site_fragment = site(site_model).moved(corner.left + REGION_GAP, corner.top + REGION_GAP)
    outside = row_of_boxes((), model["boxes"]).moved(corner.left - BOX_WIDTH // 2, MARGIN)
    shapes = [notched_cloud, *cloud_fragment.shapes[1:], *site_fragment.shapes, *outside.shapes]
    width = max(shape.rectangle.right for shape in shapes) + MARGIN
    height = max(shape.rectangle.bottom for shape in shapes) + MARGIN
    return Layout(width, height, {shape.path: shape for shape in shapes})


def corner_left_out(cloud_fragment):
    """The corner of the cloud under its last region, from halfway between the last two regions."""
    cloud_shape = cloud_fragment.shapes[0]
    regions = [shape.rectangle for shape in cloud_fragment.shapes if shape.level == REGION]
    left = (regions[-2].right + regions[-1].left) // 2
    top = regions[-1].bottom + PADDING
    return Rectangle(left, top, cloud_shape.rectangle.right - left, cloud_shape.rectangle.bottom - top)


def site(model):
    path = (model["id"],)
    slots = shared_slots([identifiers(model)])
    return framed(grid(path, model["boxes"], slots, SITE_COLUMNS), path, model["label"], SITE)


def cloud(model):
    path = (model["id"],)
    last = len(model["boundaries"]) - 1
    fragments = [region((*path, region_model["id"]), region_model, faces_right=index < last)
                 for index, region_model in enumerate(model["boundaries"])]
    return framed(side_by_side(fragments, REGION_GAP), path, model["label"], CLOUD)


def region(path, model, faces_right):
    """The VPCs stacked, all of one width, and the services of the region in a row under the first one."""
    slots = [tier_slots(vpc_model["boundaries"]) for vpc_model in model["boundaries"]]
    columns = max(columns_for(slots_by_tier) for slots_by_tier in slots)
    vpcs = [vpc((*path, vpc_model["id"]), vpc_model, slots_by_tier, columns, faces_right)
            for vpc_model, slots_by_tier in zip(model["boundaries"], slots)]
    services = row_of_boxes(path, model["boxes"], vpcs[0].width, faces_right)
    return framed(stacked([vpcs[0], services, *vpcs[1:]], VPC_GAP), path, model["label"], REGION)


def vpc(path, model, slots_by_tier, columns, faces_right):
    """The boxes of the VPC in a row, above its zones side by side."""
    zones = [zone((*path, zone_model["id"]), zone_model, slots_by_tier, columns)
             for zone_model in model["boundaries"]]
    columns_of_zones = side_by_side(zones, ZONE_GAP)
    gateways = row_of_boxes(path, model["boxes"], columns_of_zones.width, faces_right)
    return framed(stacked([gateways, columns_of_zones], TIER_GAP), path, model["label"], VPC)


def tier_slots(zones):
    """For each tier, in the order of the model, the place of each of its components in every zone."""
    tiers = dict.fromkeys(subnet["id"] for zone_model in zones for subnet in zone_model["boundaries"])
    return {tier: shared_slots(tier_members(zones, tier)) for tier in tiers}


def tier_members(zones, tier):
    subnets = [subnet for zone_model in zones for subnet in zone_model["boundaries"] if subnet["id"] == tier]
    return [identifiers(subnet) for subnet in subnets]


def identifiers(container):
    return [box["id"] for box in container["boxes"]]


def shared_slots(groups):
    """Gives each identifier one slot for all the groups, the lowest that no member of its groups holds."""
    slots = {}
    for identifier in dict.fromkeys(member for group in groups for member in group):
        companions = {member for group in groups if identifier in group for member in group}
        taken = {slots[member] for member in companions if member in slots}
        slots[identifier] = next(slot for slot in count() if slot not in taken)
    return slots


def columns_for(slots_by_tier):
    """As many columns as make the largest tier about as wide as it is high."""
    largest = max(len(set(slots.values())) for slots in slots_by_tier.values())
    return max(1, round(largest ** 0.5))


def zone(path, model, slots_by_tier, columns):
    subnets = {subnet["id"]: subnet for subnet in model["boundaries"]}
    rows = [tier_row(path, tier, subnets.get(tier), slots, columns) for tier, slots in slots_by_tier.items()]
    return framed(stacked(rows, TIER_GAP), path, model["label"], ZONE)


def tier_row(zone_path, tier, subnet, slots, columns):
    """The subnet of a zone on one tier, or the room it would take: the tiers line up across the zones."""
    path = (*zone_path, tier)
    boxes = subnet["boxes"] if subnet else []
    label = subnet["label"] if subnet else ""
    frame = framed(grid(path, boxes, slots, columns), path, label, SUBNET)
    if subnet is None:
        return Fragment(frame.width, frame.height)
    return frame


def row_of_boxes(path, boxes, width=0, faces_right=False):
    """The boxes in a row, from the left in their order, or from the right when the row faces right."""
    slots = {box["id"]: index for index, box in enumerate(boxes[::-1] if faces_right else boxes)}
    row = grid(path, boxes, slots, max(1, len(boxes)))
    room = max(width, row.width)
    return Fragment(room, row.height, row.moved(room - row.width if faces_right else 0, 0).shapes)


def grid(path, boxes, slots, columns):
    lines = -(-(max(slots.values(), default=0) + 1) // columns)
    shapes = [box_shape(path, box, slots[box["id"]], columns) for box in boxes]
    return Fragment(span(columns, BOX_WIDTH), span(lines, BOX_HEIGHT), shapes)


def span(number, size):
    return number * size + (number - 1) * BOX_GAP


def box_shape(parent_path, box, slot, columns):
    line, column = divmod(slot, columns)
    rectangle = Rectangle(column * (BOX_WIDTH + BOX_GAP), line * (BOX_HEIGHT + BOX_GAP), BOX_WIDTH, BOX_HEIGHT)
    return Shape(joined((*parent_path, box["id"])), box["label"], rectangle, BOX)


def framed(fragment, path, label, level):
    inside = fragment.moved(PADDING, TITLE_HEIGHT)
    width = fragment.width + 2 * PADDING
    height = fragment.height + TITLE_HEIGHT + PADDING
    boundary = Shape(joined(path), label, Rectangle(0, 0, width, height), level)
    return Fragment(width, height, [boundary, *inside.shapes])


def side_by_side(fragments, gap):
    starts = starts_of([fragment.width for fragment in fragments], gap)
    shapes = [shape for fragment, start in zip(fragments, starts) for shape in fragment.moved(start, 0).shapes]
    width = starts[-1] + fragments[-1].width
    return Fragment(width, max(fragment.height for fragment in fragments), shapes)


def stacked(fragments, gap):
    starts = starts_of([fragment.height for fragment in fragments], gap)
    shapes = [shape for fragment, start in zip(fragments, starts) for shape in fragment.moved(0, start).shapes]
    height = starts[-1] + fragments[-1].height
    return Fragment(max(fragment.width for fragment in fragments), height, shapes)


def starts_of(sizes, gap):
    starts = [0]
    for size in sizes[:-1]:
        starts.append(starts[-1] + size + gap)
    return starts


def joined(path):
    return PATH_SEPARATOR.join(path)
