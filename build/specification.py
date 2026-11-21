"""Builds the specification's HTML page and its good Word file from the Markdown, with pandoc."""

from tools import run_tool

PANDOC = "pandoc"
HTML_SUFFIX = ".html"
GOOD_WORD_SUFFIX = ".good.docx"
# pandoc stamps the Word file and the entries of its archive with the time of the build, unless it
# is given one: the start of the epoch, so that the same Markdown gives the same file.
SOURCE_DATE_EPOCH = "0"
SHARED_FLAGS = [
    # The apostrophes and quotes stay as typed: a text searched in the Markdown is found in every format.
    "--from=markdown-smart",
    # The level-1 heading that opens the Markdown becomes the document's title, its sections the first level.
    "--shift-heading-level-by=-1",
    "--metadata=lang:fr",
    # One line per paragraph in the HTML, so that a search for two words never falls on a line break.
    "--wrap=none",
]
HTML_FLAGS = ["--standalone", "--embed-resources"]


def build(markdown, stylesheet):
    html = markdown.with_suffix(HTML_SUFFIX)
    good_word = markdown.with_suffix(GOOD_WORD_SUFFIX)
    stylesheet_flag = f"--css={stylesheet}"
    convert(markdown, html, *HTML_FLAGS, stylesheet_flag)
    convert(markdown, good_word)


def convert(markdown, output, *writing_flags):
    arguments = [*SHARED_FLAGS, *writing_flags, f"--output={output}", markdown]
    run_tool(PANDOC, *arguments, SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH)
