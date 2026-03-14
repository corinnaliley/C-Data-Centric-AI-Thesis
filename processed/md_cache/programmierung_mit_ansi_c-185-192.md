## Anhang A

## Einf uhrung in UNIX

## A.1 Grundlagen

UNIX ist ein time-sharing-Betriebssystem . Dieses bedeutet, dass sich mehrere Benutzer an verschiedenen Terminals gleichzeitig die Resourcen eines Rechners (Speicher, Prozessorzeit, Platten, Drucker, usw.) teilen konnen. Es ist aber auch moglich, dass ein einzelner Benutzer mehrere Prozesse gleichzeitig laufen lassen kann. Wenn mehrere Prozesse eines oder mehrerer Benutzer gleichzeitig laufen, muss das Betriebssystem die Prozessorzeit den einzelnen Prozessen abwechselnd nach einem Prioritatenschema zuweisen. Wahrend die Prozessorzeit also fur kurze Intervalle ausschließlich einem einzelnen Prozess zur Verfugung steht, werden andere Resourcen (wie z.B. der Speicher) permanent einem Prozess zugeordnet. Ein Prozess belegt also auch dann Speicher, wenn zwar gestartet wurde, sich aber nicht in der Ausfuhrung befindet.

Jeder Benutzer besitzt einen Benutzernamen und ein hoffentlich nur ihm und dem System bekanntes Passwort. Unter den Benutzern gibt es einen, der unbeschrankte Privilegien besitzt, mit dem Namen root . Der Benutzer root kann dem System einen neuen Benutzernamen mit Passwort mitteilen und somit einem neuen Benutzer den Zugang zum System ermoglichen. Genauso kann er den Namen eines Benutzer aus dem System entfernen und somit diesem die Rechenberechtigung entziehen.

## A.2 Ein- und Ausloggen, Passwort

Jeder Benutzer muss sich vor jeder Sitzung am Terminal einer Zulassungsprozedur zum Rechnen unterwerfen, dem login -Verfahren. Wie diese Prozedur im einzelnen ablauft, hangt sehr stark von der jeweiligen Umgebung ab.

Im wesentlichen werden Benutzername und Passwort abgefragt. Das kann in einer Konsole oder einem grafischen login-Fenster geschehen. Heutzutage werden fast alle Systeme auch eine grafische Benutzeroberflache anbieten. Dann kann man nach erfolgreichem login uber die Oberflache ein Konsolenfenster offnen. Der Rest dieses Abschnittes wird weiter auf die Nutzung der Konsole eingehen. Von dort aus kann man alle wichtigen Operationen ausfuhren. Eine Behandlung von grafischen Benutzeroberflachen ist angesichts derer Vielfalt hier nicht moglich.

Hat man nun Zugriff auf eine Konsole, erscheint dort dann der Textcursor hinter dem Prompt des Systems, das die Form

rechnername >

hat. Das Beenden einer Sitzung erfolgt durch die Eingabe des Kommandos

exit ¿

oder noch einfacher durch Eingabe von C-d im Terminalfenster. Das Zeichen ¿ bedeutet Drucken der ENTER -Taste; C-d bedeutet, dass man die Taste Ctrl gedruckt halt und dazu die Taste d anschlagt.

## A.3 Hilfen

Die Beschreibung von beliebigen Kommandos kann man sich auf dem Bildschirm mit dem Befehl

```
man kommandoname ¿
```

( manual ) ansehen. Man erhalt dann die entsprechenden Seiten des UNIX-Manuals aufgelistet. So erhalt man die Erlauterung des Kommandos passwd durch

man passwd ¿

und die Erlauterung des Kommandos man selbst durch

```
man man ¿
```

Die UNIX-Manuals sind in verschiedene Abschnitte aufgeteilt. man liefert das erste Ergebnis, egal in welchem Bereich es gefunden wurde. Mochte man speziell z.B. die Dokumentation zu einer Bibliotheksfunktion erhalten, so muss man den Abschnitt mit angeben. Dies geschieht durch eine zusatzliche Zahl vor dem eigentlichen Begriff. Mit

man 3 printf ¿

erhalt man so die Dokumentation zu printf aus der C-Standardbibliothek.

