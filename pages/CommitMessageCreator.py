import streamlit as st
import requests
import google.generativeai as genai
from github import Github
from github import Auth

st.title("Commit Message Creator")
st.markdown("*Rephrase or create commit message based on code diff*")
st.subheader("Commit Message Classifier", divider="green")

github_repo = st.text_input("Github Repo, Eg: google/vision i.e organisation/project")

gemini_api_key = st.session_state.get("gemini_api_key")
github_token = st.session_state.get("github_token")

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


@st.cache_resource
def load_model():
    return genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                 generation_config=generation_config,
                                 safety_settings=safety_settings)


@st.cache_resource
def github_session(github_token):
    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    return g


init_button = st.button("Generate CommitMessage")

if init_button:
    with st.spinner("Gemini Session Creation"):
        gem_model = load_model()
    st.success("Gemini API Session Created")

    with st.spinner("Github Session Creation"):
        github_sess = github_session(github_token)
    st.success("Github session created")

    with st.spinner("Getting the latest commit"):
        git_repo = github_sess.get_repo(github_repo)
        latest_commit = git_repo.get_commits()[0]
        latest_commit_1 = git_repo.get_commits()[1]
        repo_compare = git_repo.compare(latest_commit_1.sha, latest_commit.sha)
        diff_content = requests.get(repo_compare.diff_url).content

    with st.spinner("Generating the commit message"):
        message_template = """Given below is the diff of a file in code: {code_block}. 
        By using the diff syntax generate the commit message by following the standards 
        of conventional commits.
        Use only the following classes to classify for conventional commits:
        ["docs", "feat", "fix", "chore", "test", "performance", "refactor"] 
        Find the filename from the diff given and try to provide
        a simple summarized commit message
        Keep commit message to be generic and 
        provide only one version of the commit message. 
        Finally give only the commit message""".format(code_block=diff_content)
        response = gem_model.generate_content(message_template)
        st.markdown("**Generated Commit Message**")
        st.success(response.candidates[0].content.parts[0].text)
