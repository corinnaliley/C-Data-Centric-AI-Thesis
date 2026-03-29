## Kapitel 15

## Probleme der Rechnerarithmetik

## 15.1 Gleitkomma-Ausnahmebehandlung

Numerisches Rechnen mit Computern ist nicht unproblematisch. Das gilt besonders fur das Rechnen mit Gleitkommawerten, in gewissem Maße aber auch fur das Rechnen mit ganzzahligen Werten. Diese Probleme sind keineswegs C-spezifisch, sondern treten bei allen Sprachen auf, die die entsprechenden Datentypen kennen, und haben eine einzige Ursache, namlich die begrenzte Stellenzahl, die dargestellt werden kann.

Erinnern Sie sich noch einmal an die Minimalanforderungen fur double -Zahlen, die am Anfang des Kurses genannt wurden: Der geforderte minimale Wertebereich ist

[ -10 +37 , -10 -37 ] ∪ { 0 } ∪ [+10 -37 , +10 +37 ]

bei einer minimalen Dichte von 10 -9 . Hieraus ergeben sich direkt die drei ' problematischen' Falle:

- · Es kann ein Uberlauf ( overflow ) eintreten, d.h. ein Wert wird dem Betrage nach großer als DBL MAX .
- · Es kann ein Unterlauf ( underflow ) eintreten, d.h. ein Wert wird dem Betrage nach kleiner als DBL MIN .
- · Ein Wert fallt in eine ' Lucke' zwischen zwei darstellbaren Zahlen, d.h. er muss gerundet werden.

Wie auf solche Falle reagiert wird, kann von Rechner zu Rechner sehr unterschiedlich sein. Mann kann deshalb nur ' ubliche' Reaktionen beschreiben; andere Reaktionen sind denkbar.

- · Beim Uberlauf gibt es drei ' ubliche' Reaktionen:
- -Das Programm wird abgebrochen.
- -Der Wert wird auf ' Infinity' gesetzt, einen ausgezeichneten Wert.
- -Der Wert wird undefiniert.

Division durch Null wird mit gewisser Berechtigung in der Regel wie ein Uberlauf behandelt.

- · Bei Unterlauf ist es ublich, den Wert durch Null zu ersetzen, ohne dass dieses dem Programm angezeigt wird.
- · Gerundet wird in der Regel automatisch, ohne dass dieses dem Programm angezeigt wird.

Nur fur den Uberlauf schreibt C vor, dass ein Programm selbst festlegen kann, wie darauf zu reagieren ist. Die entsprechenden Mittel stellt C mit der Headerdatei signal.h zur Verfugung.

## 15.2 Uberlauf bei ganzen Zahlen

Die ganzzahligen Typen sind auf der einen Seite weniger problematisch, da bei ihnen nur der Uberlauf eintreten kann, und auf der anderen Seite problematischer, da die Verhinderung/Vermeidung von Uberlaufen grundsatzlich und ausschließlich in die Verantwortung des Programmierers gestellt ist.

Uberlauf bei ganzzahligen Operationen bewirkt namlich in der Regel nichts - außer dass mit falschen Werten weitergerechnet wird. Eine Ausnahme sind Divisionen durch Null und naturlich Berechnungen des Restes mit Divisor Null, die vielfach einen Programmabbruch bewirken.

Der Hintergrund fur die ublicherweise verschiedenen Vorgehensweisen sind Hardware-Eigenschaften der Rechner: Bei Gleitkommaoperationen ist jeder Uberlauf und Unterlauf ein Fehler, der ohnehin besonders behandelt werden muss. Bei ganzzahligen Operationen tritt dagegen haufiger ein Hardware-Uberlauf auf, ohne dass das ein Fehler ist. Wir sehen uns das an einem Beispiel an. Der Einfachheit halber wird Byte-Arithmetik betrachtet, auch wenn C sie nicht explizit vorsieht. Wir haben etwa

1111 1111 b + 0000 0001 b = 1 0000 0000 b

wobei das werthochste, neunte Bit gerade das uberlaufende Bit ist, das nicht mehr gespeichert werden kann. Ob dieser Uberlauf ein Fehler ist oder nicht, hangt davon ab, ob wir die Operanden als vorzeichenbehaftet oder vorzeichenlos betrachten:

- · Bei vorzeichenbehafteter Operation haben wir gerade -1 + 1 = 0, also das korrekte Resultat!
- · Bei vorzeichenloser Operation haben wir 255 + 1 = 0 - und das ist offenbar falsch!

