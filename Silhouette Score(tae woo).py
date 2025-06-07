import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# ───────────────────────────────────────────────
# 1. 데이터 불러오기
gdf = gpd.read_file(r"C:\Users\sec\Desktop\공모전 리얼\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["elder_pop"]).copy()

# ───────────────────────────────────────────────
# 2. 이상치 제거
features = [
    'elder_pop', 'score_EMG', 'count_CLASS', 'count_KYRD',
    'count_WELFARE', 'count_LEISURE', 'count_HOSP'
]
distance_cols = [col for col in features if col != 'elder_pop']

for col in distance_cols:
    gdf.loc[(gdf[col] >= 100) | (gdf[col] >= 999) | (gdf[col] <= -100), col] = np.nan

gdf_clean = gdf.dropna(subset=distance_cols).copy()

# ───────────────────────────────────────────────
# 3. 거리 부호 반전 + 정규화
X = gdf_clean[features].copy()
for col in distance_cols:
    X[col] = -X[col]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ───────────────────────────────────────────────
# 4. Silhouette Score 계산 및 시각화
k_range = range(2, 11)
silhouette_scores = []

for k in k_range:
    model = KMeans(n_clusters=k, random_state=42, n_init='auto')
    labels = model.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    silhouette_scores.append(score)

# ───────────────────────────────────────────────
# 5. 그래프 출력
plt.figure(figsize=(8, 5))
plt.plot(k_range, silhouette_scores, marker='o', linestyle='-', color='green')
plt.title("🔢 Silhouette Score: 클러스터 수 vs. 평균 점수")
plt.xlabel("클러스터 수 (k)")
plt.ylabel("Silhouette Score (높을수록 좋음)")
plt.xticks(k_range)
plt.grid(True)
plt.tight_layout()
plt.show()
