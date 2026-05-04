# FlashGen

## Overview
FlashGen is a full‑stack web app built with **Streamlit** (frontend) and **Python** (backend). It converts an uploaded PDF into study flashcards using the Gemini AI model and stores them in **Firebase Firestore**.

## Project Structure
```
FlashGen/
├─ app.py                # Streamlit UI
├─ pdf_processor.py      # Extracts text from PDFs
├─ flashcard_generator.py # Calls Gemini to create flashcards
├─ firebase_client.py    # Firestore read/write helpers
├─ .env                  # Environment variables (GEMINI_API_KEY, FIREBASE_CREDENTIALS_PATH)
├─ requirements.txt      # Python dependencies
├─ .gitignore            # Ignored files
└─ firebase_credentials.json  # Service account JSON (add your credentials here)
```

## Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Add your credentials**
   - Edit `.env` and ensure `GEMINI_API_KEY` is set (already added).
   - Paste the Firebase service‑account JSON into `firebase_credentials.json`.
   - The path to the JSON is referenced by `FIREBASE_CREDENTIALS_PATH` in `.env` (default `firebase_credentials.json`).

3. **Run the app**
   ```bash
   streamlit run app.py
   ```
   Open the provided localhost URL in your browser.

## Usage
- Upload a PDF file on the main page.
- Click **Generate Flashcards** – the app extracts text, sends it to Gemini, and displays a list of Q/A pairs.
- Optionally **Save Flashcards to Database** to store them in Firestore.
- Use the sidebar to **Load Saved Flashcards** from the global collection.

## Notes
- The app currently uses a **single global Flashcards collection** – all users share the same cards.
- No authentication is configured (can be added later).
- Ensure your Google Cloud project has Firestore in **Native mode**.

## License
MIT – feel free to modify and extend!
