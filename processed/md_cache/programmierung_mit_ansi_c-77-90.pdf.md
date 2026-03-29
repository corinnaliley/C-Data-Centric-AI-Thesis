## Kapitel 7

## Funktionen

## 7.1 Motivation

Je umfangreicher und komplexer ein Problem ist, desto schwieriger ist es zu losen. Deshalb versucht man, Programmieraufgaben in verschiedene Teile zu zerlegen, die man ihrerseits wieder in Teilprobleme zerlegt, usw. Dabei achtet man besonders darauf, dass zwischen den Teilproblemen moglichst wenig Querverbindungen bestehen. Dieses Vorgehen hat drei Vorteile:

- · Jedes Teilproblem ist viel einfacher zu losen als das Gesamtproblem.
- · Die Teilprobleme konnen von verschiedenen Programmierern gelost weren.
- · Wenn man ' Gluck' hat, besitzt man schon Losungen fur einzelne Teilprobleme.

In der Terminologie des Programmierens entspricht eine solche Zerlegung eines Problems der Zerlegung eines Programms in Unterprogramme. C bezeichnet diese Unterprogramme grundsatzlich als Funktionen .

Wir haben bereits Funktionen kennengelernt und verwendet, namlich die Bibliotheksfunktionen printf , scanf , isspace , usw. Auch das Hauptprogramm main ist in der Terminologie von C eine Funktion, die vom Betriebssystem beim Start des Programms aufgerufen wird.

## 7.2 Vereinbarung von Funktionen

Die Vereinbarung einer Funktion besteht in C aus zwei Teilen:

- · In einer Deklaration werden die Eigenschaften einer Funktion bekanntgemacht: Name, Parameterliste und Typ des Funktionswerts.
- · In der Definition werden die Operationen festgelegt, Speicherplatz reserviert, usw.

Es ist offensichtlich, dass die Definition einer Funktion ihrer Deklaration entsprechen muss.

Die Funktionsdeklaration hat in ANSI-C die Form

typ name ( typ1 [parameter1] , ..., typN [parameterN] );

und wird als Prototyp bezeichnet.

Fur Funktionsnamen gelten dieselben Regeln wie fur Namen von Variablen und Konstanten. Wenn eine Funktion keine Parameter besitzt, muss dieses durch das Schlusselwort void gekennzeichnet werden.

Beispiel: Wir wollen eine Funktion schreiben, die die Potenz x y einer double -Zahl x und einer ganzen Zahl y berechnet ( y ≥ 0). Der Prototyp kann dann die Form

```
double potenz (double basis, int exponent); oder double potenz (double , int);
```

haben. Obwohl auch die zweite Deklaration den Intentionen von ANSI-C vollstandig entspricht, wie wir noch sehen werden, ist doch die erste Deklaration vorzuziehen, weil sie nicht nur die Typen der Parameter, sondern durch die Wahl der Namen auch deren Bedeutung beschreibt.

In der Definition einer Funktion werden die Operationen festgelegt, die beim Aufruf der Funktion durchzufuhren sind. Die Funktionsdefinition hat die Form

```
typ name ( typ1 parameter1 , ..., typN parameterN ) { lokale deklarationen anweisungsfolge }
```

Man beachte: In der Definition einer Funktion wird der Funktionsheader nicht wie in der Deklaration durch ein Semikolon abgeschlossen!

Als erstes Beispiel realisieren wir die bereits angesprochene Funktion potenz :

```
double potenz(double basis, int exponent) { double pot = 1; for (; exponent > 0; exponent --) pot *= basis; return pot; }
```

Als weiteres Beispiel betrachten wir eine Funktion strlen , die die Lange eines String bestimmt, ohne das abschließende Null-Zeichen mitzuzahlen:

```
int strlen(char s[]) { int i; for (i = 0; s[i] != '\0'; i++) ; return i; }
```

Dabei haben wir benutzt, dass sich die Lange des ubergebenen Strings aus seinem Inhalt ergibt: Das Null-Zeichen zeigt das Ende an. Im allgemeinen muss bei Feldern als Funktionsparameter jedoch die Lange des Feldes ubermittelt werden, z.B. durch einen seperaten Parameter.

Zwei Anmerkungen noch zu grundlegenden Formalien:

