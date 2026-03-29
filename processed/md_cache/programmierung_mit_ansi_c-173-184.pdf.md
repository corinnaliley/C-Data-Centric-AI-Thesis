## Kapitel 16

## Ein-/Ausgabe

## 16.1 Verarbeitung von Dateien

Langst nicht in jedem Falle kommt man mit Standardein- und -ausgabe aus, auch nicht unter Berucksichtigung der Moglichkeit, beide umzuleiten.

Ein Beispiel: Ein Programm soll zwei in sich sortierte Dateien ' mischen', d.h. es soll die beiden Dateien parallel lesen und ihre Inhalte sortiert in eine dritte Datei schreiben. Dieses lasst sich prinzipiell mit Umleitung der Standardeingabe nicht realisieren, weil Umleitung immer voraussetzt, dass man die Eingabe aus einer einzigen Datei liest.

Abhilfe schafft die Moglichkeit, direkt auf Dateien zuzugreifen. Bevor man aber direkt auf eine Datei zugreifen kann, muss man eine Vorarbeit vornehmen: Dateien werden ja vom Betriebssystem verwaltet; zu ihrer Identifikation dienen Namen. Diese Namen kann man in einem C-Programm fur die eigentlichen Zugriffe nicht verwenden, sondern nur im Zuge der Vorarbeit, namlich durch Zuordnung des (externen) Namens der Datei zu einer (programminternen) Dateivariablen .

Fur diese Zuordnung stellt stdio.h die Funktion

```
FILE *fopen (const char *dateiname , const char *zugriff);
```

## zur Verfugung:

- · Der erste Parameter ist der Zeiger auf den String, der den externen Namen der Datei enthalt.
- · Der zweite Parameter ist der Zeiger auf einen String, der die gewunschte Art des Zugriffs beschreibt. Eine Ubersicht uber die Optionen ist in Tabelle 16.1 aufgelistet.
- · Der Funktionswert ist der Zeiger auf eine Dateivariable, falls die Zuordnung vorgenommen werden konnte, oder der Nullzeiger. Der Typ FILE ist ebenfalls in stdio.h deklariert.

Die Zeiger, die fopen liefert, sind ausschließlich zur Weitergabe an die anderen Funktionen bestimmt, die Dateien bearbeiten. Der Standard legt auch keinerlei Einzelheiten des Aussehens des Typs FILE fest; in der Regel wird es sich um einen Strukturtyp handeln, der aber je nach Implementation vollig unterschiedlich aussehen kann.

Das Pendent zu fopen ist die Funktion

```
int fclose (FILE *datei);
```

Tabelle 16.1: Optionen zum Offnen von Dateien mit fopen

| Option   | Beschreibung                                                                        |
|----------|-------------------------------------------------------------------------------------|
| r        | Datei lesen; die Datei muss bereits existieren                                      |
| w        | Datei schreiben; falls die Datei existiert, wird ihr Inhalt uberschrieben           |
| a        | Datei fortsetzen; erstellt Datei, falls sie nicht existiert                         |
| r+       | Datei lesen und schreiben; die Datei muss bereits existieren                        |
| w+       | Datei lesen und schreiben; falls die Datei existiert, wird ihr Inhalt uberschrieben |
| a+       | Datei lesen und fortsetzen; erstellt Datei, falls sie nicht existiert               |

Sie lost die Zuordnung fur die ubergebene Dateivariable und meldet mit dem Funktionswert Null bzw. EOF ihren Erfolg bzw. Misserfolg.

Lesen und schreiben konnen wir jetzt nicht mehr mit scanf , getchar , printf und putchar , weil wir naturlich die betroffene Datei zusatzlich nennen mussen. Die entsprechenden Funktionen

```
int fscanf(FILE *datei, const char *format , ...); int fgetc(FILE *datei); int fprintf(FILE *datei, const char *format , ...); int fputc(int c, FILE *datei);
```

arbeiten aber letztlich genauso wie die bekannten Funktionen, nur dass sie eben gerade auf die angegebene Datei anstelle der Standardein- bzw. -ausgabe zugreifen.

Als Beispiel wird die Konkatenation von zwei Dateien realisiert:

