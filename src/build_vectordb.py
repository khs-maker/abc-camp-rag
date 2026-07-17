"""CSV → ChromaDB 벡터 데이터베이스 구축 스크립트.

KLUE-BERT 기반 한국어 문장 임베딩 모델(snunlp/KR-SBERT-V40K-klueNLI-augSTS)을 사용하여
YES24 IT 베스트셀러 도서의 제목+소개글을 벡터화하고 ChromaDB에 저장한다.
"""

import os
import re

import chromadb
import pandas as pd
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")
CSV_PATH = os.path.join(DATA_DIR, "yes24_it_bestsellers_with_desc.csv")
COLLECTION_NAME = "yes24_books"

MODEL_NAME = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build():
    print(f"CSV 로드 중: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce").fillna(999).astype(int)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0).astype(int)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0.0)
    df["ReviewCount"] = pd.to_numeric(df["ReviewCount"], errors="coerce").fillna(0).astype(int)
    print(f"총 {len(df)}권 로드 완료")

    print(f"임베딩 모델 로드 중: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print("모델 로드 완료")

    # 각 도서의 임베딩용 텍스트 생성: 제목 + 소개글
    documents = []
    metadatas = []
    ids = []

    for _, row in df.iterrows():
        title = str(row.get("Title", "")).strip()
        desc = clean_text(str(row.get("Description", "")))
        text = f"{title}. {desc}" if desc else title

        documents.append(text)
        metadatas.append({
            "rank": int(row["Rank"]),
            "title": title,
            "author": str(row.get("Author", "")),
            "publisher": str(row.get("Publisher", "")),
            "publish_date": str(row.get("PublishDate", "")),
            "price": int(row["Price"]),
            "rating": float(row["Rating"]),
            "review_count": int(row["ReviewCount"]),
            "link": str(row.get("Link", "")),
        })
        ids.append(f"book_{row['Rank']}")

    print(f"임베딩 생성 중 ({len(documents)}권)...")
    embeddings = model.encode(documents, show_progress_bar=True, batch_size=32)
    embeddings_list = embeddings.tolist()
    print("임베딩 생성 완료")

    print(f"ChromaDB 저장 중: {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # 기존 컬렉션이 있으면 삭제 후 재생성
    try:
        client.delete_collection(COLLECTION_NAME)
        print("기존 컬렉션 삭제 완료")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # 배치 단위로 삽입 (ChromaDB 제한: 최대 5461건)
    BATCH = 500
    for i in range(0, len(documents), BATCH):
        end = min(i + BATCH, len(documents))
        collection.add(
            ids=ids[i:end],
            documents=documents[i:end],
            embeddings=embeddings_list[i:end],
            metadatas=metadatas[i:end],
        )
        print(f"  저장 진행: {end}/{len(documents)}")

    print(f"완료! 총 {collection.count()}건 저장됨")
    print(f"벡터 DB 경로: {CHROMA_DIR}")


if __name__ == "__main__":
    build()