- · Eine Funktionsdefinition darf nicht innerhalb einer anderen Funktionsdefinition stehen, d.h. C erlaubt keine Schachtelung von Funktionsdefinitionen. Fur Funktionsaufrufe gilt das nicht, wie wir bereits gesehen haben: Funktionen konnen ohne weiteres andere Funktionen aufrufen.
- · Deklarationen, die innerhalb eines Funktionsrumpfes vereinbarten werden, (z.B. in den beiden Beispielen jeweils die Variable i ) sind in der Regel lokal, d.h. sie sind nur innerhalb der jeweiligen Funktion bekannt. Dass diese Einschrankung außerst sinnvoll ist, werden wir spater noch im einzelnen sehen.

## 7.3 Funktionswerte

Welchen Funktionswert eine Funktion an die rufende Funktion zuruckliefert, wird durch die return -Anweisung

```
return [ausdruck] ;
```

festgelegt. Stimmt der Typ des Ausdrucks ausdruck nicht mit dem Typ der Funktion uberein, erfolgt eine Typumwandlung wie bei einer Wertzuweisung.

Wie bereits erwahnt, ist die pauschale Bezeichnung ' Funktion' fur alle Unterprogramme eigentlich ' Etikettenschwindel' - eine Funktion braucht namlich durchaus keinen Funktionswert zuruckzuliefern! Dieses kennzeichnet man in Deklaration und Definition, indem man als Typ des Funktionswertes das Schlusselwort void angibt. Außerdem entfallt in der return -Anweisung der Ausdruck; eine return -Anweisung ohne Ausdruck direkt vor der schließenden Klammer des Funktionsrumpfes kann man sogar ganz weglassen, da die Kontrolle bei ihrem Erreichen auf jeden Fall an die aufrufende Funktion zuruckgeht.

Ein triviales Beispiel fur eine Funktion, die weder einen Parameter besitzt noch einen Funktionswert liefert, ist die ' leere' Funktion

```
void nichts\_tun(void) {
```

```
return; }
```

Ein ahnlich triviales Beispiel ist eine Funktion, die ein mehrfaches Piepen bewirkt (falls das Terminal dazu imstande ist). Sie hat als Parameter die Anzahl der Piep's und liefert ebenfalls keinen Funktionswert:

```
void piepen(int anzahl) { while (anzahl --) putchar ('\a'); }
```

Gibt eine Funktion, deren Funktionswert nicht den Typ void besitzt, keinen Funktionswert zuruck, weil die return -Anweisung oder auch nur der Ausdruck hinter return fehlt, so ist das in der Regel ein schwerer Fehler . Allerdings: Der Standard schreibt nicht vor, wie ein Compiler hierauf zu reagieren hat.

Faktisch ist die Angabe des Typs einer Funktion in Deklaration und Definition optional: Bei jeder Funktion, bei der die explizite Angabe des Typs fehlt, nimmt der Compiler den Typ int an! Der Hintergrund ist, dass man bei Compilern (und nicht nur bei ihnen) nach Moglichkeit versucht, Aufwartskompatibilitat zu wahren, d.h. ein Compiler nach neuem Standard soll auch Programme nach altem Standard ubersetzen, ohne dass Anderungen erforderlich werden. Leider konnen durch dieses Prinzip alle Absicherungen, die der ANSIStandard vorsieht, unterlaufen werden. Programmierer - gerade Programmieranfanger sind gut beraten, sich strikt an die Vorgaben des ANSI-Standards in strengster Auslegung zu halten. Moderne Compiler unterstutzen dies durch entsprechende Optionen. Ein solches Vorgehen sichert Portabilitat und hilft enorm bei der Fehlersuche.

## 7.4 Aufruf von Funktionen

Der Aufruf einer Funktion besteht aus dem Namen der Funktion, dem, in runde Klammern eingeschlossen, die Liste der Funktionsargumente folgt. Das sind die Werte, die die Funktion wahrend ihrer Ausfuhrung als Parameter haben soll.

Funktionsaufrufe kennen wir bereits aus dem ersten Programmbeispiel. Unsere Funktionsbeispiele aus diesem Abschnitt konnten wir etwa durch

```
i = potenz(2.0, 5); j = strlen("Wie lang ist dieser String?"); nichts\_tun();
```

aufrufen. Durch ihren Aufruf geht die Kontrolle auf die Funktion uber, bis diese eine weitere Funktion aufruft oder die Kontrolle an die rufende Funktion zuruckgibt.

Zulassig, wenn auch sinnlos, waren ebenso die Aufrufe

