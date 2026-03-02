import argparse
import importlib.util
import json
import logging
import requests
import sys
import threading
import time
from datetime import datetime, date
from pathlib import Path
from stop_display_curses import StopDisplayCurses


LOG = logging.getLogger()


# can be overriden with a config.py
OBA_API_KEY = "TEST"
OBA_API_WAIT_SEC = 15
OBA_API_ARR_DEPT_FOR_STOP_BASE = "https://api.pugetsound.onebusaway.org/api/where/arrivals-and-departures-for-stop/"
STOP_IDS = [
    "40_1108",  # 1 Line Westlake SB
    "40_1121",  # 1 Line Westlake NB
]
TEST_DATA_DIR = "test_data"  # relative to this file

CONFIG_NAMES = ["OBA_API_KEY", "OBA_API_WAIT_SEC", "STOP_IDS", "TEST_DATA_DIR"]


def this_file_or_cwd_path():
    this_file_path = Path.cwd()
    try:
        this_file_path = Path(__file__)
    except NameError:
        # Fallback for interactive sessions or environments without __file__
        LOG.info("Warning: __file__ not available. Using current working directory.")
    return this_file_path.parent


def check_test_data(stop_ids):
    """Returns true if there is already a json response file for each stop_id"""
    for stop_id in stop_ids:
        stop_id_path = this_file_or_cwd_path() / TEST_DATA_DIR / f"{stop_id}.json"
        if not stop_id_path.is_file():
            LOG.info(f"Couldn't find test data for stop_id '{stop_id}' at '{stop_id_path}'")
            return False
    return True


def fetch_test_data(stop_ids, repeat = False):
    """"Request current arrivals and departures info for each stop_id and save to TEST_DATA_DIR"""
    while repeat:
        for stop_id in STOP_IDS:
            url = f"{OBA_API_ARR_DEPT_FOR_STOP_BASE}/{stop_id}.json?key={OBA_API_KEY}"
            test_filename = f"{TEST_DATA_DIR}/{stop_id}.json"
            # LOG.info(f"Requesting '{url}'...")
            r = requests.get(url)
            with open(test_filename, 'wb') as f:
                f.write(r.content)
            r_text = r.content.decode("utf-8")
            r_text = r_text[0:80] + "..." if len(r_text) > 80 else ""
            # LOG.info(f"{r_text}")
            time.sleep(OBA_API_WAIT_SEC)


def fetch_stop_times(stop_id, test_data = False):
    data = {}
    if test_data:
        test_filename = f"{TEST_DATA_DIR}/{stop_id}.json"
        with open(test_filename, 'rb') as f:
            r = f.read()
            r_text = r.decode("utf-8")
            return json.loads(r_text)
    else:
        url = f"{OBA_API_ARR_DEPT_FOR_STOP_BASE}/{stop_id}.json?key={OBA_API_KEY}"
        # LOG.info(f"Requesting '{url}'...")
        r = requests.get(url)
        r_text = r.content.decode("utf-8")
    data = json.loads(r_text)
    if data is None or "code" not in data.keys() or data["code"] != 200:
        p_text = r_text[0:80] + "..." if len(r_text) > 80 else ""
        LOG.info(f"Response invalid: {p_text}")
        return {}
    return data


def fetch_stop_times_and_update(update_fn, use_test_data):
    while True:
        for stop_id in STOP_IDS:
            try:
                update_fn(
                    stop_id,
                    fetch_stop_times(stop_id, test_data=use_test_data)
                )
                time.sleep(OBA_API_WAIT_SEC)
            except Exception as e:
                LOG.error(e)


def main():
    parser = argparse.ArgumentParser(description='Render OneBusAway data')
    parser.add_argument('--config-path', '-c', default="config.py")
    parser.add_argument('--test-data', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    # load a selection of defined values from a config py file
    config_module = None
    try:
        config_path = this_file_or_cwd_path() / args.config_path
        config_spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(config_module)
    except Exception as e:
        print(f"exception loading config: {e}")
    for config_name in CONFIG_NAMES:
        if config_module and config_name in dir(config_module):
            config_value = getattr(config_module, config_name)
            globals()[config_name] = config_value
            print(f"loaded {config_name} from '{args.config_path}'")
        print(f"configured {config_name} = '{globals()[config_name]}'")

    # sort out if we already have the test data or need to collect it
    if args.fetch:
        fetch_test_data(STOP_IDS, repeat=True)
    if args.test_data and not check_test_data(STOP_IDS):
        fetch_test_data(STOP_IDS)

    # start screens
    sdc = StopDisplayCurses(STOP_IDS)
    sdc_fetcher = threading.Thread(
        target=fetch_stop_times_and_update,
        args=(sdc.update_stop_info, args.test_data),
        daemon=True
    )
    sdc_fetcher.start()
    sdc.curses_start()


if __name__ == "__main__":
    main()
