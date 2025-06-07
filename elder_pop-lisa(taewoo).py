import geopandas as gpd
import numpy as np
import folium
from esda.moran import Moran_Local
from libpysal.weights import Queen
from branca.colormap import linear

# ───────────────────────────────────────────────────────
# 1. 병합된 1km 격자 데이터 불러오기
gdf = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg", layer="merged")

# 결측치 제거 (혹시 모를 오류 방지)
gdf = gdf.dropna(subset=["elder_pop"]).copy()

# ───────────────────────────────────────────────────────
# 2. 공간 가중치 행렬 (인접 격자 기준)
w = Queen.from_dataframe(gdf)
w.transform = "r"  # row-standardized

# ───────────────────────────────────────────────────────
# 3. LISA (Local Moran's I) 분석
moran = Moran_Local(gdf["elder_pop"], w)

# ───────────────────────────────────────────────────────
# 4. 결과를 GeoDataFrame에 추가
gdf["Is"] = moran.Is             # Local Moran 통계량
gdf["p_sim"] = moran.p_sim       # p-value
gdf["cluster"] = moran.q         # 군집 분류 (1~4)

# ───────────────────────────────────────────────────────
# 5. 클러스터 레이블 분류
def get_label(row):
    if row["p_sim"] > 0.05:
        return "Not Significant"
    return {
        1: "High-High (Hotspot)",
        2: "Low-High",
        3: "Low-Low (Coldspot)",
        4: "High-Low"
    }.get(row["cluster"], "Not Significant")

gdf["label"] = gdf.apply(get_label, axis=1)

# ───────────────────────────────────────────────────────
# 6. 색상 매핑
color_map = {
    "High-High (Hotspot)": "#e31a1c",
    "Low-Low (Coldspot)": "#1f78b4",
    "Low-High": "#a6cee3",
    "High-Low": "#fb9a99",
    "Not Significant": "#cccccc"
}

# ───────────────────────────────────────────────────────
# 7. Folium 시각화
m = folium.Map(location=[37.56, 126.97], zoom_start=11, tiles='cartodbpositron')

folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": color_map.get(feature["properties"]["label"], "#cccccc"),
        "color": "black",
        "weight": 0.3,
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(fields=["label", "elder_pop"], aliases=["클러스터", "고령자 수"])
).add_to(m)

# 저장
m.save("C:/Users/sec/Desktop/공모전 리얼/lisa_elder_pop.html")
print("✔ 고령자 수 기준 LISA 분석 결과가 저장되었습니다 → 'lisa_elder_pop.html'")
