## Kapitel 2

## Standarddatentypen, Konstanten und Variablen

## 2.1 Interne Darstellungen

Heutige Computer verfugen uber Schaltelemente, die zwei stabile Zustande annehmen konnen. Identifiziert man diese beiden Zustande mit den Zahlen 0 und 1, so kann man Binarzahlen , d.h. Zahlen im Stellenwertsystem zur Basis 2, in einem Rechner speichern und verarbeiten.

Die Dezimalzahlen , mit denen zu rechnen wir gewohnt sind, lassen sich problemlos und eindeutig auch als Binarzahlen darstellen. Sehen wir uns ein Beispiel dafur an:

```
109 d = 1 · 10 2 +0 · 10 1 +9 · 10 0 = 64 + 32 + 8 + 4 + 1 = 1 · 2 6 +1 · 2 5 +0 · 2 4 +1 · 2 3 +1 · 2 2 +0 · 2 1 +1 · 2 0 = 1101101 b
```

Die dreistellige Dezimalzahl 109 ergibt bereits eine siebenstellige Binarzahl; die dreistellige Dezimalzahl 999 wurde bereits eine zehnstellige Binarzahl ergeben. Da Zahlen mit so vielen Ziffern nur sehr schlecht zu lesen sind, zumal wenn sie wie Binarzahlen nur aus Nullen und Einsen bestehen, sind im Zusammenhang mit Rechnern andere Darstellungen ublich, namlich Oktalzahlen (Basis 8; Ziffern: 0, . . . , 7) und Hexadezimalzahlen (Basis 16; Ziffern: 0, . . . , 9, A , . . . , F ). Die Umwandlung zwischen Binar- und Oktaldarstellung bzw. zwischen Binar- und Hexadezimaldarstellung ist besonders einfach: Jede Oktalziffer entspricht gerade einer Gruppe von 3 Binarziffern, jede Hexadezimalziffer gerade einer Gruppe von 4 Binarziffern. Wir sehen uns auch das an einem Beispiel an:

```
109 d = 1101101 b = 1 b · 8 2 +101 b · 8 1 +101 b · 8 0 = 1 d · 8 2 +5 d · 8 1 +5 d · 8 0 = 155 o 109 d = 1101101 b = 110 b · 16 1 +1101 b · 16 0 = 6 d · 16 1 +13 d · 16 0 = 6 D h
```

Verarbeitet werden ohne weiteres nie einzelne Bits, sondern stets Gruppen. Eine gebrauchliche Gruppe ist das Byte , das aus 8 Bits besteht.

## 2.2 Wertebereiche

Wir haben eben bereits gesehen, wie man Zahlen (genauer: nichtnegative ganze Zahlen) in einem Rechner darstellen kann. Diese Zahlen reichen aber nicht aus: Vielfach mochte man auch Zeichen oder reelle Zahlen verarbeiten. Dem tragen die Standardtypen der Programmiersprachen Rechnung. Letztlich sind sie nur Vorschriften, Bitfolgen bestimmter Lange in bestimmter Weise zu interpretieren.

Die Standardtypen, die C kennt, werden uns in den nachsten Abschnitten beschaftigen. Ein generelles Problem dabei ist, dass auf der einen Seite der Wertebereich eines Zahlentyps direkt von der Anzahl der Bits abhangt, die fur ihn verwendet werden, dass auf der anderen Seite C aber unabhangig von bestimmter Hardware definiert werden sollte.

Wir sehen uns dafur ein Beispiel an: Die am weitesten verbreitete Maßeinheit ist das bereits angesprochene Byte. In ihm kann man die Zahlen 00000000 b = 0 d bis 11111111 b = 255 d speichern - ein fur die Praxis viel zu kleiner Wertebereich. Zwei Bytes ergaben den Wertebereich 0 bis 65535 - auch noch nicht ubermaßig viel.

Will man neben den positiven auch negative Zahlen darstellen, so benotigt man ein Bit fur das Vorzeichen und erhalt dann fur Bytes den Wertebereich -127 (bzw. -128) bis +127 bzw. fur zwei Bytes den Wertebereich -32767 (bzw. -32768) bis +32767.

