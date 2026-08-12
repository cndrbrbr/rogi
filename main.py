import curses

from rogue.ui import run


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()
