from disnake import Intents
from disnake.ext.commands import Bot as _BotBase
from loguru import logger

from src.utils import get_config


class Bot(_BotBase):
    def __init__(self, *args, **kwargs) -> None:
        self.config = get_config()

        intents = Intents.default()
        intents.members = True

        super().__init__(
            intents=intents, command_prefix=self.config.prefix, *args, **kwargs
        )

    @staticmethod
    async def on_connect() -> None:
        logger.info("Connected to Discord.")

    @staticmethod
    async def on_ready() -> None:
        logger.info("Bot is ready.")

    @staticmethod
    async def on_resume() -> None:
        logger.warning("Bot has resumed.")
