## Kapitel 4

## Ausdr ucke und Operatoren

## 4.1 Aufbau von Ausdrucken

Ausdrucke setzen sich aus Operanden , Operatoren und runden Klammern zusammen, wobei die Operanden in der Regel Konstanten, Variablen (einschließlich Feldkomponenten) und Funktionsaufrufe sein konnen. Die einfachsten Ausdrucke bestehen nur aus einem Operanden.

An verschiedenen Stellen sind wir bereits Ausdrucken begegnet, ohne dass ihnen besondere Aufmerksamkeit geschenkt wurde:

i als Argument von printf i - 1 bei der Schleifenzahlung v1[i] * v2[i] beim Skalarprodukt i < LAENGE beim Skalarprodukt

Einige weitere Ausdrucke als Beispiele:

(a + b) * 7 (a + b) * (c + d) - a

Wie schon erwahnt, sind die Variablen, die wir in den Beispielen als Argumente fur printf verwendet haben, formal als spezielle Ausdrucke anzusehen. Entsprechend konnen wir naturlich auch beliebige Ausdrucke als Argumente fur printf verwenden. Warum das bei scanf nicht moglich ist, werden wir uns noch ansehen.

## 4.2 Die Wertzuweisung

Eine Besonderheit von C gegenuber anderen Sprachen ist, dass auch der Zuweisungsoperator ( = ) als Operator betrachtet wird:

i = i - 1

ist also formal ein Ausdruck und wird, wie in unseren Beispielen geschehen, nur durch das nachgestellte Semikolon zu einer Anweisung. Die Wirkung: Zunachst wird i - 1 berechnet, dann der resultierende Wert der Variablen i zugewiesen. Dieser Wert ist gleichzeitig der Wert des gesamten Ausdrucks.

Damit werden Ausdrucke wie

i = (j = (k = 0))

moglich: Die drei Variablen i , j und k erhalten jeweils den Wert 0. Da mehrere Gleichheitszeichen von rechts nach links abgearbeitet werden, sind die Klammern in diesem Ausdruck sogar uberflussig und wir konnen kurz schreiben

i = j = k = 0

Compiler betrachten den Namen einer Variablen in der Regel als Reprasentanten fur den Wert der Variablen. Bei der Funktion scanf waren wir deshalb gezwungen, den Argumenten den Adressoperator & voranzustellen, damit die Adresse des Arguments anstelle seines Wertes ubergeben wird. Gleiches gilt eigentlich auch fur die Wertzuweisung: Benotigt wird ja nicht der Wert der Variablen, die verandert werden soll, sondern ihre Adresse.

Da es klar ist, dass auf der linken Seite des Zuweisungsoperators eine Adresse benotigt wird, und da die explizite Angabe des Adressoperators an allen diesen Stellen viel zu muhsam ware, vereinbart man ganz einfach: Auf der linken Seite des Zuweisungsoperators reprasentiert ein Variablenname die Adresse der Variablen und nicht wie sonst ihren Wert. Schreiben wir etwa den (in der Sache unsinnigen) Ausdruck

## i = i

so steht also i links und rechts vom Zuweisungsoperator fur ganz verschiedene Dinge.

In der Regel gibt das keine Probleme. Wesentlich wird die Unterscheidung allerdings, wenn man sich uberlegt, was aus der linken Seite eines Zuweisungsoperators stehen darf und was nicht. Dass Variablen und Elemente von Feldern erlaubt sind, haben wir bereits gesehen. Nicht erlaubt sind dagegen zum Beispiel

```
5 = i /* nicht */ i + j = k /* erlaubt */
```

da weder die Konstante 5 noch der Ausdruck i + j einen eigenen Speicherplatz mit Adresse besitzen.

Offensichtlich unterliegen die Argumente von scanf denselben Regeln wie die linken Operanden von Wertzuweisungen: scanf soll ja auch den Variablen Werte zuweisen.

## 4.3 Arithmetische Operatoren

C kennt funf arithmetische Operatoren , namlich + , -, * , / und % .

Plus und Minus gibt es in zwei Varianten: Als unare Operatoren dienen sie als Vorzeichen, wobei das positive Vorzeichen erst durch den Standard vorgeschrieben wurde; als binare Operatoren bewirken sie Addition bzw. Subtraktion.

Multiplikation bewirkt der Stern, Division der Schragstrich. Bei der Division ganzzahliger Operanden ist eine Besonderheit zu beachten: Der Quotient ist wieder ganzzahlig! Als Erganzung zum Divisionsoperator gibt es deshalb den Modulo-Operator % , der den Rest bei der Division ganzer Zahlen liefert. Dieser Operator darf nur fur ganzzahlige Operanden verwendet werden, nicht fur Gleitkommawerte. Wir sehen uns einige Beispiele fur die Division an:

```
10.0 / 3 ergibt 3.333333 10 / 3 ergibt 3 10 % 3 ergibt 1
```

Der Divisionsrest ist nur dann eindeutig bestimmt, wenn beide Operanden nichtnegativ sind; der Divisionsrest ist dann positiv. Bei mindestens einem negativen Operanden ist es den speziellen Implementationen freigestellt, ob der Divisionsrest positiv oder negativ ist. Entsprechend ist auch die ganzzahlige Division nur fur nichtnegative Operanden eindeutig, denn die Beziehung

```
a == (a / b) * b + a % b
```

muss fur beliebige ganzzahlige Werte a und b ( b ungleich 0!) erfullt sein. Moglich ist zum Beispiel 10 / - 3 == - 3 10 % - 3 == 1 ebenso wie 10 / - 3 == - 4 10 % - 3 == - 2

Arithmetische Operatoren werden von links nach rechts abgearbeitet. Dabei werden die Regel ' Punktrechnung vor Strichrechnung' naturlich ebenso berucksichtigt wie Klammern. Außerdem besitzen Plus und Minus als unare Vorzeichenoperatoren hohere Prioritat als die binaren Operatoren. Man hat also zum Beispiel

```
a + b * c == a + (b * c) a + b - c == (a + b) - c - a * b == (- a) * b
```

Auf die Probleme numerischen Rechnens wird in einem eigenen Kapitel noch eingegangen.

## 4.4 Inkrementierung und Dekrementierung

C verfugt uber spezielle Operatoren zum Inkrementieren und Dekrementieren von Variablen: ++ erhoht seinen Operanden um 1, --verringert ihn um 1.

Beide Operatoren konnen wahlweise in Prafix -Schreibweise (vor dem Operanden) oder auch Postfix -Schreibweise (hinter dem Operanden) verwendet werden. Aquivalent sind also jeweils die Anweisungen

```
++i; i++; i = i + 1; --i; i--; i = i - 1;
```

Als Ausdrucke sind Prafix- und Postfix-Schreibweise keineswegs aquivalent:

- · Bei Prafix-Schreibweise wird erst inkrementiert bzw. dekrementiert und danach der bereits veranderte Wert der Variablen als Wert des Ausdrucks genommen.
- · Bei Postfix-Schreibweise wird erst der noch unveranderte Wert der Variablen als Wert des Ausdrucks genommen und danach inkrementiert bzw. dekrementiert.

So hat nach

```
i = 10; j = ++i;
```

i den Wert 11 und j ebenfalls den Wert 11 . Nach i = 10; j = i++;

hat i wiederum den Wert 11 , j jedoch den Wert 10 .

Interessant sind beide Operatoren vor allem im Zusammenhang mit Schleifen und Vektoren. Das Beispiel, in dem wir zwei Vektoren gelesen und ihr Skalarprodukt berechnet haben, konnen wir mit ihnen durchaus kompakter schreiben:

```
#include <stdio.h> #define LAENGE 5 int main(void) {
```

```
double v1[LAENGE], v2[LAENGE], prod; /* Variablendekl. */ int i; printf("1. Vektor eingeben!\n"); /* 1. Vektor lesen */ i = 0; /* Schleife Variante 1 */ while (i < LAENGE) { scanf("%lf", &v1[i]); i++; } printf("2. Vektor eingeben!\n"); /* 2. Vektor lesen */ i = - 1; /* Schleife Variante 2 */ while (++i < LAENGE) { scanf("%lf", &v2[i]); } /* Skalarprodukt berechnen und ausgeben */ i = 0; /* Schleife Variante 3 */ prod = 0; while (i++ < LAENGE) { prod = prod + v1[i-1] * v2[i-1]; } printf("Das Skalarprodukt ist: %f\n", prod); return 0; }
```

Quelltext 4.1: Inkrement-Operator

Es sollte klar sein, dass fur die Operanden von Inkrementierung und Dekrementierung dieselben Regeln gelten wie fur die Operanden auf der linken Seite eines Zuweisungsoperators: Erneut wird ja eine Adresse benotigt, an der der veranderte Wert gespeichert werden soll.

In der Regel wird man Inkrementierung und Dekrementierung fur ganzzahlige Operanden verwenden; erlaubt sind sie aber auch fur Gleitkommaoperanden.

## 4.5 Vergleichsoperatoren

C kennt die sechs Vergleichsoperatoren == , != , < , <= , > und >= . Das Resultat eines solchen Ausdrucks ist wahr (gleich 1), wenn die Operanden in der Relation zueinander stehen, die der Operator beschreibt, und falsch (gleich 0) sonst. Letztlich sind die Resultate von Vergleichen also int -Werte; einen besonderen Typ boolean und entsprechende logische Konstanten kennt C nicht. Es steht jedem Programmierer naturlich frei, mit enum und typedef die logischen Konstanten false und true sowie einen ' Typ' boolean geeignet zu definieren.

