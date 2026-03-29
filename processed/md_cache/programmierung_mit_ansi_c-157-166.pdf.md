## Kapitel 14

## Strukturen

## 14.1 Vereinbarung von Strukturen

Wir haben gesehen, dass man Elemente mit gleichem Typ zu Feldern zusammenfassen kann. Haufig ist es aber auch wunschenswert, Objekte mit unterschiedlichem Typ zu logischen Einheiten zusammenfassen zu konnen: Will man etwa eine Studentendatei verwalten, benotigt man (u.a.) den Namen, die Matrikelnummer und die Adresse jedes Studenten. Aber auch fur die Zusammenfassung von Objekten mit gleichem Typ bieten sich Felder in manchen Fallen nicht an: Einen Typ ' komplexe Zahl' kann man zwar durch

typedef double complex\_t[2];

deklarieren; der Zugriff auf Real- und Imaginarteil durch Indizierung macht das Arbeiten mit komplexen Zahlen aber nicht gerade ubersichtlich.

C bietet die Moglichkeit, unterschiedliche Objekte zu Strukturen zusammenzufassen.

Die Deklaration eines Strukturtyps beginnt mit dem Schlusselwort struct . Ihm kann ein Name folgen, mit dem dann im weiteren Programm der Strukturtyp bezeichnet werden kann. Ihm folgt, in geschweifte Klammern eingeschlossen, die Aufzahlung der Komponenten des Strukturtyps. Abgeschlossen wird die Deklaration durch ein Semikolon:

```
struct name { typ komponente1 ; typ komponente2 ; ... typ komponenteN ; };
```

Als Beispiel wollen wir die bereits angesprochenen Studentendaten als Strukturtyp deklarieren:

```
struct student\_s { char vorname[30]; char nachname[30]; int matrikelnr; int plz; char wohnort[30]; char strasse[30]; int hausnr; };
```

Die Gultigkeit der Namen der Komponenten eines Strukturtyps ist auf den Strukturtyp beschrankt. Damit entstehen auch dann keine Namenskonflikte, wenn eine Komponente

denselben Namen wie eine Variable, ein Feld, eine Funktion oder auch eine Komponente eines anderen Strukturtyps besitzt.

In der beschriebenen Form handelt es sich um eine reine Deklaration, d.h. es wird noch keine Variable mit dem Typ definiert und entsprechend kein Speicherplatz bereitgestellt. Variablen mit einem Strukturtyp, kurz: Strukturen, kann man auf verschiedene Weisen definieren.

Zunachst kann man die Namen direkt zwischen die schließende geschweifte Klammer und das nachfolgende Semikolon der Typdeklaration setzen:

```
struct student\_s { char vorname[30]; /* ... wie zuvor */ } student1 , student2;
```

Will man im Rest des Programms keinen Bezug mehr auf den Strukturtyp nehmen, kann man den Namen, hier also student s , auch weglassen. Wenn der Name angegeben ist, kann man Stukturen auch so definieren:

```
struct student\_s student1 , student2;
```

Fur das Aufschreiben und auch die Lesbarkeit eines Programms ist es in der Regel gunstiger, Strukturtypen mit typedef Namen zu geben:

```
typedef struct student\_s { char vorname[30]; /* ... wie zuvor */ } student\_t; struct student\_s student1 , student2;
```

```
Jetzt kann man Strukturen etwa durch student\_t student3 , student4;
```

definieren. Bei der Deklaration kann man den Strukturnamen student\_s weglassen. Die erste Variante der Variablenvereinbarung ist dann jedoch nicht mehr moglich. Das ist jedoch kein Nachteil, da die zweite Variante ohnehin kurzer ist. Eine Kombination von typedef -Deklaration und Strukturdefinition ist nicht moglich.

