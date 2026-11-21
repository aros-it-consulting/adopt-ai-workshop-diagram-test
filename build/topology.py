"""Reads the deployment model and writes it as Mermaid.

The model (topology.yaml) is a tree of boundaries holding boxes, and a list of links between boxes
or boundaries, each end named by its dotted path from the root. The Mermaid is a flowchart: one
subgraph per boundary, nested as in the model, then the links. A link is written after every box,
outside every subgraph: Mermaid draws a box in the first subgraph whose block names it, whatever
subgraph declares it.
"""

import textwrap
from pathlib import Path

import yaml

MODEL_ENCODING = "utf-8"
MODEL_PATH_SEPARATOR = "."
MERMAID_PATH_SEPARATOR = "_"
INDENT = "  "
HEADER = "flowchart TB"
BOX = '{path}["{label}"]'
BOUNDARY_OPENING = 'subgraph {path}["{label}"]'
BOUNDARY_CLOSING = "end"
ARROW = "-->"
TWO_WAY_ARROW = "<-->"
LINK = "{source} {arrow} {target}"
LABELLED_LINK = '{source} {arrow}|"{label}"| {target}'


def load(path):
    text = Path(path).read_text(encoding=MODEL_ENCODING)
    return yaml.safe_load(text)


def to_mermaid(model):
    lines = [HEADER, *write_children(model, parent_path=())]
    lines += [write_link(link) for link in model["links"]]
    return "\n".join(lines) + "\n"


def write_children(container, parent_path):
    lines = [write_node(BOX, box, parent_path) for box in container.get("boxes", [])]
    for boundary in container.get("boundaries", []):
        lines += write_boundary(boundary, parent_path)
    return lines


def write_boundary(boundary, parent_path):
    path = (*parent_path, boundary["id"])
    opening = write_node(BOUNDARY_OPENING, boundary, parent_path)
    closing = indent(BOUNDARY_CLOSING, parent_path)
    return [opening, *write_children(boundary, path), closing]


def write_node(template, node, parent_path):
    path = MERMAID_PATH_SEPARATOR.join((*parent_path, node["id"]))
    text = template.format(path=path, label=node["label"])
    return indent(text, parent_path)


def write_link(link):
    source = link["from"].replace(MODEL_PATH_SEPARATOR, MERMAID_PATH_SEPARATOR)
    target = link["to"].replace(MODEL_PATH_SEPARATOR, MERMAID_PATH_SEPARATOR)
    arrow = TWO_WAY_ARROW if link.get("both_ways") else ARROW
    if "label" not in link:
        return LINK.format(source=source, target=target, arrow=arrow)
    return LABELLED_LINK.format(source=source, target=target, arrow=arrow, label=link["label"])


def indent(text, parent_path):
    return textwrap.indent(text, INDENT * len(parent_path))
