"""Writes benchmark/results.md from benchmark/results/: one section per model, one row per file, over its trials.

The files whose trials succeed most often come first, and among equals the cheapest first.
"""
import json
from math import inf
from statistics import mean
from typing import NamedTuple

from cases import EFFORT, MODELS, RESULTS, SOURCES, TABLE, TEXT_FORMAT
from score import answer_key, verdicts

MISSING = "—"
PERCENT = 100
HEADER_START = ["File", "Success", "Relative cost"]
HEADER_END = ["Average cost ($)", "Average turns"]


class FileResult(NamedTuple):
    """What the trials of one file gave: the trials that answered every question right, for each question the
    trials that answered it right, and the mean cost."""

    filename: str
    right_trials: int
    right_answers: list[int]
    trials: int
    cost: float | None
    turns: float | None

def load_records() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(RESULTS.glob("*.json"))]


def control_cost(records: list[dict]) -> float | None:
    costs = [record["total_cost_usd"] for record in records
             if record["folder"] is None and not record["is_error"]]
    return costs[0] if costs else None


def average_cost(trials: list[dict], control: float | None) -> float | None:
    """The mean cost of the trials that answered, net of the control case."""
    costs = [trial["total_cost_usd"] - control for trial in trials if not trial["is_error"] and control is not None]
    return mean(costs) if costs else None


def average_turns(trials: list[dict]) -> float | None:
    turns = [trial["num_turns"] for trial in trials if trial["num_turns"] is not None]
    return mean(turns) if turns else None


def right_answers(trials: list[dict], number: str) -> int:
    """The number of trials that answered a question right: a trial in error is not one."""
    answers = [verdicts(trial).get(number, False) for trial in trials]
    return answers.count(True)


def succeeds(trial: dict) -> bool:
    """Whether a trial answers every question right: a trial in error does not."""
    answers = verdicts(trial)
    return bool(answers) and all(answers.values())


def format_fraction(count: int, trials: int) -> str:
    return f"{count}/{trials}"


def format_number(value: float | None, decimals: int) -> str:
    return MISSING if value is None else f"{value:.{decimals}f}"


def format_relative(cost: float | None, reference: float | None) -> str:
    if cost is None or not reference:
        return MISSING
    return f"{cost / reference * PERCENT:.0f}%"


def result_of(filename: str, trials: list[dict], numbers: list[str], control: float | None) -> FileResult:
    counts = [right_answers(trials, number) for number in numbers]
    right_trials = [succeeds(trial) for trial in trials].count(True)
    cost = average_cost(trials, control)
    return FileResult(filename, right_trials, counts, len(trials), cost, average_turns(trials))


def row(result: FileResult, reference: float | None) -> str:
    questions = [format_fraction(count, result.trials) for count in result.right_answers]
    cells = [result.filename, format_fraction(result.right_trials, result.trials),
             format_relative(result.cost, reference), *questions,
             format_number(result.cost, 4), format_number(result.turns, 1)]
    return "| " + " | ".join(cells) + " |"


def rank(result: FileResult) -> tuple:
    """Sorts the files whose trials succeed most often first, then the cheapest first; a file without a cost
    comes last among its equals."""
    cost = result.cost if result.cost is not None else inf
    return (-result.right_trials, cost, result.filename)


def table(folder: str, records: list[dict], control: float | None) -> str:
    own = [record for record in records if record["folder"] == folder]
    numbers = sorted(answer_key(folder), key=int)
    filenames = sorted({record["file"] for record in own})
    results = [result_of(filename, [record for record in own if record["file"] == filename], numbers, control)
               for filename in filenames]
    reference = next((result.cost for result in results if result.filename == TEXT_FORMAT[folder]), None)
    header = [*HEADER_START, *(f"Q{number}" for number in numbers), *HEADER_END]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += [row(result, reference) for result in sorted(results, key=rank)]
    return f"### {folder}\n\n" + "\n".join(lines)


def section(model: str, records: list[dict]) -> str:
    own = [record for record in records if record["model"] == model]
    control = control_cost(own)
    folders = sorted(path.name for path in SOURCES.iterdir() if path.is_dir())
    tables = [table(folder, own, control) for folder in folders]
    net = f"The costs are net of the control case of {model}: ${format_number(control, 4)}."
    return "\n\n".join([f"## {model}, {EFFORT} effort", *tables, net])


def missing_trials(records: list[dict]) -> list[str]:
    return [f"{record['file']} ({record['model']}, trial {record['trial']})" for record in records
            if record["folder"] is not None and record["is_error"]]


def footer(records: list[dict]) -> str:
    lines = ["- Success is the number of trials that answered every question right.",
             "- The relative cost compares the cost with the one of the text format of the folder, at 100%.",
             "- A question shows the number of trials that answered it right.",
             "- The cost is the mean of the trials, net of the control case of their model."]
    missing = missing_trials(records)
    if missing:
        lines.append(f"- In error, counted as not right: {', '.join(missing)}. "
                     "Run the benchmark again to complete them.")
    return "\n".join(lines)


def write_table() -> None:
    records = load_records()
    sections = [section(model, records) for model in MODELS]
    text = "# Results\n\n" + "\n\n".join(sections) + "\n\n" + footer(records) + "\n"
    TABLE.write_text(text, encoding="utf-8")
