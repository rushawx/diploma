import requests
import streamlit as st

from handlers.transformers import get_data, get_item_embeddings, get_model, transformer_search


BASE_URL = "back:8080"

st.title("Student Projects Recommender System")

menu = ["Welcome Page", "Select Your Project", "View Available Projects", "Signup", "Login", "Profile"]

choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Welcome Page":
    st.subheader("Welcome Page")
    st.text("This is the welcome page of Student Projects Recommender System")
elif choice == "Select Your Project":
    st.subheader("Select Your Project")
    if "username" in st.session_state:
        data = get_data()
        embeddings = get_item_embeddings()
        model = get_model()
        query = st.text_input("Enter approximate project topic")
        st.table(transformer_search(
            data, model, embeddings, query
        ))
elif choice == "View Available Projects":
    st.subheader("View Available Projects")
    st.text("TODO")
elif choice == "Signup":
    st.subheader("Signup")
    nick_name = st.text_input("Login")
    password = st.text_input("Password", type="password")
    if st.button("Signup"):
        if nick_name and password:
            if requests.post(f"http://{BASE_URL}/profile/signup", json={"nick_name": nick_name, "password": password}).status_code == 200:
                st.success("Signup successful")
            else:
                st.error("Signup failed")
        else:
            st.error("Please enter both login and password")
elif choice == "Login":
    st.subheader("Login")
    nick_name = st.text_input("Login")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if nick_name and password:
            if requests.post(f"http://{BASE_URL}/profile/login", json={"nick_name": nick_name, "password": password}).status_code == 200:
                st.success("Login successful")
                st.session_state["username"] = nick_name
            else:
                st.error("Login failed")
        else:
            st.error("Please enter both login and password")
elif choice == "Profile":
    st.subheader("Profile")
    if "username" in st.session_state:
        st.text(f"Username: {st.session_state['username']}")
    else:
        st.error("Failed to fetch profile data")
