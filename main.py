# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="주민등록 인구 및 세대현황 시각화", layout="wide")

st.title("📊 주민등록 인구 및 세대현황(월간) 시각화")
st.write("CSV 파일을 업로드하거나 기본 데이터를 불러와 시각화할 수 있습니다.")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

@st.cache_data
def read_csv_flexible(file):
    """UTF-8 → CP949 순서로 읽기"""
    try:
        return pd.read_csv(file, encoding='utf-8')
    except Exception:
        return pd.read_csv(file, encoding='cp949')

if uploaded_file:
    df = read_csv_flexible(uploaded_file)
else:
    st.info("CSV 파일을 업로드하면 자동으로 시각화됩니다.")
    st.stop()

# 데이터 미리보기
st.subheader("데이터 미리보기")
st.dataframe(df.head())

# 날짜, 지역, 인구 관련 컬럼 자동 탐색
cols = df.columns.tolist()
date_col = next((c for c in cols if any(k in c for k in ["기간", "년월", "기준", "date", "월"])), None)
region_col = next((c for c in cols if any(k in c for k in ["행정구역", "지역", "시도", "시군구", "구분"])), None)
value_cols = [c for c in cols if any(k in c for k in ["인구", "세대", "인원", "수", "합계"])]

st.markdown(f"**자동 인식된 날짜 컬럼:** `{date_col}`")
st.markdown(f"**자동 인식된 지역 컬럼:** `{region_col}`")
st.markdown(f"**값(시각화 대상) 후보 컬럼:** {value_cols}")

if not date_col or not value_cols:
    st.error("날짜 또는 인구 관련 컬럼을 찾지 못했습니다. CSV의 열 이름을 확인해주세요.")
    st.stop()

# 날짜 변환 시도
try:
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
except Exception:
    pass

# 사용자 선택
target_col = st.selectbox("시각화할 수치 컬럼을 선택하세요", value_cols)

if region_col:
    selected_regions = st.multiselect(
        "표시할 지역 선택 (선택 안 하면 전체 평균)",
        df[region_col].unique().tolist(),
        default=df[region_col].unique().tolist()[:5]
    )
    filtered = df[df[region_col].isin(selected_regions)]
else:
    filtered = df.copy()

# Plotly 시각화
st.subheader("📈 시각화 결과")

if region_col:
    fig = px.line(
        filtered,
        x=date_col,
        y=target_col,
        color=region_col,
        markers=True,
        title=f"{target_col} 추이 (지역별)"
    )
else:
    fig = px.line(filtered, x=date_col, y=target_col, markers=True, title=f"{target_col} 추이")

fig.update_layout(
    xaxis_title="기간",
    yaxis_title=target_col,
    hovermode="x unified",
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# 통계 요약
st.subheader("📊 통계 요약")
st.write(filtered.describe())

st.success("✅ Plotly 그래프에서 확대·축소, 특정 지역 비교가 가능합니다.")
