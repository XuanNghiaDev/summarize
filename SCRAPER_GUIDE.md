# 🚀 VnExpress Web Scraper Integration

## 📋 Overview

Integrated a robust web scraper to collect real articles from VnExpress newspaper for your Text Summarization model training.

## 📁 New Files Created

- **`crawl_vnexpress.py`** - Main scraper module with:
  - `crawl_article()` - Extracts single article content, title, description
  - `crawl_category()` - Extracts multiple articles from a category
  - `crawl_vnexpress()` - Main function with cache support
  - Error handling and retry logic
  - Configurable delays and limits

- **Updated `generate_sample_data.py`** - Now supports:
  - `load_vnexpress_data()` - Loads cached or crawled data
  - `process_vnexpress_data()` - Converts raw data to training format
  - `generate()` - Now accepts `use_real_data` and `force_crawl` parameters

- **Updated `run_pipeline.py`** - Command-line arguments:
  - `--real` - Use real VnExpress data
  - `--crawl` - Force recrawl (bypass cache)

## 🎯 Usage

### 1. Crawl Data Standalone
```bash
# Crawl 2 categories, 5 articles each
python crawl_vnexpress.py 2 5

# Output: data/vnexpress_cache.json
```

### 2. Run Pipeline with Real Data
```bash
# Vietnamese with real data
python run_pipeline.py vi --real

# Both languages (English uses samples)
python run_pipeline.py both --real

# Force crawl fresh data
python run_pipeline.py vi --real --crawl
```

### 3. Run Pipeline with Sample Data (Default)
```bash
# Quick testing with sample data
python run_pipeline.py vi
python run_pipeline.py both
```

## 📊 Data Format

Output JSON structure:
```json
{
  "summary": "title. description",
  "article": "full article content",
  "url": "https://vnexpress.net/...",
  "id": "vi_0000",
  "lang": "vi"
}
```

## ⚙️ Features

✅ **Automatic Caching** - Cached data at `data/vnexpress_cache.json`  
✅ **Error Handling** - Skips malformed/empty articles automatically  
✅ **Smart Delays** - Respects server with configurable delays  
✅ **Flexible Categories** - 8 main categories (Politics, World, Business, Tech, Health, Education, Law, Sports)  
✅ **Backward Compatible** - Falls back to sample data if real data unavailable  

## 🔍 Crawled Categories

- 📍 Thời sự (Politics)
- 🌍 Thế giới (World)
- 💼 Kinh doanh (Business)
- 💻 Khoa học Công nghệ (Tech)
- ❤️ Sức khỏe (Health)
- 📚 Giáo dục (Education)
- ⚖️ Pháp luật (Law)
- ⚽ Thể thao (Sports)

## 📝 Notes

- Uses `requests` + `BeautifulSoup4` for scraping
- Configurable articles per category (default: 7)
- Minimum article length: 100 characters
- Request timeout: 10 seconds
- User-Agent header included to avoid blocking

## 🐛 Troubleshooting

**No articles scraped:**
- Check internet connection
- VnExpress website may have changed HTML structure
- Try with more categories: `crawl_vnexpress.py 3 10`

**Cache not working:**
- Delete `data/vnexpress_cache.json` and recrawl
- Use `--crawl` flag to force refresh

**Import errors:**
- Install: `pip install requests beautifulsoup4`
