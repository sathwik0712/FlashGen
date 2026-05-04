import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
        response = model.generate_content(prompt)
        
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
        print(f"Error generating flashcards: {e}")
        return []
