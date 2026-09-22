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

st.subheader("2. 장르 및 영화별 총 관객 수 분포 (트리맵)")

if not filtered_df.empty:
    fig_treemap = px.treemap(
        filtered_df,
        path=[px.Constant("전체 장르"), 'genre_clean', 'movieNm'],
        values='total_audi',
        color='genre_clean',
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig_treemap.update_traces(
        hovertemplate='<b>%{label}</b><br>총 관객 수: %{value:,}명<extra></extra>',
        textinfo='label+value'
    )

    fig_treemap.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=550
    )

    st.plotly_chart(fig_treemap, use_container_width=True)

    # 2번 그래프 인사이트
    render_insight_box(
        "각 칸의 면적은 해당 영화의 총 관객 수(total_audi)에 비례합니다. 이를 통해 장르 전체의 시장 규모와 특정 영화가 장르 내에서 차지하는 흥행 비중을 한눈에 비교할 수 있습니다."
    )

st.divider()

st.subheader("3. 총 관객 수 분포 (히스토그램)")

if not filtered_df.empty:
    import numpy as np

    # 히스토그램 생성
    fig_hist = px.histogram(
        filtered_df,
        x='total_audi',
        nbins=20,
        labels={'total_audi': '총 관객 수 (명)', 'count': '영화 수 (편)'},
        color_discrete_sequence=['#0284C7']
    )

    fig_hist.update_traces(
        hovertemplate='<b>관객 수 구간</b>: %{x}<br><b>영화 수</b>: %{y}편<extra></extra>'
    )

    fig_hist.update_layout(
        xaxis_title="총 관객 수 (명)",
        yaxis_title="영화 수 (편)",
        margin=dict(t=30, b=30, l=30, r=30),
        height=450,
        bargap=0.1
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    # 가장 관객 수가 많은 영화 탐색
    max_movie = filtered_df.loc[filtered_df['total_audi'].idxmax()]
    max_title = max_movie['movieNm']
    max_audi_val = max_movie['total_audi']

    # 집중 구간 계산 (10개 구간 기준)
    counts, bin_edges = np.histogram(filtered_df['total_audi'], bins=10)
    max_bin_idx = counts.argmax()
    bin_start_man = bin_edges[max_bin_idx] / 10000
    bin_end_man = bin_edges[max_bin_idx + 1] / 10000

    # 3번 그래프 인사이트 및 주요 정보 문구 출력
    render_insight_box(
        f"대부분의 영화({counts[max_bin_idx]}편)가 <b>약 {bin_start_man:,.0f}만 명 ~ {bin_end_man:,.0f}만 명</b> 구간에 몰려 있으며, 상위 흥행작으로 갈수록 개체 수가 급격히 줄어드는 전형적인 오른쪽으로 긴 꼬리 분포를 보입니다.<br>"
        f"현재 검색 조건에서 가장 관객 수가 많은 영화는 <b>'{max_title}'</b> ({max_audi_val:,}명)입니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("4. 개봉일 스크린수와 총 관객수의 관계 (산점도)")

if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x='first_scrn',
        y='total_audi',
        color='genre_clean',
        hover_name='movieNm',
        hover_data={'first_scrn': ':,', 'total_audi': ':,', 'genre_clean': False},
        labels={'first_scrn': '개봉일 스크린수 (개)', 'total_audi': '총 관객수 (명)', 'genre_clean': '장르'}
    )
    fig_scatter.update_traces(marker=dict(size=9, opacity=0.8))
    fig_scatter.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        height=500
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    render_insight_box(
        "개봉일 스크린수가 많을수록 대체로 총 관객수가 높아지는 양의 상관관계를 나타냅니다. 다만, 스크린수가 적음에도 불구하고 입소문을 타고 선전한 작품이나, 초기 스크린 확보 대비 최종 관객수가 다소 아쉬운 사례도 함께 관찰됩니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("5. 주요 장르별 총 관객수 분포 (상자 그림)")

if not filtered_df.empty:
    # 영화 편수가 10편 이상인 장르만 선별
    genre_counts_filtered = filtered_df['genre_clean'].value_counts()
    top_genres = genre_counts_filtered[genre_counts_filtered >= 10].index.tolist()

    df_box = filtered_df[filtered_df['genre_clean'].isin(top_genres)]

    if not df_box.empty:
        fig_box = px.box(
            df_box,
            x='genre_clean',
            y='total_audi',
            color='genre_clean',
            points='outliers',  # 상자 밖으로 튀는 이상치(Outliers) 점만 표시
            hover_name='movieNm',
            hover_data={'total_audi': ':,', 'genre_clean': False},
            labels={'genre_clean': '장르', 'total_audi': '총 관객수 (명)'}
        )
        fig_box.update_layout(
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            height=500
        )

        st.plotly_chart(fig_box, use_container_width=True)

        genres_str = ", ".join([f"'{g}'" for g in top_genres])
        render_insight_box(
            f"영화가 10편 이상 수록된 주요 장르({genres_str})의 총 관객수 분포입니다. 상자 범위를 크게 벗어나 위쪽으로 튀어나온 점(Outlier)에 마우스를 올리면 장르 흥행을 견인한 메가 히트 작품의 이름을 확인할 수 있습니다."
        )
    else:
        st.info("영화가 10편 이상인 장르가 현재 선택된 필터 조건에 없습니다.")
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("6. 개봉일 스크린수, 총 관객수, 첫 주 관객수의 관계 (버블 차트)")

if not filtered_df.empty:
    df_bubble = filtered_df.copy()
    # 원 크기 계산용 (0 이하 예외 처리)
    df_bubble['bubble_size'] = df_bubble['first_week_audi'].apply(lambda x: max(x, 1))

    fig_bubble = px.scatter(
        df_bubble,
        x='first_scrn',
        y='total_audi',
        size='bubble_size',
        color='genre_clean',
        hover_name='movieNm',
        hover_data={
            'first_scrn': ':,',
            'total_audi': ':,',
            'first_week_audi': ':,',
            'bubble_size': False,
            'genre_clean': False
        },
        labels={
            'first_scrn': '개봉일 스크린수 (개)',
            'total_audi': '총 관객수 (명)',
            'first_week_audi': '첫 주 관객수 (명)',
            'genre_clean': '장르'
        },
        size_max=40
    )
    fig_bubble.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        height=520
    )

    st.plotly_chart(fig_bubble, use_container_width=True)

    render_insight_box(
        "4번 산점도에 <b>'개봉 첫 주 관객수'</b>를 원의 크기로 반영한 버블 차트입니다. 개봉 초기 관객 동원력이 컸던 작품(큰 원)이 최종 관객수까지 이어지는지, 혹은 초기 흥행은 작았으나 장기 집권하며 관객수가 늘어났는지 시각적으로 쉽게 파악할 수 있습니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트 차트)")

if not filtered_df.empty:
    fig_sunburst = px.sunburst(
        filtered_df,
        path=['nation', 'genre_clean'],
        color='nation',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig_sunburst.update_traces(
        hovertemplate='<b>%{label}</b><br>영화 수: %{value}편<br>상위 대비 비율: %{percentParent:.1%}<extra></extra>',
        textinfo='label+value'
    )

    fig_sunburst.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=500
    )

    st.plotly_chart(fig_sunburst, use_container_width=True)

    render_insight_box(
        "제작 국가(nation)에서 장르(genre)로 연결되는 선버스트 차트입니다. 각 영역의 크기는 해당 국가 및 장르에 속한 <b>영화 편수</b>를 나타내며, 안쪽 국가별 층위에서 바깥쪽 장르 층위로 국가별 주요 영화 제작 분포를 한눈에 비교할 수 있습니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

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