## A.4 Das Dateisystem

Der gesamte Massenspeicher, uber den ein UNIX-System verfugt, ist in Form einer einheitlichen baumartigen Dateistruktur organisiert, in der jeder Benutzer uber einen eigenen Teil des Dateibaumes (einen Ast) verfugt. Hier darf der Benutzer Dateien erzeugen, loschen und ausfuhren; dem Superbenutzer root gehort der gesamte Baum (vgl. Abbildung A.1). Ob der gesamte Dateibaum auf einer einzigen Platte gespeichert oder auf eine Vielzahl von Platten verteilt ist, ist fur den Benutzer weitgehend transparent.

Das UNIX-Dateisystem unterscheidet zwischen Verzeichnissen und (anderen) Dateien . Die Verzeichnisse enthalten andere Verzeichnise und Dateien; Dateien konnen zum Beispiel Texte oder ausfuhrbare Programme enthalten. Alle inneren Knoten des Dateibaumes, die Wurzel / eingeschlossen, sind Verzeichnisse. Die Blatter des Baumes sind (noch) leere Verzeichnisse oder andere Dateien. Man beachte: Verzeichnisse sind letztlich auch Dateien, nur mit ganz speziellem Inhalt.

Die Lage einer Datei (oder eines Verzeichnisses) in der Baumstruktur kann durch ihren Pfad beschrieben werden, d.h. den Weg von der Wurzel des Baumes zu der betreffenden Datei. Der Pfadname besteht aus der Folge der Namen der dabei durchlaufenen Knoten, wobei die einzelnen Dateinamen durch einen Schragstrich ( / ) voneinander getrennt werden. Die Wurzel wird nur durch einen Schragstrich bezeichnet.

Der so angegebene Weg von der Wurzel zu einer Datei ist gleichzeitig ihr vollstandiger Name. Zum Beispiel sind die vollen Namen der Dateien prog.c und a.out im Baumabschnitt von benutzer2 im Beispiel (vgl. Abbildung A.1)

Abbildung A.1: Beispiel eines UNIX-Filesystems

picture-1.png

/home/users/benutzer2/prog.c

/home/users/benutzer2/a.out

Kein Benutzer muss die Namen seiner Dateien stets vollstandig angeben, denn das System gibt jedem Dateinamen, der nicht vollstandig angegeben wird, ein Prafix, das den Weg von der Wurzel zum aktuellen Baumabschnitt des Benutzers beschreibt. Im Beispiel ist fur benutzer2 das Prafix nach dem Einloggen /home/users/benutzer2/ . So sind die Eingabe

a.out ¿

und die Eingabe

/home/users/benutzer2/a.out ¿

aquivalent. Welches Prafix das System momentan den Dateinamen gibt, lasst sich durch die Eingabe des Kommandos

pwd ¿

( print working directory ) feststellen. Das Prafix ist der Pfadname eines Verzeichnisses, das man auch Arbeitsverzeichnis ( working directory ) nennt. Eine Abkurzung dafur ist der Punkt ( . ). So kann man alternativ auch

./a.out ¿

fur obigen Aufruf verwenden. Das kann sogar notwendig sein, wenn nach ausfuhrbaren Programmen nicht im Arbeitsverzeichnis gesucht wird.

Auf eine andere Moglichkeit, ein Prafix vom System automatisch erganzen zu lassen, wird gleich noch naher eingegangen.

## A.5 Dateiverwaltung

Das momentan gultige Namensprafix kann man durch das Kommando

cd pfadname ¿

( change directory ) andern, wobei pfadname den Weg von der Wurzel zu einem Verzeichnis beschreibt. (Bei der Ausfuhrung des Kommandos wird der angegebene Pfadname ggf. noch durch das alte Prafix erganzt.)

Mit dem Kommando

```
cd .. ¿
```

wird das gegenwartige Prafix um den letzten Namen gekurzt. Dieses entspricht einer Bewegung in der Richtung zur Wurzel im Dateibaum. Mit dem Kommando

```
cd name ¿
```

wird das gegenwartige Prafix um den angegebenen Namen erweitert, sofern in der gegenwartigen Verzeichnisdatei eine Verzeichnisdatei mit diesem Namen vorhanden ist. Dieses entspricht einer Bewegung in der Richtung weg von der Wurzel im Dateibaum.

