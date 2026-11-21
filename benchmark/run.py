#!/usr/bin/env python3
"""Runs the benchmark: the trials, then the table. It can be rerun: it resumes where it stopped."""
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from cases import (ANSWERS_FIELD, CONTROL_PROMPT, EFFORT, MAX_PARALLEL, RESULTS, ROOT, SOURCES, TIMEOUT_SECONDS,
                   TRIAL_TOOLS, Case, all_cases)
from report import write_table

RECORD_FIELDS = (ANSWERS_FIELD, "total_cost_usd", "usage", "num_turns", "duration_ms", "is_error")
REQUIRED_TOOLS = ("claude", "unshare")
RESULT_EVENT = "result"
ASSISTANT_EVENT = "assistant"
TOOL_USE = "tool_use"
# The folders a session finds empty and keeps to itself: where sessions write their working files, which
# they name alike, and this folder, which holds the expected answers and the other formats of each document.
PRIVATE_FOLDERS = ("/tmp", "/var/tmp", "/dev/shm", str(ROOT))


def claude_command(model: str, prompt: str, schema: str) -> list[str]:
    # --safe-mode leaves out the machine's own setup (CLAUDE.md, plugins, MCP servers, skills, hooks):
    # a session holds the built-in tools and its file, the same on every machine.
    # --json-schema has the session give its answers as JSON that fits the schema, so that a script can score them.
    # stream-json prints every event of the session: its tool calls are kept with its result.
    return ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--json-schema", schema,
            "--model", model, "--effort", EFFORT, "--allowedTools", TRIAL_TOOLS,
            "--no-session-persistence", "--safe-mode"]


def isolation_script() -> str:
    """The shell script that shuts a session in before it starts.

    It runs as the root of a new user namespace, the only user allowed to mount. It puts an empty folder over
    each private folder, puts the working folder back at its place, which /tmp hid with it, then starts the
    session as the user who runs the benchmark.
    """
    hide = [f"mount --types tmpfs tmpfs {shlex.quote(folder)}" for folder in PRIVATE_FOLDERS]
    put_back = 'mkdir --parents "$PWD" && mount --no-canonicalize --bind /proc/self/cwd "$PWD" && cd "$PWD"'
    start = f'exec unshare --user --map-user={os.getuid()} --map-group={os.getgid()} "$@"'
    return " && ".join([*hide, put_back, start])


def isolated(command: list[str]) -> list[str]:
    # Sessions run ten at a time and name their working files alike: in a shared /tmp, one reads the other's.
    return ["unshare", "--user", "--map-root-user", "--mount", "sh", "-c", isolation_script(), "sh", *command]


def tool_calls(events: list[dict]) -> list[dict]:
    """What a session ran, in order: it explains an answer, and shows a file written outside the working folder."""
    messages = [event["message"] for event in events if event.get("type") == ASSISTANT_EVENT]
    blocks = [block for message in messages for block in message["content"]]
    return [{"tool": block["name"], "input": block["input"]} for block in blocks if block["type"] == TOOL_USE]


def to_record(completed: subprocess.CompletedProcess) -> dict:
    events = [json.loads(line) for line in completed.stdout.splitlines()]
    payload = next((event for event in events if event.get("type") == RESULT_EVENT), {})
    # A session that ends well without answers is not in error: the model declined to answer, which is a result.
    failed = not payload or bool(payload.get("is_error")) or completed.returncode != 0
    record = {field: payload.get(field) for field in RECORD_FIELDS}
    error = payload.get("result") or completed.stderr
    return {**record, "tool_calls": tool_calls(events), "is_error": failed, "error": error if failed else None}


def error_record(reason: str) -> dict:
    return {**{field: None for field in RECORD_FIELDS}, "is_error": True, "error": reason}


def call_claude(command: list[str], workdir: str) -> dict:
    try:
        completed = subprocess.run(isolated(command), cwd=workdir, capture_output=True, text=True,
                                   timeout=TIMEOUT_SECONDS, stdin=subprocess.DEVNULL)
        return to_record(completed)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as error:
        return error_record(f"{type(error).__name__}: {error}")


def stage_source(case: Case, workdir: Path) -> None:
    if case.is_control:
        return
    relative = Path("sources") / case.folder / case.filename
    (workdir / relative).parent.mkdir(parents=True)
    shutil.copy2(SOURCES / case.folder / case.filename, workdir / relative)


def run_trial(case: Case) -> dict:
    # Working folder outside the repository, which the session finds empty: the trial sees its own file only.
    with tempfile.TemporaryDirectory(prefix="bench-") as workdir:
        assert not Path(workdir).resolve().is_relative_to(ROOT), "TMPDIR is inside the repository"
        stage_source(case, Path(workdir))
        return call_claude(claude_command(case.model, case.prompt, case.schema), workdir)


def warm_up(session: tuple[str, str]) -> None:
    # A session's prompt cache belongs to its model and starts at its schema, and the first session of the two
    # pays to write it: without this discarded session, the control case and a folder's first trials cost
    # several times the others.
    model, schema = session
    with tempfile.TemporaryDirectory(prefix="bench-") as workdir:
        record = call_claude(claude_command(model, CONTROL_PROMPT, schema), workdir)
    if record["is_error"]:
        print(f"warm-up in error, the first costs will be too high: {record['error']}", flush=True)


def load(case: Case) -> dict:
    if not case.result_path.exists():
        return {}
    return json.loads(case.result_path.read_text(encoding="utf-8"))


def save(case: Case, record: dict) -> None:
    temporary = case.result_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, case.result_path)  # atomic: the file is readable or absent


def is_pending(case: Case) -> bool:
    return load(case).get("is_error", True)


def process(case: Case) -> None:
    identity = {"model": case.model, "folder": case.folder, "file": case.filename, "trial": case.trial,
                "prompt": case.prompt}
    record = {**identity, **run_trial(case)}
    save(case, record)
    print(f"done: {case.result_path.name}{' (error)' if record['is_error'] else ''}", flush=True)


def main() -> None:
    missing = [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]
    if missing:
        sys.exit(f"not found on the PATH: {', '.join(missing)}")
    RESULTS.mkdir(parents=True, exist_ok=True)
    pending = [case for case in all_cases() if is_pending(case)]
    sessions = sorted({(case.model, case.schema) for case in pending})
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        list(pool.map(warm_up, sessions))
        list(pool.map(process, pending))
    write_table()
    print("table written: benchmark/results.md")


if __name__ == "__main__":
    main()
