import os
from pathlib import Path

import discord
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == "$hello":
        await message.channel.send("hello")


if __name__ == "__main__":
    load_dotenv(Path(__file__).with_name(".env"))
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token or token == "your_discord_bot_token_here":
        raise SystemExit("Set DISCORD_TOKEN in your local .env file before running the bot.")
    client.run(token)
