import geopandas as gpd
import numpy as np
import folium
from esda.moran import Moran_Local
from libpysal.weights import Queen
from branca.colormap import linear

# ───────────────────────────────────────────────────────────
# 1. 병합된 데이터 불러오기
gdf = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["count_KYRD"]).copy()

# ───────────────────────────────────────────────────────────
# 2. 공간 가중치 행렬 (Queen: 상하좌우 + 대각선 인접)
w = Queen.from_dataframe(gdf)
w.transform = "r"

# ───────────────────────────────────────────────────────────
# 3. Local Moran's I 분석 (경로당 접근성 거리 기준)
moran = Moran_Local(gdf["count_KYRD"], w)

# ───────────────────────────────────────────────────────────
# 4. 분석 결과 추가
gdf["Is"] = moran.Is
gdf["p_sim"] = moran.p_sim
gdf["cluster"] = moran.q

# ───────────────────────────────────────────────────────────
# 5. 라벨 부여 (접근성 해석 기준!)
def get_label(row):
    if row["p_sim"] > 0.03:
        return "Not Significant"
    return {
        1: "접근성 취약지역 (Hotspot)",
        2: "좋은데 주변은 나쁨 (Low-High)",
        3: "접근성 우수지역 (Coldspot)",
        4: "나쁨인데 주변은 좋음 (High-Low)"
    }.get(row["cluster"], "Not Significant")

gdf["label"] = gdf.apply(get_label, axis=1)

# ───────────────────────────────────────────────────────────
# 6. 색상 설정
color_map = {
    "접근성 취약지역 (Hotspot)": "#b10026",
    "접근성 우수지역 (Coldspot)": "#006837",
    "좋은데 주변은 나쁨 (Low-High)": "#c7e9c0",
    "나쁨인데 주변은 좋음 (High-Low)": "#fcbba1",
    "Not Significant": "#cccccc"
}

# ───────────────────────────────────────────────────────────
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
    tooltip=folium.GeoJsonTooltip(fields=["label", "count_KYRD"], aliases=["클러스터", "경로당 거리"])
).add_to(m)

# 저장
m.save("C:/Users/sec/Desktop/공모전 리얼/lisa_kyrd_access.html")
print("✔ 경로당 접근성 거리 기준 LISA 결과 저장 완료 → 'lisa_kyrd_access.html'")
