from game.config import load_config
from game.loop import GameLoop


def main():
    config = load_config("config.json")
    loop = GameLoop(config)
    loop.run()


if __name__ == "__main__":
    main()
