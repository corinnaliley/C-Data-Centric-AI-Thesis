## Kapitel 11

## Felder

## 11.1 Ruckblick

Wir haben uns verschiedentlich bereits mit Feldern beschaftigt. Was wir dabei gelernt haben, ist im Folgenden noch einmal kurz zusammengefasst:

- · Felder konnen durch

```
typ name [ anzahl ];
```

vereinbart werden. Der Wert anzahl muss ein konstanter Ausdruck mit ganzzahligem, positivem Wert sein.

- · Die Komponenten ( Elemente ) eines Feldes sind Variablen mit dem Typ des Feldes. Sie konnen mit

name [ index ]

angesprochen werden. Da die Numerierung bei 0 beginnt, ist der großte zulassige Index um 1 kleiner als die Anzahl der Komponenten. Die Indizes selbst konnen beliebige Ausdrucke mit einem ganzzahligen Typ sein.

- · Der Programmierer ist selbst dafur verantwortlich, dass er nur zulassige Indizes verwendet.
- · Vektoren mit dem Typ char werden als Strings bezeichnet, wenn sie in einer Komponente ein Null-Zeichen enthalten.
- · Feldnamen bezeichnen selbst keine Variablen, sondern sind Zeigerkonstanten. Das hat Auswirkungen auf die Ubergabe von Feldern an Funktionen.

## 11.2 Vereinbarung von Feldern

Ahnlich wie eindimensionale Felder ( Vektoren ) konnen auch Felder mit mehreren Dimensionen vereinbart werden: Dem Namen folgen dann, jeweils in eckigen Klammern eingeschlossen, die Langenangaben fur die verschiedenen Dimensionen. So ergibt

int m[2][3];

ein zweidimensionales Feld ( Matrix ). In gleicher Weise hat man mehrere Indizes anzugeben, wenn man auf ein einzelnes Element zugreifen will; im Beispiel hat man etwa die 6 Elemente

m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2].

Sowohl die Vereinbarung eines mehrdimensionalen Feldes als auch die Zugriffe auf seine Komponenten kann man auch in anderer Weise interpretieren: Eine Matrix zum Beispiel kann man auch als Vektor betrachten, dessen Komponenten ihrerseits Vektoren sind. Bei einem dreidimensionalen Feld hat man sogar drei Moglichkeiten der Interpretation (Vektor von Matrizen, Matrix von Vektoren, Vektor von Vektoren von Vektoren). Entsprechende Zugriffe sind erlaubt: m[0] und m[1] bezeichnen so die beiden Vektoren der Lange 3, aus denen m besteht. m[1][0] bezeichnet in diesem Sinne die erste Komponente im zweiten Vektor von m .

## 11.3 Anordnung von Feldern im Speicher

Fur den C-Programmierer ist es in manchen Situationen unumganglich zu wissen, wie Felder im Speicher angeordnet sind. Grundsatzlich wird fur jedes Feld ein zusammenhangender Speicherbereich verwendet.

Bei Vektoren sind die Komponenten mit aufsteigenden Indizes hintereinander angeordnet: Den Index einer Komponente kann man als ihren Abstand vom ersten Element des Vektors interpretieren. Fur den Vektor

int v[6];

ist die Anordnung der Komponenten in Abbildung 11.1 angegeben.

Abbildung 11.1: Speicheranordnung eines Vektors mit 6 Komponenten

picture-1.png

Das ist ubrigens auch der Grund, warum bei C Felder ab 0 indiziert werden. Bei der Realisierung speziell mathematischer Formeln kann das verwirren, weil in ihnen die Indizierung in der Regel nicht bei Null beginnt.

Die Beschreibung einer Matrix als Vektor von Vektoren sollte schon nahelegen, wie Matrizen angeordnet werden: Am Anfang steht der erste Zeilenvektor, dann der zweite Zeilenvektor, usw. Die Elemente der einzelnen Zeilenvektoren folgen jeweils unmittelbar hintereinander. Fur die Matrix

int m[2][3];

ist dies in Abbildung 11.2 wiedergegeben.

Abbildung 11.2: Speicheranordnung einer (2 × 3)-Matrix

picture-2.png

Fur den Zugriff auf eine Komponente einer Matrix muss der Abstand vom ersten Element jetzt wirklich ' ausgerechnet' werden. Haben wir etwa den Zugriff m[i][j] , so ist der Abstand gerade i · 3+ j , oder allgemeiner: Zeilenindex mal Zeilenlange plus Spaltenindex. Und genau diesen Ausdruck setzt der Compiler bei jedem Zugriff auf eine Matrixkomponente ein. Die Zuordnung ( i, j ) ↦-→ i · 3 + j ist in dieser Situation die Speicherabbildungsfunktion . Ihre Gestalt hangt offenbar von der Dimensionierung der Matrix ab. Ahnliche Formeln kann man sich ubrigens auch fur Felder mit hoherer Dimension uberlegen. Dass jede Feldkomponente moglicherweise mehrere Bytes belegt und deshalb der Abstand noch einmal mit dieser Anzahl multipliziert werden muss, braucht uns nicht zu interessieren.

