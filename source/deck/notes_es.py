N={
1:"""[1:00] Apertura.
Hola a todos. Esta sesión la crearon Andrea Griffiths, de GitHub, y Shishir Tewari, de Procore, para GitHub Universe 2026. Hoy os la presento yo.
Durante los próximos 40 minutos, quedaos con una sola idea: escribes el conocimiento una vez, y cualquier agente puede usarlo.""",
2:"""[1:30] El problema. Pedir que levanten la mano, esperar 3 segundos.
Levantad la mano si esta semana habéis vuelto a explicarle la misma tarea a un agente… Mantenedla si lo que explicabais no está escrito en ningún sitio.
Ese es el problema: el contexto desaparece al cerrar la ventana del chat, y a veces solo vive en la cabeza de una persona. Para nosotros, es "Nicolas": la persona a la que llamas el viernes por la noche cuando todo se rompe.""",
3:"""[3:00] El caso Procore (Shishir).
Tomemos Procore, una empresa de software para el sector de la construcción. Allí, cada pipeline de datos sigue los mismos 7 pasos: fuentes, métricas, esquema, código, backfill, tests y despliegue. Y aun así, antes de las skills, cada uno se construía desde cero.
Lo difícil no son los pasos, es el criterio: el nivel de detalle adecuado, el nombre correcto, los joins que duplican filas, lo que nunca debe llegar al warehouse sin revisión.
Un ejemplo sencillo de duplicación: hago un join de los tickets con sus comentarios y luego cuento los tickets. Un ticket con 5 comentarios cuenta 5 veces. No hay error, pero el resultado está mal, y solo un experto lo ve.
Antes de las skills, Procore solo tenía cuatro de estos expertos, y todo pasaba por ellos. Con las skills, siguen definiendo las reglas, pero ya no son los únicos que las aplican.""",
4:"""[2:00] ¿Qué es una skill?
Una skill es simplemente una carpeta que el agente puede encontrar y cargar. El archivo principal es SKILL.md.
El agente la carga paso a paso. Primero, solo lee el nombre y la descripción, que no cuesta casi nada. Si la petición encaja, lee las instrucciones. Y los archivos extra, como referencias o scripts, solo si los necesita. Así, el contexto sigue siendo ligero.
Lo clave es la descripción: es lo que activa la skill. Si está mal escrita, la skill nunca se usará.""",
5:"""[2:30] El bucle del verificador.

Andrea escribió varias skills de verificación, como proof-review. Hoy os enseño el Proof Agent. Su trabajo: verificar el código escrito por un agente. Porque volvemos al problema de Procore: si siempre revisa el mismo experto, todo pasa por él. Así que Andrea tuvo la idea de escribir el conocimiento del revisor en una skill, y dársela al Proof Agent.

El principio es sencillo: no le pides a un alumno que corrija su propio examen. Con un agente, igual. Por eso tenemos el Proof Agent, que verifica.

A la izquierda, las entradas: la petición original, los archivos modificados y el diff. Pero nunca la opinión del agente que escribió el código sobre su propio trabajo.

En el centro, el Proof Agent, que se ejecuta en una GitHub Action.

A la derecha, el veredicto: PASS, FAIL o PARTIAL, siempre con el archivo y la línea como prueba.

Si no está bien, lo corregimos y volvemos a verificar. Hacemos un bucle, como en el diagrama de abajo.

Ojo: solo lee el diff, no ejecuta el código.

Os lo enseño de verdad.""",
6:"""[4:00] DEMO 1: Proof Agent.
Pestañas: proof-agent SKILL.md + https://github.com/AndreaGriffiths11/teamxray/pull/75
1. Frontmatter name + description: "Dos líneas deciden cuándo se carga la skill."
2. Sección When to Verify (3+ archivos, *auth*, *secret*, Dockerfile, .env): "Solo donde el riesgo es real."
3. "Do NOT share the worker's self-assessment": "Esta línea es toda la idea."
4. PR #75, comentarios del Proof Agent. FAIL: ci-cd.yml hacia la línea 119, inyección de shell a través de un tag de release. "Archivo, línea, motivo. A un humano se le podría haber escapado fácilmente."
5. PARTIAL: líneas 42-43, npm test sustituido por vitest. "No está mal, pero puede perder tests. PARTIAL: tiene que decidir un humano."
6. Historial: PARTIAL, FAIL, PARTIAL, PARTIAL, PASS. "Corregir, volver a verificar."
7. block-on-fail: false: "Aquí era consultivo. La decisión del merge sigue en tus reglas de rama, no en el modelo."
Frase de cierre: las skills apoyan la responsabilidad de los ingenieros sobre la release, no la sustituyen.
Plan B: vídeo proof-agent-narrated.mp4 (3:43).""",
7:"""[3:00] Estándares de diseño.

El Proof Agent es una skill para una sola tarea: verificar. Pero un trabajo es una cadena de tareas. En Procore, crear una métrica significa encontrar las tablas, poner nombres, programar, probar y desplegar. Y todo ese conocimiento vive en la cabeza de unos pocos expertos.

Así que el equipo de Shishir creó dataforge: cuatro skills que trabajan juntas. Ninguna conoce los datos: todo el contexto de negocio está en un único archivo, el manifest.

En la diapositiva hay tres reglas, y cada una corresponde a una skill.

Una: forge-init descubre, no adivina. Lee el código existente para entender cómo se construyen y se nombran las tablas. Si no encuentra algo, escribe "unsupported".

Dos: forge-dbx es la única que habla con la base de datos. Un agente puede escribir SQL, pero forge-dbx le da las reglas de la empresa: nada de datos de clientes en bruto, zonas en orden y nada de adivinar. Es el código de circulación. Y de regalo, cambiar de base de datos, DuckDB o Databricks, es una línea en el manifest.

Tres: forge-lint guía antes y comprueba después. Las reglas del equipo se cargan antes de que el agente escriba el código, no solo al final.

Y la cuarta, forge-builder, es el director de orquesta: hace que las tres trabajen juntas, desde la issue hasta la PR.

La prueba de que funciona: Procore publicó estas skills como open source, sin cambiar nada. En la demo, las voy a usar para otro negocio, la atención al cliente. Solo cambia el manifest.""",
8:"""En una frase: las skills son reutilizables. Escribes las reglas una vez y funcionan para otro negocio, sin reescribir nada.

Lo que demuestra la demo, en 2 puntos:
1. Reutilizables. Procore escribió estas 4 skills para su negocio, la construcción. Aquí las uso tal cual para otro negocio, la atención al cliente. Solo cambia el manifest.
2. De un ticket vago a un trabajo terminado. Un humano escribe una petición vaga ("cuenta las incidencias"). El agente, guiado por las skills, hace todo el trabajo de un ingeniero de datos: explorar, diseñar, crear las tablas, probar, desplegar y abrir una PR. Sigue las reglas de la empresa y un humano mantiene la decisión final.

La analogía: las skills son el libro de recetas de un chef, y el manifest es la cocina. Cambias de cocina, la receta sigue igual, y el plato sigue saliendo bien.

TRANSICIÓN
"Eso era en Copilot CLI. Ahora, cojamos las mismas skills y abrámoslas en otro agente: Copilot en VS Code.\"""",
9:"""[4:00] DEMO 3: las mismas skills, otro agente (Copilot en VS Code)

CONCLUSIÓN
"¿Qué acabamos de ver?
Uno. Las skills son portables: la misma carpeta funciona en Copilot CLI y en VS Code, sin reescribir nada.
Dos. El humano mantiene el control: los permisos no los decide la skill, los decide la herramienta. Rechacé la pull request, y no se creó.
Tres. Cambiar de motor cuesta una línea: duckdb pasa a ser databricks, y no cambia ninguna skill, fase ni hook.
Así que: escribes el conocimiento una vez, y funciona en cualquier agente. Build once, run on any agent."

TRANSICIÓN
"Pero ¿cómo es esto técnicamente posible? Cada agente espera sus skills en un formato distinto. Veamos cómo escribir las skills una sola vez, para todos los agentes.\"""",
10:"""[1:30] Una fuente, tres paquetes.

"Cada agente quiere su propio formato. Claude Code, Cursor y Copilot no leen los mismos archivos.
Así que escribes las skills una sola vez, en Markdown normal, en skills/SKILL.md. Un script genera los tres paquetes, uno para cada agente.
Y en cada cambio, la CI comprueba que las tres copias son idénticas a la fuente. Nadie las edita a mano, así que nunca se desvían.
Es exactamente la carpeta que usamos en la demo.
Entonces la skill viaja. Pero ¿viaja todo? No.\"""",
11:"""[1:30] Qué es portable y qué aporta la herramienta.

"A la izquierda, lo que es portable y pasa de un agente a otro: el procedimiento, es decir, el SKILL.md, los scripts, las referencias y los assets.
A la derecha, lo que no se mueve: lo aporta la herramienta en la que se ejecuta la skill, por ejemplo VS Code, Copilot CLI o Claude Code. El modelo, las herramientas, los permisos y las credenciales vienen de ella.
Lo visteis en la demo: VS Code me pidió permiso para la pull request, no la skill. La skill sabe cómo consultar databricks, pero el acceso lo concede VS Code.
Una última pregunta: ¿todo debería convertirse en una skill?\"""",
12:"""[1:30] ¿Skill o aplicación?

"No. Una skill es un conocimiento acotado y reutilizable: una checklist, una release, una migración, un pipeline de métricas.
En cuanto necesitas una interfaz estable, un estado compartido, un registro de auditoría, un proceso de larga duración o una regla aplicada fuera del modelo, construye una aplicación.
Por ejemplo, una checklist de release es una skill. Una aprobación de despliegue auditada para cumplimiento normativo es una aplicación, o la CI.
Entonces, en concreto, ¿por dónde empezáis el lunes?\"""",
13:"""[1:30] Tres cosas para el lunes.
Una: pon el contexto de negocio en un único archivo, un manifest.
Dos: dale a cada skill un único camino de ejecución.
Tres: las instrucciones guían la generación, las comprobaciones la imponen. Son los tests y las reglas de política los que bloquean el merge o el despliegue, no las buenas intenciones del modelo.""",
14:"""[1:00] Vuestros deberes.
Elegid una tarea que siempre tenéis que explicar. Escribid lo que necesita, dónde se detiene y lo que ve el revisor.
Preguntad al compañero al que siempre interrumpen, vuestro "Nicolas". Versionadla, ejecutadla en vuestro cliente y mejoradla.""",
15:"""[0:30] Gracias.
Todo está en gh.io/skills26: las diapositivas, las dos demos y las grabaciones. Gracias a Andrea Griffiths y Shishir Tewari por este contenido (licencia CC BY 4.0).""",
16:"""Opiniones.
Por favor, dejad vuestra opinión escaneando el código QR: nos ayuda a mejorar la sesión. Y ahora, vuestras preguntas.""",
}