Sieht man sich das ganze genauer an, so stellt man fest, dass bei vorzeichenlosen Operationen modulo ... MAX + 1 gerechnet wird. Bei vorzeichenbehafteten Operationen kommt man zu einem ahnliche Ergebnis.

Ubrigens: Bei den impliziten Typumwandlungen im Zuge von arithmetischen Operationen sind die Regeln gerade so angelegt, dass Uberlauf und Unterlauf nicht auftreten konnen. Werden Typumwandlungen dagegen durch Wertzuweisungen oder Castoperatoren erzwungen, konnen Uberlauf und Unterlauf wie bei arithmetischen Operationen auftreten.

## 15.3 Normalisierte Gleitkomma-Darstellungen

Wir haben gesehen, dass man im Programm oder auch bei der Eingabe fur Gleitkommawerte beliebig viele verschiedene Darstellungen verwenden kann. Der Wert 1.2 kann etwa als 1.2 , 12e-1 , 0.12e1 , usw., dargestellt werden.

Im Rechner gibt es dagegen fur jeden darstellbaren Gleitkommawert nur genau eine Darstellung, die als normalisierte Darstellung bezeichnet wird. Prinzipiell gibt es unterschiedliche normalisierte Darstellungen (beschrieben in einer Norm von IEEE), viele Rechner verwenden von diesen jedoch nur genau eine.

Der Anschaulichkeit halber wird die normalisierte Darstellungen fur dezimale Rechenwerke beschrieben. Als Beispiel nehmen wir ein Rechenwerk, das mit funf signifikanten Stellen

und einem einstelligen Exponententeil arbeitet. Eine normalisierte Darstellung setzt den (gedachten) Dezimalpunkt direkt links neben die werthochste signifikante Ziffer und passt den Exponenten entsprechend an; in ihr hat der Wert 1.2 also die eindeutige Darstellung

0 . 12000 · 10 1

Der Wertebereich dieses Rechenwerkes ist dann

[ -0 . 99999 · 10 +9 , -0 . 10000 · 10 -9 ] ∪ { 0 } ∪ [+0 . 10000 · 10 -9 , +0 . 99999 · 10 +9 ]

wobei Null (0 . 00000 · 10 0 ) besonders definiert werden muss, da die Darstellung nicht normalisiert ist.

Wenn man mit solchen Darstellungen rechnen will, muss man sie in die beiden Bestandteile zerlegen, die beiden Bestandteile getrennt verarbeiten und dann wieder zu einer normalisierten Darstellung zusammenfugen.

## 15.4 Assoziativ- und Kommutativgesetz

Ausdrucke werden Schritt fur Schritt ausgewertet - und in jedem Schritt muss der berechnete Wert innerhalb des Wertebereichs des Typs liegen. Wir sehen uns das fur den Ausdruck ab cd an, der in float -Arithmetik ausgewertet werden soll:

| A       | B       | C       | D       | A*B/C/D   | A/C*B/D   |
|---------|---------|---------|---------|-----------|-----------|
| 10 30   | 10 30   | 10 30   | 10 30   | Uberlauf  | 1         |
| 10 30   | 10 - 30 | 10 - 30 | 10 30   | 1         | Uberlauf  |
| 10 - 30 | 10 - 30 | 10 - 30 | 10 - 30 | Unterlauf | 1         |
| 10 - 30 | 10 30   | 10 30   | 10 - 30 | 1         | Unterlauf |

Obwohl das theoretische Resultat in allen Fallen 1 ist, konnen Uberlauf und Unterlauf auftreten!

Assoziativ- und Kommutativgesetz sind also auf einem Rechner fur Gleitkommazahlen nicht erfullt, da die Voraussetzungen fur beide Gesetze nicht erfullt sind: Zur Verfugung hat man ja nicht die reellen Zahlen, sondern nur eine Teilmenge, deren Werte nicht dicht in den reellen Zahlen liegen!

Folgerung: Man sollte sich bei Gleitkommaausdrucken genau uberlegen, in welcher Reihenfolge man sie ausgewertet haben mochte. Der Standard unterstutzt das, im Gegensatz zum ' alten' C: Scheinbar redundante Klammern durfen nicht mehr ' wegoptimiert' werden! War ein Compiler fruher berechtigt, in einem Ausdruck wie

