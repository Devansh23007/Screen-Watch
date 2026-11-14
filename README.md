# Screen Assistant

Watches which window is active, screenshots it when something changes, asks a Groq vision model
to describe it (apps, logos, text), and stores only the text summary.
Screenshots stay in RAM and are never saved unless you set `SAVE_IMAGES=true` in `.env`.
New screen summaries appear in the console and chat window. They include the active video title
when readable and the apps with open windows in the Windows taskbar.

## Setup (Windows)
1. Install Python 3.10+ from python.org (tick "Add to PATH").
2. Get a free API key at https://console.groq.com/keys
3. Open PowerShell in this folder, then run:

       py -m venv .venv
       .\.venv\Scripts\Activate.ps1
       pip install -r requirements.txt
       if (-not (Test-Path .env)) { Copy-Item .env.example .env }

   Edit `.env` and set `GROQ_API_KEY` to your key. `.env` is local and ignored by Git.
4. Run:  `python main.py`

## Test step by step
- python watcher.py      -> prints the active window whenever it changes
- python main.py         -> runs everything; descriptions print in the console,
                            tray icon opens the chat window

## Mac
Use `python3`, `source venv/bin/activate`, `export GROQ_API_KEY=...`.
Grant Screen Recording + Accessibility permission to Terminal/Python in
System Settings > Privacy & Security. (Tray icon support on Mac is limited.)

## Settings
Models, timing, capture, storage, and privacy settings are in `.env`.
History lives in data/history.db (open with "DB Browser for SQLite").

## Models (config.py)
- VISION_MODEL reads screenshots. gpt-oss-120b CANNOT see images, so a vision model is required.
  Groq changes its vision list often; pick one from https://console.groq.com/docs/vision
- CHAT_MODEL (openai/gpt-oss-120b) answers your chat questions using the screen reading + history.
