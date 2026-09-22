import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .insight-container {
        background-color: #F0F9FF;
        border-left: 5px solid #0284C7;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    .insight-title {
        font-weight: 700;
        color: #0369A1;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
    }
    .insight-content {
        color: #334155;
        font-size: 0.92rem;
        margin: 0;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_movie_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 전처리: 세로막대(|)로 분리된 경우 첫 번째 장르만 사용
    df['genre_clean'] = df['genre'].astype(str).apply(
        lambda x: x.split('|')[0].strip() if pd.notna(x) and x != 'nan' and x != '' else '미분류'
    )
    
    # 개봉일 날짜형 변환
    df['openDt_parsed'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')
    
    return df

try:
    df = load_movie_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

st.sidebar.header("🔍 데이터 필터")

# 국가 선택 필터
all_nations = ["전체"] + sorted(df['nation'].dropna().unique().tolist())
selected_nation = st.sidebar.selectbox("제작 국가 선택", all_nations)

# 장르 선택 필터
all_genres = sorted(df['genre_clean'].unique().tolist())
selected_genres = st.sidebar.multiselect("장르 선택", all_genres, default=all_genres)

# 관객수 범위 필터
max_audi = int(df['total_audi'].max())
min_audi = int(df['total_audi'].min())
audi_range = st.sidebar.slider(
    "총 관객 수 범위 (명)",
    min_value=min_audi,
    max_value=max_audi,
    value=(min_audi, max_audi),
    step=10000
)

# 필터링 적용
filtered_df = df[
    (df['genre_clean'].isin(selected_genres)) &
    (df['total_audi'] >= audi_range[0]) &
    (df['total_audi'] <= audi_range[1])
]

if selected_nation != "전체":
    filtered_df = filtered_df[filtered_df['nation'] == selected_nation]

st.markdown('<div class="main-header">🎬 영화 데이터 그래프 도감 2 - 분포와 관계</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">박스오피스 상위권 영화 216편의 장르별 분포와 주요 흥행 지표 간의 관계 분석 도감</div>', unsafe_allow_html=True)

# 주요 지표 요약
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("분석 대상 영화 수", f"{len(filtered_df):,} 편")
with col2:
    st.metric("평균 총 관객 수", f"{int(filtered_df['total_audi'].mean() if not filtered_df.empty else 0):,} 명")
with col3:
    st.metric("평균 스크린 수", f"{int(filtered_df['first_scrn'].mean() if not filtered_df.empty else 0):,} 개")
with col4:
    st.metric("평균 TOP 10 유지일수", f"{filtered_df['days_in_top10'].mean():.1f} 일" if not filtered_df.empty else "0 일")

st.markdown("<br>", unsafe_allow_html=True)

# 인사이트 박스 출력 헬퍼 함수
def render_insight_box(text):
    st.markdown(
        f"""
        <div class="insight-container">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            <p class="insight-content">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.subheader("1. 장르별 영화 편수 분포")

if not filtered_df.empty:
    genre_counts = filtered_df['genre_clean'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']

    fig_donut = px.pie(
        genre_counts,
        values='편수',
        names='장르',
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_donut.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>장르: %{label}</b><br>영화 수: %{value}편<br>비율: %{percent:.1%}<extra></extra>',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig_donut.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=450
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # 1번 그래프 인사이트
    top_genre = genre_counts.iloc[0]['장르'] if len(genre_counts) > 0 else "N/A"
    top_ratio = (genre_counts.iloc[0]['편수'] / genre_counts['편수'].sum() * 100) if len(genre_counts) > 0 else 0
    
    render_insight_box(
        f"박스오피스 상위 10위권 영화 중 가장 큰 비중을 차지하는 장르는 <b>'{top_genre}'</b>(약 {top_ratio:.1f}%)이며, 특정 몇몇 대중성 높은 주요 장르에 흥행 상위권 진입 편수가 집중되는 경향을 보입니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("2. 개봉일 스크린 수와 총 관객 수의 관계")

if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x='first_scrn',
        y='total_audi',
        color='genre_clean',
        size='days_in_top10',
        hover_name='movieNm',
        hover_data={
            'first_scrn': ':,m',
            'total_audi': ':,m',
            'days_in_top10': True,
            'genre_clean': True,
            'nation': True
        },
        labels={
            'first_scrn': '개봉일 스크린 수 (개)',
            'total_audi': '총 관객 수 (명)',
            'genre_clean': '장르',
            'days_in_top10': 'TOP 10 유지일수'
        },
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig_scatter.update_layout(
        height=500,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9')
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    # 2번 그래프 인사이트
    render_insight_box(
        "개봉일 스크린 수가 확보될수록 총 관객 수 역시 증가하는 양의 상관관계를 보이지만, 스크린 수가 적더라도 TOP 10 유지일수가 긴 영화는 입소문을 통해 높은 총 관객 수를 기록하는 장기 흥행 양상을 보입니다."
    )

st.divider()

st.subheader("3. 장르별 총 관객 수 분포 비교")

if not filtered_df.empty:
    fig_box = px.box(
        filtered_df,
        x='genre_clean',
        y='total_audi',
        color='genre_clean',
        points="all",
        hover_name='movieNm',
        labels={
            'genre_clean': '장르',
            'total_audi': '총 관객 수 (명)'
        },
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_box.update_layout(
        height=480,
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9')
    )

    st.plotly_chart(fig_box, use_container_width=True)

    # 3번 그래프 인사이트
    render_insight_box(
        "장르별 중앙값과 사분위 범위를 비교하면 특정 장르는 관객 수의 편차가 커 대형 흥행작과 소규모 작품 간 격차가 심한 반면, 일부 장르는 비교적 균일한 관객층을 형성하는 분포 특성을 확인할 수 있습니다."
    )

st.divider()

st.subheader("4. TOP 10 차트 유지 기간과 최종 관객 수의 관계")

if not filtered_df.empty:
    fig_days = px.scatter(
        filtered_df,
        x='days_in_top10',
        y='total_audi',
        size='first_week_audi',
        color='nation',
        hover_name='movieNm',
        labels={
            'days_in_top10': '10위권에 머문 날수 (일)',
            'total_audi': '총 관객 수 (명)',
            'first_week_audi': '개봉 첫 주 관객 수',
            'nation': '제작 국가'
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig_days.update_layout(
        height=480,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9')
    )

    st.plotly_chart(fig_days, use_container_width=True)

    # 4번 그래프 인사이트
    render_insight_box(
        "박스오피스 TOP 10 상위권에 머무른 기간이 늘어날수록 누적 관객 수는 비례하여 증가하며, 초기 개봉 첫 주 관객 수가 큰 영화가 상위권 체류 기간도 길게 유지되는 유기적 관계가 나타납니다."
    )

with st.expander("📋 필터링된 데이터 상세 보기"):
    st.dataframe(
        filtered_df[['movieNm', 'genre_clean', 'nation', 'openDt', 'first_scrn', 'first_week_audi', 'total_audi', 'days_in_top10']].rename(columns={
            'movieNm': '영화명',
            'genre_clean': '주장르',
            'nation': '제작국가',
            'openDt': '개봉일',
            'first_scrn': '개봉일 스크린수',
            'first_week_audi': '첫주 관객수',
            'total_audi': '총 관객수',
            'days_in_top10': 'TOP10 유지일수'
        }),
        use_container_width=True
    )
