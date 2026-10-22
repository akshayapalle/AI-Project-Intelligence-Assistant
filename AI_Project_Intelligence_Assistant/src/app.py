from src.approval_workflow import show_approval_workflow
import streamlit as st

from src.rag_pipeline import create_rag_answer
from src.project_intelligence import get_project_brief
from src.memory_store import initialize_memory_db


st.set_page_config(
    page_title="AI Project Intelligence Assistant",
    page_icon="📊",
    layout="wide",
)

initialize_memory_db()

st.title("📊 AI Project Intelligence Assistant")
st.caption("Your ShopSphere project copilot")
st.divider()

with st.expander("Change Request Approval Workflow", expanded=False):
    show_approval_workflow()
with st.sidebar:
    st.header("Project")
    st.write("**ShopSphere E-commerce Platform**")
    st.write("Client: Acme Retail")

    if st.button("Generate Project Brief", use_container_width=True):
        with st.spinner("Analyzing project documents..."):
            try:
                st.session_state["project_brief"] = get_project_brief()
            except Exception as error:
                st.error(f"Could not generate brief: {error}")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.divider()
    st.caption("Answers are based on indexed project documents and conversation context.")


if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "project_brief" in st.session_state:
    st.subheader("Project Intelligence Brief")
    st.markdown(st.session_state["project_brief"])
    st.divider()

st.subheader("Ask about your project")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask about status, risks, deadlines, tasks, or approvals..."
)

if question:
    st.session_state["messages"].append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching project documents..."):
            try:
                answer = create_rag_answer(
                    question,
                    top=8,
                    conversation_id="proj-ai",
                )
                st.markdown(answer)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as error:
                st.error(f"Unable to answer: {error}")
