from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf.errors import FileNotDecryptedError


class ReportError(Exception):
    """Raised when an uploaded file can't be used as a lab report. The message is shown to the user."""


def load_and_split(pdf_path: str, chunk_size: int, chunk_overlap: int) -> list[Document]:
    try:
        docs = PyPDFLoader(file_path=pdf_path).load()
    except FileNotDecryptedError as e:
        raise ReportError("This PDF is password-protected. Please upload an unlocked copy.") from e
    except Exception as e:
        raise ReportError("Couldn't read this file. It may be damaged or not a real PDF.") from e

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    # Scanned reports are images, so no text can be extracted from them
    if not chunks:
        raise ReportError(
            "No text could be found in this PDF. It looks like a scanned image, "
            "which isn't supported yet. Please upload a digital (text-based) report."
        )
    return chunks