## a + (b + c)

die Klammern schlichtweg zu ignorieren (was unter Umstanden zu ' Klimmzugen' im Programm zwang), so muss ein Standardcompiler sie jetzt berucksichtigen!

Beispiel: Sind a = 1 , b = -1e12 und c = 1e12 , dann ergibt sich bei einem Rechenwerk mit 10 signifikanten Stellen

a + (b + c) = 1

(a + b) + c = 0

## 15.5 Rundungsfehler

Damit kommen wir auch schon zum nachsten Problem, namlich der Rundung, die aufgrund der begrenzten Stellenzahl in vielen Fallen unumganglich ist, und den sich daraus ergebenden Rundungsfehler .

Nehmen wir einmal an, wir hatten ein dezimales Rechenwerk zur Verfugung, das mit zwei Dezimalstellen Genauigkeit arbeitet. Dann lasst sich in diesem Rechenwerk die Zahl 1 . 5 exakt speichern. Bildet man jetzt jedoch das Produkt 1 . 5 ∗ 1 . 5, so resultiert die Zahl 2 . 25 mit drei signifikanten Stellen, die nicht mehr exakt gespeichert werden kann, sondern zunachst durch Rundung auf zwei signifikante Stellen verkurzt werden muss. In unserem Rechenwerk ist das Resultat, je nach Art der Rundung, also entweder 2 . 2 oder 2 . 3.

Genau diese Probleme treten bei jedem Rechner auf. Allerdings lasst sich das, was bei einem Rechner passiert, fur einen Menschen nicht mehr so auf den ersten Blick uberschauen: Der Mensch ist in seinen Zahlenvorstellungen sehr stark auf das Dezimalsystem fixiert, wahrend die Rechner ja mit binaren Zahlendarstellungen arbeiten.

Und so wird vielfach ubersehen, dass Rundungsfehler nicht erst beim eigentlichen Rechnen, sondern bereits bei der Umwandlung der dezimalen Konstantendarstellung in die interne Darstellung auftreten. Dazu ein Beispiel: Der ' schone' Dezimalbruch 0 . 2 d ergibt bei Umwandlung in Binardarstellung den periodischen Bruch 0 . 001100110011 . . . b , lasst sich also im Rechner nur gerundet darstellen.

Bei arithmetischen Operationen mit gerundeten Zahlen konnen die Rundungsfehler unter Umstanden erheblich anwachsen. Dazu das folgende Beispiel, das 10000 Mal 0 . 2 addiert und das Ergebnis ausgibt:

```
float schritt = 0.2f, summe = 0.0f; int i; for (i = 0; i < 10000; i++) summe += schritt; printf("%f\n", summe); printf("%f\n", 10000 * schritt);
```

Ein Testlauf ergab fur die erste Ausgabe den Wert 1999 . 805835 und fur die zweite Ausgabe 2000 . 000000.

Der Programmierer muss sich also sehr genau uberlegen, wie er sein Programm formuliert, um den Einfluss der Rundungsfehler moglichst gering zu halten. Dazu ein Beispiel: Eine Funktion f ( x ) sei in einem Intervall [ a, b ] zu tabellieren, wobei die Anzahl N der Teilintervalle vorgegeben ist.

Als 'naive' Losung bietet sich an, zunachst einmal die Schrittweite zu berechnen und ihren Wert dann bei jedem Schleifendurchlauf zur Bestimmung des nachsten Tabellierungspunktes zu verwenden. Das Programm hat dann das folgende Schema:

```
h = (b - a) / N; x = a; while (x <= b) { printf("%f %f\n", x, f (x)); x += h; }
```

Mit den Werten a = 0 , b = 4 und N = 40 erhalt hier die Variable x vor dem letzten Schleifendurchlauf den Wert 3.9999980, erreicht also nicht exakt den rechten Rand des Ta-b

llierungsintervalls. Entsprechend ungenau werden naturlich auch die tabellierten Funktionswerte.

Gunstiger ist es, nicht mit der Schrittweite zu arbeiten, sondern die Tabellierungspunkte jeweils direkt zu berechnen, etwa nach dem folgenden Schema

```
i = 0; while (i <= N) { x = ((N - i) * a + i * b) / N printf("%f %f\n", x, f (x)); i++; }
```

Hier wird, wieder mit den Werten a = 0 , b = 4 und N = 40 , beim letzten Schleifendurchlauf der rechte Rand des Tabellierungsintervalls exakt erreicht.