Man hatte nun bei der Definition von C sagen konnen: In den Programmen konnen ganzzahlige Werte mit 1, 2 oder 4 Bytes verarbeitet werden. Das ware aber keine zweckmaßige Definition gewesen, da sie eine optimale Implementation auf vielen Rechnern verhindert hatte:

- · Nicht jeder Rechner kennt Bytes - viele Großrechner haben eine Wortstruktur , wobei jedes Wort aus 64 oder mehr Bits besteht, und konnen auf kurzere Bitfolgen gar nicht ohne weiteres zugreifen.
- · Auch bei manchem Rechner, der Bytes kennt, ist es fur das Rechnen in landlaufigem Sinne gunstiger, wenn statt einzelner Bytes Gruppen von zwei oder mehr Bytes verwendet werden.

Der ANSI-Standard fur C tragt dem Rechnung, indem er keine festen Wertebereiche, sondern nur Mindestschranken fur die Wertebereiche vorschreibt, und indem er außerdem vorschreibt, dass fur die verschiedenen Typen bestimmte benannte Konstanten in bestimmten Standard-Headerdateien verfugbar sein mussen, die die konkreten, implementationsspezifischen Werte wiedergeben. Diese Headerdateien sind limits.h fur die Wertebereiche der ganzzahligen Typen und float.h fur die Gleitkommatypen.

## 2.3 Ganzzahlige Typen

Beginnen wir nun konkret mit dem Typ, der bislang exemplarisch behandelt wurde, namlich dem Typ fur die Beschreibung ganzer Zahlen ( integer ). Dieser Typ wird in C mit dem Schlusselwort int bezeichnet.

Genau genommen bezeichnet int eine Gruppe von Typen , wie es unsere Voruberlegungen auch bereits nahelegen:

- · Neben int selbst gibt es short int (oder kurz: short ) mit moglicherweise kleinerem Wertebereich und long int (oder kurz: long ) mit moglicherweise großerem Wertebereich.

- · Man hat fur alle drei Wertebereiche die Wahl zwischen vorzeichenbehafteten (Schlusselwort signed ) und vorzeichenlosen (Schlusselwort unsigned ) Zahlen. Gibt man keines der beiden Schlusselworte an, werden die Zahlen als vorzeichenbehaftet betrachtet.

In Tabelle 2.1 finden Sie die moglichen, alternativen Bezeichnungen fur die verschiedenen Ganzzahl-Typen und die Mindestschranken, die der Standard fur sie vorschreibt.Tabelle 2.1: Vorgeschriebene Wertebereiche fur Ganzahltypen

| Typ                                     | Minimum        | Maximum      |
|-----------------------------------------|----------------|--------------|
| signed char                             | ≤ - 127        | ≥ 127        |
| unsigned char                           | = 0            | ≥ 255        |
| signed short int signed short short int | ≤ - 32767      | ≥ 32767      |
| short unsigned short int unsigned short | = 0            | ≥ 65535      |
| signed int signed int                   | ≤ - 32767      | ≥ 32767      |
| unsigned int unsigned                   | = 0            | ≥ 65535      |
| signed long int signed long long int    | ≤ - 2147483647 | ≥ 2147483647 |
| unsigned long int unsigned long         | = 0            | ≥ 4294967295 |

Die im Standard festgelegten Namen der Schranken-Konstanten in limits.h sind

- · SHRT MIN , SHRT MAX und USHRT MAX fur die short -Typen,
- · INT MIN , INT MAX und UINT MAX fur die int -Typen und
- · LONG MIN , LONG MAX und ULONG MAX fur die long -Typen.

Im Quellcode kann man Konstanten mit ganzzahligen Typen wahlweise dezimal, oktal oder hexadezimal schreiben:

- · Dezimale Konstanten beginnen mit einer Ziffer ungleich 0.
- · Oktale Konstanten beginnen mit einer 0.
- · Hexadezimale Konstanten beginnen mit 0x oder 0X ; dieser Kennung muss mindestens eine hexadezimale Ziffer folgen.

