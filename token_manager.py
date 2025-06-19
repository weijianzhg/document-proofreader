import tiktoken
from typing import List, Tuple

class TokenManager:
    def __init__(self, model_name="gpt-4.1", max_tokens=8192):
        """Initialize token manager with model-specific limits"""
        self.model_name = model_name
        self.max_tokens = max_tokens
        # Reserve tokens for system message and response
        self.max_input_tokens = max_tokens - 1000  # Reserve 1000 tokens for system message and response
        
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4")  # Use gpt-4 encoding as fallback
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string"""
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def split_text_by_tokens(self, text: str, max_tokens: int | None = None) -> List[str]:
        """Split text into chunks that fit within token limit"""
        if max_tokens is None:
            max_tokens = self.max_input_tokens
        
        if self.count_tokens(text) <= max_tokens:
            return [text]
        
        # Split by sentences first
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            current_tokens = self.count_tokens(current_chunk)
            
            # If single sentence is too long, split it further
            if sentence_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # Split long sentence by words
                word_chunks = self._split_long_sentence(sentence, max_tokens)
                chunks.extend(word_chunks)
            
            # If adding this sentence would exceed limit, start new chunk
            elif current_tokens + sentence_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        # Simple sentence splitting - could be enhanced with more sophisticated NLP
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_long_sentence(self, sentence: str, max_tokens: int) -> List[str]:
        """Split a very long sentence by words"""
        words = sentence.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            test_chunk = current_chunk + " " + word if current_chunk else word
            if self.count_tokens(test_chunk) > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = word
                else:
                    # Single word is too long, just add it anyway
                    chunks.append(word)
                    current_chunk = ""
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def validate_text_length(self, text: str) -> Tuple[bool, str]:
        """Validate if text can be processed within token limits"""
        token_count = self.count_tokens(text)
        
        if token_count <= self.max_input_tokens:
            return True, f"Text has {token_count} tokens (within limit)"
        else:
            return False, f"Text has {token_count} tokens (exceeds limit of {self.max_input_tokens})"
    
    def estimate_processing_chunks(self, text: str) -> int:
        """Estimate how many chunks this text will be split into"""
        return len(self.split_text_by_tokens(text))