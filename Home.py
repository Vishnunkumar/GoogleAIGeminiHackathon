import streamlit as st
import google.generativeai as genai
from github import Github
from github import Auth

st.title("Code Buddy")
st.markdown("*A streamlit app leveraging Google Gemini API in the backend to help"
            " get through the hard hustles of coding*")

st.subheader("Commit Message Classifier", divider="green")

gemini_api_key = st.text_input("Gemini API Key", type="password")
github_repo = st.text_input("Github Repo")
github_token = st.text_input("Gitlab Access Token", type="password")

genai.configure(api_key=gemini_api_key)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

init_button = st.button("Initialize session and retrieve the classified message")
if init_button:
    with st.spinner("Gemini API Session Creating"):
        @st.cache_resource
        def load_model():
            model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                          generation_config=generation_config,
                                          safety_settings=safety_settings)
            return model
        model = load_model()
    st.success("Gemini API Session Created")

    with st.spinner("Github session creating"):
        @st.cache_resource
        def github_session(github_token):
            auth = Auth.Token(github_token)
            g = Github(auth=auth)
            return g
        g = github_session(github_token)
    st.success("Github session created")

    with st.spinner("Github commit Retrieval"):
        git_repo = g.get_repo(github_repo)
        cmmts = [cmmt.commit.message for cmmt in git_repo.get_commits()]
        convo = model.start_chat(history=[])
        commit_template = """Using the below repo commit message classify it based on the 
        conventional commit categories: 
        Please find the categories : [fix, refactor, feat, docs, test, bug, chore]
        Please find the commit message here: {message}
        Please give the classified category in a seperate line""".format(message=cmmts[0])
        convo.send_message(commit_template)
        st.subheader("Commit Message", divider="violet")
        st.markdown("*Use the below message to re-commit the latest commit*")
        st.success("git commit -m '{final_message} : {commit}'".format(final_message = convo.last.text.replace(" \n", " "),
                                                                     commit = cmmts[0]))
