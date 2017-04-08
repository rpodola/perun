"""This module implement the heap map visualization of the profile"""
import curses
import curses.textpad
import json
import sys
from random import randint

# debug in console
import heap_representation as heap_representation


class HeapMapCursesColors(object):
    """ Class providing operations with curses colors used in the heap map.

    Attributes:
        COLOR_BORDER        Color representing border.
        COLOR_FREE_FIELD    Color representing free field.
        COLOR_INFO_TEXT     Color representing informative text.
    """
    def __init__(self):
        """ Initialize colors.

            Initialize the curses color module
            and the colors for later use in the heap map.

            16 == black
            -1 == implicit color
        """
        # initializing the curses color module
        curses.start_color()
        curses.use_default_colors()

        # good visible colors
        self.__good_colors = (
            1, 2, 3, 4, 5, 6, 7, 11, 14, 17, 21, 19,
            22, 23, 27, 33, 30, 34, 45, 41, 46, 49,
            51, 52, 54, 56, 58, 59, 62, 65, 71, 76,
            89, 91, 94, 95, 124, 125, 126, 127, 129,
            130, 131, 154, 156, 159, 161, 166, 167,
            178, 195, 197, 199, 203, 208, 210, 211,
            214, 220, 226, 229, 255)
        # structure for saving corresponding allocation
        # with their specific color representation
        self.__color_records = []

        start_pair_number = 1
        for i in self.__good_colors:
            curses.init_pair(start_pair_number, 16, i)
            start_pair_number += 1

        # border color
        curses.init_pair(start_pair_number, 16, 16)
        self.COLOR_BORDER = start_pair_number
        start_pair_number += 1
        # free field color
        curses.init_pair(start_pair_number, -1, 8)
        # for better grey scale printing
        curses.init_pair(start_pair_number, 16, 7)
        self.COLOR_FREE_FIELD = start_pair_number
        start_pair_number += 1
        # info text color
        curses.init_pair(start_pair_number, -1, 16)
        self.COLOR_INFO_TEXT = start_pair_number

    def get_field_color(self, field):
        """ Pick a right color for the given field.

        Arguments:
            field(dict): allocation's information

        Returns:
            int: number of the picked curses color.pair()
        """
        if field['uid'] is None:
            return self.COLOR_FREE_FIELD

        uid = field['uid']
        for item in self.__color_records:
            if (uid['function'] == item['uid']['function'] and
                    uid['source'] == item['uid']['source']):
                return item['color']

        color = randint(1, len(self.__good_colors))
        self.__color_records.append({'uid': uid, 'color': color})

        return color


