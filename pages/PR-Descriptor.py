import streamlit as st
import requests
import google.generativeai as genai
from github import Github
from github import Auth

st.title("Pull Request Description Generator")
st.markdown("*Creates a description which can be used when creating a pull request*")
st.subheader("Pull Request Descriptor", divider="green")

github_repo = st.text_input("Github Repo, Eg: google/vision i.e organisation/project")
target_branch_name = st.text_input("Target Branch Name", key = "target_branch_name")
feature_branch_name = st.text_input("Feature Branch Name", key = "feature_branch_name")

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


init_button = st.button("Generate Pull Request Description")

if init_button:
    with st.spinner("Gemini Session Creation"):
        gem_model = load_model()
    st.success("Gemini API Session Created")

    with st.spinner("Github Session Creation"):
        github_sess = github_session(github_token)
    st.success("Github session created")

    with st.spinner("Analyzing changes between branches"):
        try:
            github_repo = github_sess.get_repo(github_repo)
            # Get content from HEAD of target branch (assumes target branch as main by default)
            if target_branch_name:
                target_branch_commit_last = github_repo.get_commit(target_branch_name)
            else:
                target_branch_commit_last = github_repo.get_commit("HEAD")
            target_branch_sha = target_branch_commit_last.sha

            # Get content from HEAD (latest commit) of feature branch
            if feature_branch_name:
                feature_branch_commit_last = github_repo.get_commit(feature_branch_name)
                feature_branch_sha = feature_branch_commit_last.sha
            
            # Get content since main branch not provided
            else:
                st.warning("No feature branch name provided, cannot compare with main branch.")
                feature_branch_commit_last = None

            # Analyze diff (if feature branch provided)
            repo_compare = github_repo.compare(target_branch_sha, feature_branch_sha)
            diff_content = requests.get(repo_compare.diff_url).content

            # # Generating a short description without Google Gemini
            # short_description = f"""This pull request introduces changes from commit {feature_branch_sha} in branch {feature_branch_name}.
            # The latest commit on the main branch is {target_branch_sha}.
            # """
            # st.markdown("**Short Pull Request Description**")
            # st.success(short_description)

            with st.spinner("Generating a description for the pull request based on changes"):
                message_template = """Analyze the provided diff "{diff_content}" for the pull request on branch "{feature_branch_name}" (commit: {feature_branch_sha}). 
                Focus on the files that have been modified and identify the key changes introduced. 
                Take into account the surrounding code (functions, classes) to understand the context and impact of these changes. 
                Highlight both additions and deletions within the modified files, and explain their purpose in a clear and concise manner. 
                Generate a pull request description using simple and concise language that accurately reflects the technical changes in the diff.""".format(diff_content=diff_content, feature_branch_name=feature_branch_name, feature_branch_sha=feature_branch_sha)
                
                gemini_response = gem_model.generate_content(message_template)

                st.markdown("**Detailed Pull Request Description**")
                st.success(gemini_response.candidates[0].content.parts[0].text)

        except Exception as e:
            st.error(f"Error analyzing changes: {e}")