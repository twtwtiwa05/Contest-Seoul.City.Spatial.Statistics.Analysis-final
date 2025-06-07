import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import folium
import branca.colormap as cm
import os

# ───────────────────────────────────────────────
# 1. 격자 데이터 불러오기
gdf = gpd.read_file(r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["elder_pop"]).copy()

# ───────────────────────────────────────────────
# 2. 변수 설정 및 이상치 제거
features = ['elder_pop', 'score_EMG', 'count_CLASS', 'count_KYRD',
            'count_WELFARE', 'count_LEISURE', 'count_HOSP']
distance_cols = [col for col in features if col != 'elder_pop']

for col in distance_cols:
    gdf.loc[(gdf[col] >= 999) | (gdf[col] <= -100), col] = np.nan
gdf_clean = gdf.dropna(subset=distance_cols).copy()

# ───────────────────────────────────────────────
# 3. 정규화 + 거리 부호 반전
X = gdf_clean[features].copy()
for col in distance_cols:
    X[col] = -X[col]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ───────────────────────────────────────────────
# 4. KMeans 클러스터링
kmeans = KMeans(n_clusters=6, random_state=42, n_init='auto')
gdf_clean['cluster'] = kmeans.fit_predict(X_scaled)

# ───────────────────────────────────────────────
# 5. 읍면동 SHP 읽기 (한글 깨짐 방지)
shp_path = r"C:\Users\sec\Desktop\공모전 리얼\LSMD_ADM_SECT_UMD_11_202505.shp"
emd = gpd.read_file(shp_path, encoding='euc-kr')
emd = emd.to_crs(epsg=4326)

# ───────────────────────────────────────────────
# 6. 공간조인으로 클러스터 격자에 읍면동 이름 붙이기
gdf_with_dong = gpd.sjoin(
    gdf_clean, 
    emd[['EMD_CD', 'EMD_NM', 'geometry']], 
    how='left', 
    predicate='intersects'
)

# ───────────────────────────────────────────────
# 7. 클러스터 2, 4만 추출
target_clusters = [2, 4]
gdf_selected = gdf_with_dong[gdf_with_dong['cluster'].isin(target_clusters)].copy()

# ───────────────────────────────────────────────
# 8. 클러스터별 주요 읍면동 상위 10개 추출
cluster_dong_summary = (
    gdf_selected[['cluster', 'EMD_NM']]
    .dropna()
    .groupby('cluster')['EMD_NM']
    .value_counts()
    .groupby(level=0)
    .head(10)
    .unstack(fill_value=0)
)
print("\n✔ 클러스터 2 & 4의 주요 읍면동:")
print(cluster_dong_summary)

# ───────────────────────────────────────────────
# 9. Folium 지도 시각화 (2, 4번 클러스터만)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles='cartodbpositron')
colormap = cm.linear.Set1_09.scale(min(target_clusters), max(target_clusters))
colormap.caption = '클러스터 번호 (2, 4번만)'

for cluster_id in target_clusters:
    group = folium.FeatureGroup(name=f"Cluster {cluster_id}")
    geojson = folium.GeoJson(
        gdf_selected[gdf_selected['cluster'] == cluster_id],
        style_function=lambda feature, cluster_id=cluster_id: {
            'fillColor': colormap(cluster_id),
            'color': 'black',
            'weight': 0.3,
            'fillOpacity': 0.6,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['cluster', 'elder_pop'],
            aliases=['클러스터', '고령 인구 수'],
            localize=True
        )
    )
    geojson.add_to(group)
    group.add_to(m)

# 읍면동 경계
folium.GeoJson(
    emd,
    name="읍면동 경계",
    style_function=lambda x: {
        "fillColor": "none",
        "color": "gray",
        "weight": 1,
        "fillOpacity": 0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["EMD_NM"],
        aliases=["읍면동"],
        localize=True
    )
).add_to(m)

colormap.add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# ───────────────────────────────────────────────
# 10. 결과 저장
m.save("cluster_map_2_4_only.html")
print("✔ cluster_map_2_4_only.html 저장 완료")

cluster_dong_summary_reset = cluster_dong_summary.reset_index()
cluster_dong_summary_reset.to_csv("cluster_dong_summary_2_4.csv", index=False, encoding="utf-8-sig")
print("✔ cluster_dong_summary_2_4.csv 저장 완료 (한글 OK)")
