"""YES24 IT/모바일 베스트셀러 크롤러 모듈.

이 모듈은 YES24 베스트셀러 카테고리에서 도서 정보를 페이지별로 파싱하고,
수집한 데이터를 CSV 파일로 저장하는 기능을 수행합니다.
"""

import csv
import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


def get_bestseller_books(category_number: str = "001001003", page_size: int = 24) -> list[dict]:
    """YES24 IT/모바일 베스트셀러 목록 전체 페이지에서 도서 정보를 수집한다.

    Args:
        category_number: 수집 대상 카테고리 번호 (기본값: "001001003" - IT 모바일).
        page_size: 페이지당 도서 수 (기본값: 24).

    Returns:
        수집된 도서 정보 딕셔너리 리스트.
    """
    books = []
    page = 1
    last_page = 1
    base_url = "https://www.yes24.com/product/category/bestseller"
    
    # 실제 브라우저와 유사한 헤더 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.yes24.com/",
        "Connection": "keep-alive"
    }

    print("수집을 시작합니다...")

    while True:
        params = {
            "categoryNumber": category_number,
            "pageNumber": page,
            "pageSize": page_size
        }
        
        print(f"페이지 {page} 요청 중...")
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"페이지 {page} 요청 중 오류 발생: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        
        # 첫 페이지에서 마지막 페이지 파악
        if page == 1:
            end_btn = soup.select_one("div.yesUI_pagen[data-search-type='page'] a.end")
            if end_btn and end_btn.get("title"):
                try:
                    last_page = int(end_btn.get("title"))
                    print(f"감지된 마지막 페이지: {last_page}")
                except ValueError:
                    last_page = 10  # 파싱 실패 시 기본값 설정
            else:
                # '맨끝' 버튼이 없는 경우 숫자로 된 링크 중 가장 큰 값을 탐색
                page_links = soup.select("div.yesUI_pagen[data-search-type='page'] a.num")
                pages = [1]
                for link in page_links:
                    try:
                        pages.append(int(link.text.strip()))
                    except ValueError:
                        pass
                last_page = max(pages)
                print(f"감지된 마지막 페이지(숫자 링크 기준): {last_page}")

        # 도서 아이템 목록 파싱
        items = soup.select("div.itemUnit")
        if not items:
            print(f"페이지 {page}에서 도서 데이터를 찾을 수 없습니다. 수집을 종료합니다.")
            break

        for item in items:
            # 순위
            rank_el = item.select_one("em.ico.rank")
            rank = rank_el.text.strip() if rank_el else ""

            # 도서 정보 영역
            info_el = item.select_one("div.item_info")
            if not info_el:
                continue

            # 도서명 및 상세 링크
            title_el = info_el.select_one("a.gd_name")
            title = title_el.text.strip() if title_el else ""
            link = urljoin("https://www.yes24.com", title_el.get("href", "")) if title_el else ""

            # 저자 (여러 명일 수 있으므로 쉼표로 연결)
            author_els = info_el.select("span.info_auth a")
            if author_els:
                authors = ", ".join([a.text.strip() for a in author_els])
            else:
                # a 태그가 없는 경우 텍스트 전체에서 파싱 시도
                auth_span = info_el.select_one("span.info_auth")
                authors = auth_span.text.replace(" 저", "").strip() if auth_span else ""

            # 출판사
            pub_el = info_el.select_one("span.info_pub a")
            publisher = pub_el.text.strip() if pub_el else ""
            if not publisher:
                pub_span = info_el.select_one("span.info_pub")
                publisher = pub_span.text.strip() if pub_span else ""

            # 출판일
            date_el = info_el.select_one("span.info_date")
            pub_date = date_el.text.strip() if date_el else ""

            # 판매가
            price_el = info_el.select_one("strong.txt_num em.yes_b")
            price = price_el.text.strip().replace(",", "") if price_el else ""

            # 평점
            rating_el = info_el.select_one("span.rating_grade em.yes_b")
            rating = rating_el.text.strip() if rating_el else ""

            # 리뷰 수
            review_el = info_el.select_one("span.rating_rvCount em.txC_blue")
            review_count = review_el.text.strip() if review_el else "0"

            books.append({
                "Rank": rank,
                "Title": title,
                "Author": authors,
                "Publisher": publisher,
                "PublishDate": pub_date,
                "Price": price,
                "Rating": rating,
                "ReviewCount": review_count,
                "Link": link
            })

        print(f"페이지 {page} 수집 완료 (현재 누적 도서 수: {len(books)})")

        if page >= last_page:
            print("마지막 페이지에 도달하여 수집을 종료합니다.")
            break

        page += 1
        time.sleep(1.5)  # 과도한 요청 방지를 위한 딜레이

    return books


def save_to_csv(books: list[dict], filename: str = "yes24_it_bestsellers.csv") -> None:
    """수집된 도서 정보를 CSV 파일로 저장한다.

    Args:
        books: 저장할 도서 정보 딕셔너리 리스트.
        filename: 저장할 CSV 파일명 (기본값: "yes24_it_bestsellers.csv").
    """
    if not books:
        print("저장할 데이터가 없습니다.")
        return

    fieldnames = ["Rank", "Title", "Author", "Publisher", "PublishDate", "Price", "Rating", "ReviewCount", "Link"]
    
    try:
        with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for book in books:
                writer.writerow(book)
        print(f"성공적으로 데이터를 {filename} 파일로 저장했습니다.")
    except IOError as e:
        print(f"CSV 저장 중 오류 발생: {e}")


if __name__ == "__main__":
    bestseller_books = get_bestseller_books()
    save_to_csv(bestseller_books)
