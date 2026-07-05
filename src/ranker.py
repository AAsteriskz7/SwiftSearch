import json
import math

def calculate_pagerank(graph, damping=0.85, iterations=10):
    pagerank = {}
    
    for url in graph:
        pagerank[url] = 1.0
        
    for _ in range(iterations):
        new_pagerank = {}
        for url in graph:
            rank_sum = 0
            for pointing_url, outbound_links in graph.items():
                if url in outbound_links:
                    rank_sum += pagerank[pointing_url] / len(outbound_links)
                    
            new_pagerank[url] = (1 - damping) + damping * rank_sum
            
        pagerank = new_pagerank
        
    return pagerank

def tokenize_query(query):
    query = query.lower()
    
    from indexer import STOP_WORDS, tokenize
    return tokenize(query)

def score_tf_idf(query, inverted_index, total_docs):
    scores = {}
    query_words = tokenize_query(query)
    
    for word in query_words:
        if word not in inverted_index:
            continue
            
        document_frequencies = inverted_index[word]
        doc_count = len(document_frequencies)
        
        idf = math.log(total_docs / (1 + doc_count))
        
        for url, tf in document_frequencies.items():
            if url not in scores:
                scores[url] = 0
                
            scores[url] += tf * idf
            
    return scores

def search(query, inverted_index, graph, alpha=0.5):
    total_docs = len(graph)
    
    tf_idf_scores = score_tf_idf(query, inverted_index, total_docs)
    
    pageranks = calculate_pagerank(graph)
    
    final_scores = {}
    
    for url in tf_idf_scores:
        content_score = tf_idf_scores.get(url, 0)
        authority_score = pageranks.get(url, 0)
        
        final_score = (alpha * content_score) + ((1 - alpha) * authority_score)
        final_scores[url] = final_score
        
    ranked_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_results

if __name__ == "__main__":
    try:
        with open("index.json", 'r', encoding='utf-8') as f:
            index = json.load(f)
        with open("graph.json", 'r', encoding='utf-8') as f:
            graph = json.load(f)
            
        print("Data loaded successfully!")
        
        query = "example domain"
        print(f"\nSearching for: '{query}'")
        
        results = search(query, index, graph)
        
        for rank, (url, score) in enumerate(results, 1):
            print(f"{rank}. {url} (Score: {score:.4f})")
            
    except FileNotFoundError:
        print("Required files not found. Run crawler.py then indexer.py first!")