```
#include <stdio.h> /** Prototypen *******************************************/ static FILE *zugeordnete\_datei(const char *frage, const char *zugriff); static void datei\_kopieren(FILE *ziel, FILE *quelle); /*= Hauptprogramm =========================================*/ int main(void) { FILE *quelle , *ziel; ziel = zugeordnete\_datei("Zieldatei: ", "w"); if (ziel == NULL) { printf("Zieldatei nicht verfuegbar -- stop\n"); return 1; } quelle = zugeordnete\_datei("1. Quelldatei: ", "r"); if (quelle == NULL) { printf("1. Quelldatei nicht verfuegbar -- stop\n"); return 2; } datei\_kopieren(ziel, quelle); fclose(quelle); quelle = zugeordnete\_datei("2. Quelldatei: ", "r");
```

```
if (quelle == NULL) { printf("2. Quelldatei nicht verfuegbar -- stop\n"); return 3; } datei\_kopieren(ziel, quelle); fclose(quelle); fclose(ziel); return 0; } /*= Zuordnung einer Datei (mit Abfrage ihres Namens) ======*/ static FILE *zugeordnete\_datei(const char *frage, const char *zugriff) { char name[FILENAME\_MAX]; int i; FILE *datei; printf("%s", frage); i = 0; while ((i < FILENAME\_MAX) && ((name[i] = getchar()) != '\n')) i++; if (i >= FILENAME\_MAX) i--; if (name[i] != '\n') while (getchar() != '\n') ; name[i] = '\0'; datei = fopen(name, zugriff); return datei; } /*= Kopieren einer Datei (zeichenweise) ===================*/ static void datei\_kopieren(FILE *ziel, FILE *quelle) { int c; while ((c = fgetc(quelle)) != EOF) fputc (c, ziel); }
```

Quelltext 16.1: Dateiverarbeitung: Konkatenation

## 16.2 Formatierte und binare Ein-/Ausgabe

Wie schon erwahnt, muss man die Ein-/Ausgabe, die wir bislang verwendet haben, genauer als ' formatierte Ein-/Ausgabe' bezeichnen. Im Zuge der Ubertragung erfolgt in der Regel eine Umwandlung der Darstellung:

- · Bei der Eingabe mussen die Zeichen interpretiert werden, um herauszufinden, wo ein Eingabewert anfangt und wo er aufhort. Bei numerischen Werten muss dann die Zeichenfolge in die interne, binare Darstellung des Wertes umgewandelt werden.
- · Bei der Ausgabe numerischer Werte muss die interne, binare Darstellung in eine Zeichenfolge umgewandelt werden.

Das Pendent zur formatierten Ein-/Ausgabe ist die binare ( unformatierte ) Ein-/Ausgabe: Bei ihr werden die Bitfolgen der Werte im Zuge der Ubertragung nicht verandert.

Binare Ein-/Ausgabe hat einen wesentlichen Vorteil: Sie ist in der Regel sehr viel schneller als formatierte Ein-/Ausgabe. Das ist auch ohne weiteres einsichtig: Die Umwandlungen zwischen interner Darstellung und Zeichendarstellung erfordern eine Vielzahl von arithmetischen Operationen; wir haben das in einem Beispiel fur eine ganze Zahl bereits einmal gesehen. Spart man diese Operationen ein, muss das die Ubertragung beschleunigen.

Andererseits lasst sich binare Ein-/Ausgabe aus zwei Grunden nur eingeschrankt einsetzen:

- · Nicht jedes Ein-/Ausgabegerat erlaubt binare Ein-/Ausgabe! Eine Tastatur kann zum Beispiel nur Zeichen liefern; ein Bildschirm oder Drucker kann mit binaren Darstellungen nichts anfangen. Bei all diesen Geraten ist man also auf formatierte Ein-/Ausgabe angewiesen.
- · Binardateien sind in der Regel nicht portabel: Ein int -Wert zum Beispiel benotigt in der Datei wie im Speicher des Rechners 2 oder 4 Bytes (oder was auch immer); auf einem Rechner, der int -Werte anders darstellt, kann die Binardatei ohne weiteres also nicht gelesen werden. Formatierte Dateien sind zwar auch nicht ohne weiteres portabel, weil die Zeichencodes auf verschiedenen Rechern verschieden sein konnen. Die Umsetzung von Zeichencodes ist jedoch extrem simpel, verglichen mit der Umsetzung der internen Darstellungen numerischer Werte.

