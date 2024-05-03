import streamlit as st
import requests
import google.generativeai as genai
from github import Github
from github import Auth

st.title("Pull Request Description Generator")
st.markdown("*Creates a description which can be used when creating a pull request*")
st.subheader("Pull Request Descriptor", divider="green")

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


init_button = st.button("Generate Pull Request Description")

if init_button:
    with st.spinner("Gemini Session Creation"):
        gem_model = load_model()
    st.success("Gemini API Session Created")

    with st.spinner("Github Session Creation"):
        github_sess = github_session(github_token)
    st.success("Github session created")

    with st.spinner("Getting all commits"):
        git_repo = github_sess.get_repo(github_repo)
        all_commits = list(git_repo.get_commits())

  # Initialize variables for summary
modified_files = set()
added_functionality = []
fixed_bugs = []
performance_improvements = []
updated_documentation = []

for commit in all_commits:
    # Analyze each commit
    diff_content = requests.get(commit.diff_url).content
    parsed_diff = PatchSet(diff_content)

    # Extract information from the diff
    for file in parsed_diff:
      modified_files.add(file.path)
      for hunk in file:
        if hunk.is_added:
          added_functionality.append(f"{commit.sha} ({hunk.source_start_line}:{hunk.source_end_line})")
        #  For bug fixes and performance improvements, you can use heuristics or rules based on commit messages or comments
        #  This is a simplified example

  # Summarize changes based on extracted information
summary_of_changes = ""
if modified_files:
    summary_of_changes += f"* Modified files: {', '.join(modified_files)}\n"
if added_functionality:
    summary_of_changes += f"* Added functionality (commits: {', '.join(added_functionality[:3])})...\n"  # Show only first 3 for brevity
if fixed_bugs:
    summary_of_changes += f"* Fixed bugs related to ... (commits: {', '.join(fixed_bugs[:3])})...\n"
if performance_improvements:
    summary_of_changes += f"* Improved performance of ... (commits: {', '.join(performance_improvements[:3])})...\n"
if updated_documentation:
    summary_of_changes += f"* Updated documentation for {', '.join(updated_documentation[:3])} (commits: {', '.join(updated_documentation[:3])})...\n"