Strukturnamen wurden bisher mit einem nachgestellten \_s versehen. Das ist nicht zwingend erforderlich, verdeutlicht jedoch, dass es sich um einen Strukturnamen handelt. Generell haben Strukturnamen jedoch einen eigenen Namensraum, da sie ja nur zusammen mit struct verwendet werden konnen.

## 14.2 Operationen mit Strukturen

Operationen mit Strukturen als Ganzem sind nur sehr eingeschrankt moglich:

- · Wertzuweisungen zwischen Strukturen sind moglich. Dabei werden die Werte aller Komponenten ubertragen. Offensichtliche Voraussetzung ist die Identitat der Strukturtypen.
- · Funktionen konnen Strukturen als Parameter besitzen. Die Abarbeitung der Aufrufe erfolgt wie bei (einfachen) Variablen: Im Zuge des Aufrufs wird der Wert des Arguments in eine lokale Struktur der Funktion kopiert. Zumindest bei umfangreicheren Strukturen sollte man sich also genau uberlegen, ob die Ubergabe eines Zeigers auf die Struktur nicht zweckmaßiger ist.

- · Funktionen konnen Strukturen als Funktionswerte zuruckliefern. Wie bei den Parametern sollte man sich aber genau uberlegen, ob das zweckmaßig ist. Auch hier kann ein Zeiger-Parameter die bessere Losung sein.
- · Mit dem Adressoperator & kann man die Adresse einer Struktur ermitteln.
- · Bei der Definition einer Struktur kann man ihren Anfangswert festlegen, in der gleichen Form wie bei Feldern:

```
student\_t student = { "Klaus", "Meier", 12345, 37073, "Goettingen", "Einbahnstrasse", 12 };
```

Mit den Komponenten von Strukturen kann man dagegen ' ganz normal' arbeiten. Allerdings reicht die Angabe des Namens einer Komponente offensichtlich nicht aus, da alle Strukturen mit gleichem Typ ja gleichnamige Komponenten besitzen. Erforderlich ist, ahnlich wie bei Zeigern, eine Dereferenzierung: Angegeben werden der Name der Struktur und der Name der Komponente; zwischen beide wird der Punktoperator ( . ) gesetzt:

```
student\_t student; ...
```

```
student.plz = 1000;
```

Als Beispiel schreiben wir ein Programm, das den Datensatz eines Studenten liest und wieder schreibt:

```
#include <stdio.h> /** Strukturdeklaration **********************************/ typedef struct { char vorname[30]; char nachname[30]; int matrikelnr; int plz; char wohnort[30]; char strasse[30]; int hausnr; } student\_t; /** Prototypen *******************************************/ student\_t gelesener\_satz (void); void satz\_schreiben (student\_t s); /*= Hauptprogramm =========================================*/ int main(void) { student\_t satz; printf("Datensatz eingeben:\n"); satz = gelesener\_satz (); printf("Eingegebener Datensatz:\n"); satz\_schreiben (satz); return 0; } /*= Eingabefunktion =======================================*/ student\_t gelesener\_satz(void) {
```

```
student\_t s; printf("Vorname: "); scanf("%s", s.vorname); printf("Nachname: "); scanf("%s", s.nachname); printf("Matrikelnummer: "); scanf("%d", &s.matrikelnr); printf("Postleitzahl: "); scanf("%d", &s.plz); printf("Wohnort: "); scanf("%s", s.wohnort); printf("Strasse: "); scanf("%s", s.strasse); printf("Hausnummer: "); scanf("%d", &s.hausnr); return s; } /*= Ausgabefunktion =======================================*/ void satz\_schreiben(student\_t s) { printf("Vorname: %s\n", s.vorname); printf("Nachname: %s\n", s.nachname); printf("Matrikelnummer: %d\n", s.matrikelnr); printf("Postleitzahl: %d\n", s.plz); printf("Wohnort: %s\n", s.wohnort); printf("Strasse: %s\n", s.strasse); printf("Hausnummer: %d\n", s.hausnr); }
```

