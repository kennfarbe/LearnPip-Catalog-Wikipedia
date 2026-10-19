#!/usr/bin/env python3
"""End-to-end checks for the first curated Wikipedia Aha catalog."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build-catalog.py"
RELEASE_VALIDATOR = ROOT / "scripts" / "validate-release.py"
LICENSE_VALIDATOR = ROOT / "scripts" / "validate-wikipedia-content.py"
LEARNING_VALIDATOR = ROOT / "scripts" / "validate-learning-design.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def require_success(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = json.loads((ROOT / "catalog" / "questions.json").read_text(encoding="utf-8"))
    questions = source["questions"]

    if len(questions) != 24:
        raise AssertionError(f"Erwartet 24 Fragen, gefunden {len(questions)}")

    ids = [question["id"] for question in questions]
    if len(ids) != len(set(ids)):
        raise AssertionError("Fragen-IDs sind nicht eindeutig")

    age_counts = {"10-12": 0, "13-15": 0}
    revisions: dict[str, int] = {}
    for question in questions:
        age_counts[question["age_band"]] += 1
        revision = question["provenance"]["source_revision"]
        revisions[revision] = revisions.get(revision, 0) + 1
        if question["media"]:
            raise AssertionError(question["id"] + ": erstes Paket muss medienfrei bleiben")
        if question["provenance"]["kind"] != "adapted":
            raise AssertionError(question["id"] + ": erwartete Bearbeitungsprovenienz fehlt")
        if question["license"]["id"] != "CC-BY-SA-4.0":
            raise AssertionError(question["id"] + ": falsche Textlizenz")

    if age_counts != {"10-12": 12, "13-15": 12}:
        raise AssertionError(f"Falsche Zielstufenverteilung: {age_counts}")
    if len(revisions) != 6 or set(revisions.values()) != {4}:
        raise AssertionError(f"Erwartet sechs gepinnte Quellen mit je vier Fragen: {revisions}")

    review = json.loads((ROOT / "catalog" / "review.json").read_text(encoding="utf-8"))
    review_by_id = {item["id"]: item for item in review["questions"]}
    if set(review_by_id) != set(ids):
        raise AssertionError("Review-Datei stimmt nicht mit dem Fragenbestand überein")
    if any(item["status"] != "draft" for item in review_by_id.values()):
        raise AssertionError("Das erste Paket darf vor Vier-Augen-Prüfung nicht freigegeben sein")

    with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
        first = Path(first_dir)
        second = Path(second_dir)

        result = run(str(BUILD), str(first), "--catalog-version", "test", "--allow-draft")
        require_success(result)
        result = run(str(BUILD), str(second), "--catalog-version", "test", "--allow-draft")
        require_success(result)

        package_name = "org.learnpip.wikipedia.aha-test.zip"
        package_a = first / package_name
        package_b = second / package_name
        if digest(package_a) != digest(package_b):
            raise AssertionError("Katalog-Build ist nicht reproduzierbar")

        for validator in (RELEASE_VALIDATOR, LICENSE_VALIDATOR, LEARNING_VALIDATOR):
            require_success(run(str(validator), str(package_a)))

        with zipfile.ZipFile(package_a) as archive:
            names = archive.namelist()
            if names[0] != "manifest.json":
                raise AssertionError("manifest.json ist nicht erster ZIP-Eintrag")
            if set(names) != {"manifest.json", "questions.json", "LICENSES.md", "NOTICE", "ATTRIBUTION"}:
                raise AssertionError(f"Unerwarteter Paketinhalt: {names}")
            attribution = archive.read("ATTRIBUTION").decode("utf-8")
            for question in questions:
                if question["provenance"]["source_url"] not in attribution:
                    raise AssertionError(question["id"] + ": Quelle fehlt in ATTRIBUTION")

    blocked = run(str(BUILD), tempfile.mkdtemp(), "--catalog-version", "release-test")
    if blocked.returncode == 0:
        raise AssertionError("Release-Build hat Draft-Fragen unerwartet akzeptiert")
    if "nicht freigegebene Fragen" not in blocked.stdout + blocked.stderr:
        raise AssertionError("Release-Sperre meldet den Draft-Status nicht eindeutig")

    print("Wikipedia-Aha-Katalogtest erfolgreich: 24 Fragen, 12/12 Zielstufen, sechs gepinnte Quellen")


if __name__ == "__main__":
    main()
