import streamlit as st
import traceback
from pdf_processor import extract_text_from_pdf
from flashcard_generator import generate_flashcards
from firebase_client import save_flashcards, get_flashcard_sets, get_flashcard_set, delete_flashcard_set
from auth import render_auth_ui, logout_user

st.set_page_config(page_title="FlashGen", page_icon="⚡", layout="wide")

def inject_premium_css():
    """Injects the complete premium design system CSS."""
    st.markdown("""
    <style>
        /* ═══════════════════════════════════════════════════════════════════
           FLASHGEN PREMIUM DESIGN SYSTEM v2.0
           A refined, luxurious dark-mode experience
        ═══════════════════════════════════════════════════════════════════ */

        /* ── Typography ─────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"], .stMarkdown, .stText, p, h1, h2, h3, h4, span, label, div {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ── Page Background & Layout ───────────────────────────────────── */
        .stApp {
            background: linear-gradient(160deg, #0a0a0f 0%, #0d1117 40%, #101820 100%) !important;
        }

        .block-container {
            max-width: 900px !important;
            padding: 2rem 2.5rem 4rem 2.5rem !important;
            animation: pageReveal 0.6s cubic-bezier(0.22, 1, 0.36, 1);
        }

        @keyframes pageReveal {
            0% { opacity: 0; transform: translateY(12px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        /* ── Sidebar Premium ────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0c0c14 0%, #111119 100%) !important;
            border-right: 1px solid rgba(139, 92, 246, 0.08) !important;
        }

        [data-testid="stSidebar"] .block-container {
            padding: 1.5rem 1rem !important;
        }

        /* ── Headings ───────────────────────────────────────────────────── */
        h1 {
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
            background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #7c3aed 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            font-size: 2.4rem !important;
            line-height: 1.2 !important;
            padding-bottom: 0.3rem !important;
        }

        h2, h3 {
            font-weight: 700 !important;
            color: #e2e8f0 !important;
            letter-spacing: -0.02em !important;
        }

        /* ── Buttons ────────────────────────────────────────────────────── */
        div[data-testid="stButton"] button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.6rem 1.5rem !important;
            letter-spacing: 0.01em !important;
            transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1) !important;
            border: 1px solid rgba(139, 92, 246, 0.2) !important;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%) !important;
            color: #e2e8f0 !important;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.08) !important;
        }

        div[data-testid="stButton"] button:hover {
            transform: translateY(-2px) !important;
            border-color: rgba(139, 92, 246, 0.5) !important;
            box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2), 0 0 0 1px rgba(139, 92, 246, 0.1) !important;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%) !important;
        }

        div[data-testid="stButton"] button:active {
            transform: translateY(0px) scale(0.98) !important;
        }

        /* Primary button override */
        div[data-testid="stButton"] button[kind="primary"],
        div[data-testid="stButton"] button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #8b5cf6 100%) !important;
            border: none !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover,
        div[data-testid="stButton"] button[data-testid="stBaseButton-primary"]:hover {
            box-shadow: 0 8px 30px rgba(124, 58, 237, 0.5), 0 0 60px rgba(124, 58, 237, 0.15) !important;
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6366f1 100%) !important;
        }

        /* ── Input Fields ───────────────────────────────────────────────── */
        div[data-testid="stTextInput"] input,
        .stSelectbox > div > div {
            background: rgba(15, 15, 25, 0.8) !important;
            border: 1px solid rgba(139, 92, 246, 0.15) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            padding: 0.7rem 1rem !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: rgba(139, 92, 246, 0.6) !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1), 0 4px 12px rgba(139, 92, 246, 0.1) !important;
        }

        /* ── File Uploader ──────────────────────────────────────────────── */
        [data-testid="stFileUploader"] {
            background: rgba(15, 15, 25, 0.5) !important;
            border: 2px dashed rgba(139, 92, 246, 0.25) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: rgba(139, 92, 246, 0.5) !important;
            background: rgba(139, 92, 246, 0.03) !important;
        }

        /* ── Progress Bar ───────────────────────────────────────────────── */
        .stProgress > div > div {
            background: linear-gradient(90deg, #7c3aed, #6366f1, #8b5cf6) !important;
            border-radius: 10px !important;
        }

        .stProgress > div {
            background: rgba(139, 92, 246, 0.1) !important;
            border-radius: 10px !important;
        }

        /* ── Tabs ───────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0 !important;
            background: rgba(15, 15, 25, 0.6) !important;
            border-radius: 14px !important;
            padding: 4px !important;
            border: 1px solid rgba(139, 92, 246, 0.1) !important;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            transition: all 0.2s ease !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.15)) !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
        }

        /* ── Alerts & Messages ──────────────────────────────────────────── */
        .stAlert, div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: none !important;
            backdrop-filter: blur(10px) !important;
        }

        /* ── Data Editor ────────────────────────────────────────────────── */
        [data-testid="stDataFrame"], .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid rgba(139, 92, 246, 0.1) !important;
        }

        /* ── Dividers ───────────────────────────────────────────────────── */
        hr {
            border-color: rgba(139, 92, 246, 0.1) !important;
            margin: 1.5rem 0 !important;
        }

        /* ── Spinner ────────────────────────────────────────────────────── */
        .stSpinner > div {
            border-top-color: #8b5cf6 !important;
        }

        /* ── Scrollbar ──────────────────────────────────────────────────── */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(139, 92, 246, 0.3);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(139, 92, 246, 0.5);
        }

        /* ── Custom Component Classes ───────────────────────────────────── */
        .premium-card {
            background: linear-gradient(145deg, rgba(20, 20, 35, 0.9), rgba(25, 25, 40, 0.8));
            border: 1px solid rgba(139, 92, 246, 0.12);
            border-radius: 20px;
            padding: 2.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.03);
            transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
            animation: cardSlideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1);
        }

        .premium-card:hover {
            transform: translateY(-4px);
            border-color: rgba(139, 92, 246, 0.3);
            box-shadow: 0 20px 50px rgba(124, 58, 237, 0.15), 0 8px 32px rgba(0, 0, 0, 0.4);
        }

        @keyframes cardSlideUp {
            0% { opacity: 0; transform: translateY(20px) scale(0.97); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        .flashcard-question {
            background: linear-gradient(145deg, rgba(20, 20, 35, 0.95), rgba(30, 25, 50, 0.9));
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 20px;
            padding: 3rem 2.5rem;
            text-align: center;
            margin: 1.5rem 0;
            box-shadow: 0 10px 40px rgba(124, 58, 237, 0.1), 0 4px 16px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            animation: cardSlideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1);
        }

        .flashcard-question::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #7c3aed, #6366f1, #8b5cf6, #a78bfa);
            border-radius: 20px 20px 0 0;
        }

        .flashcard-answer {
            background: linear-gradient(145deg, rgba(16, 30, 25, 0.95), rgba(20, 40, 35, 0.9));
            border: 1px solid rgba(52, 211, 153, 0.2);
            border-radius: 20px;
            padding: 3rem 2.5rem;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 10px 40px rgba(52, 211, 153, 0.08), 0 4px 16px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
            animation: answerReveal 0.6s cubic-bezier(0.22, 1, 0.36, 1);
        }

        .flashcard-answer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #10b981, #34d399, #6ee7b7);
            border-radius: 20px 20px 0 0;
        }

        @keyframes answerReveal {
            0% { opacity: 0; transform: perspective(800px) rotateX(-15deg) translateY(10px); }
            100% { opacity: 1; transform: perspective(800px) rotateX(0deg) translateY(0); }
        }

        .stat-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 20px;
            padding: 0.35rem 0.9rem;
            font-size: 0.8rem;
            font-weight: 600;
            color: #a78bfa;
        }

        .welcome-subtitle {
            color: #94a3b8;
            font-size: 1.05rem;
            font-weight: 400;
            line-height: 1.6;
            margin-top: -0.5rem;
        }

        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #8b5cf6;
            margin-bottom: 0.8rem;
        }

        .quiz-header {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(99, 102, 241, 0.04));
            border: 1px solid rgba(139, 92, 246, 0.12);
            border-radius: 16px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            color: #64748b;
        }

        .empty-state-icon {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            opacity: 0.6;
        }

        .sidebar-card {
            background: rgba(139, 92, 246, 0.05);
            border: 1px solid rgba(139, 92, 246, 0.1);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)


def main():
    inject_premium_css()

    # Show auth UI if not authenticated
    if not render_auth_ui():
        return
        
    username = st.session_state['username']
    
    # ── Premium Header ──────────────────────────────────────────────────────────
    st.markdown("# ⚡ FlashGen")
    st.markdown(f'<p class="welcome-subtitle">Welcome back, <strong>{username}</strong>. Transform any PDF into intelligent study cards powered by AI.</p>', unsafe_allow_html=True)

    # ── Sidebar: User Profile & Saved Sets ──────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
            <div style="width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #7c3aed, #6366f1); display: inline-flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 700; color: white; margin-bottom: 0.8rem; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);">
                {username[0].upper()}
            </div>
            <div style="font-weight: 700; font-size: 1.1rem; color: #e2e8f0;">{username}</div>
            <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">Active Learner</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Sign Out", use_container_width=True):
            logout_user()
            
        st.markdown("---")
        st.markdown('<p class="section-label">Your Library</p>', unsafe_allow_html=True)

        if st.button("🔄 Refresh Library", use_container_width=True):
            try:
                with st.spinner("Loading your sets..."):
                    sets = get_flashcard_sets(username)
                if sets:
                    st.session_state['available_sets'] = sets
                    st.success(f"Found {len(sets)} set{'s' if len(sets) != 1 else ''}.")
                else:
                    st.info("No saved sets yet. Create your first one!")
                    st.session_state.pop('available_sets', None)
                    st.session_state.pop('loaded_set', None)
            except Exception as e:
                st.error(f"Error: {e}")

        # Show dropdown once sets are fetched
        if 'available_sets' in st.session_state and st.session_state['available_sets']:
            sets = st.session_state['available_sets']
            
            options = {}
            labels = []
            for i, s in enumerate(sets):
                label = f"{s['name']}  ({s['card_count']} cards)"
                options[label] = s
                labels.append(label)
            
            selected_label = st.selectbox(
                "Select a set:",
                labels,
                key="set_selector",
                label_visibility="collapsed"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📖 Study", use_container_width=True, type="primary"):
                    if selected_label and selected_label in options:
                        chosen = options[selected_label]
                        try:
                            with st.spinner("Loading..."):
                                cards = get_flashcard_set(chosen['id'])
                            if cards:
                                st.session_state['loaded_set'] = {
                                    'name': chosen['name'],
                                    'cards': cards
                                }
                                st.session_state['quiz_index'] = 0
                                st.session_state['show_answer'] = False
                            else:
                                st.warning("Could not load cards.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
            with col2:
                if st.button("🗑️ Delete", use_container_width=True):
                    if selected_label and selected_label in options:
                        chosen = options[selected_label]
                        try:
                            with st.spinner("Deleting..."):
                                success = delete_flashcard_set(chosen['id'])
                            if success:
                                st.success(f"Deleted!")
                                st.session_state.pop('available_sets', None)
                                if st.session_state.get('loaded_set', {}).get('name') == chosen['name']:
                                    st.session_state.pop('loaded_set', None)
                                st.rerun()
                            else:
                                st.error("Failed to delete.")
                        except Exception as e:
                            st.error(f"Error: {e}")

        # Currently studying indicator
        if 'loaded_set' in st.session_state:
            st.markdown("---")
            st.markdown(f"""
            <div class="sidebar-card">
                <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #8b5cf6; margin-bottom: 0.4rem;">Now Studying</div>
                <div style="font-weight: 600; color: #e2e8f0; font-size: 0.95rem;">{st.session_state['loaded_set']['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("✕ Close Study Session", use_container_width=True):
                st.session_state.pop('loaded_set', None)
                st.session_state.pop('quiz_index', None)
                st.session_state.pop('show_answer', None)
                st.rerun()

    # ── Main Content Area ───────────────────────────────────────────────────────
    if 'loaded_set' in st.session_state:
        # ═══════════════════════════════════════════════════════════════════
        # QUIZ MODE - Premium Study Experience
        # ═══════════════════════════════════════════════════════════════════
        loaded = st.session_state['loaded_set']
        cards = loaded.get('cards', [])
        idx = st.session_state.get('quiz_index', 0)
        
        # Quiz header with progress info
        st.markdown(f"""
        <div class="quiz-header">
            <div>
                <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #8b5cf6;">Study Session</div>
                <div style="font-weight: 700; font-size: 1.2rem; color: #e2e8f0; margin-top: 2px;">{loaded['name']}</div>
            </div>
            <div class="stat-badge">
                <span>📚</span> {len(cards)} cards
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if idx < len(cards):
            st.progress((idx) / len(cards), text=f"Card {idx + 1} of {len(cards)}")
            
            card = cards[idx]
            
            # Question Card
            st.markdown(f"""
            <div class="flashcard-question">
                <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #8b5cf6; margin-bottom: 1.2rem;">Question</div>
                <h3 style="color: #f1f5f9; margin: 0; font-weight: 700; font-size: 1.4rem; line-height: 1.5;">
                    {card.get('question', 'No Question')}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.get('show_answer', False):
                st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
                if st.button("Reveal Answer →", use_container_width=True, type="primary"):
                    st.session_state['show_answer'] = True
                    st.rerun()
            else:
                # Answer Card
                st.markdown(f"""
                <div class="flashcard-answer">
                    <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #34d399; margin-bottom: 1.2rem;">Answer</div>
                    <h4 style="color: #d1fae5; margin: 0; font-weight: 600; font-size: 1.2rem; line-height: 1.6;">
                        {card.get('answer', 'No Answer')}
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem; margin: 1rem 0 0.5rem 0;'>How confident were you?</p>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                def next_card():
                    st.session_state['quiz_index'] += 1
                    st.session_state['show_answer'] = False
                    
                with col1:
                    if st.button("😞 Forgot", use_container_width=True):
                        next_card()
                        st.rerun()
                with col2:
                    if st.button("🤔 Hard", use_container_width=True):
                        next_card()
                        st.rerun()
                with col3:
                    if st.button("✨ Easy", use_container_width=True, type="primary"):
                        next_card()
                        st.rerun()
        else:
            # Completion state
            st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
                <h2 style="margin: 0 0 0.5rem 0; font-size: 1.6rem;">Session Complete!</h2>
                <p style="color: #94a3b8; font-size: 1rem;">You've reviewed all the cards in this set. Great work!</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Restart Session", use_container_width=True, type="primary"):
                st.session_state['quiz_index'] = 0
                st.session_state['show_answer'] = False
                st.rerun()
                
    else:
        # ═══════════════════════════════════════════════════════════════════
        # GENERATOR MODE - Premium Upload & Create Experience
        # ═══════════════════════════════════════════════════════════════════
        
        # Empty state / Upload section
        if 'current_flashcards' not in st.session_state:
            st.markdown("""
            <div class="premium-card" style="text-align: center; padding: 3rem 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
                <h3 style="margin: 0 0 0.5rem 0; font-size: 1.3rem; color: #e2e8f0;">Upload a PDF to get started</h3>
                <p style="color: #64748b; font-size: 0.9rem; max-width: 400px; margin: 0 auto;">
                    Our AI will analyze your document and generate smart flashcards for effective studying.
                </p>
            </div>
            """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drop your PDF here or click to browse",
            type="pdf",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            st.markdown(f"""
            <div class="sidebar-card" style="display: flex; align-items: center; gap: 0.8rem;">
                <span style="font-size: 1.5rem;">📎</span>
                <div>
                    <div style="font-weight: 600; color: #e2e8f0; font-size: 0.9rem;">{uploaded_file.name}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{round(uploaded_file.size / 1024, 1)} KB</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)

            if st.button("⚡ Generate Flashcards", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Extracting text from PDF..."):
                        text = extract_text_from_pdf(uploaded_file)

                    if not text:
                        st.error("Could not extract text from this PDF. Try another file.")
                    else:
                        st.info(f"Extracted {len(text):,} characters. Generating flashcards...")

                        with st.spinner("AI is crafting your flashcards..."):
                            flashcards = generate_flashcards(text)

                        if flashcards:
                            st.success(f"Generated {len(flashcards)} flashcards!")
                            pdf_name = uploaded_file.name.rsplit('.', 1)[0]
                            st.session_state['current_flashcards'] = flashcards
                            st.session_state['current_set_name'] = pdf_name
                        else:
                            st.error("Generation failed. Check your API key and try again.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Display generated flashcards with premium editor
        if 'current_flashcards' in st.session_state:
            flashcards = st.session_state['current_flashcards']
            set_name = st.session_state.get('current_set_name', 'My Flashcards')

            st.markdown("---")
            st.markdown('<p class="section-label">Edit & Refine</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.2rem;">Your Flashcards</h3>
                <div class="stat-badge"><span>📝</span> {len(flashcards)} cards</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("Double-click any cell to edit. Add or remove rows as needed.")
            
            edited_flashcards = st.data_editor(
                flashcards,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "question": st.column_config.TextColumn("Question", width="medium", required=True),
                    "answer": st.column_config.TextColumn("Answer", width="large", required=True)
                },
                key="flashcard_editor"
            )
            
            st.session_state['current_flashcards'] = edited_flashcards

            st.markdown("---")
            st.markdown('<p class="section-label">Save to Library</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                custom_name = st.text_input(
                    "Set name:",
                    value=set_name,
                    key="save_name",
                    placeholder="Give your set a memorable name..."
                )
            with col2:
                st.write("")
                st.write("")
                if st.button("💾 Save", use_container_width=True, type="primary"):
                    try:
                        with st.spinner("Saving..."):
                            save_name = custom_name if custom_name else set_name
                            success = save_flashcards(flashcards, user_id=username, set_name=save_name)
                        if success:
                            st.success(f"Saved as **{save_name}**!")
                            st.session_state.pop('available_sets', None)
                            
                            if st.button("→ Study Now", use_container_width=True):
                                st.session_state['loaded_set'] = {'name': save_name, 'cards': flashcards}
                                st.session_state['quiz_index'] = 0
                                st.session_state['show_answer'] = False
                                st.rerun()
                        else:
                            st.error("Save failed. Check your Firebase credentials.")
                    except Exception as e:
                        st.error(f"Error: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("An unexpected error occurred:")
        st.code(traceback.format_exc())
