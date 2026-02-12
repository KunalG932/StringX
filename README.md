<div align="center">
  <img src="https://telegra.ph/file/1049e78ce9d6f67cfcdf2-faf067ca2ed756eb61.jpg" alt="StringX" width="500">
  <h1>StringX</h1>
  <p>A modular Telegram Bot for obtaining API credentials and generating session strings for Pyrogram and Telethon.</p>
</div>

## Features
- Generate API ID and API Hash from my.telegram.org directly through the bot.
- Create session strings for Pyrogram, Kurigram, Pyrofork, Hydrogram, and Telethon.
- Clean and simplified codebase for easy maintenance.
- User tracking and statistics.
- MongoDB integration for persistent storage.

## Commands
- /start: Initial greeting and main menu.
- /generate: Create API credentials.
- /session: Create a session string.
- /help: List all available commands.
- /stats: View user and bot statistics.
- /cancel: Terminate the current operation.

## Setup
1. Define environment variables in a .env file:
   - BOT_TOKEN
   - API_ID
   - API_HASH
   - MONGO_URI
2. Install required dependencies:
   `pip install -r requirements.txt`
3. Execute the bot:
   `python manage.py`

## Deployment
Click the button below to deploy this bot to Heroku.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/KunalG932/StringX)