Da Vergleichsausdrucke int -Werte sind, konnen sie Operanden in arithmetischen Ausdrucken sein. Da die Vergleichsoperatoren eine geringere Prioritat als die arithmetischen Operatoren haben, kommt man in der Regel ohne Klammern aus. Der Ausdruck

```
a < b + c
```

entspricht also

```
a < (b + c)
```

glyph[negationslash]

glyph[negationslash]

Tabelle 4.1: Wahrheitstafeln fur logische Operatoren

| a   | ! a   | a   | b   |   a && b | a   | b   |   a || b |
|-----|-------|-----|-----|----------|-----|-----|----------|
| 0   | 1     | 0   | 0   |        0 | 0   | 0   |        0 |
| = 0 | 0     | = 0 | 0   |        0 | = 0 | 0   |        1 |
|     |       | 0   | = 0 |        0 | 0   | = 0 |        1 |
|     |       | = 0 | = 0 |        1 | = 0 | = 0 |        1 |

glyph[negationslash]

glyph[negationslash]

glyph[negationslash]

glyph[negationslash]

was man in der Regel auch beabsichtigen wird. Die Prioritaten werden im einzelnen noch einmal behandelt, wenn wir mehr Operatoren kennen.

Auf etwas anderes soll an dieser Stelle aber noch kurz hingewiesen werden: Wie bereits erwahnt, kann es verhangnisvoll sein, wenn man statt == nur = schreibt. Jetzt konnen wir klaren, warum das so ist. Dazu betrachten wir das folgende Beispiel:

```
if (i = 1) { /* immer wahr */ ... } else { ... }
```

Hier wird die Anweisungsfolge, die dem else folgt, nie ausgefuhrt! Bei der Auswertung von i = 1 erhalt die Variable i den Wert 1 . Auch der Wert des Ausdrucks insgesamt ist damit 1 , wird entsprechend als wahr interpretiert und bewirkt die Ausfuhrung der unmittelbar folgenden Anweisungen.

Auch Endlosschleifen kann man so bequem (und ungewollt) ' zusammenbasteln':

while (i = 1) { /* Endlosschleife */

...

}

Anderungen von i im Schleifenrumpf haben hierauf keinen Einfluss, da der Ausdruck i = 1 vor jedem Schleifendurchgang erneut ausgewertet wird.

## 4.6 Logische Operatoren

Auch wenn C, wie wir gesehen haben, keinen Typ boolean kennt, kennt es doch drei logische Operatoren : && ( und ), || ( oder ) und ! ( nicht ).

Anwenden darf man diese Operatoren auf beliebige Operanden, die sich mit 0 vergleichen lassen - also insbesondere Zahlwerte, da wieder nach der bereits bekannten Regel vorgegangen wird: Ein Wert wird als wahr interpretiert, wenn er ungleich Null ist, und als falsch , wenn er gleich Null ist. Das Resultat ist entweder 1 oder 0. Die Wahrheitstafeln der drei logischen Operatoren finden Sie in Tabelle 4.1.

Logische Ausdrucke werden von links nach rechts abgearbeitet, wobei die Prioritaten der Operatoren berucksichtigt werden (erst die Negation, dann und , zuletzt oder ). Eine Besonderheit gegenuber anderen Programmiersprachen legt der Standard ausdrucklich fest: Die Auswertung eines logischen Ausdrucks wird beendet, sobald das Ergebnis feststeht. Das ist gelegentlich ausgesprochen nutzlich. Im Ausdruck

(d != 0) && (c / d < 10)

wird so die Division nicht ausgefuhrt, wenn d gleich 0 ist: Der erste Vergleich stellt fest, dass das Resultat falsch ist, unabhangig vom Wert des anderen Operanden - und verhindert so die in diesem Falle nicht zulassige Division. Man spricht dabei von ' lazy evaluation '.

glyph[negationslash]

glyph[negationslash]

glyph[negationslash]

## 4.7 Zusammengesetzte Zuweisungen

Neben dem einfachen Zuweisungsoperator = gibt es in C zehn zusammengesetzte Zuweisungsoperatoren . Diese haben einheitlich die Form op = , wobei op ein binarer Operator ist. Zwischen dem binaren Operator und dem Gleichheitszeichen darf kein Leerzeichen stehen (eine Neuerung des Standards). Fur eine Variable var und einen Ausdruck ausdr kann man die Wirkung der zusammengesetzten Zuweisungsoperatoren so beschreiben:

op = ausdr

```
var op ausdr
```

```
var entspricht var =
```

d.h. zunachst wird der Ausdruck ausdr ' normal' ausgewertet, dann sein Resultat mit dem Wert der Variablen var durch den Operator op verknupft und schließlich dieses Resultat in der Variablen var gespeichert. Der gespeicherte Wert ist gleichzeitig auch der Wert des gesamten Ausdrucks.