```
potenz(2.0, 5); strlen("Wie lang ist dieser String?");
```

nicht jedoch

z = nichts\_tun();

Liefert eine Funktion einen Funktionswert, so darf man diesen ignorieren; bei einer Funktion, die keinen Funktionswert liefert, kann man auf einen Funktionswert naturlich auch nicht zugreifen.

## 7.5 Parameter und Argumente

Wir haben bereits gesehen, wie die Kommunikation zwischen rufender und gerufener Funktion erfolgt: In der Definition einer Funktion konnen Parameter (auch: formale Parameter ) definiert werden. Diese Parameter stehen innerhalb der Funktion wie lokale Variablen des entsprechenden Typs zur Verfugung. Welche Werte sie haben, wird beim Aufruf der Funktion durch die Argumente (auch: Aktualargumente genannt) festgelegt.

Die Argumente werden den Parametern linear zugeordnet; die einzelnen Zuordnungen erfolgen wie Wertzuweisungen. Damit sollte offensichtlich sein, dass die Anzahl der Argumente mit der Anzahl der Parameter ubereinstimmen muss und dass die Typen der Argumente ggf. wie bei einer Wertzuweisung in die Typen der Parameter umgewandelt werden. Die eventuellen Typumwandlungen schreibt der ANSI-Standard vor.

Betrachten wir unter diesem Aspekt noch einmal den Funktionsheader der Funktion potenz von oben

double potenz(double basis, int exponent);

und ihren Aufruf

potenz(a, j)

Die Funktion potenz hat die Parameter basis und exponent . Beim Aufruf wird basis der Wert von a und exponent der Wert von j zugewiesen.

Die Parameter einer Funktion entsprechen lokalen Variablen des jeweiligen Typs, in die beim Aufruf die Werte der Argumente kopiert werden. Man bezeichnet das als ' call by value '. Die Konsequenzen mussen wir uns noch einmal klar machen: Eine Veranderung eines Parameters innerhalb der Funktion hat keinerlei Auswirkungen auf die Umwelt der Funktion! Wir haben dieses im Zusammenhang mit der Funktion potenz bereits doppelt genutzt:

- · Die Funktion verwendet den Parameter exponent als Schleifenzahler und verandert ihn dabei. Das hat, wenn wir die Funktion durch

potenz (a, j)

aufrufen, aber keinerlei Folgen fur die Variable j der rufenden Funktion, weil ja nur eine Kopie des Wertes von j an potenz ubergeben wird.

- · Der Aufruf

## i = potenz(2.0, 5);

ist nur deshalb zulassig, weil die Funktion nicht mit den Argumenten selbst arbeitet, sondern mit lokalen Variablen, in die die Werte der Argumente kopiert werden. Wurde die Funktion mit den Argumenten selbst arbeiten, ware der Aufruf unzulassig, weil das zweite Argument, das in der Funktion verandert wird, als Konstante keine Adresse besitzt.

Nicht in jedem Falle ist es zweckmaßig und wunschenswert, dass Funktionen ihre Parameter nicht verandern konnen. Mit der Funktion scanf kennen wir auch bereits ein Beispiel fur eine solche Funktion: Sie soll ja gerade in den Variablen, die als Argumente angegeben werden, die gelesenen Werte speichern! Entsprechend mussen in solchen Fallen die Adressen der Argumente anstelle ihrer Werte ubergeben werden. Wir haben auch bereits gesehen, wie man genau das mit dem Adressoperator & erreichen kann.

Ubergabe von Adressen bezeichnet man allgemein als ' call by reference '. Von C wird behauptet, dass es nur ' call by value' kenne, nicht jedoch ' call by reference'. Der Hintergrund ist ein kleiner sprachlicher ' Klimmzug': Schreiben wir fur eine int -Variable etwa

scanf("%d", &i)

so betrachtet C &i nicht als ' Adresse der Variablen i ', sondern als ' Ausdruck mit einem Zeigertyp' - und was dann ubergeben wird, ist eben gerade der Wert dieses Ausdrucks.

Auf die Zeigertypen und Zeiger kann an dieser Stelle noch nicht im einzelnen eingegangen werden. Zunachst nur ein Hinweis: Es reicht naturlich nicht aus, einen Zeiger an eine Funktion zu ubergeben, um ihr die Veranderung ihrer Parameter zu ermoglichen. Auch die Vereinbarung der Parameter und der Zugriff auf sie mussen entsprechend formuliert sein. Wir werden darauf spater noch ausfuhrlich zuruckkommen.

