from flask import Flask, render_template, request
from ranker import search
import db

app = Flask(__name__, template_folder='../templates')

@app.route("/")
def home():
    query = request.args.get('q', '')
    results_data = []
    
    if query:
        raw_results = search(query)
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        for url, score in raw_results:
            cursor.execute("SELECT content FROM documents WHERE url = ?", (url,))
            row = cursor.fetchone()
            if row:
                text = row['content']
                snippet = text[:150] + "..." if len(text) > 150 else text
                
                results_data.append({
                    'url': url,
                    'score': round(score, 4),
                    'snippet': snippet
                })
                
        conn.close()
            
    return render_template("index.html", query=query, results=results_data)

if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