class HeapMapVisualization(object):
    """ Class providing visualization of the heap map.

        Visualization is implemented over curses module.

    Attributes:
        NEXT_SNAPSHOT       Constant representing move's direction
                            to the next snapshot.
        PREV_SNAPSHOT       Constant representing move's direction
                            to the previous snapshot.
        CURRENT_SNAPSHOT    Constant representing move's direction
                            to the current snapshot.
    """
    NEXT_SNAPSHOT = 1
    PREV_SNAPSHOT = -1
    CURRENT_SNAPSHOT = 0

    # minimal size of the heap map window
    __MIN_ROWS = 30
    __MIN_COLS = 70

    # delay after INTRO text [ms]
    __INTRO_DELAY = 700
    # delay between frames in ANIMATION mode [ms]
    __ANIMATION_DELAY = 1000

    __MENU_TEXT = '[Q] QUIT  [<] PREVIOUS  [>] NEXT  [A] ANIMATE  ' \
                  '[4|8|6|5] CURSOR L|U|R|D'
    __ANIME_MENU_TEXT = '[S] STOP  [P] PAUSE  [R] RESTART'
    __ANIME_CONTINUE_TEXT = '[C] CONTINUE'
    __RESIZE_REQ_TEXT = "Increase the size of your screen, please"
    __INTRO_TEXT = "HEAP MAP!"

    def show_intro(self):
        """ Print INTRO screen about HEAP MAP visualization """
        text = self.__INTRO_TEXT
        row_pos = curses.LINES // 2
        col_pos = (curses.COLS - len(text)) // 2

        self.__window.addstr(row_pos, col_pos, text, curses.A_BOLD)
        self.__window.refresh()
        # just for effect :)
        curses.napms(self.__INTRO_DELAY)

    def resize_req_print(self):
        """ Print resize request to the window """
        text = self.__RESIZE_REQ_TEXT
        row_pos = curses.LINES // 2
        col_pos = (curses.COLS - len(text)) // 2

        self.__window.clear()
        self.__window.addstr(row_pos, col_pos, text, curses.A_BOLD)

    def menu_print(self, text):
        """ Print text as menu information to the window
        Arguments:
            text(string): string to print as a MENU text
        """
        row_pos = curses.LINES - 1
        col_pos = (curses.COLS - len(text)) // 2

        # clearing line
        self.__window.hline(curses.LINES - 1, 0, ' ', curses.COLS - 1)
        self.__window.addstr(row_pos, col_pos, text, curses.A_BOLD)

    def info_print(self, margin):
        """ Print the snapshot information to the window
        Arguments:
            margin(int): left margin
        """
        text = 'SNAPSHOT: ' + str(self.__current_snap)
        text += '/' + str(self.__heap['max']) + '  ('
        text += str(self.__heap['snapshots'][self.__current_snap - 1]['time'])
        text += 's)'
        row_pos = 0
        col_pos = (curses.COLS - len(text) - margin) // 2 + margin

        self.__window.addstr(row_pos, col_pos, text,
                             curses.color_pair(self.__colors.COLOR_INFO_TEXT))

    def animation_prompt(self):
        """ Animation feature of the HEAP MAP visualization """
        # TODO instead of non-blocing use timeout
        # set non_blocking window.getch()
        self.__window.nodelay(1)

        while True:
            # print ANIMATION MENU text
            self.menu_print(self.__ANIME_MENU_TEXT)

            # delay between individually heap map screens
            curses.napms(self.__ANIMATION_DELAY)

            key = self.__window.getch()

            self.following_snapshot(HeapMapVisualization.NEXT_SNAPSHOT)

            if key in (ord('s'), ord('S')):
                # stop ANIMATION
                self.following_snapshot(HeapMapVisualization.CURRENT_SNAPSHOT)
                break
            # restart animation from the 1st snapshot
            elif key in (ord('r'), ord('R')):
                self.__set_current_snap(1)
                self.following_snapshot(HeapMapVisualization.CURRENT_SNAPSHOT)
            # stop animation until 'C' key is pressed
            elif key in (ord('p'), ord('P')):
                while self.__window.getch() not in (ord('c'), ord('C')):
                    self.menu_print(self.__ANIME_CONTINUE_TEXT)
            # change of the screen size occurred
            elif key == curses.KEY_RESIZE:
                self.following_snapshot(HeapMapVisualization.CURRENT_SNAPSHOT)

        # empty buffer window.getch()
        while self.__window.getch() != -1:
            pass
        # set blocking window.getch()
        self.__window.nodelay(0)

    def create_screen_decomposition(self, rows, cols):
        """ Create a matrix with corresponding representation of the snapshot
        Arguments:
            rows(int): total number of the screen's rows
            cols(int): total number of the screen's columns

        Returns:
            dict: matrix representing map's snapshot decomposition
                  and size of the field
        """
        snap = self.__heap['snapshots'][self.__current_snap - 1]
        stats = self.__heap['stats']

        # calculating approximated field size
        line_address_range = stats['max_address'] - stats['min_address']
        field_size = line_address_range / (rows * cols)

        # creating empty matrix
        matrix = [[None for _ in range(cols)] for _ in range(rows)]

        allocations = snap['map']
        # sorting allocations records by frequency of allocations
        allocations.sort(key=lambda x: x['address'])
        iterator = iter(allocations)

        record = next(iterator, None)
        # set starting address to first approx field
        last_field = stats['min_address']
        remain_amount = 0 if record is None else record['amount']
        for row in range(rows):
            for col in range(cols):

                if record is not None:
                    # if is record address not in the next field,
                    # let's put there empty field
                    if record['address'] > last_field + field_size:
                        matrix[row][col] = {"uid": None,
                                            "address": last_field,
                                            "amount": 0}
                        last_field += field_size
                        continue

                    matrix[row][col] = {"uid": record['uid'],
                                        "address": record['address'],
                                        "amount": record['amount']}

                    if remain_amount <= field_size:
                        record = next(iterator, None)
                        if record is None:
                            remain_amount = 0
                        else:
                            remain_amount = record['amount']

                    else:
                        remain_amount -= field_size

                    last_field += field_size
                else:
                    matrix[row][col] = {"uid": None,
                                        "address": last_field,
                                        "amount": 0}
                    last_field += field_size

        return {"data": matrix, "field_size": field_size,
                "rows": rows, "cols": cols}

    def matrix_print(self, map_data, rows, cols, add_length):
        """ Prints the screen representation matrix to the window
        Arguments:
            map_data(dict): representing information about map's snapshot
            rows(int): total number of the screen's rows
            cols(int): total number of the screen's columns
            add_length(int): length of the maximal address
        """
        # border_sym = u"\u2588"
        border_sym = ' '
        field_sym = '_'
        tik_delimiter = '|'
        tik_freq = 10
        tik_amount = int(map_data['field_size'] * tik_freq)

        # calculating address range on one line
        address = map_data['data'][0][0]['address']
        line_address_size = int(map_data['cols'] * map_data['field_size'])

        for row in range(rows):
            # address info printing calculated from 1st and field size (approx)
            if row not in (0, rows-1):
                address_string = str(address)
                if len(address_string) < add_length:
                    address_string += border_sym*(add_length - len(address_string))
                address += line_address_size
            elif row == 0:
                address_string = "ADDRESS:"
                if len(address_string) < add_length:
                    address_string += border_sym * \
                                      (add_length - len(address_string))
            else:
                address_string = border_sym*(add_length)

            self.__window.addnstr(row, 0, address_string, len(address_string),
                                  curses.color_pair(self.__colors.COLOR_INFO_TEXT))

            tik_counter = 0
            for col in range(add_length, cols):
                # border printing
                if col in (add_length, cols-1) or row in (0, rows-1):
                    self.__window.addch(row, col, border_sym,
                                        curses.color_pair(self.__colors.COLOR_BORDER))

                # field printing
                else:
                    field = map_data['data'][row - 1][col - add_length - 1]
                    if tik_counter % tik_freq == 0:
                        symbol = tik_delimiter
                    elif row == rows-2:
                        symbol = border_sym
                    else:
                        symbol = field_sym

                    color = self.__colors.get_field_color(field)
                    self.__window.addstr(row, col, symbol,
                                         curses.color_pair(color))

                tik_counter += 1

        # adding tik amount info
        tik_amount_str = ''
        for i, col in enumerate(range(add_length, cols, tik_freq)):
            if tik_freq >= cols - col:
                break
            tik_string = str(tik_amount * i) + self.__memory_unit
            tik_amount_str += tik_string
            tik_amount_str += border_sym*(tik_freq - len(tik_string))

        self.__window.addstr(rows - 1, add_length + 1, tik_amount_str,
                             curses.color_pair(self.__colors.COLOR_INFO_TEXT))

    def __redraw_heap_map(self):
        """ Redraw the heap map screen to represent the specified snapshot
        Returns:
            bool: success of the operation
        """
        curses.update_lines_cols()
        self.__window.clear()

        # calculate space for the addresses information
        max_add_len = len(str(self.__heap['stats']['max_address']))
        if max_add_len < len('ADDRESS:'):
            max_add_len = len('ADDRESS:')

        # check for the minimal screen size
        if curses.LINES < self.__MIN_ROWS or \
                        (curses.COLS - max_add_len) < self.__MIN_COLS:
            return False

        # number of the screen's rows == (minimum of rows) - (2*border field)
        map_rows = self.__MIN_ROWS - 2
        # number of the screen's columns == (terminal's current number of
        # the columns) - (size of address info - 2*border field)
        map_cols = curses.COLS - max_add_len - 2

        # creating the heap map screen decomposition
        decomposition = self.create_screen_decomposition(map_rows, map_cols)
        assert decomposition

        # printing heap map decomposition to the console window
        self.matrix_print(decomposition, self.__MIN_ROWS, curses.COLS,
                          max_add_len)
        # printing heap info to the console window
        self.info_print(max_add_len)
        # update map information and coordinates
        self.__map_cords.update({'row': 1, 'col': max_add_len + 1,
                                 'map': decomposition})
        return True

    def __set_current_snap(self, following_snap):
        """ Sets current snapshot
        Arguments:
            following_snap(int): number of the snapshot to set
        """
        if following_snap in range(1, self.__heap['max'] + 1):
            self.__current_snap = following_snap
            return True
        else:
            return False

    def following_snapshot(self, direction):
        """ Set following snapshot to print
        Arguments:
            direction(int): direction of the following snapshot (PREVIOUS/NEXT)

        Returns:
            bool: success of the operation
        """
        if not self.__set_current_snap(self.__current_snap + direction):
            return

        if self.__redraw_heap_map():
            # printing menu to the console window
            self.menu_print(self.__MENU_TEXT)
            # set cursor's position to the upper left corner of the heap map
            self.cursor_reset()
            self.print_field_info()
        else:
            self.resize_req_print()

    def cursor_reset(self):
        """ Sets the cursor to the upper left corner of the heap map """
        self.__window.move(self.__map_cords['row'], self.__map_cords['col'])

    def cursor_move(self, direction):
        """ Move the cursor to the new position defined by direction
        Arguments:
            direction(any): character returned by curses.getch()
        """
        # save current cursor's position
        row_col = self.__window.getyx()

        map_rows = self.__map_cords['map']['rows']
        map_cols = self.__map_cords['map']['cols']

        if direction == ord('4'):
            if row_col[1] - self.__map_cords['col'] > 0:
                self.__window.move(row_col[0], row_col[1] - 1)
            else:
                self.__window.move(row_col[0],
                                   self.__map_cords['col'] + map_cols - 1)

        elif direction == ord('6'):
            if row_col[1] - self.__map_cords['col'] < map_cols - 1:
                self.__window.move(row_col[0], row_col[1] + 1)
            else:
                self.__window.move(row_col[0],
                                   self.__map_cords['col'])

        elif direction == ord('8'):
            if row_col[0] - self.__map_cords['row'] > 0:
                self.__window.move(row_col[0] - 1, row_col[1])
            else:
                self.__window.move(self.__map_cords['row'] + map_rows - 1,
                                   row_col[1])

        elif direction == ord('5'):
            if row_col[0] - self.__map_cords['row'] < map_rows - 1:
                self.__window.move(row_col[0] + 1, row_col[1])
            else:
                self.__window.move(self.__map_cords['row'], row_col[1])

    def print_field_info(self):
    # TODO
        if self.__map_cords['map'] is None:
            return

        # save current cursor's position
        row_col = self.__window.getyx()
        # calculate map field from cursor's position
        matrix_row = row_col[0] - self.__map_cords['row']
        matrix_col = row_col[1] - self.__map_cords['col']

        try:
            data = self.__map_cords['map']['data'][matrix_row][matrix_col]
            if data['uid'] is None:
                info = "TODO global"
            else:
                info = "Starting address: " + str(data['address']) + '\n'
                info += "Allocated space: " + str(data['amount']) + ' ' \
                        + self.__memory_unit + '\n'
                info += "Allocation: " + str(data['uid'])
        except KeyError:
            info = ''

        self.__window.addstr(self.__map_cords['map']['rows'] + 5, 0, info)
        self.__window.move(*row_col)

    def __init__(self, window, heap):
        # memory space unit
        self.__memory_unit = heap['unit']
        # initialized curses window
        self.__window = window
        # heap representation
        self.__heap = heap
        # currently printed map's snapshot
        self.__current_snap = 0
        # map coordinates and metadata
        self.__map_cords = {'row': 0, 'col': 0, 'map': {}}

        # initialize curses colors
        self.__colors = HeapMapCursesColors()
        # set cursor visible
        curses.curs_set(2)


