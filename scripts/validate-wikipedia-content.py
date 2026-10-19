#!/usr/bin/env python3
"""Fail-closed licensing gate for Wikipedia-based LearnPip catalog packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlparse
import zipfile

TEXT_LICENSE_ID = "CC-BY-SA-4.0"
TEXT_LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
WIKIPEDIA_HOST = "de.wikipedia.org"
COMMONS_HOST = "commons.wikimedia.org"


def fail(message: str) -> None:
    raise SystemExit("Wikipedia-Lizenzprüfung abgelehnt: " + message)


def permanent_revision(url: str, revision: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != WIKIPEDIA_HOST:
        return False
    if not revision.isdigit():
        return False
    query = parse_qs(parsed.query)
    if revision in query.get("oldid", []):
        return True
    path = parsed.path.casefold()
    return (
        path.endswith("/special:permanentlink/" + revision)
        or path.endswith("/spezial:permanentlink/" + revision)
    )


def require_text_license(question: dict, index: int) -> None:
    license_info = question.get("license")
    if not isinstance(license_info, dict):
        fail(f"Frage {index}: Lizenzobjekt fehlt")
    if license_info.get("id") != TEXT_LICENSE_ID:
        fail(f"Frage {index}: Wikipedia-abgeleitete Texte müssen {TEXT_LICENSE_ID} verwenden")
    if license_info.get("license_url") != TEXT_LICENSE_URL:
        fail(f"Frage {index}: falscher oder fehlender CC-BY-SA-4.0-Lizenzlink")
    if not str(license_info.get("holder", "")).strip():
        fail(f"Frage {index}: Rechteinhaber/Urheberangabe fehlt")
    if not str(license_info.get("attribution", "")).strip():
        fail(f"Frage {index}: Attribution fehlt")


def require_question_provenance(question: dict, index: int) -> str:
    provenance = question.get("provenance")
    if not isinstance(provenance, dict):
        fail(f"Frage {index}: Provenienz fehlt")
    kind = provenance.get("kind")
    if kind not in {"adapted", "verbatim"}:
        fail(f"Frage {index}: Wikipedia-Frage muss adapted oder verbatim sein")
    source_url = str(provenance.get("source_url", "")).strip()
    revision = str(provenance.get("source_revision", "")).strip()
    if not permanent_revision(source_url, revision):
        fail(f"Frage {index}: Quelle ist keine gepinnte Revision der deutschsprachigen Wikipedia")
    if kind == "adapted" and not str(provenance.get("modification_note", "")).strip():
        fail(f"Frage {index}: Änderungsvermerk für bearbeiteten Wikipedia-Text fehlt")
    return source_url


def require_media_license(media: dict, question_id: str, media_index: int) -> str | None:
    path = str(media.get("path", "")).strip()
    label = f"{question_id} / Medium {media_index} ({path or 'ohne Pfad'})"
    license_info = media.get("license")
    if not isinstance(license_info, dict):
        fail(label + ": eigenes Lizenzobjekt fehlt")
    for field in ("id", "license_url", "holder", "attribution"):
        if not str(license_info.get(field, "")).strip():
            fail(label + f": Lizenzfeld {field} fehlt")

    provenance = media.get("provenance")
    if not isinstance(provenance, dict):
        fail(label + ": Provenienz fehlt")
    kind = provenance.get("kind")
    if kind == "original":
        return None
    if kind not in {"adapted", "verbatim"}:
        fail(label + ": ungültige Provenienzart")

    source_url = str(provenance.get("source_url", "")).strip()
    revision = str(provenance.get("source_revision", "")).strip()
    if not source_url or not revision:
        fail(label + ": konkrete Quelle und Quellenrevision fehlen")

    parsed = urlparse(source_url)
    if parsed.scheme != "https":
        fail(label + ": Medienquelle muss HTTPS verwenden")
    if parsed.hostname == COMMONS_HOST and "/wiki/" not in parsed.path:
        fail(label + ": Commons-Quelle muss auf eine Dateibeschreibungsseite verweisen")
    if kind == "adapted" and not str(provenance.get("modification_note", "")).strip():
        fail(label + ": Änderungsvermerk für bearbeitetes Medium fehlt")
    return source_url


def validate_package(path: Path) -> None:
    if not path.is_file():
        fail("Paket fehlt")
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            for required in ("questions.json", "ATTRIBUTION"):
                if required not in names:
                    fail(required + " fehlt")
            questions_doc = json.loads(archive.read("questions.json").decode("utf-8"))
            attribution = archive.read("ATTRIBUTION").decode("utf-8")
    except (OSError, zipfile.BadZipFile, UnicodeError, json.JSONDecodeError) as error:
        fail(str(error))

    questions = questions_doc.get("questions")
    if not isinstance(questions, list) or not questions:
        fail("Fragenliste ist leer")

    source_urls: set[str] = set()
    media_urls: set[str] = set()
    seen_ids: set[str] = set()

    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            fail(f"Frage {index}: ungültiges Objekt")
        question_id = str(question.get("id", "")).strip()
        if not question_id:
            fail(f"Frage {index}: ID fehlt")
        if question_id in seen_ids:
            fail(f"doppelte Fragen-ID: {question_id}")
        seen_ids.add(question_id)

        require_text_license(question, index)
        source_urls.add(require_question_provenance(question, index))

        media_items = question.get("media", [])
        if not isinstance(media_items, list):
            fail(f"{question_id}: media muss eine Liste sein")
        for media_index, media in enumerate(media_items, start=1):
            if not isinstance(media, dict):
                fail(f"{question_id}: ungültiges Medienobjekt")
            source = require_media_license(media, question_id, media_index)
            if source:
                media_urls.add(source)

    for source_url in sorted(source_urls | media_urls):
        if source_url not in attribution:
            fail("ATTRIBUTION enthält Quellenlink nicht: " + source_url)

    print(f"Wikipedia-Lizenzprüfung erfolgreich: {len(questions)} Fragen")
    print(f"Gepinnte Wikipedia-Quellen: {len(source_urls)}")
    print(f"Referenzierte externe Medienquellen: {len(media_urls)}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("genau ein ZIP-Pfad ist erforderlich")
    validate_package(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