Nicht alle binaren Operatoren sind bei der Zusammensetzung erlaubt; von den Operatoren, die wir bislang kennengelernt haben, durfen nur die funf arithmetischen Operatoren verwendet werden. Sehen wir uns einige konkrete Beispiele an. Die nebeneinanderstehenden Ausdrucke sind hier jeweils aquivalent:

```
x += 3.5 entspricht x = x + 3.5 i *= j + 10 entspricht i = i * (j + 10) a += b += c entspricht a = a + (b = b + c) v[i + j*k] += 3 entspricht v[i + j*k] = v[i + j*k] + 3
```

Insbesondere das letzte dieser Beispiele zeigt, dass die zusammengesetzten Zuweisungsoperatoren einige Schreibarbeit sparen helfen. Aber nicht nur das: Dem Compiler wird es erleichtert, effizienten Code zu erzeugen. Der Indexausdruck im letzten Beispiel braucht auf jeden Fall nur einmal berechnet zu werden. Verwendet man die zusammengesetzte Zuweisung, so steht der Indexausdruck auch nur einmal im Programm, so dass der Compiler ihn nicht doppelt berechnen muss. Verwendet man dagegen die einfache Zuweisung, so muss man darauf hoffen, dass der Compiler die Identitat erkennt und die Doppelberechnung wegoptimiert.

## 4.8 Bedingte Ausdrucke

Ein auf den ersten Blick ziemlich kurioses, in der Praxis gelegentlich aber durchaus nutzliches Konstrukt ist der bedingte Ausdruck ( ? : ).

```
bedingung ? ausdruck1 : ausdruck2
```

Wenn die Bedingung bedingung den Wert wahr besitzt, ist der Wert des Gesamtausdrucks der Wert von ausdruck1 , sonst der Wert von ausdruck2 . Ein zunachst noch mehr formales Beispiel: Statt

```
if ( bedingung ) { x = ausdruck1 ; } else { x = ausdruck2 ; }
```

kann man kurz

```
x = bedingung ? ausdruck1 : ausdruck2 ; schreiben. Ein konkretes Beispiel: Durch max = z1 > z2 ? z1 : z2;
```

erhalten wir in der Variablen max das Maximum der beiden Zahlen z1 und z2 .

Die drei Ausdrucke, die gemeinsam einen bedingten Ausdruck bilden, brauchen auf keinen Fall geklammert zu werden, da die Operatoren ? und : zwar eine hohere Prioritat als der Zuweisungsoperator, gleichzeitig aber eine niedrigere Prioritat als alle anderen Operatoren haben.

## 4.9 Der Kommaoperator

Der Kommaoperator ( , ) fasst mehrere Ausdrucke zu einem einzigen Ausdruck zusammen.

Beispiel: Die Werte der beiden Variablen x und y sollen vertauscht werden. Statt

- h = x;
- x = y;
- y = h;

kann man auch

h = x, x = y, y = h;

schreiben. Dass dieses kurzer scheint, liegt ausschließlich daran, dass jeweils eine Anweisung in eine Zeile geschrieben wurde, was der Standard keineswegs verlangt.

Durch Kommaoperatoren getrennte Ausdrucke werden von links nach rechts ausgewertet. Der Wert des Gesamtausdrucks ist der Wert des am weitesten rechts stehenden, zuletzt ausgewerteten Teilausdrucks.

Der Kommaoperator sollte nur dann verwendet werden, wenn Konstruktionen sehr eng zusammengehoren, wie im Beispiel: Den Tausch der Werte von zwei Variablen kann man durchaus als eine Operation ansehen. Wir werden andere Stellen kennenlernen, an denen sich der Kommaoperator als durchaus nutzlich erweist.

Kommata, die in Variablenvereinbarungen und Funktionsaufrufen stehen, haben ubrigens nichts mit dem Kommaoperator zu tun. Entsprechend haben sie dort auch keinen Einfluss auf die Reihenfolge der Auswertung.

## 4.10 Prioritat der Operatoren

Da wir nun schon eine ganze Reihe von Operatoren behandelt haben, ist es an der Zeit, dass wir uns die Prioritaten der Operatoren einmal im Zusammenhang ansehen. Die Aufstellung ist in Abbildung 4.2 enthalten.

Als erstes ist die Prioritatsstufe der Operatoren angegeben: Je hoher die Stufe, desto hoher die Prioritat. Wenn auf einer Stufe mehrere Operatoren stehen, so haben sie dieselbe Prioritat.

Fur jede Prioritatsstufe ist ganz rechts angegeben, ob die Abarbeitung ihrer Operatoren von links nach rechts (z.B. bei Addition und Subtraktion) oder von rechts nach links (z.B. bei Wertzuweisungen) erfolgt.

