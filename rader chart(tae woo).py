import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# ───────────────────────────────────────────────
# 1. 데이터 불러오기 및 전처리
gdf = gpd.read_file(r"C:\Users\sec\Desktop\공모전 리얼\merged_1km_data.gpkg", layer="merged")
gdf = gdf.dropna(subset=["elder_pop"]).copy()

features = [
    'elder_pop', 'score_EMG', 'count_CLASS', 'count_KYRD',
    'count_WELFARE', 'count_LEISURE', 'count_HOSP'
]
distance_cols = [col for col in features if col != 'elder_pop']

# 이상치 제거
for col in distance_cols:
    gdf.loc[(gdf[col] >= 100) | (gdf[col] >= 999) | (gdf[col] <= -100), col] = np.nan
gdf_clean = gdf.dropna(subset=distance_cols).copy()

# ───────────────────────────────────────────────
# 2. 클러스터링 (k=6)
X = gdf_clean[features].copy()
for col in distance_cols:
    X[col] = -X[col]  # 거리값 부호 반전

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=6, random_state=42, n_init='auto')
gdf_clean['cluster'] = kmeans.fit_predict(X_scaled)

# ───────────────────────────────────────────────
# 3. 클러스터별 평균값 요약 (원본값 기준)
summary = gdf_clean.groupby('cluster')[features].mean()

# 정규화
summary_scaled = pd.DataFrame(
    StandardScaler().fit_transform(summary),
    columns=summary.columns,
    index=summary.index
)

# ───────────────────────────────────────────────
# 4. Radar Chart 시각화
labels = features
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

plt.figure(figsize=(8, 8))
colors = plt.cm.tab10(np.linspace(0, 1, summary_scaled.shape[0]))

for i, (cluster, row) in enumerate(summary_scaled.iterrows()):
    values = row.tolist()
    values += values[:1]
    plt.polar(angles, values, label=f'Cluster {cluster}', color=colors[i])
    plt.fill(angles, values, alpha=0.1, color=colors[i])

plt.xticks(angles[:-1], labels, fontsize=10)
plt.yticks([-2, -1, 0, 1, 2], fontsize=8)
plt.title("🧭 정규화된 클러스터별 변수 분포 Radar Chart", fontsize=14)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
plt.show()
