# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# 기본 페이지 설정
# -----------------------------------
st.set_page_config(page_title="인구 및 세대현황 시각화", page_icon="📊", layout="wide")

st.markdown(
    "<h1 style='text-align:center; color:#333;'>📊 주민등록 인구 및 세대현황 시각화</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr style='margin-bottom:20px;'>", unsafe_allow_html=True)

# -----------------------------------
# CSV 불러오기 (GitHub 또는 업로드)
# -----------------------------------
@st.cache_data
def read_csv_auto(file_or_url):
    import io, requests
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    delimiters = [",", ";", "\t"]

    # GitHub URL일 경우 자동 다운로드
    if isinstance(file_or_url, str) and file_or_url.startswith("http"):
        content = requests.get(file_or_url).content
        f = io.BytesIO(content)
    else:
        f = file_or_url

    for enc in encodings:
        for sep in delimiters:
            try:
                f.seek(0)
                df = pd.read_csv(f, encoding=enc, sep=sep)
                if df.shape[1] > 1:
                    return df
            except Exception:
                continue
    raise ValueError("CSV 파일을 읽을 수 없습니다.")

# -----------------------------------
# CSV 불러오기 UI
# -----------------------------------
option = st.radio(
    "데이터 불러오기 방법 선택",
    ["GitHub CSV URL", "직접 업로드"],
    horizontal=True,
)

if option == "GitHub CSV URL":
    github_url = st.text_input(
        "GitHub의 CSV raw 링크를 입력하세요:",
        placeholder="예: https://raw.githubusercontent.com/username/repo/main/data.csv"
    )
    if github_url:
        try:
            df = read_csv_auto(github_url)
            st.success("✅ GitHub CSV 파일을 성공적으로 불러왔습니다.")
        except Exception as e:
            st.error(f"❌ 불러오기 실패: {e}")
            st.stop()
    else:
        st.info("🔗 GitHub CSV URL을 입력하면 데이터를 불러옵니다.")
        st.stop()
else:
    uploaded_file = st.file_uploader("📁 CSV 파일을 선택하세요", type=["csv"])
    if uploaded_file:
        try:
            df = read_csv_auto(uploaded_file)
            st.success("✅ CSV 파일을 성공적으로 불러왔습니다.")
        except Exception as e:
            st.error(f"❌ 업로드 실패: {e}")
            st.stop()
    else:
        st.info("CSV 파일을 업로드하면 시각화가 시작됩니다.")
        st.stop()

# -----------------------------------
# 데이터 미리보기
# -----------------------------------
st.subheader("📄 데이터 미리보기")
st.dataframe(df.head(), use_container_width=True)

# -----------------------------------
# 주요 컬럼 자동 탐색
# -----------------------------------
cols = df.columns.tolist()
date_col = next((c for c in cols if any(k in c for k in ["기간", "년월", "기준", "date", "월"])), None)
region_col = next((c for c in cols if any(k in c for k in ["행정구역", "지역", "시도", "시군구", "구분"])), None)
value_cols = [c for c in cols if any(k in c for k in ["인구", "세대", "합계", "수", "인원"])]

if not date_col or not value_cols:
    st.error("❌ 날짜 또는 인구 관련 컬럼을 찾을 수 없습니다. CSV 열 이름을 확인해주세요.")
    st.stop()

try:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
except:
    pass

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

# -----------------------------------
# 사용자 선택
# -----------------------------------
st.subheader("⚙️ 시각화 옵션 선택")

target_col = st.selectbox("시각화할 지표를 선택하세요", value_cols)

if region_col:
    regions = df[region_col].dropna().unique().tolist()
    selected = st.multiselect("표시할 지역 선택", regions, default=regions[:5])
    filtered = df[df[region_col].isin(selected)]
else:
    filtered = df.copy()

# -----------------------------------
# 그래프
# -----------------------------------
st.subheader("📈 시각화 결과")

if region_col:
    fig = px.line(
        filtered,
        x=date_col,
        y=target_col,
        color=region_col,
        markers=True,
        title=f"{target_col} 추이 (지역별)",
    )
else:
    fig = px.line(filtered, x=date_col, y=target_col, markers=True, title=f"{target_col} 추이")

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    title_font=dict(size=22, color="#333"),
    xaxis_title="기간",
    yaxis_title=target_col,
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# 통계 요약
# -----------------------------------
st.subheader("📊 통계 요약")
st.dataframe(filtered.describe(), use_container_width=True)
