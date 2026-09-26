import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from openai import APIConnectionError, APIStatusError, APITimeoutError

import bot


class BotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # No real environment variables, .env reads, or network requests in tests.
        self.env = patch.object(bot.os, "getenv", return_value="test-placeholder")
        self.env.start()
        self.addCleanup(self.env.stop)
        self.factory = patch.object(bot, "AsyncOpenAI")
        factory = self.factory.start()
        self.addCleanup(self.factory.stop)
        self.ai = factory.return_value.__aenter__.return_value
        self.ai.responses.create = AsyncMock(
            return_value=SimpleNamespace(output_text="Arrr! Here be an answer.")
        )

    def message(self, text, is_bot=False, in_server=True):
        return SimpleNamespace(
            content=text, author=SimpleNamespace(bot=is_bot),
            channel=SimpleNamespace(send=AsyncMock()),
            guild=SimpleNamespace() if in_server else None,
        )

    async def test_hello_and_ignored_messages(self):
        hello = self.message("$hello")
        await bot.on_message(hello)
        hello.channel.send.assert_awaited_once_with("hello")
        for text, is_bot in [("$hello", True), ("Ahoy!", True), ("", False)]:
            msg = self.message(text, is_bot)
            await bot.on_message(msg)
            msg.channel.send.assert_not_awaited()
        self.ai.responses.create.assert_not_awaited()

    async def test_empty_messages(self):
        for text in ["", "   \n\t"]:
            msg = self.message(text)
            await bot.on_message(msg)
            msg.channel.send.assert_not_awaited()
        self.ai.responses.create.assert_not_awaited()

    async def test_direct_messages(self):
        msg = self.message("Why is the sea blue?", in_server=False)
        await bot.on_message(msg)
        msg.channel.send.assert_not_awaited()
        hello = self.message("$hello", in_server=False)
        await bot.on_message(hello)
        hello.channel.send.assert_awaited_once_with("hello")
        self.ai.responses.create.assert_not_awaited()

    async def test_ordinary_text_and_old_prefix(self):
        for text in ["Ahoy!", "$question Why?", "$question", "$hello there"]:
            msg = self.message(text)
            await bot.on_message(msg)
            self.assertEqual(self.ai.responses.create.call_args.kwargs["input"], text)
            msg.channel.send.assert_awaited_once()

    async def test_missing_key(self):
        for key in ["", "  ", "your_openai_api_key_here"]:
            with patch.object(bot.os, "getenv", return_value=key):
                self.assertIn("OPENAI_API_KEY", await bot.answer_question("Why?"))
        self.ai.responses.create.assert_not_awaited()

    async def test_question_and_mentions(self):
        msg = self.message("  Why is the sea blue?\n")
        await bot.on_message(msg)
        self.assertEqual(self.ai.responses.create.call_args.kwargs["input"],
                         "Why is the sea blue?")
        self.assertEqual(msg.channel.send.call_args.args[0], "Arrr! Here be an answer.")
        self.assertFalse(msg.channel.send.call_args.kwargs["allowed_mentions"].everyone)

    async def test_api_errors(self):
        request = httpx.Request("POST", "https://example.invalid")
        errors = [APIConnectionError(request=request), APITimeoutError(request=request)]
        for status in [401, 429, 500]:
            errors.append(APIStatusError("private details", response=httpx.Response(
                status, request=request), body=None))
        for error in errors:
            self.ai.responses.create.side_effect = error
            answer = await bot.answer_question("Why?")
            self.assertIn("Try again", answer)
            self.assertNotIn("private details", answer)

    async def test_empty_and_long_answers(self):
        self.ai.responses.create.return_value = SimpleNamespace(output_text="  ")
        self.assertIn("No answer", await bot.answer_question("Why?"))
        for text in ["a" * 2000, "a" * 2001, "\U0001f600" * 2001]:
            self.ai.responses.create.return_value = SimpleNamespace(output_text=text)
            answer = await bot.answer_question("Why?")
            self.assertLessEqual(len(answer.encode("utf-16-le")), 4000)
            if len(text) > 2000:
                self.assertTrue(answer.endswith("..."))
            else:
                self.assertEqual(answer, text)

    async def test_hello_while_question_pending(self):
        started, release = asyncio.Event(), asyncio.Event()

        async def pending(**kwargs):
            started.set()
            await release.wait()
            return SimpleNamespace(output_text="Arrr!")

        self.ai.responses.create.side_effect = pending
        task = asyncio.create_task(bot.on_message(self.message("Why?")))
        try:
            await asyncio.wait_for(started.wait(), 1)
            hello = self.message("$hello")
            await asyncio.wait_for(bot.on_message(hello), 1)
            hello.channel.send.assert_awaited_once_with("hello")
            self.assertFalse(task.done())
        finally:
            release.set()
            await task


if __name__ == "__main__":
    unittest.main()
