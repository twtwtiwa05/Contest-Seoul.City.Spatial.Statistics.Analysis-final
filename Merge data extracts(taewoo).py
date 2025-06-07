import geopandas as gpd
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# 1) 파일 경로 설정
elder_shp   = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_인구정보-고령 인구 수(전체)-(격자) 1KM_서울특별시_202410\\nlsp_020001010.shp"
kyrd_shp    = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-경로당 접근성-500M_2023\\123.2 경로당(시군구격자) 접근성.shp"
emg_shp     = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-응급의료시설 접근성-500M_2023\\159.2 응급의료시설(시군구격자) 접근성.shp"
class_shp   = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-노인교실 접근성-500M_2023\\127.2 노인교실(시군구격자) 접근성.shp"
hosp_shp    = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-병원 접근성-500M_2023\\147.2 병원(시군구격자) 접근성.shp"
health_shp  = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-보건기관 접근성-500M_2023\\135.2 보건기관(시군구격자) 접근성.shp"
welfare_shp = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-노인복지관-500M_2023\\119.2 노인복지관(시군구격자) 접근성.shp"
leisure_shp = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\(B100)국토통계_국토정책지표-노인여가복지시설 접근성-500M_2023\\131.2 노인여가복지시설(시군구격자) 접근성.shp"

# ──────────────────────────────────────────────────────────────────────────────
# 2) GeoDataFrame 불러오기 및 CRS 통일
gdf_elder   = gpd.read_file(elder_shp).to_crs(epsg=4326)
gdf_kyrd    = gpd.read_file(kyrd_shp).to_crs(epsg=4326).rename(columns={'value': 'count_KYRD'})
gdf_emg     = gpd.read_file(emg_shp).to_crs(epsg=4326).rename(columns={'value': 'score_EMG'})
gdf_class   = gpd.read_file(class_shp).to_crs(epsg=4326).rename(columns={'value': 'count_CLASS'})
gdf_hosp    = gpd.read_file(hosp_shp).to_crs(epsg=4326).rename(columns={'value': 'count_HOSP'})
gdf_health  = gpd.read_file(health_shp).to_crs(epsg=4326).rename(columns={'value': 'count_HEALTH'})
gdf_welfare = gpd.read_file(welfare_shp).to_crs(epsg=4326).rename(columns={'value': 'count_WELFARE'})
gdf_leisure = gpd.read_file(leisure_shp).to_crs(epsg=4326).rename(columns={'value': 'count_LEISURE'})

# ──────────────────────────────────────────────────────────────────────────────
# 3) 집계용 컬럼 설정
cols_1km = ['gid','geometry']
cols_kyrd = ['gid','count_KYRD']
cols_emg  = ['gid','score_EMG']
cols_cls  = ['gid','count_CLASS']
cols_hosp = ['gid','count_HOSP']
cols_hlth = ['gid','count_HEALTH']
cols_wlf  = ['gid','count_WELFARE']
cols_lsr  = ['gid','count_LEISURE']

# ──────────────────────────────────────────────────────────────────────────────
# 4) 500m → 1km 집계 (spatial join)
def aggregate_to_1km(gdf_500m, cols_500m, gdf_1km, value_col):
    join = gpd.sjoin(gdf_500m[cols_500m + ['geometry']], gdf_1km[cols_1km], how='left', predicate='within')
    join = join.rename(columns={'gid_left': 'gid_500m', 'gid_right': 'gid_1km'})
    return join.groupby('gid_1km')[value_col].sum().reset_index()

agg_kyrd  = aggregate_to_1km(gdf_kyrd, cols_kyrd, gdf_elder, 'count_KYRD')
agg_emg   = aggregate_to_1km(gdf_emg, cols_emg, gdf_elder, 'score_EMG')
agg_cls   = aggregate_to_1km(gdf_class, cols_cls, gdf_elder, 'count_CLASS')
agg_hosp  = aggregate_to_1km(gdf_hosp, cols_hosp, gdf_elder, 'count_HOSP')
agg_hlth  = aggregate_to_1km(gdf_health, cols_hlth, gdf_elder, 'count_HEALTH')
agg_wlf   = aggregate_to_1km(gdf_welfare, cols_wlf, gdf_elder, 'count_WELFARE')
agg_lsr   = aggregate_to_1km(gdf_leisure, cols_lsr, gdf_elder, 'count_LEISURE')

# ──────────────────────────────────────────────────────────────────────────────
# 5) 병합
df_1km = gdf_elder[['gid','val','geometry']].rename(columns={'val':'elder_pop'})

df_1km = df_1km.merge(agg_kyrd,  left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')
df_1km = df_1km.merge(agg_emg,   left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')
df_1km = df_1km.merge(agg_cls,   left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')
df_1km = df_1km.merge(agg_hosp,  left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')
df_1km = df_1km.merge(agg_hlth,  left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')
df_1km = df_1km.merge(agg_wlf,   left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')
df_1km = df_1km.merge(agg_lsr,   left_on='gid', right_on='gid_1km', how='left').drop(columns='gid_1km')

# NaN → 0
for col in ['count_KYRD','score_EMG','count_CLASS','count_HOSP','count_HEALTH','count_WELFARE','count_LEISURE']:
    df_1km[col] = df_1km[col].fillna(0)

print("=== 병합 후 1km 격자 샘플 ===")
print(df_1km.head())

# ──────────────────────────────────────────────────────────────────────────────
# 6) 파일 저장
shp_path = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.shp"
gpkg_path = r"C:\\Users\\sec\\Desktop\\공모전 리얼\\merged_1km_data.gpkg"

df_1km.to_file(shp_path)
df_1km.to_file(gpkg_path, layer='merged', driver='GPKG')

print(f"✔ 병합된 1km 결과가 저장되었습니다.\n → SHP: {shp_path}\n → GPKG: {gpkg_path}")
