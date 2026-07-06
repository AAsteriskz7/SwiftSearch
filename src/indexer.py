import json
import re


#massive set of common english words. we filter them out so we dont search using them as keywords. 
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

def tokenize(text): 
    text = text.lower()#converts everything to lowercase
    
    words = re.findall(r'[a-z0-9]+', text) #deletes all punctation and sybmols and emojits etc
    
    filtered_words = [word for word in words if word not in STOP_WORDS] #checking against our set above to see if its in it. 
    
    return filtered_words

def build_index(crawled_data):
    inverted_index = {} #empty dict, or database. should populate this with word as key and url as value. 
    
    for url, text in crawled_data.items(): #adding to db
        words = tokenize(text)
        
        for word in words:
            if word not in inverted_index:
                inverted_index[word] = {}
                
            if url not in inverted_index[word]:
                inverted_index[word][url] = 0
                
            inverted_index[word][url] += 1
            
    return inverted_index

def save_index(index, filename="index.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4)

def load_data(filename="crawled_data.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

if __name__ == "__main__":
    print("Loading crawled data...")
    data = load_data()
    
    if not data:
        print("No data found! Please run crawler.py first.")
    else:
        print(f"Loaded {len(data)} pages. Building index...")
        
        index = build_index(data)
        
        save_index(index)
        
        print(f"Index built successfully! Total unique words: {len(index)}")
        
        sample_word = list(index.keys())[0] if index else None
        if sample_word:
            print(f"\nExample - Word '{sample_word}' is found in:")
            for url, count in index[sample_word].items():
                print(f"  - {url} ({count} times)")
