import streamlit as st
import requests
import google.generativeai as genai
from github import Github
from github import Auth

st.title("Pull Request Reviewer")
st.markdown("*Provide initial code review based on code diff*")
st.subheader("Pull Request Reviewer", divider="green")

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


get_review_button = st.button("Get review comment for the latest open pull request")

if get_review_button:
    with st.spinner("Gemini Session Creation"):
        gem_model = load_model()
    st.success("Gemini API Session Created")

    with st.spinner("Github Session Creation"):
        github_sess = github_session(github_token)
    st.success("Github session created")

    with st.spinner("Getting the latest pull request"):
        git_repo = github_sess.get_repo(github_repo)
        try:
            pull_req = git_repo.get_pulls(state="open")[0]
        except IndexError:
            raise ValueError("Try with only open PRs for now")
        diff_content = requests.get(pull_req.diff_url).text

    with st.spinner("Generating the review"):
        message_template = """Given is the diff of the pull request of code: {code_block}. 
        By using the diff syntax review the code and provide breif comments. 
        Make sure the review comments follow the best practices and optimzations.
        Mention the line number, method and the variable name while providing the comment
        Clearly mention the bugs if anything found
        Properly mention the changes in the functions and classes and their lines respectively""".format(code_block=diff_content)
        response = gem_model.generate_content(message_template)
        st.markdown("**Generated Code Review**")
        st.success(response.candidates[0].content.parts[0].text)