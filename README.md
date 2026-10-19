# LearnPip-Catalog-Wikipedia

Dieses Repository pflegt kuratierte, Wikipedia-basierte Lernfragen als eigenständige LearnPip-Katalogprodukte.

## Status

Die Repository- und Release-Infrastruktur ist vorbereitet. Reale Wikipedia-Inhalte werden erst veröffentlicht, wenn Artikelrevisionen, Attribution, Bearbeitungen und Lizenzen vollständig und reproduzierbar nachgewiesen sind. Bis dahin gibt es bewusst kein Inhaltsrelease.

## Schnittstelle zu LearnPip

Katalog-Releases verwenden ausschließlich den öffentlichen LearnPip-Austauschvertrag `org.learnpip.catalog.zip` in einer von LearnPip unterstützten Schema-Version. `catalog_version`, `source_revision` und die LearnPip-Anwendungsversion sind voneinander unabhängig.

LearnPip ist weder Build- noch Runtime-Abhängigkeit dieses Repositories. Veröffentlichte Pakete bleiben lokal/offline importierbar.

## Repository-Inhalte

- `catalog/`: kuratierte Paketquellen und erzeugte Paketbestandteile
- `scripts/`: katalogspezifische Generatoren und Validatoren
- `LICENSES.md`: Lizenzmatrix
- `NOTICE`: Hinweise zu Herkunft und Projektabgrenzung
- `ATTRIBUTION`: Quellen-, Autoren-/Revisions- und Änderungsnachweise
- `.github/workflows/validate.yml`: unabhängige CI und Release-Prüfung

## Veröffentlichung

Jede Frage muss ihre konkrete Wikipedia-Quelle und Revision nachweisen. Abgeleitete Texte müssen Änderungen kenntlich machen. Bilder und andere Medien werden einzeln nach ihrer tatsächlichen Lizenz behandelt; die Textlizenz darf nicht pauschal auf Medien übertragen werden.

Ein neues Katalogrelease erfordert kein LearnPip-Release.
