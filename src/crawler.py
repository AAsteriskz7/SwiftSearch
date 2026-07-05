import requests
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def fetch_page(url):
    #custom agent to tell servers what its for
    headers = {
        'User-Agent': 'SwiftSearchCrawler/1.0 (Educational Project; avsad)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5) #args: timeout - makes sure bot doesnt freeze 
        response.raise_for_status() #throws error if the page is not found (4xx or 5xx)
        
        content_type = response.headers.get('Content-Type', '') # verify the content we get to make sre its html and not other files. 
        if 'text/html' not in content_type:
            return None
            
        return response.text
        
    except requests.exceptions.Timeout:
        print(f"[Timeout] Request for {url} timed out after 5 seconds.")
    except requests.exceptions.HTTPError as e:
        print(f"[HTTP Error] Status code {response.status_code} for {url} - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[Request Error] Could not connect to {url} - {e}")
        
    return None

def extract_text(html_content):
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "html.parser") #parses html into a tree structure in memeory, easy to naviagate
    
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose() # this is a loop to find all style and script tags and delete them (they contain no relevant content)
        
    text = soup.get_text(separator=" ") #get the rest of the text
    words = text.split()
    cleaned_text = " ".join(words)
    
    return cleaned_text

def extract_links(html_content, base_url):
    if not html_content:
        return []
        
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    
    for tag in soup.find_all('a'): #finds every anchor tag on the page
        href = tag.get('href') #finds all links within each tag 
        if not href:
            continue
            
        full_url = urljoin(base_url, href) # and converts to full urls
        full_url = full_url.split('#')[0]
        full_url = full_url.rstrip('/')
        
        parsed = urlparse(full_url)
        if parsed.scheme in ('http', 'https'): #checks to make sure the urls that we keep are only standard web links and not mailto or javascript links
            links.add(full_url)
            
    return list(links)

def crawl(seed_urls, max_pages=5, delay=1, output_file="crawled_data.json"):
    to_crawl = list(seed_urls) #acts as a queue for bfs, pop from front and add new links to back. 
    #basically bfs
    visited = set()
    crawled_data = {}
    graph = {}
    
    while to_crawl and len(visited) < max_pages:
        url = to_crawl.pop(0)
        
        if url in visited:
            continue
            
        print(f"\n[{len(visited) + 1}/{max_pages}] Crawling: {url}")
        
        html = fetch_page(url)
        visited.add(url)
        
        if html:
            text = extract_text(html)
            crawled_data[url] = text
            
            out_links = extract_links(html, url)
            graph[url] = out_links
            print(f"   Found {len(out_links)} outbound links.")
            
            for link in out_links:
                if link not in visited and link not in to_crawl:
                    to_crawl.append(link)
                    
            time.sleep(delay)
            
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(crawled_data, f, indent=4) #saves our data into a JSON file so we an access in phase 2. 
        
    with open('graph.json', 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=4)
        
    return crawled_data

if __name__ == "__main__":
    seeds = ["https://example.com"]
    print("Starting crawl test...")
    
    results = crawl(seeds, max_pages=2, delay=1.5)
    
    print("\n=== Crawl Complete! ===")
    print(f"Total pages successfully crawled: {len(results)}")
    
    for url, text in results.items():
        print(f"\nURL: {url}")
        print(f"Snippet (first 100 chars): {text[:100]}...")
