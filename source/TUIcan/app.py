import curses
import sys

from signal import signal, SIGWINCH
from TUIcan.window import BackgroundWindow, MenuWindow


class Screen:
    """Main class for a TUI full screen applications.

    ============
    Requirements
    ============

    (1) `stdscr` ... : The 'standard screen' curses object.

    (2) `size` ..... : A tuple in the form of (COLUMNS, ROWS) to
                       specify the minimum number of characters per
                       line (COLUMNS) and minimum number of lines
                       (ROWS) required to draw the screen.

                       Default: 60 columns x 25 rows (60, 25).

    ================
    Acknowledgements
    ================

    (1) https://stackoverflow.com/questions/14200721/
        how-to-create-a-menu-and-submenus-in-python-curses

    (2) https://stackoverflow.com/questions/5161552/
        python-curses-handling-window-terminal-resize
    """

    SHOW_WINDOWS_KEYS = [
        curses.KEY_F1,
        curses.KEY_F2,
        curses.KEY_F3,
        curses.KEY_F4,
        curses.KEY_F5,
        curses.KEY_F6,
        curses.KEY_F7,
        curses.KEY_F8
    ]

    def __init__(self, stdscr, size=(60, 25), actions={}):
        stdscr.clear()
        self.minyx = (size[1], size[0])
        self.screen = self.draw_screen(stdscr)
        y, x = self.screen.getmaxyx()
        if y < self.minyx[0] or x < self.minyx[1]:
            self.exit()
        self.mainframe = BackgroundWindow(
            self.screen, self.minyx, title='MAINFRAME')
        self.menu = None
        self.menu_actions = {
            'Toggle this Menu': self.toggle_menu_on_off,
            'Beep': curses.beep,
            'Flash': curses.flash,
            'Quit': self.exit
        }
        self.actions = actions
        for k in self.menu_actions.keys():
            self.actions[k] = self.menu_actions[k]
        self.menu = MenuWindow(
            self.screen, self.minyx,
            colours=(8, 1), items=list(self.actions.keys()))
        curses.napms(100)

    def draw_screen(self, stdscr):
        signal(SIGWINCH, self.resize_screen)
        curses.noecho()
        stdscr.keypad(True)
        curses.cbreak()
        curses.curs_set(0)
        if curses.has_colors():
            curses.init_pair(
                1, curses.COLOR_CYAN, curses.COLOR_BLUE)
            curses.init_pair(
                2, curses.COLOR_WHITE, curses.COLOR_BLUE)
            curses.init_pair(
                3, curses.COLOR_BLACK, curses.COLOR_BLUE)
            curses.init_pair(
                4, curses.COLOR_YELLOW, curses.COLOR_BLUE)
            curses.init_pair(
                5, curses.COLOR_CYAN, curses.COLOR_BLUE)
            curses.init_pair(
                6, curses.COLOR_YELLOW, curses.COLOR_RED)
            curses.init_pair(
                7, curses.COLOR_BLACK, curses.COLOR_YELLOW)
            curses.init_pair(
                8, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        else:
            for i in range(1, 8):
                curses.init_pair(i, curses.COLOR_WHITE, curses.COLOR_BLACK)
        return stdscr

    def resize_screen(self, signum, frame):
        curses.endwin()
        curses.initscr()
        self.refresh_screen()

    def blank_screen(self):
        def set_screen_border():
            self.screen.border()
            y, x = self.screen.getmaxyx()
            left_text = 'Press [C-c] for menu'
            right_text = f'{x}x{y}'
            if y < self.minyx[0] or x < self.minyx[1]:
                pass
            else:
                self.screen.addstr(y-1, 2, left_text)
                self.screen.addstr(
                    y-1, x-len(right_text)-2, right_text)
        self.screen.clear()
        set_screen_border()
        self.screen.refresh()

    def _print_warning(self):
        y, x = self.screen.getmaxyx()
        warning = f'> {self.minyx[1]}x{self.minyx[0]} ' + \
            'character display required <'
        if x >= len(warning)+2:
            self.screen.addstr(
                round(y/2),
                round(x/2)-round(len(warning)/2),
                warning, curses.A_BOLD)
        return True

    def refresh_screen(self):
        self.blank_screen()
        y, x = self.screen.getmaxyx()
        if y < self.minyx[0] or x < self.minyx[1]:
            self._print_warning()
        else:
            self.redraw_screen()
        self.screen.refresh()
        return True

    def redraw_screen(self):
        self.mainframe.update()
        try:
            self.menu.update()
        except AttributeError as e:
            pass

    def toggle_menu_on_off(self):
        self.menu.toggle

    def exit(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def wait_for_key(self):
        curses.noecho()
        self.screen.keypad(True)
        curses.cbreak()
        curses.curs_set(0)
        while True:
            curses.flushinp()
            curses.napms(10)
            self.refresh_screen()
            try:
                self.key = self.screen.getch()
            except KeyboardInterrupt:
                self.key = None
                self.toggle_menu_on_off()
            if self.key == ord('Q'):
                self.exit()
            elif self.key == ord('x'):
                self.toggle_menu_on_off()
            elif self.key == curses.KEY_UP:
                if self.menu:
                    self.menu.move_down()
                else:
                    pass
            elif self.key == curses.KEY_DOWN:
                if self.menu:
                    self.menu.move_up()
                else:
                    pass
            elif self.key == curses.KEY_LEFT:
                pass
            elif self.key == curses.KEY_RIGHT:
                pass
            elif self.key in [10, 13, curses.KEY_ENTER]:
                if self.menu.show:
                    position = self.menu.position
                    actions = list(self.actions.keys())
                    action = actions[position]
                    self.actions[action]()
                else:
                    pass


if __name__ == "__main__":
    pass