Nach dem Einloggen befindet man sich in seinem Heimatverzeichnis ( home directory ), d.h. in der Wurzel des eigenen Teilbaumes. Fur benutzer2 heißt das etwa, dass nach dem Einloggen

## /home/users/benutzer2/

das aktuelle Prafix ist. Dieses Prafix kann man jederzeit wiederherstellen, indem man nur

cd ¿

eintippt. Fur das Heimatverzeichnis eines Benutzers gibt es auch noch eine spezielle Kurzform, namlich

## ~benutzer2/

Das System bestimmt dann selbst, wie der Pfad zu diesem Verzeichnis korrekt zu erganzen ist.

Welche Dateien ein Verzeichnis mit dem Namen name enthalt, lasst sich mit dem Kommando

```
ls name ¿
```

( list ) feststellen. Beispiele:

- ls / ¿
- ls /home ¿
- ls /home/users/benutzer2 ¿
- ls ~benutzer2 ¿

Das erste Kommando zeigt alle Eintrage in der Wurzel, das zweite alle Eintrage im Verzeichnis /home , das dritte und vierte alle Eintrage im home-Verzeichnis des Benutzers benutzer2 .

Gibt man nur das Kommando

ls ¿

ein, so werden alle Eintrage im aktuellen Verzeichnis angezeigt, d.h. dem Verzeichnis, dessen Pfadname durch pwd geliefert wird.

Mit der Option -l ( long )

ls -l ¿

wird fur jeden Eintrag des Verzeichnisses mehr Information ausgegeben: Jede Zeile enthalt Angaben zu einer Datei, deren Name am Ende der Zeile steht. Die ersten 10 Zeichen haben die Form

```
d rwx rwx rwx
```

## und bedeuten:

- d es handelt sich um ein Verzeichnis
- r die Datei darf gelesen werden
- w in die Datei darf geschrieben werden
- x die Datei darf (als Programm) ausgefuhrt oder (als Verzeichnis) aufgelistet werden

Steht an der Position von d ein Bindestrich ( -), so handelt es sich nicht um ein Verzeichnis. An den anderen Stellen bedeutet ein Bindestrich, dass das entsprechende Zugriffsrecht nicht besteht. Die drei Gruppen rwx markieren, von links nach rechts, die Zugriffsrechte fur den Besitzer der Datei, fur seine Gruppe und fur andere Benutzer.

Die Zugriffsrechte, also der Schutz der Dateien, konnen mit dem Kommando chmod ( change mode ) geandert werden. Sehen Sie sich die Einzelheiten einmal selbst mit dem Kommando man an.

Mit der Optionenkombination -al

```
ls -al ¿
```

werden auch Dateien erfasst, deren Name mit einem Punkt beginnt und die sonst nicht aufgelistet werden.

Neue Verzeichnisse kann man mit dem Kommando

```
mkdir name ¿
```

( make directory ) anlegen, leere Verzeichnisse mit dem Kommando

```
rmdir name ¿
```

( remove directory ) loschen, entsprechende Zugriffsrechte vorausgesetzt. Andere Dateien kann man mit

```
rm name1 name2 ... nameN ¿
```

( remove ) loschen, ebenfalls entsprechende Zugriffsrechte vorausgesetzt. Beim Loschen ist oft die Option -i

```
rm -i name1 name2 ... nameN ¿
```

zweckmaßig. Sie bewirkt, dass man fur jede einzelne Datei das Loschen durch Eintippen von y (es) noch einmal ausdrucklich bestatigen muss.

Kopieren bzw. Umbenennen kann man Dateien mit den Kommandos

cp quelle ziel ¿

