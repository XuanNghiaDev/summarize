"""
crawl_vnexpress.py
Lấy dữ liệu thực từ báo VnExpress để training model Text Summarization
Hỗ trợ cache và retry logic
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

CACHE_FILE = "data/vnexpress_cache.json"
REQUEST_TIMEOUT = 10
RETRY_ATTEMPTS = 3

# =========================
# LẤY NỘI DUNG BÀI VIẾT
# =========================
def crawl_article(url: str) -> Optional[Dict]:
    """Crawl nội dung một bài viết từ VnExpress"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # =========================
        # TITLE
        # =========================
        title_tag = soup.find("h1", class_="title-detail")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # =========================
        # DESCRIPTION
        # =========================
        desc_tag = soup.find("p", class_="description")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # =========================
        # CONTENT
        # =========================
        paragraphs = soup.find_all("p", class_="Normal")

        contents = []
        for p in paragraphs:
            # bỏ đoạn tác giả
            if p.find("strong"):
                continue

            text = p.get_text(strip=True)

            # bỏ đoạn quá ngắn
            if len(text) < 30:
                continue

            contents.append(text)

        article_content = "\n".join(contents)

        # Validate dữ liệu
        if not title or not article_content or len(article_content) < 100:
            return None

        # =========================
        # GỘP TITLE + DESCRIPTION
        # =========================
        final_summary = f"{title}. {description}".strip()

        return {
            "summary": final_summary,
            "article": article_content,
            "url": url
        }

    except Exception as e:
        print(f"  ✗ ERROR crawling {url}: {e}")
        return None


# =========================
# LẤY TOÀN BỘ BÀI TRONG CHUYÊN MỤC
# =========================
def crawl_category(category_url: str, limit: int = 7, delay: float = 1.0) -> List[Dict]:
    """Crawl toàn bộ bài viết từ một chuyên mục"""
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        seen = set()

        # lấy toàn bộ link bài báo
        for a in soup.find_all("a", href=True):
            href = a["href"]

            # chỉ lấy bài báo
            if "vnexpress.net" in href and href.endswith(".html"):
                # tránh duplicate
                if href not in seen:
                    seen.add(href)
                    links.append(href)

            # chỉ lấy N bài
            if len(links) >= limit:
                break

        print(f"\n📁 CATEGORY: {category_url}")
        print(f"📊 FOUND: {len(links)} articles")

        articles = []
        for idx, link in enumerate(links, 1):
            print(f"  [{idx}/{len(links)}] Crawling: {link}")

            article = crawl_article(link)

            if article:
                articles.append(article)

            time.sleep(delay)

        print(f"✓ Extracted {len(articles)} valid articles")
        return articles

    except Exception as e:
        print(f"✗ CATEGORY ERROR: {e}")
        return []


# =========================
# HỖ TRỢ CACHE
# =========================
def load_cache() -> List[Dict]:
    """Tải dữ liệu từ cache nếu tồn tại"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✓ Loaded {len(data)} articles from cache")
                return data
        except Exception as e:
            print(f"⚠ Failed to load cache: {e}")
    return []


def save_cache(data: List[Dict]) -> None:
    """Lưu dữ liệu vào cache"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved {len(data)} articles to cache")
    except Exception as e:
        print(f"✗ Failed to save cache: {e}")


# =========================
# DANH SÁCH CHUYÊN MỤC
# =========================
CATEGORIES = [
    'https://vnexpress.net/thoi-su',
    'https://vnexpress.net/the-gioi',
    'https://vnexpress.net/kinh-doanh',
    'https://vnexpress.net/khoa-hoc-cong-nghe',
    'https://vnexpress.net/goc-nhin',
    'https://vnexpress.net/bat-dong-san',
    'https://vnexpress.net/suc-khoe',
    'https://vnexpress.net/giai-tri',
    'https://vnexpress.net/the-thao',
    'https://vnexpress.net/phap-luat',
    'https://vnexpress.net/giao-duc',
    'https://vnexpress.net/doi-song',
    'https://vnexpress.net/oto-xe-may',
    'https://vnexpress.net/du-lich',
    'https://vnexpress.net/y-kien',
    'https://vnexpress.net/tam-su',
    'https://vnexpress.net/thu-gian'
]


# =========================
# CRAWL TOÀN BỘ
# =========================
def crawl_vnexpress(
    num_categories: Optional[int] = None,
    articles_per_category: int = 7,
    use_cache: bool = True,
    delay: float = 1.0
) -> List[Dict]:
    """
    Crawl dữ liệu từ VnExpress
    
    Args:
        num_categories: Số lượng chuyên mục crawl (None = tất cả)
        articles_per_category: Số bài viết mỗi chuyên mục
        use_cache: Dùng cache nếu tồn tại
        delay: Độ trễ giữa các request (giây)
    
    Returns:
        List of articles with {summary, article, url}
    """
    # Kiểm tra cache
    if use_cache:
        cached = load_cache()
        if cached:
            return cached

    categories_to_crawl = CATEGORIES[:num_categories] if num_categories else CATEGORIES

    all_data = []

    for idx, category in enumerate(categories_to_crawl, 1):
        print(f"\n{'='*60}")
        print(f"Category {idx}/{len(categories_to_crawl)}")
        print(f"{'='*60}")

        try:
            data = crawl_category(category, limit=articles_per_category, delay=delay)
            all_data.extend(data)
        except Exception as e:
            print(f"✗ CATEGORY ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"✓ TOTAL: {len(all_data)} articles")
    print(f"{'='*60}")

    # Lưu cache
    if all_data:
        save_cache(all_data)

    return all_data


# =========================
# MAIN - Run standalone
# =========================
if __name__ == "__main__":
    import sys

    num_cats = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    articles_per_cat = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    print(f"🚀 Crawling {num_cats} categories, {articles_per_cat} articles each...")

    data = crawl_vnexpress(
        num_categories=num_cats,
        articles_per_category=articles_per_cat,
        use_cache=False,
        delay=1.5
    )

    # Lưu vào file
    output_file = "data/vnexpress_dataset.json"
    os.makedirs("data", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved to {output_file}")
