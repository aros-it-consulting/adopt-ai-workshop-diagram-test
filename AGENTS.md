# Working on the diagram test

This repository measures which formats of a document a coding agent reads right, and what each one
costs. [`README.md`](README.md) describes its folders and its documents, and how the benchmark is
run and read: read it first. This file holds what it takes to change the repository.

## Tools

[mise](https://mise.jdx.dev) installs the tools, listed in `mise.toml`: Python, uv, Mermaid's CLI,
pandoc and a headless Chrome. Run `mise install` once.

| Command | What it does |
| --- | --- |
| `mise run benchmark` | Runs the trials not done yet, then writes `benchmark/results.md` |
| `mise exec -- uv run build/build.py` | Builds the diagrams, the HTML page and the good Word file |
| `mise exec -- uv run build/degrade_docx.py` | Builds the bad Word file |

The scripts of `benchmark/` use Python's standard library only. `build.py` and `degrade_docx.py`
declare their dependencies in their header, which `uv run` installs. There is no test suite: the
checks are the ones given below, for the benchmark and for the build.

## The benchmark

`cases.py` holds the constants and lists the cases, `run.py` runs the trials, `score.py` scores
their answers and `report.py` writes the table.

A trial is a real session, billed like any other: do not run trials, nor delete their records,
unless asked to. With every record there, `mise run benchmark` runs no trial and only writes the
table again: it checks a change to `score.py` or `report.py` for free.

### Trials

- Every file of a subfolder of `sources/` is a case, unless `NOT_A_CASE` names it, as it does
  `topology.mermaid.svg`: a file added there gets its trials at the next run. A new subfolder also
  needs its prompt and its schema in `questions/`, its expected answers in `answers/` and its text
  format in `TEXT_FORMAT`.
- Trials run ten at a time. A call that takes more than five minutes is recorded as an error.
- A trial runs in safe mode (`--safe-mode`), which leaves out the machine's own setup.
- Each trial is shut in its own mount namespace (`unshare`, Linux only): it finds `/tmp`, `/var/tmp`
  and `/dev/shm` empty and keeps them to itself, and it finds this repository empty. Trials name
  their working files alike: in a shared `/tmp`, one read what another had extracted from another
  format.
- A trial's record keeps its tool calls, in order: they explain an answer.
- A trial runs again when its record is missing or in error, and only then. The benchmark does not
  notice a file of `sources/` or of `questions/` that changes: the table keeps the trials of the
  old one until their records are deleted.

### Scoring

- A trial's session checks its answers against the schema of `questions/` (`--json-schema`).
- `score.py` compares names without their case or their spacing, and a list as a set unless the
  expected answer says its order counts (`ordered`). An expected answer can also name the items a
  list may hold or leave out (`tolerated`).
- Every answer of a trial that declines to answer is wrong.
- An expected answer that changes re-scores the stored trials at the next table.

### Costs

- A control case, a prompt that only replies "ok", gives for each model the cost of an empty session
  that answers through a schema, which is subtracted from every trial of that model.
- Before the trials, one discarded session per model and schema writes its prompt cache. Without it,
  the first sessions of a schema pay for that write: the control case and a folder's first trials
  would cost several times the others.

## The sources

`sources/1_data_model/order_model.mmd`, `build/topology.yaml` and `sources/3_specification/spec.md`
are the sources of the diagrams and of the specification's HTML page and Word files. The other files
of `sources/` are built from them: a change goes in these three, or in the scripts of `build/`. The
deployment model gives both its Mermaid text (`build/topology.py`) and the architect's drawing
(`build/architecture.py`), which the build stops on if two links ever have to share a lane.

- `build.py` builds the diagrams, the HTML page and the good Word file: the same sources give the
  same files, byte for byte. After a build, `git status` shows the files the change alters, and no
  other.
- `degrade_docx.py` builds the bad Word file, with the same contents at every run but new dates in
  its zip: git shows `spec.bad.docx` as modified even when nothing changed. Keep the rebuilt file
  only when its contents had to change.
- No script builds the PDFs: a person exports them from the Word files, with Word. A Word file that
  changes leaves its PDF out of date until then.
