import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def fetch_page(url):
    """
    Downloads the HTML content of a URL.
    
    Args:
        url (str): The webpage URL to fetch.
        
    Returns:
        str: The raw HTML text if successful, None otherwise.
    """
    # A custom User-Agent identifying our crawler politely
    headers = {
        'User-Agent': 'SwiftSearchCrawler/1.0 (Educational Project; avsad)'
    }
    
    try:
        # We set a timeout of 5 seconds to prevent hanging indefinitely
        response = requests.get(url, headers=headers, timeout=5)
        
        # raise_for_status() throws an HTTPError if the response code is 4xx or 5xx
        response.raise_for_status()
        
        return response.text
        
    except requests.exceptions.Timeout:
        print(f"[Timeout] Request for {url} timed out after 5 seconds.")
    except requests.exceptions.HTTPError as e:
        print(f"[HTTP Error] Status code {response.status_code} for {url} - {e}")
    except requests.exceptions.RequestException as e:
        print(f"[Request Error] Could not connect to {url} - {e}")
        
    return None

def extract_text(html_content):
    """
    Parses HTML content and extracts clean, readable visible text.
    
    Args:
        html_content (str): The raw HTML string.
        
    Returns:
        str: Cleaned plain text.
    """
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements so their code doesn't get treated as text
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
        
    # Get text
    text = soup.get_text(separator=" ")
    
    # Clean up whitespace: split the text by whitespace and join back with single spaces
    words = text.split()
    cleaned_text = " ".join(words)
    
    return cleaned_text

def extract_links(html_content, base_url):
    """
    Finds all outbound links, resolves relative URLs, strips fragments,
    and filters for HTTP/HTTPS links.
    
    Args:
        html_content (str): The raw HTML string.
        base_url (str): The URL of the page being crawled (used to resolve relative links).
        
    Returns:
        list: A list of unique, normalized URLs found on the page.
    """
    if not html_content:
        return []
        
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    
    for tag in soup.find_all('a'):
        href = tag.get('href')
        if not href:
            continue
            
        # 1. Resolve relative links (e.g., '/about' -> 'https://example.com/about')
        full_url = urljoin(base_url, href)
        
        # 2. Strip URL fragments (e.g., 'https://example.com/page#section' -> 'https://example.com/page')
        full_url = full_url.split('#')[0]
        
        # 3. Clean trailing slashes to normalize URLs
        full_url = full_url.rstrip('/')
        
        # 4. Filter for only http and https links (ignoring mailto:, javascript:, etc.)
        parsed = urlparse(full_url)
        if parsed.scheme in ('http', 'https'):
            links.add(full_url)
            
    return list(links)

def crawl(seed_urls, max_pages=5, delay=1):
    """
    Crawls a web graph starting from seed URLs up to max_pages.
    
    Args:
        seed_urls (list): A list of starting URLs.
        max_pages (int): The maximum number of unique pages to crawl.
        delay (float): Politeness sleep time in seconds between requests.
        
    Returns:
        dict: A dictionary mapping url -> clean_text.
    """
    # Initialize the queue with our starting seed URLs
    to_crawl = list(seed_urls)
    
    # Keep track of pages we have already crawled
    visited = set()
    
    # Store the results: {url: clean_text}
    crawled_data = {}
    
    while to_crawl and len(visited) < max_pages:
        # Pop the first URL in the list (Breadth-First Search)
        url = to_crawl.pop(0)
        
        # Avoid duplicate crawling
        if url in visited:
            continue
            
        print(f"\n[{len(visited) + 1}/{max_pages}] Crawling: {url}")
        
        html = fetch_page(url)
        
        # Mark as visited
        visited.add(url)
        
        if html:
            # 1. Extract text and save it
            text = extract_text(html)
            crawled_data[url] = text
            
            # 2. Find outgoing links
            out_links = extract_links(html, url)
            print(f"   Found {len(out_links)} outbound links.")
            
            # 3. Add undiscovered links to our queue
            for link in out_links:
                if link not in visited and link not in to_crawl:
                    to_crawl.append(link)
                    
            # 4. Politeness sleep so we don't overload servers
            time.sleep(delay)
            
    return crawled_data

if __name__ == "__main__":
    # Let's test our crawling loop starting with example.com
    seeds = ["https://example.com"]
    print("Starting crawl test...")
    
    results = crawl(seeds, max_pages=2, delay=1.5)
    
    print("\n=== Crawl Complete! ===")
    print(f"Total pages successfully crawled: {len(results)}")
    
    for url, text in results.items():
        print(f"\nURL: {url}")
        print(f"Snippet (first 100 chars): {text[:100]}...")