## 7.6 Felder als Parameter

Felder nehmen als Parameter (und Argumente) eine Sonderstellung ein. In der Terminologie von C gilt: Der Name eines Feldes ist eine Zeigerkonstante, deren Wert die Adresse der ersten Komponente des Feldes ist.

Die Konsequenz ist, dass bei Feldern nie eine Kopie der Werte der Komponenten an eine Funktion ubergeben wird, sondern stets nur die (Anfangs-)Adresse des Feldes. Sieht man also bei einer Funktion ein Feld als Parameter vor, so muss man darauf achten, dass man nicht unerwunschte Nebeneffekte durch die Veranderung von Feldkomponenten erzeugt.

Als Beispiel fur eine Funktion mit einem Feld als Parameter haben wir bereits die Funktion strlen betrachtet. Sie greift zwar auf die Komponenten ihres Parameters zu, verandert sie aber nicht; Nebeneffekte treten also nicht auf.

Als weiteres Beispiel wollen wir jetzt eine Funktion betrachten, die einen String invertiert. Die Anweisungsfolge, die diese Aufgabe lost, haben wir bereits betrachtet. Jetzt wollen wir sie als Funktion formulieren. Die Funktion strlen werden wir verwenden, um die Lange des String zu bestimmen. Außerdem ist ein Rahmenprogramm zum Lesen und Schreiben der Strings angeben.

```
#include <stdio.h> #define LAENGE 20 /** Prototypen *******************************************/
```

```
void invert(char str[]); int strlen(char str[]); /*= Rahmenprogramm ========================================*/ int main(void) { char string[LAENGE + 1]; int anzahl; printf("String eingeben (max. %d Zeichen):\n", LAENGE); scanf("%s", string); invert(string); printf("Der invertierte String ist \'%s\'\n", string); return 0; } /*= Funktionen ============================================*/ /*- Invertieren eines String ------------------------------*/ void invert(char str[]) { int i, j, n; char c; n = strlen(str); for (i = 0, j = n - 1; i < j; i++, j--) c = str[i], str[i] = str[j], str[j] = c; } /*- Bestimmung der Laenge eines String --------------------*/ int strlen(char str[]) { int i = 0; while (str[i] != '\0') i++; return i; }
```

Quelltext 7.1: Invertieren eines Strings

Einige Anmerkungen dazu:

- · Das Rahmenprogramm ' verlasst' sich darauf, dass der Benutzer keinen zu langen String eingibt; dieser String darf keine ' white spaces' enthalten.
- · Das Hauptprogramm ist wie ublich als erstes angegeben und erst danach die Funktionen.
- · Die Funktionsdeklarationen von invert und strlen stehen vor dem Hauptprogramm. Auch das ist ublich. Wir hatten auch invert innerhalb des Hauptprogramms und strlen innerhalb von invert deklarieren konnen; das hatte zur Folge gehabt, dass invert nur innerhalb des Hauptprogramms und strlen nur innerhalb von invert zur Verfugung steht.

Ubrigens: Nur Feldnamen werden als Zeigerkonstanten betrachtet; fur Feldkomponenten gilt das nicht. Rufen wir die Funktion potenz etwa durch

a = potenz(t[k], 4);

auf, so wird der Wert von t[k] ubergeben und nicht die Adresse.

## 7.7 Das Attribut const

Wir haben eben gesehen, dass eine Funktion bei einem Feld, das als Argument ubergeben wird, stets den direkten Zugriff auf die Originaldaten hat und diese ggf. verandern kann.

Das ist ziemlich unschon, weil der Programmierer sehr diszipliniert arbeiten muss, damit nicht ungewollte und ungewunschte Veranderungen erfolgen. War Disziplin fruher das einzige Mittel, Nebeneffekte zu verhindern, so gibt der Standard dem Programmierer Unterstutzung: Versieht man einen Parameter mit dem Attribut const , so erzeugt der Compiler bei jeder Zuweisung an den Parameter, bei Feldern auch an eine Komponente, eine Fehlermeldung. Wohlgemerkt: Der Compiler meldet den Fehler nur; er sorgt nicht automatisch dafur, dass eine Kopie angelegt wird.

