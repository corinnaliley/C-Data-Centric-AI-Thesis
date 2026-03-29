## Anhang B

## Die C-Standardbibliothek

Die Header-Dateien der CStandardbibliothek sind hier vollstandig aufgezahlt, nicht jedoch die der enthaltenen Elemente. Hier sollen nur die (subjektiv) wichtigsten Konstanten, Typen, Funktionen und Variablen aufgelistet werden. Auf UNIX/LINUX-Systemen sollte man 3 fkt bzw. man 3 datei die Dokumentation zur Funktion fkt bzw. zur Headerdatei datei .h der Standardbibliothek liefern.

- · assert.h

debugging-Hilfen:

Makro NDEBUG - Funktion assert

- · ctype.h

Funktionen zur Klassifizierung/Umwandlung von Zeichen

Argument und Funktionswert der Funktionen sind jeweils vom Typ int . Hat das ubergebene Argument den Wert EOF, so ist der Funktionswert bei allen Funktionen EOF. Wird die Funktion mit einer char -Variablen als Argument aufgerufen, so wird deren Wert implizit in einen int -Wert umgewandelt und es werden folgende Werte zuruckgeliefert:

- -int isalnum(int c)
- - ungleich 0, falls c ein alphanumerisches Zeichen reprasentiert (Ziffer oder Buchstabe), 0 sonst.
- -int isalpha(int c)
- - ungleich 0, falls c Buchstaben reprasentiert, 0 sonst.
- -int iscntrl(int c)
- - ungleich 0, falls c ein Steuerzeichen reprasentiert (siehe Zeichensatz), 0 sonst
- -
- int isdigit(int c) - ungleich 0, falls c Ziffer reprasentiert, 0 sonst.
- -int isgraph(int c)
- - ungleich 0, falls c druckbares Zeichen (ohne Leerzeichen) reprasentiert, 0 sonst.
- -int islower(int c)
- - ungleich 0, falls c Kleinbuchstaben reprasentiert, 0 sonst.
- -int isprint(int c)
- - ungleich 0, falls c druckbares Zeichen (mit Leerzeichen) reprasentiert, 0 sonst.
- -int ispunct(int c)
- - ungleich 0, falls c ein druckbares Sonderzeichen reprasentiert, 0 sonst.

- -int isspace(int c)
- - ungleich 0, falls c Leerraum reprasentiert (also Leerzeichen oder eines der Zeichen \ f, \ n, \ r, \ t, \ v) , 0 sonst
- -int isupper(int c)
- - ungleich 0, falls c Großbuchstaben reprasentiert, 0 sonst.
- -int isxdigit(int c)
- - ungleich 0, falls c hexadezimale Ziffer reprasentiert, 0 sonst.
- -int tolower(int c)
- - Falls der Argumentwert ein Wert aus dem Bereich 'A' bis 'Z' ist, so wird der entsprechende ' Kleinbuchstabenwert' (aus 'a' bis 'z' ) zuruckgegeben. Anderenfalls wird der Argumentwert zuruckgegeben.
- -int toupper(int c)
- - wie tolower nur umgekehrt: zu ' Kleinbuchstabenwert' wird (soweit moglich) entsprechender ' Großbuchstabenwert' zuruckgegeben

## · errno.h

Fehlerbehandlung fur mathematische Funktionen:

Makro EDOM - Makro ERANGE - globale Variable errno

- · float.h

Angaben zu den Gleitkommazahlwertebereichen:

FLT MAX -

- FLT MIN -
- DBL MAX -
- DBL MIN -
- LDBL MAX -

LDBL MIN

·

iso646.h

alternative Schreibweisen fur logische Operatoren

## · limits.h

Angaben zu den Ganzzahlwertebereichen:

CHAR BIT -CHAR MAX -CHAR MIN -SCHAR MAX -SCHAR MIN -UCHAR MAX -SHRT MAX -SHRT MIN -USHRT MAX -INT MAX -INT MIN -UINT MAX -LONG MAX -LONG MIN -ULONG MAX

- · locale.h Sprach-, Schrift-, Zeitrechnungs- und wahrungsspezifische Angaben
- · math.h

Gleitkomma-Arithmetik:

Makro HUGE VAL , Funktionen: fabs -ceil -floor -

acos -asin -atan -

cos -sin -tan -cosh -sinh -tanh -exp -

log -log10 -

pow -sqrt

- · setjmp.h

Sprunge in andere Programmteile

- · signal.h

Signal(Interrupt)behandlung

- · stdarg.h

