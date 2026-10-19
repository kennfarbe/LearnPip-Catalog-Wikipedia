# Lizenz- und Quellenregeln für Wikimedia-Inhalte

Dieses Dokument beschreibt die verbindlichen Regeln für Wikipedia-basierte
LearnPip-Kataloge in diesem Repository.

## Grundsatz

Wikipedia-Text und Wikimedia-Medien werden lizenzrechtlich getrennt behandelt.
Eine Lizenzangabe für einen Wikipedia-Artikel gilt niemals automatisch für ein
Bild, eine Grafik, eine Audio- oder Videodatei.

Die technische Prüfung in diesem Repository ersetzt keine Rechtsberatung. Sie
soll jedoch verhindern, dass ein Katalog ohne die hier festgelegten
Mindestnachweise veröffentlicht wird.

## Wikipedia-Text

Für aus deutschsprachigen Wikipedia-Artikeln abgeleitete Fragen gelten
folgende Anforderungen:

1. Als Quelle wird eine konkrete Artikelrevision verwendet, niemals nur der
   jeweils aktuelle Artikelstand.
2. Die Quelle enthält einen permanenten Revisionslink mit `oldid` oder einen
   `Special:PermanentLink`.
3. Die Revisions-ID wird zusätzlich als `source_revision` gespeichert.
4. Abgeleitete Fragen und Erklärungen werden als CC BY-SA 4.0 veröffentlicht.
5. Die Attribution verweist auf den Wikipedia-Artikel beziehungsweise dessen
   Versionsgeschichte, über die die Beitragenden nachvollziehbar sind.
6. Jede Bearbeitung wird als Bearbeitung gekennzeichnet. Bei
   `provenance.kind = adapted` ist ein aussagekräftiger
   `modification_note` Pflicht.
7. Ein Abrufdatum darf dokumentiert werden, ersetzt aber niemals die
   Revisions-ID.

Die Wikimedia-Nutzungsbedingungen erlauben die Namensnennung unter anderem
durch einen Hyperlink oder eine URL zum Artikel, dessen Versionsgeschichte die
Beitragenden aufführt. Für bearbeitete Inhalte sind außerdem die Änderung und
die verwendete Lizenz anzugeben.

Verbindliche Referenzen:

- https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use/de
- https://creativecommons.org/licenses/by-sa/4.0/

## Wikimedia Commons und andere Medien

Für jedes übernommene Medium wird die Lizenz unabhängig geprüft. Mindestens
folgende Angaben müssen pro Asset gespeichert werden:

- eindeutiger lokaler Medienpfad,
- Quelle beziehungsweise Dateibeschreibungsseite,
- konkrete Quellenrevision,
- Urheber oder sonstiger Rechteinhaber,
- verlangte Attribution,
- konkrete Lizenzbezeichnung,
- Link auf den Lizenztext,
- Änderungsvermerk, falls das Medium bearbeitet wurde.

Die MediaWiki-`imageinfo`-API kann `extmetadata` liefern, unter anderem
Lizenzname, Urheber- und Quellenangaben. Diese Metadaten sind ein
Erfassungswerkzeug; vor Freigabe muss der konkrete Nachweis redaktionell
geprüft werden.

Ein Medium wird nicht übernommen, wenn seine Lizenz oder Attribution nicht
eindeutig ermittelt werden kann. Lokal auf Wikipedia verwendete, nicht freie
Dateien oder reine Fair-Use-Nutzungen sind für Katalogreleases ausgeschlossen.

Referenzen:

- https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia
- https://www.mediawiki.org/wiki/Extension:CommonsMetadata

## Eigene Inhalte

Eigene Skripte und Werkzeuge dieses Repositories stehen unter AGPL-3.0-only.
Diese Lizenz erstreckt sich nicht auf Wikipedia-abgeleitete Katalogtexte oder
Drittmedien.

Eigene, nicht aus Wikipedia abgeleitete Medien oder Texte müssen vor der
Veröffentlichung ausdrücklich mit einer Lizenz versehen werden. Sie dürfen
nicht stillschweigend als CC BY-SA 4.0 behandelt werden.

## Release-Regel

Ein Inhaltsrelease ist nur zulässig, wenn der Wikipedia-Lizenzvalidator für
jede veröffentlichte Frage und jedes veröffentlichte Medium erfolgreich
durchläuft. Fehlende oder mehrdeutige Angaben führen zum Abbruch.