def heap_map_prompt(window, heap):
    """ Visualization prompt

        Heap map's screen is represented by dictionary as follow:
        {'col': X coordinate of upper left corner of the map (int),
         'row': Y coordinate of upper left corner of the map (int),
         'map':{
            'rows': number of map's rows (int),
            'cols': number of map's columns (int),
            'data': matrix with map's data
          }
         }

        Coordinate space is 0---->X
                            |
                            |
                            |
                            Y
    """
    heap_map = HeapMapVisualization(window, heap)

    heap_map.show_intro()
    # print 1st snapshot's heap map
    heap_map.following_snapshot(HeapMapVisualization.NEXT_SNAPSHOT)

    while True:
        # catching key value
        key = window.getch()

        # quit of the visualization
        if key in (ord('q'), ord('Q')):
            break
        # previous snapshot
        elif key == curses.KEY_LEFT:
            heap_map.following_snapshot(HeapMapVisualization.PREV_SNAPSHOT)
        # next snapshot
        elif key == curses.KEY_RIGHT:
            heap_map.following_snapshot(HeapMapVisualization.NEXT_SNAPSHOT)
        # start of the animation
        elif key in (ord('a'), key == ord('A')):
            heap_map.animation_prompt()
        # cursor moved
        elif key in (ord('4'), ord('6'), ord('8'), ord('5')):
            heap_map.cursor_move(key)
            heap_map.print_field_info()
        # change of the screen size occurred
        elif key == curses.KEY_RESIZE:
            heap_map.following_snapshot(HeapMapVisualization.CURRENT_SNAPSHOT)

def heap_map(heap_map):
    """ Initialize heap map and call curses wrapper and start visualization

        Wrapper initialize terminal,
        turn off automatic echoing of keys to the screen,
        turn reacting to keys instantly
        (without requiring the Enter key to be pressed) on,
        enable keypad mode for special keys s.a. HOME.

    Arguments:
        heap_map(dict): the heap representation

    Returns:
        string: message informing about operation success
    """
    # after integration remove try block
    try:
        # call __heap map visualization prompt in curses wrapper
        curses.wrapper(heap_map_prompt, heap_map)
    except curses.error as error:
        print('Screen too small!', file=sys.stderr)
        print(str(error), file=sys.stderr)


if __name__ == "__main__":
    with open("memory.perf") as prof_json:
        prof = heap_representation.create(json.load(prof_json))
        heap_map(prof)
