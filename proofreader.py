import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from token_manager import TokenManager

# Load environment variables from .env file
load_dotenv()

class Proofreader:
    def __init__(self, api_key=None):
        """Initialize the proofreader with OpenAI API"""
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY", "")

        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=api_key)
        self.token_manager = TokenManager(model_name="gpt-4.1", max_tokens=8192)

    def proofread_text(self, text):
        """Proofread text with automatic chunking for long content"""
        if not text or not text.strip():
            return text

        # Check if text exceeds token limit
        token_count = self.token_manager.count_tokens(text)
        if token_count <= self.token_manager.max_input_tokens:
            return self._proofread_single_chunk(text)

        # Split into chunks if too long
        chunks = self.token_manager.split_text_by_tokens(text)
        corrected_chunks = []

        for chunk in chunks:
            corrected_chunk = self._proofread_single_chunk(chunk)
            corrected_chunks.append(corrected_chunk)

        # Rejoin chunks with appropriate spacing
        return self._rejoin_chunks(corrected_chunks)

    def _proofread_single_chunk(self, text):
        """Proofread a single chunk of text that fits within token limits"""
        try:
            # using gpt-4.1 as requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert proofreader and editor. Your task is to:

1. Correct spelling, grammar, and punctuation errors
2. Improve sentence structure and clarity
3. Ensure consistent style and tone
4. Fix any awkward phrasing
5. Maintain the original meaning and intent
6. Preserve the original formatting and structure

Rules:
- Only make necessary corrections and improvements
- Do not change the fundamental meaning or style unless there are clear errors
- Maintain the same paragraph structure
- If the text is already well-written, make minimal or no changes
- Return only the corrected text, no explanations or comments
- Preserve any intentional formatting like line breaks"""
                    },
                    {
                        "role": "user",
                        "content": f"Please proofread and improve this text:\n\n{text}"
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent corrections
                max_tokens=2000
            )

            corrected_text = response.choices[0].message.content
            if corrected_text:
                corrected_text = corrected_text.strip()

            # Ensure we return something even if the API returns empty
            if not corrected_text:
                return text

            return corrected_text

        except Exception as e:
            # If there's an error with the API call, return the original text
            return text

    def _rejoin_chunks(self, chunks):
        """Rejoin corrected chunks with appropriate spacing"""
        if not chunks:
            return ""

        # Join chunks with a single space, but preserve paragraph structure
        result = ""
        for i, chunk in enumerate(chunks):
            if i == 0:
                result = chunk
            else:
                # Check if we need paragraph separation or just space
                if chunk.startswith(('•', '-', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    result += "\n\n" + chunk
                elif result.endswith('.') or result.endswith('!') or result.endswith('?'):
                    result += " " + chunk
                else:
                    result += " " + chunk

        return result

    def proofread_with_suggestions(self, text):
        """Proofread text and return both corrected version and explanation of changes"""
        if not text or not text.strip():
            return {"corrected": text, "suggestions": []}

        try:
            # using gpt-4.1 as requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert proofreader. Proofread the text and return your response in JSON format with:
- "corrected": the corrected version of the text
- "suggestions": an array of objects with "original", "corrected", and "reason" for each change

Only suggest necessary corrections for grammar, spelling, punctuation, and clarity.
Maintain the original meaning and style. If no changes are needed, return the original text with empty suggestions array."""
                    },
                    {
                        "role": "user",
                        "content": f"Proofread this text: {text}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )

            content = response.choices[0].message.content or ""
            result = json.loads(content) if content else {"corrected": text, "suggestions": []}

            return {
                "corrected": result.get("corrected", text),
                "suggestions": result.get("suggestions", [])
            }

        except Exception as e:
            return {"corrected": text, "suggestions": []}
