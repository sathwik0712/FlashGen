import os
import json
import time
import google.generativeai as genai
import google.api_core.exceptions
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    # 1. Try environment variable (local)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    # 2. Try Streamlit Secrets (cloud)
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except:
        pass
    return None

api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)

def generate_flashcards(text):
    """
    Calls the Gemini API to generate flashcards from the provided text.
    Returns a list of dictionaries with 'question' and 'answer' keys.
    """
    prompt = f"""
    You are an expert educational assistant. Your task is to read the following text extracted from a PDF and generate useful flashcards (Questions and Answers) to help someone study this material.
    
    Please output the flashcards as a JSON list of objects, where each object has a 'question' and an 'answer' key. Do not include any other text or formatting, just the raw JSON array.
    
    Text:
    {text}
    """
    
    try:
        # Using a model name that is confirmed to exist in your environment
        model = genai.GenerativeModel('gemini-flash-latest')
        
        response = None
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                break
            except google.api_core.exceptions.ResourceExhausted:
                import streamlit as st
                if attempt < 2:
                    wait_time = 10 * (attempt + 1)
                    st.warning(f"Rate limit reached. Waiting {wait_time}s to retry...")
                    time.sleep(wait_time)
                else:
                    st.error("Gemini API Quota Exhausted. Please wait a few minutes or check your usage in Google AI Studio.")
                    return []
            except Exception as e:
                import streamlit as st
                st.error(f"API Error: {e}")
                return []
        
        if not response or not response.text:
            print("Gemini returned an empty response.")
            return []
        
        # Robust JSON extraction
        response_text = response.text.strip()
        
        # Try to find the start and end of the JSON array
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            try:
                flashcards = json.loads(json_str)
                return flashcards
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        
        # Fallback to simple stripping if indices not found or failed
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        try:
            flashcards = json.loads(response_text)
            return flashcards
        except Exception as e:
            print(f"Final fallback failed: {e}")
            return []
    except Exception as e:
        import streamlit as st
        st.error(f"Gemini API Error: {e}")
        print(f"Error generating flashcards: {e}")
        return []
