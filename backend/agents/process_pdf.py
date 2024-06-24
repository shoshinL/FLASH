from typing import List
from venv import logger
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
import platform
import tiktoken

from settingUtils.api_key_utils import require_api_key

def load_pdf(file_path) -> List[Document]:
    system = platform.system()
    if system == "Windows":
        file_path = file_path.replace("/", "\\")
    elif system == "Darwin" or system == "Linux":
        file_path = file_path.replace("\\", "/")
    else:
        raise OSError("Unsupported operating system")

    loader = PyPDFLoader(file_path, extract_images=False)
    return loader.load()

@require_api_key
def get_retrieval_embeddings(api_key, documents: List[Document]):
    try:
        if not api_key:
            raise ValueError("API key is missing.")
        
        text_splitter_for_retrieval = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=250, chunk_overlap=50
        )
        
        logger.info("Splitting documents for retrieval...")
        doc_splits_retrieval = text_splitter_for_retrieval.split_documents(documents)
        
        logger.info("Creating vector store from documents...")
        vectorstore = Chroma.from_documents(
            documents=doc_splits_retrieval,
            collection_name="rag-chroma",
            embedding=NVIDIAEmbeddings(model='NV-Embed-QA', nvidia_api_key=api_key)
        )
        
        logger.info("Initializing retriever from vector store...")
        retriever = vectorstore.as_retriever()
        
        return retriever
    except Exception as e:
        logger.error(f"Error in get_retrieval_embeddings: {e}")
        return None

def concatenate_pages(documents: List[Document]) -> List[Document]:
    # Assuming 'documents' is a list of Document instances sorted by their page number
    concatenated_content = ""
    last_page = None
    sources = set()

    for doc in documents:
        if doc.metadata['page'] == last_page:
            # Same page, add a space
            concatenated_content += " " + doc.page_content
        else:
            # New page, add two line breaks
            if last_page is not None:  # to avoid adding line breaks before any content at start
                concatenated_content += "\n\n"
            concatenated_content += doc.page_content
        last_page = doc.metadata['page']
        sources.add(doc.metadata['source'])

    # Assuming all documents come from the same source file, which should be checked or handled if not
    source = sources.pop() if len(sources) == 1 else "Multiple sources"

    # Creating the final metadata
    page_range = f"{documents[0].metadata['page']}-{documents[-1].metadata['page']}"
    final_metadata = {
        "source": source,
        "pages": page_range
    }

    # Return the concatenated document
    return Document(concatenated_content, metadata=final_metadata)

def get_question_formulation_chunks(documents: List[Document], question_context: str) -> List[Document]:
    """
    Splits concatenated document pages into chunks suitable for question formulation.
    
    Parameters:
    documents (List[Document]): A list of Document instances sorted by their page number.
    question_context (str): The context of the question to consider for chunk size adjustment.
    
    Returns:
    List[Document]: A one-element list containing the concatenated documents.
    """
    # Concatenate all pages into a single Document instance
    concatenated_document = concatenate_pages(documents)
    
    # Encode the question context into tokens using tiktoken
    encoder = tiktoken.get_encoding("gpt2")  # Adjust based on the actual encoding method used
    question_context_size = len(encoder.encode(question_context))
    
    # Initialize the text splitter with adjusted chunk size
    adjusted_chunk_size = 5000 - question_context_size
    chunk_overlap = 500
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=adjusted_chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    # Split the concatenated document into smaller chunks
    doc_chunks = text_splitter.split_documents([concatenated_document])
    
    return doc_chunks