import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from firebase_admin import auth

def get_api_key():
    return os.getenv("FIREBASE_WEB_API_KEY", "")

def signup_user(email, password):
    """
    Creates a new user in Firebase Auth and sends a verification email.
    """
    api_key = get_api_key()
    if not api_key:
        return False, "Firebase Web API Key is missing. Check your .env file."
        
    email = email.strip().lower()
    if not email or not password:
        return False, "Email and password cannot be empty."
        
    # 1. Create the user
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    
    if res.ok:
        data = res.json()
        id_token = data['idToken']
        
        # 2. Send verification email
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        v_payload = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
        v_res = requests.post(verify_url, json=v_payload)
        
        if v_res.ok:
            return True, "Signup successful! A verification link has been sent to your email. You MUST click it before logging in."
        else:
            return True, "Signup successful, but we failed to send the verification email."
    else:
        error_msg = res.json().get('error', {}).get('message', 'Unknown error')
        if "EMAIL_EXISTS" in error_msg:
            return False, "This email is already registered."
        elif "WEAK_PASSWORD" in error_msg:
            return False, "Password should be at least 6 characters."
        return False, f"Signup failed: {error_msg}"

def login_user(email, password):
    """
    Verifies user credentials and ensures their email is verified.
    """
    api_key = get_api_key()
    if not api_key:
        return False, "Firebase Web API Key is missing."
        
    email = email.strip().lower()
    if not email or not password:
        return False, "Email and password cannot be empty."
        
    # 1. Sign in
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    
    if res.ok:
        data = res.json()
        id_token = data['idToken']
        
        # 2. Check email verification status
        lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        l_res = requests.post(lookup_url, json={"idToken": id_token})
        
        if l_res.ok:
            user_info = l_res.json()['users'][0]
            if user_info.get('emailVerified'):
                return True, "Login successful."
            else:
                return False, "Login failed: You have not verified your email address yet. Please check your inbox/spam folder."
        return False, "Could not verify your email status."
    else:
        error_msg = res.json().get('error', {}).get('message', 'Unknown error')
        if "INVALID_LOGIN_CREDENTIALS" in error_msg or "EMAIL_NOT_FOUND" in error_msg or "INVALID_PASSWORD" in error_msg:
            return False, "Invalid email or password."
        return False, f"Login failed: {error_msg}"

# The Google Login function has been removed to avoid auth/unauthorized-domain errors.

def render_auth_ui():
    """
    Renders a premium login/signup UI in Streamlit.
    Returns True if the user is authenticated, False otherwise.
    """
    # Check for login token from Google OAuth redirect
    token = st.query_params.get("token")
    if token:
        try:
            decoded_token = auth.verify_id_token(token)
            st.session_state['authenticated'] = True
            st.session_state['username'] = decoded_token.get('email', 'GoogleUser').split('@')[0]
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Session expired. Please try again.")
            st.query_params.clear()

    if st.session_state.get('authenticated', False):
        return True

    # Premium Auth Page CSS
    st.markdown("""
    <style>
        /* Auth page specific overrides */
        .auth-hero {
            text-align: center;
            padding: 2rem 0 2.5rem 0;
        }
        .auth-logo {
            font-size: 3.5rem;
            margin-bottom: 0.8rem;
            animation: logoFloat 3s ease-in-out infinite;
        }
        @keyframes logoFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
        }
        .auth-title {
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #ffffff 0%, #a78bfa 60%, #7c3aed 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            margin: 0 !important;
            letter-spacing: -0.03em !important;
        }
        .auth-subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-top: 0.6rem;
            font-weight: 400;
        }
        .auth-features {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }
        .auth-feature {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            color: #94a3b8;
            font-weight: 500;
        }
        .auth-feature-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #8b5cf6;
        }
    </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
    <div class="auth-hero">
        <div class="auth-logo">⚡</div>
        <h1 class="auth-title">FlashGen</h1>
        <p class="auth-subtitle">Transform documents into knowledge, effortlessly.</p>
        <div class="auth-features">
            <div class="auth-feature"><div class="auth-feature-dot"></div> AI-Powered</div>
            <div class="auth-feature"><div class="auth-feature-dot"></div> PDF to Cards</div>
            <div class="auth-feature"><div class="auth-feature-dot"></div> Smart Study</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        login_email = st.text_input("Email address", key="login_user", placeholder="you@example.com")
        login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
        st.markdown("<div style='height: 0.3rem'></div>", unsafe_allow_html=True)
        if st.button("Sign In", use_container_width=True, type="primary"):
            if not login_email or not login_password:
                st.warning("Please fill in both fields.")
            else:
                with st.spinner("Authenticating..."):
                    success, msg = login_user(login_email, login_password)
                if success:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = login_email.strip().lower().split('@')[0]
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error(msg)
                
    with tab2:
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        st.caption("Create a free account to start generating flashcards.")
        signup_email = st.text_input("Email address", key="signup_user", placeholder="you@example.com")
        signup_password = st.text_input("Choose a password", type="password", key="signup_pass", placeholder="Min. 6 characters")
        signup_confirm = st.text_input("Confirm password", type="password", key="signup_confirm", placeholder="Re-enter your password")
        st.markdown("<div style='height: 0.3rem'></div>", unsafe_allow_html=True)
        
        if st.button("Create Account", use_container_width=True, type="primary"):
            if not signup_email or not signup_password:
                st.warning("Please fill in all fields.")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Creating your account..."):
                    success, msg = signup_user(signup_email, signup_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                    
    return False

def logout_user():
    """Logs out the current user."""
    for key in ['authenticated', 'username', 'available_sets', 'loaded_set', 'current_flashcards', 'current_set_name']:
        st.session_state.pop(key, None)
    st.rerun()