Die Dezimalzahl 109, fur die wir oben die Umwandlung betrachtet haben, konnen wir in einem Programm also wahlweise so schreiben:

109

dezimal

0155

oktal

0x6D

hexadezimal

0X6D

hexadezimal

Eine dezimal geschriebene Konstante erhalt den ersten moglichen Typ aus int , long und unsigned long ; eine oktal oder hexadezimal geschriebene Konstante erhalt den ersten

moglichen Typ aus int , unsigned int und unsigned long . Der Programmierer kann den Typ aber auch explizit festlegen, indem er einer Konstanten die Buchstaben u oder U fur unsigned -Typen und/oder l oder L fur long -Typen nachstellt. So ist

109lu

die dezimale Darstellung der Dezimalzahl 109 im Typ unsigned long .

Negative Konstanten kennt C nicht! Vorzeichen werden vielmehr stets als einstellige (unare) Operatoren interpretiert. Da es sich bei Konstanten mit negativem Vorzeichenoperator jedoch um einen konstanten Ausdruck handelt, werden diese trotzdem vom Compiler und nicht zur Laufzeit berechnet. Aber darauf werden wir erst spater zuruckkommen.

## 2.4 Der Typ char

Zeichen ( character ) werden von C als Teilmenge der ganzen Zahlen behandelt; den Typ bezeichnet das Schlusselwort char . Das funktioniert so: Die verfugbaren Zeichen werden durchnummeriert, beginnend bei 0. Im Rechner werden die Zeichen dargestellt, indem diese Ordnungszahlen gespeichert werden. Letztlich geht jede Programmiersprache so vor, nur ist in der Regel die Koppelung von Zahlen und Zeichen nicht so eng.

Wieder ergeben sich Probleme aus der Tatsache, dass C auf moglichst allen Rechnern implementiert werden konnen soll, auch wenn die Rechner mit unterschiedlichen Zeichensatzen arbeiten. So kann nur vorgeschrieben werden, dass bestimmte Zeichen vorhanden sein mussen, namlich

- · die 26 Großbuchstaben des (englischen) Alphabets,
- · die 26 Kleinbuchstaben des (englischen) Alphabets,
- · die 10 (Dezimal-)Ziffern,
- · 30 druckbare Sonderzeichen wie Leerzeichen, Plus und Minus, Punkt, Komma, Klammern, usw., und
- · 7 Steuerzeichen zur Steuerung von Ein-/Ausgabegeraten.

Man beachte: Die deutschen Umlaute und das ß gehoren nicht zum Zeichensatz von ANSI-C! Weitestgehend entsprechen diese Anforderungen des Standard der Realitat des ASCII-Code ( American Standard Code for Information Interchange ), der insgesamt 128 Zeichen umfasst:

- · Die Zeichen mit den Ordnungszahlen 0 bis 31 sowie das Zeichen mit der Ordnungszahl 127 sind Steuerzeichen.
- · Die Zeichen mit den Ordnungszahlen 32 bis 126 sind druckbar.

Dass an dieser Stelle keine Tabelle mit den Ordnungszahlen der verschiedenen ASCIIZeichen zu finden ist, liegt daran, dass man sich die Ordnungszahlen der Zeichen bewusst nicht merken sollte. Durch die Zeichenkonstanten hat man in C jederzeit Zugriff auf die Ordnungszahl eines Zeichens, ohne den Wert selbst kennen zu mussen.

Zur internen Speicherung von Zeichen wird das Byte verwendet, das seinerseits uber mindestens 8 Bits verfugen muss.

Obwohl ein Vorzeichen bei Zeichen nicht plausibel erscheint, unterscheidet man zwischen signed und unsigned , damit der Typ char kompatibel zu den int -Typen bleibt, deren Teilmenge er ja ist. Die Wertebereiche der beiden char -Typen wurden bereits in Tabelle 2.1 mit aufgelistet.

Die konkreten implementationsspezifischen Werte enthalt limits.h in Form der Konstanten

