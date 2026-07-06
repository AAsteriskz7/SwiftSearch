import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'search_engine.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Documents table: Stores crawled pages
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        url TEXT PRIMARY KEY,
        content TEXT,
        word_count INTEGER
    )
    ''')
    
    # Links table: Stores the web graph for PageRank
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS links (
        from_url TEXT,
        to_url TEXT,
        PRIMARY KEY (from_url, to_url)
    )
    ''')
    
    # Inverted Index table: Maps words to documents and stores term frequency
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inverted_index (
        word TEXT,
        url TEXT,
        frequency INTEGER,
        PRIMARY KEY (word, url)
    )
    ''')
    
    # Metadata table: To store global stats like total documents and average doc length for BM25
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    # Create indices for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_index_word ON inverted_index(word)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_url)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
