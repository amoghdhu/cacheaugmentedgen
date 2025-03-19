import json
import os
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Document:
    def __init__(self, id: str, content: str, topic: str):
        self.id = id
        self.content = content
        self.topic = topic

class DocumentStore:
    def __init__(self, data_path: str = None):
        self.documents: List[Document] = []
        self.vectorizer = TfidfVectorizer()
        self.document_vectors = None
        
        if data_path and os.path.exists(data_path):
            self.load_documents(data_path)
    
    def load_documents(self, data_path: str):
        """Load documents from a JSON file"""
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        for doc_data in data:
            doc = Document(
                id=doc_data.get('id', str(len(self.documents))),
                content=doc_data.get('content', ''),
                topic=doc_data.get('topic', 'general')
            )
            self.documents.append(doc)
        
        # Create document vectors for search
        if self.documents:
            contents = [doc.content for doc in self.documents]
            self.document_vectors = self.vectorizer.fit_transform(contents)
    
    def get_documents(self, topic: str) -> List[Document]:
        """Get all documents for a specific topic"""
        return [doc for doc in self.documents if doc.topic.lower() == topic.lower()]
    
    def get_all_topics(self) -> List[str]:
        """Get a list of all unique topics"""
        return list(set(doc.topic for doc in self.documents))
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """Search for documents relevant to the query"""
        if not self.documents or self.document_vectors is None:
            return []
        
        # Transform query to vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarity
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # Get top-k document indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Return top-k documents
        return [self.documents[i] for i in top_indices] 