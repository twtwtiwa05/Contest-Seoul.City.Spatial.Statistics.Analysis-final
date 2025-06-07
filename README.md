# 격자 기반 고령자 의료 복지 커버리지 통합 분석
본 프로젝트는 서울시를 대상으로 1km 격자 단위의 공간 데이터(노인여가시설, 병원, 응급의료시설, 노인교실, 노인복지기관, 경로당, 보건기관)를 활용하여, 고령 인구 분포와 복지·의료 시설의 접근성을 통합적으로 분석하고, LISA 및 K-means 클러스터링 기법을 통해 복지 및 의료 커버리지가 동시에 취약한 고위험 지역을 식별하였다. 특히 단순 시설 수 중심이 아닌 도로망 기반 이동 거리와 Huff 모델을 활용한 실제 선택 확률 기반 커버리지 지표를 구축함으로써, 공간적 접근성과 수요-공급 상호작용을 동시에 반영하였다. 또한, 공간통계 기반의 정량 분석을 통해 복지 사각지대의 공간적 클러스터를 도출하고, 행정동 단위로 개발 우선순위를 재설계하였다. 분석 결과, 신림동·상계동·반포동 등 10개 지역이 복지와 의료 모두에서 중복된 취약성을 나타냈으며, 이는 정책 개입의 시급성과 지역 맞춤형 대응 필요성을 뒷받침한다. 이에 따라 본 프로젝트는 모바일 복지 버스, 건강쉼터, 자치 기반 커뮤니티 복지망 등 지역별 특성을 반영한 창의적이고 실현 가능한 대안을 제안하고, 결과를 동적 지도 시각화 및 행정 활용이 가능한 엑셀 기반 자료로 가공하여 실제 정책에 연계 가능한 데이터 기반 의사결정 프레임워크를 제시하였다.

# 안내설명
anaconda, python 환경을 이용하여 본 프로젝트를 수행했습니다. 아래에 파이썬 코드를 clone해서 사용할 수 있습니다. 파이썬 코드를 통해 분석을 수행할 수 있고 folium을 이용하여 html 형식으로 시각화 할 수 있습니다. 실제 html 결과도 프로젝트에 첨부하였습니다. 크롬 브라우저를 이용해서 통해 시각화 자료도 볼 수 있습니다. 
# 파이썬 코드 
1.데이터 생성 병합 코드

-Merge data extracts(taewoo).py 

2.lisa 분석 파이썬 코드
  -count_CLASS-lisa(taewoo).py


  -count_HEALTH-lisa(taewoo).py


  -count_HOSP-lisa(taewoo).py


  -count_KYRD-lisa(taewoo).py


  -count_LEISURE-lisa(taewoo).py

  -count_WELFARE-lisa(taewoo).py

  -elder_pop-lisa(taewoo).py



3.Elbow Method로 K-MEANS 군집 수 정하는 파이썬 코드 

-Elbow Method(taewoo).py


4.rader chart로 군집 특성 시각화 하는 파이썬 코드


-rader chart(tae woo).py

5.K -MEANS 군집 분석 파이썬 코드 

-k-means cluster(tae woo).py

6.Huff 모델 기반 분석 파이썬 코드

-Living facilities- huff(taewoo).py

-medical treantment-huff(taewoo).py
