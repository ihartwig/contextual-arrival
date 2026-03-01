import json
import time

from collections import namedtuple


StopArrivalInfo = namedtuple('StopArrivalInfo', ['arrival_time', 'update_time', 'live'])


class StopDisplayCurses:
    def __init__(self, stop_ids):
        self.stop_info = {}  # type: List[StopArrivalInfo]
        for stop_id in stop_ids:
            self.stop_info[stop_id] = []

    def update_display(self):
        now_ms = int(time.time_ns() / 1000000)
        for stop_id, stop_info in self.stop_info.items():
            arrival_times_str = ""
            for next_arrival in stop_info:
                arrival_diff_ms = next_arrival.arrival_time - now_ms
                arrival_diff_min = round(arrival_diff_ms / (1000 * 60))
                arrival_times_str = f"{arrival_times_str} {arrival_diff_min}"
            arrival_times_str = f"{arrival_times_str} min"
            print(f"{stop_id}: {arrival_times_str}")
        # print(self.stop_info)

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
            print("Response did not contain stop info: {new_stop_info}")
        # sort by arrival time since we aren't sure if the arrivals are sorted 
        sorted_arrivals = [v for k, v in sorted(temp_arrivals.items())]
        self.stop_info[stop_id] = sorted_arrivals
        print(f"{new_stop_info['currentTime']}: {sorted_arrivals}")
        self.update_display()
