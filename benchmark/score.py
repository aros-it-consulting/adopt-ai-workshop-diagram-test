"""Scores a trial with no model in between: its answers against the expected ones of answers/, question by question.

Names are compared without their case or their spacing. A list is compared as a set, unless the expected
answer says its order counts. A partly right answer is wrong.
"""
import json
import re
from functools import cache

from cases import ANSWERS, ANSWERS_FIELD

EXPECTED = "expected"
ORDERED = "ordered"
TOLERATED = "tolerated"
SPACING = re.compile(r"\s+")
SINGLE_SPACE = " "


@cache
def answer_key(folder: str) -> dict:
    """The expected answers of a folder, by question number."""
    return json.loads((ANSWERS / f"{folder}.json").read_text(encoding="utf-8"))


def canonical(value, ordered: bool):
    """A value in the form two answers are compared in."""
    if isinstance(value, str):
        return SPACING.sub(SINGLE_SPACE, value).strip().casefold()
    if isinstance(value, dict):
        return {name: canonical(item, ordered) for name, item in value.items()}
    if isinstance(value, list):
        return canonical_list(value, ordered)
    return value


def canonical_list(items: list, ordered: bool) -> list[str]:
    texts = [json.dumps(canonical(item, ordered), sort_keys=True) for item in items]
    if ordered:
        return texts
    return sorted(set(texts))


def is_right(answer, expectation: dict) -> bool:
    ordered = expectation.get(ORDERED, False)
    given = canonical(answer, ordered)
    tolerated = canonical(expectation.get(TOLERATED, []), ordered)
    if isinstance(given, list):
        given = [item for item in given if item not in tolerated]
    return given == canonical(expectation[EXPECTED], ordered)


def verdicts(trial: dict) -> dict[str, bool]:
    """Whether a trial answers each question right; nothing for a trial in error, which was not put the questions.

    A session that declined to answer is wrong on every question.
    """
    if trial["is_error"]:
        return {}
    answers = trial[ANSWERS_FIELD] or {}
    return {number: is_right(answers.get(number), expectation)
            for number, expectation in answer_key(trial["folder"]).items()}
