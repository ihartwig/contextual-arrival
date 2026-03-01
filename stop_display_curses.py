import json

class StopDisplayCurses:
    def __init__(self, stop_ids):
        self.stop_info = {}
        for stop_id in stop_ids:
            self.stop_info[stop_id] = None

    def update_display(self):
        print(self.stop_info)

    def update_stop_info(self, new_stop_info):
        print(f"{new_stop_info['currentTime']}: {new_stop_info['data']['entry']['arrivalsAndDepartures']}")
        self.update_display()
