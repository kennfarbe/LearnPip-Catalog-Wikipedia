#!/usr/bin/env python3
"""Tests for the fail-closed Wikipedia licensing validator."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-wikipedia-content.py"

ARTICLE_URL = "https://de.wikipedia.org/w/index.php?title=Beispiel&oldid=123456789"
MEDIA_URL = "https://commons.wikimedia.org/w/index.php?title=File:Example.svg&oldid=987654321"


def base_question() -> dict:
    return {
        "id": "wikipedia:test:1",
        "language": "de",
        "prompt": "Welche Aussage trifft zu?",
        "answers": [
            {"id": "A", "text": "Richtig", "blocks": []},
            {"id": "B", "text": "Falsch", "blocks": []},
        ],
        "correct_answer_ids": ["A"],
        "explanation": "Beispielerklärung.",
        "topics": ["Beispiel"],
        "difficulty": "easy",
        "license": {
            "id": "CC-BY-SA-4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "holder": "Wikipedia-Autorinnen und -Autoren",
            "attribution": "Quelle: deutschsprachige Wikipedia, permanente Revision",
        },
        "provenance": {
            "kind": "adapted",
            "source_url": ARTICLE_URL,
            "source_revision": "123456789",
            "modification_note": "Als Lernfrage mit Antwortalternativen bearbeitet.",
        },
        "media": [
            {
                "path": "media/example.svg",
                "alt": "Beispielgrafik",
                "license": {
                    "id": "CC-BY-SA-4.0",
                    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
                    "holder": "Beispielautor",
                    "attribution": "Beispielautor, Wikimedia Commons",
                },
                "provenance": {
                    "kind": "verbatim",
                    "source_url": MEDIA_URL,
                    "source_revision": "987654321",
                },
            }
        ],
        "subject": "Beispiel",
        "topic": "Beispiel",
        "question_version": "1",
        "selection_mode": "single",
        "prompt_blocks": [{"kind": "text", "text": "Welche Aussage trifft zu?"}],
        "explanation_blocks": [{"kind": "text", "text": "Beispielerklärung."}],
    }


def write_package(path: Path, question: dict, attribution: str | None = None) -> None:
    text = attribution
    if text is None:
        text = (
            "Wikipedia-Quelle: " + ARTICLE_URL + "\n"
            "Medienquelle: " + MEDIA_URL + "\n"
        )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "questions.json",
            json.dumps({"questions": [question]}, ensure_ascii=False),
        )
        archive.writestr("ATTRIBUTION", text)


def run_validator(package: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(package)],
        check=False,
        capture_output=True,
        text=True,
    )


def assert_rejected(question: dict, expected: str, attribution: str | None = None) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        package = Path(temp_dir) / "catalog.zip"
        write_package(package, question, attribution)
        result = run_validator(package)
        if result.returncode == 0:
            raise AssertionError("Ungültiges Paket wurde akzeptiert")
        output = result.stdout + result.stderr
        if expected not in output:
            raise AssertionError(f"Erwartete Meldung fehlt: {expected}\n{output}")


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        package = Path(temp_dir) / "catalog.zip"
        write_package(package, base_question())
        result = run_validator(package)
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    question = base_question()
    question["provenance"]["source_url"] = "https://de.wikipedia.org/wiki/Beispiel"
    assert_rejected(question, "keine gepinnte Revision")

    question = base_question()
    question["license"]["id"] = "CC-BY-4.0"
    assert_rejected(question, "müssen CC-BY-SA-4.0 verwenden")

    question = base_question()
    del question["provenance"]["modification_note"]
    assert_rejected(question, "Änderungsvermerk")

    question = base_question()
    del question["media"][0]["license"]["license_url"]
    assert_rejected(question, "Lizenzfeld license_url fehlt")

    question = base_question()
    question["media"][0]["provenance"]["source_url"] = (
        "https://commons.wikimedia.org/wiki/File:Example.svg"
    )
    assert_rejected(question, "keine gepinnte Dateirevision")

    question = base_question()
    assert_rejected(question, "ATTRIBUTION enthält Quellenlink nicht", attribution=ARTICLE_URL + "\n")

    print("Wikipedia-Lizenztests erfolgreich")


if __name__ == "__main__":
    main()
