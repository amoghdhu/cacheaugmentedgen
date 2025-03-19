import time
from typing import List, Dict, Tuple, Any
from .document_store import DocumentStore, Document

class CacheAugmentedGeneration:
    def __init__(self, llm, document_store, cache_size=100):
        self.llm = llm
        self.document_store = document_store
        self.cache = {}  
        self.cache_size = cache_size
        self.cache_hits = 0
        self.total_queries = 0
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_response_time_with_cache': 0,
            'avg_response_time_without_cache': 0,
            'total_response_time_with_cache': 0,
            'total_response_time_without_cache': 0,
            'queries_with_cache': 0,
            'queries_without_cache': 0
        }
        
    def preload_cache(self, topics=None):
        if topics is None:
            topics = self.document_store.get_all_topics()
            
        for topic in topics:
            docs = self.document_store.get_documents(topic)
            if docs:
                self.cache[topic] = self._process_documents(docs)
                
        return list(self.cache.keys())
            
    def _process_documents(self, docs: List[Document]) -> str:
        return "\n\n---\n\n".join([doc.content for doc in docs])
    
    def predict_relevant_topics(self, user_query: str) -> List[str]:
        relevant_topics = []
        for topic in self.cache.keys():
            if any(keyword in user_query.lower() for keyword in topic.lower().split()):
                relevant_topics.append(topic)
        return relevant_topics
    
    def answer_query(self, user_query: str, use_cache: bool = True) -> Dict[str, Any]:
        self.total_queries += 1
        start_time = time.time()
        
        result = {
            'query': user_query,
            'response': '',
            'used_cache': False,
            'topics_used': [],
            'response_time': 0,
        }
        
        if use_cache:
            relevant_topics = self.predict_relevant_topics(user_query)
            if relevant_topics:
                context = "\n\n".join([self.cache[topic] for topic in relevant_topics])
                
                response = self.llm.generate(context + "\n\nQuestion: " + user_query)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                self.metrics['cache_hits'] += 1
                self.metrics['total_response_time_with_cache'] += response_time
                self.metrics['queries_with_cache'] += 1
                self.metrics['avg_response_time_with_cache'] = (
                    self.metrics['total_response_time_with_cache'] / 
                    self.metrics['queries_with_cache']
                )
                
                result.update({
                    'response': response,
                    'used_cache': True,
                    'topics_used': relevant_topics,
                    'response_time': response_time,
                })
                return result
        
        docs = self.document_store.search(user_query)
        context = self._process_documents(docs)
        response = self.llm.generate(context + "\n\nQuestion: " + user_query)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.metrics['cache_misses'] += 1
        self.metrics['total_response_time_without_cache'] += response_time
        self.metrics['queries_without_cache'] += 1
        self.metrics['avg_response_time_without_cache'] = (
            self.metrics['total_response_time_without_cache'] / 
            self.metrics['queries_without_cache']
        )
        
        result.update({
            'response': response,
            'used_cache': False,
            'topics_used': [],
            'response_time': response_time,
        })
        return result
    
    def get_metrics(self):
        """Get current performance metrics"""
        return self.metrics 