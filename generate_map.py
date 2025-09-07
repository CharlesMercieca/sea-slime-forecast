import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.lines import Line2D
import matplotlib.ticker as mtick

import json

from datetime import datetime, timedelta

now = datetime.now()
later = now + timedelta(hours=12)

df = pd.read_csv("data/results.csv")
if len(df) == 0:
	df = None
else:
	df

MALTA_GEOJSON = "data/malta_01m.geojson"

subtitle = f"Last Run: {now.strftime('%d %b %Y %H:%M')} Next Scheduled Run: {later.strftime('%d %b %Y %H:%M')}"

#Palette
PAPER  = "#F1E9D2"   # land
SEA    = "#A6C2D2"   # water
INK    = "#2F2A26"   # outlines/text
ACCENT = "#F45B69"   # points

#Load Malta
with open(MALTA_GEOJSON, "r", encoding="utf-8") as f:
    mt = json.load(f)

def add_geojson_polys(ax, feature, face=PAPER, edge=INK, lw=1.2, hatch="///", alpha=0.96, z=2):
    geom = feature["geometry"]
    coords = geom["coordinates"]

    def add_poly(rings):
        ext = rings[0]
        ax.add_patch(Polygon(ext, closed=True, facecolor=face,
                             edgecolor=edge, linewidth=lw, hatch=hatch, alpha=alpha, zorder=z))

    if geom["type"] == "Polygon":
        add_poly(coords)
    elif geom["type"] == "MultiPolygon":
        for rings in coords:
            add_poly(rings)

# --- Compute bbox ---
xs, ys = [], []
for feat in mt["features"]:
    geom = feat["geometry"]
    if geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            for x,y in ring:
                xs.append(x); ys.append(y)
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            for ring in poly:
                for x,y in ring:
                    xs.append(x); ys.append(y)

pad_x, pad_y = 0.04, 0.04
x_min, x_max = min(xs)-pad_x, max(xs)+pad_x
y_min, y_max = min(ys)-pad_y, max(ys)+pad_y

#Plot map
fig, ax = plt.subplots(figsize=(7, 9), dpi=150)
ax.set_facecolor(SEA)
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

for feat in mt["features"]:
    add_geojson_polys(ax, feat)

#Load & plot points
if df is not None:
    df = df[df["lon"].between(x_min, x_max) & df["lat"].between(y_min, y_max)]
    if len(df):
        ax.scatter(df["lon"], df["lat"], s=14, facecolor=ACCENT,
                    edgecolor=INK, linewidth=0.6, zorder=3)
else:
    ax.set_title("All Clear!! 🏊🐳🏄", fontname="Segoe UI Emoji")

#Generate bar chart
if df is not None and "nearest_beach" in df.columns:
    counts = df.groupby("nearest_beach").size().sort_values(ascending=False)/1000

    inset_ax = fig.add_axes([0.5, 0.7, 0.479, 0.27], facecolor=PAPER)

    counts.plot(kind="barh", ax=inset_ax, color=ACCENT, edgecolor=INK)

    inset_ax.invert_yaxis()
    inset_ax.tick_params(axis="x", colors=INK, labelsize=7)
    inset_ax.tick_params(axis="y", colors=INK, labelsize=7)
    inset_ax.set_ylabel("")
    inset_ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    for spine in inset_ax.spines.values():
        spine.set_color(INK)

    inset_ax.set_title("% of beached particles", fontsize=8, color=INK, pad=4)

ax.tick_params(colors=INK, labelsize=8)
for s in ax.spines.values():
    s.set_color(INK); s.set_linewidth(1)

plt.tight_layout()
fig.text(0.5, 0.2, subtitle, 
         ha="center", va="top", fontsize=8, color=INK)

plt.savefig("forecast_map.png", dpi=250,
            facecolor="white",
            bbox_inches="tight")