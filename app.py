from flask import Flask, render_template, request, jsonify
import os
import json
from cag.document_store import DocumentStore
from cag.groq_llm import GroqLLM
from cag.cag_system import CacheAugmentedGeneration

app = Flask(__name__)

# Initialize components
data_path = os.path.join('data', 'documents.json')

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists(data_path):
    sample_data = [
        {
            "id": "1",
            "topic": "python",
            "content": "Python is a high-level, interpreted programming language known for its readability and versatility. It supports multiple programming paradigms including procedural, object-oriented, and functional programming."
        },
        {
            "id": "2",
            "topic": "python",
            "content": "Python has a comprehensive standard library and a large ecosystem of third-party packages. Popular libraries include NumPy for numerical computing, Pandas for data analysis, and TensorFlow for machine learning."
        },
        {
            "id": "3",
            "topic": "javascript",
            "content": "JavaScript is a scripting language primarily used for creating interactive web pages. It's an essential part of web applications and runs in the browser environment."
        },
        {
            "id": "4",
            "topic": "javascript",
            "content": "Modern JavaScript includes features like arrow functions, destructuring, and async/await. Popular frameworks include React, Vue, and Angular."
        },
        {
            "id": "5",
            "topic": "machine learning",
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data and improve from experience without being explicitly programmed."
        },
        {
            "id": "6",
            "topic": "machine learning",
            "content": "Common machine learning algorithms include linear regression, decision trees, neural networks, and clustering algorithms. The field is divided into supervised, unsupervised, and reinforcement learning."
        },
        {
            "id": "7",
            "topic": "databases",
            "content": "Databases are organized collections of data stored and accessed electronically. SQL databases like MySQL and PostgreSQL use structured query language for managing data."
        },
        {
            "id": "8",
            "topic": "databases",
            "content": "NoSQL databases like MongoDB and Redis provide flexible schemas and are often used for large-scale, distributed data storage needs."
        },
        {
            "id": "9",
            "topic": "cache augmented generation",
            "content": "Cache Augmented Generation (CAG) is a technique that improves on Retrieval Augmented Generation (RAG) by preloading relevant knowledge into a language model's context before the user asks a question."
        },
        {
            "id": "10",
            "topic": "cache augmented generation",
            "content": "CAG addresses latency issues in RAG by eliminating real-time document retrieval for common queries, resulting in faster response times and better user experience."
        }
    ]
    with open(data_path, 'w') as f:
        json.dump(sample_data, f)

document_store = DocumentStore(data_path)

# Initialize Groq LLM
print("Using Llama 3.3 via Groq API")
llm = GroqLLM()

cag_system = CacheAugmentedGeneration(llm, document_store)

# Preload cache
cached_topics = cag_system.preload_cache()

@app.route('/')
def index():
    topics = document_store.get_all_topics()
    return render_template('index.html', topics=topics, cached_topics=cached_topics)

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    query_text = data.get('query', '')
    use_cache = data.get('use_cache', True)
    
    result = cag_system.answer_query(query_text, use_cache=use_cache)
    metrics = cag_system.get_metrics()
    
    return jsonify({
        'result': result,
        'metrics': metrics
    })

@app.route('/api/metrics')
def metrics():
    return jsonify(cag_system.get_metrics())

if __name__ == '__main__':
    app.run(debug=True) 