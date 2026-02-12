from Bot import bot, LOGGER
from Bot.modules import *
from pyrogram import idle
import asyncio

async def main():
    LOGGER.info("Starting...")
    await bot.start()
    LOGGER.info("Started.")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try: asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt: LOGGER.info("Stopped.")
