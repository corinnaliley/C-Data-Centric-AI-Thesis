## Kapitel 10

## Der Pr aprozessor

## 10.1 Uberblick

Den Praprozessor , den der Standard vorsieht, haben wir mit zwei seiner Direktiven bereits kennengelernt:

- · Eine include -Direktive wird durch den Inhalt der in ihr genannten Datei ersetzt.
- · Eine define -Direktive bewirkt nach unserem derzeitigen Kenntnisstand, dass der in ihr definierte Name im Rest des Moduls durch den ebenfalls in ihr definierten Ersatztext ersetzt wird.

Die grundsatzliche Arbeitsweise des Prapozessors kennen wir damit: Er uberarbeitet den Text, indem er Einsetzungen, Ersetzungen - und unter Umstanden auch Streichungen vornimmt. Alles geschieht auf rein formaler Ebene, also ohne Rucksicht auf die logische Struktur der Funktionen, die der Modul enthalt.

Man kann sich den Praprozessor als Programm vorstellen, das vor der eigentlichen Ubersetzung lauft, oder auch als ersten Durchlauf des Compilers durch das Programm.

Was ein Standard-Praprozessor konnen muss, ist ebenso im Standard festgelegt wie die Form der Direktiven:

- · Jede Direktive beginnt mit einem Nummernzeichen ( # ). Diese Nummernzeichen muss, von ' white spaces' abgesehen, das erste Zeichen in der Zeile sein.
- · Dem Nummernzeichnen folgt der Name der Direktive. Ob weitere Eintrage erforderlich sind oder nicht, hangt von der jeweiligen Direktive ab.
- · Jede Direktive wird durch ein Zeilenende-Zeichen beendet. Allerdings: Reicht der Platz in einer Zeile nicht aus, so kann man Fortsetzungszeilen schreiben. Dazu muss man direkt vor das Zeilenende-Zeichen der fortzusetzenden Zeile einen Backslash ( \ ) setzen.

Wir haben fur Direktiven also die allgemeine Form

# name [text]

Die Direktiven, die es neben include und define gibt, dienen im wesentlichen zur bedingten Compilation . Darunter versteht man, dass Teile des Quellcodes in Abhangigkeit von bestimmten Bedingungen ubersetzt werden oder auch nicht. Bedingte Compilation ist in zwei Fallen besonders nutzlich:

- · Sie erlaubt es, Headerdateien so zu formulieren, dass man in beliebiger Reihenfolge auf sie zugreifen kann.

- · Varianten von Funktionen, die sich nur in Details unterscheiden, konnen in einer Quelldatei gespeichert werden. Die Entscheidung daruber, welche Variante ubersetzt werden soll, braucht erst beim Aufruf des Compilers getroffen zu werden.

## 10.2 Die Direktive #include

Die include -Direktive kennen wir bereits vollstandig. Ihre beiden Formen sind

#include < name >

#include " name "

Zur Erinnerung noch einmal der Unterschied zwischen den beiden Formen: Bei der zweiten Form sucht der Praprozessor die angegebene Datei zunachst im aktuellen Verzeichnis. Findet er sie dort nicht, sucht er in anderen Directories, die implementationsspezifisch festgelegt sein mussen. Die erste Form arbeitet ebenso, nur dass die Suche in der aktuellen Directory entfallt.

Faktisch heißt das:

- · die spitzen Klammern werden bei Standard-Headerdatei verwendet,
- · die Gansefußchen bei eigenen Dateien.

Der Name darf jeweils auch Pfadangaben enthalten.

## 10.3 Makros ( #define )

Dass man mit der Direktive #define Kontanten benennen kann, haben wir bereits gelernt und genutzt. Tatsachlich ist diese Moglichkeit nur ein Teilaspekt der Direktive. Zur Erinnerung noch einmal die Form der Direktive:

#define name [ersatztext]

An dem, was wir uber den Eintrag name bereits wissen, andert sich zunachst nur die Nomenklatur: Namen, die in einer define -Direktive definiert werden, werden vielfach als Makros bezeichnet. Die Ersetzungen, die ein Makro bewirkt, bezeichnet man als Expandierung des Makro .

Als ersatztext sind, uber unsere bisherigen Kenntnisse hinaus, beliebige Zeichenfolgen erlaubt. Diese Zeichenfolgen durfen insbesondere auch bereits zuvor definierte Makros enthalten oder leer sein.

Zulassig sind so zum Beispiel

```
#define BREITE 10 #define HOEHE (BREITE + 5)
```

Makros konnen Parameter erhalten:

#define name ( parameter ) ersatztext

Wichtig ist, dass die offnende Klammer dem Namen unmittelbar folgen muss - damit wird gekennzeichnet, dass die Klammer eine Parameterliste einleitet und nicht Bestandteil des Ersatztextes ist. Zum Beispiel konnen wir also

#define QUADRAT(x) x * x

definieren. An den Stellen, an denen der Makro expandiert werden soll, mussen Argumente angegeben werden, ahnlich wie bei einer Funktion. Die Folge ist praktisch eine doppelte Textersetzung: Der Makro einschließlich seiner Argumentliste wird durch den Ersatztext ersetzt; im Ersatztext werden die Parameter durch die Argumente ersetzt. So ergeben zum Beispiel die Aufrufe

```
x = QUADRAT(7.4);
```

- y = QUADRAT(x + 1);

letztlich die Quellanweisungen

```
x = 7.4 * 7.4; y = x + 1 * x + 1;
```

Das zweite Beispiel zeigt, dass der Makro QUADRAT unvollstandig definiert ist: Fur y resultiert ein Ausdruck, der offensichtlich nicht der Intention entspricht. Abhilfe schafft

#define QUADRAT(x) ((x) * (x))

Die außeren Klammern sind notig, da es Operatoren gibt, deren Prioritat hoher als die der Multiplikation ist.

Makros mit Parametern konnen wie Funktionen die Lesbarkeit eines Programms erhohen und Schreibarbeit sparen. Man muss sich aber daruber klar sein, dass zwischen Makros und Funktionen ganz wesentliche Unterschiede bestehen, die letztlich alle aus der Tatsache resultieren, dass Makros expandiert werden, bevor die eigentliche Ubersetzung beginnt und dass sie damit im ausfuhrbaren Programm uberhaupt nicht mehr in Erscheinung treten. Einige Details:

- · Dass auch bei Makros die Anzahlen von Parametern und Argumenten ubereinstimmen mussen, sollte klar sein. Die Parameter von Makros besitzen jedoch keine Typen, so dass die Argumente beliebige Typen besitzen konnen - Typen spielen ja erst spater eine Rolle, wenn der Compiler ubersetzt.
- · Jeder Aufruf eines Makro wird durch seinen Ersatztext ersetzt. Das hat einerseits zur Folge, dass der Maschinencode, der aus dem Ersatztext resultiert, mehrfach im ausfuhrbaren Programm steht, wahrend der Maschinencode, der aus einer Funktion resultiert, nur einmal im Programm steht. Dadurch entfallen andererseits die Sprunge und die Parameterzuordnung, mit denen Funktionsaufrufe verbunden sind.

Aus der Tatsache, dass ein Makro-Aufruf durch Textersetzung aufgelost wird, folgt auch, dass man vorsichtig sein muss, wenn man als Argumente Ausdrucke mit Nebeneffekten einsetzt. Aus dem Aufruf

- i = QUADRAT(j++);

resultiert so

i = ((j++) * (j++));

Abgesehen davon, dass der doppelte Nebeneffekt in der Regel nicht beabsichtigt sein wird, ist er auch gefahrlich. Mit den Gefahren von Nebeneffekten haben wir uns bereits in Abschnitt 4.11 befasst.

Man kann die Argumente von einem Makro auch als Zeichenkette verwenden. Dazu muss man ihnen bei der Verwendung # voranstellen. Ein nutzliches Beispiel ist im Abschnitt 10.5 angegeben.

## 10.4 Bedingte Compilation ( #if , #elif , #else )

Die Direktiven-Konstrukte, die bedingte Compilation erlauben, arbeiten mit der Logik der if -Anweisungen. Ihre Form ist allerdings durchaus anders:

- #if bedingung quellcode

```
[ #elif bedingung quellcode ] ... [ #else quellcode ] #endif
```

Die Bedingungen mussen konstante Ausdrucke sein und werden in der C-typischen Weise als wahr oder falsch interpretiert. Der Quellcode, der fur die einzelnen Falle vorgesehen ist, kann aus vollstandigen Anweisungen bestehen, braucht es aber nicht. Selbstverstandlich muss der Programmierer immer dafur sorgen, dass der Quellcode, der durch die Auswahl entsteht, vollstandige Quellanweisungen ergibt.

Wir betrachten ein Beispiel: Wir wollen einen Modul testen und dazu Ausgabeanweisungen in den Quellcode einfugen. Das konnen wir etwa in dieser Form tun:

```
#define TESTEN 1 ... #if TESTEN printf ("Kontrollpunkt A erreicht\n") #endif
```

Haben wir unsere Tests abgeschlossen, so brauchen wir die define -Direktive fur TESTEN nur durch

```
#define TESTEN 0
```

zu ersetzen, wahrend alle ubrigen Testzusatze im Modul stehen bleiben konnen: Der Praprozessor entfernt sie, so dass sie in Zukunft nicht mit ubersetzt werden. Der wesentliche Vorteil dieses Verfahrens zeigt sich, wenn wir Anderungen am Modul vornehmen und ihn danach erneut testen mussen: Durch erneute Anderung der define -Direktive konnen wir alle Testausgabe wieder aktivieren.

In einem Punkt ist das Beispiel noch ziemlich untypisch: Man wird dem Namen TESTEN keinen Wert geben, sondern nur

#define TESTEN

schreiben. Der Name wird dadurch zwar definiert, reprasentiert jedoch keinen Wert. Abfragen kann man das durch den Praprozessor-Operator

```
defined ( name )
```

Er pruft nur, ob der Name name definiert ist oder nicht; welchen Wert der Name ggf. reprasentiert, wird nicht gepruft. Wohlgemerkt: Dieser Operator steht nur in PraprozessorDirektiven zur Verfugung. Unser Beispiel konnte damit so aussehen:

```
#define TESTEN ... #if defined (TESTEN) printf ("Kontrollpunkt A erreicht\n") #endif
```

Dieses kann man mit einer weiteren Direktive noch kurzer und pragnanter schreiben: Die Direktive

```
#ifdef name
```

hat gerade dieselbe Wirkung wie

## #if defined ( name )

Bei #ifdef kann immer nur ein Name angegeben werden; bei if konnten wir zum Beispiel aber auch

```
#if defined ( name1 ) || defined ( name2 )
```

schreiben. ifdef ist also tatsachlich nur eine Kurzform fur Spezialfalle.

Es sollte jetzt auch schon klar sein, wie man Großen in mehreren Headerdateien definieren kann, ohne dass es zu Konflikten kommt, unabhangig von der Reihenfolge, in der auf die Headerdateien zugegriffen wird. Schreiben wir etwa

```
#if !defined (EOF) #define EOF (- 1)
```

#endif

so ist EOF beim ersten Auftreten dieser Direktivenfolge noch nicht definiert - die define -Direktive wird also wirksam. Findet der Praprozessor dieselbe Direktivenfolge erneut, ist EOF bereits definiert, so dass er die Wiederholung aus dem zu ubersetzenden Quellcode eliminiert.

## 10.5 Weitere Moglichkeiten ( #ifndef , #undef )

Neben den Direktiven, die wir kennengelernt haben, schreibt der Standard vier weitere Direktiven vor:

ifndef

ist das Pendent zu ifdef : Gepr¨uft wird, ob der angegebene Name nicht definiert ist.

undef

streicht den angegebenen Namen aus der Liste der definierten Namen, l¨oscht also praktisch den Makro.

error

erlaubt die Ausgabe eigener Fehlermeldungen w¨ahrend der Compilation.

line

erlaubt die Einflussnahme auf die Form der Meldungen des Compilers.

Daneben schreibt der Standard die Vordefinition von funf Makros vor:

- \_\_FILE\_\_ Name der Quelldatei, die gerade ¨ubersetzt wird
- \_\_LINE\_\_
- Nummer der Quellzeile, die gerade ¨ubersetzt wird
- \_\_DATE\_\_ Datum der Ubersetzung

¨

- \_\_TIME\_\_ ¨

Uhrzeit der Ubersetzung

\_\_STDC\_\_ wahr oder falsch oder nicht

, je nachdem, ob der Compiler ein Standardcompiler ist

Diese Makros sind faktisch Schlusselworten gleichgestellt und durfen vom Programmierer nicht fur eigene Zwecke verwendet werden.

Fur die Fehlersuche in großen Projekten mit mehreren Quelldateien konnen diese Makros sehr nutzlich sein. Zum Beispiel liefert

```
#define DEBUG ... #ifdef DEBUG #define REPORT printf("Zeile %d in %s erreicht\n", \ \_\_LINE\_\_ , \_\_FILE\_\_) #else #define REPORT #endif
```

eine einfache und ausbaufahige Hilfe bei der Uberwachung des Programmablaufs. Manchmal will man sich bei der Ausfuhrung eines Programms davon uberzeugen, dass eine bestimmte Programmzeile auch erreicht wurde. An solchen kritischen Stellen fugt man einfach die Zeile REPORT; in den Quelltext ein und erhalt dann eine aussagekraftige Kontrollausgabe, sofern DEBUG bei der Compilation definiert wurde. Ausbaubar ist das Makro z.B. so:

#define REPORTINT(x) printf("%s(%d) : Wert: %d\n", \ \_\_FILE\_\_ , \_\_LINE\_\_ , x)

Damit kann der aktuelle Wert von int -Variablen ausgegeben werden. Auf double -Variablen angewendet liefert das Makro naturlich Unsinn.

Schließlich kann man durch folgende Variante auch noch dafur sorgen, dass der Name der angesprochenen Variablen mit ausgegeben wird.

#define REPORTINT(x) printf("%s(%d) : " #x " == %d\n", \ \_\_FILE\_\_ , \_\_LINE\_\_ , x)

Wie schon erwahnt sorgt # dafur, dass das Argument in Anfuhrungszeichen eingeschlossen wird. REPORTINT(a); wird also zu

printf("%s(%d) : " "a" " == %d\n", ..., ..., a);

expandiert. Durch die Zusammensetzung von Zeichenkettenkonstanten ergibt sich ein zusammenhangender Formatstring fur printf . Maßnahmen wie solche raffinierten Testausgaben fass man untr dem Begriff ' low-level debugging' zusammen. Geschickt eingesetzt konnen sie Programmierer sehr bei der Fehlersuche unterstutzen.

## 10.6 Makro-Definition im Compileraufruf

Wir haben gesehen, wie man Makros mit den Direktive define definieren bzw. mit der Direktive undef loschen kann. Beides kann man auch durch Optionen im Aufruf des Compilers erreichen. Der gcc -Compiler unterstutzt dazu die Kommandozeilenparameter:

- -D name
- -D name = text
- -U name

Im Zusammenhang mit bedingter Compilation wird man diese Moglichkeit haufig nutzen, weil sie es einem erspart, zwischen den verschiedenen Compilerlaufen den Quellcode zu modifizieren. Man kann zum Beispiel direkt im Compileraufruf angeben, ob Testausgaben erzeugt werden soll oder nicht, ohne den entsprechenden Makro im Quellcode zu definieren oder zu loschen.