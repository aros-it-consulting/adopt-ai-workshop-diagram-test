"""Types text into a Word paragraph as runs of direct formatting.

The text comes from pandoc's HTML: an element's text, its line breaks and its
footnote references, typed as superscript numbers. The terms a reader of the
specification searches for (the gift card, the rule identifiers, the status
codes) are cut into three runs, the middle one flagged as not to be
spell-checked: Word shows the word whole, the file's XML never holds it in
one piece.
"""

import re
from dataclasses import dataclass, replace

from docx.shared import Length, RGBColor

# Upper-case words are the status codes of the specification's annex A.
SPLIT_TERMS = re.compile(r"((?i:cartes? cadeaux?)|RG-\d\d|[A-Z][A-Z_]{3,})")
RUNS_PER_TERM = 3
LINE_BREAK_TAG = "br"
# pandoc ends the line after each <br />: the break is already typed.
HTML_LINE_END = "\n"


@dataclass(frozen=True)
class Look:
    """The direct formatting of a run; None leaves a property to the paragraph's style."""

    bold: bool | None = None
    size: Length | None = None
    color: RGBColor | None = None
    superscript: bool | None = None
    no_proof: bool | None = None


def add_run(paragraph, text, look):
    run = paragraph.add_run(text)
    run.bold = look.bold
    run.font.size = look.size
    run.font.color.rgb = look.color
    run.font.superscript = look.superscript
    run.font.no_proof = look.no_proof


def split_term(term):
    first_cut = len(term) // RUNS_PER_TERM
    second_cut = len(term) - first_cut
    return term[:first_cut], term[first_cut:second_cut], term[second_cut:]


def write_term(paragraph, term, look):
    unchecked = replace(look, no_proof=True)
    head, middle, tail = split_term(term)
    add_run(paragraph, head, look)
    add_run(paragraph, middle, unchecked)
    add_run(paragraph, tail, look)


def write_fragment(paragraph, fragment, look):
    if SPLIT_TERMS.fullmatch(fragment):
        write_term(paragraph, fragment, look)
        return
    add_run(paragraph, fragment, look)


def write_text(paragraph, text, look):
    typed = (text or "").replace(HTML_LINE_END, "")
    fragments = filter(None, SPLIT_TERMS.split(typed))
    for fragment in fragments:
        write_fragment(paragraph, fragment, look)


def write_child(paragraph, child, look):
    if child.tag == LINE_BREAK_TAG:
        paragraph.add_run().add_break()
        return
    reference_look = replace(look, superscript=True)
    write_text(paragraph, child.text_content(), reference_look)


def write_inlines(paragraph, element, look):
    """Types an element of pandoc's HTML: its text, its line breaks, its footnote references."""
    write_text(paragraph, element.text, look)
    for child in element:
        write_child(paragraph, child, look)
        write_text(paragraph, child.tail, look)
