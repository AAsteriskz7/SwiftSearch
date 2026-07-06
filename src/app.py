from flask import Flask, render_template, request
import json
from ranker import search

app = Flask(__name__, template_folder='../templates')

try:
    with open("index.json", 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    with open("graph.json", 'r', encoding='utf-8') as f:
        graph = json.load(f)
    with open("crawled_data.json", 'r', encoding='utf-8') as f:
        crawled_data = json.load(f)
except FileNotFoundError:
    inverted_index = {}
    graph = {}
    crawled_data = {}

@app.route("/")
def home():
    query = request.args.get('q', '')
    results_data = []
    
    if query:
        raw_results = search(query, inverted_index, graph)
        
        for url, score in raw_results:
            text = crawled_data.get(url, "")
            snippet = text[:150] + "..." if len(text) > 150 else text
            
            results_data.append({
                'url': url,
                'score': round(score, 4),
                'snippet': snippet
            })
            
    return render_template("index.html", query=query, results=results_data)

if __name__ == "__main__":
    app.run(debug=True)