Quelltext 14.1: Arbeiten mit Strukturen

## 14.3 Schachtelung strukturierter Typen

Jede Strukturkomponente darf einen beliebigen Typ besitzen. Wir haben das zum Beispiel schon genutzt, indem wir Felder als Strukturkomponenten deklariert haben. Entsprechend kann man Felder definieren, deren Komponenten Strukturen sind. Außerdem darf jede Strukturkomponente ihrerseits eine Struktur sein.

Zum Beispiel konnen wir vereinbaren

```
typedef struct { char vorname[30]; char nachname[30]; } name\_t; typedef struct { int plz; char wohnort[30]; char strasse[30]; int hausnr; } adresse\_t; typedef struct { name\_t name; int matrikelnr;
```

```
adresse\_t adresse;
```

} student\_t;

student\_t student , studenten[50];

Fur die Zugriffe auf einzelne Komponenten muss man dann die ' Pfade' nachverfolgen, zum Beispiel

```
student.adresse.hausnr = 17; if (studenten[17].name.vorname[0] == 'K') ...
```

Die Abarbeitung solcher Pfade erfolgt, wie es nahe liegt, von links nach rechts.

## 14.4 Zeiger auf Strukturen

Es wurde bereits angesprochen, dass man sich sehr genau uberlegen sollte, ob man umfangreiche Strukturen als Parameter von Funktionen oder als Funktionstypen vorsieht, weil beides das Kopieren ganzer Strukturen impliziert. In der Regel wird man deshalb im Zusammenhang mit Funktionen Zeiger auf Strukturen verwenden. Es ist ubrigens nicht so recht nachvollziehbar, warum C nicht grundsatzlich Strukturen wie Felder behandelt, also Strukturnamen als Zeiger auf den Anfang der Struktur betrachtet.

Fur Zeiger auf Strukturen gelten dieselben Regeln wie fur Zeiger auf einfache Variablen:

student\_t student , *p = &student;

Beim Zugriff auf die Komponenten muss man berucksichtigen, dass der Punktoperator hohere Prioritat besitzt als der Dereferenzierungsoperator ( * ). Wir mussen also

(* strukturzeiger ). strukturkomponente

schreiben. Abkurzend und suggestiver ist die aquivalente Schreibweise mit dem PfeilOperator ( -> ).

strukturzeiger -> strukturkomponente

Sehen wir uns als Beispiel noch einmal die Ein-/Ausgabe an. Diesmal sind die Strukturen verschachtelt und es werden den Funktionen Zeiger auf die Strukturen ubergeben, um das automatische Kopieren der ganzen Strukturen zu vermeiden.

```
#include <stdio.h> /** Strukturdeklarationen ********************************/ typedef struct { char vorname[30]; char nachname[30]; } name\_t; typedef struct { char strasse[30]; int hausnr; int plz; char wohnort[30]; } adresse\_t; typedef struct { name\_t name; int matrikelnr;
```

```
adresse\_t adresse; } student\_t; /** Prototypen *******************************************/ void satz\_lesen(student\_t *const s); void satz\_schreiben(const student\_t *const s); /*= Hauptprogramm =========================================*/ int main(void) { student\_t satz; printf("Datensatz eingeben:\n"); satz\_lesen (&satz); printf("Eingegebener Datensatz:\n"); satz\_schreiben (&satz); return 0; } /*= Eingabefunktion =======================================*/ void name\_lesen(name\_t *const n) { printf("Vorname: "); scanf("%s", n->vorname); printf("Nachname: "); scanf("%s", n->nachname); } void adresse\_lesen(adresse\_t *const a) { printf("Postleitzahl: "); scanf("%d", &a->plz); printf("Wohnort: "); scanf("%s", a->wohnort); printf("Strasse: "); scanf("%s", a->strasse); printf("Hausnummer: "); scanf("%d", &a->hausnr); } void satz\_lesen (student\_t *const s) { name\_lesen(&s->name); printf("Matrikelnummer: "); scanf("%d", &s->matrikelnr); adresse\_lesen(&s->adresse); } /*= Ausgabefunktion =======================================*/ void satz\_schreiben (const student\_t *const s) { printf("Vorname: %s\n", s->name.vorname); printf("Nachname: %s\n", s->name.nachname); printf("Matrikelnummer: %d\n", s->matrikelnr); printf("Postleitzahl: %d\n", s->adresse.plz); printf("Wohnort: %s\n", s->adresse.wohnort); printf("Strasse: %s\n", s->adresse.strasse); printf("Hausnummer: %d\n", s->adresse.hausnr); }
```

