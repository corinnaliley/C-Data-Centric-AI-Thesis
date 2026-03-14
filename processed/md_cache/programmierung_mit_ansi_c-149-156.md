## Kapitel 13

## Speicher auf dem Heap

## 13.1 Speichertypen

Wir haben bisher zwei logische Arten von Speicher kennengelernt:

- · Externe Variablen sind grundsatzlich statisch, ebenso interne Variablen mit dem Attribut static . Das hieß, dass bereits der Compiler den erforderlichen Speicherplatz bereitstellt, der dann wahrend der gesamten Ausfuhrung des Programms zur Verfugung steht.
- · Automatische Variablen sind dynamisch. Das hieß, dass der Speicher fur sie erst in dem Moment bereitgestellt wird, in dem bei der Ausfuhrung des Programms der Block betreten wird, der ihre Definition enthalt, und dass dieser Speicher beim Verlassen des Blocks auch wieder freigegeben wird. Diese Art von Variablen wird in der Regel auf einem Stack bereitgestellt. Dabei handelt es sich um eine Datenstruktur, die linear wachst. D.h. Speicherplatz einer Variablen auf dem Stack kann erst wieder freigegeben werden, wenn alle spater erzeugten Variablen ebenfalls wieder freigegeben wurden. Das entspricht genau der Verwendung von automatischen Variablen. Es handelt sich also um strukturierten dynamischen Speicher.

Es gibt eine dritte logische Art von Speicher: Ein Programm hat die Moglichkeit, wahrend es lauft Speicher vom Betriebssystem anzufordern, wobei sich die Große des angeforderten Speichers erst bei Ablauf des Programms z.B. durch eine Benutzereingabe ergibt. Dieser Speicher steht ihm dann so lange zur Verfugung, bis es ihn explizit wieder freigibt oder bis es terminiert. Die Verfugbarkeit dieses Speichers ist insbesondere nicht an die Blockstruktur des Programms gebunden. Man bezeichnet die Gesamtheit dieses Speichers als Heap . Da dieser Speicher in beliebiger Reihenfolge angefordert und wieder freigegeben werden kann, ist klar, dass er nicht besonders strukturiert sein kann. Die Funktionen zur Anforderung von Speicher auf dem Heap mussen also einen gewissen Aufwand betreiben, um den Speicher zu verwalten. Der von automatischen Variablen genutzte Speicher auf dem Stack erfordert fast keinen zusatzlichen Aufwand.

Wieviel Speicher auf dem Heap zur Verfugung steht, hangt vom jeweiligen Rechner und Betriebssystem ab. Die Große des Heap kann durch den physikalisch vorhandenen Speicher begrenzt sein. Die meisten Betriebssystem unterstutzen jedoch virtuellen Speicher. D.h. jedem Programm steht der gesamte Adressraum zur Verfugung. Sollte mehr als der tatsachlich vorhandene Speicher benotigt werden, so werden gerade nicht benotigte Speicherbereiche auf die Festplatte ausgelagert. Belegt ein Zeiger 32 Bit, so sind theoretisch maximal 4 Gigabyte adressierbar.

Bei statischem Speicher und bei Speicher auf dem Stack sorgt der Compiler dafur, dass eine Zuordnung zwischen Variablen und Adressen erfolgt. Bei Speicher auf dem Heap sieht das ganz anders aus: Die Anforderung von Speicher vom Betriebssystem erfolgt naturlich durch Aufruf einer entsprechenden Funktion. Die kann - als einzige Moglichkeit - einen Zeiger auf den Anfang des bereitgestellten Speichers als Funktionswert zuruckgeben , falls genug Speicher vorhanden ist. Man ist also gezwungen, diesen Wert in einer ' passenden' Zeigervariablen zu speichern, damit man ihn spater fur die Zugriffe auf den Speicher verwenden kann.

## 13.2 Funktionen zur Heapverwaltung

C kennt drei Funktionen, mit denen man Speicher auf dem Heap anfordern kann, und eine Funktion zur Freigabe. Alle vier Funktionen sind in der Standard-Headerdatei stdlib.h deklariert. Wichtig sind zunachst nur die Funktionen

void *malloc(size\_t groesse);

void free(void *zeiger);