- · CHAR MIN und CHAR MAX fur den Typ char ohne Zusatz,
- · SCHAR MIN und SCHAR MAX fur den Typ char mit dem Zusatz signed und
- · UCHAR MAX fur den Typ char mit dem Zusatz unsigned .

Aus der Existenz der verschiedenen Werte kann man schließen, dass der Typ char , anders als die int -Typen, je nach Implementation vorzeichenlos oder vorzeichenbehaftet sein kann, wenn das nicht explizit durch unsigned oder signed festgelegt wird.

Zeichenkonstanten sind einzelne Zeichen, eingeschlossen in Apostrophe, etwa

'w'

Eine Zeichenkonstante reprasentiert die Ordnungszahl ihres Zeichens - welche das ist, hangt vom Zeichensatz ab, den der Rechner verwendet. Dabei ist eines noch wichtig zu erwahnen, weil es oft vergessen wird: Die Zeichenkonstante '0' reprasentiert in der Regel nicht die Ordnungszahl 0, die Zeichenkonstante '1' in der Regel nicht die Ordnungszahl 1, usw. Gesehen haben wir das fur den ASCII-Code im Grunde genommen bereits: Die Ordnungszahlen der druckbaren Zeichen beginnen in ihm erst bei 32!

Einige Zeichen konnen nicht ohne weiteres angegeben werden. Dafur gibt es zwei Grunde:

- · Einige druckbare Zeichen haben im Quellcode bestimmte Bedeutung. Von diesen haben wir den Apostroph bereits kennengelernt, der (u.a.) Zeichenkonstanten begrenzt.
- · Die Steuerzeichen fur Ein-/Ausgabegerate, die C definiert, stehen auf der Tastatur nicht zur Verfugung.

Fur elf solche Zeichen stellt C Escapesequenzen bereit. Tabelle 2.2 listet diese auf.

Tabelle 2.2: Escapesequenzen

| Zeichen   | Beschreibung                                                                                                                                  |
|-----------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| \a        | Piepen (wird nicht von allen Ausgabegeraten un- terstutzt)                                                                                    |
| \b        | Backspace                                                                                                                                     |
| \f        | Seitenvorschub (wird nur von Druckern beachtet)                                                                                               |
| \n        | Zeilenvorschub                                                                                                                                |
| \r        | Positionierung auf Zeilenanfang                                                                                                               |
| \t        | Horizontaler Tabulator                                                                                                                        |
| \v        | Vertikaler Tabulator (wird nur von Druckern beachtet)                                                                                         |
| \'        | Apostroph, der nicht zur Begrenzung einer Zeichen- konstante dient                                                                            |
| \"        | Gansefußchen, die nicht zur Begrenzung einer String- konstante dienen                                                                         |
| \\        | Backslash                                                                                                                                     |
| \?        | Fragezeichen. Nur relevant, wenn man zwei unmittel- bar aufeinanderfolgende Fragezeichen in einer Zeichen- kettenkonstanten verwenden mochte. |
|           | Hintergrund ist die selten benotigte Moglichkeit, Son- derzeichen durch eine Kombination aus zwei Fragezei-                                   |

## 2.5 Zeichenkettenkonstanten

Eine Zeichenkettenkonstante , der Kurze wegen gerne mit dem englischen Begriff String bezeichnet, ist eine Folge von beliebig vielen Zeichen, die in Gansefußchen eingeschlossen ist. Wir haben einen solchen String bereits im einfuhrenden Beispiel verwendet. Strings, die nur durch ' white spaces' getrennt sind, werden vom Praprozessor zu einem einzigen String zusamengefugt.

printf("Dieser String ist zu lang, um ihn in einer " "einzelnen Zeile unterzubringen.\n");

Der Backslash \ ist in einer Zeichenkettenkonstante nur in Verbindung mit einer Escapesequenz erlaubt. Zeilenumbruche sind gar nicht erlaubt. Soll ein Zeilenumbruch in der Ausgabe erfolgen, so ist die Escapesequenz \n zu verwenden. Da Gansefußchen zur Begrenzung von Strings dienen, konnen diese ebenfalls nur als Escapesequenz \" innerhalb eines Strings auftauchen.

