import geopandas as gpd
import numpy as np
import folium
from esda.moran import Moran_Local
from libpysal.weights import Queen
from branca.colormap import linear

# ───────────────────────────────────────────────────────────
# 1. 데이터 불러오기
gdf = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["count_WELFARE"]).copy()

# ───────────────────────────────────────────────────────────
# 2. 공간 가중치 행렬
w = Queen.from_dataframe(gdf)
w.transform = "r"

# ───────────────────────────────────────────────────────────
# 3. Local Moran's I 분석
moran = Moran_Local(gdf["count_WELFARE"], w)

# ───────────────────────────────────────────────────────────
# 4. 결과 정리
gdf["Is"] = moran.Is
gdf["p_sim"] = moran.p_sim
gdf["cluster"] = moran.q

# 5. 클러스터 라벨링 (접근성 해석 기준!)
def get_label(row):
    if row["p_sim"] > 0.05:
        return "Not Significant"
    return {
        1: "접근성 취약지역 (Hotspot)",      # 거리 높고 주변도 멀다
        2: "좋은데 주변은 나쁨 (Low-High)",  # 나만 접근성 좋음
        3: "접근성 우수지역 (Coldspot)",      # 거리 낮고 주변도 가까움
        4: "나쁨인데 주변은 좋음 (High-Low)"  # 나만 나쁨
    }.get(row["cluster"], "Not Significant")

gdf["label"] = gdf.apply(get_label, axis=1)

# ───────────────────────────────────────────────────────────
# 6. 시각화 색상
color_map = {
    "접근성 취약지역 (Hotspot)": "#bd0026",
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
    tooltip=folium.GeoJsonTooltip(fields=["label", "count_WELFARE"], aliases=["클러스터", "복지관 거리"])
).add_to(m)

m.save("C:/Users/sec/Desktop/공모전 리얼/lisa_welfare_access.html")
print("✔ 복지관 접근성 거리 기준 LISA 분석 완료 → 'lisa_welfare_access.html'")
