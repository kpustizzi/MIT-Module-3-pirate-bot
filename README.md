# Minimal Discord bot

Replies `hello` when a person sends exactly `$hello`. Requires Python 3.10+.

## Setup (Windows PowerShell)

1. Create a virtual environment and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
   On its **Bot** page, enable **Message Content Intent** under privileged gateway intents.
   In **OAuth2 > URL Generator**, select the `bot` scope and the **View Channels** and
   **Send Messages** permissions. Open the generated URL to invite the bot to your server.

3. Copy the example configuration:

   ```powershell
   Copy-Item .env.example .env
   ```

   After reviewing these files, edit `.env` locally and replace the placeholder with
   your bot token from the portal's Bot page. Never paste the token into chat, screenshots,
   source code, or commits. `.env` is ignored by Git; `.env.example` contains only a placeholder.

4. Start the bot:

   ```powershell
   .\.venv\Scripts\python.exe bot.py
   ```

   Send `$hello` in a server channel the bot can view and send messages in. It should
   respond `hello`. Press Ctrl+C in the terminal to stop it.

If it does not respond, check the channel permissions and Message Content Intent
in the portal. The code already enables that intent, as required by the
[discord.py quickstart](https://discordpy.readthedocs.io/en/stable/quickstart.html).
