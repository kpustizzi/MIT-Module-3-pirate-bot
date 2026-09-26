import os
from pathlib import Path

import discord
from dotenv import load_dotenv
from openai import APIError, AsyncOpenAI


async def answer_question(question):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_api_key_here":
        return "Arrr! The captain needs to set OPENAI_API_KEY before I can answer questions."

    try:
        async with AsyncOpenAI(api_key=api_key, timeout=30.0, max_retries=0) as ai:
            response = await ai.responses.create(
                model="gpt-4.1-mini",
                instructions=(
                    "Answer helpfully in a playful pirate voice. Keep your answer brief: "
                    "two or three short sentences, under 1500 characters."
                ),
                input=question,
                max_output_tokens=300,
                store=False,
            )
        answer = response.output_text.strip()
    except APIError:
        # Never expose exception details, which can include request information.
        return "Arrr! The OpenAI seas be rough. Try again later, or ask the captain to check API access and quota."

    if not answer:
        return "Arrr! No answer came back from the seas. Try asking again."
    # Count UTF-16 units conservatively so emoji also fit Discord's limit.
    if len(answer.encode("utf-16-le")) > 4000:
        answer = answer.encode("utf-16-le")[:3994].decode("utf-16-le", errors="ignore") + "..."
    return answer


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
        return

    parts = message.content.split(maxsplit=1)
    if not parts or parts[0] != "$question":
        return
    question = parts[1].strip() if len(parts) > 1 else ""
    if not question:
        await message.channel.send("Arrr! Ask me something: `$question Why is the sea blue?`")
        return

    answer = await answer_question(question)
    await message.channel.send(answer, allowed_mentions=discord.AllowedMentions.none())


if __name__ == "__main__":
    load_dotenv(Path(__file__).with_name(".env"))
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token or token == "your_discord_bot_token_here":
        raise SystemExit("Set DISCORD_TOKEN in your local .env file before running the bot.")
    client.run(token)
