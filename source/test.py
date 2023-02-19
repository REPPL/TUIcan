import curses
import os

from TUIcan.app import Screen

SIZE = (60, 25)

def main():
    os.system('clear')
    print(
        f'\nMinimum display size is {SIZE[0]} x {SIZE[1]} characters.\n')
    app = curses.wrapper(Screen, size=SIZE)
    app.wait_for_key()


if __name__ == "__main__":
    main()
