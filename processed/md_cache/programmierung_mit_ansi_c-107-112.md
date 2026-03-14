## Kapitel 9

## Ubersicht uber die Standardbibliothek

Zu jeder C-Implementierung gehort standardmaßig eine Sammlung vordefinierter Routinen, die Ein-/Ausgabe und andere Operationen ermoglichen. Diese Sammlung wird Standardbibliothek genannt.

## 9.1 Headerdateien

Die Nutzung der Standardbibliothek erleichtern die Standard-Headerdateien , die der Standard vorschreibt, wenn eine Standardbibliothek vorhanden ist, und auf die man mit #include -Direktiven zugreifen kann. Man konnte die entsprechenden Deklarationen naturlich auch explizit in seine Programme schreiben - aber das ware ziemlich unsinnig.

Insgesamt schreibt der Standard 15 Headerdateien vor. Einige davon haben wir bereits kennengelernt:

| ctype.h   | Zeichenverarbeitung                      |
|-----------|------------------------------------------|
| float.h   | Interne Datenformate (Gleitkommatypen)   |
| limits.h  | Interne Datenformate (ganzzahlige Typen) |
| stdio.h   | Ein-/Ausgabe                             |
| string.h  | Stringverarbeitung                       |

Einige weitere Headerdateien werden in diesem Abschnitt naher behandelt, auch wenn fur eine vollstandige Besprechung die Zeit fehlt:

assert.h

Testhilfen

errno.h

Fehlernummern

math.h

mathematische Funktionen

stddef.h

elementare Typen

stdlib.h

diverse Hilfsroutinen

time.h

Termine und Zeiten

Der Vollst¨andigkeit halber seien auch die ¨ubrigen Headerdateien erw¨ahnt:

locale.h

l¨anderspezifische Darstellungen (Zeiten, Geldbetr¨age,

usw.)

setjmp.h

Spr¨unge zwischen Funktionen

signal.h

Behandlung von Signalen ( ' Interrupts')

stdarg.h Funktionen mit variabler Argumentzahl (wie printf )

Manche Deklarationen sind in mehreren Headerdateien enthalten. Das erlaubt es, alle Headerdateien unabhangig voneinander zu nutzen, und insbesondere, die include 's fur

die Headerdateien in beliebiger Reihenfolge anzugeben. Andererseits erfordert es, die Headerdateien so gegeneinander abzusichern, dass der Compiler keine Deklarationen doppelt findet. Dieses ist mit bedingter Compilation moglich; die im nachsten Kapitel behandelt wird.

Fur das Verstandnis des weiteren ist es hilfreich daran zu erinnern, dass die Headerdateien die genannten Funktionalitaten nur bekannt machen. D.h. sie enthalten z.B nur Prototypen von Funktionen. Dadurch wird es dem Compiler moglich, den korrekten Funktionsaufruf im Quelltext zu uberprufen. Die eigentlichen Implementationen konnen dagegen in Binardateien gesammelt sein, die durch Vorkompilation oder anders erzeugt wurden.

## 9.2 Mathematische Funktionen

Die numerischen Funktionen, die man ublicherweise in Programmiersprachen zur Verfugung hat, bietet auch C. Die Prototypen sind in math.h enthalten.

Tabelle 9.1: Mathematische Funktionen mit einem Argument

