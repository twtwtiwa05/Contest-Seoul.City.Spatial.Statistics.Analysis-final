import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from branca.colormap import linear

# ──────────────────────────────────────────────
# 1. 격자 데이터 불러오기 + 중심점 계산
gdf = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["elder_pop"]).copy()

# 중심점 정확도 확보용 TM 좌표계로 변환
gdf = gdf.to_crs(epsg=5179)
gdf["centroid"] = gdf.geometry.centroid
gdf["lat"] = gdf["centroid"].to_crs(epsg=4326).y
gdf["lon"] = gdf["centroid"].to_crs(epsg=4326).x
gdf = gdf.to_crs(epsg=4326)
gdf = gdf.drop(columns=["centroid"])

# ──────────────────────────────────────────────
# 2. 허프모델 기반 의료 커버리지 계산
β = 2
gdf["attr_EMG"] = 1 / (gdf["score_EMG"].replace(0, np.nan) ** β)
gdf["attr_HOSP"] = 1 / (gdf["count_HOSP"].replace(0, np.nan) ** β)
gdf["attr_HEALTH"] = 1 / (gdf["count_HEALTH"].replace(0, np.nan) ** β)

gdf[["attr_EMG", "attr_HOSP", "attr_HEALTH"]] = gdf[["attr_EMG", "attr_HOSP", "attr_HEALTH"]].fillna(0)
gdf["attr_MED"] = gdf["attr_EMG"] + gdf["attr_HOSP"] + gdf["attr_HEALTH"]
gdf["prob_MED"] = gdf["attr_MED"] / gdf["attr_MED"].sum()
gdf["cov_MED"] = gdf["prob_MED"] * gdf["elder_pop"]
gdf["cov_ratio"] = gdf["cov_MED"] / gdf["elder_pop"]
gdf.loc[gdf["elder_pop"] < 50, "cov_ratio"] = np.nan  # 수요 적은 격자 제외

# ──────────────────────────────────────────────
# 3. SHP 행정동 경계 파일 불러오기 및 공간조인
emd = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\LSMD_ADM_SECT_UMD_11_202505.shp", encoding="euc-kr")
emd = emd.to_crs(gdf.crs)

gdf_points = gdf.copy()
gdf_points["geometry"] = gdf_points.geometry.centroid
gdf_joined = gpd.sjoin(gdf_points, emd[["EMD_CD", "EMD_NM", "geometry"]], how="left", predicate="within")
gdf_joined["geometry"] = gdf["geometry"]  # 원래 폴리곤 복원
gdf_joined = gdf_joined.set_geometry("geometry")

# ──────────────────────────────────────────────
# 4. 커버리지 낮은 상위 10개 지역 추출 및 엑셀 저장
top10 = gdf_joined.dropna(subset=["cov_ratio"]).sort_values(by="cov_ratio").head(10)
top10_out = top10[["gid", "EMD_NM", "elder_pop", "cov_MED", "cov_ratio", "lat", "lon"]]
top10_out.to_excel("Top10_의료커버리지_취약지역.xlsx", index=False)

# ──────────────────────────────────────────────
# 5. Folium 지도 시각화
m = folium.Map(location=[top10["lat"].mean(), top10["lon"].mean()], zoom_start=11, tiles="cartodbpositron")
colormap = linear.YlOrRd_09.scale(gdf["cov_MED"].quantile(0.05), gdf["cov_MED"].quantile(0.95))
colormap.caption = "의료시설 통합 커버리지"
colormap.add_to(m)

# 전체 격자 폴리곤 시각화
folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": colormap(feature["properties"]["cov_MED"]),
        "color": "gray",
        "weight": 0.2,
        "fillOpacity": 0.6
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["elder_pop", "cov_MED"],
        aliases=["고령자 수", "의료 커버리지"],
        localize=True
    )
).add_to(m)

# 상위 10개 마커 표시
for _, row in top10.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(
            f"<b>격자 ID:</b> {row['gid']}<br>"
            f"<b>행정동:</b> {row['EMD_NM']}<br>"
            f"<b>고령자 수:</b> {int(row['elder_pop'])}명<br>"
            f"<b>의료 커버리지:</b> {row['cov_MED']:.3f}<br>"
            f"<b>1인당 커버력:</b> {row['cov_ratio']:.5f}",
            max_width=300
        ),
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# 지도 저장
m.save("의료커버리지_TOP10_행정동.html")
print("✅ 완료: HTML 지도 + Excel 파일 저장")