Achtung : 'x' bedeutet nicht dasselbe wie "x" ! Darauf werden wir in anderem Zusammenhang noch zuruckkommen.

## 2.6 Gleitkommatypen

Zum numerischen Rechnen benotigt man Gleitkommazahlen . C stellt diese mit den Typen float , double und long double zur Verfugung. Alle drei Typen mussen mindestens den Wertebereich

[ -10 +37 , -10 -37 ] ∪ { 0 } ∪ [+10 -37 , +10 +37 ]

besitzen. Zur Beschreibung von Gleitkommazahlen reicht die Angabe des Wertebereichs allerdings nicht aus; ebenso benotigt man die Angabe der Dichte der Zahlen. Sie kann durch den Abstand der Zahl 1 von der nachstgelegenen großeren Zahl beschrieben werden. Der Standard verlangt die minimalen Dichten

- · 10 -5 beim Typ float und
- · 10 -9 bei den Typen double und long double .

Das entspricht einer Genauigkeit von 6 bzw. 10 dezimal-Stellen. Wahrend sich diese Angaben auf die dezimale Darstellung beziehen, werden Gleitkommazahlen intern binar verarbeitet. Bei der Umwandlung von der einen in die andere Form treten zwangslaufig Rundungsfehler auf. Die Mindestanzahl an Dezimalstellen, die bei Umwandlung in Binardarstellung und Ruckumwandlung erhalten bleibt, wird durch die Anzahl der signifikanten Stellen angegeben. Auch dafur macht der Standard ein Vorgabe.

Die konkreten Werte fur die Wertebereiche der Gleitkommatypen findet man in der Datei float.h :

- · Wertebereich: FLT MAX , DBL MAX , LDBL MAX
- · Dichte: FLT EPSILON , DBL EPSILON , LDBL EPSILON
- · Anzahl der signifikanten Stellen: FLT DIG , DBL DIG , LDBL DIG .

Im Programm hat man prinzipiell zwei Moglichkeiten der Darstellung:

- · Man kann einen Dezimalpunkt schreiben, der vor, inmitten oder hinter der Ziffernfolge stehen kann.
- · Man kann einen Exponententeil angeben, der mit dem Kennbuchstaben e oder E beginnt und danach den Exponenten zur Basis 10 als ganze Zahl mit oder ohne Vorzeichen aufweist.

Außerdem kann man diese beiden Moglichkeiten auch kombinieren.

Einige Beispiele:

|   .1 |   0.1 |   1e-1 |   1.0E-1 |
|------|-------|--------|----------|
|    1 |     1 |      1 |        1 |
|   10 |    10 |     10 |       10 |

Ohne weiteres besitzen Gleitkommakonstanten den Typ double . Mit den nachgestellten Kennbuchstaben f oder F bzw. l oder L konnen aber auch Konstanten mit dem Typ float bzw. long double angegeben werden.

## 2.7 Aufzahlungskonstanten

Aufzahlungskonstanten sind Konstanten mit ganzzahligem Wert, die durch eine sogenannte enum -Deklaration einen Namen erhalten, mit dem sie im weiteren angesprochen werden konnen.

```
enum [name] { konstantenliste };
```

## Dabei:

- · Das Schlusselwort enum leitet die Deklaration ein.
- · Optional kann der Aufzahlungstyp benannt werden. Die eckigen Klammern sollen andeuten, dass der Name name optional ist; sie durfen in keinem Falle mitgeschrieben werden.
- · Die Liste der Konstanten wird in geschweifte Klammern eingeschlossen. Die Elemente der Liste werden voneinander jeweils durch ein Komma getrennt. Es ist ublich, wenn auch nicht notwendig, fur die Namen der Konstanten ausschließlich Großbuchstaben zu verwenden, was der Lesbarkeit des Programms dienen soll.
- · Die Vereinbarung wird durch ein Semikolon abgeschlossen.

## Beispiel

```
enum farbe { ROT, GELB, BLAU, GRUEN };
```

Dem ersten Namen in einer enum -Liste wird der Wert 0 zugeordnet, allen weiteren der um eins erhohte Wert des Vorgangers.