| Funktion   | Beschreibung                                                                               |
|------------|--------------------------------------------------------------------------------------------|
| sin        | Sinus                                                                                      |
| cos        | Cosinus                                                                                    |
| tan        | Tangens                                                                                    |
| asin       | Arcus Sinus                                                                                |
| acos       | Arcus Cosinus                                                                              |
| atan       | Arcus Tangens                                                                              |
| sinh       | Sinus hyperbolicus                                                                         |
| cosh       | Cosinus hyperbolicus                                                                       |
| tanh       | Tangens hyperbolicus                                                                       |
| exp        | Exponentialfunktion                                                                        |
| log        | naturlicher Logarithmus                                                                    |
| log10 sqrt | Logarithmus zur Basis 10 Quadratwurzel                                                     |
| ceil       | Aufrundung auf ganze Zahl                                                                  |
| floor      | (das Resultat ist ein double -Wert!) Abrundung auf ganze Zahl (das Resultat ist ein double |
| fabs       | -Wert!) Absolutbetrag (Achtung: abs fur int -Argumente                                     |

Viele der Funktionen haben die Deklaration

double name (double);

d.h. sie haben einen double -Parameter und liefern einen double -Funktionswert. Diese Funktionen sind in Tabelle 9.1 aufgelistet. Dazu ist noch wichtig zu erwahnen, dass die Winkelfunktionen alle im Bogenmaß (d.h. voller Kreisumfang entspricht 2 π ) rechnen. Von den ubrigen Funktionen sind drei besonders erwahnenswert, die jeweils zwei double -Parameter besitzen und einen double -Funktionswert liefern:

atan2 liefert bei einem Aufruf atan2 (y, x) den Arcus Tangens von y/x , wobei auch eines der beiden Argumente Null sein darf (aber nicht beide gleich-

zeitig). Der Wertebereich ist [ -π, π ], unter Berucksichtigung der Vorzeichen beider Argumente, wahrend der Wertebereich bei atan nur [ -π/ 2 , π/ 2] ist.

glyph[negationslash]

liefert bei einem Aufruf fmod (x, y) die Nachkommastellen des Quotienten x/ | y | ( y = 0). Nutzlich ist diese Funktion zum Beispiel, wenn man Winkel modulo 2 π rechnen mochte.

liefert bei einem Aufruf pow (x, y) die Potenz x y .

fmod

pow

Der Standard spricht nur von der Standardbibliothek. Trotzdem konnen die Funktionen auf mehrere Bibliotheksdateien (d.h. Binardateien die Implementationen von Funktionen enthalten) verteilt sein. Nicht immer durchsucht in solchen Fallen der Linker auch alle Bibliotheksdateien. Fur diesen Fall und auch fur die Moglichkeit der Erzeugung und des Testens eigener Bibliotheken gibt es Linker-Optionen, mit denen man die zu verwendenden Bibliotheksdateien angeben kann.

Speziell im Falle der Verwendung der mathematischen Bibliotheksfunktionen ist dies meist erforderlich und wird gern vergessen. Speziell im Falle des gcc benotigt man dazu die Option -lm im Aufruf des gcc , die hinter die Namen der Dateien geschrieben wird, etwa so:

gcc -Wall prog.c -lm gcc -Wall -o prog prog.c -lm

Hintergrund: Bei einigen Rechnern beherrscht der Hauptprozessor selbst nur ganzzahlige Arithmetik. Fur Gleitkommaarithmetik gibt es zwei Moglichkeiten: Man kann einen zusatzlichen Gleitkommaprozessor einbauen oder man muss die Gleitkommaarithmetik durch entsprechende Funktionen realisieren. Dass die Bibliotheken in beiden Fallen zwar dieselben Eingangspunkte haben, daruber hinaus aber sehr verschieden aussehen, sollte offensichtlich sein. Sieht man nun fur die mathematischen Funktionen eine besondere Bibliothek vor, so braucht man nur diese in verschiedenen Varianten zu unterhalten, wahrend die ' Hauptbibliothek' nur in einer Variante existiert.

## 9.3 Fehlerbehandlung

Die Headerdatei errno.h enthalt zwar nur drei Deklarationen, bietet aber trotzdem interessante Moglichkeiten:

Die Variable errno wird von vielen Bibliotheksfunktionen genutzt, um eventuelle Fehler zu markieren. Besitzt errno den Wert Null, so bedeutet das, dass kein Fehler aufgetreten ist, wahrend positive Werte Fehler anzeigen.

Allerdings: errno wird nur einmal automatisch auf Null zuruckgesetzt, namlich beim Start des Programms. Mochte man eine bestimmte Operation auf fehlerfreien Ablauf hin uberwachen, so ist es zweckmaßig, errno vor der Operation selbst auf Null zuruckzusetzen.

Welche Fehler durch welche Nummern gekennzeichnet werden, uberlasst der Standard den Implementatoren. Er schreibt jedoch eine Funktion (in string.h ) vor, mit der man Fehlernummern in Klarschrift umsetzen kann. Außerdem erlauben die beiden anderen Deklarationen in errno.h die direkte Behandlung der haufigsten Fehler, namlich Fehler bei den mathematischen Funktionen:

- · EDOM ist der Wert, den errno erhalt, wenn ein Argument außerhalb des zulassigen Wertebereichs liegt. Der Funktionswert der mathematischen Funktion ist in diesem Falle undefiniert.
- · ERANGE ist der Wert, den errno erhalt, wenn der Funktionswert außerhalb des zulassigen Wertebereichs liegt. Der Funktionswert der mathematischen Funktion wird dann

auf den Wert HUGE VAL gesetzt, mit dem korrekten Vorzeichen. HUGE VAL ist in math.h deklariert.

Durch den Aufruf sqrt (- 2.0) wurde etwa errno auf den Wert EDOM und durch den Aufruf exp (2000.0) auf den Wert ERANGE gesetzt. Beim ersten Aufruf ware der Funktionswert undefiniert, beim zweiten HUGE VAL (vergleichbar mit ±∞ ).

Damit errno in allem Modulen eines komplexen Programms zur Verfugung stehen kann, darf die Variable mit nur einem Speicherplatz verbunden sein. Darum ist die Variable in errno.h extern deklariert und steht in allen Modulen zur Verfugung, die errno.h durch #include einbinden.

Sogar nur eine Deklarationen enthalt die Headerdatei assert.h , die zum Test von Programmen dient: Die Funktion

void assert(int bedingung );

bewirkt nichts, wenn bedingung den Wert wahr besitzt. Sollte der Wert falsch sein, wird das Programm mit einer Fehlermeldung abgebrochen.

Eine zweite Definition wird in der Headerdatei zwar verwendet, ist aber nicht in ihr enthalten: Wenn der Name NDEBUG nicht definiert ist, werden die Tests wie beschrieben ausgefuhrt; ist der Name dagegen definiert, unterbleiben die Tests. Das erlaubt, die Aufrufe von assert im Quellcode stehen zu lassen, obwohl sie nicht ausgefuhrt werden sollen - vielleicht braucht man sie nach Anderungen am Programm ja noch einmal. Man muss nur eine Definition fur NDEBUG ins Programm einfugen. Namen werden mit der #define -Direktive definiert; auf Details geht das nachste Kapitel ein.

## 9.4 Elementare Typen

Die Typdeklarationen und Konstantendefinitionen, die stddef.h enthalt, sind weitgehend auch in anderen Headerdateien enthalten. Auf einige dieser Deklarationen werden wir noch zuruckkommen.

## 9.5 Diverse Hilfsroutinen

Wundert man sich bei mancher Headerdatei uber die Zusammenstellung der Deklarationen, so enthalt insbesondere stdlib.h ein ziemlich buntes Gemisch von Deklarationen:

- · Es gibt Funktionen, die den Inhalt eines String als Zahl interpretieren - z.B. atoi .

```
int atoi(const char *s);
```

Daneben gibt es noch eine Reihe weiterer Umwandlungsfunktionen.

- · Es gibt Funktionen zur dynamischen Bereitstellung von Speicher - und naturlich auch zur Freigabe solchen Speichers. Wegen ihrer besonderen Bedeutung ist ihnen ein extra Kapitel gewidmet.
- · Zwei Funktionen ( abort und exit ) erlauben die Beendigung eines Programms an beliebiger Stelle, also ohne geschachtelte Funktionsaufrufe erst bis ins Hauptprogramm zuruckverfolgen zu mussen:

```
void abort(void);
```

void exit(int status);

- · Mit getenv kann man sich Informationen uber die Betriebssystemumgebung beschaffen oder mit system die Ausfuhrung von Betriebssystemkommandos verlangen.

- · Die Funktion qsort sortiert einen Vektor; mit bsearch kann man in einem sortierten Vektor nach einer Komponente mit einem bestimmten Wert suchen.
- · Es gibt Funktionen, die die Verarbeitung erweiterter Zeichensatze erlauben.

Zwei Gruppen von Funktionen aus stdlib.h fehlen in diesem sehr pauschalen Uberblick. Sie sollen jetzt ein wenig ausfuhrlicher behandelt werden:

## Die Funktion

int rand(void);

realisiert einen Pseudo-Zufallszahlen-Generator : Sie liefert bei jedem Aufruf eine ganze Zahl aus dem Bereich [0 , RAND MAX ], wobei RAND MAX ≥ 32767(= 2 15 -1) gelten muss.

Von einem ' Pseudo'-Zufallszahlen-Generator spricht man, weil die Zahlen, die rand liefert, nicht wirklich zufallig sind. Vielmehr gibt es eine bestimmte Formel, wie aus dem Startwert bzw. dem letzten gelieferten Wert die nachste zu liefernde Zahl zu berechnen ist.

Pseudo-Zufallszahlen sind zum Programmtest oft nutzlich. Betrachten wir als Beispiel den Test einer Sortierfunktion: Man mochte zwar moglichst gut verteilte Zahlen haben, wofur der Generator sorgt - man kann aber auch nicht bei jedem Test andere Werte brauchen, weil eventuelle Fehler reproduzierbar sein mussen. Um verschiedene Zahlenfolgen erzeugen zu konnen, kann man den Startwert (standardmaßig 1) mit der Funktion srand angeben; ihr Prototyp ist

## void srand(unsigned int start);

Steckt man hier etwa Sekunden und Minuten der aktuellen Uhrzeit hinein, so lassen sich die Zahlenfolgen ohne weiteres nicht mehr nachvollziehen. Zumindest werden die Zahlen so ' zufallig', dass sie fur Spiele und ahnliche Programme vollstandig ausreichen.

Genau genommen liefert rand ' gleich verteilte' Zahlen, d.h. die Zahlen sind gleichmaßig uber den erlaubten Wertebereich verteilt. Braucht man fur einen Test etwa Zahlen mit einer Gauß-Verteilung, so kann man rand nicht ohne weiteres verwenden.

Zur zweiten Gruppe gehoren vier Funktionen zur ganzzahligen Arithmetik: Die Funktionen abs und labs haben als Argument einen int - bzw. long -Ausdruck und liefern als Funktionswert dessen Absolutbetrag; die Funktionen div und ldiv haben als Argumente zwei int - bzw. long -Ausdruck und liefern als Funktionswert sowohl den ganzzahligen Quotienten als auch den Rest - wie man erreichen kann, dass Funktionswerte aus mehreren Einzelwerten bestehen, werden wir noch kennenlernen. Das Stichwort ist ' Strukturen'.

## 9.6 Termine und Zeiten

Die verwendete Prozessorzeit des aktuellen Prozesses liefert die Funktion

clock\_t clock(void);

die in time.h deklariert ist. Dabei ist clock t ein ganzzahliger Typ, der ebenfalls in time.h deklariert ist. Dies geschieht durch eine typedef -Deklaration - eine typische Anwendung von typedef .

Dieses ist erneut eine typische Vorgehensweise des Standard: Vorgeschrieben wird zwar ein ganzzahliger Typ, nicht jedoch ein konkreter ganzzahliger Typ. Das erlaubt den Implementatoren, zwischen short , int und long zu wahlen, abhangig von der Hardware des Rechners, auf dem die Implementation laufen soll. Fur den Programmierer wird die konkrete Wahl durch den speziellen Typ weitestgehend transparent, ohne dass sich Restriktionen

ergeben: Bei arithmetischen Operationen sorgt der Compiler fur die entsprechenden Umwandlungen! Probleme gibt es allenfalls bei der Ausgabe mit printf , weil man nicht weiß, welchen Formatbeschreiber man zu verwenden hat; das lasst sich aber auch losen, indem man den Wert hierfur zunachst in long umwandelt.

Die Maßeinheit von clock ist implementations-spezifisch. In Sekunden kann man den Funktionswert von clock umrechnen, indem man ihn durch die ebenfalls in time.h definierte Konstante CLOCKS PER SEC dividiert.

Ebenso lasst der Standard offen, zu welchem Zeitpunkt die Zeitmessung gestartet wurde. Es handelt sich dabei um Implementationsabhangiges Verhalten, das entsprechend in der jeweiligen Dokumentation der Implementation beschrieben wird. Mogliche Zeitpunkte fur den Start der Zeitmessung sind der Zeitpunkt des Programmstarts oder der erste Aufruf von clock im Programm.

Die ubrigen Funktionen aus time.h , etwa die Bestimmung von Datum und Uhrzeit, erfordern Kenntnisse, die wir derzeit noch nicht haben.