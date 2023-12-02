import curses


class TerminalUI:
    col1_msgs = 1
    col2_msgs = 1

    def __init__(self, message1, message2, command_handler):
        self.ch = command_handler

        self.stdscr = curses.initscr()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.refresh()

        if curses.COLS < 103:
            raise Exception("window to small (minimum 103 columns)")

        self.top_message1 = curses.newwin(8, curses.COLS // 2, 0, 0)
        self.top_message1.addstr(message1)
        self.top_message1.refresh()

        self.top_message2 = curses.newwin(1, (curses.COLS // 2) - 1, 0, (curses.COLS // 2) + 1)
        self.top_message2.addstr(message2)
        self.top_message2.refresh()

        self.column1 = curses.newwin(curses.LINES - 9, curses.COLS // 2, 9, 0)
        self.column1.scrollok(True)
        self.column1.refresh()

        self.column2 = curses.newwin(curses.LINES - 2, (curses.COLS // 2) - 1, 1, (curses.COLS // 2) + 1)
        self.column2.scrollok(True)
        self.column2.refresh()

        self.cmd_input = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

    def draw(self):
        for i in range(curses.LINES - 1):
            self.stdscr.addch(i, curses.COLS // 2, '|')
        self.stdscr.refresh()

    def add_text_to_column1(self, text, count=True):
        if count:
            self.column1.addstr(f'{self.col1_msgs}> {text}\n')
            self.col1_msgs += 1
        else:
            self.column1.addstr(f' > {text}\n')

        self.column1.refresh()

    def add_text_to_column2(self, text, count=True):
        if count:
            self.column2.addstr(f'{self.col2_msgs}> {text}\n')
            self.col2_msgs += 1
        else:
            self.column2.addstr(f' > {text}\n')
        self.column2.refresh()

    def run(self):
        while True:
            self.cmd_input.addstr(0, 0, "Command: ")
            self.cmd_input.refresh()
            cmd = self.cmd_input.getstr().decode('utf-8')
            if cmd != '':
                res = self.ch.handle(cmd)
                self.add_text_to_column1(res)

            self.cmd_input.clear()
            self.cmd_input.refresh()