Anders formuliert: Bei formatierten Dateien hat man immer eine implizite Interpretationsvorschrift, namlich Interpretation als Zeichen; bei Binardateien fehlt diese Vorschrift.

Unter UNIX ist es deshalb ublich, weitestgehend formatierte Ein-/Ausgabe und entsprechend formatierte Dateien zu verwenden. Auf die beiden Funktionen fread und fwrite , mit denen binare Ein-/Ausgabe moglich ist, wird deshalb auch nicht naher eingegangen.

Die wesentlichsten Funktionen zur formatierten Ein-/Ausgabe kennen wir bereits seit langerem; was nachzutragen bleibt, sind die vielfaltigen Moglichkeiten, Einfluss auf die Form der Umwandlung zu nehmen.

## 16.3 Ausgabeformate

Die Formatbeschreiber fur die Ausgabe haben die allgemeine Form

%< modus >< laenge ><. stellen >< typ > kennung

Wir sehen: Außer dem Prozentzeichen am Anfang und dem Kennbuchstaben kennung am Ende sind alle Eintrage optional.

Der Formatierungsstring und die Liste der Ausgabewerte werden linear abgearbeitet. Die Abarbeitung beginnt mit der Interpretation des Formatierungsstring. Was weiter passiert, hangt von den dabei gefundenen Zeichen ab:

- · Wenn im Formatierungsstring ein Prozentzeichen gefunden wird, wird zunachst der vollstandige Formatbeschreiber interpretiert. Dann wird der nachste Ausgabewert ihm entsprechend in eine Zeichenfolge umgewandelt und in die Ausgabedatei ubertragen.
- · Wenn im Formatierungsstring ein anderes Zeichen gefunden wird, wird es ohne weiteres in die Ausgabedatei ubertragen.

Die Kennungen fur die verschiedenen Datentypen bzw. ihre externen Darstellungen, die weitgehend am Anfang des Kurses bereits aufgezahlt wurden, lassen sich in vier Gruppen unterteilen:

- 1. Ausgabe ganzer Zahlen

Der Ausgabewert muss den Typ int bzw. unsigned int besitzen. Die zu erzeugende externe Darstellung wird durch die folgenden Kennbuchstaben beschrieben:

- i der Wert wird als signed int betrachtet, die Darstellung erfolgt dezimal, ggf. mit Vorzeichen
- d wie i
- u der Wert wird als unsigned int betrachtet, die Darstellung erfolgt dezimal
- o der Wert wird als unsigned int betrachtet, die Darstellung erfolgt oktal
- x der Wert wird als unsigned int betrachtet, die Darstellung erfolgt hexadezimal unter Verwendung von Kleinbuchstaben
- X wie x , jedoch mit Großbuchstaben
- 2. Ausgabe von Gleitkommazahlen

Der Ausgabewert wird als double erwartet. Die zu erzeugende externe Darstellung wird durch die folgenden Kennbuchstaben beschrieben:

- f Darstellung ohne Exponententeil
- e Darstellung mit Exponententeil, der Exponenten-Kennbuchstabe ist e ; die Darstellung wird so normiert, dass links vom Dezimalpunkt genau eine Ziffer steht, die nur dann Null ist, wenn der Wert insgesamt Null ist
- E wie e , jedoch mit Exponenten-Kennbuchstabe E
- g wie f oder e , je nach Großenordnung des Ausgabewertes; Nullen am Ende der Ziffernfolge werden unterdruckt; der Dezimalpunkt wird nur geschrieben, wenn ihm eine Ziffer folgt
- G wie g , jedoch wird ggf. E anstelle von e verwendet

Die letzte Ziffer wird jeweils gerundet.