Man kann die Werte jedoch auch explizit in der Form = wert angeben. Dann wird fur Namen, fur die kein Wert angegeben ist, aufsteigend weitergezahlt. Beispiel:

```
enum escapes { BELL = '\a' , NEWLINE = '\n' }; enum farbe { ROT = 1, GELB = 4, BLAU, GRUEN = 2 };
```

Hier erhalt BLAU den Wert 5, wahrend allen anderen Namen die angegebenen Werte zugeordnet werden.

Alle Namen in einer oder verschiedenen Aufzahlungsdeklarationen im selben Gultigkeitsbereich mussen sich unterscheiden. Die Werte, die verschiedenen Namen zugeordnet werden, auch innerhalb einer einzelnen Aufzahlungsdeklaration, brauchen nicht verschieden zu sein. Auch negative Werte konnen vergeben werden. Einzige Restriktion: Die Werte mussen ganzzahlig sein.

## 2.8 Benannte Konstanten

Aufzahlungskonstanten sind auf ganzzahlige Werte beschrankt. Aber auch fur Gleitkommawerte muss man eine Moglichkeit haben, symbolische Namen zu vergeben. Erste Beispiele sind mit FLT\_MAX oder DBL\_EPSILON schon genannt worden. Generell sind benannte

Konstanten fur den Programmierer im Alltag wichtig, um ' magische Konstanten' zu vermeiden.

Betrachten wir als Beispiel ein Programm, in dem Verkaufspreise berechnet werden. Stand in ihm an allen Stellen, an denen Mehrwertsteuer berechnet wird, explizit die Konstante 14 bzw. 1.14, so gab es zum 1.1.1993 mit der Erhohung der Mehrwertsteuer viel Arbeit fur die Programmierer: Diese Konstanten mussten alle ersetzt werden! Ein besonderes Problem dabei ist: Fur jede 14 bzw. 1.14 musste separat entschieden werden, ob die 14 bzw. 1.14 die Mehrwertsteuer war oder eine andere Große bezeichnete, zum Beispiel den Verschnitt des Materials, die nicht verandert werden durfte.

Mit Hilfe der Praprozessor-Direktive

#define name ersatztext

kann man solchen Konstanten sinnvolle Namen geben, etwa

#define MWST 14.0

In allen nachfolgenden Zeilen wird an allen Stellen, an denen name nicht innerhalb eines String oder als Teil eines anderen Namens steht, name durch ersatztext ersetzt. Wie bei den Aufzahlungskonstanten ist es ublich, fur die Namen ausschließlich Großbuchstaben zu verwenden, auch wenn der Standard das nicht vorschreibt.

Aufzahlungskonstanten und durch #define benannte Konstanten haben manches gemeinsam. Es gibt aber (naturlich) auch Unterschiede:

- · Bei #define muss man die Werte stets explizit angeben, wahrend man bei Aufzahlungskonstanten den Compiler zahlen lassen kann. Das ist insbesondere dann interessant, wenn man nur erreichen will, dass die Konstanten verschiedene Werte reprasentieren und ggf. eine bestimmte Großenrelation zwischen ihnen besteht, die Werte selbst aber unwesentlich sind.
- · Aufzahlungskonstanten konnen nur ganzzahlige Werte zugeordnet werden, wahrend bei #define beliebige Werte - und wie wir spater sehen werden nicht nur Werte angegeben werden konnen.

Erweitern wir dazu unser Beispiel der Mehrwertsteuer noch etwas: Benotigt man im Programm neben dem vollen Steuersatz auch den ermaßigten, so konnte (und sollte) man schreiben

```
#define MWST 14.0 #define MWST\_ERM (MWST / 2)
```

statt an allen entsprechenden Stellen explizit MWST / 2 hinzuschreiben. Der ermaßigte Steuersatz lag bislang zwar immer bei der Halfte des vollen - nur war das eher Zufall und Gewohnheit. Der Vorteil dieser Formulierung: Fur die Anderung zum 1.1.1993 brauchten nur diese beiden Zeilen durch

