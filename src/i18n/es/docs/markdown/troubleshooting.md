Estrategias de resolución de problemas
=====================

Esta página presenta un marco general y metódico para solucionar por tu cuenta la mayoría de problemas que puedas encontrar al usar Caddy *sin usar IA*. Recomendamos pasos similares cuando pides ayuda en nuestros foros. En muchos casos, puedes responderte tú mismo o arreglar el problema aplicando un razonamiento crítico.


¿Qué sabes?
-----------------

Puede que no sepas cuál es el problema, qué lo causa o cómo solucionarlo, así que empecemos por algunas cosas básicas de las que seguramente sí estás seguro:

### Qué esperas

Dilo en voz alta, en tu cabeza o escríbelo. Sé claro y específico para que no haya dudas ni ambigüedad. Incluso puedes explicarte a ti mismo *por qué* esperas eso.

"Debe funcionar" no es una buena expectativa.

"Espero una redirección 301 cuando hago una solicitud a esta URI" es mucho mejor.


### Comportamiento actual

Observa lo que está ocurriendo. ¿Qué está pasando *exactamente* y cómo contrasta con tu expectativa? Sintetiza lo que sabes.

"No funciona" no es útil y es un enfoque superficial; evita esa frase salvo que sea un atajo para describir un comportamiento específico que ya se haya documentado con detalle.

"En lugar de una respuesta 301, recibo una respuesta 200, aunque sí veo la cabecera `Server: Caddy`", es mucho mejor porque compara y contrasta lo que sabes con lo que esperas, y sintetiza otra información conocida, lo que indica que la solicitud al menos llega a una instancia de Caddy.


### Registros

¿Qué hay en los registros de Caddy? Por defecto, se escriben en la terminal desde la que se inició el proceso. Si se ejecuta de forma "desvinculada" como servicio del sistema, puede que tengas que obtener los registros en otro lugar.

Ten en cuenta que los registros de solicitudes HTTP ("access logs") son distintos de los registros de proceso y debes habilitarlos explícitamente en tu configuración.

También puede ser útil habilitar el nivel DEBUG si aún no lo has hecho.

Pero, de cualquier modo, una de las primeras cosas que debes hacer es revisar los registros. *Todos*. El contexto del mensaje importa, así que una sola línea de registro aislada suele ser de poca utilidad. Recopila más de lo que crees necesitar y guárdalo durante todo el proceso de resolución.

¿Hay pistas en los registros?


Reconocer y cuestionar supuestos
-------------------------------

Antes de seguir, tenemos que recalcar lo importante que es cuestionar lo que supones. Todos hacemos suposiciones basadas en lo que estamos acostumbrados y esperamos. "Si eres consciente de tus suposiciones, tu poder será mayor" (—Yoda, o algo así).

Por ejemplo, una suposición común es que, tras recompilar Caddy, ejecutar `caddy` hará que se use el código nuevo. Esto solo es cierto si el binario compilado reemplazó al que está en tu `$PATH`. Normalmente, la invocación correcta es `./caddy`.

Las suposiciones se acumulan a medida que el despliegue o la configuración se vuelven más complejos. Por ejemplo, desplegar en Docker implica reconstruir una imagen y ejecutarla, lo cual multiplica las suposiciones que puedes hacer.

Muchas preguntas y reportes de errores terminan siendo problemas de configuración del sistema o de red externos, no de Caddy. Por ejemplo, si no puedes conectarte a tu instancia de Caddy, pero Caddy claramente está en ejecución, probablemente asumas que no es DNS. Pista: casi siempre es DNS.

Incluso el simple hecho de asumir que recargaste una configuración cuando en realidad no lo hiciste es un error frecuente. Procura ser riguroso en tu proceso. Verifica en todos los niveles.


Reproducir el comportamiento
----------------------

Este es un paso clave que a menudo hace que los problemas se resuelvan solos: reproducir el problema.

En concreto, haz que ocurra otra vez *de la forma más mínima posible*. Elimina configuración innecesaria, pasos de despliegue y factores del entorno, hasta que el problema desaparezca.

Una estrategia habitual es eliminar solo un elemento cada vez y volver a probar hasta que el problema desaparezca. Entonces, ese elemento que quitaste probablemente sea la causa, o bien —y aquí de nuevo conviene cuestionar supuestos— alguna combinación de ese elemento y el anterior. Verifícalo añadiendo de nuevo las cosas en el orden inverso. Así se acota.

Otra idea es eliminar aproximadamente la mitad de los elementos en cada iteración y, cuando el problema desaparezca, eliminar solo la mitad de esa mitad, y así sucesivamente. Esto es como una búsqueda binaria y puede ser más rápido.

Alternativamente, en lugar de eliminar, puedes invertir estas estrategias y construir tu configuración o escenario de forma incremental desde cero, reintentando cada vez, hasta que aparezca el problema.

A menudo, este proceso por sí solo identifica el problema y la solución puede volverse evidente. Si no, al menos puedes dejar por escrito los pasos mínimos para reproducirlo.


Explorar comportamientos
-----------------

Con los pasos para reproducir el problema ya conocidos, estás bien situado para diagnosticar una causa. Esto implica probar, y si sabes, leer el código.

Si no puedes explicar por qué ocurre el problema, varía el comportamiento. Haz un cambio pequeño y vuelve a probar. Por ejemplo, si la configuración usa una expresión regular, cambia o simplifica la expresión, o elimínala por completo y observa si obtienes *algo* parecido al comportamiento que buscas. Aunque no sea exactamente lo que quieres, al menos sabrás que se trata de un problema de la expresión regular o de la configuración.

Mientras exploras, observa patrones de lo que funciona y de lo que no. Eso debería llevarte por el camino de la solución.

Si encuentras una solución, entonces puedes decidir si debe considerarse un bug o no. A veces no es obvio si es un bug; no pasa nada si abres una incidencia con tus experimentos y pides retroalimentación a los mantenedores.

Y si no es un bug, ¡enhorabuena! Resolviste un problema y aprendiste algo en el proceso.

Considera compartir tu experiencia [en el foro](https://caddy.community) para ayudar a otros que puedan encontrarse con el mismo problema.
