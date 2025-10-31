# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(page_title="인구 및 세대현황 시각화", page_icon="📊", layout="wide")

st.markdown(
    "<h1 style='text-align:center; color:#333;'>📊 주민등록 인구 및 세대현황 시각화</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr style='margin-bottom:20px;'>", unsafe_allow_html=True)


# -----------------------------
# 데이터 미리보기
# -----------------------------
st.subheader("📄 데이터 미리보기")
st.dataframe(df.head(), use_container_width=True)

# -----------------------------
# 주요 컬럼 자동 탐색
# -----------------------------
cols = df.columns.tolist()
date_col = next((c for c in cols if any(k in c for k in ["기간", "년월", "기준", "date", "월"])), None)
region_col = next((c for c in cols if any(k in c for k in ["행정구역", "지역", "시도", "시군구", "구분"])), None)
value_cols = [c for c in cols if any(k in c for k in ["인구", "세대", "합계", "수", "인원"])]

if not date_col or not value_cols:
    st.error("❌ 날짜 또는 인구 관련 컬럼을 찾을 수 없습니다. CSV 열 이름을 확인해주세요.")
    st.stop()

# 날짜 변환 시도
try:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
except:
    pass

# -----------------------------
# 정보 요약
# -----------------------------
st.markdown(
    f"""
    <div style='padding:10px; background-color:#f8f9fa; border-radius:10px; margin:15px 0;'>
    📅 <b>기간 컬럼:</b> {date_col} &nbsp;&nbsp;
    📍 <b>지역 컬럼:</b> {region_col if region_col else "없음"} &nbsp;&nbsp;
    📈 <b>값 컬럼:</b> {', '.join(value_cols)}
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 시각화 옵션 선택
# -----------------------------
st.subheader("⚙️ 시각화 옵션 선택")

selected_values = st.multiselect(
    "시각화할 지표 선택 (여러 개 선택 가능)",
    value_cols,
    default=value_cols[:2]
)

if not selected_values:
    st.warning("지표를 하나 이상 선택하세요.")
    st.stop()

if region_col:
    regions = df[region_col].dropna().unique().tolist()
    selected_regions = st.multiselect(
        "표시할 지역 선택",
        regions,
        default=regions[:5]
    )
    filtered = df[df[region_col].isin(selected_regions)]
else:
    filtered = df.copy()

# -----------------------------
# 데이터 변환 및 그래프 생성
# -----------------------------
plot_df = filtered.melt(
    id_vars=[date_col, region_col] if region_col else [date_col],
    value_vars=selected_values,
    var_name="지표",
    value_name="값"
)

st.subheader("📈 시각화 결과")

if region_col:
    fig = px.line(
        plot_df,
        x=date_col,
        y="값",
        color="지표",
        line_dash=region_col,
        markers=True,
        title="선택한 지표 비교 (지역별)"
    )
else:
    fig = px.line(
        plot_df,
        x=date_col,
        y="값",
        color="지표",
        markers=True,
        title="선택한 지표 비교"
    )

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    title_font=dict(size=22, color="#333"),
    xaxis_title="기간",
    yaxis_title="값",
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 통계 요약
# -----------------------------
st.subheader("📊 통계 요약")
st.dataframe(filtered.describe(), use_container_width=True)
