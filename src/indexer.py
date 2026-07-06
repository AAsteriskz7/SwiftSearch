import re
import nltk
from nltk.stem import PorterStemmer
import db

# Massive set of common english words. We filter them out so we don't search using them. 
STOP_WORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", 
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", 
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", 
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", 
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", 
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", 
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", 
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", 
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", 
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", 
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", 
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
])

# Initialize the stemmer
stemmer = PorterStemmer()

def tokenize(text): 
    text = text.lower()
    words = re.findall(r'[a-z0-9]+', text)
    # Filter out stop words and apply Porter Stemmer
    filtered_words = [stemmer.stem(word) for word in words if word not in STOP_WORDS]
    return filtered_words

def build_index():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("Loading documents from SQLite database...")
    cursor.execute("SELECT url, content, word_count FROM documents")
    documents = cursor.fetchall()
    
    if not documents:
        print("No documents found. Run the crawler first.")
        conn.close()
        return
        
    print(f"Loaded {len(documents)} pages. Building inverted index...")
    
    # We will build it in memory first, then batch insert for speed
    inverted_index = {}
    total_length = 0
    
    for row in documents:
        url = row['url']
        content = row['content']
        total_length += row['word_count']
        
        words = tokenize(content)
        
        for word in words:
            if word not in inverted_index:
                inverted_index[word] = {}
            if url not in inverted_index[word]:
                inverted_index[word][url] = 0
            inverted_index[word][url] += 1
            
    # Calculate average document length
    avg_length = total_length / len(documents) if len(documents) > 0 else 0
    
    print("Saving to database...")
    # Clear the old index
    cursor.execute("DELETE FROM inverted_index")
    cursor.execute("DELETE FROM metadata WHERE key IN ('total_docs', 'avgdl')")
    
    # Store metadata for BM25
    cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ('total_docs', str(len(documents))))
    cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ('avgdl', str(avg_length)))
    
    # Batch insert index
    insert_data = []
    for word, url_counts in inverted_index.items():
        for url, freq in url_counts.items():
            insert_data.append((word, url, freq))
            
    cursor.executemany("INSERT INTO inverted_index (word, url, frequency) VALUES (?, ?, ?)", insert_data)
    
    conn.commit()
    conn.close()
    
    print(f"Index built successfully! Total unique stem roots: {len(inverted_index)}")

if __name__ == "__main__":
    db.init_db()
    build_index()
