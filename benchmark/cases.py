"""Paths, constants and the list of the benchmark's cases."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
QUESTIONS = ROOT / "questions"
ANSWERS = ROOT / "answers"
RESULTS = ROOT / "benchmark" / "results"
TABLE = ROOT / "benchmark" / "results.md"

# The benchmark runs once per model, each with its own control case and its own section of the table.
MODELS = ("haiku", "sonnet")
EFFORT = "low"
TRIAL_TOOLS = "Read,Bash,Write"
MAX_PARALLEL = 10
TIMEOUT_SECONDS = 300
SOURCE_TRIALS = 5
CONTROL_TRIAL = 1
CONTROL_PROMPT = 'Reply "ok", without reading any file or running any command.'
# The control case answers through a schema too: what a schema adds to a session is in the cost it gives.
CONTROL_SCHEMA = '{"type": "object", "properties": {"reply": {"type": "string"}}, "required": ["reply"]}'
# The field of a session's output, and of a trial's record, that holds the answers.
ANSWERS_FIELD = "structured_output"
FILENAME_PLACEHOLDER = "<file>"

NOT_A_CASE = {("2_deployment", "topology.mermaid.svg")}
# The text format of each subfolder: the reference of the relative cost.
TEXT_FORMAT = {
    "1_data_model": "order_model.mmd",
    "2_deployment": "topology.mmd",
    "3_specification": "spec.md",
}


@dataclass(frozen=True)
class Case:
    """One trial of a file of sources/ on a model, or its control case (folder and filename set to None)."""

    model: str
    folder: str | None
    filename: str | None
    trial: int

    @property
    def is_control(self) -> bool:
        return self.folder is None

    @property
    def result_path(self) -> Path:
        if self.is_control:
            return RESULTS / f"{self.model}__control__{self.trial}.json"
        return RESULTS / f"{self.model}__{self.folder}__{self.filename}__{self.trial}.json"

    @property
    def prompt(self) -> str:
        if self.is_control:
            return CONTROL_PROMPT
        template = (QUESTIONS / f"{self.folder}.md").read_text(encoding="utf-8")
        return template.replace(FILENAME_PLACEHOLDER, self.filename)

    @property
    def schema(self) -> str:
        if self.is_control:
            return CONTROL_SCHEMA
        return (QUESTIONS / f"{self.folder}.schema.json").read_text(encoding="utf-8")


def cases_of_folder(model: str, folder: Path) -> list[Case]:
    files = sorted(path.name for path in folder.iterdir() if path.is_file())
    return [
        Case(model, folder.name, filename, trial)
        for filename in files
        if (folder.name, filename) not in NOT_A_CASE
        for trial in range(1, SOURCE_TRIALS + 1)
    ]


def cases_of_model(model: str) -> list[Case]:
    folders = sorted(path for path in SOURCES.iterdir() if path.is_dir())
    cases = [Case(model, None, None, CONTROL_TRIAL)]
    for folder in folders:
        cases.extend(cases_of_folder(model, folder))
    return cases


def all_cases() -> list[Case]:
    return [case for model in MODELS for case in cases_of_model(model)]