Auch wenn noch nicht alle Operatoren bekannt sind, lohnt es sich, die Tabelle einmal in Muße zu studieren und sich die Prioritatsstufen im wesentlichen einzupragen. Allzu extensive Nutzung der Kenntnis der Prioritatsstufen lohnt allerdings auch nicht, da dann

Tabelle 4.2: Prioritaten der Operatoren

|   Stufe | Operator                         | Beschreibung                                                                                                                                                                                                                                              | Auswertungsreihenfolge   |
|---------|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
|      15 | ( ) [ ] -> .                     | Auswertung von Parametern Auswahl einer Feldkomponente Auswahl einer Strukturkomponente                                                                                                                                                                   | →                        |
|      14 | ! ~ ++ -- + - ( Typ ) & * sizeof | Negation (logisch, bitweise) Inkrementierung, Dekrementierung (Prafix oder Postfix) Vorzeichen (unar) Typumwandlung Adressbildung, Dereferenzierung (unar) Bestimmung des Speicherbedarfs Multiplikation (binar), Division Rest bei ganzzahliger Division | ←                        |
|      13 | * / %                            |                                                                                                                                                                                                                                                           | →                        |
|      12 | + -                              | Summe, Differenz (binar)                                                                                                                                                                                                                                  | →                        |
|      11 | << >>                            | bitweise Verschiebung nach links, rechts                                                                                                                                                                                                                  | →                        |
|      10 | < <= > >=                        | Vergleich auf kleiner, kleiner oder gleich Vergleich auf großer, großer oder gleich                                                                                                                                                                       | →                        |
|       9 | == !=                            | Vergleich auf gleich, ungleich                                                                                                                                                                                                                            | →                        |
|       8 | &                                | Und (bitweise)                                                                                                                                                                                                                                            | →                        |
|       7 | ^                                | exklusives Oder (bitweise)                                                                                                                                                                                                                                | →                        |
|       6 | |                                | inklusives Oder (bitweise)                                                                                                                                                                                                                                | →                        |
|       5 | &&                               | Und (logisch)                                                                                                                                                                                                                                             | →                        |
|       4 | ||                               | inklusives Oder (logisch)                                                                                                                                                                                                                                 | →                        |
|       3 | ? :                              | bedingte Auswertung (nur paarweise!)                                                                                                                                                                                                                      | ←                        |
|       2 | = +=                             | Wertzuweisung zusammengesetzte Wertzuweisung (auch: -= , *=, %= , /= , <<= , >>= , |= )                                                                                                                                                                   | ← &= , ^= ,              |

leicht vollig unleserliche Ausdrucke resultieren. Die folgende Auswahl verdeutlicht diesen Umstand:

| i - j      | /*   | 1: binaer */                         |
|------------|------|--------------------------------------|
| i -- j     | /*   | 2: unzulaessig */                    |
| i - - j    | /*   | 3: binaer/unaer */                   |
| i --- j    | /*   | 4: Dekrement/binaer (wie 6.) */      |
| i - -- j   | /*   | 5: binaer/Dekrement */               |
| i -- - j   | /*   | 6: Dekrement/binaer */               |
| i ---- j   | /*   | 7: unzulaessig */                    |
| i - --- j  | /*   | 8: unzulaessig */                    |
| i -- -- j  | /*   | 9: unzulaessig */                    |
| i --- - j  |      | /* 10: Dekrement/binaer/unaer */     |
| i ----- j  |      | /* 11: unzulaessig */                |
| i - ---- j |      | /* 12: unzulaessig */                |
| i -- --- j |      | /* 13: unzulaessig */                |
| i --- -- j |      | /* 14: Dekrement/binaer/Dekrement */ |
| i ---- - j |      | /* 15: unzulaessig */                |
| i ------ j |      | /* 16: unzulaessig */                |

Falls ein Ausdruck dieser Art benotigt wird, kann es nicht schaden, ihn auch dann zu klammern, wenn dies nicht zwingend notwendig ist.

## 4.11 Nebeneffekte

Unter einem Nebeneffekt versteht man bei der Programmierung, dass als Nebenprodukt der Auswertung eines Ausdrucks der Wert einer Variablen verandert wird.

In der Regel wird dringend geraten, Nebeneffekte zu vermeiden. Das ist in C jedoch nicht moglich, denn C ist geradezu die ' Sprache der Nebeneffekte': Da die Wertzuweisung keine Anweisung, sondern ein Operator ist, lassen sich die Werte von Variablen nur durch Nebeneffekte verandern!

Neben den Zuweisungsoperatoren bewirken auch die Inkrement- und Dekrementoperatoren sowie alle Funktionen mit Ausgabeparametern Nebeneffekte. Beispiel:

while (scanf (...) == 1)

```
...
```

Der Standard schreibt nur sehr eingeschrankt vor, zu welchem Zeitpunkt Nebeneffekte wirksam werden mussen:

