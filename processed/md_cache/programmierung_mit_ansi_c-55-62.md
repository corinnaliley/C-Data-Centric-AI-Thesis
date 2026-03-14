## Kapitel 5

## Zeichen und Strings

## 5.1 Stringvariablen und -konstanten

Den Datentyp char haben wir bereits kennengelernt. Ebenso wurde bereits angesprochen, wie Stringkonstanten aussehen. Wie sieht es mit Stringvariablen aus? Diese werden durch Felder von char -Werten realisiert. Ein Feld von Zeichen wird dadurch zu einem String, dass man hinter dem letzten ' echten' Zeichen ein Null-Zeichen speichert. Bei Stringkonstanten sorgt der Compiler sogar dafur, dass dieses Null-Zeichen automatisch angehangt wird. Das Null-Zeichen hat die Ordnungszahl 0 und kann im Quelltext als \0 geschrieben werden.

Damit wissen wir jetzt auch, warum 'w' und "w" nicht dasselbe bedeuten:

- · 'w' hat als Wert die Ordnungszahl des Zeichen w .
- · "w" hat als Wert die Zeichenfolge aus dem Zeichen w und einem nachfolgenden NullZeichen.

Vereinbart man Stringvariablen, so muss man bei der Langenangabe das Null-Zeichen stets mitzahlen. Von den Vereinbarungen

```
char text1[4] = "Text", /* nicht korrekt */ text2[5] = "Text", text3[6] = "Text";
```

ist die erste also nicht korrekt, weil sie das abschließende Null-Zeichen nicht berucksichtigt. Bei der zweiten Vereinbarung sind die Lange von Variable und Konstante gerade identisch. Die dritte Vereinbarung ist auch zulassig; bei ihr bleibt die letzte der sechs verfugbaren Zeichenpositionen frei.

Eine zusatzliche Moglichkeit fur Stringkonstanten sollte hier noch erwahnt werden, weil sie haufiger nutzlich ist: Langere Stringkonstanten kann man, in Teile zerlegt, in mehrere Zeilen schreiben. Dazu beendet man die Teile am Zeilenende mit einem Gansefußchen und leitet den nachsten Teil wieder mit einem Gansefußchen ein; zwischen den Teilen durfen neben dem Zeilenende-Zeichen auch Leerzeichen und horizontale Tabulatoren stehen. Der Compiler fugt diese Teile unmittelbar hintereinander. Welche der beiden Darstellungen

```
printf("Dieses ist ein nicht besonders langer String\n"); printf("Dieses ist ein nicht besonders " "langer String\n");
```

wir wahlen, ist also fur das Resultat gleichgultig. Man beachte das Leerzeichen am Ende des ersten Teilstring. Es ist notwendig, da beim Zusammenfugen der Zeichenketten keine zusatzlichen Leerzeichen eingefugt werden.

## 5.2 Arbeiten mit Strings

Offensichtlich erlaubt das Null-Zeichen zweierlei:

- · Das Ende eines Strings lasst sich erkennen, ohne dass man seine Lange vorab kennen muss. Die Funktionen scanf und printf sind zum Beispiel darauf angewiesen, weil sie die Lange ihres Formatierungsstrings ja nicht mitgeteilt bekommen.
- · Ein String kann seine Lange wahrend der Ausfuhrung des Programms dynamisch andern, da er ohne weiteres kurzer sein darf als die Stringvariable, in der er gespeichert ist.

Dass die Umkehrung strikt verboten ist, dass also ein String (einschließlich des abschließenden Null-Zeichens) die Lange des Feldes nie ubersteigen darf, ist klar: Da Stringvariablen letztlich Felder sind, gelten naturlich auch dieselben Regeln wie fur Felder. Erneut ist ausschließlich der Programmierer selbst dafur verantwortlich, dass keine Indexuberschreitungen vorkommen.

Auch fur das Anhangen des abschließenden Null-Zeichens an einen String ist, abgesehen von den Stringkonstanten und einigen Standardfunktionen, der Programmierer selbst verantwortlich.

Als erstes Beispiel betrachten wir eine Anweisungsfolge, die einen String kopiert, dabei seien quelle und ziel entsprechende Felder, wobei ziel groß genug ist um den zu kopierenden String aufzunehmen.

