import os
import time
from groq import Groq

class GroqLLM:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    for line in f:
                        if line.startswith("GROQ_API_KEY="):
                            self.api_key = line.strip().split("=")[1].strip('"')
                            break
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or .env file")
            
        self.model_name = model_name
        self.client = Groq(api_key=self.api_key)
        print(f"Initialized Groq client with model: {model_name}")
    
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        start_time = time.time()
        
        if "Question:" in prompt:
            question = prompt.split("Question:")[-1].strip()
            context = prompt.split("Question:")[0].strip()
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant that provides accurate information based on the context provided."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that provides accurate information."},
                {"role": "user", "content": prompt}
            ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.5,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            
            result = response.choices[0].message.content
            
            end_time = time.time()
            print(f"Generation took {end_time - start_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}" 