Variable Argumentlisten fur Funktionen mit einer variablen Anzahl von Parametern (wie z.B. printf und scanf ):

va list -va start -va arg -va end

## · stddef.h

Definitionen von einfachen Typen und Werten

- -NULL
- - der ' Nullzeiger', eine benannte Konstante vom Zeigertyp deren Wert verschieden ist von jedem echtenSZeigerwert
- -size t

- vorzeichenloser ganzzahliger Typ dessen Wertebereich alle zulassigen Speicherbereichsgroßen umfasst (m.a.W.: Menge der Werte, die vom sizeof -Operator (in der jeweiligen Implementation) zuruckgeliefert werden konnen)

- · stdio.h

Ein- und Ausgabe-Funktionen (siehe die Kapitel des Skripts zur Ein- und Ausgabe)

- · stdlib.h

Umwandlung von Strings zu Zahlwerten:

atof -atoi -atol -strtod -strtol -strtoul

Pseudozufallsgenerator:

RAND MAX -rand -srand

dynamische Speicherverwaltung:

malloc -calloc -realloc -free

ganzzahlige Mathematik:

div t -ldiv t -abs -div -labs -ldiv

Programmabbruch:

EXIT FAILURE -EXIT SUCCESS -exit -abort -atexit

Systemaufrufe:

system -getenv

Algorithmen:

bsearch -qsort

Umwandlungen zwischen verschiedenen Zeichensatzen

## · string.h

Stringbearbeitung

- -char *strerror(int Kennzahl);
- - liefert den Zeiger auf den Anfag des Strings, der die Klarschrift-Fehlermeldung zum Fehler mit dem Fehlercode Kennzahl enthalt
- -size t strlen(const char *s);
- - liefert die Anzahl der Zeichen des Strings, auf dessen Anfang s zeigt. Das Stringende-Zeichen des Strings wird dabei nicht mitgezahlt.