```
i = 0; while (quelle[i] != '\0') { ziel[i] = quelle[i]; i++; } ziel[i] = '\0';
```

Diese Formulierung ist fur C allerdings ziemlich untypisch. In der Regel wird man

```
i = 0; while (ziel[i] = quelle[i]) { i++; }
```

finden. Das funktioniert, weil das Zeichen '\0' gerade die Ordnungszahl Null besitzt. Die Bedingung der while -Anweisung wird also gerade dann falsch , wenn bei der Wertzuweisung das Null-Zeichen ubertragen wurde.

Die Vorteile der zweiten Formulierung gegenuber der ersten sind offensichtlich:

- · Die Schleife terminiert erst, wenn das Null-Zeichen bereits ubertragen ist, so dass es nicht hinter der Schleife besonders behandelt werden muss.
- · In jedem Schleifendurchlauf wird nur zweimal auf eine Vektorkomponente zugegriffen und nicht dreimal.

## 5.3 Ein-/Ausgabe von Zeichen

Da die Verarbeitung von Zeichen und Strings ein wesentlicher Aspekt von C ist, gibt es in der Standardbibliothek, vermittelt durch stdio.h , spezielle Funtionen zu ihrer Ein- und Ausgabe. Wir wollen uns zunachst nur die Funktionen fur Zeichen ansehen.

Die Funktion getchar () liefert als Funktionswert das nachste Zeichen von der Standardeingabe - oder ggf. den Wert EOF . Damit es mit EOF keine Probleme gibt, muss der

Funktionswert einen Typ besitzen, in dem sich alle Zeichen und zusatzlich EOF darstellen lassen, und das ist gerade der Typ int . Entsprechend muss der Funktionswert bei der Zuweisung an eine Zeichenvariable umgewandelt werden. Nach der Zuweisung ist kein Vergleich mit EOF mehr moglich, da EOF nicht im Wertebereich von char liegt.

Die Umkehrung ist die Funktion putchar (c) . Sie schreibt das Zeichen c auf die Standardausgabe. Dabei ist zu beachten: c kann den Typ int besitzen oder wird (wenn es den Typ char oder short besitzt) in den Typ int umgewandelt. Die Funktion selbst wandelt diesen Wert in den Typ unsigned char zuruck um, um das zu schreibende Zeichen zu bestimmen. Der Funktionswert ist das geschriebene Zeichen im Typ int , wenn kein Fehler aufgetreten ist, bzw. EOF sonst.

Als Beispiel betrachten wir eine Anweisungsfolge, die die Standardeingabe auf die Standardausgabe kopiert:

```
#include <stdio.h> int c; while ((c = getchar ()) != EOF) { putchar (c); }
```

Dass diese Anweisungsfolge (bei der ublichen Zuordnung von Standardein- und -ausgabe) kein Durcheinander auf dem Bildschirm erzeugt, hat zwei simple Hintergrunde: Zum einen arbeitet getchar wie scanf gepuffert, d.h. es wird zunachst das ENTER des Benutzers abgewartet und dann die eingegebene Zeile Zeichen fur Zeichen abgearbeitet. Zum anderen liefert getchar das Zeilenende-Zeichen wie alle anderen Zeichen auch an das Programm ab, das es mit putchar wieder schreibt.

Mit der Funktion getchar haben wir jetzt ubrigens auch eine Moglichkeit, bei der Eingabe mehrerer Zahlen den Benutzer dazu zu zwingen, jede Zahl einzeln mit ENTER abzuschließen: Nachdem wir eine Zahl in der Zeile interpretiert haben, uberspringen wir in einer Schleife alle Zeichen bis zum Zeilenende:

```
#include <stdio.h> #define ANZAHL 10 /* Anzahl Wiederholungen */ int main(void) { int i = ANZAHL , wert; /* Variablendeklarationen */ printf("Geben Sie die Zahlen ein. " "Bitte jeweils mit ENTER abschliessen!\n"); while (i--) { /* Schleife ! */ scanf("%d", &wert); /* eine Zahl lesen */ while (getchar () != '\n') { /* Zeilenrest ignorieren */ } printf("%d\n", wert); /* gelesene Zahl schreiben */ } return 0; }
```

