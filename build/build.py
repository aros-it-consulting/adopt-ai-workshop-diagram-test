#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11", "pyyaml>=6"]
# ///
"""Builds what the group receives in sources/ from the three sources of the workshop.

The data model (order_model.mmd) is rendered by Mermaid. The deployment (topology.yaml) is written
as Mermaid, which Mermaid renders too, and drawn the way an architect lays it out (architecture.py):
the text an agent reads best, the drawing Mermaid makes of it, and the drawing made for people. The
data model and the architect's drawing then exist as an SVG and as a PNG. The specification
(spec.md) becomes one HTML page and the good Word file, with pandoc.

Mermaid's CLI, pandoc and the headless Chrome are installed by mise (see mise.toml at the project
root). Run from the project root, without argument:

    mise exec -- uv run build/build.py

The same sources give the same files, byte for byte.
"""

import tempfile
from pathlib import Path

import architecture
import diagrams
import specification
import topology

BUILD = Path(__file__).resolve().parent
SOURCES = BUILD.parent / "sources"
DATA_MODEL = SOURCES / "1_data_model" / "order_model.mmd"
SVG_SUFFIX = ".svg"
TOPOLOGY_MODEL = BUILD / "topology.yaml"
DEPLOYMENT = SOURCES / "2_deployment"
TOPOLOGY_MERMAID = DEPLOYMENT / "topology.mmd"
TOPOLOGY_MERMAID_SVG = DEPLOYMENT / "topology.mermaid.svg"
TOPOLOGY_SVG = DEPLOYMENT / "topology.svg"
SPECIFICATION = SOURCES / "3_specification" / "spec.md"
STYLESHEET = BUILD / "spec.css"
ENCODING = "utf-8"


def build_data_model(work_directory):
    svg = DATA_MODEL.with_suffix(SVG_SUFFIX)
    diagrams.render_mermaid(DATA_MODEL, svg, work_directory)
    diagrams.export_png(svg)


def build_deployment(work_directory):
    model = topology.load(TOPOLOGY_MODEL)
    mermaid = topology.to_mermaid(model)
    drawing = architecture.draw(model)
    DEPLOYMENT.mkdir(exist_ok=True)
    TOPOLOGY_MERMAID.write_text(mermaid, encoding=ENCODING)
    diagrams.render_mermaid(TOPOLOGY_MERMAID, TOPOLOGY_MERMAID_SVG, work_directory)
    TOPOLOGY_SVG.write_text(drawing, encoding=ENCODING)
    diagrams.export_png(TOPOLOGY_SVG)


def main():
    with tempfile.TemporaryDirectory() as temporary_directory:
        work_directory = Path(temporary_directory)
        build_data_model(work_directory)
        build_deployment(work_directory)
    specification.build(SPECIFICATION, STYLESHEET)


if __name__ == "__main__":
    main()