- -char *strcpy(char *s1, const char *s2);
- - kopiert (byteweise) die Zeichen des Strings auf dessen Anfang s2 zeigt (inklusive Stringende-Zeichen) in einen Speicherbereich auf dessen Anfang s1 zeigt. Der Wert von s1 wird als Funktionswert zuruckgeliefert.
- -char *strncpy(char *s1, const char *s2, size t n); - wie strcpy , jedoch werden genau n Zeichen geschrieben. Außerdem wird das Kopieren beendet, sobald das Stringende-Zeichen im Quellstring gefunden wurde und erganzt danach nur noch (binare) Nullen. Das bedeutet insbesondere: Wenn der zu kopierende String aus n oder mehr Zeichen besteht, wird der kopierte String nicht durch ein Stringende-Zeichen abgeschlossen. Der Wert von s1 wird als Funktionswert zuruckgeliefert.
- -char *strcat(char *s1, const char *s2);
- - kopiert den String auf dessen Anfang s2 zeigt hinter den String auf dessen Anfang s1 zeigt. Das Stringende-Zeichen von s1 wird dabei uberschrieben. Hinter dem letzten kopierten Zeichen wird das Stringende-Zeichen automatisch angehangt. Der Wert von s1 wird als Funktionswert zuruckgeliefert.
- -char *strncat(char *s1, const char *s2, size t n); - wie strcat , jedoch wird das Kopieren vorzeitig beendet, sobald n Zeichen ubertragen wurden.
- -
- int strcmp(const char *s1, const char *s2)
- - liefert einen int -Wert kleiner, gleich oder großer Null, je nachdem, ob der String, auf dessen Anfang s1 zeigt, lexikographisch kleiner, gleich oder großer ist als der String, auf dessen Anfang s2 zeigt. [Ein String heißt lexikographisch kleiner als ein anderer, wenn in ihm an der ersten Unterscheidungsstelle ein kleinerer char -Wert steht als im anderen String.
- -int strncmp(const char *s1, const char *s2, size t n);
- - wie strcmp , jedoch werden hochstens n
- Zeichen verglichen
- - liefert Zeiger auf das zuerst gefundene Vorkommen des Zeichens c in dem String, auf dessen Anfang s zeigt bzw. den Nullzeiger, falls das Zeichen nicht
- char *strchr(const char *s, int c) gefunden wurde.
- -strrchr
- - wie strchr , jedoch wird beginnend beim Stringende-Zeichen in Richtung Anfang gesucht.
- -strspn
- -strcspn
- -strpbrk
- -char *strstr(const char *s1, const char *s2)
- - sucht das erste Vorkommen des Strings auf dessen Anfang s2 zeigt, im String, auf dessen Anfang s1 weist (dabei wird das Stringende-Zeichen nicht mit verglichen). Der Funktionswert ist der Zeiger auf den Anfang der gefundenen Teilfolge bzw. der Nullzeiger.
- -strtok

## Speicherbearbeitung

- -memchr
- -memcmp
- -
- -

- void *memcpy(void *s1, const void *s2, size t n) zeigt zeigt. Funkti-
- - kopiert die ersten n Bytes eines Speicherbereichs auf dessen Anfang s2 in die ersten n Bytes des Speicherbereichs auf dessen Anfang s1 onswert ist s1 .
- -memmove
- -memset

## · time.h

Zeitmessung:

CLOCKS PER SEC -clock t -clock

Datums- und Uhrzeitbestimmung:

time t -time -difftime -struct tm -gmtime -localtime -asctime -ctime

## · wchar.h

- Umwandlung von Strings zu Zahlwerten fur den erweiterten Zeichensatz

String- und Speicherbearbeitung fur den erweiterten Zeichensatz Ein- und Ausgabe fur den erweiterten Zeichensatz

- · wctype.h

Zeichenuntersuchung fur den erweiterten Zeichensatz

## Abbildungsverzeichnis

| 7.1                 | Turme von Hanoi . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         | 77   |
|---------------------|-----------------------------------------------------------------------------------------|------|
|                     | 11.1 Speicheranordnung eines Vektors mit 6 Komponenten . . . . . . . . . . .            | 112  |
|                     | 11.2 Speicheranordnung einer (2 × 3)-Matrix . . . . . . . . . . . . . . . . . . .       | 112  |
|                     | 14.1 Verkettete Liste . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 156  |
| A.1                 | Beispiel eines UNIX-Filesystems . . . . . . . . . . . . . . . . . . . . . . .           | 179  |
| Tabellenverzeichnis | Tabellenverzeichnis                                                                     |      |
| 2.1                 | Vorgeschriebene Wertebereiche fur Ganzahltypen . . . . . . . . . . . . . .              | 11   |
| 2.2                 | Escapesequenzen . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         | 13   |
| 2.3                 | Schlusselworter von C . . . . . . . . . . . . . . . . . . . . . . . . . . . . .         | 18   |
| 3.1                 | Kennbuchstaben fur Ausgabeformate . . . . . . . . . . . . . . . . . . . . .             | 23   |
| 3.2                 | Kennbuchstaben fur Eingabeformate . . . . . . . . . . . . . . . . . . . . .             | 25   |
| 4.1                 | Wahrheitstafeln fur logische Operatoren . . . . . . . . . . . . . . . . . . .           | 37   |
| 4.2                 | Prioritaten der Operatoren . . . . . . . . . . . . . . . . . . . . . . . . . .          | 40   |
| 4.3                 | Hierarchie der impliziten Typumwandlung . . . . . . . . . . . . . . . . . .             | 43   |
| 5.1                 | Funktionen zur Klassifizierung von Zeichen . . . . . . . . . . . . . . . . .            | 52   |
| 9.1                 | Mathematische Funktionen mit einem Argument . . . . . . . . . . . . . .                 | 100  |
|                     | 16.1 Optionen zum Offnen von Dateien mit fopen . . . . . . . . . . . . . . . .          | 166  |

## Quelltextbeispiele

| 1.1   | Unser Erstes Beispiel . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    |   5 |
|-------|--------------------------------------------------------------------------------------|-----|
| 3.1   | einfache formatierte Eingabe/Ausgabe . . . . . . . . . . . . . . . . . . . .         |  21 |
| 3.2   | Wiederholt Zahlen einlesen und ausgeben mit einer Schleife                           |  26 |
| 3.3   | Zahlen kopieren mit Vorschuben . . . . . . . . . . . . . .                           |  27 |
| 3.4   | Eingabe bis zum Ende der Eingabe ( EOF ) verarbeiten . . . . . . . . . . . .         |  28 |
| 3.5   | Auswahl aus Alternativen mit if und else . . . . . . . .                             |  29 |
| 3.6   | Arbeit mit Vektoren: Berechnen eines Skalarproduktes . . . . . . . . . . .           |  31 |
| 4.1   | Inkrement-Operator . . . . . . . . . . . . . . . . . . . . .                         |  35 |
| 5.1   | Kopieren von 10 Zahlen (Eine Zahl pro Zeile) . . . . . . . . . . . . . . . .         |  49 |
| 6.1   | Berechnung von Kreisumfang oder Flache . . . . . . . . .                             |  57 |
| 6.2   | Berechnung von Kreisumfang oder Flache mit switch . .                                |  60 |
| 6.3   | Auswahl aus Alternativen (neu) . . . . . . . . . . . . . . . . . . . . . . . .       |  62 |
| 6.4   | Arbeit mit Vektoren: Skalarprodukt mit for -Schleife . . . . . . . . . . . .         |  63 |
| 6.5   | Auswahl aus Alternativen (mit break ) . . . . . . . . . . . . . . . . . . . .        |  65 |
| 6.6   | Ziffernubereinstimmungen . . . . . . . . . . . . . . . . . . . . . . . . . . .       |  67 |
| 7.1   | Invertieren eines Strings . . . . . . . . . . . . . . . . . . .                      |  73 |
| 7.2   | Turme von Hanoi rekursiv . . . . . . . . . . . . . . . . . . . . . . . . . . .       |  78 |
| 8.1   | Invertieren eines Strings mit Funktionen . . . . . . . . . . . . . . . . . . .       |  83 |
| 8.2   | Stapelverwaltung . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .     |  86 |
| 8.3   | Stapelverwaltung (modularisiert I): stapel.h . . . . . . .                           |  88 |
| 8.4   | Stapelverwaltung (modularisiert I): stapel.c . . . . . . .                           |  88 |
| 8.5   | Stapelverwaltung (modularisiert I): stapeltest.c . . . .                             |  89 |
| 8.6   | makefile fur Stapelverwaltung . . . . . . . . . . . . . . .                          |  91 |
| 8.7   | Stapelverwaltung (modularisiert II): stapel.c . . . . . .                            |  92 |
| 8.8   | Stapelverwaltung (modularisiert III): stapel.h . . . . . .                           |  93 |
| 8.9   | Stapelverwaltung (modularisiert III): stapel.c . . . . . .                           |  93 |
|       | 12.1 Verwendung von Zeigern auf Funktionen und typedef . .                           | 136 |
|       | 13.1 Auflisten der letzten Zahlen der Eingabe . . . . . . . . . . . . . . . . . . .  | 143 |
|       | 13.2 Matrizen mit beliebigen Dimensionen bereitstellen . . . .                       | 147 |
|       | 14.1 Arbeiten mit Strukturen . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 151 |
|       | 14.2 Arbeiten mit verschachtelten Strukturen und Zeigern auf Strukturen . . .        | 153 |
|       | 16.1 Dateiverarbeitung: Konkatenation . . . . . . . . . . . . .                      | 166 |

## Literaturverzeichnis

- [1] C Programming Language. Wikipedia-Eintrag: http://en.wikipedia.org/w/index. php?title=C\_programming\_language&oldid=40429557 .
- [2] GNU Compiler Collection (GCC). Internet-Website: http://gcc.gnu.org/ .
- [3] Joachim Goll, Ulrich Brockl, and Manfred Dausmann. C als erste Programmiersprache . Teubner, 2003.
- [4] Samuel P. Harbison and Guy L. Steele Jr. C. A Reference Manual . Prentice Hall, 2002.
- [5] Sammlung von Standardisierungsdokumenten. Internet-Website: http://www. open-std.org/JTC1/SC22/WG14/www/standards , Juni 2005.
- [6] ISO/IEC 9899:TC2. Internet-Dokument: http://www.open-std.org/jtc1/sc22/ wg14/www/docs/n1124.pdf , Mai 2005. ISO/IEC.
- [7] Brian W. Kernighan and Dennis M. Ritchie. The C Programming Language . Prentice Hall, 2nd edition, 1988.
- [8] Linksammlung zur C-Programmierung. Internet-Website: http://www.lysator.liu. se/c/ , 2001.
- [9] Martin Lowes and Augustin Paulik. Programmieren mit C. ANSI Standard . Teubner, 1999.

## Stichwortverzeichnis

| Symbole                                                                         |                                                                               | call by value . . . . . . . . . . . . . . . . . . . . . . . 72, 123                                                          |                                                                                |
|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| #define                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . 16, 106                 | case                                                                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58     |
| #elif                                                                           | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 107         | cast . . . . . . . . . . . . . . . .                                                                                         | siehe Typumwandlung                                                            |
|                                                                                 |                                                                               | Castoperatoren . . . . . . . . . . . . . . . . . . . . . . . . . 44                                                          |                                                                                |
| #else                                                                           | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 107         | char                                                                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12     |
| #if . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 107 |                                                                               | character . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12                                                   |                                                                                |
| #ifdef                                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 109           | Compiler. . . . . . . . . . . . . . . . . . . . . . . . . . . . 2, 183                                                       |                                                                                |
| #ifndef                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 109             |                                                                                                                              | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 75, 122            |
| #include                                                                        | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 106               | const                                                                                                                        |                                                                                |
| #undef                                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 109           | continue                                                                                                                     | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66               |
| A                                                                               |                                                                               | D                                                                                                                            |                                                                                |
| abort                                                                           | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102         | Datei . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 178                                                |                                                                                |
| Adressoperator . . . . . . . . . . . . . . . . . . . . . . . . 119              |                                                                               | Dateivariablen . . . . . . . . . . . . . . . . . . . . . . . . . 165                                                         |                                                                                |
| Aktualargumente . . . . . . . . . . . . . . . . . . . . . . . 72                |                                                                               | Dateiverarbeitung . . . . . . . . . . . . . . . . . . . . . 165                                                              |                                                                                |
| ANSI-Standard........... . . . . . . . . . . . . . . . 1                        |                                                                               | default                                                                                                                      | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58             |
| Argumente .. . . . . . . . . . . . . . . . . . . . . . . . . . . . 72           |                                                                               | Dekrementierung . . . . . . . . . . . . . . . . . . . . . . . 35                                                             |                                                                                |
| arithmetische Operatoren . . . . . . . . . . . . . . . 34                       |                                                                               | Dereferenzierung. . . . . . . . . . . . . . . . . . . . . . . 119                                                            |                                                                                |
| array. . . . . . . . . . . . . . . . . . . . . . . . . . siehe                  | Felder                                                                        | Dereferenzierungsoperator . . . . . . . . . . . . . 119                                                                      |                                                                                |
| ASCII-Code............. . . . . . . . . . . . . . . . 12                        |                                                                               | Dezimalzahlen . . . . . . . . . . . . . . . . . . . . . . . . . . . 9                                                        |                                                                                |
| Aufzahlungskonstanten . . . . . . . . . . . . . . . . . 15                      |                                                                               | Direktiven . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105                                                     |                                                                                |
| Ausdrucksanweisungen... . . . . . . . . . . . . . . . 55                        |                                                                               | Division . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34                                                  |                                                                                |
| Ausdrucke . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33        |                                                                               | Divisionsrest . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34                                                     |                                                                                |
| ausfuhrbares Programm. . . . . . . . . . . . . . . . . . 3                      |                                                                               | do                                                                                                                           | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60 |
| Ausloschung . . . . . . . . . . . . . . . . . . . . . . . . . . . 163           |                                                                               | double                                                                                                                       |                                                                                |
| auto                                                                            | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 95    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14 dynamischer Speicher . . . . . . . . . . . . . 116, 141 |                                                                                |
| B                                                                               |                                                                               | E                                                                                                                            |                                                                                |
| bedingte Compilation. . . . . . . . . . . . . . . . . . 105                     |                                                                               |                                                                                                                              |                                                                                |
| bedingter Ausdruck . . . . . . . . . . . . . . . . . . . . . 38                 |                                                                               | echo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27                                              |                                                                                |
| benannte Konstanten . . . . . . . . . . . . . . . . . . . 15                    |                                                                               | Editor . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 183                                                 |                                                                                |
| Bezeichner . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17       |                                                                               | EDOM                                                                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 101      |
| Bibliotheksdateien . . . . . . . . . . . . . . . . . . . . . 101                |                                                                               | else                                                                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56     |
| Binarzahlen. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9        |                                                                               | End Of File. . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28                                                      |                                                                                |
| Block . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55  |                                                                               | enum . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15                                              |                                                                                |
| boolean. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36     |                                                                               | ERANGE                                                                                                                       | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 101            |
| break                                                                           | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59, 65          | errno                                                                                                                        | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 101          |
|                                                                                 | Byte.. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10 | Escapesequenzen. . . . . . . . . . . . . . . . . . . . . . . . 13                                                            |                                                                                |
|                                                                                 |                                                                               | exit                                                                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102      |
| C                                                                               | call by reference. . . . . . . . . . . . . . . . . . . . 73, 123              | extern . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 85 extern                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 93           |

## F

| Felder. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30, 111                                                            |
|--------------------------------------------------------------------------------------------------------------------------------------|
| Elemente . . . . . . . . . . . . . . . . . . . . . . . . . . 111                                                                     |
| Initialisierung . . . . . . . . . . . . . . . . . . . . . 116                                                                        |
| Komponenten ....... . . . . . . . . . . . . . . 111                                                                                  |
| float . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14                                                       |
| for . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 62                                                     |
| Formatbeschreiber . . . . . . . . . . . . . . . . . . . . . . 22                                                                     |
| Ausgabe..... . . . . . . . . . . . . . . . . . . . . . . 168                                                                         |
| Eingabe . . . . . . . . . . . . . . . . . . . . . . . . . . . 171                                                                    |
| formatierte Ein-/Ausgabe . . . . . . . . . . . . . . 21                                                                              |
| free . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 142                                                       |
| Funktionen . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69                                                              |
| Argument .. . . . . . . . . . . . . . . . . . . . . . . . . 71                                                                       |
| Aufruf. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71                                                                 |
| Definition. . . . . . . . . . . . . . . . . . . . . . . . . . .69                                                                    |
| Deklaration. . . . . . . . . . . . . . . . . . . . . . . . . 69                                                                      |
| Prototyp . . . . . . . . . . . . . . . . . . . . . . . . . . . 69 Funktionsheader . . . . . . . . . . . . . . . . . . . . . . . . 70 |
| Funktionswert . . . . . . . . . . . . . . . . . . . . . . . . . . 71                                                                 |
| Funktionszeiger . . . . . . . . . . . . . . . . . . . . . . . . 136                                                                  |

## G

gepufferte Eingabe . . . . . . . . . . . . . . . . . . . . . . 27

geschweifte Klammern . . . . . . . . . . . . . . . . . . 55

getenv

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102

Gleitkommazahlen . . . . . . . . . . . . . . . . . . . . . . 14

global. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92

goto

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64

graphische Zeichen . . . . . . . . . . . . . . . . . . . . . . . 3

## H

Hauptmodul ... . . . . . . . . . . . . . . . . . . . . . . . . . 89

Hauptprogramm ........ . . . . . . . . . . . . . . . . . 4

Headerdatei. . . . . . . . . . . . . . . . . . . . . . . . . . . . . 88

Heap . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141

Hexadezimalzahlen. . . . . . . . . . . . . . . . . . . . . . . 9

## I

if

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55

Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30, 111

Indexuberschreitung . . . . . . . . . . . . . . . . . . . 113

Initialisierung . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

Felder . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116

Strukturen . . . . . . . . . . . . . . . . . . . . . . . . 151

Inkrementierung . . . . . . . . . . . . . . . . . . . . . . . . 35

int

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

integer. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

intern. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 85

Iteration . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76

## K

Kommaoperator ...... . . . . . . . . . . . . . . . . . . 39

Kommentar............... . . . . . . . . . . . . . . . 5

Konkatenation. . . . . . . . . . . . . . . . . . . . . . . . . 133

## L

last in first out (lifo) . . . . . . . . . . . . . . . . . . . . 85

lazy evaluation. . . . . . . . . . . . . . . . . . . . . . . . . . 37

leere Anweisung . . . . . . . . . . . . . . . . . . . . . . . . 55

Linker . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3, 183

logische Operatoren. . . . . . . . . . . . . . . . . . . . . 37

lokal . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92

long

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10

long double

. . . . . . . . . . . . . . . . . . . . . . . . . . . 14

loop . . . . . . . . . . . . . . . . . . . . . . . .

siehe

Schleifen

## M

main

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4

Makros . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 106

Expandierung . . . . . . . . . . . . . . . . . . . . . 106

malloc

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 142

Matrizen. . . . . . . . . . . . . . . . . . . . . . . . . . . 30, 111

Mindestschranken. . . . . . . . . . . . . . . . . . . . . . . 10

Minus . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

Module . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 88

Modulo-Operator . . . . . . . . . . . . . . . . . . . . . . . 34

Multiplikation . . . . . . . . . . . . . . . . . . . . . . . . . . 34

## N

Namen ...... . . . . . . . . . . . . . . . . . . . . . . . . . . . 17

Nebeneffekt..... . . . . . . . . . . . . . . . . . . . . . . . . 41

normalisierte Darstellung . . . . . . . . . . . . . . 160

Null-Zeichen. . . . . . . . . . . . . . . . . . . . . . . . . . . . 47

Nullzeiger . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127

## O

Objekt-Programm ....... . . . . . . . . . . . . . . . . 3

Objektdatei . . . . . . . . . . . . . . . . . . . . . . . . . . . 183

Oktalzahlen. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 9

Operanden...... . . . . . . . . . . . . . . . . . . . . . . . .33

Operatoren . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33

*

. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34

*

(Dereferenzierungsoperator) . . . . . 119

+

(Inkrementierung) . . . . . . . . . . . . . . . . 35

,

(Kommaoperator) ... . . . . . . . . . . . . . 39

| -                                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34   |
|----------------------------------------------------------------------------|----------------------------------------------------------------------------|
| -- (Dekrementierung) . . . . . . . . . . . . . . 35                        |                                                                            |
| ->                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 153      |
| .. (Punktoperator). . . . . . . . . . . . . . . . 151                      |                                                                            |
| /                                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34   |
| <                                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36   |
| <=                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36     |
| =                                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33   |
| ==                                                                         |                                                                            |
| > . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36 | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36     |
| >=                                                                         | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36     |
| ? : (bedingter Ausdruck). . . . . . . . . . .38                            |                                                                            |
| % (Modulo-Operator) . . . . . . . . . . . . . . . 34                       |                                                                            |
| & (Adressoperator) . . . . . . . . . . . . . . . . 119                     |                                                                            |
| && (logisches UND) . . . . . . . . . . . . . . . . . 37                    |                                                                            |
| Ordnungszahlen . . . . . . . . . . . . . . . . . . . . . . . . 12          |                                                                            |

overflow . . . . . . . . . . . . . . . . . . . .

siehe

Uberlauf

## P

| Parameter . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 72        |
|---------------------------------------------------------------------------------|
| Pfad. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 178   |
| Plus . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34 |
| pointer . . . . . . . . . . . . . . . . . . . . . . . . siehe Zeiger            |
| portabel . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2    |
| Praprozessor . . . . . . . . . . . . . . . . . . . . . . . . 5, 105             |
| Praprozessor-Direktiven . . . . . . . . . . . . . . . . . 6                     |
| printf . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22     |
| Prioritaten. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39       |
| Punktoperator. . . . . . . . . . . . . . . . . . . . . . . . . 151              |

## R

| rand . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103   |
|----------------------------------------------------------------------------------|
| register . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 96        |
| Rekursion. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4       |
| direkte . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76             |
| indirekte. . . . . . . . . . . . . . . . . . . . . . . . . . . . 76              |
| return . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 71      |
| runde Klammer.......... . . . . . . . . . . . . . . . 33                         |
| Rundungsfehler. . . . . . . . . . . . . . . . . . . . . . . . 162                |

## S

| scanf                                                                | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24   |
|----------------------------------------------------------------------|----------------------------------------------------------------------------|
| Schlusselworter . . . . . . . . . . . . . . . . . . . . . . . . . 18 |                                                                            |
| short                                                                | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10   |
| signed                                                               | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11       |
| sizeof                                                               | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45       |
| Speicher                                                             |                                                                            |
| dynamisch.... . . . . . . . . . . . . . . . . . . . . . 141          |                                                                            |
| statisch. . . . . . . . . . . . . . . . . . . . . . . . . . . . 141  |                                                                            |

| Speicherabbildungsfunktion . . . . . . . 113, 143                             |
|-------------------------------------------------------------------------------|
| Speicherblocke . . . . . . . . . . . . . . . . . . . . . . . . . 139          |
| Sprunge . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64    |
| break . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 65          |
| continue . . . . . . . . . . . . . . . . . . . . . . . . . . . 66             |
| srand . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103   |
| sscanf . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 143    |
| Stack . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141 |
| Standard-Headerdateien . . . . . . . . . . . . . . . . 99                     |
| Standardausgabegerat. . . . . . . . . . . . . . 21, 183                       |
| Standardbibliothek . . . . . . . . . . . . . . 1, 99, 185                     |
| Standardeingabegerat . . . . . . . . . . . . . . 21, 183                      |
| Standardtypen.. . . . . . . . . . . . . . . . . . . . . . . . . 10            |
| static . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 92, 95     |
| statischer Speicher . . . . . . . . . . . . . . . . . . . . . 141             |
| String . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14 |
| struct . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 149    |
| Strukturen. . . . . . . . . . . . . . . . . . . . . . . . . . . . . 149       |
| Initialisierung . . . . . . . . . . . . . . . . . . . . . 151                 |
| switch . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58   |
| Syntaxeinfarbung . . . . . . . . . . . . . . . . . . . . . . . . 2            |
| system . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 102    |

## T

| typedef . . . . . . . . . . . . . . . . . . . . . . . . . . . 19, 136   |
|-------------------------------------------------------------------------|
| Typumwandlung................... . . . . . 42                           |
| implizit. . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42    |

## U

| ¨                                                                     | Uberlauf. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 159 siehe Unterlauf   |
|-----------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| underflow....... . . . . . . . . . . . union                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 157                       |
| UNIX ...... . . . . . . . . . . . . . . . . . . . . . . . . . . . 177 |                                                                                             |
| home directory . . . . . . . . . . . . . . . . . . . . 180            |                                                                                             |
| Jokerzeichen. . . . . . . . . . . . . . . . . . . . . . . 182         |                                                                                             |
|                                                                       | login . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177                       |
| Metazeichen . . . . . . . . . . . . . . . . . . . . . . . 182         |                                                                                             |
|                                                                       | root . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 177                      |
| wild cards . . . . . . . . . . . . . . . . . . . . . . . . . 182      |                                                                                             |
| working directory. . . . . . . . . . . . . . . . . . 179              |                                                                                             |
| UNIX-Befehle                                                          |                                                                                             |
| cd chmod (change mode).. . . . . . . . . . . . . 181                  | (change directory) . . . . . . . . . . . . . . 180                                          |
| cp (copy). . . . . . . . . . . . . . . . . . . . . . . . . . 181      |                                                                                             |
| lpq (lineprinter queue) . . . . . . . . . . . . 182                   |                                                                                             |
| lprm (lineprinter remove) . . . . . . . . . . 183                     |                                                                                             |
| lpr (lineprinter) . . . . . . . . . . . . . . . . . . . 182 ls        |                                                                                             |
|                                                                       | (list) . . . . . . . . . . . . . . . . . . . . . . . . . . . 180                            |
| man (manual). . . . . . . . . . . . . . . . . . . . . . 178           |                                                                                             |

| mkdir (make directory) . . . . . . . . . . . . 181                        |                                                                  |
|---------------------------------------------------------------------------|------------------------------------------------------------------|
| mv (move) . . . . . . . . . . . . . . . . . . . . . . . . . 181           |                                                                  |
| pwd (print working directory) . . . . . . 179                             |                                                                  |
| rmdir (remove directory) . . . . . . . . . . 181                          |                                                                  |
| rm (remove) . . . . . . . . . . . . . . . . . . . . . . . 181             |                                                                  |
| unsigned                                                                  | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11 |
| Unterlauf . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 159 |                                                                  |

## V

| Variablen . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16                                                           |
|--------------------------------------------------------------------------------------------------------------------------------------|
| automatisch . . . . . . . . . . . . . . . . . . . . . . . . 94 statisch . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 94 |
| Vektoren. . . . . . . . . . . . . . . . . . . . . . . . . . . 30, 111                                                                |
| Verbunde..... . . . . . . . . . . . . . . . . . . . . . . . . . 157                                                                  |
| Vergleichsoperatoren . . . . . . . . . . . . . . . . . . . . 36                                                                      |
| verkettete Listen. . . . . . . . . . . . . . . . . . . . . . . 156                                                                   |
| Verschattung . . . . . . . . . . . . . . . . . . . . . . . . . . . 85                                                                |
| Verzeichnisse . . . . . . . . . . . . . . . . . . . . . . . . . . 178                                                                |
| Verzweigungen. . . . . . . . . . . . . . . . . . . . . . . . . . 64                                                                  |
| void . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69                                                      |
| volatile . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 97                                                            |

## W

| Wahrheitstafeln. . . . . . . . . . . . . . . . . . . . . . . . . 37            |
|--------------------------------------------------------------------------------|
| Wertzuweisung... . . . . . . . . . . . . . . . . . . . . . . .33               |
| while . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60 |
| white spaces . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3       |
| Wortstruktur . . . . . . . . . . . . . . . . . . . . . . . . . . . 10          |

## Z

| Zeichenkettenkonstante . . . . . . . . . . . . . . . . . 14                  |
|------------------------------------------------------------------------------|
| Zeiger . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 120 |
| Zeiger auf Zeiger. . . . . . . . . . . . . . . . . . . . . . . 132           |
| Zeigerarithmetik . . . . . . . . . . . . . . . . . . . . . . . 124           |
| Zeigerausdruck . . . . . . . . . . . . . . . . . . . . . . . . 120           |
| Zeigerparameter . . . . . . . . . . . . . . . . . . . . . . . 120            |
| Zeigervariablen . . . . . . . . . . . . . . . . . . . . . . . . 121          |
| Zufallszahlen-Generator. . . . . . . . . . . . . . . . 103                   |
| Zuweisungsoperator. . . . . . . . . . . . . . . . . . . . . 33               |
| zusammengesetzter . . . . . . . . . . . . . . . . . 38                       |