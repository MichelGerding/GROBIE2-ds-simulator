import curses


class TerminalUI:
    """ TerminalUI class"""
    col1_msgs = 1
    col2_msgs = 1

    previous_commands = []
    commands_index = 0

    def __init__(self, message1, message2, command_handler):
        self.ch = command_handler

        self.stdscr = curses.initscr()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.refresh()

        if curses.COLS < 103:
            raise Exception("window to small (minimum 103 columns)")

        top_msg1_lines = 7  # TODO:: make line height dynamic

        self.top_message1 = curses.newwin(top_msg1_lines, curses.COLS // 2, 0, 0)
        self.top_message1.addstr(message1)
        self.top_message1.refresh()

        self.top_message2 = curses.newwin(1, (curses.COLS // 2) - 1, 0, (curses.COLS // 2) + 1)
        self.top_message2.addstr(message2)
        self.top_message2.refresh()

        self.column1 = curses.newwin(curses.LINES - (top_msg1_lines + 1), curses.COLS // 2, (top_msg1_lines + 1), 0)
        self.column1.scrollok(True)
        self.column1.refresh()

        self.column2 = curses.newwin(curses.LINES - 2, (curses.COLS // 2) - 1, 1, (curses.COLS // 2) + 1)
        self.column2.scrollok(True)
        self.column2.refresh()

        self.cmd_input = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

    def draw(self):
        """ Draw the updated screen """
        for i in range(curses.LINES - 1):
            self.stdscr.addch(i, curses.COLS // 2, '|')
        self.stdscr.refresh()

    def add_text_to_column1(self, text, count=True):
        """ add text to the first/left column of the screen. this does not include the help text """
        if count:
            self.column1.addstr(f'{self.col1_msgs}> {text}\n')
            self.col1_msgs += 1
        else:
            self.column1.addstr(f' > {text}\n')

        self.column1.refresh()

    def add_text_to_column2(self, text, count=True):
        """ add text to the second/right column of the screen. this does not include the column label """
        if count:
            self.column2.addstr(f'{self.col2_msgs}> {text}\n')
            self.col2_msgs += 1
        else:
            self.column2.addstr(f' > {text}\n')
        self.column2.refresh()

    def run(self):
        """ Run the terminal UI """
        while True:
            self.cmd_input.addstr(0, 0, "Command: ")
            self.cmd_input.refresh()
            cmd_win = curses.newwin(1, curses.COLS - 9, curses.LINES - 1, 9)
            cmd_win.keypad(True)
            cmd = ''
            while True:
                c = cmd_win.getch()
                if c == curses.KEY_UP:
                    if self.previous_commands:  # Check if previous_commands is not empty
                        self.commands_index = min(self.commands_index + 1, len(self.previous_commands) - 1)
                        cmd = self.previous_commands[self.commands_index]
                elif c == curses.KEY_DOWN:
                    if self.previous_commands:  # Check if previous_commands is not empty
                        self.commands_index = max(self.commands_index - 1, -1)
                        cmd = self.previous_commands[self.commands_index] if self.commands_index != -1 else ''
                elif c == curses.KEY_ENTER or c == 10 or c == 13:
                    break
                elif c == curses.KEY_BACKSPACE or c == 127 or c == 0x08:  # Check if the key pressed is the backspace key
                    cmd = cmd[:-1]
                else:
                    cmd += chr(c)
                cmd_win.clear()
                cmd_win.addstr(0, 0, cmd)
                cmd_win.refresh()

            if cmd != '':
                self.previous_commands.insert(0, cmd)
                self.commands_index = -1
                res = self.ch.handle(cmd)
                self.add_text_to_column1(res)

            self.cmd_input.clear()
            self.cmd_input.refresh()