```
#define MWST 15.0 #define MWST\_ERM 7.0
```

ersetzt und danach das Programm neu ubersetzt und gebunden zu werden.

## 2.9 Variablen

Konstanten verandern ihren Wert zur Laufzeit eines Programms nicht. Sie besitzen außerdem nur ihren Wert und Typ, nicht jedoch einen Speicherplatz ; zumindest nicht in der Theorie, in der Praxis sieht das gelegentlich anders aus.

Variablen besitzen dagegen einen Speicherplatz und Typ und in der Regel auch einen Wert, namlich den, der an diesem Speicherplatz steht. Es ist jederzeit moglich, diesen Wert zu andern. Solange der Wert einer Variablen nicht gesetzt wurde, braucht sie keinen wohldefinierten Wert zu besitzen.

In C mussen alle Variablen vereinbart werden, bevor sie verwendet werden konnen. Gewohnlich geschieht dieses am Anfang einer Funktion. Die Vereinbarung von Variablen hat die Form

[speicherklasse] typ namenliste ;

## Dabei:

- · Die Angabe eines Speicherklassen-Attributs ist optional; darauf werden wir spater zuruckkommen.
- · typ ist eines der Schlusselworter oder eine der Schlusselwort-Kombinationen, die wir bereits kennengelernt haben, oder auch ein Aufzahlungstyp. Auf weitere Moglichkeiten werden wir spater zuruckkommen.
- · Die namenliste enthalt, durch je ein Komma voneinander getrennt, die Namen der zu vereinbarenden Variablen.
- · Die Vereinbarung wird durch ein Semikolon abgeschlossen.

Beispiele:

```
int i; double a, b, c; enum farbe kreide;
```

Solch eine Vereinbarung hat zwei Funktionen:

- · Zum einen wird der Compiler veranlasst, Speicherplatz fur die Variablen bereitzustellen.
- · Zum anderen erhalt der Compiler die Vorschrift, wie die Bitfolge, die sich an dem Speicherplatz einer Variablen befindet, zu interpretieren ist (als ganze Zahl mit oder ohne Vorzeichen, als Gleitkommazahl, usw.).

Die Vereinbarung einer Variablen bewirkt im Allgemeinen ohne weiteres nicht gleichzeitig einen wohldefinierten Anfangswert fur die Variable. Erforderlichenfalls kann man dies aber sicherstellen, indem man die Vereinbarung um ein Gleichheitszeichen und den gewunschten Wert erweitert. Diese Form der Vereinbarung heißt Initialisierung . Beispiel:

```
double x = 2.5e-7; enum farbe kreide = ROT; int i, summe = 0, quotient = 1, j;
```

Anfangswerte mussen immer individuell zugewiesen werden; eine abkurzende Schreibweise, um mehreren Variablen denselben Anfangswert zuzuweisen, gibt es nicht.

## 2.10 Namen

Um verschiedene Speicherplatze und andere Objekte, die in C-Programmen eine Rolle spielen, ansprechen zu konnen, muss man sie mit einem Namen oder Bezeichner versehen. Dies haben wir schon in verschiedenen Zusammenhangen kennengelernt. Entsprechend wird es Zeit, dass wir uns mit den Regeln fur sie beschaftigen. Zur Bildung von Namen stehen folgende Zeichen zur Verfugung:

- · uneingeschrankt die 52 Buchstaben, wobei zwischen Groß- und Kleinbuchstaben strikt unterschieden wird,
- · die 10 Ziffern, wobei das erste Zeichen eines Namen keine Ziffer sein darf, um eine Unterscheidung von numerischen Konstanten zu erlauben, und
- · das Unterstreichungszeichen ( \_ ). Dieses Zeichen darf auch am Anfang eines Namens stehen; sollte an dieser Stelle aber fur Bibliotheksfunktionen reserviert bleiben.