Die Funktion malloc stellt, wenn moglich, einen zusammenhangenden Speicherbereich der Große groesse zur Verfugung und liefert als Funktionswert den Zeiger auf den Anfang dieses Speicherbereichs. Die Große bezieht sich dabei auf ein Vielfaches des Speicherbedarfs eines Zeichens - wir erinnern uns: Der Standard schreibt sizeof (char) == 1 vor. Falls der angeforderte Speicher nicht bereitgestellt werden kann, ist der Funktionswert der Nullzeiger ( NULL ). Da die Speicherbereitstellung bei jedem Versuch fehlschlagen kann, sollte man den Ruckgabewert von malloc immer auf NULL uberprufen.

Der Typ dieser Funktion ist void * . Ein Zeiger dieses Typs ist kompatibel zu allen anderen Zeigertypen, so dass man seinen Wert jeder beliebigen Zeigervariablen zuweisen kann, unabhangig von deren Typ und ohne einen Castoperator hinschreiben zu mussen. Dass man Zeiger mit dem Typ void * selbst nicht dereferenziert werden kann, haben wir bereits gesehen.

Die Funktion free gibt einen Speicherbereich wieder frei. Voraussetzung fur ordnungsgemaßes Arbeiten der Funktion ist, dass man ihr nur Zeiger als Argument ubergibt, die man sich zuvor mit malloc oder einer der beiden anderen Bereitstellungsfunktionen beschafft hat. Dahinter steht, dass zumindest manche Betriebssysteme ' in der Nahe' der Zeiger, die sie beim Aufruf von malloc liefern, zusatzliche interne Informationen unterbringen, die beim Aufruf von free benotigt werden, etwa Angaben uber die Große des Speichers. Einzige Ausnahme ist NULL . Wird NULL als Argument von free verwendet, tut die Funktion nichts.

## 13.3 Bereitstellung von Speicher

Bei der Matrizenmultiplikation, oder auch vielen anderen mathematischen Programmen, die mit Vektoren und Matrizen arbeiten, weiß man in der Regel beim Schreiben des Programms nicht, wie groß die Vektoren und Matrizen maximal werden konnen. Dies macht die Verwendung von statischen Variablen problematisch.

Dieses Problem wird in C durch die Bereitstellung der benotigten Vektoren und Matrizen auf dem Heap gelost. Durch

```
float *v; int laenge; /* ... Initialisierung von laenge */ v = (float *) malloc(laenge * sizeof(float));
```

```
if (v == NULL) { /* Fehlerbehandlung , ggf. Programmabbruch */ }
```

stellt das Betriebssystem ja gerade den Speicherplatz bereit, den ein float -Vektor mit laenge Komponenten benotigt. Entsprechend kann man sich mit

```
float *m; int n; /* ... Initialisierung von n */ m = (float *) malloc(n * n * sizeof(float)); if (m == NULL) { /* Fehlerbehandlung , ggf. Programmabbruch */ }
```

den Speicherplatz fur eine ( n × n )-Matrix mit float -Komponenten beschaffen.

Zeigervariablen erlauben es immer, ihren Wert als Zeiger auf den Anfang eines Vektors zu interpretieren. Das haben wir hier fur den Speicher auf den Heap genutzt. Ohne weiters ist es dagegen nicht moglich, Speicher auf dem Heap mit einer Matrixstruktur zu versehen. Wir sind also, wie in der Regel auch in Funktionen, dazu gezwungen, die Speicherabbildungsfunktion selber zu definieren und sie fur jeden Zugriff selber auszuwerten. Die entsprechende Vorgehensweise wurde schon im Abschnitt uber Funktionen besprochen.

Am Ende dieses Kapitels wird noch einmal auf Matrizen auf dem Heap eingegangen. Wir werden sehen, dass sich, wenn auch mit einigem Aufwand, letztlich doch auch Matrizen erzeugen lassen.

Speicher, den man sich mit malloc beschafft, besitzt ubrigens keine wohldefinierten Werte. Will man bestimmte Anfangswerte haben, muss man selber explizit fur deren Zuweisung sorgen.

## 13.4 Beispiel: Speichern von Zahlen

Es wird Zeit fur ein konkretes Beispiel. Wir wollen nur die letzten Zahlen einer Eingabe verarbeiten, zum Beispiel die letzten 10. Allerdings soll die Anzahl letztlich erst beim Aufruf des Programms festgelegt werden: Wenn ein entsprechender Aufrufparameter (in der Form -nnn ) angegeben ist, soll sein Wert verwendet werden; sonst soll 10 verwendet werden.

Um das Programm nicht ausufern zu lassen, werden zwei Vereinfachungen gegenuber der ' Soll-Losung' vorgenommen:

- · Unzulassige Aufrufparameter sollen nicht besonders bemangelt, sondern nur durch den Standardwert 10 ersetzt werden.
- · Die Verarbeitung soll nur im Auflisten der Zahlen bestehen.

Die Losung verwendet die Funktion sscanf , die in string.h deklariert wird. Sie arbeitet genau wie scanf , jedoch liest sie nicht von der Standardeingabe, sondern verarbeitet als Eingabe den String, auf den das erste Argument zeigt.

```
#include <stdio.h> #include <stdlib.h> #include <string.h> #define DEFLEN 10
```

```
/** Prototypen *******************************************/ static int lesen(unsigned int maxlen , float *v); /*= Hauptprogramm =========================================*/ int main(int anzahl , char *argument[]) { unsigned int maxlen , len, i; float *v; if (anzahl < 2 || sscanf(argument[1], "-%u", &maxlen) != 1) maxlen = DEFLEN; v = (float *) malloc(maxlen * sizeof (float)); if (v == NULL) { printf("Speicher nicht verfuegbar!\n"); return 1; } printf("Bitte Zahlen eingeben: "); len = lesen (maxlen , v); for (i = 0; i < len; i++) printf("%f\n", v[i]); free(v); return 0; } /*= Lesen der Eingabe =====================================*/ static int lesen(unsigned int maxlen , float *v) { int i = 0; float z; while (i < maxlen) { if (scanf("%f", &v[i]) == EOF) return i; i++; } while (scanf("%f", &z) != EOF) { memmove(&v[0], &v[1], (maxlen - 1) * sizeof (float)); v[maxlen - 1] = z; } return maxlen; }
```

Quelltext 13.1: Auflisten der letzten Zahlen der Eingabe

Eine Frage stellt sich noch: Ist es eigentlich zweckmaßig, die gespeicherten Werte umzuspeichern? Lasst sich dieses ggf. vermeiden?

Zur ersten Teil der Frage: Ganz ohne Umspeicherungen kommen wir nicht aus. Da float -Werte in der Regel nur 4 Bytes beanspruchen, spricht im Beispiel wenig dagegen, sie selbst umzuspeichern short - und char -Werte benotigen zwar in der Regel weniger Speicherplatz, aber diese Typen helfen hier nicht weiter.

Anders sieht es aus, wenn die Werte mehr Speicherplatz benotigen - etwa wenn sie Strings

oder, allgemeiner, Vektoren sind. Das fuhrt zum zweiten Teil der Frage: Naturlich brauchen wir die Werte selbst nicht umzuspeichern! Um das Umspeichern zu vermeiden, mussen wir allerdings die Datenstruktur andern: Anstelle eines Vektors, der selbst die Daten enthalt, mussen wir einen Vektor definieren, der Zeiger auf die Daten enthalt. Dann reicht es aus, die Zeiger umzuspeichern - und die belegen in der Regel jeweils 2 oder 4 Bytes, je nach Rechner.

Realisiert man diese Idee, so hat man zwei Schritte auszufuhren: Im ersten muss man den Zeigervektor bereitstellen und im zweiten die Zeiger auf die Daten. Und dabei kann man sich geschickt oder ungeschickt anstellen: Ungeschickt ware es, in einer Schleife fur jede Vektorkomponente separat den Zeiger auf einen passenden Speicherbereich zu beschaffen, weil malloc in der Regel eine ziemlich aufwendige Funktion ist. Es reicht durchaus aus, einen einzigen, zusammenhangenden Speicherbereich zu beschaffen und dann Zeiger auf Teile dieses Speicherbereichs zu berechnen. Das konnen wir, wenn wir beim Werttyp float bleiben, zum Beispiel so losen:

```
float **v, *z; int j; ... v = (float **) malloc(maxlen * sizeof(float *)); if (v != NULL) { z = (float *) malloc(maxlen * sizeof(float)); if (z != NULL) { for (j = 0; j < maxlen; j++) v[j] = &z[j]; } else { free(v); v = NULL; } }
```

Jetzt zeigt die j -te Komponente von v anfangs auf die j -te Komponente von z - doch das andert sich unter Umstanden wahrend der Ausfuhrung des Programms.

In der Folge sind weitere Anderungen am Programm erforderlich. Sie sollten sie sich selbst einmal uberlegen.

## 13.5 Speicherfreigabe

