# YES24 IT 베스트셀러 분석 프로젝트

YES24 IT/모바일 분야 베스트셀러 데이터를 수집하고, 시각화 대시보드 및 AI 추천 챗봇을 구현한 프로젝트입니다.

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **데이터 소스** | YES24 IT/모바일 베스트셀러 (1,000권) |
| **수집 항목** | 순위, 제목, 저자, 출판사, 출판일, 가격, 평점, 리뷰 수, 소개글 |
| **핵심 기술** | Python, Streamlit, ChromaDB, KLUE-BERT, Groq LLM |

---

## 주요 기능

### 1. 웹 크롤러 (`scraper.py`)
- YES24 IT/모바일 베스트셀러 페이지를 자동으로 크롤링
- 페이지네이션 자동 처리로 전체 도서 목록 수집
- CSV 파일로 저장 (`data/yes24_it_bestsellers.csv`)

### 2. 상세 설명 수집기 (`src/fetch_content.py`)
- 수집된 도서의 상세 페이지에서 소개글(Description)을 비동기로 크롤링
- aiohttp 기반 비동기 처리로 빠른 수집 (동시 요청 5개)
- 설명이 추가된 CSV 저장 (`data/yes24_it_bestsellers_with_desc.csv`)

### 3. 벡터 데이터베이스 구축 (`src/build_vectordb.py`)
- KLUE-BERT (`snunlp/KR-SBERT-V40K-klueNLI-augSTS`) 한국어 임베딩 모델 사용
- 도서 제목 + 소개글을 벡터화하여 ChromaDB에 저장
- 의미 기반 유사 도서 검색 가능

### 4. Excel 대시보드 (`src/create_excel_dashboard.py`)
- CSV 데이터를 기반으로 Excel 대시보드 자동 생성
- 6개 시트: 대시보드, 도서 목록, 출판사 분석, 키워드 분석, 평점리뷰 분석, 연도월별 동향
- 차트 및 KPI 자동 생성

### 5. Streamlit 대시보드 (`src/app.py`)
- **탐색적 데이터 분석 (EDA)**: 출판사별 도서 수, 가격 분포, 평점 vs 리뷰, 연도별 동향, 키워드 분석 등
- **도서 검색**: 키워드 기반 제목/내용 검색, 필터링, 페이지네이션
- **AI 추천 챗봇**: KLUE-BERT 벡터 검색 + Groq LLM Function Calling 기반 추천
  - 벡터 DB는 앱 실행 시 자동 구축 (최초 1회만 소요)

---

## 프로젝트 구조

```
ABC-LAG/
├── data/
│   ├── yes24_it_bestsellers.csv          # 기본 수집 데이터
│   ├── yes24_it_bestsellers_with_desc.csv # 설명 포함 데이터
│   ├── yes24_it_mobile_bestseller.csv    # 모바일 베스트셀러
│   ├── metadata.tsv                      # 벡터 DB 메타데이터
│   ├── vectors.tsv                       # 벡터 데이터
│   └── chroma_db/                        # ChromaDB 저장소 (자동 구축)
├── src/
│   ├── app.py                            # Streamlit 대시보드 메인
│   ├── build_vectordb.py                 # 벡터 DB 구축 스크립트
│   ├── create_excel_dashboard.py         # Excel 대시보드 생성
│   ├── create_pptx.js                    # PPT 생성 스크립트
│   └── fetch_content.py                  # 상세 설명 수집기
├── scraper.py                            # 기본 크롤러
├── fetch_page.py                         # 페이지 수집 유틸리티
├── requirements.txt                      # Python 의존성
├── opencode.json                         # opencode 설정
└── .gitignore                            # Git 무시 규칙
```

---

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상 환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터 수집

```bash
# 1단계: 베스트셀러 목록 크롤링
python scraper.py

# 2단계: 도서 상세 설명 수집 (선택)
python src/fetch_content.py
```

### 3. 대시보드 실행

```bash
# Streamlit 대시보드 실행
streamlit run src/app.py
```

> **참고:** 벡터 데이터베이스(ChromaDB)는 앱 실행 시 자동으로 구축됩니다. (최초 실행 시 잠시 소요)

### 5. Excel 대시보드 생성 (선택)

```bash
python src/create_excel_dashboard.py
```

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| **언어** | Python 3.10+ |
| **웹 크롤링** | requests, BeautifulSoup, aiohttp |
| **데이터 처리** | pandas, csv |
| **시각화** | Streamlit, Plotly, openpyxl |
| **벡터 DB** | ChromaDB |
| **임베딩 모델** | KLUE-BERT (snunlp/KR-SBERT-V40K-klueNLI-augSTS) |
| **LLM** | Groq (llama-3.3-70b-versatile) |

---

## 데이터 컬럼

| 컬럼명 | 설명 | 유형 |
|--------|------|------|
| Rank | 베스트셀러 순위 | int |
| Title | 도서 제목 | str |
| Author | 저자 | str |
| Publisher | 출판사 | str |
| PublishDate | 출판일 | str |
| Price | 판매가 (원) | int |
| Rating | 평점 | float |
| ReviewCount | 리뷰 수 | int |
| Link | YES24 상세 페이지 URL | str |
| Description | 도서 소개글 | str |

---

## 주의사항

- 크롤링 시 과도한 요청을 방지하기 위해 `time.sleep(1.5)` 적용
- `.gitignore`에 엑셀(`*.xlsx`), 파워포인트(`*.pptx`) 파일은 커밋에서 제외
- Groq API 키는 [Groq Console](https://console.groq.com)에서 무료 발급 가능

---

## 라이선스

이 프로젝트는 학습 및 연구 목적으로 제작되었습니다.
