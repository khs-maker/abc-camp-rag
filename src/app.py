"""YES24 IT 베스트셀러 탐색적 데이터 분석(EDA), 검색, 추천 챗봇 Streamlit 대시보드."""

import json
import os
import re
from collections import Counter

import chromadb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from groq import Groq
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# 페이지 설정
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="YES24 IT 베스트셀러 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PATH_WITH_DESC = os.path.join(DATA_DIR, "yes24_it_bestsellers_with_desc.csv")
PATH_ORIGINAL = os.path.join(DATA_DIR, "yes24_it_bestsellers.csv")

# ---------------------------------------------------------------------------
# 데이터 로드 & 전처리
# ---------------------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
    if os.path.exists(PATH_WITH_DESC):
        df = pd.read_csv(PATH_WITH_DESC)
    elif os.path.exists(PATH_ORIGINAL):
        df = pd.read_csv(PATH_ORIGINAL)
        df["Description"] = ""
    else:
        return pd.DataFrame()

    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce").fillna(999).astype(int)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0).astype(int)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0.0)
    df["ReviewCount"] = pd.to_numeric(df["ReviewCount"], errors="coerce").fillna(0).astype(int)

    def parse_publish_ym(date_str: str) -> str:
        if not isinstance(date_str, str):
            return "기타"
        m = re.search(r"(\d{4})년\s*(\d{2})월", date_str)
        if m:
            return f"{m.group(1)}-{m.group(2)}"
        m2 = re.search(r"(\d{4})년", date_str)
        if m2:
            return f"{m2.group(1)}-01"
        return "기타"

    df["PublishYM"] = df["PublishDate"].apply(parse_publish_ym)
    df["PublishYear"] = df["PublishYM"].apply(lambda x: x.split("-")[0] if "-" in x else "기타")
    df["PublishMonth"] = df["PublishYM"].apply(lambda x: x.split("-")[1] if "-" in x else "00")

    # Description 에서 태그/특수문자 제거 (검색용)
    df["DescClean"] = df["Description"].fillna("").apply(
        lambda t: re.sub(r"[^\w\s가-힣]", " ", str(t))
    )

    st.session_state["has_desc"] = bool(df["Description"].str.strip().any())
    return df


# ---------------------------------------------------------------------------
# ChromaDB 벡터 검색
# ---------------------------------------------------------------------------
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
COLLECTION_NAME = "yes24_books"
EMBED_MODEL_NAME = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"


@st.cache_resource
def load_embed_model():
    return SentenceTransformer(EMBED_MODEL_NAME)


@st.cache_resource
def load_chroma_collection():
    if not os.path.exists(CHROMA_DIR):
        return None
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        return None


def vector_search(query: str, top_n: int = 10):
    """ChromaDB에서 의미 기반 유사 도서를 검색한다."""
    collection = load_chroma_collection()
    if collection is None:
        return []

    model = load_embed_model()
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_n,
        include=["documents", "metadatas", "distances"],
    )

    books = []
    if results and results["metadatas"]:
        for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
            similarity = 1 - dist  # cosine distance → similarity
            if similarity < 0.2:
                continue
            books.append({**meta, "similarity": round(similarity, 3)})
    return books


