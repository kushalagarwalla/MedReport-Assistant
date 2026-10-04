import logging
import os
import re
import tempfile
import uuid

import streamlit as st

from medreport.agent import build_agent
from medreport.config import settings
from medreport.ingestion import ReportError, load_and_split
from medreport.vectorstore import build_vector_store

logger = logging.getLogger(__name__)

st.set_page_config(page_title="MedReport Assistant", page_icon="🩺")
st.title("🩺 MedReport Assistant")
st.caption("Upload your lab report and ask questions about it in plain language. This is not medical advice.")


def start_new_session():
    # Clears the previous report and conversation
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.agent = None
    st.session_state.file_id = None
    st.session_state.upload_error = None


# Streamlit reruns this script on every interaction, so anything that must
# survive between messages lives in st.session_state (one per browser session)
if "thread_id" not in st.session_state:
    start_new_session()


def build_agent_from_upload(uploaded_file):
    # PyPDFLoader needs a path on disk, so write the upload to a temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(uploaded_file.getvalue())
        pdf_path = f.name
    try:
        chunks = load_and_split(pdf_path, settings.chunk_size, settings.chunk_overlap)
    finally:
        os.remove(pdf_path)

    vector_store = build_vector_store(chunks, settings.embedding_model)
    return build_agent(vector_store)


uploaded = st.file_uploader("Upload your lab report", type="pdf")

if uploaded is None:
    if st.session_state.file_id is not None:
        start_new_session()
    st.info("Upload a PDF lab report to get started.")
    st.stop()

# Only process when a different file is uploaded, not on every rerun
if st.session_state.file_id != uploaded.file_id:
    start_new_session()
    st.session_state.file_id = uploaded.file_id
    with st.spinner("Reading your report..."):
        try:
            st.session_state.agent = build_agent_from_upload(uploaded)
        except ReportError as e:
            st.session_state.upload_error = str(e)
        except Exception:
            logger.exception("Failed to process uploaded report")
            st.session_state.upload_error = "Something went wrong while processing your report. Please try uploading it again."

if st.session_state.upload_error:
    st.error(st.session_state.upload_error)
    st.stop()

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

if query := st.chat_input("Ask about your report"):
    st.chat_message("user").write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.invoke(
                {"messages": [{"role": "user", "content": query}]},
                {"configurable": {"thread_id": st.session_state.thread_id}},
            )
        # .text joins the reply's text blocks and skips the model's hidden reasoning blocks
        answer = response["messages"][-1].text
        # Streamlit shows HTML tags as plain text, so swap stray <br> tags for spaces
        answer = re.sub(r"<br\s*/?>", " ", answer, flags=re.IGNORECASE)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