- · Nebeneffekte konnen naturlich nicht eintreten, bevor die Auswertung des Ausdrucks beginnt, durch die sie erzeugt werden.
- · Wenn die Auswertung eines Ausdrucks abgeschlossen ist, mussen auch seine Nebeneffekte eingetreten sein.

Die Folge: Wenn eine Variable innerhalb eines Ausdrucks mehrfach angesprochen wird und außerdem Nebeneffekte fur sie eintreten, ist meist nicht definiert, welchen Wert die Variable im Einzelfall besitzt. So konnen Ausdrucke wie

```
v[i] = i++; v[i] = w[i++]; s += v1[i] * v2[i++]; b = a++ + a;
```

implementationsspezifisch unterschiedliche Resultate zeitigen.

Ahnliche Probleme konnen sich aus der Tatsache ergeben, dass die Reihenfolge der Auswertung von Ausdrucken nur teilweise festgelegt ist:

- · Fur die drei Ausdrucke, die gemeinsam einen bedingten Ausdruck bilden, liegt die Reihenfolge eindeutig fest: Erst wird die Bedingung ausgewertet, dann der Ausdruck, der das Resultat ergibt. Der jeweils andere Ausdruck wird nicht ausgewertet und es treten keine Nebeneffekte fur ihn ein.
- · Logische Ausdrucke werden von links nach rechts ausgewertet; ihre Berechnung wird beendet, sobald das Resultat feststeht. Bei || ist das der Fall, sobald der erste Teilausdruck wahr ist, bei && sobald der erste Teilausdruck falsch ist. Nebeneffekte treten jeweils auf, bevor mit dem nachsten Teilausdruck fortgefahren wird.
- · Ausdrucke, die mit dem Kommaoperator verknupft sind, werden von links nach rechts ausgewertet. Dabei treten alle Nebeneffekte auf, bevor der rechte Ausdruck ausgewertet wird.
- · Sonst ist zwar festgelegt, in welcher Reihenfolge aufeinanderfolgende Operatoren gleicher Hierarchiestufe ausgefuhrt werden, nicht aber die Reihenfolge der Berechnung der Operanden.

Betrachten wir fur den letzten Punkt ein Beispiel: Der Ausdruck

```
(a) + (b) + (c) muss wie ((a) + (b)) + (c)
```

ausgewertet werden. Sind a , b und c ihrerseits Ausdrucke, so ist keineswegs festgelegt, welcher von ihnen zuerst berechnet wird. Konkret: Die Anweisungsfolge

```
i = 5; j = i * 3 + ++i - 7;
```

kann in der Variablen j je nach Implementation den Wer 14 oder 17 liefern.

Ebenfalls ist nicht festgelegt, in welcher Reihenfolge die Argumente eines Funktionsaufrufs berechnet werden. So kann die Anweisungsfolge

n = 3; printf("%d, %d\n", ++n, 2*n);

je nach Implementation die Ausgabe 4, 6 oder 4, 8 ergeben.

Aber auch die scheinbar problemlosen Operatoren bieten ' Fallstricke', weil bei ihnen Teilausdrucke unter Umstanden nicht ausgewertet werden und in ihnen steckende Nebeneffekte entsprechend mal eintreten und mal nicht:

```
if (x == y && a == ++b) /* 1 */ ... if (x == y || a == ++b) /* 2 */ ... z = x == y ? a : ++b; /* 3 */
```

Im ersten Beispiel wird b nur dann inkrementiert, wenn x == y gilt; im zweiten und dritten Beispiel wird b nur dann inkrementiert, wenn x != y gilt.

Fazit: Bei Operatoren und Funktionen, die Nebeneffekte erzeugen, sollte man außerste Vorsicht walten lassen - zumal man Fehler im Programm, die aus Nebeneffekten resultieren, oft nur mit großer Muhe findet. Insbesondere sollte man darauf achten, dass Variablen, die inkrementiert oder dekrementiert werden, innerhalb eines Ausdrucks nur an der Stelle vorkommen, an der sie inkrementiert bzw. dekrementiert werden.

## 4.12 Typumwandlung

Einen wesentlicher Punkt ist bisher noch nicht eindeutig geklart worden: Welche Typen durfen bzw. mussen die Operanden eines binaren arithmetischen Operators besitzen?

Die Antwort ist ganz einfach: Jede beliebige Kombination ist erlaubt! Oder, um den Fachbegriff zu verwenden: mixed mode ist uneingeschrankt erlaubt. Das Beispiel, das wir bereits betrachtet hatten, war

10.0 / 3 = 3.333333

