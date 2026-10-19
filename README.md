# LearnPip-Catalog-Wikipedia

Dieses Repository pflegt kuratierte, Wikipedia-basierte Lernfragen als eigenständige LearnPip-Katalogprodukte.

## Status

Die Repository- und Release-Infrastruktur einschließlich einer fail-closed Lizenzprüfung ist vorbereitet. Reale Wikipedia-Inhalte werden erst veröffentlicht, wenn Artikelrevisionen, Attribution, Bearbeitungen, redaktionelle Freigaben und gegebenenfalls Medienlizenzen vollständig und reproduzierbar nachgewiesen sind.

Bis zu einem redaktionell geprüften Beispielpaket gibt es bewusst kein Inhaltsrelease.

## Schnittstelle zu LearnPip

Katalog-Releases verwenden ausschließlich den öffentlichen LearnPip-Austauschvertrag `org.learnpip.catalog.zip` in einer von LearnPip unterstützten Schema-Version. `catalog_version`, `source_revision` und die LearnPip-Anwendungsversion sind voneinander unabhängig.

LearnPip ist weder Build- noch Runtime-Abhängigkeit dieses Repositories. Veröffentlichte Pakete bleiben lokal/offline importierbar.

## Repository-Inhalte

- `catalog/`: kuratierte Paketquellen und erzeugte Paketbestandteile
- `scripts/`: katalogspezifische Generatoren und Validatoren
- `tests/`: Negativ- und Freigabetests für Quellen- und Lizenzregeln
- `docs/WIKIMEDIA-LICENSING.md`: verbindliche Quellen- und Lizenzregeln
- `LICENSES.md`: Lizenzmatrix
- `NOTICE`: Hinweise zu Herkunft und Projektabgrenzung
- `ATTRIBUTION`: Quellen-, Autoren-/Revisions- und Änderungsnachweise
- `.github/workflows/validate.yml`: unabhängige CI und Paketprüfung

## Lizenzprinzip

Wikipedia-abgeleitete Fragen und Erklärungen werden in diesem Projekt unter CC BY-SA 4.0 veröffentlicht. Jede Frage muss auf eine konkrete permanente Revision der deutschsprachigen Wikipedia verweisen und Bearbeitungen kenntlich machen.

Bilder und andere Medien werden unabhängig vom Artikel geprüft. Jedes Asset benötigt seine tatsächliche Lizenz, Urheber-/Rechteinhaberangabe, Attribution und eine gepinnte Quelle. Nicht freie oder nur über Fair-Use-Regeln verwendbare Medien werden nicht in Katalogreleases übernommen.

Details stehen in `docs/WIKIMEDIA-LICENSING.md`.

## Veröffentlichung

Vor einem Release werden drei Ebenen geprüft:

1. technischer LearnPip-Katalogvertrag,
2. Integrität des Releasepakets,
3. Wikipedia-/Wikimedia-Lizenz- und Quellenregeln.

Ein neues Katalogrelease erfordert kein LearnPip-Release.