Quelltext 14.2: Arbeiten mit verschachtelten Strukturen und Zeigern auf Strukturen

## 14.5 Strukturen auf dem Heap

Fur Zeiger auf Strukturen gelten dieselben Regeln wie fur Zeiger auf einfache Variablen. Insbesondere heißt das auch: Definiert man eine Zeigervariable, so wird nur der Speicher fur die Aufnahme des Zeigers bereitgestellt. Durch Zuweisung eines Zeigers auf eine statische oder automatische Struktur kann man solch einer Zeigervariablen einen Wert geben. Aber auch Bereitstellung von Speicher auf dem Heap ist moglich.

## student\_t *p;

...

## p = (student\_t *)malloc(sizeof (student\_t));

Hier ist der Operator sizeof unentbehrlich! Wieviel Speicher eine Struktur benotigt, kann namlich von Rechner zu Rechner sehr unterschiedlich sein, selbst wenn die einzelnen Komponenten auf den Rechnern jeweils gleichviel Speicher benotigen. Dahinter steht eine Vorschrift des Standards: Die Komponenten einer Struktur mussen im Speicher des Rechners zwar dieselbe Reihenfolge besitzen wie in der Deklaration - sie mussen aber nicht luckenlos aufeinanderfolgen! Entsprechend addiert der Operator sizeof nicht einfach den Speicherbedarf der Komponenten, sondern berucksichtigt auch eventuelle Lucken. Als Grundregel sollte man sich einfach merken: Bei jedem Aufruf von malloc steckt im Argument der Operator sizeof !

## 14.6 Datum und Uhrzeit

Mit der Kenntnis von Strukturen kann nun auch die Headerdatei time.h besprochen werden. Aktuelles Datum und Uhrzeit kann man sich von der Funktion

```
time\_t time(time\_t *zeit);
```

liefern lassen - in einer implementationsspezifischen Darstellung. Dabei:

- · Der Funktionswert (time\_t)(-1) ( Typecast ) markiert, dass Datum und Uhrzeit nicht verfugbar sind.
- · Wenn zeit der Nullzeiger ist, wird nur der Funktionswert geliefert; sonst wird das Resultat zusatzlich auch in die angegebene Variable geschrieben.

Die Headerdatei bietet aber auch die Moglichkeit, daraus eine allgemein verstandliche Darstellung erzeugen zu lassen. In ihr ist der Strukturtyp

```
struct tm
```

definiert. Er muss zumindest die folgenden Komponenten besitzen:

```
int tm\_sec Sekunde in der Minute, 0 . . . 61 int tm\_min Minute in der Stunde, 0 . . . 59 int tm\_hour Stunde seit Mitternacht, 0 . . . 23 int tm\_mday Tag im Monat, 1 . . . 31 int tm\_mon Monat im Jahr, 0 . . . 11 int tm\_year Jahr seit 1900 int tm\_wday Tag in der Woche (ab Sonntag), 0 . . . 6 int tm\_yday Tag seit 1. Januar, 0 . . . 365 int tm\_isdst Sommerzeit-Marke (daylight saving time) ( < 0 : unbekannt)
```

wobei die Reihenfolge der Komponenten durch den Standard nicht festgelegt ist. Die Umwandlung eines Wertes mit dem Typ time\_t in den Typ tm nehmen die Funktionen