Bei Parametern ist das Attribut const zunachst nur fur Felder sinnvoll, weil man bei ' einfachen' Variablen ohnehin nur eine Kopie des Wertes erhalt, die man unbesorgt verandern kann. Die Funktion strlen sollte man zum Beispiel so deklarieren:

int strlen(const char str[]);

Hier mag das uberflussig erscheinen, weil man auf den ersten Blick sieht, dass im Rumpf der Funktion nichts ' Boses' passiert. Uberlegen Sie sich aber auch dieses:

- · Bei vielen Funktionen, etwa den Funktionen der Standardbibliothek, kann man sich nur die Deklarationen in einer Headerdatei und ggf. eine zugehorige Beschreibung ansehen, wahrend die Definition nicht zuganglich ist.
- · Je langer eine Funktion ist, desto muhsamer wird die Prufung, ob sie einen Parameter verandert oder nicht.

In beiden Fallen ist es angenehm, schon aus dem Prototyp ablesen zu konnen, ob die Funktion ein ubergebenes Feld unverandert lasst.

Das Attribut const darf man ubrigens auch fur Variablen vergeben. Dann kann es auch fur einfache Variablen sinnvoll sein.

## 7.8 Prototypen

Prototypen, d.h. Funktionsdeklarationen mit Angabe der Parameterliste, haben verschiedene Zwecke:

- · Der Compiler kann prufen, ob Argumente und Parameter einer Funktion ubereinstimmen oder doch zumindest zueinander ' passen', ohne den fur die Funktion auszufuhrenden Code zu kennen. Das ist haufig dann der Fall, wenn die Funktion aus einer Bibliothek stammt, deren Quelltext nicht veroffentlich wurde.
- · Der Compiler kann, soweit erforderlich und moglich, die Typen der Argumente in die Typen der Parameter umwandeln. Die Umwandlung erfolgt, wie bereits angesprochen, nach denselben Regeln wie bei Wertzuweisungen.
- · Der Compiler kann einen Funktionswert bei Bedarf in einen anderen Typ umwandeln.

Es sollte klar sein: Damit die Prufungen und ggf. Umwandlungen ausgefuhrt werden konnen, muss der Prototyp einer Funktion in der Quelldatei vor ihrem ersten Aufruf stehen. Die Definition kann dann an beliebiger anderer Stelle folgen.

## 7.9 Rekursion

C erlaubt Rekursion . Man spricht von

- · direkter Rekursion , wenn eine Funktion sich selbst aufruft, und von
- · indirekter Rekursion , wenn sich zwei oder mehr Funktionen wechselseitig aufrufen.

Rekursion wird in der Mathematik haufig in Definitionen verwendet. Das ' klassische' Beispiel ist die Berechnung der Fakultat n ! einer nichtnegativen ganzen Zahl n :

