import curses
import time
import logging

from collections import deque
from collections import namedtuple


LOG = logging.getLogger()


StopArrivalInfo = namedtuple('StopArrivalInfo', ['arrival_time', 'update_time', 'live'])


class CursesLogHandler(logging.Handler):
    def __init__(self, display: "StopDisplayCurses"):
        super().__init__()
        self.display = display

    def emit(self, record):
        msg = self.format(record)
        self.display.push_log(msg)


class StopDisplayCurses:
    def __init__(self, stop_ids):
        self.log_lines = deque()  # type: Deque[str]
        self.stop_info = {}       # type: Dict[str, List[StopArrivalInfo]]
        for stop_id in stop_ids:
            self.stop_info[stop_id] = []
        self.display_lines = []   # type: List[str]

    def push_log(self, log_str):
        # add lines to the log, limit 7
        self.log_lines.append(log_str)
        while(len(self.log_lines) > 7):
            self.log_lines.popleft()
        self.update_display()

    def update_display(self):
        """
        sets self.dis: List[str] to display
        """
        display_lines = []  # type: List[str]
        now_ms = int(time.time_ns() / 1000000)
        for stop_id, stop_info in self.stop_info.items():
            arrival_times_str = ""
            for next_arrival in stop_info:
                arrival_diff_ms = next_arrival.arrival_time - now_ms
                arrival_diff_min = round(arrival_diff_ms / (1000 * 60))
                arrival_times_str = f"{arrival_times_str} {arrival_diff_min}"
            arrival_times_str = f"{arrival_times_str} min"
            display_lines.append(f"{stop_id}: {arrival_times_str}")
        display_lines.append(" ")
        for log_line in self.log_lines:
            display_lines.append(f"LOG {log_line}")
        self.display_lines = display_lines

    def update_stop_info(self, stop_id, new_stop_info):
        temp_arrivals = {}  # type: Dict[int, StopArrivalInfo]
        try:
            new_stop_info_time = new_stop_info['currentTime']
            new_stop_info_arrivals = new_stop_info['data']['entry']['arrivalsAndDepartures']
            for new_stop_info_arrival in new_stop_info_arrivals:
                if 'predictedArrivalTime' not in new_stop_info_arrival or \
                    new_stop_info_arrival['predictedArrivalTime'] == 0:
                    # next arrival doesn't have real time data, use scheduled time
                    temp_arrivals[new_stop_info_time] = StopArrivalInfo(
                        new_stop_info_arrival['scheduledArrivalTime'],
                        new_stop_info_time,
                        False
                    )
                else:
                    # next arrival has real time data
                    temp_arrivals[new_stop_info_time] = StopArrivalInfo(
                        new_stop_info_arrival['predictedArrivalTime'],
                        new_stop_info_time,
                        True
                    )
        except KeyError:
            self.push_log("Response did not contain stop info: {new_stop_info}")
        # sort by arrival time since we aren't sure if the arrivals are sorted 
        sorted_arrivals = [v for k, v in sorted(temp_arrivals.items())]
        self.stop_info[stop_id] = sorted_arrivals
        self.push_log(f"{new_stop_info['currentTime']}: {sorted_arrivals}")
        self.update_display()

    def _addstr_safe(self, win, y, x, text, attr=0):
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        max_len = w - x
        if max_len <= 0:
            return
        try:
            win.addstr(y, x, text[:max_len], attr)
        except curses.error:
            pass

    def curses_start(self):
        curses.wrapper(self.curses_main)

    def curses_main(self, stdscr):
        # Colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN,    -1)   # Header
        curses.init_pair(2, curses.COLOR_GREEN,   -1)   # Live / arriving soon
        curses.init_pair(3, curses.COLOR_YELLOW,  -1)   # Scheduled / moderate wait
        curses.init_pair(4, curses.COLOR_RED,     -1)   # Late / long wait
        curses.init_pair(5, curses.COLOR_WHITE,   -1)   # Normal text
        curses.init_pair(6, curses.COLOR_BLACK,   curses.COLOR_CYAN)   # Title bar
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)   # Log text

        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(1000)  # refresh every second

        scroll_offset = 0
        log_scroll = 0

        # redirect log lines to curses display
        LOG.handlers.clear()
        LOG.addHandler(CursesLogHandler(self))
        LOG.setLevel(logging.INFO)

        # main loop
        while True:
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    break
                # todo scroll back and forth?

                stdscr.erase()
                # h, w = stdscr.getmaxyx()

                for y, display_line in enumerate(self.display_lines):
                    self._addstr_safe(stdscr, y, 0, display_line)
            except Exception as e:
                LOG.error(e)

            stdscr.refresh()
