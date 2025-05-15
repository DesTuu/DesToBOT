import os
from logging.config import dictConfig
import logging
import pathlib
import discord


COOLDOWN_DURATION = 10

activities = [
    discord.Game(name='!help'),
    discord.Streaming(name='!help', url='https://m.twitch.tv/destuuuuuuu'),
    discord.Activity(name='!help', type=discord.ActivityType.listening),
    discord.Activity(name='!help', type=discord.ActivityType.watching),
    discord.Activity(name='!help', type=discord.ActivityType.competing)
]

PREFIX = "//"

HEARTBEAT_TIMEOUT = 60

BASE_DIR = pathlib.Path(__file__).parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

CMD_DIR = BASE_DIR / "cmds"

COG_DIR = BASE_DIR / "cogs"

DB_DIR = BASE_DIR / "db"

BUMP_POINTS_FILE = DB_DIR / "bump_points.json"

QUIZ_QUESTIONS_FILE = DB_DIR / "quiz_questions.txt"

QUIZ_POINTS_FILE = DB_DIR / "quiz_points.json"

LAST_BUMPER_FILE = DB_DIR / "last_bumper.json"

LAST_MSG_ID = DB_DIR / "last_msg_id.txt"

def get_guild_names(bot):
    for i in bot.guilds:
        yield i.name


def on_ready_message(bot):
    if len(set(get_guild_names(bot))) >= 2:
        print(f"Bot znajduje się na takich serwerach jak: {', '.join(get_guild_names(bot))}")
    else:
        print(f"Bot znajduje się na tylko na jednym serwerze: {', '.join(get_guild_names(bot))}")


LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "infos.log"),
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
