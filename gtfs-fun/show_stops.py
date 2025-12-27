import requests
import partridge as ptg
from datetime import datetime, date
from pathlib import Path


# url = "https://www.soundtransit.org/GTFS-KCM/google_transit.zip"
url = "https://www.soundtransit.org/GTFS-rail/40_gtfs.zip"
r = requests.get(url)
gtfs_zip_path = Path("temp_gtfs.zip")
if not gtfs_zip_path.exists():
    with open(inpath, 'wb') as f:
        f.write(r.content)
del r

# read in the gtfs feed as a partridge object
# today = date(2025, 12, 21)
today = date.today()
service_ids_by_date = ptg.read_service_ids_by_date(gtfs_zip_path)
sids = [service_ids for date, service_ids in service_ids_by_date.items() if date == today]
gtfs = ptg.load_feed(gtfs_zip_path, {"trips.txt": {"service_id": sids}})

print(f"Loading services for {repr(today)}...")
print(f"{dir(gtfs)}")
print(f"Found active service_id: {sids}")
print(f"Found active routes:")
print(gtfs.routes)
print(f"Found active stops:")
print(gtfs.stops)
select_route = 0
select_trip = 11
route_id = gtfs.routes["route_id"].iloc[select_route]
trip_id = gtfs.trips[gtfs.trips["route_id"] == route_id]["trip_id"].iloc[select_trip]
print(f"Selecting route '{route_id}' trip '{trip_id}' - stop times:")
print(gtfs.stop_times[gtfs.stop_times["trip_id"] == trip_id])