Die Frage ist: Welchen Wert erhalten solche Ausdrucke? Der Rechner kann grundsatzlich nur Operanden mit identischen Typen verknupfen, so dass also vor die eigentliche Verknupfung ggf. eine Typumwandlung vorgeschaltet werden muss. Dieses ubernimmt der C-Compiler in der Regel fur den Programmierer; man bezeichnet solche Typumwandlungen auch als implizite Typumwandlungen . Dass das Resultat einer Verknupfung den Typ der beteiligten Operanden (ggf. nach der Umwandlung) hat, ist naheliegend, von der

ganzzahligen Division vielleicht einmal abgesehen. Man kann deshalb auch vom ' Typ eines Ausdrucks' sprechen.

Schauen wir uns zunachst an, was bei der Verknupfung von zwei Operanden durch einen binaren arithmetischen Operator geschieht:

Der erste Grundsatz: Mit Werten der Typen char und short , mit oder ohne Vorzeichen, wird nicht gerechnet, d.h. Werte mit diese Typen werden vor dem Rechnen auf jeden Fall automatisch in int bzw. unsigned int umgewandelt. Ein Ausdruck wie 'Z' - 'A' hat also den Typ int .

Der zweite Grundsatz: Bei Operanden mit unterschiedlichen Typen wird der Operand mit dem ' niederwertigen' Typ in den ' hoherwertigen' Typ umgewandelt. Was unter ' niederwertig' und ' hoherwertig' zu verstehen ist, legt die in Tabelle 4.3 dargestellte Hierarchie der Typen fest.

Tabelle 4.3: Hierarchie der impliziten Typumwandlung

| long und int ungleich   | long und int ungleich   |   long und int gleich | long und int gleich   |
|-------------------------|-------------------------|-----------------------|-----------------------|
| 7.                      | long double             |                     5 | long double           |
| 6.                      | double                  |                     4 | double                |
| 5.                      | float                   |                     3 | float                 |
| 4.                      | unsigned long           |                     2 | unsigned int / long   |
| 3. 2.                   | long unsigned int       |                     1 | int / long            |

1.

int

Dass die Typen char und short hier nicht vorkommen, liegt daran, dass sie ohnehin umgewandelt werden.

Bei komplexeren Ausdrucken entwickelt sich der Typ im Laufe der Auswertung. Insbesondere wird nicht zuerst der Typ des Resultats bestimmt und erst danach die Berechnung ausgefuhrt. Dahinter steht, dass jeder Teilausdruck im einfachsten moglichen Typ ausgewertet werden soll. Beispiel:

```
short s = 65; int i = 7; long j = 1000; float x = 3.0; double y = 46.5;
```

printf("%f\n", s * i + j % i + y / x);

Zunachst werden die Multiplikationen und Divisionen ausgefuhrt, wobei die angegebene Reihenfolge nicht notwendig eingehalten werden muss:

- · Im Ausdruck s * i wird s zunachst in int umgewandelt. Die Multiplikation liefert den int -Wert 455.
- · Im Ausdruck j % i wird i zunachst in long umgewandelt. Der Divisionsrest ist der long -Wert 6.
- · Im Ausdruck y / x wird x zunachst in double umgewandelt. Der Quotient ist der double -Wert 15.5.

Die Additionen mussen nun von links nach rechts ausgefuhrt werden:

- · Der int -Wert 455 wird in long umgewandelt und zum long -Wert 6 addiert. Die Summe ist der long -Wert 461.

- · Der long -Wert 461 wird in double umgewandelt und zum double -Wert 15.5 addiert. Die Summe ist der double -Wert 476.5. Das ist gleichzeitig das Gesamtresultat.

Die Art und Weise, in der die impliziten Typumwandlungen erfolgen, birgt wieder ' Fallstricke'. Ein haufig gemachter Fehler ist zum Beispiel die unbeabsichtigte ganzzahlige Divisionen. So liefert der Ausdruck 1 / 2 * 3.5 stets den Wert 0! In derart offensichtlicher Form kommt dieser Fehler in der Praxis naturlich selten vor. Haufiger ist er mit zwei int -Variablen, etwa i / j * 3.5 - was an der ganzzahligen Division nichts andert.

Die Zuweisungsoperatoren nehmen eine Sonderstellung ein! Es ist einer Variablen ein Wert zuzuweisen - der Typ einer Variablen ist aber nichts, was wahrend der Ausfuhrung eines Programms verandert werden kann. Typumwandlung im Zuge einer Wertzuweisung ist also zwar ggf. erforderlich, kann aber stets nur in einer Umwandlung des Typs des Wertes in den Typ der Variablen bestehen. Dabei kann es erforderlich sein, dass aus einem ' hoherwertigen' in einen ' niederwertigen' Typ umgewandelt wird:

- · Bei der Umwandlung zwischen ganzzahligen Typen werden nur die wertniedrigsten Bits ubernommen.
- · Bei der Umwandlung eines Gleitkommawertes in einen ganzzahligen Typ gehen eventuelle Nachkommastellen verloren. Eine Rundung erfolgt bei dieser Umwandlung nicht ! So erhalt die int -Variable i durch die Wertzuweisung i = 3.9; den Wert 3 !
- · Wenn bei Gleitkommatypen aus hoherer in niedrigere Genauigkeit umgewandelt wird (z.B. von double in float ), bleibt es den Implementatoren uberlassen, ob dabei gerundet oder abgeschnitten wird. (Das ist bei binaren Darstellungen letztlich gleichwertig!)
- · Bei der Umwandlung aus einem ' großen' ganzzahligen Typ in einen ' kleinen' Gleitkommatyp kann Genauigkeit verlorengehen.

Uber die impliziten Typumwandlungen, die ggf. fur die Argumente von Funktionen durchgefuhrt werden, wurde bei der Einfuhrung von printf schon einiges gesagt. Im Rahmen der Behandlung der Funktionen wird darauf noch weiter eingegangen.

## 4.13 Castoperatoren

Gelegentlich ist es wunschenswert, den Compiler dazu zwingen zu konnen, einen Wert in einen bestimmten Typ umzuwandeln, etwa zur Vermeidung von unerwunschten ganzzahligen Divisionen.

Hierfur stellt C die Castoperatoren zur Verfugung. Solch ein Castoperator ist eine Typbezeichnung, die in runde Klammern eingeschlossen wird. Castoperatoren sind immer unar und haben sehr hohe Prioritat, wie alle anderen unaren Operatoren.

Wollen wir etwa erreichen, dass der double -Quotient von zwei int -Variablen i und j berechnet wird, so konnen wir alternativ schreiben

(double) i / j

- i / (double) j

Der Castoperator wirkt dabei wegen seiner hohen Prioritat jeweils nur auf einen der beiden Operanden. Der andere Operand wird dann gemaß der Regeln der impliziten Typumwandlung ebenfalls nach double umgewandelt.

Alle Probleme der Umwandlungen, die durch Wertzuweisungen erzwungen werden, konnen offensichtlich auch bei der Verwendung von Castoperatoren auftreten. Daruber hinaus erlauben die Castoperatoren bei unsachgemaßer Verwendung auch viel Unsinn. Dies wird besonders spater bei der Verwendung von Zeigern deutlich werden.

## 4.14 Der sizeof -Operator

Mit dem sizeof -Operator lasst sich der Speicherbedarf fur Datentypen ermitteln. Das wird spater noch eine Rolle spielen, wenn dynamisch Speicher bereitgestellt werden soll.

```
sizeof ausdruck sizeof ( typ )
```

Im ersten Fall ist das Resultat der Speicherbedarf der benotigt wurde, um eine einfache Variable vom Typ des Ausdrucks zu speichern. Im zweiten Fall ist das Resultat der Speicherbedarf einer einfachen Variablen mit dem angegebenen Typ. Die Maßeinheit ist rechnerspezifisch, wird jedoch dadurch festgelegt, dass der Standard sizeof (char) == 1 vorschreibt. Festgelegt ist außerdem, dass das Resultat den Typ size\_t besitzt - oder umgekehrt: Der Typ size\_t ist so zu definieren, dass sein Wertebereich alle moglichen Resultate des Operators sizeof umfasst. size\_t ist demnach kein elementarer Datentyp, sondern wird in den Headerdateien stddef.h , stdlib.h und string.h deklariert.

Bei der Verwendung des sizeof -Operators sind einige Dinge besonders zu beachten:

- · Handelt es sich bei ausdruck um den Namen eines Feldes, bzw. bei typ um einen Feldtyp, so wird sowohl die Dimension des Feldes als auch die Große der einzelnen Elemente berucksichtigt.

```
int feld[7]; size\_t s; s = sizeof (feld); /* s == 28 */ s = sizeof (char [2][5]); /* s == 10 */
```

- · Der sizeof -Operator ist trotz seiner Form nicht mit einem Funktionsauruf wie z.B. bei printf(...) zu verwechseln. Ganz speziell gilt, dass keine Nebeneffekte fur den Ausdruck ausdruck auftreten. Der Compiler ermittelt lediglich den Typ des Ausdrucks. Zur Laufzeit des Programms werden keine weiteren Operationen ausgefuhrt. Das kann zu einiger Verwirrung fuhren:

```
int s = 0; printf("%d\n", sizeof (5 / s)); /* Ausgabe: 4 */ printf("%d\n", sizeof (s = 5)); /* Ausgabe: 4 */ /* s == 0 */
```

Es sind also sogar Ausdrucke erlaubt, die zur Laufzeit einen Fehler verursachen wurden (im Beispiel Division mit 0). Da dieser Ausdruck jedoch formal den Typ int besitzt, wird der Wert 4 ermittelt (vorausgesetzt der Typ int besitzt die Große 4, was jedoch auf gangigen 32-Bit Architekturen der Fall ist).