Am Beginn des Abschnitts wurde erwahnt, dass Speicher auf dem Heap dem Programm so lange zur Verfugung steht, bis es ihn wieder freigibt. Das stimmt, leider, nur bei formaler Betrachtung: Der Speicher steht zwar formal zur Verfugung - um ihn nutzen zu konnen, braucht man zusatzlich aber auch einen Zeiger auf ihn. Und diese Zeiger konnen in der Regel selbst nicht auf dem Heap liegen, sondern mussen statische oder automatische Variablen sein.

Wir sehen uns das an einem Beispiel an: Formal ist die Funktion

```
void muellerzeugung(int menge) { float *v; v = (float *) malloc(menge * sizeof(float)); }
```

sicher korrekt. Allerdings verschwindet ihre lokale, automatische Variable v mit Abschluss der Funktion wieder - und mit ihr auch der Zeiger auf den Speicherbereich, den wir uns mit malloc beschafft haben.

Mit einer Funktion wie muellerzeugung konnen wir entsprechend jedes Programm zum ' Absturz' bringen - wir brauchen sie nur oft genug mit einem hinreichend großen Argument aufzurufen: Bei jedem Aufruf wird Speicher angefordert. Da dieser Speicher nicht wieder freigegeben wird, muss der Heap notwendig irgendwann voll sein.

Es ist also ein schwerwiegender Fehler, Speicher auf dem Heap zu beschaffen, diesen aber nicht wieder freizugegeben. Wird der Speicher nur lokal in einer Funktion benotigt, so ist diese auch dafur zustandig, ihn wieder freizugeben. Das kann so aussehen:

```
void kein\_muell (int menge) { float *v; v = (float *) malloc(menge * sizeof(float)); /* ... */ free (v); }
```

Oft soll aber der bereitgestellte Speicher uber einen langeren Zeitraum verwendet werden. Dann sollte es moglich sein, die Speicherreservierungen zu protokollieren, um wahrend der Testphase des Programms eventuelle Speicherlecks mithilfe des Protokolls zu entdecken. Der Protokollmechanismus kann so implementiert werden, dass man ihn z.B. durch bedingte Compilation leicht abschalten kann. Damit reservierter Speicher leicht wieder freigegeben werden kann, sollte es zu jeder Funktion, die Speicher bereitstellt, eine passende Funktion geben, die ihn wieder freigibt. Besonders bei komplexen Datenstrukturen kann das sehr hilfreich sein: Man muss am Ende nur zahlen, ob beide Funktionen gleichoft erfolgreich aufgerufen wurden. Im nachsten Abschnitt wird fur Matrizen ein solchen Funktionenpaar vorgestellt.

Außerdem gilt naturlich erneut, was schon fur Zeiger auf Konstanten gilt: Uberschreibt man den Zeiger auf einen Speicherbereich im Heap durch einen anderen Wert, hat man anschließend keinen Zugriff mehr auf ihn. Insbesondere kann man ihn nicht einmal mehr freigeben!

So offensichtlich wie in der Anweisungsfolge

```
float f, *v; v = (float *) malloc(laenge * sizeof(float)); v = &f;
```

wird das sicher kein Programmierer machen - in verdeckter Form kommt es leider allzu haufig vor!

## 13.6 Matrizen auf dem Heap

Jetzt soll endlich ein allgemein brauchbares Beispiel fur beliebig dimensionale Matrizen implementiert werden. Wie man sich den Speicher fur sie auf dem Heap beschaffen kann, haben wir oben gesehen. Wie man eine vernunftige Indizierung erreichen kann, wollen wir uns jetzt uberlegen.

Dazu mussen wir uns noch einmal in Erinnerung rufen, wie fur eine Matrix m der Ausdruck m[i] zu interpretieren ist. Zunachst zwei elementare formale Uberlegungen:

- · Paare eckiger Klammern sind Operatoren; aufeinanderfolgende Paare werden von links nach rechts abgearbeitet.
- · Der Name einer Matrix reprasentiert einen Zeiger auf den Vektor der Zeiger auf die Zeilen.

Beide Uberlegungen ergeben zusammen: Der Wert des Ausdrucks m[i] ist ein Zeiger auf eine Zeile der Matrix.

Da m der Name einer Matrix ist, ist der Vektor der Zeiger auf die Zeilen und entsprechend der Wert des Ausdrucks m[i] eine Konstante. Es steht allerdings nirgends, dass bei doppelter Indizierung, etwa m[i][j] , der Teilausdruck m[i] eine Konstante sein muss .

