# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# 기본 페이지 설정
# ----------------------------
st.set_page_config(
    page_title="주민등록 인구 및 세대현황 시각화",
    page_icon="📊",
    layout="wide"
)

# ----------------------------
# 상단 제목 섹션
# ----------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #333333;'>
        📊 주민등록 인구 및 세대현황 시각화
    </h1>
    <p style='text-align: center; color: #555555; font-size: 17px;'>
        주민등록 인구 및 세대 현황 데이터를 업로드하면 자동으로 시각화됩니다.
    </p>
    <hr style='border: 1px solid #ccc; margin-top: 10px; margin-bottom: 30px;'>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# CSV 업로드 및 읽기 함수
# ----------------------------
@st.cache_data
def read_csv_auto(file):
    """CSV 파일 자동 인식 (인코딩/구분자 자동 시도)"""
    import io
    if file is None:
        return None

    file.seek(0)
    content = file.read()
    if not content:
        raise ValueError("업로드한 파일이 비어 있습니다.")
    file.seek(0)

    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    delimiters = [",", ";", "\t"]

    for enc in encodings:
        for sep in delimiters:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=enc, sep=sep)
                if df.shape[1] > 1:
                    return df
            except Exception:
                continue

    raise ValueError("CSV 파일을 읽을 수 없습니다. (인코딩 또는 구분자 문제)")

# ----------------------------
# 파일 업로드 UI
# ----------------------------
uploaded_file = st.file_uploader(
    "📁 CSV 파일을 선택하세요",
    type=["csv"],
    label_visibility="collapsed"
)

if not uploaded_file:
    st.markdown(
        "<div style='text-align:center; color:#777; font-size:16px;'>CSV 파일을 업로드하면 자동으로 그래프가 생성됩니다.</div>",
        unsafe_allow_html=True
    )
    st.stop()

# ----------------------------
# 데이터 읽기
# ----------------------------
try:
    df = read_csv_auto(uploaded_file)
except Exception as e:
    st.error(f"❌ 파일을 불러오는 중 오류 발생: {e}")
    st.stop()

# ----------------------------
# 데이터 미리보기
# ----------------------------
st.subheader("📄 데이터 미리보기")
st.dataframe(df.head(), use_container_width=True)

# ----------------------------
# 주요 컬럼 자동 탐색
# ----------------------------
cols = df.columns.tolist()
date_col = next((c for c in cols if any(k in c for k in ["기간", "년월", "기준", "date", "월"])), None)
region_col = next((c for c in cols if any(k in c for k in ["행정구역", "지역", "시도", "시군구", "구분"])), None)
value_cols = [c for c in cols if any(k in c for k in ["인구", "세대", "인원", "수", "합계"])]

if not date_col or not value_cols:
    st.error("날짜 또는 인구 관련 컬럼을 찾지 못했습니다. CSV의 열 이름을 확인해주세요.")
    st.stop()

st.markdown(
    f"""
    <div style='padding:10px 15px; background-color:#f9f9f9; border-radius:10px; margin-top:10px; margin-bottom:20px;'>
    📅 <b>날짜 컬럼:</b> {date_col} &nbsp;&nbsp;
    📍 <b>지역 컬럼:</b> {region_col if region_col else "없음"} &nbsp;&nbsp;
    📈 <b>값 컬럼 후보:</b> {', '.join(value_cols)}
    </div>
    """,
    unsafe_allow_html=True
)

# 날짜 변환 시도
try:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
except Exception:
    pass

# ----------------------------
# 사용자 선택 UI
# ----------------------------
st.markdown("### ⚙️ 시각화 옵션")

target_col = st.selectbox("시각화할 지표를 선택하세요", value_cols)

if region_col:
    selected_regions = st.multiselect(
        "표시할 지역을 선택하세요 (미선택 시 전체)",
        options=df[region_col].unique().tolist(),
        default=df[region_col].unique().tolist()[:5]
    )
    filtered = df[df[region_col].isin(selected_regions)]
else:
    filtered = df.copy()

# ----------------------------
# Plotly 시각화
# ----------------------------
st.markdown("### 📈 시각화 결과")

if region_col:
    fig = px.line(
        filtered,
        x=date_col,
        y=target_col,
        color=region_col,
        markers=True,
        title=f"{target_col} 변화 추이 (지역별)",
    )
else:
    fig = px.line(
        filtered,
        x=date_col,
        y=target_col,
        markers=True,
        title=f"{target_col} 변화 추이",
    )

fig.update_layout(
    xaxis_title="기간",
    yaxis_title=target_col,
    template="plotly_white",
    hovermode="x unified",
    title_x=0.5,
    title_font=dict(size=22, color="#333"),
    legend=dict(title=None, orientation="h", y=-0.2, x=0.5, xanchor="center"),
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 통계 요약
# ----------------------------
st.markdown("### 📊 통계 요약")
st.dataframe(filtered.describe(), use_container_width=True)

st.success("✅ 데이터 시각화가 완료되었습니다.")
