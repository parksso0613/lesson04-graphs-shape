import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간 및 분포",
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
    try:
        df = pd.read_csv(url)
    except Exception as e:
        # 백업용 대체 샘플 데이터 (외부 URL 접속 실패 시 앱이 꺼지지 않도록 방어)
        data = {
            'movieCd': ['20200001', '20200002', '20200003', '20200004', '20200005', '20200006'],
            'movieNm': ['샘플영화 A', '샘플영화 B', '샘플영화 C', '샘플영화 D', '샘플영화 E', '샘플영화 F'],
            'openDt': ['20230101', '20230105', '20230210', '20230301', '20230405', '20230501'],
            'genre': ['드라마|멜로', '액션|스릴러', '애니메이션', '코미디', '드라마', '액션'],
            'nation': ['한국', '미국', '일본', '한국', '프랑스', '미국'],
            'first_scrn': [1000, 1500, 500, 800, 300, 1200],
            'first_show': [5000, 7000, 2000, 4000, 1500, 6000],
            'first_week_audi': [500000, 1200000, 200000, 300000, 100000, 800000],
            'total_audi': [3500000, 8500000, 1200000, 2100000, 450000, 5500000],
            'days_in_top10': [25, 40, 15, 20, 10, 30]
        }
        df = pd.DataFrame(data)
        st.warning("⚠️ 원본 데이터 서버 접속에 일시적인 문제가 있어 기본 샘플 데이터를 불러왔습니다.")

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

all_nations = ["전체"] + sorted(df['nation'].dropna().unique().tolist())
selected_nation = st.sidebar.selectbox("제작 국가 선택", all_nations)

all_genres = sorted(df['genre_clean'].unique().tolist())
selected_genres = st.sidebar.multiselect("장르 선택", all_genres, default=all_genres)

max_audi = int(df['total_audi'].max()) if not df.empty else 1000000
min_audi = int(df['total_audi'].min()) if not df.empty else 0
audi_range = st.sidebar.slider(
    "총 관객 수 범위 (명)",
    min_value=min_audi,
    max_value=max(max_audi, min_audi + 1),
    value=(min_audi, max(max_audi, min_audi + 1)),
    step=10000
)

filtered_df = df[
    (df['genre_clean'].isin(selected_genres)) &
    (df['total_audi'] >= audi_range[0]) &
    (df['total_audi'] <= audi_range[1])
]

if selected_nation != "전체":
    filtered_df = filtered_df[filtered_df['nation'] == selected_nation]

st.markdown('<div class="main-header">🎬 영화 데이터 그래프 도감 1 - 시간 및 분포</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">KOBIS 1년치 일별 박스오피스 상위권 영화 데이터 시각화 도감</div>', unsafe_allow_html=True)

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
    
    top_genre = genre_counts.iloc[0]['장르'] if len(genre_counts) > 0 else "N/A"
    top_ratio = (genre_counts.iloc[0]['편수'] / genre_counts['편수'].sum() * 100) if len(genre_counts) > 0 else 0
    
    render_insight_box(
        f"박스오피스 상위권 영화 중 가장 큰 비중을 차지하는 장르는 <b>'{top_genre}'</b>(약 {top_ratio:.1f}%)이며, 특정 대중성 높은 주요 장르에 편수가 집중되는 경향을 보입니다."
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

    render_insight_box(
        "각 칸의 면적은 해당 영화의 총 관객 수(total_audi)에 비례합니다. 이를 통해 장르 전체의 시장 규모와 특정 영화가 장르 내에서 차지하는 흥행 비중을 비교할 수 있습니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("3. 총 관객 수 분포 (히스토그램)")

if not filtered_df.empty:
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

    max_movie = filtered_df.loc[filtered_df['total_audi'].idxmax()]
    max_title = max_movie['movieNm']
    max_audi_val = max_movie['total_audi']

    counts, bin_edges = np.histogram(filtered_df['total_audi'], bins=min(10, len(filtered_df)))
    max_bin_idx = counts.argmax()
    bin_start_man = bin_edges[max_bin_idx] / 10000
    bin_end_man = bin_edges[max_bin_idx + 1] / 10000

    render_insight_box(
        f"대부분의 영화({counts[max_bin_idx]}편)가 <b>약 {bin_start_man:,.0f}만 명 ~ {bin_end_man:,.0f}만 명</b> 구간에 몰려 있으며, 상위 흥행작으로 갈수록 개체 수가 줄어드는 분포를 보입니다.<br>"
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
        "개봉일 스크린수가 많을수록 대체로 총 관객수가 높아지는 양의 상관관계를 나타냅니다. 스크린수 대비 입소문으로 선전한 작품도 함께 관찰됩니다."
    )
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("5. 주요 장르별 총 관객수 분포 (상자 그림)")

if not filtered_df.empty:
    genre_counts_filtered = filtered_df['genre_clean'].value_counts()
    top_genres = genre_counts_filtered[genre_counts_filtered >= 2].index.tolist() # 샘플 데이터 호환을 위해 기준 유연화

    df_box = filtered_df[filtered_df['genre_clean'].isin(top_genres)]

    if not df_box.empty:
        fig_box = px.box(
            df_box,
            x='genre_clean',
            y='total_audi',
            color='genre_clean',
            points='outliers',
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

        render_insight_box(
            "주요 장르별 총 관객수 분포입니다. 상자 범위를 벗어나 위쪽으로 튀어나온 점(Outlier)에 마우스를 올리면 흥행을 견인한 작품의 이름을 확인할 수 있습니다."
        )
    else:
        st.info("조건에 부합하는 장르 데이터가 부족합니다.")
else:
    st.warning("선택한 필터 조건에 해당하는 데이터가 없습니다.")

st.divider()

st.subheader("6. 개봉일 스크린수, 총 관객수, 첫 주 관객수의 관계 (버블 차트)")

if not filtered_df.empty:
    df_bubble = filtered_df.copy()
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
        "개봉 초기 관객 동원력('첫 주 관객수')을 원의 크기로 반영한 버블 차트입니다. 초기 흥행이 최종 관객수까지 이어지는지 시각적으로 파악할 수 있습니다."
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
        "제작 국가(nation)에서 장르(genre)로 연결되는 선버스트 차트입니다. 각 영역의 크기는 해당 국가 및 장르에 속한 영화 편수를 나타냅니다."
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
