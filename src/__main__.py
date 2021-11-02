from . import Bot


def main() -> None:
    bot = Bot()

    bot.load_extension("jishaku")

    bot.run()


if __name__ == "__main__":
    main()
