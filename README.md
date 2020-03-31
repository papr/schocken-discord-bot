# SchockenBot

## Valid Commands

- Command - **State** - Comment
- `!start` - **start** - startet eine neue Runde Schocken
- `!einwerfen` - **vorrunde** - Zeitfenster in dem alle einwerfen
- `!weiter` - **vorrunde** - startet die Runde mit allen Spielern die eingeworfen haben
- `!stechen` - **stechen** - zum auswürfeln des stechens
- `!würfeln` - **Runde** - einfacher wurf

## States

- start - nichts läuft, warten auf neue runde
- vorrunde - einwerfen und bestimmung der teilnehmer
- stechen - wenn zweimal eingeworfen haben
- runde - die schocken runden

## Notes

- Würfe sind immer von groß nach klein sortiert (TODO: sonder würfe anpassen)

## offene Fragen

- timout zum einwerfen anstatt mit `!weiter` zu starten?
    -> Runde wird durch !würfeln des ersten Spielers gestartet (siehe TODO)
- aktives werfen mit einem command oder automatischer wurf nach x sekunden (oder beides?)


## optionale Funktionalitäten
- message zeile bei teilnahme in buttons verwandeln ist das möglich?
- mehrere Schocken Runden gleichzeitig
- geldschulden datenbank
  - bierwunsch
- verschiedene würfe? mit bounce, one bounce, am rand etc. (mit unterschiedlichen chancen auf rausfliegende würfel)

## TODO
- SchockenSpiel braucht ein Attribut aktueller_spieler oder jeder Spieler() braucht ein Attribut aktiv
- weiter; spieler mit niedrigstem wurf startet mit seinem ersten wurf die runde (state change zu Runde) **[Andre]**
  - Ergebnis: sortierte Liste SchockenSpiel.spieler_liste [reihenfolge verschoben auf den niedrigsten]
- Runde; 
  - Rundenablauf; würfel beiseite legen
    - Ergebnis: Liste mit Würfen der einzelnen leute [sollte nach jedem wurf aktuell sein] [siehe input wurfauswertung]
  - Wurfauswertung; als ergebnissliste durchgehen und auswerten **[Pablo]**
    - init input:
      - Liste der spieler namen, sortiert nach rundenreihenfolge
    - auswertung[spielername, augen]
      - augen pro spieler [sortiertes int tuple]
      - anzahl der würfe
  - Deckel-Verteilung; Schlusskriterium auswerten[leute ohne deckel aus der liste nehmen wenn der top leer ist] **[Pablo]**
    - Halbzeit initialisierung

## Klassen und Attribute

Spieler:
- name
- deckel
- augen [letzter wurf]
- anzahl der würfe

## Deployment Instructions

```
python -m pip install -U pip
python -m pip install -U schocken
python -m schocken
```

