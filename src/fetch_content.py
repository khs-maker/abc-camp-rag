"""YES24 IT 베스트셀러 상세 설명 수집 모듈.

이 모듈은 기존 수집된 도서 목록 CSV의 상세 링크(Link)에 비동기로 요청을 보내
각 도서의 상세 소개글(Description)을 크롤링하고, 이를 추가한 새 CSV 파일을 저장합니다.
"""

import asyncio
import csv
import os
import re
from typing import Any
import aiohttp
from bs4 import BeautifulSoup

# 입력 및 출력 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "data", "yes24_it_bestsellers.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "yes24_it_bestsellers_with_desc.csv")

# 웹 요청용 헤더 설정 (실제 브라우저 유사)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def clean_html_text(raw_html: str) -> str:
    """HTML 태그와 불필요한 공백을 제거하여 순수 텍스트로 정제한다.

    Args:
        raw_html: 정제할 원본 HTML 문자열.

    Returns:
        정제된 순수 텍스트 문자열.
    """
    if not raw_html:
        return ""
    # HTML 태그 제거
    text = re.sub(r"<[^>]*>", " ", raw_html)
    # 엔티티 문자 처리
    text = (
        text.replace("&nbsp;", " ")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
    )
    # 다중 공백 및 줄바꿈 정리
    text = re.sub(r"\s+", " ", text)
    return text.strip()


async def fetch_book_description(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
    retries: int = 3,
) -> str:
    """도서 상세 페이지에서 책 소개 텍스트를 크롤링한다.

    Args:
        session: aiohttp 클라이언트 세션 객체.
        url: 도서 상세 페이지 URL.
        semaphore: 동시 요청 제한을 위한 세마포어 객체.
        retries: 요청 실패 시 재시도 횟수.

    Returns:
        수집된 도서 소개글 텍스트. 실패 시 빈 문자열 반환.
    """
    if not url or not url.startswith("http"):
        return ""

    async with semaphore:
        for attempt in range(retries):
            try:
                # 과도한 트래픽 유발 방지를 위한 약한 지연
                await asyncio.sleep(0.1)
                async with session.get(url, headers=HEADERS, timeout=15) as response:
                    if response.status == 200:
                        # YES24는 기본적으로 EUC-KR 또는 UTF-8을 사용하므로 호환성 처리
                        html = await response.text(encoding="utf-8", errors="replace")
                        soup = BeautifulSoup(html, "html.parser")

                        # 1순위: textarea.replace_introduce (YES24 책소개 원본 텍스트가 인코딩되어 있음)
                        intro_el = soup.select_one("textarea.replace_introduce")
                        if intro_el and intro_el.text.strip():
                            return clean_html_text(intro_el.text)

                        # 2순위: meta description (요약본)
                        meta_desc = soup.find("meta", attrs={"name": "description"})
                        if meta_desc and meta_desc.get("content"):
                            return clean_html_text(str(meta_desc.get("content")))

                        # 3순위: og:description
                        og_desc = soup.find("meta", attrs={"property": "og:description"})
                        if og_desc and og_desc.get("content"):
                            return clean_html_text(str(og_desc.get("content")))

                        return ""
                    else:
                        print(f"[Warning] HTTP {response.status} for {url} (Attempt {attempt+1}/{retries})")
            except Exception as e:
                print(f"[Error] Failed to fetch {url} (Attempt {attempt+1}/{retries}): {e}")
            
            # 재시도 전 대기
            await asyncio.sleep(1.0)
        
        return ""


async def main() -> None:
    """메인 실행 함수. CSV 데이터를 읽어 상세 설명을 수집한 뒤 저장한다."""
    if not os.path.exists(INPUT_CSV):
        print(f"[Error] 입력 CSV 파일이 존재하지 않습니다: {INPUT_CSV}")
        return

    print("도서 목록을 불러오는 중...")
    books: list[dict[str, Any]] = []
    with open(INPUT_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            books.append(dict(row))

    total_books = len(books)
    print(f"총 {total_books}개의 도서 데이터를 확인했습니다.")

    # 동시 요청 수 제한 (5개)
    sem = asyncio.Semaphore(5)
    
    async with aiohttp.ClientSession() as session:
        print("책 소개 정보 수집을 시작합니다... (이 작업은 몇 분 정도 소요될 수 있습니다)")
        
        # 진행상황을 모니터링하기 위해 gather 대신 태스크 리스트를 준비하고 
        # 완료될 때마다 로깅할 수 있게끔 수정
        results = []
        completed_count = 0
        
        # as_completed를 쓰지 않고 gather로 결과를 모으되 중간 출력을 위해 
        # gather에 들어가는 개별 코루틴을 래핑하여 완료 카운트를 올릴 수 있다.
        async def fetch_and_count(book_link: str) -> str:
            nonlocal completed_count
            res = await fetch_book_description(session, book_link, sem)
            completed_count += 1
            if completed_count % 50 == 0 or completed_count == total_books:
                print(f"진행 상황: {completed_count}/{total_books} 완료 ({(completed_count/total_books)*100:.1f}%)")
            return res

        ordered_tasks = [fetch_and_count(book.get("Link", "")) for book in books]
        results = await asyncio.gather(*ordered_tasks)
        
        for book, desc in zip(books, results):
            book["Description"] = desc

    # 새 CSV 파일에 저장
    fieldnames = list(books[0].keys())
    try:
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for book in books:
                writer.writerow(book)
        print(f"성공적으로 상세 설명이 추가된 데이터를 저장했습니다: {OUTPUT_CSV}")
    except IOError as e:
        print(f"[Error] CSV 파일 저장 실패: {e}")


if __name__ == "__main__":
    asyncio.run(main())
