# Projekt auf dein GitHub bringen

Das Projekt ist bereits ein fertiges Git-Repository mit sechs Commits
(ein Commit pro Entwicklungsschritt). Du musst es nur noch mit einem neuen
GitHub-Repository verbinden und hochladen.

## 1. Entpacken

Entpacke `vorsorge-datasync.zip` an einen Ort deiner Wahl und öffne ein
Terminal in dem entstandenen Ordner `vorsorge-datasync`.

Prüfen, dass die Git-Historie da ist:

```bash
git log --oneline
```

Du solltest sechs Commits sehen (Schritt 1 bis 6).

## 2. Leeres Repository auf GitHub anlegen

Auf github.com → **New repository**:
- Name z. B. `vorsorge-datasync`
- **Kein** README, **keine** .gitignore, **keine** Lizenz hinzufügen
  (das ist alles schon im Projekt – sonst gibt es einen Konflikt)
- Erstellen

GitHub zeigt dir danach die URL, z. B.
`https://github.com/DEIN-NAME/vorsorge-datasync.git`

## 3. Verbinden und hochladen

```bash
# Haupt-Branch auf "main" setzen (Standard bei GitHub)
git branch -M main

# dein neues GitHub-Repo als Remote eintragen (URL anpassen!)
git remote add origin https://github.com/DEIN-NAME/vorsorge-datasync.git

# hochladen
git push -u origin main
```

Beim ersten Push fragt GitHub nach Anmeldung. Am einfachsten über den
Browser (GitHub CLI `gh auth login`) oder mit einem Personal Access Token
als Passwort.

## 4. Fertig

Lade die Seite deines Repositories neu – README, Code und die sechs Commits
sind sichtbar.

## Optional: vor dem Hochladen selbst testen

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                            # sollte 18 Tests grün zeigen
```

## Hinweis zur Autorschaft

Die Commits sind aktuell auf den Namen „GP Koch" und deine E-Mail-Adresse
gesetzt. Falls du für GitHub einen anderen Namen/eine andere E-Mail nutzt,
kannst du das vor dem ersten Push anpassen:

```bash
git config user.name "Dein Name"
git config user.email "deine@email.ch"
```

(Bestehende Commits behalten die alten Angaben; das ist für ein
Demo-Projekt unproblematisch. Wer es vereinheitlichen will, kann die
Historie mit `git rebase` neu schreiben – für dieses Projekt nicht nötig.)
