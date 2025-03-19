# Cache Augmented Generation (CAG) Demo

This project demonstrates Cache Augmented Generation (CAG), a technique that improves on Retrieval Augmented Generation (RAG) by preloading relevant knowledge into a language model's context.

## How It Works

1. **Document Store**: Manages a collection of documents organized by topics
2. **Cache System**: Preloads documents for frequently accessed topics
3. **Query Processing**:
   - When a query is received, the system tries to find relevant cached topics
   - If found, it uses the cached information to generate a response
   - If not, it falls back to traditional RAG by retrieving documents on-demand

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install flask scikit-learn numpy groq
   ```
3. Set your Groq API key:
   ```
   export GROQ_API_KEY=your_groq_api_key_here
   ```
   
   Or create a `.env` file with:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

Run the application:
```
python app.py
```

Then open your browser and navigate to `http://127.0.0.1:5000`