Quelltext 5.1: Kopieren von 10 Zahlen (Eine Zahl pro Zeile)

Dabei nutzen wir: scanf bleibt auf dem ersten Zeichen stehen, das nicht mehr interpretiert wurde, spatestens also auf dem Zeilenende-Zeichen. Das ist durchaus wesentlich fur das Funktionieren des Programms: Die ' Wegwerf'-Schleife wird ja mindestens einmal durchlaufen, holt also zumindest ein Zeichen - wenn sie kein Zeichen der ' alten' Zeile mehr finden wurde (hier also zumindest das Zeilenende-Zeichen), wurde sie uber das Betriebssystem eine neue Eingabezeile anfordern - und das ware hier ein vollstandig unerwunschter Effekt.

## 5.4 Ein-/Ausgabe von Strings

Fur die Ein-/Ausgabe von Strings stehen spezielle Funktionen zur Verfugung. Wir haben aber bereits alternative Moglichkeiten kennengelernt: Sowohl mit den Funktionen scanf und printf als auch mit den Funktionen getchar und putchar konnen wir Strings lesen und schreiben. Zur Erinnerung: Der entsprechende Formatbeschreiber fur Ein- und Ausgabe ist %s .

Sehen wir uns zunachst die Ausgabe an. Sie ist mit beiden Moglichkeiten recht einfach:

```
#define LAENGE ?? char str[LAENGE]; int i; /* ... Initialisierung von str ... */ printf ("%s", str); /* Variante 1 */ i = 0; /* Variante 2 */ while (str[i]) { putchar(str[i]); i++; }
```

Bei der Schleife sieht man direkt, dass die Ausgabe nur dann korrekt funktioniert, wenn der String korrekt durch ein Null-Zeichen abgeschlossen ist. Beim Aufruf von printf sieht man das zwar nicht, es gilt aber ebenso.

Die Eingabe ist, wenn man sie naiv programmiert, ahnlich einfach:

```
#define LAENGE ?? char str[LAENGE]; int i; scanf ("%s", str); /* Variante 1 */ i = 0; /* Variante 2 */ while ((str[i] = getchar ()) != '\n') { i++; } str[i] = '\0';
```

Ganz aquivalent sind beide Eingaben nicht:

- · scanf uberliest zunachst ' white spaces' und liest danach Zeichen, bis ein erneutes ' white space' gefunden wird, d.h. ein Leerzeichen, ein (horizontales) Tabulatorzeichen oder ein Zeilenende-Zeichen.

- · In der Schleife wird auf jeden Fall von der aktuellen Position in der Zeile bis zum Zeilenende gelesen. Die Anweisung hinter der Schleife ersetzt das Zeilenende-Zeichen durch das Null-Zeichen.

' Naiv' sind die beiden Realisierungen deshalb, weil in beiden Fallen nicht sichergestellt wird, dass der gelesene String in die Variable str hineinpasst.

Um den Aufruf von scanf enstprechend sicherer zu machen, benotigt man die erweiterten Moglichkeiten von Formatbeschreibern, wie sie in Kapitel 16 beschrieben werden. Die Schleife sollten wir jedoch geeignet modifizieren, was auch nicht ubermaßig schwierig ist:

```
#define LAENGE ?? char str[LAENGE]; int i; i = 0; while (i < LAENGE && (str[i] = getchar ()) != '\n') { i++; } if (i == LAENGE) { printf("Eingegebener String zu lang!\n"); return 1; } else { str[i] = '\0'; }
```

## 5.5 Klassifizierung von Zeichen

Neben stdio.h stellen auch die Standardheaderdateien ctype.h und string.h Standardfunktionen zur Verarbeitung von Zeichen und Strings zur Verfugung. Vielmehr stehen zwei weitere Headerdateien zur Verfugung:

- · Die Headerdatei ctype.h definiert Funktionen zur Klassifizierung von Zeichen und zur Umwandlung zwischen Groß- und Kleinbuchstaben.
- · Die Headerdatei string.h definiert Funktionen mit denen man
- -Strings kopieren, konkatenieren oder vergleichen,
- -in Strings nach Zeichen oder Strings suchen oder
- -verschiedene andere Dinge erledigen kann.

