https://flashgen-38e7xuvtmmqmnfcaq6gjgr.streamlit.app/    
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
