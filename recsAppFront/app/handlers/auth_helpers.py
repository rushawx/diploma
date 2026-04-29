import requests
import streamlit as st
from datetime import datetime, timedelta
from app.config import Settings

settings = Settings()


def login(nick_name: str, password: str) -> bool:
    """Login user and store JWT token in session state"""
    try:
        response = requests.post(
            f"{settings.BACKEND_BASE_URL}/profile/login",
            json={"nick_name": nick_name, "password": password},
            timeout=settings.BACKEND_TIMEOUT,
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["token_type"] = data["token_type"]
            st.session_state["username"] = nick_name
            st.session_state["login_time"] = datetime.now()
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(settings.CONNECTION_ERROR_MESSAGE.format(str(e)))
        return False


def signup(user_data: dict) -> bool:
    """Signup new user with full profile data"""
    try:
        response = requests.post(
            f"{settings.BACKEND_BASE_URL}/profile/signup",
            json=user_data,
            timeout=settings.BACKEND_TIMEOUT,
        )

        if response.status_code == 200:
            st.success("Signup successful! Please login.")
            return True
        else:
            st.error(f"Signup failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(settings.CONNECTION_ERROR_MESSAGE.format(str(e)))
        return False


def logout():
    """Clear user session"""
    for key in settings.SESSION_STATE_KEYS:
        st.session_state.pop(key, None)
    st.success("Logged out successfully")


def get_auth_headers() -> dict:
    """Get authentication headers for API requests"""
    if "access_token" not in st.session_state:
        return {}

    token_type = st.session_state.get("token_type", "bearer")
    return {
        "Authorization": f"{token_type.capitalize()} {st.session_state['access_token']}"
    }


def is_authenticated() -> bool:
    """Check if user is authenticated with valid token"""
    return "access_token" in st.session_state


def is_token_expired() -> bool:
    """Check if JWT token is expired"""
    if "login_time" not in st.session_state:
        return True

    login_time = st.session_state["login_time"]
    expiration_time = login_time + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    return datetime.now() > expiration_time


def make_authenticated_request(
    method: str, endpoint: str, **kwargs
) -> requests.Response:
    """Make authenticated API request with JWT token"""
    if not is_authenticated():
        raise Exception("User not authenticated")

    if is_token_expired():
        logout()
        st.error(settings.SESSION_EXPIRED_MESSAGE)
        st.stop()

    headers = kwargs.pop("headers", {})
    headers.update(get_auth_headers())

    url = f"{settings.BACKEND_BASE_URL}{endpoint}"

    try:
        response = requests.request(
            method, url, headers=headers, timeout=settings.BACKEND_TIMEOUT, **kwargs
        )

        if response.status_code == 401:
            logout()
            st.error(settings.AUTH_ERROR_MESSAGE)
            st.stop()

        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {str(e)}")
        raise


def get_user_profile() -> dict:
    """Get current user profile"""
    try:
        response = make_authenticated_request("GET", "/profile/me")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(
                f"Failed to get profile: {response.json().get('detail', 'Unknown error')}"
            )
            return {}
    except Exception as e:
        st.error(f"Error fetching profile: {str(e)}")
        return {}