Auch bei Typumwandlungen konnen Rundungsfehler auftreten - und das nicht nur bei erzwungenen Umwandlungen: Fur den Typ float sind nur 6 signifikante Stellen vorgeschrieben, wahrend der Typ long uber mindestens 10 Stellen verfugen muss. Bei einer Umwandlung von long in float , wie sie ggf. automatisch bei der Auswertung von Ausdrucken erfolgt, konnen also durchaus die letzten Stellen des long -Wertes verloren gehen.

## 15.6 Ausloschung

Wir haben eben gesehen, dass sich die Rundungsfehler bei Gleitkomma-Arithmetik in bestimmten Situationen beherrschen oder doch zumindest reduzieren lassen. In anderen Situationen ist das nicht so einfach oder sogar unmoglich.

```
Wir betrachten zunachst wieder ein Beispiel: Gegeben seien Zahlen x 1 = 0.42178 · 10 2 x 2 = 0.23722 · 10 3 y 1 = 0.99986 · 10 2 y 2 = 0.99987 · 10 2 Dann gilt x 1 x 2 = 0.1000546516 · 10 5 y 1 y 2 = 0.9997300182 · 10 4 und x 1 x 2 -y 1 y 2 = 0 . 10005465160 · 10 5 -0 . 09997300182 · 10 5 = 0 . 00008164978 · 10 5 normalisiert: 0 . 81649780000 · 10 1
```

Das zwischenzeitliche Vorkommen fuhrender Nullen wird als Ausloschung bezeichnet.

Erlaubt die verfugbare Arithmetik nicht die exakte Darstellung der Zwischenresultate, sondern z.B. nur funfstellige Resultate, so werden bereits die Produkte x 1 x 2 und y 1 y 2 gerundet geliefert:

```
x 1 x 2 ≈ x = 0 . 10005 · 10 5 und y 1 y 2 ≈ y = 0 . 99973 · 10 4
```

Erst danach kann die Subtraktion ausgefuhrt werden und liefert

x - y = 0 . 100050 · 10 5

- 0 . 099973 · 10 5

= 0 . 000077 · 10 5 normalisiert: 0 . 770000 · 10 1 gerundet: 0 . 77000 · 10 1

Der Vergleich der Differenzen x 1 x 2 -y 1 y 2 und x -y zeigt, dass das gerundete Resultat zwar dieselbe Großenordnung besitzt wie das exakte Resultat, dass aber nicht einmal die werthochsten Ziffern ubereinstimmen.

Ausloschung tritt immer dann ein, wenn zwei beinahe gleichgroße Zahlen subtrahiert werden. Selbst wenn die einzelne Subtraktion fehlerfrei ausgefuhrt wird, ist die Ausloschung numerisch gefahrlich, wenn die zu subtrahierenden Daten selber bereits gerundet wurden.

Im Beispiel, das wir eben betrachtet haben, hatte das tatsachliche Resultat noch die Großenordnung des theoretischen Resultats. Es bereitet jedoch keine Probleme, Beispiele zu finden, in denen auch die Großenordnungen voneinander abweichen. Dazu betrachten wir die Taylorreihe der Exponentialfunktion

e z = ∞ ∑ k = 0 z k k !

Diese Reihe ist absolut konvergent fur jedes z aus der komplexen Zahlenebene. Fur reelles, negatives z haben die Summanden alternierende Vorzeichen. In diesem Fall ist der Fehler, den man begeht, wenn man die n -te Partialsumme als Wert fur e z nimmt, kleiner als der ( n +1)-te Summand, der als erster vernachlassigt wird.

Wertet man diese Reihe unter Verwendung einer Arithmetik mit 6-stelliger dezimaler Mantisse fur z = -14 aus, so erhalt man nach 50 Additionen den Wert -0 . 159691 das korrekte Resultat ware 0 . 00000083152900! (Der Abbruch der Summation nach 50 Schritten erfolgt, weil alle weiteren Summanden so klein sind, dass sie bei der verwendeten Arithmetik keinen Beitrag mehr zu der Summe liefern.)

Hier lasst sich mit Mitteln der Programmiertechnik nichts mehr ausrichten. Abhilfe schaffen nur noch besondere Algorithmen, die die Probleme der Gleitkommaarithmetik berucksichtigen, oder der Einsatz der Intervallrechnung.