Der Header ctype.h soll an dieser Stelle kurz behandelt werden, weil zum einen der Umfang der Headerdatei nicht groß, zum anderen die Funktionen sehr grundlegend und einfach sind.

Die Funktionen tolower und toupper wandeln Groß- in Kleinbuchstaben bzw. Kleinin Großbuchstaben um; andere Zeichen bleiben unverandert. Das Argument ist jeweils das ggf. umzuwandelnde Zeichen in int -Darstellung, der Funktionswert das resultierende Zeichen in int -Darstellung.

Die ubrigen Funktionen haben als Argument ebenfalls ein Zeichen in int -Darstellung; ihr Funktionswert ist ungleich oder gleich Null und kann entsprechend als wahr oder falsch interpretiert werden, je nachdem, ob das Zeichen zu einer bestimmten Gruppe von Zeichen gehort oder nicht. Eine Liste der Funktionen ist in Tabelle 5.1 zu finden.

In alle Funktionen (einschließlich tolower und toupper ) darf man ubrigens als Argument auch EOF ubergeben - und erhalt dann EOF als Funktionswert zuruck.

Tabelle 5.1: Funktionen zur Klassifizierung von Zeichen

| Funktion   | Beschreibung                                    |
|------------|-------------------------------------------------|
| islower    | Kleinbuchstabe                                  |
| isupper    | Großbuchstabe                                   |
| isalpha    | Buchstabe, klein oder groß                      |
| isdigit    | Dezimalziffer                                   |
| isxdigit   | Hexadezimalziffer                               |
| isalnum    | Buchstabe oder Ziffer                           |
| iscntrl    | Steuerzeichen (nicht druckbar)                  |
| isgraph    | druckbares Zeichen (ohne Leerzeichen)           |
| isprint    | druckbares Zeichen (einschließlich Leerzeichen) |
| ispunct    | druckbares Sonderzeichen (ohne Leerzeichen)     |
| isspace    | white space'                                    |

'

Als Beispiel betrachten wir einen Programmausschnitt, in dem eine Hexadezimalzahl als Zeichenfolge eingelesen und in die entsprechende interne Darstellung umgewandelt wird. Wir gehen davon aus, dass die eingegebene Zahl nicht großer als UINT\_MAX ist. Die Interpretation soll stoppen, sobald das erste nicht interpretierbare Zeichen gefunden wird. Diese Aufgabe konnte man zwar auch mit scanf losen - es ist aber durchaus nutzlich, wenn man sich einmal Gedanken daruber macht, was bei der Ausfuhrung einer Standardfunktion tatsachlich passiert.

```
#include <stdio.h> #include <ctype.h> ... int c; unsigned int x; x = 0; while ( isxdigit( c = getchar() ) ) { x = x * 16; if ( isdigit(c) ) { x = x + c - '0'; } else { x = x + toupper(c) - 'A' + 10; } }
```

Diese Anweisungsfolge leistet das Verlangte, falls in dem verwendeten Zeichensatz die zehn Ziffern und die Buchstaben A bis F jeweils unmittelbar aufeinanderfolgen. Das ist die einzige Voraussetzung. Ansonsten ist dieses Programmstuck ohne weiteres portierbar auf Implementationen, denen z.B. nicht der ASCII-Zeichensatz zugrunde liegt.

Die vielen Klammern sind ubrigens alle wirklich notig:

- · Die Klammern um die Bedingung der while -Anweisung und um die Argumentliste (das Argument) von isxdigit sind offensichtlich notwendig.
- · Beim Aufruf einer Funktion muss das Klammernpaar auch dann folgen, wenn die Funktion keine Parameter besitzt. (Wenn Sie diese Klammern wegließen, wurde der Compiler also ' maulen' - allerdings nicht wegen fehlender Klammern, sondern wegen inkompatibler Typen; die Hintergrunde konnen wir erst spater behandeln.)

Ein sachlicher Mangel der Anweisungsfolge soll nicht unerwahnt bleiben: Es ist keinerlei Sicherung gegen eine Bereichsuberschreitung eingebaut!