Damit ist jetzt auch schon angedeutet, was passiert, wenn man mit unzulassigen Indizes auf ein Feld zugreift: Der Abstand wird ausgerechnet und zum Zugriff verwendet. So bewirkt v[-1] gerade den Zugriff auf den Speicherbereich direkt vor dem Beginn des Vektors. Versuchte Zugriffe auf Feldkomponenten jenseits der Feldgrenzen nennt man Indexuberschreitung .

Ob und ggf. was fur Folgen eine Indexuberschreitung hat, hangt von der Situation ab. Manche bleiben, von eventuell verfalschten Resultaten abgesehen, ohne Wirkung. So bewirkt zum Beispiel

m[0][3] = m[1][0];

auf jeden Fall nichts ! Das Indexpaar [0][3] ist zwar nicht zulassig - da es aber denselben Abstand vom Anfang der Matrix liefert wie das Indexpaar [1][0] , namlich 3, wird nur ein int -Wert mit sich selbst uberschrieben.

Nicht jeder Verstoß endet so ohne Folgen. Da ist es fast schon angenehmer, wenn die Abstande so falsch sind, dass das Programm wegen Zugriffs auf einen ' verbotenen' Speicherbereich ' gekillt' wird, als wenn es mit verfalschten Daten weiterrechnet. An der Stelle, auf die zum Beispiel durch v[-1] zugegriffen wird, steht ja in der Regel eine andere Variable des Programms, die durch

v[-1] = 0;

verfalscht wurde.

Wird ein Programm mit einer Meldung wie ' segmentation fault', ' bus error' bzw. ' memory fault' abgebrochen, sollte man das Programm zunachst auf Indexuberschreitungen hin untersuchen.

## 11.4 Felder als Parameter

Erinnerung: Die Lange eines Strings , der durch ein char -Feld realisiert ist, ist etwas anderes als die Lange dieses Feldes . Die Lange des Strings ist die Anzahl der Bytes vor dem Nullbyte im Feld. Die Lange des char -Feldes in dem die Zeichen des Strings gespeichert sind ist die Anzahl der Bytes, die das komplette Feld belegt.

Was eine Funktion dagegen nicht bestimmen kann, ist die Lange eines ubergebenen Feldes. Wenn eine Funktion die Lange eines als Argument ubergebenen Feldes benotigt, so muss ihr diese mit Hilfe eines seperaten Parameters mitgeteilt werden. Selbst berechnen kann sie die Lange namlich nicht, denn im Speicher folgt einfach Byte auf Byte - eine besondere Grenze, an der die Funktion erkennen konnte, dass das ubergebene Feld ' zu Ende' ist, gibt es nicht.

Wegen des Unterschieds zwischen Lange eines Strings und Lange des Feldes durch den ein String realisiert ist, bilden Strings nur scheinbar eine Ausnahme. Als Beispiel betrachten wir eine Funktion, die die Summe der Komponenten eines Vektors berechnet:

```
float vektorsumme(const float v[], int laenge) { float s = 0; while (--laenge >= 0) s += v[laenge]; return s; }
```

Der Vorteil dieses Vorgehens ist, dass die Funktion fur Vektoren beliebiger Lange eingesetzt werden kann: Der Funktion wird mitgeteilt, wo der Vektor beginnt ( v[] ). Sie unterstellt, dass weitere laenge - 1 Komponenten folgen. Dass das so ist, ist wieder ausschließlich in die Verantwortung des Programmierers gestellt. Zulassig ware zum Beispiel

```
float v1[7], v2[50], m[5][20], summe; ... summe = vektorsumme(v1, 7) + vektorsumme(v2, 50); summe = vektorsumme(m[3], 20);
```

Nicht zulassig ware dagegen, bei gleichen Definitionen, wie bereits angesprochen

```
summe = vektorsumme(v1, 10);
```

da die Funktion auf Speicher zugreifen wurde, der nicht zu v1 gehort. Andererseits durfen wir ohne weiteres

```
summe = vektorsumme(v2, 10); summe = vektorsumme(&v2[10], 10);
```

schreiben - es steht uns ja frei, einen Teil der Komponenten von v2 zu ignorieren, hier im ersten Fall die letzten 40 und im zweiten Fall die ersten 10 und die letzten 30. Und schließlich ist auch

```
summe = vektorsumme(m[0], 100);
```