# ---------------------------------------------------------------------------
# Groq Function Calling 도구 정의
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_books_by_price",
            "description": "가격 범위로 도서를 검색하거나 정렬할 때 사용합니다. 최소~최대 가격 범위를 지정하여 해당 범위의 도서 목록을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_price": {
                        "type": "integer",
                        "description": "최소 가격 (원). 예: 10000",
                    },
                    "max_price": {
                        "type": "integer",
                        "description": "최대 가격 (원). 예: 30000",
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["price_asc", "price_desc", "rating", "reviews"],
                        "description": "정렬 기준: price_asc(가격 낮은순), price_desc(가격 높은순), rating(평점순), reviews(리뷰 많은순)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "반환할 최대 도서 수. 기본값 10.",
                    },
                },
                "required": ["min_price", "max_price"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_books_by_sales_rank",
            "description": "판매지수(리뷰 수 기준)로 도서를 검색하거나 정렬할 때 사용합니다. 리뷰 수는 판매량과 강하게 상관되며, 판매지수의 대리 지표로 활용됩니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_reviews": {
                        "type": "integer",
                        "description": "최소 리뷰 수. 예: 50",
                    },
                    "max_reviews": {
                        "type": "integer",
                        "description": "최대 리뷰 수. 예: 400",
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["reviews_desc", "price_asc", "price_desc", "rating"],
                        "description": "정렬 기준: reviews_desc(리뷰 많은순), price_asc(가격 낮은순), price_desc(가격 높은순), rating(평점순)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "반환할 최대 도서 수. 기본값 10.",
                    },
                },
                "required": ["min_reviews", "max_reviews"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_statistics",
            "description": "전체 도서의 가격 통계(최소, 최대, 평균, 중앙값, 표준편차)를 조회합니다. 가격 분포를 파악할 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_statistics",
            "description": "전체 도서의 판매지수(리뷰 수) 통계(최소, 최대, 평균, 중앙값)를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Groq Function Calling 실행 함수
# ---------------------------------------------------------------------------

def exec_tool(tool_name: str, tool_args: dict, dataframe: pd.DataFrame) -> str:
    """LLM이 호출한 도구를 실행하고 JSON 문자열을 반환한다."""

    if tool_name == "search_books_by_price":
        mn = tool_args.get("min_price", 0)
        mx = tool_args.get("max_price", 999999)
        sort_by = tool_args.get("sort_by", "price_asc")
        limit = tool_args.get("limit", 10)

        result = dataframe[(dataframe["Price"] >= mn) & (dataframe["Price"] <= mx)].copy()

        sort_map = {
            "price_asc": ("Price", True),
            "price_desc": ("Price", False),
            "rating": ("Rating", False),
            "reviews": ("ReviewCount", False),
        }
        col, asc = sort_map.get(sort_by, ("Price", True))
        result = result.sort_values(by=col, ascending=asc).head(limit)

        books = []
        for _, r in result.iterrows():
            books.append({
                "title": r["Title"],
                "author": r["Author"],
                "publisher": r["Publisher"],
                "price": int(r["Price"]),
                "rating": float(r["Rating"]),
                "review_count": int(r["ReviewCount"]),
                "link": r["Link"],
            })
        return json.dumps({"total_found": len(dataframe[(dataframe["Price"] >= mn) & (dataframe["Price"] <= mx)]), "books": books}, ensure_ascii=False)

    elif tool_name == "search_books_by_sales_rank":
        mn = tool_args.get("min_reviews", 0)
        mx = tool_args.get("max_reviews", 999999)
        sort_by = tool_args.get("sort_by", "reviews_desc")
        limit = tool_args.get("limit", 10)

        result = dataframe[
            (dataframe["ReviewCount"] >= mn) & (dataframe["ReviewCount"] <= mx)
        ].copy()

        sort_map = {
            "reviews_desc": ("ReviewCount", False),
            "price_asc": ("Price", True),
            "price_desc": ("Price", False),
            "rating": ("Rating", False),
        }
        col, asc = sort_map.get(sort_by, ("ReviewCount", False))
        result = result.sort_values(by=col, ascending=asc).head(limit)

        books = []
        for _, r in result.iterrows():
            books.append({
                "title": r["Title"],
                "author": r["Author"],
                "publisher": r["Publisher"],
                "price": int(r["Price"]),
                "rating": float(r["Rating"]),
                "review_count": int(r["ReviewCount"]),
                "link": r["Link"],
            })
        return json.dumps({"total_found": len(dataframe[(dataframe["ReviewCount"] >= mn) & (dataframe["ReviewCount"] <= mx)]), "books": books}, ensure_ascii=False)

    elif tool_name == "get_price_statistics":
        prices = dataframe["Price"]
        stats = {
            "min": int(prices.min()),
            "max": int(prices.max()),
            "mean": round(float(prices.mean()), 0),
            "median": round(float(prices.median()), 0),
            "std": round(float(prices.std()), 0),
            "count": len(dataframe),
        }
        return json.dumps(stats, ensure_ascii=False)

    elif tool_name == "get_sales_statistics":
        reviews = dataframe["ReviewCount"]
        stats = {
            "min": int(reviews.min()),
            "max": int(reviews.max()),
            "mean": round(float(reviews.mean()), 1),
            "median": round(float(reviews.median()), 1),
            "count": len(dataframe),
        }
        return json.dumps(stats, ensure_ascii=False)

    return json.dumps({"error": f"알 수 없는 도구: {tool_name}"}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CSS 스타일
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .title-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 28px 32px; border-radius: 14px; color: #fff;
        margin-bottom: 24px; box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    .title-banner h1 { margin:0; font-size:2.2rem; font-weight:800; letter-spacing:-0.5px; }
    .title-banner p  { margin:6px 0 0 0; font-size:1.05rem; opacity:0.88; }
    .book-card {
        background: var(--background-secondary-color,#fff); padding:18px 22px;
        border-radius:10px; border:1px solid rgba(0,0,0,0.06);
        margin-bottom:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04);
    }
    .book-title { font-size:17px; font-weight:700; color:#1e293b; margin-bottom:6px; }
    .book-meta  { font-size:12.5px; color:#64748b; margin-bottom:10px; }
    .badge { display:inline-block; padding:2px 9px; border-radius:12px;
             font-size:11px; font-weight:600; margin-right:5px; }
    .badge-rank    { background:#ffe4e6; color:#e11d48; }
    .badge-rating  { background:#fef9c3; color:#a16207; }
    .badge-price   { background:#dcfce7; color:#15803d; }
    .badge-reviews { background:#e0e7ff; color:#4338ca; }
    mark { background:#fde68a; padding:0 2px; border-radius:3px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 데이터 로드
# ---------------------------------------------------------------------------
df = load_data()

if df.empty:
    st.markdown(
        "<div class='title-banner'><h1>📚 YES24 IT 베스트셀러 대시보드</h1>"
        "<p>수집된 데이터가 없습니다. 먼저 크롤러를 실행해 주세요.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ---------------------------------------------------------------------------
# 타이틀
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class='title-banner'>
        <h1>📚 YES24 IT 베스트셀러 분석 & 검색</h1>
        <p>IT/모바일 분야 베스트셀러 1,000권의 데이터를 탐색하고 키워드로 도서를 검색하세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 사이드바 필터
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ 필터 & 설정")

# Groq API 키 입력
groq_api_key = st.sidebar.text_input(
    "🔑 Groq API Key",
    type="password",
    placeholder="gsk_...",
    help="https://console.groq.com 에서 무료로 발급받은 API 키를 입력하세요.",
)

sort_by = st.sidebar.selectbox(
    "정렬 기준",
    ["순위순", "평점 높은순", "리뷰 많은순", "가격 높은순", "가격 낮은순"],
)

all_publishers = sorted(df["Publisher"].dropna().unique())
selected_publishers = st.sidebar.multiselect("출판사", options=all_publishers, default=[])

min_rating, max_rating = st.sidebar.slider(
    "평점 범위", 0.0, 10.0,
    value=(float(df["Rating"].min()), float(df["Rating"].max())), step=0.1,
)

min_price, max_price = st.sidebar.slider(
    "가격 범위 (원)", int(df["Price"].min()), int(df["Price"].max()),
    value=(int(df["Price"].min()), int(df["Price"].max())), step=1000,
)

# 필터 적용
fdf = df.copy()
if selected_publishers:
    fdf = fdf[fdf["Publisher"].isin(selected_publishers)]
fdf = fdf[(fdf["Rating"] >= min_rating) & (fdf["Rating"] <= max_rating)]
fdf = fdf[(fdf["Price"] >= min_price) & (fdf["Price"] <= max_price)]

sort_map = {
    "평점 높은순": ("Rating", False),
    "리뷰 많은순": ("ReviewCount", False),
    "가격 높은순": ("Price", False),
    "가격 낮은순": ("Price", True),
    "순위순": ("Rank", True),
}
sort_col, sort_asc = sort_map[sort_by]
fdf = fdf.sort_values(by=sort_col, ascending=sort_asc)

# ---------------------------------------------------------------------------
# 탭 구성
# ---------------------------------------------------------------------------
tab_eda, tab_search, tab_chat = st.tabs(
    ["📊 탐색적 데이터 분석 (EDA)", "🔍 도서 검색", "🤖 도서 추천 챗봇"]
)

# ========================== TAB 1 : EDA ====================================
with tab_eda:
    # ---- KPI ----
    st.subheader("📈 요약 통계")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("도서 수", f"{len(fdf):,}권")
    c2.metric("평균 평점", f"{fdf['Rating'].mean():.2f}")
    c3.metric("평균 가격", f"{int(fdf['Price'].mean()):,}원")
    c4.metric("총 리뷰", f"{int(fdf['ReviewCount'].sum()):,}개")
    c5.metric("출판사 수", f"{fdf['Publisher'].nunique()}곳")

    st.markdown("---")

    if fdf.empty:
        st.warning("해당 필터에 맞는 도서가 없습니다.")
        st.stop()

    # ---- Row 1 : 출판사 Top10 + 가격 분포 ----
    row1_l, row1_r = st.columns(2)

    with row1_l:
        st.markdown("#### 🏢 출판사별 도서 수 Top 10")
        pub_cnt = fdf["Publisher"].value_counts().head(10).reset_index()
        pub_cnt.columns = ["출판사", "도서 수"]
        fig = px.bar(pub_cnt, x="도서 수", y="출판사", orientation="h",
                      color="도서 수", color_continuous_scale="Teal",
                      labels={"도서 수": "권", "출판사": ""})
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False,
                          margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with row1_r:
        st.markdown("#### 💵 가격 분포")
        fig = px.histogram(fdf, x="Price", nbins=25,
                           color_discrete_sequence=["#0f3460"],
                           labels={"Price": "가격 (원)", "count": "권"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), bargap=0.08)
        st.plotly_chart(fig, use_container_width=True)

    # ---- Row 2 : 평점 vs 리뷰 + 연도별 동향 ----
    row2_l, row2_r = st.columns(2)

    with row2_l:
        st.markdown("#### ⭐ 평점 vs 리뷰 수")
        color_col = "Publisher" if fdf["Publisher"].nunique() < 12 else None
        fig = px.scatter(fdf, x="Rating", y="ReviewCount", size="Price",
                          color=color_col, hover_name="Title",
                          size_max=30,
                          labels={"Rating": "평점", "ReviewCount": "리뷰 수"})
        fig.update_layout(xaxis_range=[1.5, 10.5], margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with row2_r:
        st.markdown("#### 📅 연도별 출판 동향")
        yt = fdf["PublishYear"].value_counts().reset_index()
        yt.columns = ["연도", "권수"]
        yt = yt.sort_values("연도")
        fig = px.bar(yt, x="연도", y="권수", color="권수",
                      color_continuous_scale="Sunset",
                      labels={"연도": "", "권수": "도서 수"})
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ---- Row 3 : 월별 출판 추이 + 평점 분포 ----
    row3_l, row3_r = st.columns(2)

    with row3_l:
        st.markdown("#### 📆 월별 출판 추이 (전체 기간)")
        monthly = fdf.groupby("PublishYM").size().reset_index(name="권수")
        monthly = monthly[monthly["PublishYM"] != "기타"].sort_values("PublishYM")
        if not monthly.empty:
            fig = px.line(monthly, x="PublishYM", y="권수", markers=True,
                           color_discrete_sequence=["#e11d48"],
                           labels={"PublishYM": "연-월", "권수": "도서 수"})
            fig.update_layout(xaxis_tickangle=-45, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("월별 데이터가 부족합니다.")

    with row3_r:
        st.markdown("#### 📊 평점 분포")
        fig = px.histogram(fdf, x="Rating", nbins=20,
                           color_discrete_sequence=["#f59e0b"],
                           labels={"Rating": "평점", "count": "권"})
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), bargap=0.08)
        st.plotly_chart(fig, use_container_width=True)

    # ---- Row 4 : 리뷰 Top 10 + 가격 box plot ----
    row4_l, row4_r = st.columns(2)

    with row4_l:
        st.markdown("#### 💬 리뷰 수 Top 10 도서")
        top_review = fdf.nlargest(10, "ReviewCount")[["Title", "ReviewCount", "Rating"]].reset_index(drop=True)
        top_review["Title"] = top_review["Title"].apply(lambda t: t[:28] + "…" if len(str(t)) > 28 else t)
        fig = px.bar(top_review, x="ReviewCount", y="Title", orientation="h",
                      color="Rating", color_continuous_scale="RdYlGn",
                      labels={"ReviewCount": "리뷰 수", "Title": ""})
        fig.update_layout(yaxis={"categoryorder": "total ascending"},
                          margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with row4_r:
        st.markdown("#### 📦 주요 출판사 가격 분포")
        top5_pubs = fdf["Publisher"].value_counts().head(5).index.tolist()
        box_df = fdf[fdf["Publisher"].isin(top5_pubs)]
        fig = px.box(box_df, x="Publisher", y="Price", color="Publisher",
                      labels={"Publisher": "", "Price": "가격 (원)"})
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ---- Row 5 : 키워드 분석 + 저자 분석 ----
    row5_l, row5_r = st.columns(2)

    with row5_l:
        st.markdown("#### 🔤 제목 핵심 키워드 Top 20")
        titles_text = " ".join(fdf["Title"].dropna().tolist())
        words = re.findall(r"[가-힣a-zA-Z]{2,}", titles_text)
        stop_words = {
            "with", "and", "the", "for", "using", "codes", "chatgpt",
        }
        words = [w for w in words if w.lower() not in stop_words]
        wc = Counter(words).most_common(20)
        if wc:
            wdf = pd.DataFrame(wc, columns=["키워드", "빈도"])
            fig = px.bar(wdf, x="키워드", y="빈도", color="빈도",
                          color_continuous_scale="Viridis",
                          labels={"키워드": "", "빈도": "횟수"})
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with row5_r:
        st.markdown("#### ✍️ 다출간 저자 Top 15")
        # 저자 쉼표 기준 분리
        authors_exploded = fdf["Author"].dropna().str.split(",").explode().str.strip()
        author_cnt = authors_exploded.value_counts().head(15).reset_index()
        author_cnt.columns = ["저자", "도서 수"]
        fig = px.bar(author_cnt, x="도서 수", y="저자", orientation="h",
                      color="도서 수", color_continuous_scale="Magma",
                      labels={"도서 수": "권", "저자": ""})
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False,
                          margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ---- 데이터 테이블 & 다운로드 ----
    st.markdown("---")
    st.subheader("📋 필터링된 도서 목록")
    display_cols = ["Rank", "Title", "Author", "Publisher", "PublishDate",
                    "Price", "Rating", "ReviewCount"]
    st.dataframe(
        fdf[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

    csv_bytes = fdf.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ 현재 필터 결과 CSV 다운로드", data=csv_bytes,
                       file_name="yes24_filtered.csv", mime="text/csv")

# ========================== TAB 2 : 검색 ===================================
with tab_search:
    st.subheader("🔎 키워드 도서 검색")

    sc1, sc2 = st.columns([4, 1])
    with sc1:
        query = st.text_input("검색 키워드 입력 (예: 클로드, 파이썬, AI, 프롬프트)",
                              placeholder="키워드를 입력하세요…")
    with sc2:
        search_in = st.radio("검색 범위", ["제목 + 내용", "제목만", "내용만"], index=0)

    # 정렬
    result_sort = st.radio(
        "결과 정렬", [" relevance (기본)", "평점 높은순", "리뷰 많은순", "가격 낮은순"],
        horizontal=True,
    )

    # 필터된 데이터 기반 검색
    sdf = fdf.copy()
    if query.strip():
        q = query.lower()
        if search_in == "제목만":
            mask = sdf["Title"].str.lower().str.contains(q, na=False)
        elif search_in == "내용만":
            mask = sdf["DescClean"].str.lower().str.contains(q, na=False)
        else:
            mask = (
                sdf["Title"].str.lower().str.contains(q, na=False)
                | sdf["DescClean"].str.lower().str.contains(q, na=False)
            )
        sdf = sdf[mask]

    if "평점 높은순" in result_sort:
        sdf = sdf.sort_values("Rating", ascending=False)
    elif "리뷰 많은순" in result_sort:
        sdf = sdf.sort_values("ReviewCount", ascending=False)
    elif "가격 낮은순" in result_sort:
        sdf = sdf.sort_values("Price", ascending=True)

    st.markdown(f"**검색 결과: {len(sdf)}권**")

    if sdf.empty:
        st.info("검색 결과가 없습니다. 다른 키워드나 필터를 시도해 보세요.")
    else:
        PAGE_SIZE = 20
        total_pages = max(1, -(-len(sdf) // PAGE_SIZE))  #向上取整
        if total_pages > 1:
            page = st.number_input("페이지", min_value=1, max_value=total_pages, value=1)
        else:
            page = 1
        start = (page - 1) * PAGE_SIZE
        page_df = sdf.iloc[start : start + PAGE_SIZE]

        def highlight(text: str, q: str) -> str:
            """검색어를 하이라이트하여 반환."""
            if not q.strip():
                return text
            pattern = re.compile(re.escape(q), re.IGNORECASE)
            return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", str(text))

        for _, row in page_df.iterrows():
            title_hl = highlight(row["Title"], query)
            author_hl = highlight(row["Author"], query)
            desc_hl = highlight(row["Description"], query) if row["Description"] else ""

            card = f"""
            <div class="book-card">
                <span class="badge badge-rank">🏆 {row['Rank']}위</span>
                <span class="badge badge-rating">⭐ {row['Rating']}</span>
                <span class="badge badge-price">💰 {row['Price']:,}원</span>
                <span class="badge badge-reviews">💬 {row['ReviewCount']}개</span>
                <div class="book-title" style="margin-top:8px">{title_hl}</div>
                <div class="book-meta">저자: <b>{author_hl}</b> | 출판사: <b>{row['Publisher']}</b> | 출판일: <b>{row['PublishDate']}</b></div>
            </div>
            """
            st.markdown(card, unsafe_allow_html=True)

            with st.expander(f"📖 '{row['Title'][:40]}' 상세 보기"):
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.metric("평점", f"{row['Rating']}")
                    st.metric("리뷰", f"{row['ReviewCount']}개")
                    st.metric("가격", f"{row['Price']:,}원")
                    if row["Link"]:
                        st.markdown(f"[🔗 YES24에서 보기]({row['Link']})")
                with c2:
                    st.markdown("**도서 소개:**")
                    if desc_hl:
                        st.markdown(desc_hl, unsafe_allow_html=True)
                    else:
                        st.write("*소개글이 없습니다.*")

        if total_pages > 1:
            st.caption(f"페이지 {page} / {total_pages} (총 {len(sdf)}권)")

# ========================== TAB 3 : 챗봇 ====================================
with tab_chat:
    st.subheader("🤖 AI 도서 추천 챗봇 (KLUE-BERT + ChromaDB)")

    if not groq_api_key:
        st.info(
            "💡 **왼쪽 사이드바**에서 Groq API Key를 입력해 주세요.\n\n"
            "[Groq Console](https://console.groq.com)에서 무료로 발급받을 수 있습니다."
        )
        st.stop()

    # 벡터 DB 상태 확인
    collection = load_chroma_collection()
    if collection is None:
        st.warning(
            "⚠️ 벡터 데이터베이스가 없습니다. 먼저 아래 명령으로 구축해 주세요:\n\n"
            "```bash\npython src/build_vectordb.py\n```"
        )
        st.stop()

    st.caption(f"📦 벡터 DB: {collection.count()}건의 도서 임베딩 로드 완료 (KLUE-BERT)")

    def build_context_from_books(books: list[dict]) -> str:
        """검색된 도서 리스트를 LLM 컨텍스트용 텍스트로 변환한다."""
        lines = []
        for b in books:
            parts = [
                f"순위: {b.get('rank', 'N/A')}",
                f"제목: {b.get('title', '')}",
                f"저자: {b.get('author', '')}",
                f"출판사: {b.get('publisher', '')}",
                f"출판일: {b.get('publish_date', '')}",
                f"가격: {b.get('price', 0):,}원",
                f"평점: {b.get('rating', 0)}",
                f"리뷰수: {b.get('review_count', 0)}개",
                f"링크: {b.get('link', '')}",
                f"유사도: {b.get('similarity', 0)}",
            ]
            lines.append(" | ".join(parts))
        return "\n".join(lines)

    def ask_groq(api_key: str, user_query: str, book_context: str, dataframe: pd.DataFrame) -> str:
        client = Groq(api_key=api_key)

        system_prompt = (
            "당신은 YES24 IT/모바일 분야 베스트셀러 전문 추천 도서관입니다.\n"
            "아래는 KLUE-BERT 임베딩 모델로 사용자 질문과 의미적으로 가장 유사한 도서 데이터입니다.\n"
            "사용자의 질문에 대해 이 데이터를 기반으로 가장 적합한 도서를 추천하세요.\n\n"
            "## 도구 사용 규칙\n"
            "- 사용자가 **가격 범위**를 물어보면 (예: '1만원 이하', '2만~3만원대', '가격이 가장 비싼 책') → `search_books_by_price` 도구를 호출하세요.\n"
            "- 사용자가 **판매지수/인기/리뷰**를 물어보면 (예: '가장 많이 팔린', '리뷰가 많은', '인기 있는') → `search_books_by_sales_rank` 도구를 호출하세요.\n"
            "- 사용자가 **가격 통계**를 물어보면 (예: '평균 가격이 얼마야', '가격 분포가 어떻게 되나') → `get_price_statistics` 도구를 호출하세요.\n"
            "- 사용자가 **판매지수 통계**를 물어보면 (예: '평균 리뷰 수', '판매지수 분포') → `get_sales_statistics` 도구를 호출하세요.\n"
            "- 도구 호출 결과를 받아서 사용자에게 보기 좋게 마크다운으로 답변하세요.\n"
            "- 도구 결과에 있는 도서만 추천하고, 없는 도서를 지어내지 마세요.\n\n"
            "## 추천 규칙\n"
            "1. 데이터에 없는 도서를 지어내지 마세요. 오직 아래 목록 또는 도구 결과에 있는 도서만 추천하세요.\n"
            "2. 추천할 도서가 없다면 솔직하게 없다고 답변하세요.\n"
            "3. 각 추천 도서에 대해 제목, 저자, 가격, 평점, 한 줄 추천 이유를 포함하세요.\n"
            "4. 추천 도서 뒤에 반드시 [도서 상세보기](링크) 형식으로 YES24 링크를 포함하세요.\n"
            "5. 마크다운 형식으로 보기 좋게 답변하세요.\n"
            "6. 최대 5권까지 추천하세요.\n\n"
            f"=== 의미 기반 검색 결과 (총 {len(books)}건, 유사도순 정렬) ===\n"
            f"{book_context}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]

        # Tool calling 루프 (최대 3회)
        for _ in range(3):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=2048,
            )

            choice = response.choices[0]

            # 더 이상 tool call이 없으면 최종 응답 반환
            if choice.finish_reason != "tool_calls" or not choice.message.tool_calls:
                return choice.message.content

            # tool_calls를 messages에 추가
            messages.append(choice.message)

            # 각 tool call 실행
            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                tool_result = exec_tool(fn_name, fn_args, dataframe)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

        # 루프 종료 시 최종 응답
        return response.choices[0].message.content or "죄송합니다. 요청을 처리할 수 없습니다."

    # 세션 상태 초기화
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "안녕하세요! 📚 YES24 IT 베스트셀러 추천 도서관입니다.\n\n"
                    "KLUE-BERT 임베딩 모델을 사용하여 의미적으로 가장 관련 있는 도서를 찾아드립니다.\n"
                    "가격 범위, 판매지수(리뷰 수) 기반 검색도 가능합니다.\n\n"
                    "어떤 종류의 책을 찾고 계신가요? 예시:\n"
                    "- \"1만원 이하 파이썬 책 추천해줘\"\n"
                    "- \"가장 많이 팔린 IT 책 보여줘\"\n"
                    "- \"가격이 2만원 이상인 AI 책有哪些\"\n"
                    "- \"평균 가격이 얼마야?\""
                ),
            }
        ]

    # 채팅 히스토리 출력
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 사용자 입력
    if user_input := st.chat_input("궁금한 점을 입력하세요..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 벡터 검색으로 관련 도서 찾기
        with st.spinner("🔍 KLUE-BERT로 의미 기반 도서 검색 중..."):
            books = vector_search(user_input, top_n=15)

        if not books:
            with st.chat_message("assistant"):
                no_result = "죄송합니다. 요청하신 키워드와 관련된 도서를 찾지 못했습니다. 다른 키워드로 다시 검색해 보세요."
                st.markdown(no_result)
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": no_result}
            )
        else:
            book_ctx = build_context_from_books(books)

            with st.chat_message("assistant"):
                with st.spinner(f"📚 상위 {len(books)}건의 유사 도서 기반으로 추천을 생성하고 있습니다..."):
                    try:
                        answer = ask_groq(groq_api_key, user_input, book_ctx, fdf)
                    except Exception as e:
                        answer = f"⚠️ API 호출 중 오류가 발생했습니다: {e}"

                st.markdown(answer)

            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )
