# contextual-arrival

Command line apps to render next arrival data from OneBusAway data streams of supporting transit agencies.




## Running

```
usage: app.py [-h] [--config-path CONFIG_PATH] [--test-data] [--fetch]

Render OneBusAway data

options:
  -h, --help            show this help message and exit
  --config-path, -c CONFIG_PATH
  --test-data
  --fetch
```

There is currently only 1 screen that runs automatically. More screens may be added in the future.

## Usage with venv

First time setup (from repo root):
```
python3 -m venv .venv

```

Each new shell (from repo root):
```
source .venv/bin/activate
```

`deactivate` to deactivate in shell.

## Configuration

Add a `config.py` file with known variables for configuration, for example:
```
OBA_API_KEY = "TEST"
STOP_IDS = [
    "40_1108", # 1 Line S - Westlake
    "40_1121", # 1 Line N - Westlake
    "1_700", # Buses 4th Ave & Pike St
]
```

## GTFS

There's an environment and sample script based on https://kuanbutts.com/2021/12/20/gtfs-and-rt-get-next-stop/ in the `gtfs-fun` directory, though this is not used since Sound Transit does not seem to publish a GTFS-RT feed for the light rail trains.