- 3. Ausgabe von Zeichen und Strings
- s der Ausgabeparameter wird als Zeiger auf einen String betrachtet, der Wert des String geschrieben
- c der int -Wert wird in unsigned char umgewandelt geschrieben
- 4. Kennungen fur verschiedene Zwecke
- p der Wert wird als Zeiger betrachtet und in implementations-spezifischer Darstellung geschrieben
- n es wird keine Ausgabe erzeugt, sondern die Anzahl der bislang ubertragenen Zeichen in den nachsten Parameter der Ausgabeliste geschrieben; dieser Parameter muss entsprechend den Typ int * besitzen
- % ein Prozentzeichen wird geschrieben (dem Formatbeschreiber wird kein Ausgabewert zugeordnet)

Wenn in einem Formatbeschreiber nur die Kennung kennung angegeben ist, werden Werte mit bestimmten Typen erwartet, erfolgt die Darstellung in einem Standardformat. Zum Beispiel wird bei Verwendung des Formatbeschreibers u ein unsigned int -Wert erwartet. Auch werden bei der Umwandlung nur die signifikanten Ziffern des Wertes erzeugt. Abweichende Werte und Darstellungen lassen sich mit den optionalen Eintragen der Formatbeschreiber anzeigen bzw. erzeugen.

Der Eintrag laenge legt die Mindestzahl der zu erzeugenden Zeichen fest, die ggf. durch voran- oder nachgestellte Leerzeichen zu erreichen ist. Falls bei der Umwandlung des Wertes mehr Zeichen entstehen, wird die Angabe ignoriert. laenge kann eine dezimale Konstante oder ein Stern sein; wenn ein Stern angegeben ist, wird der nachste Wert der Ausgabeliste als Wert von laenge genommen und nicht geschrieben. Dieser Wert muss den Typ int besitzen.

Negative Langen sind nicht moglich (abgesehen davon, dass sie auch nicht sinnvoll sind): Ein Minuszeichen wird als Modifikator betrachtet und bewirkt linksbundige Ausgabe anstelle der sonst rechtsbundigen, so dass fur laenge nur die angegebene Ziffernfolge ubrigbleibt.

Einige Beispiele: Seien x und y durch

```
int x = 743, i = 4; float y = 123.4567; definiert. Dann erhalten wir printf("%d", x); → 743 printf("%2d", x); → 743 printf("%6d", x); → glyph[visiblespace]glyph[visiblespace]glyph[visiblespace]743 printf("%-6d", x); → 743glyph[visiblespace]glyph[visiblespace]glyph[visiblespace] printf("%*d", i, x); → glyph[visiblespace]743 printf("%f", y); → 123.456703 printf("%4f", y); → 123.456703 printf("%s", "Hallo"); → Hallo printf("Hallo"); → Hallo printf("%s", "Hallo%Hallo"); → Hallo%Hallo printf("Hallo%Hallo"); → Fehler! printf("%10s", "Hallo"); → glyph[visiblespace]glyph[visiblespace]glyph[visiblespace]glyph[visiblespace]glyph[visiblespace]Hallo
```

Wie stellen interpretiert wird, hangt in erster Linie von kennung ab. Formal kann stellen wie laenge eine dezimale Konstante oder ein Stern sein; wenn ein Stern angegeben ist, wird der nachste Wert der Ausgabeliste als Wert von stellen genommen und nicht geschrieben. Dieser Wert muss den Typ int besitzen:

- · Bei ganzzahligen Werten ist stellen die Mindestzahl der zu schreibenden Ziffern, auch wenn dadurch fuhrende Nullen erscheinen.
- · Bei den Kennungen f , e und E ist stellen die Anzahl der Stellen hinter dem Dezimalpunkt; wird die Anzahl der Stellen hinter dem Dezimalpunkt auf Null gesetzt, entfallt auch der Dezimalpunkt selbst.
- · Bei den Kennungen g und G wird genauso verfahren; nur wird ggf. bei stellen der Wert 0 durch 1 ersetzt.
- · Bei Strings bewirkt stellen , dass hochstens so viele Zeichen des String ubertragen werden.

Seien x und y wie oben definiert. Dann gilt

printf("%6.4d", x);

→ glyph[visiblespace]glyph[visiblespace]0743

printf("%-6.4d", x);

→ 0743glyph[visiblespace]glyph[visiblespace]

printf("%7.2f", y);

→ glyph[visiblespace]123.46