```
struct tm *gmtime(const time\_t *zeit); struct tm *localtime(const time\_t *zeit);
```

vor - in Greenwich-Standardzeit bzw. in die lokale Zeit. Daneben gibt es auch die Umkehrung: Die Funktion

time\_t mktime(struct tm *zeitpunkt);

wandelt den Wert der Struktur in die interne Darstellung um. Sie unterstellt, dass es sich um eine lokale Zeit handelt.

## 14.7 Verkettete Listen

Strukturen und Zeiger auf Strukturen bilden die Grundlage einer wichtigen nicht elementaren Datenstruktur, namlich der verketteten Liste . Wegen der Bedeutung der verketteten Listen soll ein kurzer Uberblick geben werden.

Anschaulich kann man verkettete Listen mit ' Schnitzeljagd' vergleichen:

- · Man hat einen Verweis, wo man beginnen muss (Zeigervariable).
- · AmStart findet man einen Zettel mit einer Aufgabe und einen neuen Verweis (Struktur mit Daten- und Zeigerkomponente).
- · Folgt man den Verweisen, kommt man irgendwann zum Ende (Zeigerkomponente mit Nullzeiger).

Abbildung 14.1 verdeutlicht das.

Abbildung 14.1: Verkettete Liste

picture-1.png

Im Programm kann man das durch Deklarationen wie

```
struct liste { DATENTYP daten;
```

struct liste *nachfolger;

};

nachvollziehen. Interessant ist, dass hier scheinbar eine ' rekursive Deklaration' vorliegt. Tatsachlich ist die zweite Komponente aber ein Zeigertyp und steht nur fur eine Adresse, nicht fur den Strukturtyp, der gerade deklariert wird.

Standardoperationen fur verkettete Listen sind

- · Einfugen eines neuen Eintrags.
- · Suchen eines Eintrags mit bestimmtem Wert.
- · Entfernen eines Eintrags.

Typischerweise werden verkettete Listen auf dem Heap angelegt. Der Fantasie sind beim Aufbau verketteter Strukturen keine Grenzen gesetzt:

- · In einer verketteten Liste kann jeder Eintrag Anfang einer verketteten Liste sein.
- · Mehrere Zeigerkomponenten in jeder Struktur erlauben den Aufbau von mehrfach verketteten Listen oder auch von Baumen .

## 14.8 Verbunde

Formal den Strukturen sehr ahnlich sind die Verbunde : Statt struct schreibt man union . Inhaltlich bestehen jedoch ganz gravierende Unterschiede:

- · Bei Strukturen belegen aufeinanderfolgende Komponenten aufeinanderfolgende Platze im Speicher, wenn auch vielleicht nicht luckenlos, wie wir gesehen haben.
- · Bei einem Verbund beginnen alle Komponenten an derselben Speicheradresse. Der Verbund belegt insgesamt so viel Speicher wie seine langste Komponente. Dadurch wird erreicht, dass der gleiche Speicherplatz zu unterschiedlichen Zeitpunkten in unterschiedlicher Weise genutzt werden kann, z.B. je nach Situation zur Speicherung eines eines float -Wertes oder (wenn dieser gerade nicht benotigt wird) zur Speicherung eines int -Wertes.

In der Praxis kommen Verbunde recht selten vor. Ein kurzes Beispiel soll zeigen, dass ihre Verwendung extrem leicht zu Fehlern fuhrt. Wir hatten gesehen, wie man sich selber mit Castoperatoren ' austricksen' kann, etwa indem man

```
int i, *ip = &i; float *fp; ... fp = (float *) ip; *fp = 6.5f; printf("%d\n", i);
```

```
schreibt. Mit einem Verbund kann man dasselbe einfacher haben: union { int i; float f; } quatsch; ... quatsch.f = 6.5f; printf("%d\n", quatsch.i);
```