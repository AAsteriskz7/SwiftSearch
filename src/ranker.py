import math
import db

def calculate_pagerank(damping=0.85, iterations=10):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Load all documents
    cursor.execute("SELECT url FROM documents")
    urls = [row['url'] for row in cursor.fetchall()]
    
    # Load all links
    cursor.execute("SELECT from_url, to_url FROM links")
    links_data = cursor.fetchall()
    
    conn.close()
    
    # Build graph
    graph = {url: [] for url in urls}
    for row in links_data:
        from_u, to_u = row['from_url'], row['to_url']
        if from_u in graph:
            graph[from_u].append(to_u)
            
    # Init pagerank
    pagerank = {url: 1.0 for url in urls}
    
    for _ in range(iterations):
        new_pagerank = {}
        for url in urls:
            rank_sum = 0
            for pointing_url, outbound_links in graph.items():
                if url in outbound_links:
                    rank_sum += pagerank[pointing_url] / len(outbound_links)
                    
            new_pagerank[url] = (1 - damping) + damping * rank_sum
        pagerank = new_pagerank
        
    return pagerank

def tokenize_query(query):
    from indexer import tokenize
    return tokenize(query)

def score_bm25(query, total_docs, avgdl, k1=1.5, b=0.75):
    scores = {}
    query_words = tokenize_query(query)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    for word in query_words:
        # Get the documents containing this word and their term frequency
        cursor.execute('''
            SELECT i.url, i.frequency, d.word_count 
            FROM inverted_index i
            JOIN documents d ON i.url = d.url
            WHERE i.word = ?
        ''', (word,))
        
        results = cursor.fetchall()
        
        doc_count = len(results)
        if doc_count == 0:
            continue
            
        # Standard BM25 IDF formula
        idf = math.log(((total_docs - doc_count + 0.5) / (doc_count + 0.5)) + 1)
        
        for row in results:
            url = row['url']
            tf = row['frequency']
            doc_length = row['word_count']
            
            # BM25 Term Frequency formula
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avgdl))
            
            if url not in scores:
                scores[url] = 0
            scores[url] += idf * (numerator / denominator)
            
    conn.close()
    return scores

def search(query, alpha=0.5):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM metadata WHERE key = 'total_docs'")
    row = cursor.fetchone()
    total_docs = float(row['value']) if row else 0
    
    cursor.execute("SELECT value FROM metadata WHERE key = 'avgdl'")
    row = cursor.fetchone()
    avgdl = float(row['value']) if row else 0
    
    conn.close()
    
    if total_docs == 0:
        return []
        
    bm25_scores = score_bm25(query, total_docs, avgdl)
    pageranks = calculate_pagerank()
    
    final_scores = {}
    
    # Combine scores (only for pages that match the query text)
    for url in bm25_scores:
        content_score = bm25_scores.get(url, 0)
        authority_score = pageranks.get(url, 0)
        
        final_score = (alpha * content_score) + ((1 - alpha) * authority_score)
        final_scores[url] = final_score
        
    ranked_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_results

if __name__ == "__main__":
    query = "example"
    print(f"\nSearching for: '{query}' using BM25 and SQLite...")
    
    results = search(query)
    
    if not results:
        print("No results found.")
    else:
        for rank, (url, score) in enumerate(results, 1):
            print(f"{rank}. {url} (Score: {score:.4f})")
