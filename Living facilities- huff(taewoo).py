import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from branca.colormap import linear

# 1. 격자 데이터 불러오기
gdf = gpd.read_file(r"C:\Users\sec\Desktop\공모전 리얼\merged_1km_data.gpkg", layer="merged")

# 2. 전처리
gdf = gdf.dropna(subset=["elder_pop"]).copy()
gdf.replace({999: np.nan, -999: np.nan}, inplace=True)
gdf = gdf.to_crs(epsg=5179)
gdf["centroid"] = gdf.geometry.centroid
gdf["lat"] = gdf["centroid"].to_crs(epsg=4326).y
gdf["lon"] = gdf["centroid"].to_crs(epsg=4326).x
gdf = gdf.to_crs(epsg=4326).drop(columns="centroid")

# 3. Huff 모델 적용 (거리 → 매력도)
β = 2
for col in ["count_KYRD", "count_CLASS", "count_WELFARE", "count_LEISURE"]:
    gdf[f"attr_{col}"] = 1 / (gdf[col].replace(0, np.nan) ** β)

# 4. 통합 매력도 계산 및 커버리지 추정
attr_cols = ["attr_count_KYRD", "attr_count_CLASS", "attr_count_WELFARE", "attr_count_LEISURE"]
gdf["attr_WELFARE"] = gdf[attr_cols].sum(axis=1).fillna(0)
gdf["prob_WELFARE"] = gdf["attr_WELFARE"] / gdf["attr_WELFARE"].sum()
gdf["cov_WELFARE"] = gdf["prob_WELFARE"] * gdf["elder_pop"]
gdf["cov_ratio_W"] = gdf["cov_WELFARE"] / gdf["elder_pop"]
gdf.loc[gdf["elder_pop"] < 50, "cov_ratio_W"] = np.nan  # 고령자 너무 적은 격자 제외

# 5. 행정동 SHP 읽고 병합
emd = gpd.read_file(r"C:\Users\sec\Desktop\공모전 리얼\LSMD_ADM_SECT_UMD_11_202505.shp", encoding="euc-kr")
emd = emd.to_crs(gdf.crs)
gdf_points = gdf.copy()
gdf_points["geometry"] = gdf_points.geometry.centroid
gdf_joined = gpd.sjoin(gdf_points, emd[["EMD_CD", "EMD_NM", "geometry"]], how="left", predicate="within")
gdf_joined["geometry"] = gdf["geometry"]
gdf_joined = gdf_joined.set_geometry("geometry")

# 6. Top10 추출 및 저장
top10 = gdf_joined.dropna(subset=["cov_ratio_W"]).sort_values(by="cov_ratio_W").head(10)
top10_out = top10[["gid", "EMD_NM", "elder_pop", "cov_WELFARE", "cov_ratio_W", "lat", "lon"]]
top10_out.to_excel("Top10_복지커버리지_취약지역.xlsx", index=False)

# 7. 시각화
m = folium.Map(location=[top10["lat"].mean(), top10["lon"].mean()], zoom_start=11, tiles="cartodbpositron")
colormap = linear.YlGnBu_09.scale(gdf["cov_WELFARE"].quantile(0.05), gdf["cov_WELFARE"].quantile(0.95))
colormap.caption = "복지시설 커버리지"
colormap.add_to(m)

folium.GeoJson(
    gdf,
    style_function=lambda feat: {
        "fillColor": colormap(feat["properties"]["cov_WELFARE"]),
        "color": "gray",
        "weight": 0.2,
        "fillOpacity": 0.6
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["elder_pop", "cov_WELFARE", "cov_ratio_W"],
        aliases=["고령자 수", "복지 커버리지", "1인당 커버력"],
        localize=True
    )
).add_to(m)

for _, row in top10.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(
            f"<b>격자 ID:</b> {row['gid']}<br>"
            f"<b>행정동:</b> {row['EMD_NM']}<br>"
            f"<b>고령자 수:</b> {int(row['elder_pop'])}명<br>"
            f"<b>복지 커버리지:</b> {row['cov_WELFARE']:.3f}<br>"
            f"<b>1인당 커버력:</b> {row['cov_ratio_W']:.5f}",
            max_width=300
        ),
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

m.save("복지커버리지_TOP10_행정동.html")
print("✅ 복지 커버리지 분석 완료! 지도 및 Top10 저장됨.")
