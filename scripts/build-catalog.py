#!/usr/bin/env python3
"""Build a deterministic LearnPip ZIP from the curated Wikipedia question source."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
QUESTIONS_PATH = CATALOG_DIR / "questions.json"
REVIEW_PATH = CATALOG_DIR / "review.json"
LICENSES_PATH = CATALOG_DIR / "LICENSES.md"
NOTICE_PATH = CATALOG_DIR / "NOTICE"

PACKAGE_ID = "org.learnpip.wikipedia.aha"
SCHEMA_VERSION = "1.0.0"
FORMAT_ID = "org.learnpip.catalog.zip"
CREATED_AT = "2026-10-19T00:00:00Z"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def fail(message: str) -> None:
    raise SystemExit("Katalog-Build abgelehnt: " + message)


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)}: {error}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} muss ein JSON-Objekt enthalten")
    return data


def validate_review(questions: list[dict], allow_draft: bool) -> None:
    review = load_json(REVIEW_PATH)
    if review.get("schema_version") != "1":
        fail("unbekannte review.json-Schema-Version")
    if review.get("package_id") != PACKAGE_ID:
        fail("review.json enthält falsche package_id")

    records = review.get("questions")
    if not isinstance(records, list):
        fail("review.json questions fehlt")

    by_id: dict[str, dict] = {}
    for record in records:
        if not isinstance(record, dict):
            fail("ungültiger Review-Eintrag")
        question_id = str(record.get("id", "")).strip()
        if not question_id or question_id in by_id:
            fail("fehlende oder doppelte Frage im Review")
        status = record.get("status")
        if status not in {"draft", "approved"}:
            fail(f"{question_id}: ungültiger Review-Status")
        reviewers = record.get("reviewers")
        if not isinstance(reviewers, list):
            fail(f"{question_id}: reviewers muss eine Liste sein")
        if status == "approved" and len({str(item).strip() for item in reviewers if str(item).strip()}) < 2:
            fail(f"{question_id}: approved benötigt mindestens zwei Reviewer")
        by_id[question_id] = record

    question_ids = {str(question.get("id", "")).strip() for question in questions}
    if question_ids != set(by_id):
        fail("review.json und questions.json enthalten unterschiedliche Fragen")

    if not allow_draft:
        drafts = sorted(question_id for question_id, record in by_id.items() if record.get("status") != "approved")
        if drafts:
            fail(
                "Release enthält noch nicht freigegebene Fragen: "
                + ", ".join(drafts[:5])
                + (" ..." if len(drafts) > 5 else "")
            )


def build_attribution(questions: list[dict]) -> bytes:
    sources: dict[tuple[str, str], dict] = {}
    for question in questions:
        provenance = question["provenance"]
        key = (provenance["source_url"], provenance["source_revision"])
        sources.setdefault(
            key,
            {
                "attribution": question["license"]["attribution"],
                "modification_note": provenance["modification_note"],
            },
        )

    lines = [
        "Attribution und Quellen",
        "========================",
        "",
        "Lizenz der Wikipedia-abgeleiteten Lerninhalte: CC BY-SA 4.0",
        LICENSE_URL,
        "",
        "Die Lernfragen, Antwortalternativen und Erklärungen sind Bearbeitungen.",
        "",
    ]
    for (source_url, revision), meta in sorted(sources.items()):
        lines.extend(
            [
                meta["attribution"],
                f"Permanente Quelle: {source_url}",
                f"Revision: {revision}",
                f"Änderung: {meta['modification_note']}",
                "",
            ]
        )
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


def source_revision(questions: list[dict]) -> str:
    records = sorted(
        {
            (question["provenance"]["source_url"], question["provenance"]["source_revision"])
            for question in questions
        }
    )
    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "wikipedia-revisions-" + hashlib.sha256(payload).hexdigest()[:16]


def record(path: str, data: bytes) -> dict:
    return {
        "path": path,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
    }


def write_entry(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--catalog-version", required=True)
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()

    questions_doc = load_json(QUESTIONS_PATH)
    questions = questions_doc.get("questions")
    if not isinstance(questions, list) or not questions:
        fail("questions.json enthält keine Fragen")
    if not all(isinstance(question, dict) for question in questions):
        fail("questions.json enthält ungültige Fragen")

    validate_review(questions, args.allow_draft)

    files = {
        "questions.json": QUESTIONS_PATH.read_bytes(),
        "LICENSES.md": LICENSES_PATH.read_bytes(),
        "NOTICE": NOTICE_PATH.read_bytes(),
        "ATTRIBUTION": build_attribution(questions),
    }

    manifest = {
        "format_id": FORMAT_ID,
        "schema_version": SCHEMA_VERSION,
        "package_id": PACKAGE_ID,
        "catalog_version": args.catalog_version,
        "source_revision": source_revision(questions),
        "title": "Alltagswissen mit Aha-Effekt",
        "description": "Kurze, einfache Wikipedia-basierte Lernfragen mit Aha-Erklärungen für die Zielstufen 10–12 und 13–15.",
        "language": "de",
        "publisher": "LearnPip-Catalog-Wikipedia",
        "created_at": CREATED_AT,
        "license": {
            "id": "CC-BY-SA-4.0",
            "license_url": LICENSE_URL,
            "holder": "Wikipedia-Autorinnen und -Autoren sowie LearnPip-Katalogredaktion für Bearbeitungen",
            "attribution": "Quellen, permanente Revisionen und Bearbeitungen siehe ATTRIBUTION.",
        },
        "files": [record(name, files[name]) for name in sorted(files)],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    package = args.output_dir / f"{PACKAGE_ID}-{args.catalog_version}.zip"
    with zipfile.ZipFile(package, "w") as archive:
        write_entry(archive, "manifest.json", manifest_bytes)
        for name in sorted(files):
            write_entry(archive, name, files[name])

    print(package)


if __name__ == "__main__":
    main()
