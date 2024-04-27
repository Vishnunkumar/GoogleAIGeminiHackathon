import streamlit as st
import google.generativeai as genai
from github import Github
from github import Auth

st.title("Code Buddy")
st.markdown("*A streamlit app leveraging Google Gemini API in the backend to help"
            " get through the hard hustles of coding*")

st.subheader("Commit Message Classifier", divider="green")

gemini_api_key = st.text_input("Gemini API Key", type="password")
github_token = st.text_input("Gitlab Access Token", type="password")

init_button = st.button("Save session")

if __name__ == "__main__":

    if init_button:
        with st.spinner("Gemini Session Creation"):
            st.session_state.gemini_api_key = gemini_api_key
            st.session_state.github_token = github_token
        st.success("Session Creation Complete, Please head over to the other pages to try out the different features")

