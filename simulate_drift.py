import opendrift
from opendrift.readers import reader_netCDF_CF_generic, reader_global_landmask, reader_grib2
from opendrift.models.oceandrift import OceanDrift
from datetime import datetime, timezone

import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Transformer, CRS

import os

start_time = datetime.now()

#initial setup
reader_cmems=reader_netCDF_CF_generic.Reader('data/currents_malta.nc')
reader_landmask = reader_global_landmask.Reader()

#beaches
beaches = pd.read_csv("data//malta_beach_locations.csv")
beaches[['lat', 'lon']] = beaches['beach_latlon'].str.split(',',expand=True)

#look up tree setup
crs_geo = CRS.from_epsg(4326)
crs_m   = CRS.from_epsg(3035)

t = Transformer.from_crs(crs_geo, crs_m, always_xy=True)

bx, by = t.transform(beaches["lon"].to_numpy(), beaches["lat"].to_numpy())

#location setup
lat, lon = 36.0075, 14.4305

o = OceanDrift(loglevel=20)
o.add_reader([reader_cmems, reader_landmask])

o.seed_elements(lon, lat, radius=350, number=1000, time=start_time)
ds=o.run(steps=288, time_step=300, time_step_output=900) # 86400 // 300   # = 288

#save beachings
df=ds[['lon', 'lat', 'status']].to_dataframe().reset_index().query('status==1')
df['start'] = start_time

#calculate nearest beachings
px, py = t.transform(df["lon"].to_numpy(), df["lat"].to_numpy())
tree = cKDTree(np.column_stack([bx, by]))
dist_m, idx = tree.query(np.column_stack([px, py]), k=1)

df["nearest_beach"] = beaches.loc[idx, "location_name"].values
df["distance_m"] = dist_m

df.to_csv('data/results.csv', index=False)
