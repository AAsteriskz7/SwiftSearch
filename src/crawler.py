import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import sqlite3
import db

def fetch_robots_txt(domain):
    robots_url = f"{domain}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except Exception:
        parser.allow_all = True
    return parser

def extract_text(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text(separator=" ")
    return " ".join(text.split())

def extract_links(html_content, base_url):
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    for tag in soup.find_all('a'):
        href = tag.get('href')
        if not href:
            continue
        full_url = urljoin(base_url, href)
        full_url = full_url.split('#')[0].rstrip('/')
        parsed = urlparse(full_url)
        if parsed.scheme in ('http', 'https'):
            links.add(full_url)
    return list(links)

def fetch_page_sync(url):
    headers = {'User-Agent': 'SwiftSearchCrawler/2.0 (Educational Project; avsad)'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'text/html' in content_type:
            return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"
    return None

async def crawl_worker(queue, visited, robots_cache, max_pages):
    db_conn = db.get_connection()
    while True:
        try:
            url = await queue.get()
        except asyncio.QueueEmpty:
            break

        if len(visited) >= max_pages:
            queue.task_done()
            continue

        if url in visited:
            queue.task_done()
            continue
            
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in robots_cache:
            robots_cache[domain] = await asyncio.to_thread(fetch_robots_txt, domain)
            
        if not robots_cache[domain].can_fetch("SwiftSearchCrawler", url):
            print(f"[Robots.txt] Denied access to {url}")
            queue.task_done()
            continue

        visited.add(url)
        print(f"[{len(visited)}/{max_pages}] Crawling: {url}")
        
        html = await asyncio.to_thread(fetch_page_sync, url)
        
        if html and not html.startswith("ERROR:"):
            text = extract_text(html)
            out_links = extract_links(html, url)
            
            # Store in SQLite
            cursor = db_conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO documents (url, content, word_count) VALUES (?, ?, ?)", 
                          (url, text, len(text.split())))
            for link in out_links:
                cursor.execute("INSERT OR IGNORE INTO links (from_url, to_url) VALUES (?, ?)", (url, link))
                if link not in visited:
                    await queue.put(link)
            db_conn.commit()
            print(f"   -> Found {len(out_links)} outbound links.")
        elif html and html.startswith("ERROR:"):
            print(f"[Request Error] Could not connect to {url} - {html}")
            
        queue.task_done()
        await asyncio.sleep(0.5) # Politeness delay
        
    db_conn.close()

async def crawl(seed_urls, max_pages=5, concurrency=5):
    db.init_db()
    queue = asyncio.Queue()
    for url in seed_urls:
        await queue.put(url)
        
    visited = set()
    robots_cache = {}
    
    workers = [
        asyncio.create_task(crawl_worker(queue, visited, robots_cache, max_pages))
        for _ in range(concurrency)
    ]
    
    while len(visited) < max_pages:
        active_tasks = sum(1 for w in workers if not w.done())
        if active_tasks == 0 and queue.empty():
            break
        await asyncio.sleep(1)
        
    for w in workers:
        w.cancel()

if __name__ == "__main__":
    seeds = ["https://example.com", "https://books.toscrape.com/"]
    print("Starting Async SQLite Crawler test (using threads)...")
    asyncio.run(crawl(seeds, max_pages=15, concurrency=3))
    print("\n=== Async Crawl Complete! ===")
    
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM documents")
    doc_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM links")
    link_count = cur.fetchone()[0]
    print(f"Database now contains {doc_count} documents and {link_count} links.")
    conn.close()