zulassig. Das mag auf den ersten Blick verwunderlich erscheinen - spatestens auf den zweiten Blick wird es klar: Die Matrix m besteht aus insgesamt 100 Komponenten, die im Speicher unmittelbar aufeinanderfolgen. Was sollte uns also daran hindern, diesen Speicherbereich bei Bedarf auch als Vektor zu betrachten? Nur m als Parameter anzugeben reicht jedoch nicht aus. Ohne Zusatz bezeichnet m einen Vektor von Zeilenvektoren, nicht einen Vektor von float -Werten. m[0] bezeichnet den ersten Zeilenvektor, die weiteren Zeilenvektoren folgen jedoch unmittelbar im Speicher.

Schwieriger wird es, wenn ein mehrdimensionales Feld auch in der Funktion als solches betrachtet werden muss - und wenn obendrein die Große des Feldes in den einzelnen Dimensionen von Aufruf zu Aufruf verschieden konnen sein soll. In Deklaration und Definition einer Funktion durfen wir Felder zwar auch ' echt' dimensionieren, d.h. in die Klammern etwas eintragen - nur mussen das Konstanten oder konstante Ausdrucke sein, deren Wert dann naturlich von Aufruf zu Aufruf nicht verandert werden kann. Andererseits durfen wir in einer Funktionsvereinbarung nur fur die erste Dimension die Langenangabe weglassen. Der Prototyp

```
float f(float m[][3], int zeilen);
```

ist also zwar zulassig, erlaubt den Einsatz der Funktion f aber nur fur Matrizen mit 3 Spalten - und ist deshalb fur die Praxis unzureichend. Der Prototyp

float f(float m[][], int zeilen , int spalten);

ist nicht erlaubt. Der Grund sollte klar sein: Ohne die Langenangabe der Zeilen hat der Compiler keine Moglichkeit, die Speicherabbildungsfunktion zu berechnen.

Die Abhilfe: Man ubergibt die Matrix formal als Vektor und gibt diesem Vektor in der Funktion wieder Matrixstruktur, indem man die Speicherabbildungsfunktion selbst berechnet. Das ist zwar nicht schon, in C aber nicht zu vermeiden.

Ein Beispiel ist das Matrizenprodukt C = A · B fur Matrizen A = ( a ij ), B = ( b jk ) und C = ( c ik ) mit i = 1 , . . . , glyph[lscript] , j = 1 , . . . , m und k = 1 , . . . , n :

c ik = m ∑ j =1 ( a ij · b jk )

Der Prototyp einer entsprechenden Funktion kann

void matprod(float c[], const float a[], const float b[], int l, int m, int n);

sein. Bevor wir die Funktion definieren, deklarieren wir zunachst einen Makro, der zu einem Indexpaar den Abstand vom Anfang des Vektors berechnet. Dieser Makro benotigt zusatzlich zu den beiden Indizes offensichtlich auch die Lange der Zeilen der Matrix als Parameter. In diesen Makro konnen wir dann auch gleich noch die Transformation der logischen Indizes 1 , . . . , x in die C-Indizes 0 , . . . , x -1 hineinstecken:

#define lin(zeile, spalte , laenge) \ (((zeile)-1)*(laenge)+(spalte)-1)

Jetzt konnen wir die Funktion definieren - in einer Schreibweise, die der Formel zumindest einigermaßen nahekommt:

