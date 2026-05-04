import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """
    Initializes the Firebase app using the service account JSON.
    """
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
        if not os.path.exists(cred_path):
            print(f"CRITICAL: Firebase credentials file NOT FOUND at {cred_path}")
            return False
            
        try:
            # Basic check to see if it's still a placeholder
            import json
            with open(cred_path, 'r') as f:
                data = json.load(f)
                if data.get("project_id") == "YOUR_PROJECT_ID":
                    print("CRITICAL: firebase_credentials.json still contains PLACEHOLDER values. Please replace them with your actual Firebase service account JSON.")
                    return False
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            if "InvalidData" in str(e):
                print("HINT: This usually means the private_key in your JSON file is malformed or has incorrect characters/line breaks.")
            return False
    return True

import streamlit as st

@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        if not initialize_firebase():
            return None
    try:
        return firestore.client()
    except Exception as e:
         print(f"Firestore client error: {e}")
         return None

def save_flashcards(flashcards, user_id, set_name=None):
    """
    Saves a list of flashcards as a named set document in 'flashcard_sets' for a specific user.
    Each set contains all its cards as an embedded array.
    """
    db = get_db()
    if not db:
        return False

    try:
        from datetime import datetime, timezone
        if not set_name:
            set_name = datetime.now(timezone.utc).strftime("Set %Y-%m-%d %H:%M")

        set_ref = db.collection('flashcard_sets').document()
        set_ref.set({
            'name': set_name,
            'user_id': user_id,
            'card_count': len(flashcards),
            'created_at': firestore.SERVER_TIMESTAMP,
            'cards': [
                {'question': c.get('question'), 'answer': c.get('answer')}
                for c in flashcards
            ]
        })
        return True
    except Exception as e:
        print(f"Error saving flashcard set to Firebase: {e}")
        return False

def get_flashcard_sets(user_id):
    """
    Retrieves metadata (id, name, created_at, card_count) for a specific user's saved sets.
    Returns a list of dicts sorted newest-first.
    """
    db = get_db()
    if not db:
        return []

    try:
        docs = db.collection('flashcard_sets').where(
            'user_id', '==', user_id
        ).stream()
        
        sets = []
        for doc in docs:
            data = doc.to_dict()
            sets.append({
                'id': doc.id,
                'name': data.get('name', 'Unnamed Set'),
                'card_count': data.get('card_count', 0),
                'created_at': data.get('created_at'),
            })
            
        # Sort in Python to avoid needing a Firestore composite index
        sets.sort(key=lambda x: x['created_at'] if x['created_at'] else 0, reverse=True)
        return sets
    except Exception as e:
        print(f"Error retrieving flashcard sets: {e}")
        return []


def get_flashcard_set(set_id):
    """
    Retrieves all cards for a specific set by its Firestore document ID.
    """
    db = get_db()
    if not db:
        return []

    try:
        doc = db.collection('flashcard_sets').document(set_id).get()
        if doc.exists:
            return doc.to_dict().get('cards', [])
        return []
    except Exception as e:
        print(f"Error retrieving flashcard set {set_id}: {e}")
        return []

def delete_flashcard_set(set_id):
    """
    Deletes a specific flashcard set by its Firestore document ID.
    """
    db = get_db()
    if not db:
        return False

    try:
        db.collection('flashcard_sets').document(set_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting flashcard set {set_id}: {e}")
        return False
