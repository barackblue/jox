# core/scraper.py
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse

HEADERS = {
    'User-Agent': 'jox-scraper/1.0 (+https://example.com)',
    'Accept-Language': 'en-US,en;q=0.9'
}

def safe_truncate(text, chars=600):
    if not text:
        return ''
    if len(text) <= chars:
        return text
    return text[:chars].rsplit(' ', 1)[0] + '…'

def get_duckduckgo_urls(query, max_results=10):
    """Try to fetch top result URLs from DuckDuckGo HTML search using GET (more stable)."""
    try:
        r = requests.get('https://html.duckduckgo.com/html/', params={'q': query}, headers=HEADERS, timeout=8)
        r.raise_for_status()
    except Exception as e:
        # network / block issue
        # print("ddg request fail:", e)
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    # preferred selector for ddg html
    for a in soup.select('a.result__a'):
        href = a.get('href')
        if href:
            links.append(href)
            if len(links) >= max_results:
                break

    # fallback: any <a> results (best-effort)
    if not links:
        for a in soup.select('a'):
            href = a.get('href')
            if href and href.startswith('http'):
                links.append(href)
                if len(links) >= max_results:
                    break
    return links

def resolve_redirects(url):
    """Follow redirects once to get the final url (best-effort)."""
    try:
        r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=6)
        if r.status_code < 400 and r.url:
            return r.url
    except Exception:
        pass
    return url

def scrape_url_summary(url, max_chars=600):
    """Scrape a single URL and return dict with title, summary, source_url.
       Works without Django settings (uses local safe_truncate)."""
    try:
        final = resolve_redirects(url)
        r = requests.get(final, headers=HEADERS, timeout=8)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, 'html.parser')
    for s in soup(['script', 'style', 'noscript', 'header', 'footer', 'iframe']):
        s.decompose()

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
    if not paragraphs:
        # fallback to meta description or first big text block
        meta = soup.find('meta', attrs={'name':'description'}) or soup.find('meta', attrs={'property':'og:description'})
        if meta and meta.get('content'):
            paragraphs = [meta.get('content')]
        else:
            # try main text containers
            main = soup.find(['article','main','div'])
            if main:
                txt = main.get_text(" ", strip=True)
                if txt:
                    paragraphs = [txt]

    content = "\n\n".join(paragraphs).strip()
    if not content:
        return None

    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else (urlparse(url).netloc or url)
    summary = safe_truncate(content, max_chars)
    # polite pause
    time.sleep(0.15)
    return {'title': title, 'summary': summary, 'source_url': final}
