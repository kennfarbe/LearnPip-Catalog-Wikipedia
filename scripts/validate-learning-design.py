#!/usr/bin/env python3
"""Learning-design gate for the first playful Wikipedia catalog."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import zipfile

ALLOWED_AGE_BANDS = {"10-12", "13-15"}
MAX_PROMPT = 240
MAX_ANSWER = 180
MIN_EXPLANATION = 40
MAX_EXPLANATION = 600


def fail(message: str) -> None:
    raise SystemExit("Lernzielprüfung abgelehnt: " + message)


def main() -> None:
    if len(sys.argv) != 2:
        fail("genau ein ZIP-Pfad ist erforderlich")

    path = Path(sys.argv[1])
    if not path.is_file():
        fail("Paket fehlt")

    try:
        with zipfile.ZipFile(path) as archive:
            questions = json.loads(
                archive.read("questions.json").decode("utf-8")
            ).get("questions")
    except (OSError, KeyError, UnicodeError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        fail(str(error))

    if not isinstance(questions, list) or not questions:
        fail("Fragenliste ist leer")

    seen_age_bands: set[str] = set()

    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            fail(f"Frage {index}: ungültiges Objekt")

        question_id = str(question.get("id", f"#{index}"))
        prompt = str(question.get("prompt", "")).strip()
        explanation = str(question.get("explanation", "")).strip()
        age_band = str(question.get("age_band", "")).strip()
        answers = question.get("answers")

        if not prompt:
            fail(f"{question_id}: Fragetext fehlt")
        if len(prompt) > MAX_PROMPT:
            fail(f"{question_id}: Fragetext ist zu lang für eine einfache Aufgabe")

        if age_band not in ALLOWED_AGE_BANDS:
            fail(
                f"{question_id}: age_band muss 10-12 oder 13-15 sein"
            )
        seen_age_bands.add(age_band)

        if not isinstance(answers, list) or not 2 <= len(answers) <= 4:
            fail(f"{question_id}: es sind zwei bis vier Antworten erforderlich")

        for answer in answers:
            text = str(answer.get("text", "")).strip() if isinstance(answer, dict) else ""
            if not text:
                fail(f"{question_id}: leere Antwort")
            if len(text) > MAX_ANSWER:
                fail(f"{question_id}: Antwort ist zu lang")

        if not MIN_EXPLANATION <= len(explanation) <= MAX_EXPLANATION:
            fail(
                f"{question_id}: Aha-Erklärung muss zwischen "
                f"{MIN_EXPLANATION} und {MAX_EXPLANATION} Zeichen lang sein"
            )

        if explanation.casefold() in {
            str(answer.get("text", "")).strip().casefold()
            for answer in answers
            if isinstance(answer, dict)
        }:
            fail(f"{question_id}: Erklärung darf nicht nur die Antwort wiederholen")

        if question.get("difficulty") not in {"easy", "medium"}:
            fail(f"{question_id}: erstes Aha-Paket verwendet nur easy oder medium")

    if seen_age_bands != ALLOWED_AGE_BANDS:
        missing = ", ".join(sorted(ALLOWED_AGE_BANDS - seen_age_bands))
        fail("beide Zielstufen müssen vertreten sein; fehlt: " + missing)

    print(
        "Lernzielprüfung erfolgreich: "
        f"{len(questions)} einfache Aufgaben, Zielstufen 10-12 und 13-15"
    )


if __name__ == "__main__":
    main()