( copy

```
) bzw.
```

```
mv quelle ziel ¿
```

( move ). Durch Umbenennen kann eine Datei auch aus einem Verzeichnis in ein anderes verlegt werden.

## A.6 Metazeichen

Bei vielen Kommandos ist es zweckmaßig, Dateinamen nicht explizit anzugeben, sondern die Metazeichen ( Jokerzeichen , wild cards ) Fragezeichen ( ? ) und Stern ( * ) zu verwenden:

- · Ein Fragezeichen steht fur genau ein beliebiges Zeichen.
- · Ein Stern steht fur eine beliebig lange (auch leere) Folge beliebiger Zeichen.

Beispiele:

```
rm *.c ¿ rm *~ ¿ rm * ¿ rm -i * ¿ rm aufg?.c ¿
```

Setzen wir voraus, dass die entsprechenden Zugriffsrechte bestehen, so gilt: Im ersten Beispiel werden in der aktuellen Directory alle Dateien mit dem Suffix .c geloscht und im zweiten Beispiel alle Dateien, bei denen das letzte Zeichen des Namen ~ ist; im dritten Beispiel werden in der aktuellen Directory alle Dateien ausnahmslos und ohne Ruckfrage geloscht; im vierten Beispiel werden in der aktuellen Directory alle Dateien geloscht, fur die dieses ausdrucklich bestatigt wird; im letzten Beispiel werden in der aktuellen Directory alle Dateien geloscht, deren Name mit aufg beginnt, dann ein beliebiges Zeichen aufweist und danach mit .c endet.

## A.7 Auflisten von Datei-Inhalten

Durch

```
cat datei ¿
```

wird der Inhalt der entsprechenden Datei aufgelistet. Dieses Kommando empfiehlt sich allerdings nur fur ziemlich kurze Dateien, da die Ausgabe ' durchrollt', wenn sie langer als eine Bildschirmseite ist. Seitenweise kann man sich den Inhalt einer Datei mit dem

## Kommando

more datei ¿

ansehen: Die Ausgabe stoppt, sobald der Bildschirm voll ist; durch Drucken der Leertaste wird die nachste Bildschirmseite gezeigt, durch Drucken der ENTER -Taste nur die nachste Zeile.

Zur Ausgabe auf einen Drucker dient das Kommando

lpr datei ¿

( lineprinter ) oder, wenn verschiedene Drucker zur Verfugung stehen

lpr -P xyz datei ¿

wobei xyz fur den Namen des Druckers steht. Leider kommt es immer wieder vor, dass Drucker durch Fehlbedienung blockiert werden. Den Status eines Druckers kann man sich mit dem Kommando

lpq -P xyz ¿

( lineprinter queue ) ansehen. Stellt man fest, dass die Warteschlange des Druckers nicht leer ist, der Drucker aber trotzdem nicht arbeitet, kann es daran liegen, dass er blockiert ist. Falls eine eigene Datei der ' Ubeltater' ist, kann man versuchen, die Datei aus der Warteschlange zu loschen. Hierzu dient das Kommando

```
lprm -P xyz # ¿
```

( lineprinter remove ), bei dem man als Nummer die Zahl einzusetzen hat, die das Kommando lpq fur die Datei gemeldet hat.

## A.8 Umleitung von Ein- und Ausgabe

UNIX-Kommandos holen ihre Eingabe vielfach vom Standardeingabegerat (Tastatur) und schreiben ihre Ausgabe vielfach auf das Standardausgabegerat (Bildschirm).

Die Standardein-/ausgabe lasst sich aber beim Aufruf eines Kommandos ohne weiteres umleiten.

```
programm < name
```

bewirkt, dass die Datei (oder das Gerat) mit dem Namen name als Standardeingabegerat verwendet wird;

```
programm > name programm >> name
```

bewirken, dass die Datei (oder das Gerat) mit dem Namen name als Standardausgabegerat verwendet wird.

Beide Formen unterscheiden sich nur dann, wenn die Datei, in die die Ausgabe umgeleitet wird, bereits existiert: Bei einem Winkel wird der bisherige Inhalt der Datei zunachst geloscht; bei zwei Winkeln wird die Ausgabe an den bisherigen Inhalt der Datei angehangt.

Umleitung von Ein- und Ausgabe ist bei vielen Kommandos moglich. Besonders interessant ist die Umleitung fur eigene Programme. Man kann fur umfangreichere Tests die benotigte Eingabe in einer Datei speichern und diese als Eingabequelle verwenden. So muss die Eingabe nicht jedesmal von Hand erneut eingegeben werden.

## A.9 Editieren

Meist hat man die Wahl zwischen verschiedene Editoren , d.h. Programmen, mit denen man Texte, zum Beispiel auch C-Quellprogramme eingeben kann. Wichtig ist, dass der Editor den eingegebenen Quelltext ohne Formatierungsanweisungen oder Anweisungen zur Dokumentorganisation speichert. Ein normales Textverarbeitungsprogramm, mit dem man z.B. seine Briefe verfasst ist daher in der Regel nicht geeignet. Mit der Zeit entwickelt sicher jeder eine Vorliebe fur einen bestimmten Editor.

Es wurde wenig bringen, an dieser Stelle zu versuchen, die Funktionsweise eines Editors zu erklaren oder auf spezielle Funktionen eines bestimmten Editors einzugehen. Neben den oft vorinstallierten Editoren gibt es eine Reihe freier Editoren, die man konstenlos im Internet herunterladen kann. Es lohnt sich auf jeden Fall zunachst einige verschiedene Editoren auszuprobieren und sich erst dann zu entscheiden.

## A.10 Ubersetzen und Binden

Prinzipiell sind zwei Schritte erforderlich sind, um aus dem Quellcode eines C-Programms ein ausfuhrbares Programm zu erzeugen:

- 1. Der Quellcode wird mit dem Compiler ubersetzt. Der Compiler erzeugt eine Objektdatei .
- 2. In der Regel werden Bibliotheksroutinen benotigt. Die Objektdatei und diese Routinen werden durch den Linker gebunden.

Dazu benotigt man einen Compiler und Linker. Auf Linux-basierten Systemen ist meist die GNU Compiler-Sammlung (GNU Compiler Collection, GCC, http://gcc.gnu.org ) zusammen mit der GNU C Bibliothek (GNU C Library, glibc, http://www.gnu.org/software/libc ) installiert. Beide kann man kostenlos im Internet herunterladen.

Die beide Schritte - compilieren und linken - werden vom gcc mit einem einzigen Kommando bewirkt:

gcc prog.c

Dabei ist prog.c der Name der C-Quelldatei; das Suffix .c zeigt dem Compiler an dass es sich um C-Quellcode handelt. Das ausfuhrbare Programm erhalt den Namen a.out . Die Eingabe dieses Namens als UNIX-Kommando bewirkt die Ausfuhrung des Programms.

Soll das ausfuhrbare Programm einen anderen Namen als a.out erhalten, zum Beispiel prog , so muss man die Option -o und den neuen Namen zusatzlich in das gcc -Kommando eintragen:

gcc -o prog prog.c

Eine zusatzliche Option sollte man beim Aufruf des gcc auf jeden Fall angeben, namlich -Wall , so dass der Aufruf

gcc -Wall [ -o prog ] prog.c

ist. Ist diese Option angegeben, schreibt der Compiler zu ' verdachtigem' Code, den er sonst kommentarlos akzeptieren wurde, Warnungen. In vielen Fallen weisen diese Warnungen auf Programmierfehler hin, ohne deren Beseitigung das Programm nicht laufen wird. Merke: Ein Programm, das ein Compiler widerspruchslos akzeptiert, ist noch lange kein korrektes Programm!

Die Option -O optimiert den erzeugten Maschinencode hinsichtlich Große und Geschwindigkeit. Die Ausfuhrung eines Programms kann so deutlich beschleunigt werden. Der Compiler kann aber auch mehr Warnungen ausgeben. Durch die bei der Optimierung verwendete Datanfluss-Analyse wird zum Beispiel auch erkannt, ob eine Variable ggf. uninitialisiert verwendet wird.

Zwei weitere Optionen, namlich -ansi und -pedantic , unterstutzen den Programmierer, der sauberes Standard-C programmieren und keine Erweiterungen des gcc verwenden mochte.

Der normale einfache Compileraufruf sieht also so aus:

gcc -Wall -ansi -pedantic -O [ -o prog ] prog.c

Eine weitere oft benotigte Option ist -lm . Sie sorgt dafur, dass der Bibliotheksteil mit den mathematischen Funktionen gebunden wird. Da es sich um eine Linker-Option handelt, wird sie nach den Quelltextdateien angegeben.