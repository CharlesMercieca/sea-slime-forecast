import os
from pathlib import Path
from dotenv import load_dotenv
from copernicusmarine import subset
from datetime import datetime, timedelta, timezone

start = datetime.now(timezone.utc)
end = start + timedelta(hours=48)

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
CMEMS_USER = os.getenv("CMEMS_USER")
CMEMS_PASS = os.getenv("CMEMS_PASS")

subset(
    dataset_id="cmems_mod_med_phy-cur_anfc_4.2km_PT15M-i",
    variables=["uo", "vo"],
    minimum_longitude=13.7, maximum_longitude=15.7,
    minimum_latitude=35.5, maximum_latitude=36.5,
    minimum_depth=0, maximum_depth=1,
    start_datetime=start,
    end_datetime=end,
    username=CMEMS_USER,
    password=CMEMS_PASS,
    output_filename="data/currents_malta.nc"
)
