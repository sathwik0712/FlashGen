import os
import json
import time
import google.generativeai as genai
import google.api_core.exceptions
from dotenv import load_dotenv

load_dotenv()

def _get_api_key():
    """Get API key from environment or Streamlit secrets (for cloud deployment)."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    return key

def generate_flashcards(text):
    """
    Calls the Gemini API to generate flashcards from the provided text.
    Uses the most credit-efficient model possible.
    """
    # 1. Configure API
    api_key = _get_api_key()
    if not api_key:
        import streamlit as st
        st.error("GEMINI_API_KEY is not set.")
        return []
    genai.configure(api_key=api_key)

    # 2. CREDIT SAVER: Truncate text to avoid massive token usage
    # Most study material fits in 12,000 chars (~3,000 tokens)
    text = text[:12000]

    prompt = f"""
    You are an expert educational assistant. Generate a JSON list of objects with 'question' and 'answer' keys from this text:
    {text}
    """
    
    try:
        # 3. Use the smallest/cheapest model (Flash Lite)
        model = genai.GenerativeModel('gemini-flash-lite-latest')
        
        response = None
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                break
            except google.api_core.exceptions.ResourceExhausted:
                import streamlit as st
                if attempt < 2:
                    time.sleep(10 * (attempt + 1)) # Wait and retry
                else:
                    st.error("Daily Quota Reached. Try again tomorrow!")
                    return []
        
        if not response or not response.text:
            return []
        
        # Robust JSON extraction
        response_text = response.text.strip()
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            return json.loads(json_str)
            
        return []
    except Exception as e:
        import streamlit as st
        st.error(f"Generation Error: {e}")
        return []