```
printf("%7.3s", "Hallo"); → glyph[visiblespace]glyph[visiblespace]glyph[visiblespace]glyph[visiblespace]Hal printf("%7.6s", "Hallo"); → glyph[visiblespace]Halloglyph[visiblespace]
```

Dass man Ausgabewerte mit long -Typen und dem Typ long double durch Angabe des Kennbuchstabens l bzw. L fur typ besonders kennzeichnen muss, haben wir bereits gesehen.

Ebenfalls erwahnt wurde bereits das Zeichen -als modus . Ein weiteres Zeichen, das hier zugelassen ist, ist + . Es bewirkt fur vorzeichenbehaftete Zahlen, dass auch positive Vorzeichen geschrieben werden.

Fur weitere Einzelheiten zu den Ausgabeformaten sei auf die Literatur verwiesen.

## 16.4 Eingabeformate

Die Formatbeschreiber fur die Eingabe haben die Form

%<*>< laenge >< typ > kennung

Dabei sind die in spitzen Klammern stehenden Eintrage erneut optional.

Der Formatierungsstring, die Zeichen aus der Eingabedatei und die Liste der Eingabevariablen werden linear abgearbeitet. Die Abarbeitung beginnt mit der Interpretation des Formatierungsstring. Was weiter passiert, hangt von den dabei gefundenen Zeichen ab. Zunachst soll der einfachste Fall unterstellt werden, dass namlich die Formatbeschreiber nur aus dem einleitenden Prozentzeichen und der Kennung kennung bestehen, dass keine optionalen Eintrage enthalten sind:

- · Wenn im Formatierungsstring ein ' white space' gefunden wird, werden so lange Zeichen aus der Eingabedatei geholt, bis das nachste Zeichen kein ' white space' ist. Die ubertragenen ' white spaces' werden ignoriert.
- · Wenn im Formatierungsstring ein Zeichen gefunden wird, das kein Prozentzeichen und kein ' white space' ist, wird es mit dem nachsten Zeichen der Eingabedatei verglichen. Wenn Ubereinstimmung besteht, werden beide Zeichen ignoriert. Sonst werden so lange Zeichen in der Eingabedatei ubersprungen, bis ein ' white space' gefunden wird, dann die Routine mit Fehlerstatus abgebrochen.
- · Wenn im Formatierungsstring ein Prozentzeichen gefunden wird, wird zunachst der vollstandige Formatbeschreiber interpretiert. Dann werden so lange Zeichen aus der Eingabedatei geholt, wie diese zur Kennung kennung des Formatbeschreibers ' passen'. Anschließend wird diese Zeichenfolge in die entsprechende interne Darstellung umgewandelt und das Resultat in der nachsten Eingabevariablen gespeichert.

Die Kennungen fur die verschiedenen Datentypen bzw. ihre externen Darstellungen lassen sich wieder in vier Gruppen unterteilen. Wir kennen sie weitgehend bereits:

## 1. Eingabe ganzer Zahlen

Die Eingabevariable muss den Typ int bzw. unsigned int besitzen. Die erwartete externe Darstellung wird durch die folgenden Kennbuchstaben beschrieben:

- i ganze Zahl mit oder ohne Vorzeichen in C-Schreibweise, d.h. mit 0x oder 0X beginnende Zahlen werden als hexadezimal, andere mit 0 beginnende Zahlen als oktal dargestellt betrachtet; Zahlen, die nicht mit Null beginnen, werden als dezimal dargestellt betrachtet
- d ganze Zahl mit oder ohne Vorzeichen in dezimaler Darstellung
- u ganze Zahl ohne Vorzeichen in dezimaler Darstellung

- o ganze Zahl mit oder ohne Vorzeichen in oktaler Darstellung
- x ganze Zahl mit oder ohne Vorzeichen in hexadezimaler Darstellung, jedoch ohne einleitendes 0x bzw. 0X
- X wie x
- 2. Eingabe von Gleitkommazahlen

Die Eingabevariable muss den Typ float besitzen. Die verfugbaren Kennungen sind die Buchstaben e , E , f , g und G . Sie erwarten samtlich eine beliebige zulassige Darstellung einer Gleitkommazahl, also mit oder ohne Vorzeichen, mit oder ohne Dezimalpunkt, mit oder ohne Exponententeil.