n ! := { n · ( n -1)! fur n > 0 1 fur n = 0

Mit rekursiven Funktionen lassen sich solche Formeln direkt umsetzen:

```
long int fakultaet(int n) { if (n < 0) /* Fehler */ return 0; if (n == 0) /* Abbruchbedingung */ return 1; return n * fakultaet(n - 1); }
```

Der Programmierer muss dafur sorgen, dass die Rekursion (irgendwann) ' abbricht'. Im Beispiel sorgen die Abbruchbedingung n > 0 und der rekursive Aufruf mit dem um eins verringerten Argument gemeinsam dafur.

Ob man rekursiv formulierte Berechnungen auch rekursiv realisieren sollte, steht auf einem anderen Blatt. Rekursion ist in der Regel ziemlich aufwendig: Die Parameter mussen kopiert werden ( ' call by value'), lokale Variablen mussen bereitgestellt, der Unterprogrammsprung muss ausgefuhrt werden. Man sollte sich deshalb zunachst einmal uberlegen, ob sich eine rekursiv formulierte Aufgabe nicht auch ohne weiteres iterativ , d.h. mit einer Schleife, losen lasst.

Auch unter diesem Aspekt ist die Berechnung der Fakultat einer nichtnegativen ganzen Zahl das ' klassische' Beispiel. Man kann sie namlich durch

n ! = n ∏ i =1 i

definieren und dann wie folgt realisieren.

```
long int fakultaet (int n) { long int fak = 1; if (n < 0) /* Fehler */ return 0; while (n > 1) fak *= n--; return fak; }
```

Ob eine rekursive oder eine nicht-rekursive Realisierung bestimmter Funktionen vorzuziehen ist, hangt sehr vom Einzelfall ab. Immer dann, wenn sich Rekursion, wie bei den Fakultaten, durch eine einfache Schleife oder ein ahnlich einfaches anderes Konstrukt vermeiden lasst, sollte man sie auch vermeiden. Andererseits gibt es Falle, in denen Rekursion

nur mit erheblichen ' Klimmzugen' zu vermeiden ware - und dann sollte man sie auch nutzen.

Die folgenden Beispiele sollten ausreichen, um ein grundlegendes Verstandnis fur rekursive Algorithmen zu bekommen. Eine ausfuhrlichere Behandlung rekursiver Algorithmen und Techniken kann hier nicht erfolgen.

## 7.10 Beispiel: Turme von Hanoi

Nicht in jedem Falle gibt es zu einem rekursiv formulierten Problem so offensichtlich eine iterative Losung wie bei den Fakultaten.

Ein solches Beispiel sind die ' Turme von Hanoi' (Abbildung 7.1): Man hat einen Turm von Scheiben, bei dem jede Scheibe kleiner ist als die, auf der sie liegt. Der Turm soll versetzt werden, wobei zusatzliche Regeln einzuhalten sind:

Abbildung 7.1: Turme von Hanoi

picture-1.png

- · Es darf immer nur die oberste Scheibe eines Turmes bewegt werden.
- · Neben dem Ausgangsturm und dem Zielplatz steht ein dritter Platz zur Ablage von Scheiben zur Verfugung.
- · Jede Scheibe darf nur auf den Boden oder auf eine großere Scheibe gelegt werden.

Nehmen wir einmal an, dass der Turm aus n Scheiben besteht. Die drei Platze wollen wir mit ' O' ( ' Originalplatz'), ' H' ( ' Hilfsplatz') und ' Z' ( ' Zielplatz') bezeichnen. Dann ist die rekursive Losung der Aufgabe trivial:

- 1. Man legt die obersten n -1 Scheiben von ' O' nach ' H'.
- 2. Die unterste Scheibe wird nach ' Z' gelegt.
- 3. Man legt die n -1 Scheiben von ' H' nach ' Z'.

Damit hat man das Problem der n Scheiben auf zwei Probleme mit jeweils n -1 Scheiben zuruckgefuhrt. Diese lost man nach demselben Verfahren, wobei nur die drei Platze ihre Bedeutung wechseln:

- · Im ersten Schritt ist ' H' der ' Zielplatz' fur den Turm aus n -1 Scheiben und ' Z' der ' Hilfsplatz'.
- · Im dritten Schritt ist ' H' der ' Originalplatz' des Turms aus n -1 Scheiben und ' O' der ' Hilfsplatz'.

Dass die Rekursion zum Erfolg fuhrt, ist klar: Bei jedem Rekursionsschritt verringert sich die Hohe des zu verschiebenden Turmes um 1 - und fur einen Turm der Hohe 1 besteht seine Verschiebung einfach in der Verschiebung seiner einen Scheibe.

Ein Programm, das diesen rekursiven Algorithmus rekursiv realisiert, kann so aussehen:

```
#include <stdio.h> /** Prototyp *********************************************/ void hanoi(int hoehe, char von, char nach, char ueber); /*= Rahmenprogramm ========================================*/ int main(void) { int n; printf("Wie hoch ist der Turm? "); scanf("%d", &n); hanoi(n, 'O', 'Z', 'H'); return 0; } /*= rekursives Ausfuehren der Zuege =======================*/ void hanoi(int hoehe, char von, char nach, char ueber) { if (hoehe > 1) hanoi(hoehe - 1, von, ueber, nach); printf("Bewege Scheibe '%d' nach '%c'!\n", hoehe, nach); if (hoehe > 1) hanoi(hoehe - 1, ueber, nach, von); }
```

Quelltext 7.2: Turme von Hanoi rekursiv

An dieser Stelle sei angemerkt, dass es auch fur die Losung dieses Problems einen iterativen Algorithmus gibt.

## 7.11 Beispiel: Quicksort

Die beiden Beispiele fur Rekursion, die wir bislang betrachtet haben, ließen sich auch iterativ losen. Bei den Fakultaten war das sehr einfach, bei den Turmen von Hanoi erforderte es schon langere Uberlegungen.

Es gibt jedoch auch Aufgaben, die sich prinzipiell nur rekursiv losen lassen. Hierzu zahlt ' Quicksort', ein Verfahren zum Sortieren von Vektoren.

Quicksort funktioniert so: Wir wahlen zunachst ein beliebiges Element des Vektors, z.B. das an seinem Anfang stehende. Jetzt vertauschen wir Elemente des Vektors so, dass

- · das ausgewahlte Element an seinen endgultigen Platz kommt, und dass
- · links von ihm nur nicht großere und rechts von ihm nur nicht kleinere stehen.

Damit sind wir in einer ahnlichen Situation wie bei den ' Turmen von Hanoi': Anstelle eines Vektors mit z.B. n Komponenten haben wir jetzt zwar zwei Vektoren zu sortieren - die Gesamtzahl der Komponenten dieser beiden Vektoren ist aber nur n -1. Damit ist jeder der beiden Teilvektoren (echt) kurzer als der Ausgangsvektor und es ist klar, dass der Algorithmus terminiert: Irgendwann im Zuge der Rekursion wird jeder Teilvektor auf die Lange 0 oder 1 reduziert - und ein leerer Vektor ist ebenso sortiert wie ein Vektor mit nur einer Komponente.

Damit erweist sich die rekursive Routine selbst wieder als sehr simpel:

```
void quick(int z[], int von, int bis) { int p; if (von < bis) { p = platz(z, von, bis); quick(z, von, p - 1); quick(z, p + 1, bis); } }
```

Nicht so ohne weiteres hinschreiben kann man die Funktion platz . Wir mussen uns zunachst uberlegen, wie sie arbeiten soll, und tun das anhand eines Beispiels. In der Zahlenfolge

```
2 8 7 5 3 6 4 1
```

soll das erste Element ( 2 ) an seinen endgultigen Platz gebracht werden; dabei sollen die ubrigen Zahlen so vertauscht werden, dass links von der 2 nur nicht großere Zahlen und rechts davon nur nicht kleinere Zahlen stehen. Dazu speichern wir die 2 zunachst in einer Hilfsvariablen:

```
2 -8 7 5 3 6 4 1
```

Dadurch wird die erste Komponente des Vektors frei. Jetzt suchen wir von ganz rechts die erste Zahl, die kleiner als 2 ist, und speichern sie auf den freien Platz um:

2

1

8

7

5

3

6

4

-

Dadurch wird deren alter Platz frei. Jetzt suchen wir, rechts neben der umgespeicherten Zahl beginnend, aufwarts nach der ersten Zahl, die großer als 2 ist, und speichern sie auf den freien Platz um:

```
2 1 -7 5 3 6 4 8
```

Dadurch wird deren alter Platz frei. Jetzt suchen wir wieder, links neben der umgespeicherten Zahl beginnend, abwarts nach der ersten Zahl, die kleiner als 2 ist, und speichern sie auf den freien Platz um. Und diese abwechselnde Suche von rechts und links wiederholen wir, bis sich die Indizes uberschneiden. Dann haben wir den gesuchten Platz gefunden: Wir konnen die herausgenommene Zahl an diesem Platz wieder in den Vektor eintragen und den Index des Platzes als Funktionswert zuruckliefern.

Die Realisierung kann so aussehen:

```
int platz (int z[], int von, int bis) { int h; h = z[von]; while (von < bis) { while (von < bis && z[bis] >= h) bis --; if (von < bis) { z[von] = z[bis]; von++; }
```

```
while (von < bis && z[von] <= h) von++; if (von < bis) { z[bis] = z[von]; bis --; } } z[von] = h; return von; }
```

Was den Quicksort von den Fakultaten und den ' Turmen von Hanoi' unterscheidet, ist die Tatsache, dass Daten gespeichert werden mussen: Haben wir den Ausgangsvektor unterteilt, konnen wir nur einen der beiden Teilvektoren sofort weiter verarbeiten; Anfangsund Endindex des anderen Teilvektors mussen wir speichern. Fur den Teilvektor, den wir sofort weiterverarbeiten, gilt dasselbe: Erneut konnen wir nur einen seiner Teile sofort weiterverarbeiten; Anfangs- und Endindex des anderen Teils mussen wir speichern.

Formulieren wir den Algorithmus rekursiv, so sorgt der Compiler fur die Speicherung der Anfangs- und Endindizes der noch zu sortierenden Teilvektoren. Versuchen wir, den Algorithmus iterativ zu losen, mussen wir selbst fur die Speicherung der Anfangs- und Endindizes der noch zu sortierenden Teilvektoren sorgen. Eine scheinbar iterative Realisierung des Quicksort ist letztlich also nur Simulation von Rekursion - und dafur spricht wenig.

Quicksort ist fur Vektoren ein sehr schnelles Sortierverfahren - sofern die Vektoren nicht schon weitgehend vorsortiert sind. In der hier vorgestellten Variante wird Quicksort fur (auf- oder absteigend) sortierte Vektoren allerdings zum extremen ' Slowsort', weil in jedem Schritt die Ausgangsfolge der Lange m in eine leere Teilfolge und eine Teilfolge mit m -1 Komponenten zerlegt wird. Am schnellsten ist Quicksort dann, wenn in jedem Schritt die Ausgangsfolge in zwei gleich lange Teilfolgen zerlegt wird. Dem kann man Rechnung tragen, indem man nicht jeweils das erste Element der Teilfolge an seinen endgultigen Platz bringt. Denkbar ware, stets das mittlere Element zu nehmen, oder auch von erstem, mittlerem und letztem Element das mit dem in der Mitte liegenden Wert.

Auch bei der rekursiven Funktion kann man noch mancherlei ' optimieren':

- · Von den beiden rekursiven Aufrufen ist der zweite uberflussig und kann ohne weiteres durch eine Schleife ersetzt werden:

```
void quick(int z[], int von, int bis) { int p; while (von < bis) { p = platz(z, von, bis); quick(z, von, p - 1); von = p + 1; } }
```

Der erste rekursive Aufruf lasst sich dagegen nicht ohne weiteres ersetzen, weil die Rekursion gerade dafur sorgt, dass die Werte von p und bis (automatisch) gesichert werden.

- · Die maximale Rekursionstiefe kann im ' worst case' (in jedem Schritt Abspalten nur eines Elements) bei n zu sortierenden Zahlen n -1 erreichen. Das kann man verhindern, indem man jeweils zunachst die kurzere Teilfolge durch Rekursion, danach die

langere Teilfolge durch Iteration sortiert:

```
void quick(int z[], int von, int bis) { int p; while (von < bis) { p = platz(z, von, bis); if (p - von < bis - p) { quick(z, von, p - 1); von = p + 1; } else { quick(z, p + 1, bis); bis = p - 1; } } }
```

Jetzt kann die Rekursionstiefe bei zunachst n Zahlen nur noch maximal log 2 n erreichen.

- · Die Funktion lasst sich auch mit nur zwei Parametern formulieren, wenn man nicht mit den Anfangs- und Endindizes, sondern mit Zeigern auf die entsprechenden Komponenten arbeitet. Hierfur fehlen uns derzeit aber noch die Mittel.

Wir haben jetzt drei Beispiele fur Rekursion betrachtet:

- · Bei den Fakultaten haben wir gesehen, dass Rekursion wenig sinnvoll ist.
- · Bei den ' Turmen von Hanoi' gibt es zwar eine nichtrekursive Losung. Ob diese aber effizienter als die rekursive Losung ist, musste man erst genauer untersuchen.
- · Beim Quicksort ist jede scheinbar iterative Losung tatsachlich nur Simulation von Rekursion.

## 7.12 Beispiel: Potenzen

Die bisherige Implementierung der Potenzfunktion lasst sich noch weiter optimieren. Dazu verwendet man die Binardarstellung des Exponenten.

x 109 d = x 1101101 b = x 1 · 64 · x 1 · 32 · x 0 · 16 ︸︷︷︸ =1 · x 1 · 8 · x 1 · 4 · x 0 · 2 ︸︷︷︸ =1 · x 1 · 1

Man berechnet also iterativ die Potenzen x (2 k ) , k = 0 , 1 , . . . und entscheidet in jedem Schritt, ob der Faktor am Ergebnis beteiligt ist. Das erreicht man mit dem ModuloOperator. Anschließend wird der Exponent durch zwei geteilt, um im nachsten Schritt das nachste Bit ermitteln zu konnen - Division mit zwei entspricht dem Schieben der Bits um eine Stelle nach rechts.

```
double potenz(double basis, unsigned exponent) { double p = 1; while (exponent != 0) { if (exponent % 2) p *= basis; exponent /= 2; basis *= basis; } return p; }
```

Diese iterative Losung kommt mit maximal log 2 (exponent) Schritten aus. Das ist ein enormer Gewinn gegenuber linearem Aufwand.