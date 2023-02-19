import curses


class DefaultWindow:
    """
    """

    def __init__(
            self, screen, minyx, colours=(1, 2), title=None, fill_char=' '):
        self.screen = screen
        self.minyx = minyx
        self.colours = colours
        self.title = title
        self.fill_char = fill_char
        self.mode = curses.A_NORMAL
        self.frame = None

    def update(self):
        self.height, self.length = (0, 0)
        self.y, self.x = (0, 0)
        self.frame = self.draw_frame()
        self.frame.refresh()
        return True

    def _fill_with(self, window):
        if not self.fill_char:
            character = ' '
        else:
            character = self.fill_char
        y, x = window.getmaxyx()
        if y < self.minyx[0] or x < self.minyx[1]:
            for j in range(1, y-1):
                for i in range(1, x-1):
                    window.addnstr(
                        j, i, character, window.getmaxyx()[1], self.mode)
        return True

    def draw_frame(self):
        frame = self.screen.subwin(
            self.height, self.length, self.y, self.x)
        frame.border()
        frame.bkgd(' ', curses.color_pair(self.colours[0]))
        self._fill_with(frame)
        y, x = frame.getmaxyx()
        if self.title:
            frame.addnstr(
                0, 2, f' {self.title.upper()} ', x-1, self.mode)
            for col in range(1, x-1):
                frame.addch(1, col, curses.ACS_HLINE, self.mode)
        window = frame.subwin(y-2, x-2, self.y+1, self.x+1)
        window.bkgd(' ', curses.color_pair(self.colours[1]))
        frame.refresh()
        return window


class BackgroundWindow(DefaultWindow):
    """
    """

    def __init__(
            self, screen, minyx, colours=(1, 2), title=None, fill_char=' '):
        super().__init__(screen, minyx, colours, title, fill_char)
        self.mode = curses.A_NORMAL
        self._text = ''
        self.update()

    def update(self):
        y, x = self.screen.getmaxyx()
        self.height, self.length = (y-2, x-4)
        self.y, self.x = (1, 2)
        self.frame = self.draw_frame()
        self.frame.refresh()
        return True

    def set_background(self, m):
        self._text = m

    def draw_background(self):
        if not self._text:
            return False
        zoom = 1
        max_y, max_x = self.frame.getmaxyx()
        if max_y < self.minyx[0] or max_x < self.minyx[1]:
            for j in range(0, len(self._text)):
                y = 1 + j * zoom
                if y + zoom >= max_y:
                    break
                for i in range(0, len(self._text[j])-1):
                    x = i * zoom
                    if x + zoom == max_x:
                        continue
                    t, c = self._text[j][i].tile
                    for yy in range(0, zoom):
                        for xx in range(0, zoom):
                            self.frame.addstr(
                                y+yy, x+xx, t, curses.color_pair(c))
        return True


class MenuWindow(DefaultWindow):
    """
    """

    def __init__(self, screen, minyx, colours=(1, 2), items=None):
        super().__init__(screen, minyx, colours)
        self.mode = curses.A_NORMAL
        self.items = items
        self._position = 0
        self.frame = None
        self.show = False
        self.update()

    @property
    def position(self):
        return self._position

    @property
    def toggle(self):
        self.show = not self.show
        self.update()
        return True

    def update(self):
        if not self.show:
            self._position = 0
            return False
        y, x = self.screen.getmaxyx()
        self.y, self.x = (4, x-5)
        width = max([len(i) for i in self.items]) + 4
        self.height = min(
            self.minyx[0]+self.y, len(self.items) + 2)
        self.length = min(self.minyx[1]+self.x, width)
        self.x -= self.length
        self.frame = self.draw_frame()
        max_length = max([len(k) for k in self.items])
        for i, item in enumerate(self.items):
            item += ' ' * (max_length - len(item))
            if i == self._position:
                self.frame.addstr(i+1, 1, f' {item} ', curses.A_REVERSE)
            else:
                self.frame.addstr(i+1, 2, item)
        self.frame.refresh()
        return True

    def draw_frame(self):
        frame = curses.newwin(
            self.height, self.length, self.y, self.x)
        frame.border()
        frame.bkgd(' ', curses.color_pair(self.colours[0]))
        return frame

    def move_down(self):
        if self.show:
            self._position = max(0, self._position-1)

    def move_up(self):
        if self.show:
            self._position = min(len(self.items)-1, self._position+1)