void matprod (float c[], const float a[], const float b[],

```
int l, int m, int n) { int i, j, k; for (i = 1; i <= l; i++) for (k = 1; k <= n; k++) { c[lin(i,k,n)] = 0; for (j = 1; j <= m; j++) c[lin(i,k,n)] += a[lin(i,j,m)] * b[lin(j,k,n)]; } }
```

Diese Formulierung entspricht in etwa der Schreibweise der Formel, dafur aber nicht so sehr der Schreibweise von C. Dieses Beispiel wird deshalb im nachsten Abschnitt noch einmal aufgegriffen.

Ein Aufruf der Funktion konnte so aussehen:

```
#define DIM\_L ... #define DIM\_M ... #define DIM\_N ... /* ... */ float A[DIM\_L][DIM\_M], B[DIM\_M][DIM\_N], C[DIM\_L][DIM\_N]; /* ... Initialisierung der Matrizen ... */ matprod (C[0], A[0], B[0], DIM\_L, DIM\_M, DIM\_N);
```

Im ubrigen lasst sich auch diese Routine noch nicht wirklich universell fur die Multiplikation von zwei float -Matrizen einsetzen: Ein Programm, das Matrizen verarbeitet, soll in der Regel bei jedem Aufruf Matrizen unterschiedlicher Große verarbeiten konnen. Um das zu realisieren, gibt es in C zwei Moglichkeiten:

- · Man arbeitet mit dynamischem Speicher . Das bedeutet, man bestimmt zunachst die Große der zu bearbeitenden Matrizen und beschafft sich dann vom Betriebssystem den entsprechenden Speicher. Methoden dazu werden im Kapitel 13 vorgestellt. Der Einsatz unserer Funktion matprod ware dann moglich.
- · Man arbeitet mit ' Maximalgroßen' fur die Matrizen, d.h. man uberlegt sich eine obere Schranke fur die Große der vorkommenden Matrizen und definiert alle Matrizen mit dieser Große. Das wird in mathematischen Programmen oft gemacht, hat aber auch seine Nachteile:
- -Sollte der Benutzer des Programms großere Matrizen verarbeiten wollen, muss die Verarbeitung abgelehnt werden.
- -Funktionen wie matprod benotigen zusatzliche Parameter: Fur die Schleifen wird die ' logische' (genutzte) Große der Matrizen benotigt; fur die Berechnung der Speicherabbildungsfunktion wird dagegen die ' physikalische' (vereinbarte) Große der Matrizen benotigt.

Leider fehlt die Zeit, auf Einzelheiten einzugehen. Vielleicht formulieren Sie selbst die Funktion matprod einmal so um, dass sie auch dann korrekt arbeitet, wenn die Matrizen nur einen Teil des fur sie bereitgestellten Speichers belegen.

## 11.5 Initialisierung von Feldern

Felder konnen initialisiert werden. Fur Strings haben wir diese Moglichkeit auch bereits genutzt. Allgemein sieht die Anfangswertzuweisung fur Felder aber anders aus: Die Werte der Komponenten werden einzeln aufgefuhrt, voneinander jeweils durch ein Komma getrennt und insgesamt in geschweifte Klammern eingeschlossen:

int v[6] = {6, 5, 4, 17, 18, 19};

Gibt man zu wenig Werte an, so werden die ubrigen auf Null gesetzt; gibt man zu viele Werte an, wird der Compiler einen Fehler anzeigen. Wenn man fur jede Komponente einen Wert angibt, kann man den Compiler auch abzahlen lassen und die Feldlange ganz weglassen: Die Definition

int v[] = {6, 5, 4, 17, 18, 19};

ist also zulassig und ergibt einen Vektor mit 6 Komponenten.

Bei der Initialisierung mehrdimensionaler Felder muss man sich wieder klar machen, dass sie formal Vektoren von Vektoren sind. Entsprechend kann man dann zum Beispiel

int m[2][3] = {{ 6, 5, 4}, {17, 18, 19}};

schreiben.

Wenn man Anfangswerte angibt, darf man bei mehrdimensionalen Feldern die Lange in der ersten Dimension weglassen; der Compiler bestimmt sie dann durch Abzahlen. Das ist nicht nur fur Schreibfaule interessant, sondern erspart einem einerseits das Abzahlen der Daten und verhindert andererseits ein Verzahlen dabei.

Auch mehrdimensionale Felder lassen sich teilweise initialisieren. Alle nicht angegebenen Komponenten erhalten dann den Wert 0 . Dabei wird die durch geschweiften Klammern angegebene Struktur eingehalten.

```
float v[12] = { 0 }; /* alle Komponenten = 0 */ int m[4][2][3] = {{{ 1, 2, 3 }, { 4, 5, 6 }}, {{ 7, 8 }}, {{ 9 }, { 10 }}}; /* entspricht = {{{ 1, 2, 3 }, { 4, 5, 6 }}, {{ 7, 8, 0 }, { 0, 0, 0 }}, {{ 9, 0, 0 }, { 10, 0, 0 }}, {{ 0, 0, 0 }, { 0, 0, 0 }}} */
```

Im Beispiel hatte man wiederum die erste Dimension des Feldes m weglassen konnen. Der Compiler hatte fur sie dann 3 bestimmt, da fur drei Zeilen Anfangswerte angegeben wurden.

Fur Strings haben wir bereits eine Kurzform der Initialisierung kennengelernt: Wenn eine Stringkonstante angegeben ist, zerlegt der Compiler diese in einzelne Zeichen und sorgt selber fur das abschließende Null-Zeichen. Die beiden Definitionen

```
char str1[6] = "hallo", str2[6] = {'h', 'a', 'l', 'l', 'o', '\0'};
```

sind also aquivalent. Und da wir auch hier wieder den Compiler abzahlen lassen konnen, sind die beiden Definitionen

```
char str3[] = "hallo", str4[] = {'h', 'a', 'l', 'l', 'o', '\0'};
```

ebenfalls aquivalent.

Alle Konstanten, die in den Initialisierungen angegeben wurden, durften ubrigens auch konstante Ausdrucke sein, bei automatischen Feldern sogar beliebige Ausdrucke.

Ein Manko ist sicher, dass man alle Anfangswerte explizit angeben muss. Eine Abkurzung wie ' trage 10mal den Wert 7 ein' gibt es nicht! Auch kann man nicht nur fur einzelne Feldkomponenten Anfangswerte angeben.