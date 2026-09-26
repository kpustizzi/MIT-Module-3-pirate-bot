# Minimal Discord bot

Replies `hello` when a person sends exactly `$hello`. Use `$question <text>` for a
brief OpenAI answer in a playful pirate voice. Requires Python 3.10+.

## Setup (Windows PowerShell)

1. Create a virtual environment and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
   ```

2. Create an application in the [Discord Developer Portal](https://discord.com/developers/applications).
   On its **Bot** page, enable **Message Content Intent** under privileged gateway intents.
   In **OAuth2 > URL Generator**, select the `bot` scope and the **View Channels** and
   **Send Messages** permissions. Open the generated URL to invite the bot to your server.

3. For a new installation only, copy the example configuration (skip this if you
   already have `.env`; do not overwrite it):

   ```powershell
   if (-not (Test-Path .env)) { Copy-Item .env.example .env }
   ```

   Edit `.env` locally to set `DISCORD_TOKEN` from the portal's Bot page and
   `OPENAI_API_KEY` from your [OpenAI API project](https://platform.openai.com/api-keys).
   For an existing installation, add the OpenAI key while keeping your Discord token.
   Your OpenAI project needs API access and available quota/billing; API usage can incur charges.
   Never paste either secret into chat, screenshots, source code, or commits.
   `.env` is ignored by Git; `.env.example` contains only placeholders.

4. Start the bot:

   ```powershell
   .\.venv\Scripts\python.exe bot.py
   ```

   Send `$hello` in a server channel the bot can view and send messages in. It should
   respond `hello`. Press Ctrl+C in the terminal to stop it.

## Questions

Send `$question Why is the sea blue?` in Discord. Only the question text is sent
to OpenAI, and the answer is posted to the same channel; no conversation history is sent.
The bot uses `gpt-4.1-mini` with the official SDK's asynchronous Responses API so
other messages can be handled while the request is pending. See the
[OpenAI SDK documentation](https://developers.openai.com/api/docs/libraries).

- Empty questions get a usage hint without calling OpenAI.
- Missing or placeholder OpenAI keys get a setup message; `$hello` still works.
- API failures (including invalid keys, rate limits, and a 30-second request timeout)
  get a friendly error without exposing API details or credentials.
- Empty responses get a retry hint. Long answers are truncated to Discord's
  2,000-character limit, with emoji accounted for. Generated mentions cannot ping users.

Restart the bot after changing your local configuration. Existing environment
variables take precedence over `.env` values.

If it does not respond, check the channel permissions and Message Content Intent
in the portal. The code already enables that intent, as required by the
[discord.py quickstart](https://discordpy.readthedocs.io/en/stable/quickstart.html).
