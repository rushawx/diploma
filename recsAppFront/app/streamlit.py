import streamlit as st
from app.config import Settings
from handlers.auth_helpers import (
    get_user_profile,
    is_authenticated,
    is_token_expired,
    login,
    logout,
    make_authenticated_request,
    signup,
)
from handlers.transformers import (
    get_data,
    get_item_embeddings,
    get_model,
    transformer_search,
)

settings = Settings()

st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
)

st.title(settings.APP_TITLE)

if "model" not in st.session_state:
    with st.spinner("Loading ML model..."):
        st.session_state["model"] = get_model()
    st.success("🚀 Model and data loaded successfully!")

menu = [
    "Welcome Page",
    "Select Your Project",
    "View Available Projects",
    "Signup",
    "Login",
    "Profile",
]

choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Welcome Page":
    st.subheader("Welcome Page")
    st.text("This is the welcome page of Student Projects Recommender System")
elif choice == "Select Your Project":
    st.subheader("Select Your Project")
    if is_authenticated():
        if is_token_expired():
            st.warning("Session expired. Please login again.")
        else:
            data = get_data()
            embeddings = get_item_embeddings()
            model = get_model()
            query = st.text_input("Enter approximate project topic")
            if query:
                st.table(transformer_search(data, model, embeddings, query))
    else:
        st.warning("Please login to access this feature")
elif choice == "View Available Projects":
    st.subheader("View Available Projects")
    if is_authenticated():
        try:
            response = make_authenticated_request("GET", "/projects/")
            if response.status_code == 200:
                projects = response.json()
                st.json(projects)
            else:
                st.error(f"Failed to fetch projects: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please login to access this feature")
elif choice == "Signup":
    st.subheader("Signup")
    nick_name = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Signup"):
        if nick_name and password:
            signup(nick_name, password)
        else:
            st.error("Please enter both username and password")
elif choice == "Login":
    st.subheader("Login")
    nick_name = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if nick_name and password:
            if login(nick_name, password):
                st.success("Login successful!")
                st.rerun()
        else:
            st.error("Please enter both username and password")
elif choice == "Profile":
    st.subheader("Profile")
    if is_authenticated():
        profile = get_user_profile()
        if profile:
            st.json(profile)
    else:
        st.warning("Please login to view your profile")

if is_authenticated() and st.sidebar.button("Logout"):
    logout()
    st.rerun()

if is_authenticated():
    st.sidebar.success(f"Logged in as: {st.session_state.get('username', 'Unknown')}")
