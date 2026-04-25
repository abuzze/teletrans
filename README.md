# Telegram Italienisch-Deutsch Vokabeltrainer

Telegram-Bot der italienische Wörter übersetzt, mit Metadaten anreichert und in Google Sheets speichert. Inklusive Quiz-Modus zum Lernen.

## Setup

### 1. Telegram Bot erstellen
1. Öffne [@BotFather](https://t.me/BotFather) in Telegram
2. Sende `/newbot` und folge den Anweisungen
3. Kopiere den Bot-Token

### 2. Anthropic API Key
1. Erstelle einen Account auf [console.anthropic.com](https://console.anthropic.com)
2. Erstelle einen API Key unter Settings → API Keys

### 3. Google Sheets API
1. Gehe zu [Google Cloud Console](https://console.cloud.google.com)
2. Erstelle ein neues Projekt
3. Aktiviere die **Google Sheets API** und **Google Drive API**
4. Erstelle unter "Credentials" einen **Service Account**
5. Erstelle einen Key (JSON) für den Service Account und lade die Datei herunter
6. Speichere die Datei als `credentials.json` im Projektordner
7. Erstelle ein neues Google Sheet mit dem Namen **"Vocabolario"**
8. Teile das Sheet mit der E-Mail-Adresse des Service Accounts (steht in der JSON-Datei unter `client_email`)

### 4. Projekt einrichten
```bash
cd tele_translater
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env mit deinen Werten ausfüllen
```

### 5. Bot starten
```bash
python bot.py
```

## Verwendung

| Befehl | Beschreibung |
|--------|-------------|
| Wort senden | Übersetzt das italienische Wort |
| `/quiz` | Startet ein Vokabelquiz (5 Fragen) |
| `/stats` | Zeigt Anzahl gespeicherter Wörter |
| `/cancel` | Bricht laufendes Quiz ab |


## Building the docker container

From the main directory run 

```
docker build -t teletrans:v99 -t teletrans:latest -f docker/Dockerfile .
```

Run the container 

```
docker run --rm -it teletrans:latest
```

Use the docker-compose.yml to run the app permanently

```
cd docker
docker compose up -d
```
