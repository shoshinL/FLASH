from typing import List
from apiUtils.key_manager import get_api_key
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.vectorstores import Chroma, VectorStoreRetriever
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings


def load_pdf(file_path) -> List[Document]:
    loader = PyPDFLoader(file_path, extract_images=False)
    return loader.load()

def get_retrieval_embeddings(documents: List[Document]) -> VectorStoreRetriever:
    api_key = get_api_key()
    text_splitter_for_retrieval = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=50
    )

    doc_splits_retrieval = text_splitter_for_retrieval.split_documents(documents)

    vectorstore = Chroma.from_documents(
    documents=doc_splits_retrieval,
    collection_name="rag-chroma",
    embedding=NVIDIAEmbeddings(model='NV-Embed-QA', nvidia_api_key=api_key)
    )
    retriever = vectorstore.as_retriever()
    return retriever

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

def get_question_formulation_chunks(documents: List[Document]) -> List[Document]:
    # Assuming 'documents' is a list of Document instances sorted by their page number
    document = concatenate_pages(documents)
    
    text_splitter_for_question_formulation = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=3000, chunk_overlap=500
    )

    doc_splits_question_formulation = text_splitter_for_question_formulation.split_documents(document)

    return doc_splits_question_formulation