Namen durfen zwar beliebig lang sein, jedoch schreibt der Standard nur vor, dass die ersten 31 Zeichen signifikant sein mussen. Ein Compiler darf also Namen als gleich interpretieren, die sich erst im 32. oder einem spateren Zeichen unterscheiden. Die Minimalschranke fur die Anzahl signifikanter Zeichen von Namen, die uber eine Quelldatei hinaus verwendet werden sollen, liegt sogar nur bei 6.

Bestimmte Zeichenfolgen, die Schlusselworter (Tabelle 2.3), sind zwar wie Namen aufgebaut, durfen aber nur mit ihrer festgelegten Bedeutung verwendet werden.

Tabelle 2.3: Schlusselworter von C

| auto     | double   | int      | struct   |
|----------|----------|----------|----------|
| break    | else     | long     | switch   |
| case     | enum     | register | typedef  |
| char     | extern   | return   | union    |
| const    | float    | short    | unsigned |
| continue | for      | signed   | void     |
| default  | goto     | sizeof   | volatile |
| do       | if       | static   | while    |

Da auch bei den Schlusselwortern zwischen Groß- und Kleinbuchstaben unterschieden wird, konnte man zum Beispiel zwar Int oder INT als Namen deklarieren, nicht jedoch int . Es ist in C ublich, wenn auch keineswegs vorgeschrieben, fur die Namen von Variablen nur Kleinbuchstaben und fur benannte Konstanten nur Großbuchstaben zu verwenden.

Um die Verstandlichkeit von Quelltexten zu erhohen, sollte man bei der Namensvergabe gewissen Konventionen folgen. Dies ist umso wichtiger, je umfangreicher der Quelltext ist. In der Regel sollte man die Namen von Variablen und Konstanten so wahlen, dass sie etwas uber die Bedeutung ihres Wertes aussagen. Das impliziert, dass Namen haufig 4 bis 6 Zeichen lang sind, oft auch langer. Die kleinen Beispiele in diesem Text konnen dies nicht hinreichend illustrieren.

In der Regel findet man in gut formulierten Quelltexten nur selten Variablennamen, die nur aus ein oder zwei Buchstaben bestehen. Sinnvoll sind solche kurzen Bezeichner allerdings in folgenden Fallen:

- · Bei der Realisierung mathematischer Formeln sollte man die Bezeichnungen aus den Formeln ubernehmen, soweit das moglich ist.
- · Hochgradig lokale Variablen, etwa Zahlvariablen in Schleifen, haben haufig keine benennbare Bedeutung. Ubliche Namen fur solche Variablen sind zum Beispiel

i, j, k (Lauf-)Indizes m, n Anzahlen c, ch Zeichen s Zeichenketten ( ' Strings') p, z Zeiger

Man sollte auch daran denken, dass die Lange eines Namen nicht allein seligmachend ist. Zumindest fur den Geubten hat der Name i ebenso viel (oder wenig) Aussagekraft wie der Name laufvariable !

Und noch etwas sollte man beachten:

- · Zu ahnliche Namen verleiten zu Schreib- und Lesefehlern.
- · Die Ziffer 1 und die Buchstaben I und l verwechselt man besonders leicht, ebenso die Ziffer 0 und den Buchstaben O (und auch den Buchstaben Q).

## 2.11 Typnamen

Das Schlusselwort typedef erlaubt die Deklaration eigener Typnamen, die dann im weiteren Programm wie die entsprechenden Schlusselworter verwendet werden konnen:

```
typedef typ name ;
```

Ublich ist es, fur die Namen nur Großbuchstaben zu verwenden oder ihnen \_t anzufugen. Diese beiden Varianten werden auch von der Standardbibliothek verwendet. Beispiel:

```
typedef int INTEGER; typedef enum farbe farbe\_t; INTEGER i = 1; farbe\_t kreide;
```

Wie man sieht, werden durch typedef keine neuen Typen deklariert, sondern nur bekannte Typen benannt. Entsprechend bringt typedef an dieser Stelle nichts wirklich Neues, auch wenn man die positiven Auswirkungen auf die Lesbarkeit der Programme nicht unterschatzen sollte. In der Standardbibliothek werden an mehreren Stellen typedef - Deklarationen verwendet. Beispiele findet man in Abschnitt 4.14 oder 9.6.