- 3. Eingabe von Zeichen und Strings

Die Eingabevariable muss den Typ char besitzen; in der Regel wird sie die erste Komponente eines Feldes sein mussen, das hinreichend groß ist, alle ubertragenen Zeichen aufzunehmen. Die erwartete externe Darstellung wird durch die folgenden Kennungen beschrieben:

- s beliebige Zeichenfolge, beendet durch ein ' white space'; an die Zeichenfolge wird automatisch ein Null-Zeichen angehangt
- [ wie s , jedoch kann explizit angegeben werden, bei welchen Zeichen die Ubertragung stoppen soll (vgl. unten)
- c einzelnes Zeichen, das auch ein ' white space' sein kann
- 4. Kennungen fur verschiedene Zwecke
- p Erwartet wird ein Zeigerwert in implementations-spezifischer Darstellung; die Eingabevariable muss einen Zeigertyp besitzen. Die Kennung ist, wenn uberhaupt, nur dann sinnvoll, wenn die zu lesende Eingabe unter derselben Implementation geschrieben wurde.
- n Es werden keine Zeichen aus der Eingabedatei geholt, sondern die Anzahl der bisher umgewandelten Werte in die nachste Eingabevariable ubertragen. Diese Eingabevariable muss den Typ int besitzen.
- % Kennung fur ein Prozentzeichen, das als Eingabezeichen erwartet wird.

Die Kennbuchstaben fur numerische Werte mussen durch die Typkennung h , l oder L modifiziert werden, wenn die Eingabevariable nicht den Typ int bzw. float besitzt. Durch laenge kann man angeben, wie viele Zeichen maximal fur den Eingabewert interpretiert werden sollen.

Als Beispiel betrachten wir die Anweisungsfolge

```
int i, anzahl; char c; float f; double d; ...
```

```
anzahl = scanf("%5d %c %f %lf", &i, &c, &f, &d); Dann bewirkt die Eingabezeile 12345Y3.14 2.12
```

die Zuweisungen

```
i = 12345; c = 'Y'; f = 3.14; d = 2.12; anzahl = 4;
```

Durch die Eingabezeilen

```
12345 Y3.14 2.12 12345 Y 3.14 2.12
```

andert sich am Resultat nichts (wegen des Leerzeichens in glyph[visiblespace]%c !!). Schreiben wir dagegen

```
123456Y3.14 2.12
```

so werden die Zuweisungen

```
i = 12345; c = '6';
```

```
anzahl = 2;
```

ausgefuhrt, wahrend die Zuweisungen fur f und d unterbleiben.

Beginnt ein Formatbeschreiber mit einem Stern, so wird er zwar bei der Interpretation der Eingabe ' normal' abgearbeitet - der gelesene Wert wird jedoch nicht in einer Eingabevariablen gespeichert. Auch dafur ein Beispiel:

```
int i, o, anzahl; char c; float f; ... anzahl = scanf("%3d zahl %4o %*d %c %f", &i, &o, &c, &f);
```

```
Mit den Eingabezeilen
```

```
473 zahl1563 567 R2.33E+2 473 zahl1568 567 R2.33E+2 473z ah l1563 567 R2.33E+2
```

erhalten wir jetzt

```
i = 473; i = 473; i = 473; o = 883; o = 110; c = 'R'; c = '5'; f = 233.0; f = 67; anzahl = 4; anzahl = 4; anzahl = 1;
```

Eine interessante Moglichkeit ist, fur Strings die zulassigen oder nicht zulassigen Zeichen explizit anzugeben:

```
[ zeichenfolge ] [^ zeichenfolge ]
```

Wir haben in einem Beispiel einmal mit getchar in einer Schleife dafur gesorgt, dass aus jeder Eingabe nur die Zahl am Anfang interpretiert und der Rest der Eingabezeile ignoriert wurde:

```
scanf("%d", &wert); /* eine Zahl lesen */ while (getchar() != '\n') /* Rest ignorieren */ ;
```

Jetzt konnen wir auch kurzer

```
scanf("%d%*[^\n]", &wert); getchar ();
```

schreiben. Achtung: Das Format %d%*[^\n]%*c bei gleichzeitigem Verzicht auf den Aufruf von getchar ist nicht moglich. Wird fur den Formatbeschreiber %*[^\n] kein zulassiges Zeichen gefunden, so wird die Funktion mit einem Fehler beendet, der Formatbeschreiber %*c also gar nicht mehr bearbeitet. Immer dann, wenn das Zeilenende-Zeichen der Zahl unmittelbar folgt, wurde es also im Puffer stehenbleiben.

## 16.5 Funktionen zur Ein-/Ausgabe

Das Funktionenpaar

```
int scanf(const char *format , ...); int printf(const char *format , ...);
```

kennen wir bereits seit Beginn des Kurses: Es erlaubt den Zugriff auf Standardein- und -ausgabe. Den Zugriff auf beliebige Dateien erlaubt das Funktionenpaar

```
int fscanf(FILE *datei, const char *format , ...); int fprintf(FILE *datei, const char *format , ...);
```

das am Anfang dieses Abschnitts eingefuhrt wurde. scanf und printf dienen ausschließlich der Bequemlichkeit des Programmierers: Der Standard schreibt vor, dass fur die Standardein- und -ausgabe die Namen stdin bzw. stdout vordefiniert sind, so dass man grundsatzlich auch

```
fscanf(stdin , ...); fprintf(stdout , ...)
```

schreiben konnte. (Es gibt ubrigens mit stderr noch eine dritte ' Standarddatei' fur die Ausgabe von Fehlermeldungen. Sie wird bei interaktiven Programmen in der Regel auch dem Bildschirm zugeordnet.)

Es gibt noch ein drittes, in manchen Fallen interessantes Funktionenpaar, namlich

```
int sscanf(const char *s, const char *format , ...); int sprintf(char *s, const char *format , ...);
```

Auch diese Funktionen fuhren Umwandlungen zwischen interner und externer Darstellung durch, nur greifen sie nicht auf eine Datei zu, sondern statt dessen auf den String, der als erster Parameter ubergeben wird. Letztlich werden damit dem Programmierer nur die Umwandlungsroutinen fur seine Zwecke zur Verfugung gestellt, die hinter den Formatbeschreibern stehen.

## 16.6 Vorausschau beim Lesen

Eine weitere Funktion mochte zum Abschluss dieses Abschnitts noch ansprechen, namlich

```
int ungetc(int c, FILE *datei);
```

Dahinter steht: Bei der Interpretation von Eingabe merkt man in der Regel erst ein Zeichen zu spat, dass man die Interpretation schon hatte beenden mussen. Fur solche Falle ist ungetc gedacht: Die Funktion bietet die Moglichkeit, ein Zeichen in die Eingabedatei zuruckzuschreiben ! Liest man die Datei anschließend erneut, so erhalt man das zuruckgeschriebene Zeichen erneut als Eingabe.

Wir sehen uns dafur ein Beispiel an: Eine Eingabezeile soll eine bestimmte Anzahl von Eintragen enthalten, die nacheinander abzuarbeiten sind. Der Benutzer soll nur die ersten

Eintrage angeben mussen; fehlende Angaben sollen durch Standardwerte ersetzt werden. Der Einfachheit halber soll angenommen werden, dass die Eintrage Zeichen sind und dass der Standardwert das Leerzeichen sein soll. Bei der Losung mussen wir darauf achten, dass wir das Zeilenende-Zeichen nicht entfernen, solange noch weitere Eingabezeichen folgen. Realisieren lasst sich das durch die Funktion

```
int naechstes\_zeichen(void) { int c; if ((c = getchar ()) == '\n') { ungetc (c, stdin); c = ' '; } return c; }
```

Erwarten wir etwa 40 Zeichen je Zeile, so konnen wir diese Funktion durch

```
for (i = 0; i < 40; i++) { c = naechstes\_zeichen(); ... } getchar ();
```

nutzen. Der Aufruf von getchar hinter der Schleife sorgt dafur, dass das ZeilenendeZeichen der nun vollstandig abgearbeiteten Eingabezeile aus der Eingabe entfernt wird. Es gibt ubrigens eine Reihe von Restriktionen fur ungetc , auf die hier nicht naher eingegangen werden kann.