import geopandas as gpd
import numpy as np
import folium
from esda.moran import Moran_Local
from libpysal.weights import Queen
from branca.colormap import linear

gdf = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["count_LEISURE"]).copy()

w = Queen.from_dataframe(gdf)
w.transform = "r"

moran = Moran_Local(gdf["count_LEISURE"], w)

gdf["Is"] = moran.Is
gdf["p_sim"] = moran.p_sim
gdf["cluster"] = moran.q

def label_leisure(row):
    if row["p_sim"] > 0.05:
        return "Not Significant"
    return {
        1: "접근성 취약지역 (Hotspot)",
        2: "좋은데 주변은 나쁨 (Low-High)",
        3: "접근성 우수지역 (Coldspot)",
        4: "나쁨인데 주변은 좋음 (High-Low)"
    }.get(row["cluster"], "Not Significant")

gdf["label"] = gdf.apply(label_leisure, axis=1)

color_map = {
    "접근성 취약지역 (Hotspot)": "#7f0000",
    "접근성 우수지역 (Coldspot)": "#00441b",
    "좋은데 주변은 나쁨 (Low-High)": "#d9f0a3",
    "나쁨인데 주변은 좋음 (High-Low)": "#f7fcb9",
    "Not Significant": "#cccccc"
}

m = folium.Map(location=[37.56, 126.97], zoom_start=11)
folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": color_map.get(feature["properties"]["label"], "#cccccc"),
        "color": "black", "weight": 0.3, "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(fields=["label", "count_LEISURE"], aliases=["클러스터", "여가시설 거리"])
).add_to(m)
m.save("C:/Users/sec/Desktop/공모전 리얼/lisa_leisure_access.html")
