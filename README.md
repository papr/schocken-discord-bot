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
- aktives werfen mit einem command oder automatischer wurf nach x sekunden (oder beides?)
- message zeile bei teilnahme in buttons verwandeln ist das möglich?

## optional Features

- mehrere Schocken Runden gleichzeitig
- geldschulden datenbank
- verschiedene würfe? mit bounce, one bounce, am rand etc. (mit unterschiedlichen chancen auf rausfliegende würfel)


## TODO

- einwerfen; nachwerfen, sortierte liste (nur verschieben nicht sortieren)
  - Ergebnis: Sortierte Spieler Liste
- weiter; spieler mit niedrigstem wurf startet mit seinem ersten wurf die runde (state change zu Runde)
- Runde; 
  - 
  - Ergebnis: 