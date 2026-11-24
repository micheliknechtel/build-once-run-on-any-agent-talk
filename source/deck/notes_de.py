N={
1:"""[1:00] Eröffnung.
Hallo zusammen. Diese Session wurde von Andrea Griffiths von GitHub und Shishir Tewari von Procore für GitHub Universe 2026 erstellt. Heute präsentiere ich sie Ihnen.
Merken Sie sich für die nächsten 40 Minuten eine einzige Idee: Sie schreiben das Know-how einmal, und jeder Agent kann es nutzen.""",
2:"""[1:30] Das Problem. Um Handzeichen bitten, 3 Sekunden warten.
Heben Sie die Hand, wenn Sie diese Woche einem Agenten dieselbe Aufgabe noch einmal erklärt haben… Lassen Sie sie oben, wenn das, was Sie erklärt haben, nirgendwo aufgeschrieben ist.
Das ist das Problem: Der Kontext verschwindet, sobald Sie das Chatfenster schließen, und manchmal existiert er nur im Kopf einer einzigen Person. Bei uns ist das „Nicolas“: die Person, die man am Freitagabend anruft, wenn alles kaputtgeht.""",
3:"""[3:00] Der Fall Procore (Shishir).
Nehmen wir Procore, ein Softwareunternehmen für die Baubranche. Dort folgt jede Datenpipeline denselben 7 Schritten: Quellen, Metriken, Schema, Code, Backfill, Tests, Deployment. Und trotzdem wurde vor den Skills jede Pipeline von Grund auf neu gebaut.
Das Schwierige sind nicht die Schritte, sondern das Urteilsvermögen: der richtige Detailgrad, der richtige Name, die Joins, die Zeilen duplizieren, und was niemals ohne Review ins Warehouse darf.
Ein einfaches Beispiel für Duplikate: Ich verknüpfe Tickets mit ihren Kommentaren und zähle dann die Tickets. Ein Ticket mit 5 Kommentaren zählt 5-mal. Kein Fehler, aber das Ergebnis ist falsch, und nur ein Experte sieht es.
Vor den Skills hatte Procore nur vier solche Experten, und alles lief über sie. Mit Skills legen sie weiterhin die Regeln fest, aber sie sind nicht mehr die Einzigen, die sie anwenden.""",
4:"""[2:00] Was ist ein Skill?
Ein Skill ist einfach ein Ordner, den der Agent finden und laden kann. Die Hauptdatei ist SKILL.md.
Der Agent lädt ihn Schritt für Schritt. Zuerst liest er nur den Namen und die Beschreibung, das kostet fast nichts. Wenn die Anfrage passt, liest er die Anweisungen. Und die zusätzlichen Dateien, wie Referenzen oder Skripte, nur wenn er sie braucht. So bleibt der Kontext schlank.
Der entscheidende Punkt ist die Beschreibung: Sie löst den Skill aus. Wenn sie schlecht geschrieben ist, wird der Skill nie verwendet.""",
5:"""[2:30] Die Prüfschleife.

Andrea hat mehrere Prüf-Skills geschrieben, zum Beispiel proof-review. Heute zeige ich Ihnen den Proof Agent. Seine Aufgabe: Code prüfen, den ein Agent geschrieben hat. Denn wir finden hier das Problem von Procore wieder: Wenn immer derselbe Experte prüft, läuft alles über ihn. Also hatte Andrea die Idee, das Wissen des Reviewers in einen Skill zu schreiben und ihn dem Proof Agent zu geben.

Das Prinzip ist einfach: Man lässt einen Schüler nicht seine eigene Prüfung korrigieren. Bei einem Agenten ist es genauso. Deshalb gibt es den Proof Agent, der prüft.

Links die Eingaben: die ursprüngliche Anfrage, die geänderten Dateien und der Diff. Aber niemals die Meinung des Agenten, der den Code geschrieben hat, über seine eigene Arbeit.

In der Mitte der Proof Agent, der in einer GitHub Action läuft.

Rechts das Urteil: PASS, FAIL oder PARTIAL, immer mit Datei und Zeile als Beleg.

Wenn es nicht gut ist, korrigieren wir und prüfen erneut. Wir drehen eine Schleife, wie im Diagramm unten.

Hinweis: Er liest nur den Diff, er führt den Code nicht aus.

Ich zeige Ihnen das jetzt live.""",
6:"""[4:00] DEMO 1: Proof Agent.
Tabs: proof-agent SKILL.md + https://github.com/AndreaGriffiths11/teamxray/pull/75
1. Frontmatter name + description: „Zwei Zeilen entscheiden, wann der Skill geladen wird.“
2. Abschnitt When to Verify (3+ Dateien, *auth*, *secret*, Dockerfile, .env): „Nur dort, wo das Risiko real ist.“
3. „Do NOT share the worker's self-assessment“: „Diese Zeile ist die ganze Idee.“
4. PR #75, Kommentare des Proof Agent. FAIL: ci-cd.yml um Zeile 119, Shell-Injection über einen Release-Tag. „Datei, Zeile, Grund. Ein Mensch hätte das leicht übersehen können.“
5. PARTIAL: Zeilen 42-43, npm test durch vitest ersetzt. „Nicht falsch, aber es könnten Tests wegfallen. PARTIAL: Ein Mensch muss entscheiden.“
6. Verlauf: PARTIAL, FAIL, PARTIAL, PARTIAL, PASS. „Korrigieren, erneut prüfen.“
7. block-on-fail: false: „Hier war es nur beratend. Die Merge-Entscheidung liegt in Ihren Branch-Regeln, nicht im Modell.“
Schlusssatz: Skills unterstützen die Verantwortung der Engineers für das Release, sie ersetzen sie nicht.
Backup: Video proof-agent-narrated.mp4 (3:43).""",
7:"""[3:00] Design-Standards.

Der Proof Agent ist ein Skill für eine einzige Aufgabe: prüfen. Aber ein Job ist eine Kette von Aufgaben. Bei Procore bedeutet eine Metrik zu erstellen: die Tabellen finden, benennen, coden, testen und deployen. Und all dieses Wissen steckt in den Köpfen einiger weniger Experten.

Also hat Shishirs Team dataforge entwickelt: vier Skills, die zusammenarbeiten. Keiner von ihnen kennt die Daten: Der gesamte Geschäftskontext steckt in einer einzigen Datei, dem Manifest.

Auf der Folie stehen drei Regeln, und jede gehört zu einem Skill.

Erstens: forge-init erkundet, es rät nicht. Es liest den bestehenden Code, um zu verstehen, wie Tabellen gebaut und benannt werden. Wenn es etwas nicht findet, schreibt es „unsupported“.

Zweitens: forge-dbx ist der Einzige, der mit der Datenbank spricht. Ein Agent kann SQL schreiben, aber forge-dbx gibt ihm die Regeln des Unternehmens: keine rohen Kundendaten, Zonen in der richtigen Reihenfolge und kein Raten. Das ist die Straßenverkehrsordnung. Als Bonus ist ein Datenbankwechsel, DuckDB oder Databricks, eine einzige Zeile im Manifest.

Drittens: forge-lint leitet vorher an und prüft danach. Die Regeln des Teams werden geladen, bevor der Agent den Code schreibt, nicht erst am Ende.

Und der vierte, forge-builder, ist der Dirigent: Er lässt die drei zusammenarbeiten, vom Issue bis zum PR.

Der Beweis, dass es funktioniert: Procore hat diese Skills als Open Source veröffentlicht, ohne etwas zu ändern. In der Demo nutze ich sie für einen anderen Geschäftsbereich, den Kundensupport. Nur das Manifest ändert sich.""",
8:"""In einem Satz: Skills sind wiederverwendbar. Sie schreiben die Regeln einmal, und sie funktionieren für einen anderen Geschäftsbereich, ohne etwas neu zu schreiben.

Was die Demo beweist, in 2 Punkten:
1. Wiederverwendbar. Procore hat diese 4 Skills für sein Geschäft geschrieben, das Bauwesen. Hier nutze ich sie unverändert für einen anderen Bereich, den Kundensupport. Nur das Manifest ändert sich.
2. Vom vagen Ticket zur fertigen Arbeit. Ein Mensch schreibt eine vage Anfrage („zähl die Incidents“). Der Agent, geleitet von den Skills, erledigt die ganze Arbeit eines Data Engineers: erkunden, entwerfen, die Tabellen erstellen, testen, deployen, einen PR öffnen. Er folgt den Regeln des Unternehmens, und ein Mensch behält die letzte Entscheidung.

Die Analogie: Die Skills sind das Rezeptbuch eines Kochs, und das Manifest ist die Küche. Sie wechseln die Küche, das Rezept bleibt gleich, und das Gericht ist trotzdem gut.

ÜBERGANG
„Das war in Copilot CLI. Jetzt nehmen wir dieselben Skills und öffnen sie in einem anderen Agenten: Copilot in VS Code.“""",
9:"""[4:00] DEMO 3: dieselben Skills, ein anderer Agent (Copilot in VS Code)

FAZIT
„Was haben wir gerade gesehen?
Erstens. Skills sind portabel: Derselbe Ordner läuft in Copilot CLI und in VS Code, ohne etwas neu zu schreiben.
Zweitens. Der Mensch behält die Kontrolle: Berechtigungen entscheidet nicht der Skill, sondern das Tool. Ich habe den Pull Request abgelehnt, und er wurde nicht erstellt.
Drittens. Ein Engine-Wechsel kostet eine Zeile: duckdb wird zu databricks, und kein Skill, keine Phase und kein Hook ändert sich.
Also: Sie schreiben das Know-how einmal, und es funktioniert mit jedem Agenten. Build once, run on any agent.“

ÜBERGANG
„Aber wie ist das technisch möglich? Jeder Agent erwartet seine Skills in einem anderen Format. Sehen wir uns an, wie man Skills nur einmal schreibt, für alle Agenten.“""",
10:"""[1:30] Eine Quelle, drei Pakete.

„Jeder Agent will sein eigenes Format. Claude Code, Cursor und Copilot lesen nicht dieselben Dateien.
Also schreiben Sie die Skills nur einmal, in einfachem Markdown, in skills/SKILL.md. Ein Skript erzeugt die drei Pakete, eines für jeden Agenten.
Und bei jeder Änderung prüft die CI, dass die drei Kopien mit der Quelle identisch sind. Niemand bearbeitet sie von Hand, also laufen sie nie auseinander.
Das ist genau der Ordner, den wir in der Demo verwendet haben.
Der Skill reist also mit. Aber reist alles mit? Nein.“""",
11:"""[1:30] Was portabel ist, was das Tool bereitstellt.

„Links das, was portabel ist und von einem Agenten zum anderen wandert: die Vorgehensweise, also die SKILL.md, die Skripte, die Referenzen und die Assets.
Rechts das, was nicht wandert: Es wird vom Tool bereitgestellt, in dem der Skill läuft, zum Beispiel VS Code, Copilot CLI oder Claude Code. Das Modell, die Tools, die Berechtigungen und die Zugangsdaten kommen von dort.
Sie haben es in der Demo gesehen: VS Code hat mich um Erlaubnis für den Pull Request gebeten, nicht der Skill. Der Skill weiß, wie man databricks abfragt, aber den Zugriff gewährt VS Code.
Eine letzte Frage: Sollte alles zu einem Skill werden?“""",
12:"""[1:30] Skill oder App?

„Nein. Ein Skill ist abgegrenztes, wiederverwendbares Know-how: eine Checkliste, ein Release, eine Migration, eine Metrik-Pipeline.
Sobald Sie eine stabile Schnittstelle, gemeinsamen Zustand, einen Audit-Trail, einen lang laufenden Prozess oder eine Regel brauchen, die außerhalb des Modells durchgesetzt wird, bauen Sie eine Anwendung.
Zum Beispiel ist eine Release-Checkliste ein Skill. Eine auditierte Deployment-Freigabe für Compliance ist eine Anwendung oder CI.
Also, ganz konkret: Wo fangen Sie am Montag an?“""",
13:"""[1:30] Drei Dinge für Montag.
Erstens: Legen Sie den Geschäftskontext in eine einzige Datei, ein Manifest.
Zweitens: Geben Sie jedem Skill einen einzigen Ausführungspfad.
Drittens: Anweisungen leiten die Generierung, Prüfungen setzen sie durch. Tests und Policy-Regeln blockieren den Merge oder das Deployment, nicht die guten Absichten des Modells.""",
14:"""[1:00] Ihre Hausaufgabe.
Wählen Sie eine Aufgabe, die Sie immer wieder erklären. Schreiben Sie auf, was sie braucht, wo sie aufhört und was der Reviewer sieht.
Fragen Sie die Kollegin oder den Kollegen, die ständig unterbrochen werden, Ihren „Nicolas“. Versionieren Sie es, führen Sie es in Ihrem Client aus, verbessern Sie es.""",
15:"""[0:30] Vielen Dank.
Alles finden Sie unter gh.io/skills26: die Folien, die beiden Demos und die Aufnahmen. Danke an Andrea Griffiths und Shishir Tewari für diese Inhalte (Lizenz CC BY 4.0).""",
16:"""Feedback.
Bitte geben Sie uns Ihr Feedback, indem Sie den QR-Code scannen: Das hilft uns, die Session zu verbessern. Und jetzt zu Ihren Fragen.""",
}
