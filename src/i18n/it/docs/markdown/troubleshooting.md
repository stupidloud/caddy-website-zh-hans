Strategie di risoluzione dei problemi
=====================================

Questa pagina presenta un framework metodico e generale per risolvere da soli la maggior parte dei problemi che potreste incontrare usando Caddy *senza l'uso dell'IA*. Raccomandiamo passaggi simili quando chiedete aiuto nei nostri forum. In molti casi, potete rispondere alla vostra stessa domanda o risolvere i vostri problemi applicando un po' di pensiero critico.


Cosa sapete?
------------

Potreste non sapere quale sia il problema, cosa lo stia causando o come risolverlo, quindi iniziamo con alcune cose fondamentali che sicuramente sapete:

### Cosa vi aspettate

Ditelo ad alta voce, o nella vostra testa, oppure scrivetelo. Siate chiari e specifici in modo che non ci siano dubbi o spazio per ambiguità. Potreste anche spiegare a voi stessi *perché* vi aspettate proprio quello.

"Dovrebbe funzionare" non è un'aspettativa valida.

"Mi aspetto un reindirizzamento 301 quando effettuo una richiesta a questo URI" è molto meglio.


### Comportamento attuale

Osservate cosa sta succedendo. Cosa sta accadendo *esattamente* e come si contrappone alla vostra aspettativa? Sintetizzate ciò che sapete.

"Non funziona" è inutile e pigro; evitate questa frase ovunque, tranne forse come descrizione abbreviata per un comportamento specifico che è già stato documentato in dettaglio.

"Invece di una risposta 301, ottengo una risposta 200, sebbene veda l'header `Server: Caddy`", è molto meglio poiché confronta ciò che sapete con ciò che vi aspettate e sintetizza altre informazioni note, il che ci dice che la richiesta sta almeno raggiungendo un'istanza di Caddy.


### Log

Cosa c'è nei log di Caddy? Per impostazione predefinita, questi vengono scritti nel terminale che ha avviato il processo. Se eseguite Caddy in modalità "distaccata" (detached), ad esempio come servizio di sistema, potreste dover recuperare i log da un'altra parte.

Si noti che i log delle richieste HTTP ("access logs") sono diversi dai log di processo e devono essere abilitati esplicitamente nella configurazione.

Potreste anche voler abilitare il logging a livello DEBUG, se non l'avete già fatto.

In ogni caso, una delle prime cose da fare è guardare i log. *Tutti.* Il contesto del messaggio è importante, quindi una singola riga di log isolata è raramente utile. Raccoglietene più di quante pensiate di averne bisogno e conservatele durante tutto il processo di risoluzione dei problemi.

Ci sono indizi nei log?


Riconoscere e dubitare delle supposizioni
-----------------------------------------

Prima di proseguire oltre, dobbiamo sottolineare quanto sia fondamentale criticare ciò che si suppone. Tutti facciamo supposizioni basate su ciò a cui siamo abituati e su ciò che ci aspettiamo. "Siate consapevoli delle vostre supposizioni, e grande sarà il vostro potere." (&mdash;Yoda, o qualcosa del genere.)

Ad esempio, una supposizione comune è che dopo aver ricompilato Caddy, eseguendo `caddy` verrà eseguito il nuovo codice. Questo è vero solo se il binario compilato ha sostituito quello presente nel vostro `$PATH`. Invece, di solito l'invocazione corretta è `./caddy`.

Le supposizioni si stratificano man mano che il vostro deployment o la vostra configurazione diventano più complessi. Ad esempio, il deployment in Docker comporta la ricostruzione di un'immagine e la sua esecuzione, il che moltiplica le supposizioni che potreste fare.

Molte domande e segnalazioni di bug finiscono per essere problemi con le configurazioni di sistema e di rete esterne, non con Caddy stesso. Ad esempio, se non riuscite a connettervi alla vostra istanza di Caddy, ma Caddy è chiaramente in esecuzione, probabilmente supponete che non sia un problema di DNS. Suggerimento: è quasi sempre il DNS.

Anche solo supporre di aver ricaricato una configurazione, quando in realtà non è così, è un errore comune. Sforzatevi di essere rigorosi nel vostro processo. Verificate ad ogni livello.


Riprodurre il comportamento
---------------------------

Questo è un passaggio chiave che spesso fa sì che i problemi si risolvano da soli: fate in modo che il problema si verifichi di nuovo.

Nello specifico, fatelo accadere di nuovo *nel modo più minimale possibile*. Eliminate configurazioni non necessarie, passaggi di deployment, fattori ambientali, ecc., finché il problema non scompare.

Una strategia comune è eliminare una sola cosa alla volta e riprovare, finché il problema non scompare. Allora quella cosa che avete rimosso è probabilmente la causa, o &mdash; e questo è un buon momento per dubitare delle supposizioni &mdash; la causa è una combinazione dell'ultima cosa e di ciò che avete rimosso in precedenza. Verificate aggiungendo di nuovo le prime cose rimosse. Restringete il campo.

Un'altra idea è eliminare circa la metà di tutto ad ogni iterazione e, una volta che il problema scompare, eliminare solo la metà di quella metà, e così via. Questo è come una ricerca binaria e può essere più veloce.

In alternativa, invece dell'eliminazione, potreste invertire queste strategie e costruire incrementalmente la vostra configurazione o scenario da zero, riprovando ogni volta, finché il problema non appare.

Spesso, questo processo da solo identificherà il problema e la soluzione potrebbe diventare ovvia. In caso contrario, potrete almeno scrivere i passaggi minimi per riprodurre il problema.


Esplorare i comportamenti
-------------------------

Con i passaggi noti per riprodurre il problema, sarete in una buona posizione per diagnosticarne la causa. Ciò comporta armeggiare e, se siete esperti, leggere il codice.

Se non riuscite a spiegare perché il problema si stia verificando, variate il comportamento. Apportate una piccola modifica e riprovate. Ad esempio, se la vostra configurazione coinvolge un'espressione regolare, cambiate/semplificate l'espressione &mdash; o rimuovetela del tutto &mdash; e vedete se ottenete *qualcosa* che assomigli al comportamento che state cercando. Anche se non è quello che volete, almeno saprete che il problema risiede nell'espressione regolare o nella configurazione.

Mentre esplorate, notate i pattern di ciò che funziona e cosa no. Questo dovrebbe condurvi verso la soluzione.

Se trovate una soluzione, potete decidere se debba essere considerata un bug o meno. A volte non è ovvio; va bene pubblicare una issue con i vostri esperimenti e ottenere comunque un feedback dai manutentori.

E se non è un bug, congratulazioni! Avete risolto un problema e imparato almeno qualcosa nel processo.

Considerate di pubblicare la vostra esperienza [nel forum](https://caddy.community) per aiutare altri che potrebbero incontrare lo stesso problema.
