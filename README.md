# Adopt'AI workshop: the diagram test

One document, several formats, the same questions: this repository measures which formats a coding
agent reads right, and what each one costs.

A benchmark runs the same test on every file, several times per model, and
writes its table in [`benchmark/results.md`](benchmark/results.md).

![The deployment of an online shop at a cloud provider, as an architect draws it](sources/2_deployment/topology.png)

*`sources/2_deployment/topology.png`: the deployment as a picture. The same folder holds it as an SVG
and as Mermaid text.*

## Contents

| Folder | Contents |
| --- | --- |
| `sources/` | Three subfolders, each one document in several formats |
| `questions/` | Two files per subfolder of `sources/`: the prompt sent for each of its files, where `<file>` stands for the file's name, and the JSON schema its answers must fit |
| `answers/` | One file per subfolder of `sources/`: the expected answers, each with its reason |
| `benchmark/` | The scripts that run the trials, score their answers and write the table; one record per trial in `results/`; the table, `results.md` |
| `build/` | The scripts that build the files of `sources/` |

Everything is in English, except the specification under test, a French document.

## The documents

The three documents describe the same online shop.

| Subfolder | Document | Formats |
| --- | --- | --- |
| `1_data_model/` | Its data model | Mermaid (`.mmd`), SVG, PNG |
| `2_deployment/` | Its deployment at a cloud provider | Mermaid (`.mmd`), SVG, PNG |
| `3_specification/` | The specification of its returns and refunds | Markdown, HTML, a good and a bad Word file, a good and a bad PDF |

- A PNG is a screenshot of its SVG. Both show the same drawing: the SVG keeps its labels as text,
  the PNG holds pixels only.
- In `2_deployment/`, `topology.svg` and its PNG are the drawing laid out for people, the way an
  architect draws it. `topology.mermaid.svg` is the drawing Mermaid makes of the `.mmd`. It is there
  to compare the two drawings, and the benchmark leaves it out.
- The good Word file is the one pandoc writes from the Markdown. The bad one holds the same facts,
  laid out the way a document passed from hand to hand ends up: headings without a heading style,
  every table pasted as screenshots, the footnotes typed by hand far from their numbers, the
  amendment as the scan of its signed page.
- The PDFs are the Word files exported by Word.

## Ask the questions yourself

The agent must find one file and nothing else. At the root of this repository it would find the
expected answers and the other formats of the document. Give it a folder that holds the file only,
at the path the questions name:

    trial=$(mktemp -d)
    mkdir -p "$trial/sources/2_deployment"
    cp sources/2_deployment/topology.png "$trial/sources/2_deployment/"
    prompt=$(sed 's/<file>/topology.png/' questions/2_deployment.md)
    (cd "$trial" && claude "$prompt")

Then compare what it answers with `answers/2_deployment.json`, and start again with `topology.svg`
and `topology.mmd`.

## Run the benchmark

It needs Linux, [mise](https://mise.jdx.dev), and `claude` and `unshare` on the PATH.

    mise install
    mise run benchmark

`mise install` is run once: it installs the Python the benchmark runs on, along with the tools that
build the sources.

The benchmark writes one JSON file per trial in `benchmark/results/`, then the table
`benchmark/results.md`. It runs only the trials that have no file there, or whose file records an
error. This repository holds the files of a full run: as it stands, the command runs no trial and
only writes the table again. To run trials again, delete their files. Each trial is a real session,
billed like any other.

### How it works

- The benchmark runs on two models, Haiku and Sonnet, both at low effort. Each file of `sources/`
  gets five trials per model.
- A trial is one `claude -p` call that finds its file and nothing else: not the other formats, not
  the expected answers, not the machine's own CLAUDE.md, plugins, MCP servers, skills and hooks.
- A trial answers as one JSON object, which a script scores against `answers/`, with no model in
  between. A partly right answer is wrong. A trial succeeds when it answers every question right,
  whatever it costs.
- A cost is net of the cost of an empty session on the same model. The relative cost is a file's
  cost as a percentage of the one of its subfolder's text format: `order_model.mmd`, `topology.mmd`
  or `spec.md`.

### The table

The table has one section per model, and in it one row per file: its success, the number of trials
that answered every question right, then its relative cost, then for each question the number of
trials that answered it right, the mean cost of the trials and their mean number of turns. The files
whose trials succeed most often come first, and among equals the cheapest first.