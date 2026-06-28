# SwiftSearch: Search Engine from Scratch

## Description
A mini search engine featuring a web crawler, an inverted index, and a PageRank-style ranking algorithm.

## Technology Stack
- **Language**: Python
- **Libraries/Frameworks**: BeautifulSoup, Requests, Flask

---

## Current Status
- **Current Phase**: Phase 1: The Web Crawler (Data Collection)

---

## Roadmap

### Phase 1: The Web Crawler (Data Collection)
Your search engine needs data before it can search for anything. The crawler (or spider) will visit web pages, extract the text, find new links, and repeat.

- **Tech**: Python, `requests` library, `BeautifulSoup`.
- **Steps**:
  1. **Seed URLs**: Start with a small list of starting websites (e.g., Wikipedia pages).
  2. **Fetching & Parsing**: Use `requests` to download the HTML. Use `BeautifulSoup` to strip away the HTML tags and extract just the readable text.
  3. **Link Extraction**: Have `BeautifulSoup` find all `<a>` tags to collect outgoing links, adding them to a queue to be crawled next.
  4. **Politeness & Limits**: Implement a limit (e.g., stop after crawling 500 pages) so it doesn't run forever. Add a small `time.sleep()` delay so you don't overwhelm servers.

### Phase 2: The Inverted Index (The Database)
If you search a textbook for a word, you don't read the whole book—you use the index at the back. An inverted index does exactly this: it maps words to the documents that contain them.

- **Tech**: Python dictionaries (or SQLite if you want to store it on disk).
- **Steps**:
  1. **Tokenization**: Split the extracted text from Phase 1 into individual words, convert everything to lowercase, and remove punctuation.
  2. **Filtering**: Remove common "stop words" (like *the*, *and*, *is*, *at*) that don't add search value.
  3. **Building the Map**: Create a dictionary where the key is the word, and the value is a list of URLs (or Document IDs) where that word appears, plus the frequency of the word on that page.

### Phase 3: The Ranking Algorithm (The Brains)
When a user searches for "Python," your index might return 100 pages. How do you decide which one shows up first? You'll combine content relevance with a simplified PageRank.

- **Content Relevance (TF-IDF)**: Calculate Term Frequency (how often the word appears on the page) against Inverse Document Frequency (how rare the word is across all pages).
- **PageRank (Authority)**: Track which pages link to which. A page is considered more "important" if many other pages link to it. You can implement a simplified version of the PageRank formula:
  $$PR(u) = (1-d) + d \sum_{v \in B_u} \frac{PR(v)}{L(v)}$$
  *(Where $PR(u)$ is the PageRank of page $u$, $d$ is a damping factor usually set to 0.85, $B_u$ is the set of pages linking to $u$, and $L(v)$ is the number of outbound links from page $v$.)*
- **Final Score**: Search Score = (Content Relevance Score) + (PageRank Score).

### Phase 4: The Web Interface (Flask)
Finally, you need a way for users to interact with your engine.

- **Tech**: Flask (Python web framework), HTML/CSS.
- **Steps**:
  1. **Backend Route**: Create a simple Flask app with a route that accepts a search query string.
  2. **Processing**: Pass the query to your inverted index, calculate the scores, and sort the URLs from highest to lowest score.
  3. **Frontend Template**: Create a clean, minimalist HTML page with a search bar, and a results page that loops through and displays the ranked URLs and a small snippet of text.