Und dieses konnen wir nutzen: Wir wollen einmal unterstellen, dass wir eine n × m -Matrix A mit double -Komponenten benotigen. Dann beschaffen wir uns in einem ersten Schritt einen Vektor mit n Komponenten, die jeweils den Zeiger auf eine Zeile aufnehmen konnen. In einem zweiten Schritt beschaffen wir uns die Speicher fur die Zeilen und tragen die Zeiger darauf in die Komponenten des zunachst beschafften Vektors ein.

Im Programm kann das so aussehen:

```
int n, m; ... double **a; int i; ... a = (double **) malloc(n * sizeof (double *)); if (a == NULL) /* ... Fehlerbehandlung */ for (i = 0; i < n; i++) { a[i] = (double *) malloc(m * sizeof (double)); if (a[i] == NULL) /* ... Fehlerbehandlung */ }
```

Schreiben wir jetzt etwa a[i][j] , so wird wieder zunachst a[i] ausgewertet. Dabei resultiert der Zeiger auf die entsprechende Zeile. Danach erfolgt die zweite Indizierung und liefert uns den Wert der entsprechenden Komponente der Zeile, also genau das, was wir haben wollen.

Bei der Freigabe einer so bereitgestellten Matrix muss man offensichtlich genau umgekehrt vorgehen und erst die einzelnen Zeilen und dann den Vektor der Zeiger auf die Zeilen freigeben. Das Arbeiten mit Matrizen wird dadurch sehr einfach, da man so bereitgestellte Matrizen auch in Funktionen vernunftig indizieren kann. Die Parameter, die die Matrizen reprasentieren, sind formal ja Vektoren (von Zeigern) - und fur Vektoren funktioniert die Indizierung auch in Funktionen.

Der Preis, den man dafur zahlen muss, sind die relativ aufwendige Bereitstellung und Freigabe der Matrizen. Man kann ihn aber auf ein Minimum reduzieren, indem man einmal die entsprechenden Operationen als Funktionen programmiert und in einem separaten Modul unterbringt, auf den man dann bei Bedarf zuruckgreifen kann.

Wenn man diese Funktionen schreibt, kann man gleich noch etwas optimieren: Die Funktionen malloc und free sind in der Regel ziemlich aufwendig, so dass man sie nicht unnotig oft aufrufen sollte. Entsprechend ist es hier in der Regel gunstiger, sich den gesamten Speicherbereich fur die Matrix mit einem Aufruf von malloc zu beschaffen und diesen Speicher dann in einer Schleife aufzuteilen, wie in einem fruheren Beispiel bereits gesehen:

```
#include <stdlib.h> static int anzahl = 0;
```

```
/*= Matrixallokation ======================================*/ double **matrixalloc(unsigned int n, unsigned int m) { double **a; a = (double **) malloc(n * sizeof (double *)); if (a != NULL) { a[0] = (double *) malloc(n * m * sizeof (double)); if (a[0] == NULL) { free(a); a = NULL; } else { unsigned int i; for (i = 1; i < n; i++) a[i] = a[i-1] + m; anzahl++; /* Matrix bereitgestellt */ } } return a; } /*= Matrixfreigabe ========================================*/ void matrixfree(double **a) { if (a != NULL) free(a[0]); free(a); anzahl --; /* Matrix freigegeben */ } /*= Matrix -Zaehler ========================================*/ int matrixanzahl(void) { return anzahl; /* falls matrixanzahl() != 0, */ } /* wurden nicht alle */ /* Matrizen freigegeben */
```

Quelltext 13.2: Matrizen mit beliebigen Dimensionen bereitstellen

Beachte: Zeilenvertauschungen durch Vertauschen von Zeigern sind jetzt ohne weiteres nicht mehr moglich. Zum Freigeben der Matrizen wird vorausgesetzt, dass der Zeiger auf die erste Zeile der Matrix auch auf den Anfang des verwendeten Speicherbereichs zeigt. Sollte dies nach Zeilenvertauschungen nicht mehr der Fall sein, scheitert die Freigabe des Speichers mit free . Ein Losung ware, in matrixfree den kleinsten Zeiger zu suchen und als Argument von free zu verwenden.

Auch kann und sollte man in die Funktionen gleich noch eine halbwegs komfortable Behandlung von Fehlern bei der Speicherbereitstellung einbauen, so wie es hier gemacht wurde. Mit der Funktion matrixanzahl steht eine einfache Moglichkeit bereit, um zu prufen, ob bei Programmende alle Matrizen ordnungsgemaß freigegeben wurden.